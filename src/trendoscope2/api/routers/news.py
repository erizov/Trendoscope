"""
News API endpoints.
Handles news feed, translation, and related operations.
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional
import logging

from ...ingest.news_sources_async import AsyncNewsAggregator
from ...nlp.translator import translate_and_summarize_news
from ...config import (
    NEWS_FETCH_TIMEOUT, NEWS_MAX_PER_SOURCE, NEWS_DB_DEFAULT_LIMIT,
    NEWS_TRANSLATION_MAX_ITEMS
)
from ...services.background_tasks import background_manager
from ...utils.encoding import fix_double_encoding, safe_str
from ...utils.text_processing import clean_html
from ...services.categorization_service import CategorizationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/feed")
async def get_news_feed(
    category: str = Query(default="all", description="Category filter"),
    limit: Optional[int] = Query(default=None, ge=5, le=100, description="Maximum items"),
    language: str = Query(default="all", description="Language filter (all, ru, en)"),
    translate_to: str = Query(default="none", description="Translate to (none, ru, en)"),
    use_cache: bool = Query(default=True, description="Use cached news if available")
):
    """Get news feed (async with caching)."""
    try:
        if limit is None:
            limit = NEWS_DB_DEFAULT_LIMIT
        logger.info(f"Fetching news: category={category}, limit={limit}, use_cache={use_cache}")
        
        # Try to use cached news first
        if use_cache:
            cached_news = background_manager.get_cached_news()
            if cached_news:
                logger.info(f"Using {len(cached_news)} cached news items")
                news_items = cached_news
            else:
                # Fallback to async fetch
                logger.info("No cache available, fetching async...")
                async with AsyncNewsAggregator(timeout=NEWS_FETCH_TIMEOUT) as aggregator:
                    news_items = await aggregator.fetch_trending_topics(
                        include_russian=True,
                        include_international=True,
                        include_ai=True,
                        include_politics=True,
                        include_us=True,
                        include_eu=True,
                        include_regional=True,
                        include_asia=True,
                        max_per_source=NEWS_MAX_PER_SOURCE
                    )
        else:
            # Force fresh fetch
            async with AsyncNewsAggregator(timeout=NEWS_FETCH_TIMEOUT) as aggregator:
                news_items = await aggregator.fetch_trending_topics(
                    include_russian=True,
                    include_international=True,
                    include_ai=True,
                    include_politics=True,
                    include_us=True,
                    include_eu=True,
                    include_regional=True,
                    include_asia=True,
                    max_per_source=NEWS_MAX_PER_SOURCE
                )
        
        logger.info(f"Fetched {len(news_items)} news items")
        
        # Fix double-encoding issues in all news items
        # Detect and set language for each item
        encoding_fixed_count = 0
        for item in news_items:
            try:
                # Fix encoding for all text fields BEFORE language detection
                original_title = item.get('title', '')
                original_summary = item.get('summary', '')
                
                fixed_title = fix_double_encoding(original_title)
                fixed_summary = fix_double_encoding(original_summary)
                fixed_source = fix_double_encoding(item.get('source', ''))
                
                # Check if encoding was fixed
                if fixed_title != original_title or fixed_summary != original_summary:
                    encoding_fixed_count += 1
                    logger.debug(f"Fixed encoding for: '{original_title[:50]}...'")
                
                item['title'] = fixed_title
                item['summary'] = fixed_summary
                item['source'] = fixed_source
                
                # Clean HTML from summary and description
                if item.get('summary'):
                    item['summary'] = clean_html(item['summary'])
                
                if item.get('description'):
                    item['description'] = clean_html(item['description'])
                
                # Safely extract text fields
                title = safe_str(item.get('title', ''))
                summary = safe_str(item.get('summary', ''))
                text = f"{title} {summary}"
                
                # Ensure text is a string (not bytes)
                if isinstance(text, bytes):
                    try:
                        text = text.decode('utf-8')
                    except UnicodeDecodeError:
                        text = text.decode('utf-8', errors='replace')
                
                # Detect language
                cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
                latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                total_chars = cyrillic_chars + latin_chars
                
                if total_chars > 0:
                    cyrillic_ratio = cyrillic_chars / total_chars
                    item['language'] = 'ru' if cyrillic_ratio > 0.3 else 'en'
                else:
                    item['language'] = 'en'
            except (UnicodeDecodeError, UnicodeEncodeError, AttributeError, TypeError) as e:
                logger.warning(f"Language detection error: {e}")
                item['language'] = 'en'  # Default to English on error
        
        # Categorize news (after encoding is fixed)
        # Always recategorize based on content, ignoring URL-based categories
        category_counts = {}
        for item in news_items:
            # Always recategorize based on content for more accurate categorization
            old_category = item.get('category', 'none')
            item['category'] = CategorizationService.categorize(item)
            category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
            
            # Log if category changed
            if old_category != item['category']:
                logger.debug(
                    f"Recategorized: '{item.get('title', '')[:50]}...' -> "
                    f"{old_category} -> {item['category']} "
                    f"(lang: {item.get('language', 'unknown')})"
                )
        
        logger.info(f"Category distribution: {category_counts}")
        logger.info(
            f"Encoding fixes applied: {encoding_fixed_count} out of {len(news_items)} items"
        )
        
        # Filter by category if not 'all'
        if category != 'all':
            news_items = [
                item for item in news_items
                if item.get('category') == category
            ]
            logger.info(f"After category filter '{category}': {len(news_items)} items")
        
        # Filter by language
        if language != 'all':
            news_items = [item for item in news_items if item.get('language') == language]
        
        # Translate if requested
        if translate_to != 'none' and news_items:
            try:
                items_to_translate = [
                    item for item in news_items
                    if item.get('language') != translate_to
                ]
                if items_to_translate:
                    translated = translate_and_summarize_news(
                        items_to_translate[:NEWS_TRANSLATION_MAX_ITEMS],
                        target_language=translate_to,
                        provider="free",
                        max_items=NEWS_TRANSLATION_MAX_ITEMS
                    )
                    # Update in list
                    translated_map = {item.get('link'): item for item in translated}
                    for i, item in enumerate(news_items):
                        if item.get('link') in translated_map:
                            news_items[i] = translated_map[item.get('link')]
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        return {
            "success": True,
            "count": len(news_items),
            "category": category,
            "news": news_items[:limit]
        }
    except Exception as e:
        logger.error(f"Error fetching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_article(
    article: Dict[str, Any] = Body(...),
    target_language: str = Query(..., description="Target language (ru, en)")
):
    """Translate a single article."""
    try:
        title = article.get('title', '').strip()
        summary = article.get('summary', '').strip()
        source_lang = article.get('source_language', article.get('language', 'en'))
        
        if not title and not summary:
            raise HTTPException(status_code=400, detail="Title or summary required")
        
        news_item = {
            'title': title,
            'summary': summary,
            'language': source_lang
        }
        
        translated_items = translate_and_summarize_news(
            [news_item],
            target_language=target_language,
            provider="free",
            max_items=1
        )
        
        if not translated_items:
            raise HTTPException(status_code=500, detail="Translation failed")
        
        translated = translated_items[0]
        
        return {
            "success": True,
            "translated": {
                "title": translated.get('title', title),
                "summary": translated.get('summary', summary)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
