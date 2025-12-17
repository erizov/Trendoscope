"""
News service for processing and managing news items.
Handles fetching, processing, filtering, and translation of news.
"""
import logging
from typing import Dict, Any, List, Optional
from ..ingest.news_sources_async import AsyncNewsAggregator
from ..nlp.translator import translate_and_summarize_news
from ..config import (
    NEWS_FETCH_TIMEOUT, NEWS_MAX_PER_SOURCE, NEWS_TRANSLATION_MAX_ITEMS
)
from ..services.background_tasks import background_manager
from ..utils.encoding import fix_double_encoding, safe_str
from ..utils.text_processing import clean_html
from ..services.categorization_service import CategorizationService

logger = logging.getLogger(__name__)


class NewsService:
    """Service for processing news items."""

    @staticmethod
    async def fetch_news(
        use_cache: bool = True,
        force_fresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch news items from sources or cache.

        Args:
            use_cache: Whether to use cached news if available
            force_fresh: Force fresh fetch even if cache exists

        Returns:
            List of news items
        """
        # Lazy import to avoid circular dependency
        from ..services.cache_service import get_cache_service
        cache = get_cache_service()
        cache_key = "news:feed:all"
        
        # Try cache first
        if use_cache and not force_fresh:
            # Try Redis/in-memory cache
            cached_news = cache.get(cache_key)
            if cached_news:
                logger.info(f"Using {len(cached_news)} cached news items")
                return cached_news
            
            # Fallback to background manager cache
            cached_news = background_manager.get_cached_news()
            if cached_news:
                logger.info(f"Using {len(cached_news)} background cached news items")
                # Store in Redis cache for next time
                cache.set(cache_key, cached_news, ttl=300)  # 5 minutes
                return cached_news

        logger.info("Fetching fresh news...")
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
        
        # Cache the result
        cache.set(cache_key, news_items, ttl=300)  # 5 minutes
        
        return news_items

    @staticmethod
    def process_news_items(news_items: List[Dict[str, Any]]) -> int:
        """
        Process news items: fix encoding, clean HTML, detect language.

        Args:
            news_items: List of news items to process

        Returns:
            Number of items with encoding fixes applied
        """
        encoding_fixed_count = 0

        for item in news_items:
            try:
                # Fix encoding for all text fields
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

                # Detect language
                NewsService._detect_language(item)

            except (UnicodeDecodeError, UnicodeEncodeError, AttributeError, TypeError) as e:
                logger.warning(f"Processing error for item: {e}")
                item['language'] = 'en'  # Default to English on error

        logger.info(
            f"Encoding fixes applied: {encoding_fixed_count} out of "
            f"{len(news_items)} items"
        )
        return encoding_fixed_count

    @staticmethod
    def _detect_language(item: Dict[str, Any]) -> None:
        """
        Detect language for a news item based on text content.

        Args:
            item: News item dictionary (modified in place)
        """
        title = safe_str(item.get('title', ''))
        summary = safe_str(item.get('summary', ''))
        text = f"{title} {summary}"

        # Ensure text is a string (not bytes)
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('utf-8', errors='replace')

        # Detect language based on character distribution
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total_chars = cyrillic_chars + latin_chars

        if total_chars > 0:
            cyrillic_ratio = cyrillic_chars / total_chars
            item['language'] = 'ru' if cyrillic_ratio > 0.3 else 'en'
        else:
            item['language'] = 'en'

    @staticmethod
    def categorize_news(news_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Categorize news items and return category distribution.

        Args:
            news_items: List of news items to categorize

        Returns:
            Dictionary with category counts
        """
        category_counts = {}

        for item in news_items:
            old_category = item.get('category', 'none')
            item['category'] = CategorizationService.categorize(item)
            category_counts[item['category']] = (
                category_counts.get(item['category'], 0) + 1
            )

            # Log if category changed
            if old_category != item['category']:
                logger.debug(
                    f"Recategorized: '{item.get('title', '')[:50]}...' -> "
                    f"{old_category} -> {item['category']} "
                    f"(lang: {item.get('language', 'unknown')})"
                )

        logger.info(f"Category distribution: {category_counts}")
        return category_counts

    @staticmethod
    def filter_news(
        news_items: List[Dict[str, Any]],
        category: str = 'all',
        language: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Filter news items by category and language.

        Args:
            news_items: List of news items to filter
            category: Category filter ('all' for no filter)
            language: Language filter ('all' for no filter)

        Returns:
            Filtered list of news items
        """
        filtered = news_items

        # Filter by category
        if category != 'all':
            filtered = [
                item for item in filtered
                if item.get('category') == category
            ]
            logger.info(f"After category filter '{category}': {len(filtered)} items")

        # Filter by language
        if language != 'all':
            filtered = [
                item for item in filtered
                if item.get('language') == language
            ]

        return filtered

    @staticmethod
    async def translate_news(
        news_items: List[Dict[str, Any]],
        target_language: str
    ) -> List[Dict[str, Any]]:
        """
        Translate news items to target language.

        Args:
            news_items: List of news items to translate
            target_language: Target language code (ru, en)

        Returns:
            List of news items with translations applied
        """
        if not news_items:
            return news_items

        try:
            items_to_translate = [
                item for item in news_items
                if item.get('language') != target_language
            ]

            if not items_to_translate:
                return news_items

            translated = translate_and_summarize_news(
                items_to_translate[:NEWS_TRANSLATION_MAX_ITEMS],
                target_language=target_language,
                provider="free",
                max_items=NEWS_TRANSLATION_MAX_ITEMS
            )

            # Update items in list
            translated_map = {item.get('link'): item for item in translated}
            result = news_items.copy()

            for i, item in enumerate(result):
                if item.get('link') in translated_map:
                    result[i] = translated_map[item.get('link')]

            return result

        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return news_items

    @staticmethod
    async def get_news_feed(
        category: str = 'all',
        limit: Optional[int] = None,
        language: str = 'all',
        translate_to: str = 'none',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get processed news feed with all filters and transformations.

        Args:
            category: Category filter
            limit: Maximum number of items to return
            language: Language filter
            translate_to: Target language for translation ('none' to skip)
            use_cache: Whether to use cached news

        Returns:
            Dictionary with success status, count, category, and news items
        """
        # Lazy import to avoid circular dependency
        from ..services.cache_service import get_cache_service
        cache = get_cache_service()
        # Create cache key based on all parameters
        cache_key = f"news:feed:{category}:{language}:{translate_to}:{limit or 'all'}"
        
        # Try cache first
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Using cached news feed: {cache_key}")
                return cached_result
        
        # Fetch news
        news_items = await NewsService.fetch_news(use_cache=use_cache)

        # Process news items
        NewsService.process_news_items(news_items)

        # Categorize news
        NewsService.categorize_news(news_items)

        # Filter news
        news_items = NewsService.filter_news(news_items, category, language)

        # Translate if requested
        if translate_to != 'none':
            news_items = await NewsService.translate_news(news_items, translate_to)

        # Apply limit
        if limit:
            news_items = news_items[:limit]

        result = {
            "success": True,
            "count": len(news_items),
            "category": category,
            "news": news_items
        }
        
        # Cache the result
        cache.set(cache_key, result, ttl=300)  # 5 minutes
        
        return result

    @staticmethod
    async def translate_article(
        article: Dict[str, Any],
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translate a single article.

        Args:
            article: Article dictionary with title and summary
            target_language: Target language code (ru, en)

        Returns:
            Dictionary with translated title and summary
        """
        title = article.get('title', '').strip()
        summary = article.get('summary', '').strip()
        source_lang = article.get('source_language', article.get('language', 'en'))

        if not title and not summary:
            raise ValueError("Title or summary required")

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
            raise ValueError("Translation failed")

        translated = translated_items[0]

        return {
            "success": True,
            "translated": {
                "title": translated.get('title', title),
                "summary": translated.get('summary', summary)
            }
        }
