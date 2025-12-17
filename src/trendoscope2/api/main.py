"""
FastAPI application for Trendoscope2.
Minimal setup with essential endpoints.
"""
from fastapi import FastAPI, HTTPException, Query, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import sys
import os
import mimetypes

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ..ingest.news_sources import NewsAggregator
from ..ingest.news_sources_async import AsyncNewsAggregator
from ..nlp.translator import translate_and_summarize_news
from ..storage.news_db import NewsDatabase
from ..config import (
    DATA_DIR, TTS_PROVIDER, TTS_CACHE_ENABLED, TTS_FALLBACK_ENABLED,
    EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD,
    EMAIL_FROM, EMAIL_ENABLED, EMAIL_RATE_LIMIT_PER_MINUTE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TELEGRAM_ENABLED,
    TELEGRAM_POST_FORMAT, TELEGRAM_MAX_POST_LENGTH, TELEGRAM_RATE_LIMIT_PER_MINUTE,
    NEWS_FETCH_TIMEOUT, NEWS_MAX_PER_SOURCE, NEWS_DB_DEFAULT_LIMIT,
    NEWS_TRANSLATION_MAX_ITEMS, NEWS_DB_MAX_RECORDS, TTS_CLEANUP_MAX_AGE_DAYS
)
from ..services.background_tasks import background_manager
from ..services.email_service import EmailService
from ..services.telegram_service import TelegramService
from ..tts.tts_service import TTSService
from .schemas import (
    TranslateArticleRequest,
    RutubeGenerateRequest,
    TTSGenerateRequest,
    EmailSendRequest,
    EmailDigestRequest,
    TelegramPostRequest,
    NewsFeedQueryParams
)

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)
logging.basicConfig(level=numeric_level)
logger = logging.getLogger(__name__)
logger.setLevel(numeric_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to replace startup/shutdown events."""
    logger.info("Starting background tasks...")
    await background_manager.start_all(news_interval=300)  # 5 minutes
    logger.info("Background tasks started")
    try:
        yield
    finally:
        logger.info("Stopping background tasks...")
        await background_manager.stop_all()
        logger.info("Background tasks stopped")


app = FastAPI(
    title="Trendoscope2 API",
    description="Improved news aggregation and content generation",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TTS service
tts_service = TTSService(
    provider=TTS_PROVIDER,
    cache_enabled=TTS_CACHE_ENABLED,
    fallback_enabled=TTS_FALLBACK_ENABLED
)

# Initialize Email service
email_service = EmailService(
    smtp_host=EMAIL_SMTP_HOST,
    smtp_port=EMAIL_SMTP_PORT,
    smtp_user=EMAIL_SMTP_USER,
    smtp_password=EMAIL_SMTP_PASSWORD,
    from_email=EMAIL_FROM,
    rate_limit_per_minute=EMAIL_RATE_LIMIT_PER_MINUTE
)

# Initialize Telegram service
telegram_service = TelegramService(
    bot_token=TELEGRAM_BOT_TOKEN,
    default_channel_id=TELEGRAM_CHANNEL_ID,
    rate_limit_per_minute=TELEGRAM_RATE_LIMIT_PER_MINUTE
)

# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to main news page."""
    try:
        news_file = frontend_path / "news_feed.html"
        
        # Direct server-side redirect to news feed (more reliable than client-side)
        if news_file.exists():
            return RedirectResponse(url="/static/news_feed.html", status_code=301)
        
        # Fallback: serve index.html if news_feed.html doesn't exist
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(
                path=str(index_file),
                media_type="text/html",
                filename="index.html"
            )
    except Exception as e:
        logger.warning(f"Could not serve frontend: {e}")
    
    # Fallback to JSON status if no frontend files are available
    return {
        "name": "Trendoscope2",
        "version": "2.0.0",
        "status": "running",
        "frontend": "/static/news_feed.html" if frontend_path.exists() else None
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Check Redis
        redis_ok = False
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            redis_ok = True
        except:
            pass
        
        # Check database
        db_ok = False
        try:
            with NewsDatabase() as db:
                stats = db.get_statistics()
                db_ok = True
        except:
            pass
        
        return {
            "status": "healthy" if (redis_ok and db_ok) else "degraded",
            "redis": "ok" if redis_ok else "unavailable",
            "database": "ok" if db_ok else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/news/feed")
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
        def fix_double_encoding(text):
            """Fix double-encoded UTF-8 text (mojibake)."""
            if not text:
                return ''
            if isinstance(text, bytes):
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    return text.decode('utf-8', errors='replace')
            
            if not isinstance(text, str):
                text = str(text)
            
            # Check if text looks like double-encoded UTF-8 (mojibake)
            # Common pattern: "Р"Рё" instead of "Ди"
            # This happens when UTF-8 bytes are interpreted as Latin-1
            try:
                # Detect mojibake: if text contains sequences like "Р"Рё" (common in Russian)
                # These are UTF-8 bytes interpreted as Latin-1
                has_mojibake_pattern = False
                if len(text) > 0:
                    # Check for common mojibake patterns (more comprehensive list)
                    mojibake_indicators = [
                        'Р"', 'РІ', 'РЅ', 'Рѕ', 'Р°', 'Рё', 'СЂ', 'СЃ', 'РЅР°', 'РІРѕ',
                        'РґРё', 'РїРѕ', 'РєР°', 'РјРё', 'РЅР°С€', 'РІР°С€', 'РїСЂРё'
                    ]
                    has_mojibake_pattern = any(indicator in text[:300] for indicator in mojibake_indicators)
                    
                    # Also check if text has high-byte chars but no valid Cyrillic
                    high_byte_chars = sum(1 for c in text[:200] if ord(c) > 127)
                    cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
                    if high_byte_chars > 5 and cyrillic_chars < high_byte_chars * 0.2:
                        has_mojibake_pattern = True
                
                if has_mojibake_pattern or any(ord(c) > 127 for c in text[:200] if text):
                    # Try: encode as latin1 then decode as utf8
                    fixed = text.encode('latin1', errors='ignore').decode('utf-8', errors='replace')
                    # Only use if it looks better
                    if fixed and '\ufffd' not in fixed[:100]:
                        # Check if fixed version has more Cyrillic characters
                        cyrillic_original = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
                        cyrillic_fixed = sum(1 for c in fixed if '\u0400' <= c <= '\u04FF')
                        # Also check if fixed has fewer high-byte non-Cyrillic chars
                        high_byte_original = sum(1 for c in text[:200] if ord(c) > 127 and not ('\u0400' <= c <= '\u04FF'))
                        high_byte_fixed = sum(1 for c in fixed[:200] if ord(c) > 127 and not ('\u0400' <= c <= '\u04FF'))
                        
                        # More lenient condition: if fixed has ANY Cyrillic and fewer mojibake chars
                        if (cyrillic_fixed > cyrillic_original) or \
                           (cyrillic_fixed > 0 and high_byte_fixed < high_byte_original) or \
                           (cyrillic_fixed > 0 and cyrillic_original == 0):
                            logger.debug(f"Fixed encoding: '{text[:50]}...' -> '{fixed[:50]}...' (Cyrillic: {cyrillic_original}->{cyrillic_fixed})")
                            return fixed
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                logger.debug(f"Encoding fix error: {e}")
                pass
            
            return text
        
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
                def clean_html(text):
                    """Remove HTML tags from text."""
                    if not text:
                        return ''
                    # Try BeautifulSoup first
                    try:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(text, 'html.parser')
                        cleaned = soup.get_text(separator=' ', strip=True)
                        # Remove extra whitespace
                        cleaned = ' '.join(cleaned.split())
                        return cleaned
                    except Exception:
                        # Fallback: regex-based HTML tag removal
                        import re
                        cleaned = re.sub(r'<[^>]+>', '', text)
                        cleaned = ' '.join(cleaned.split())
                        return cleaned
                
                # Clean HTML from summary
                if item.get('summary'):
                    item['summary'] = clean_html(item['summary'])
                
                # Clean HTML from description if present
                if item.get('description'):
                    item['description'] = clean_html(item['description'])
                
                # Safely extract text fields
                def safe_str(value):
                    """Safely convert value to string, handling encoding issues."""
                    if value is None:
                        return ''
                    if isinstance(value, bytes):
                        try:
                            return value.decode('utf-8')
                        except UnicodeDecodeError:
                            return value.decode('utf-8', errors='replace')
                    return str(value)
                
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
            item['category'] = _categorize_news(item)
            category_counts[item['category']] = category_counts.get(item['category'], 0) + 1
            
            # Log if category changed
            if old_category != item['category']:
                logger.debug(f"Recategorized: '{item.get('title', '')[:50]}...' -> {old_category} -> {item['category']} (lang: {item.get('language', 'unknown')})")
        
        logger.info(f"Category distribution: {category_counts}")
        logger.info(f"Encoding fixes applied: {encoding_fixed_count} out of {len(news_items)} items")
        
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


def _categorize_news(item: Dict[str, Any]) -> str:
    """Categorize news item based on content - 8 main categories."""
    try:
        # Text fields should already be fixed by fix_double_encoding
        # But we still need to safely extract them
        def safe_str(value):
            """Safely convert value to string, handling encoding issues."""
            if value is None:
                return ''
            if isinstance(value, bytes):
                try:
                    return value.decode('utf-8')
                except UnicodeDecodeError:
                    return value.decode('utf-8', errors='replace')
            return str(value)
        
        title = safe_str(item.get('title', ''))
        summary = safe_str(item.get('summary', ''))
        description = safe_str(item.get('description', ''))
        
        # Combine text
        text = f"{title} {summary} {description}"
        
        # Ensure UTF-8 and convert to lowercase safely
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                text = text.decode('utf-8', errors='replace')
        
        # Convert to lowercase safely (handles Cyrillic)
        text = text.lower()
        
        # Ensure we have text to categorize
        if not text or len(text.strip()) == 0:
            logger.warning(f"Empty text for categorization, item: {item.get('title', 'no title')[:50]}")
            return 'general'
    except (UnicodeDecodeError, UnicodeEncodeError, AttributeError, TypeError) as e:
        # Fallback: use only title if encoding fails
        logger.warning(f"Encoding error in categorization: {e}, item keys: {list(item.keys())}")
        try:
            text = safe_str(item.get('title', '')).lower()
            if not text or len(text.strip()) == 0:
                return 'general'
        except Exception:
            return 'general'
    
    # Legal & Criminal (courts, law, crime, justice) - проверяем первым
    legal_keywords = [
        'court', 'judge', 'lawyer', 'attorney', 'trial', 'verdict', 'sentenced', 'conviction',
        'criminal', 'crime', 'arrest', 'police', 'investigation', 'lawsuit', 'legal',
        'justice', 'prison', 'jail', 'prosecutor', 'defendant', 'case', 'ruling',
        'суд', 'судья', 'адвокат', 'прокурор', 'приговор', 'уголовн', 'преступ',
        'полиц', 'следств', 'дело', 'обвинение', 'оправдан', 'тюрьма', 'арест',
        'юрист', 'право', 'закон', 'нарушение', 'расследование', 'обыск', 'задержан',
        'подозреваем', 'обвиняем', 'штраф', 'наказание', 'судопроизводство'
    ]
    
    # War & Conflict - проверяем вторым (более специфично)
    conflict_keywords = [
        'war', 'military', 'army', 'weapon', 'conflict', 'attack', 'defense', 'battle',
        'война', 'военн', 'армия', 'оружи', 'конфликт', 'удар', 'атак', 'оборон',
        'бой', 'сражение', 'вооружен', 'войск', 'солдат', 'фронт', 'наступление',
        'обстрел', 'ракет', 'бомбардировк', 'санкц', 'санкции', 'sanction'
    ]
    
    # Business & Economy - расширенные ключевые слова (проверяем ДО tech)
    business_keywords = [
        'market', 'stock', 'stock market', 'economy', 'economic', 'business', 'company', 'corporation',
        'trading', 'trade', 'investment', 'investor', 'ceo', 'cfo', 'revenue', 'profit', 'loss',
        'бизнес', 'компани', 'корпорац', 'рынок', 'фондов', 'экономик', 'экономика',
        'инвестиц', 'инвестор', 'акци', 'акции', 'финанс', 'финансы', 'банк', 'банки',
        'валют', 'доллар', 'евро', 'рубл', 'рубль', 'курс', 'обмен', 'обменн',
        'инфляц', 'инфляция', 'безработиц', 'безработица', 'gdp', 'ввп',
        'recession', 'depression', 'crisis', 'кризис', 'рецессия', 'торговл', 'торговля',
        'экспорт', 'импорт', 'производств', 'производство', 'завод', 'предприяти', 'предприятие',
        'бюджет', 'налог', 'налоги', 'налогообложен'
    ]
    
    # Tech (AI, ML, technology, platforms, internet)
    tech_keywords = [
        'ai', 'artificial', 'intelligence', 'gpt', 'neural', 'machine', 'learning',
        'tech', 'technology', 'algorithm', 'data', 'digital', 'internet', 'platform',
        'cloud', 'software', 'app', 'ии', 'нейросет', 'технолог', 'алгоритм', 'данные',
        'telegram', 'google', 'microsoft', 'apple', 'meta', 'программ', 'код',
        'chatbot', 'chat', 'robot', 'робот', 'автоматизац', 'кибер', 'cyber'
    ]
    
    # Science & Research - расширенные ключевые слова
    science_keywords = [
        'science', 'research', 'study', 'university', 'scientist', 'discovery',
        'наука', 'исследован', 'ученые', 'университет', 'открыти', 'experiment',
        'climate', 'energy', 'environment', 'климат', 'энергия', 'экология',
        'медицин', 'лекарств', 'лечение', 'болезн', 'вирус', 'вакцин',
        'космос', 'space', 'mars', 'марс', 'ракет', 'спутник', 'satellite',
        'физик', 'хими', 'биолог', 'генетик', 'dna', 'ген'
    ]
    
    # Society (social issues, people, rights) - расширенные ключевые слова
    society_keywords = [
        'social', 'people', 'society', 'protest', 'demonstration', 'rights', 'human rights', 'welfare',
        'социальн', 'общество', 'социальная', 'люди', 'права', 'справедлив', 'справедливость',
        'пенси', 'пенсия', 'пенсионер', 'пенсионеры', 'льгот', 'льгота', 'выплат', 'выплата',
        'миграц', 'миграция', 'беженц', 'беженец', 'демографи', 'демография', 'население',
        'образование', 'школ', 'школа', 'университет', 'студент', 'учитель', 'education',
        'здравоохранение', 'больниц', 'больница', 'врач', 'медицин', 'медицина', 'здоровье',
        'культур', 'культура', 'искусств', 'искусство', 'театр', 'кино', 'музей'
    ]
    
    # Politics (general, any country) - проверяем последним (самая общая категория)
    politics_keywords = [
        'politics', 'government', 'election', 'president', 'minister', 'congress',
        'политик', 'правительств', 'выборы', 'президент', 'министр', 'партия',
        'biden', 'trump', 'putin', 'путин', 'parliament', 'senate', 'кремль',
        'белый дом', 'white house', 'госдум', 'дум', 'сенат', 'конгресс',
        'депутат', 'депутаты', 'законодательств', 'законодатель', 'политическ',
        'власть', 'власт', 'администрац', 'администрация', 'кабинет', 'кабинет министров',
        'премьер', 'премьер-министр', 'глава', 'руководитель', 'лидер', 'лидеры',
        'оппозиц', 'оппозиция', 'фракц', 'фракция', 'коалиц', 'коалиция',
        'реформа', 'реформы', 'законопроект', 'законопроекты', 'голосован', 'голосование',
        'избирательн', 'избирательный', 'кампания', 'кампании', 'кандидат', 'кандидаты'
    ]
    
    # Check categories (order matters - most specific first)
    # Используем подсчет совпадений для более точной категоризации
    # Сначала проверяем специфичные категории, потом общие
    
    def count_matches(keywords, text):
        """Count how many keywords match in text."""
        return sum(1 for kw in keywords if kw in text)
    
    # Подсчитываем совпадения для каждой категории
    legal_matches = count_matches(legal_keywords, text)
    conflict_matches = count_matches(conflict_keywords, text)
    business_matches = count_matches(business_keywords, text)
    science_matches = count_matches(science_keywords, text)
    society_matches = count_matches(society_keywords, text)
    tech_matches = count_matches(tech_keywords, text)
    politics_matches = count_matches(politics_keywords, text)
    
    # Находим категорию с максимальным количеством совпадений
    category_scores = {
        'legal': legal_matches,
        'conflict': conflict_matches,
        'business': business_matches,
        'science': science_matches,
        'society': society_matches,
        'tech': tech_matches,
        'politics': politics_matches
    }
    
    # Если есть совпадения, возвращаем категорию с наибольшим количеством
    max_score = max(category_scores.values())
    if max_score > 0:
        # Если несколько категорий имеют одинаковый максимум, выбираем по приоритету
        for category in ['legal', 'conflict', 'business', 'science', 'society', 'tech', 'politics']:
            if category_scores[category] == max_score:
                return category
    
    # Если нет совпадений, возвращаем general
    return 'general'


@app.post("/api/news/translate")
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


@app.post("/api/rutube/generate")
async def generate_text_from_rutube(
    request: RutubeGenerateRequest
):
    """Generate text from Rutube video."""
    try:
        # Import here to avoid errors if dependencies missing
        from ..ingest.rutube_processor import process_rutube_video, validate_rutube_url
        from ..nlp.transcriber import transcribe_audio, detect_language
        import asyncio
        from pathlib import Path
        import shutil
        
        url = request.url
        if not validate_rutube_url(url):
            raise HTTPException(status_code=400, detail="Invalid Rutube URL")
        
        temp_dir = None
        try:
            logger.info(f"Processing Rutube video: {url}")
            video_path, audio_path, video_info = await asyncio.to_thread(
                process_rutube_video, url
            )
            temp_dir = video_path.parent
            
            # Detect language
            try:
                audio_path_obj = Path(audio_path) if not isinstance(audio_path, Path) else audio_path
                language = await asyncio.to_thread(detect_language, audio_path_obj, "base")
                lang_code = "ru" if language == "ru" else "en"
            except:
                language = None
                lang_code = "auto"
            
            # Transcribe
            audio_path_obj = Path(audio_path) if not isinstance(audio_path, Path) else audio_path
            transcript_result = await asyncio.to_thread(
                transcribe_audio,
                audio_path_obj,
                language=language,
                model_size="base"
            )
            transcript = transcript_result["text"]
            detected_lang = transcript_result.get("language", language or "en")
            lang_code = "ru" if detected_lang == "ru" else "en"
            
            return {
                "success": True,
                "video_info": video_info,
                "transcript": transcript,
                "language": lang_code,
                "transcript_length": len(transcript)
            }
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    await asyncio.to_thread(shutil.rmtree, temp_dir, ignore_errors=True)
                except:
                    pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rutube processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")


@app.post("/api/tts/generate")
async def generate_tts(request: TTSGenerateRequest):
    """
    Generate audio from text using TTS with automatic fallback.
    
    Args:
        request: TTS generation request with text, language, voice_gender, provider
        
    Returns:
        Dictionary with audio information and URL
    """
    try:
        # Additional validation (in case Pydantic validation didn't catch it)
        text = request.text.strip() if request.text else ""
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Text cannot be empty"
            )
        
        # Limit text length
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        logger.info(
            f"Generating TTS: length={len(text)}, "
            f"language={request.language}, voice_gender={request.voice_gender}, "
            f"provider={request.provider or 'default'}"
        )
        
        # Generate audio (run in thread pool for pyttsx3 to avoid blocking)
        import asyncio
        result = await asyncio.to_thread(
            tts_service.generate_audio,
            text=text,
            language=request.language if request.language != 'auto' else None,
            voice_gender=request.voice_gender,
            provider=request.provider
        )
        
        return {
            "success": True,
            **result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate TTS: {str(e)}"
        )


@app.get("/api/tts/audio/{audio_id}")
async def get_tts_audio(audio_id: str):
    """
    Get TTS audio file by ID.
    
    Args:
        audio_id: Audio file ID
        
    Returns:
        Audio file (MP3)
    """
    try:
        audio_path = tts_service.get_audio_path(audio_id)
        
        if not audio_path or not audio_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Audio file not found: {audio_id}"
            )
        
        # Determine MIME type from file extension
        mime_type, _ = mimetypes.guess_type(str(audio_path))
        if not mime_type:
            # Default to audio/mpeg for MP3 files
            if audio_path.suffix.lower() == '.mp3':
                mime_type = "audio/mpeg"
            elif audio_path.suffix.lower() == '.wav':
                mime_type = "audio/wav"
            else:
                mime_type = "application/octet-stream"
        
        return FileResponse(
            path=str(audio_path),
            media_type=mime_type,
            filename=f"{audio_id}{audio_path.suffix}",
            headers={
                "Content-Disposition": f'attachment; filename="{audio_id}{audio_path.suffix}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting TTS audio: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audio: {str(e)}"
        )


@app.get("/api/tts/stats")
async def get_tts_stats():
    """
    Get TTS service statistics including cache info.
    
    Returns:
        Dictionary with TTS statistics
    """
    try:
        stats = tts_service.get_cache_stats()
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting TTS stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


# ============================================================
# Email Endpoints
# ============================================================

@app.post("/api/email/send")
async def send_email(request: EmailSendRequest):
    """
    Send email to recipient.
    
    Args:
        request: Email send request with to_email, subject, content
        
    Returns:
        Success status
    """
    try:
        success = email_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        return {
            "success": True,
            "message": "Email sent successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email sending error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@app.post("/api/email/digest")
async def send_daily_digest(request: EmailDigestRequest):
    """
    Send daily news digest email.
    
    Args:
        request: Digest request with to_email and language
        
    Returns:
        Success status
    """
    try:
        # Get top news items
        from ..ingest.news_sources_async import AsyncNewsAggregator
        async with AsyncNewsAggregator(timeout=NEWS_FETCH_TIMEOUT) as aggregator:
            news_items = await aggregator.fetch_trending_topics(
                include_russian=True,
                include_international=True,
                max_per_source=NEWS_MAX_PER_SOURCE
            )
        
        # Limit to top 5
        news_items = news_items[:5]
        
        success = await email_service.send_daily_digest_async(
            to_email=request.to_email,
            news_items=news_items,
            language=request.language
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send daily digest"
            )
        
        return {
            "success": True,
            "message": "Daily digest sent successfully",
            "items_count": len(news_items)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily digest error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send daily digest: {str(e)}"
        )


@app.get("/api/email/status")
async def get_email_status():
    """
    Get email service status.
    
    Returns:
        Email service availability status
    """
    return {
        "success": True,
        "enabled": email_service.is_available(),
        "configured": bool(EMAIL_SMTP_USER and EMAIL_SMTP_PASSWORD)
    }


# ============================================================
# Telegram Endpoints
# ============================================================

@app.post("/api/telegram/post")
async def post_to_telegram(request: TelegramPostRequest):
    """
    Post article to Telegram channel.
    
    Args:
        request: Telegram post request with article and options
        
    Returns:
        Success status with message ID
    """
    try:
        if not telegram_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Telegram service is not available. Check configuration."
            )
        
        success = await telegram_service.post_article(
            article=request.article,
            channel_id=request.channel_id,
            format_type=request.format_type
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to post to Telegram"
            )
        
        return {
            "success": True,
            "message": "Posted to Telegram successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram posting error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post to Telegram: {str(e)}"
        )


@app.get("/api/telegram/test")
async def test_telegram_connection():
    """
    Test Telegram bot connection.
    
    Returns:
        Connection status
    """
    try:
        if not telegram_service.is_available():
            return {
                "success": False,
                "message": "Telegram service is not configured",
                "available": False
            }
        
        connected = await telegram_service.test_connection()
        
        return {
            "success": connected,
            "message": "Connected successfully" if connected else "Connection failed",
            "available": telegram_service.is_available()
        }
    except Exception as e:
        logger.error(f"Telegram test error: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "available": False
        }


@app.get("/api/telegram/status")
async def get_telegram_status():
    """
    Get Telegram service status.
    
    Returns:
        Telegram service availability status
    """
    return {
        "success": True,
        "enabled": telegram_service.is_available(),
        "configured": bool(TELEGRAM_BOT_TOKEN),
        "default_channel": TELEGRAM_CHANNEL_ID
    }


# ============================================================
# Database Management Endpoints
# ============================================================

@app.post("/api/db/cleanup")
async def cleanup_database(
    keep_count: int = Query(default=10000, ge=1000, le=100000, description="Number of records to keep")
):
    """
    Cleanup database, keeping only the most recent N records.
    
    Args:
        keep_count: Number of most recent records to keep (default: from config, min: 1000, max: 100000)
    
    Returns:
        Cleanup statistics
    """
    try:
        if keep_count is None:
            keep_count = NEWS_DB_MAX_RECORDS
        with NewsDatabase() as db:
            # Get statistics before cleanup
            stats_before = db.get_statistics()
            total_before = stats_before.get('total_items', 0)
            
            # Perform cleanup
            deleted_count = db.cleanup_old_records(keep_count=keep_count)
            
            # Get statistics after cleanup
            stats_after = db.get_statistics()
            total_after = stats_after.get('total_items', 0)
            
            logger.info(f"Database cleanup completed: kept {total_after} records, deleted {deleted_count} records")
            
            return {
                "success": True,
                "message": f"Database cleanup completed successfully",
                "kept_records": total_after,
                "deleted_records": deleted_count,
                "total_before": total_before,
                "total_after": total_after,
                "keep_limit": keep_count
            }
    except Exception as e:
        logger.error(f"Database cleanup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup database: {str(e)}"
        )


@app.get("/api/db/stats")
async def get_database_stats():
    """
    Get database statistics.
    
    Returns:
        Database statistics including total records count
    """
    try:
        with NewsDatabase() as db:
            stats = db.get_statistics()
            return {
                "success": True,
                **stats
            }
    except Exception as e:
        logger.error(f"Database stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database statistics: {str(e)}"
        )

