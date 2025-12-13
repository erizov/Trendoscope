"""
FastAPI application for Trendoscope.
"""
from fastapi import FastAPI, HTTPException, Query, Request, Depends, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
import os
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..gen.generate import generate_summary
from ..pipeline.orchestrator import run_pipeline
from ..gen.post_generator import generate_post_from_storage, get_available_styles
from ..ingest.news_sources import NewsAggregator
from ..nlp.controversy_scorer import ControversyScorer
from ..nlp.translator import translate_and_summarize_news
from ..storage.news_db import NewsDatabase
from ..services.news_service import NewsService
from ..services.post_service import PostService
from ..utils.response import APIResponse
from ..utils.logger import setup_logging, get_logger
from ..core.dependencies import get_news_service, get_post_service, get_config
from ..core.settings import get_settings
from ..core.health import (
    get_health_checker,
    check_database,
    check_cache,
    check_openai_provider,
    check_anthropic_provider,
    check_translator
)
from ..core.exceptions import (
    TrendoscopeException,
    ServiceUnavailableError,
    LLMProviderError
)
from ..core.error_handler import (
    trendoscope_exception_handler,
    general_exception_handler
)

# Setup structured logging
settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Trendoscope API",
    description="Analyze LiveJournal posts and generate viral content",
    version="2.2.0",
    default_response_class=JSONResponse
)

# Ensure UTF-8 encoding for all responses
@app.middleware("http")
async def add_utf8_header(request: Request, call_next):
    """Add UTF-8 charset to all responses."""
    response = await call_next(request)
    if "content-type" in response.headers:
        content_type = response.headers["content-type"]
        if "charset" not in content_type.lower():
            response.headers["content-type"] = f"{content_type}; charset=utf-8"
    else:
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom exception handlers
app.add_exception_handler(TrendoscopeException, trendoscope_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
try:
    from .posts import router as posts_router
    # Set limiter on posts router
    posts_router.limiter = limiter
    app.include_router(posts_router)
except ImportError as e:
    logger.warning(f"Could not import posts router: {e}")

try:
    from .cost_analytics import router as analytics_router
    app.include_router(analytics_router)
except ImportError as e:
    logger.warning(f"Could not import analytics router: {e}")

try:
    from .post_editing import router as editing_router
    app.include_router(editing_router)
except ImportError as e:
    logger.warning(f"Could not import post editing router: {e}")

# WebSocket endpoint
try:
    from .websocket import websocket_endpoint
    app.websocket("/ws")(websocket_endpoint)
except ImportError as e:
    logger.warning(f"Could not import websocket: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add to logger context
    logger.info(
        "request_started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": get_remote_address(request)
        }
    )
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code
        }
    )
    
    return response

# Serve static files (frontend)
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "frontend"
)
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>Trendoscope</title></head>
        <body>
            <h1>Trendoscope API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


@app.post("/api/generate/summary")
async def generate(
    request: Request,
    items: List[Dict],
    mode: str = "logospheric",
    provider: str = "demo",
    model: Optional[str] = None
):
    """
    Generate summary from posts.

    Args:
        items: List of analyzed posts
        mode: Generation mode (analytical, provocative, humorous, etc.)
        provider: LLM provider (openai, anthropic, local, demo)
        model: Model name (optional)

    Returns:
        Generated summary with titles, ideas, and viral potential
    """
    try:
        return generate_summary(
            items,
            mode=mode,
            provider=provider,
            model=model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/run")
async def run_full_pipeline(
    blog_url: str = Query(
        default="https://civil-engineer.livejournal.com",
        description="LiveJournal blog URL"
    ),
    max_posts: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of posts to fetch"
    ),
    mode: str = Query(
        default="logospheric",
        description="Generation mode"
    ),
    provider: str = Query(
        default="demo",
        description="LLM provider"
    ),
    model: Optional[str] = Query(
        default=None,
        description="Model name"
    )
):
    """
    Run full Trendoscope pipeline.

    This endpoint:
    1. Fetches posts from LiveJournal
    2. Analyzes them with NLP
    3. Indexes in vector database
    4. Extracts trending topics
    5. Generates content recommendations

    Returns:
        Complete pipeline results including posts, trends, and generated content
    """
    try:
        result = run_pipeline(
            blog_url=blog_url,
            max_posts=max_posts,
            mode=mode,
            provider=provider,
            model=model
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )


@app.get("/favicon.ico")
async def favicon():
    """Return favicon (simple 204 to avoid 404 errors)."""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/metrics")
async def get_metrics_endpoint():
    """Get application metrics."""
    from ..utils.monitoring import get_metrics
    return get_metrics()


@app.get("/api/balance/check")
async def check_balance(
    provider: str = Query(default="openai", description="Provider to check")
):
    """Check AI provider balance."""
    has_balance, error = check_provider_balance(provider)
    return {
        "provider": provider,
        "has_balance": has_balance,
        "error": error,
        "recommended_provider": "demo" if not has_balance else provider
    }


@app.get("/api/health")
async def health():
    """
    Comprehensive health check endpoint.
    
    Checks:
    - Database connectivity
    - Cache availability
    - LLM providers
    - Translation service
    """
    health_checker = get_health_checker()
    
    # Register health checks on first call
    if not health_checker._checks:
        health_checker.register("database", check_database)
        health_checker.register("cache", check_cache)
        health_checker.register("openai", check_openai_provider)
        health_checker.register("anthropic", check_anthropic_provider)
        health_checker.register("translator", check_translator)
    
    # Run all checks
    results = await health_checker.check_all()
    overall_status = await health_checker.check_overall()
    
    return {
        "status": overall_status.value,
        "checks": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "details": result.details,
                "timestamp": result.timestamp.isoformat()
            }
            for name, result in results.items()
        }
    }


@app.get("/api/modes")
async def get_modes():
    """Get available generation modes."""
    import json
    prompts_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "gen",
        "prompts.json"
    )
    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    return {
        "modes": [
            {"name": name, "description": data["description"]}
            for name, data in prompts.items()
        ]
    }


@app.get("/api/post/styles")
async def get_post_styles():
    """Get available post generation styles."""
    from ..gen.post_generator import get_available_styles
    return {"styles": get_available_styles()}


@app.get("/api/style/status")
async def get_style_status():
    """Check if style guide is available."""
    from ..storage.style_storage import has_saved_style, load_style_guide

    has_style = has_saved_style()
    style_data = None

    if has_style:
        style_data = load_style_guide()

    return {
        "has_style": has_style,
        "blog_url": style_data.get("blog_url") if style_data else None,
        "saved_at": style_data.get("saved_at") if style_data else None,
        "post_count": len(style_data.get("style", {}).get("common_phrases", [])) if style_data else 0
    }


@app.get("/api/news/feed")
@limiter.limit("30/minute")
async def get_news_feed(
    request: Request,
    category: str = Query(
        default="all",
        description="Category filter (all, ai, politics, us, eu, russia)"
    ),
    limit: int = Query(
        default=20,
        ge=5,
        le=100,
        description="Maximum news items to return"
    ),
    language: str = Query(
        default="all",
        description="Language filter - show only articles in this language (all, ru, en)"
    ),
    translate_to: str = Query(
        default="none",
        description="Translate articles to target language (none, ru, en)"
    )
):
    """
    Get news feed with controversy scoring.
    
    Args:
        category: Filter by category
        limit: Maximum items
        language: Show only articles in this language (all, ru, en)
        translate_to: Translate articles to target language (none, ru, en)
    
    Returns:
        List of scored news items
    """
    
    try:
        logger.info(f"Fetching news: category={category}, limit={limit}, language={language}, translate_to={translate_to}")
        
        # Map new categories to source types
        category_map = {
            'tech': {'ai': True, 'russian': True},
            'business': {'russian': True, 'international': True},
            'politics': {'politics': True, 'us': True, 'russian': True},
            'conflict': {'politics': True, 'international': True},
            'legal': {'legal': True, 'international': True, 'russian': True},
            'society': {'russian': True, 'international': True},
            'science': {'ai': True, 'international': True},
            'all': {'ai': True, 'politics': True, 'us': True, 'eu': True, 
                   'russian': True, 'international': True, 'legal': True}
        }
        
        # Get source flags for category
        sources = category_map.get(category, category_map['all'])
        
        # Fetch news with parallel fetching (fast!)
        aggregator = NewsAggregator(timeout=5)  # 5 second timeout per source
        news_items = aggregator.fetch_trending_topics(
            include_ai=sources.get('ai', False),
            include_politics=sources.get('politics', False),
            include_us=sources.get('us', False),
            include_eu=sources.get('eu', False),
            include_russian=sources.get('russian', False),
            include_international=sources.get('international', False),
            include_legal=sources.get('legal', False),
            max_per_source=2,  # Reduced for speed
            parallel=True,  # Enable parallel fetching
            max_workers=10  # 10 parallel requests
        )
        
        logger.info(f"Fetched {len(news_items)} news items")
        
        # Filter out invalid/empty articles
        from ..utils.news_validator import is_valid_article
        news_items = [item for item in news_items if is_valid_article(item)]
        logger.info(f"After validation: {len(news_items)} valid news items")
        
        # Detect and set language for each item (based on entire article, not words)
        for item in news_items:
            # Detect language based on entire article content
            title = item.get('title', '')
            summary = item.get('summary', '')
            full_text = item.get('full_text', '')
            text = f"{title} {summary} {full_text}"
            
            # Language detection: count Cyrillic vs Latin characters
            cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
            latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
            total_chars = cyrillic_chars + latin_chars
            
            if total_chars > 0:
                cyrillic_ratio = cyrillic_chars / total_chars
                # If more than 30% Cyrillic, consider it Russian
                if cyrillic_ratio > 0.3:
                    item['language'] = 'ru'
                else:
                    item['language'] = 'en'
            else:
                # Default to English if no text
                item['language'] = 'en'
        
        # Filter by language - show complete articles only in selected language
        if language != 'all':
            original_count = len(news_items)
            news_items = [
                item for item in news_items
                if item.get('language') == language
            ]
            logger.info(f"Filtered to {len(news_items)} complete articles for language={language} (from {original_count})")
        
        # Translate if requested (translate_to is not 'none')
        if translate_to != 'none' and news_items:
            try:
                # Only translate items that are NOT already in target language
                items_to_translate = [
                    item for item in news_items
                    if item.get('language') != translate_to
                ]
                
                if items_to_translate:
                    # Limit translation to 3 items at a time for speed
                    max_translate = min(len(items_to_translate), 3)
                    items_to_translate_limited = items_to_translate[:max_translate]
                    items_not_translated = items_to_translate[max_translate:]
                    
                    logger.info(f"Translating {max_translate} items to {translate_to} using free translator (limited from {len(items_to_translate)})")
                    # Use free translator, limit to 3 items for speed
                    translated = translate_and_summarize_news(
                        items_to_translate_limited,
                        target_language=translate_to,
                        provider="free",  # Use free translator
                        max_items=3  # Limit to 3 items for speed
                    )
                    
                    # Add non-translated items back (they keep original language)
                    translated.extend(items_not_translated)
                    
                    # Update translated items in the list
                    translated_map = {item.get('link'): item for item in translated}
                    for i, item in enumerate(news_items):
                        if item.get('link') in translated_map:
                            news_items[i] = translated_map[item.get('link')]
                            news_items[i]['language'] = translate_to
            except Exception as e:
                logger.warning(f"Translation failed: {e}, continuing without translation")
        
        # Categorize news
        for item in news_items:
            item['category'] = _categorize_news(item)
        
        # Filter by category if not 'all'
        if category != 'all':
            news_items = [
                item for item in news_items
                if item['category'] == category
            ]
        
        # Score for controversy
        scorer = ControversyScorer()
        scored_items = scorer.score_batch(news_items)
        
        # Add fetch timestamp to each item (for sorting by recency)
        from datetime import datetime
        import time
        fetch_timestamp = time.time()  # Unix timestamp for accurate sorting
        
        for item in scored_items:
            # Add fetched_at timestamp (when we fetched/generated this news)
            # Use Unix timestamp for accurate numeric sorting
            if 'fetched_at' not in item:
                item['fetched_at'] = fetch_timestamp
            elif isinstance(item.get('fetched_at'), str):
                # Convert ISO string to timestamp if needed
                try:
                    item['fetched_at'] = datetime.fromisoformat(
                        item['fetched_at'].replace('Z', '+00:00')
                    ).timestamp()
                except:
                    item['fetched_at'] = fetch_timestamp
            # Ensure published field exists for sorting
            if 'published' not in item or not item['published']:
                item['published'] = item.get('published_at', '')
        
        # Sort by most recent first (fetched_at timestamp, then published date)
        # This ensures last generated news appears on top
        def sort_key(item):
            # Primary: fetched_at timestamp (when we generated it) - higher = newer
            fetched = item.get('fetched_at', 0)
            if isinstance(fetched, str):
                try:
                    fetched = datetime.fromisoformat(
                        fetched.replace('Z', '+00:00')
                    ).timestamp()
                except:
                    fetched = 0
            
            # Secondary: published date (from RSS feed) - for tie-breaking
            published = item.get('published', '') or item.get('published_at', '')
            # Convert published string to comparable value
            published_sort = published if published else ''
            
            return (fetched, published_sort)
        
        scored_items.sort(key=sort_key, reverse=True)  # Most recent first
        
        # Limit results
        scored_items = scored_items[:limit]
        
        logger.info(f"Returning {len(scored_items)} scored items")
        
        return {
            'success': True,
            'count': len(scored_items),
            'category': category,
            'news': scored_items
        }
        
    except Exception as e:
        logger.error(f"News feed error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news: {str(e)}"
        )


def _categorize_news(item: Dict[str, Any]) -> str:
    """Categorize news item based on content - 8 main categories."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    
    # Legal & Criminal (courts, law, crime, justice)
    legal_keywords = [
        'court', 'judge', 'lawyer', 'attorney', 'trial', 'verdict', 'sentenced', 'conviction',
        'criminal', 'crime', 'arrest', 'police', 'investigation', 'lawsuit', 'legal',
        'justice', 'prison', 'jail', 'prosecutor', 'defendant', 'case', 'ruling',
        'суд', 'судья', 'адвокат', 'прокурор', 'приговор', 'уголовн', 'преступ',
        'полиц', 'следств', 'дело', 'обвинение', 'оправдан', 'тюрьма', 'арест',
        'юрист', 'право', 'закон', 'нарушение', 'расследование', 'обыск'
    ]
    
    # Tech (AI, ML, technology, platforms, internet)
    tech_keywords = [
        'ai', 'artificial', 'intelligence', 'gpt', 'neural', 'machine', 'learning',
        'tech', 'technology', 'algorithm', 'data', 'digital', 'internet', 'platform',
        'cloud', 'software', 'app', 'ии', 'нейросет', 'технолог', 'алгоритм', 'данные',
        'telegram', 'google', 'microsoft', 'apple', 'meta', 'программ', 'код'
    ]
    
    # Business & Economy
    business_keywords = [
        'market', 'stock', 'economy', 'business', 'company', 'startup',
        'investment', 'ceo', 'бизнес', 'компани', 'рынок', 'экономик',
        'стартап', 'инвестиц', 'акци', 'финанс', 'банк', 'валют'
    ]
    
    # War & Conflict
    conflict_keywords = [
        'war', 'military', 'army', 'weapon', 'conflict', 'attack', 'defense',
        'война', 'военн', 'армия', 'оружи', 'конфликт', 'удар', 'атак', 'оборон'
    ]
    
    # Politics (general, any country)
    politics_keywords = [
        'politics', 'government', 'election', 'president', 'minister', 'congress',
        'политик', 'правительств', 'выборы', 'президент', 'министр', 'партия',
        'biden', 'trump', 'putin', 'путин', 'parliament', 'senate'
    ]
    
    # Society (social issues, people, rights)
    society_keywords = [
        'social', 'people', 'society', 'protest', 'rights',
        'социальн', 'общество', 'люди', 'права', 'справедлив'
    ]
    
    # Science & Research
    science_keywords = [
        'science', 'research', 'study', 'university', 'scientist', 'discovery',
        'наука', 'исследован', 'ученые', 'университет', 'открыти', 'experiment',
        'climate', 'energy', 'environment', 'климат', 'энергия', 'экология'
    ]
    
    # Check categories (order matters - most specific first)
    if any(kw in text for kw in legal_keywords):
        return 'legal'
    elif any(kw in text for kw in conflict_keywords):
        return 'conflict'
    elif any(kw in text for kw in tech_keywords):
        return 'tech'
    elif any(kw in text for kw in business_keywords):
        return 'business'
    elif any(kw in text for kw in politics_keywords):
        return 'politics'
    elif any(kw in text for kw in science_keywords):
        return 'science'
    elif any(kw in text for kw in society_keywords):
        return 'society'
    else:
        return 'general'


@app.post("/api/post/generate")
async def generate_post_endpoint(
    request: Request,
    style: str = Query(
        default="philosophical",
        description="Post style"
    ),
    topic: str = Query(
        default="any",
        description="Post topic focus"
    ),
    provider: str = Query(
        default="openai",
        description="LLM provider"
    ),
    model: Optional[str] = Query(
        default=None,
        description="Model name (overrides quality tier)"
    ),
    quality: str = Query(
        default="standard",
        description="Quality tier: draft (cheap), standard (balanced), premium (best)"
    ),
    temperature: float = Query(
        default=0.8,
        description="Generation temperature"
    ),
    translate: bool = Query(
        default=True,
        description="Translate English news to Russian (set false to save costs)"
    ),
    author_style: Optional[str] = Query(
        default=None,
        description="Author style (tolstoy, dostoevsky, pushkin, lermontov, turgenev, leskov, mark_twain, faulkner)"
    )
):
    """
    Generate a new post in author's style based on trending news.

    Args:
        style: Post style (philosophical, ironic, analytical, provocative)
        topic: Topic focus (any, ai, politics, us_affairs, russian_history, science)
        provider: LLM provider
        model: Model name
        temperature: Generation temperature

    Returns:
        Generated post with title, text, and tags
    """
    try:
        from ..gen.post_generator import generate_post_from_storage
        from ..gen.model_selector import select_model_for_task
        
        logger.info(f"Generating post: style={style}, topic={topic}, provider={provider}, quality={quality}")
        
        # Select model based on quality tier if not specified
        if not model:
            model_config = select_model_for_task("post_generation", quality, provider)
            model = model_config["model"]
            # Override temperature and max_tokens if using quality tier
            if quality in ["draft", "standard", "premium"]:
                temperature = model_config.get("temperature", temperature)
        
        # Set translation preference
        import os
        if not translate:
            os.environ["SKIP_TRANSLATION"] = "true"
        else:
            os.environ.pop("SKIP_TRANSLATION", None)

        result = generate_post_from_storage(
            style=style,
            topic=topic,
            provider=provider,
            model=model,
            temperature=temperature
        )
        
        # Track cost if using AI provider
        if provider in ["openai", "anthropic"]:
            try:
                from ..gen.cost_tracker import track_call
                from ..utils.prometheus_metrics import record_llm_call
                # Estimate tokens (rough calculation)
                prompt_len = len(str(result.get("title", "")) + str(result.get("text", "")))
                estimated_tokens_in = prompt_len // 4  # Rough estimate
                estimated_tokens_out = len(result.get("text", "")) // 4
                cost = track_call(provider, model, estimated_tokens_in, estimated_tokens_out)
                result["cost_estimate"] = f"${cost:.4f}"
                record_llm_call(provider, model, cost)
            except Exception:
                pass  # Don't fail if cost tracking fails
        
        logger.info(f"Post generated successfully: {result.get('title', 'No title')[:50]}")
        
        # Broadcast via WebSocket if available
        try:
            from .websocket import manager
            await manager.broadcast_post_update(result)
        except Exception:
            pass  # WebSocket not critical
        
        # Track metrics
        try:
            from ..utils.prometheus_metrics import increment_endpoint_counter
            increment_endpoint_counter("/api/post/generate", 200)
        except Exception:
            pass

        return result

    except Exception as e:
        logger.error(f"Post generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Post generation failed: {str(e)}"
        )


@app.get("/api/news/search")
async def search_news_in_db(
    query: str = Query(..., description="Search phrase in Russian or English"),
    category: str = Query(default="all", description="Filter by category"),
    limit: int = Query(default=20, le=100, description="Max results"),
    min_controversy: Optional[int] = Query(
        default=None,
        description="Minimum controversy score (0-100)"
    )
):
    """
    Full-text search in news database.
    
    Supports:
    - Russian and English keywords
    - Phrase search (use quotes)
    - Category filtering
    - Controversy filtering
    
    Example queries:
    - "программист AI"
    - "truck driver conviction"
    - "суд приговор"
    """
    try:
        with NewsDatabase() as db:
            results = db.search(
                query,
                category=category if category != 'all' else None,
                limit=limit,
                min_controversy=min_controversy
            )
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/api/news/translate")
@limiter.limit("20/minute")
async def translate_article(
    request: Request,
    article: Dict[str, Any] = Body(...)
):
    """
    Translate a single article.
    
    Request body:
    {
        "title": "Article title",
        "summary": "Article summary",
        "source_language": "en",
        "target_language": "ru"
    }
    
    Returns:
    {
        "success": true,
        "translated": {
            "title": "Translated title",
            "summary": "Translated summary"
        }
    }
    """
    try:
        title = article.get('title', '')
        summary = article.get('summary', '')
        source_lang = article.get('source_language', 'en')
        target_lang = article.get('target_language', 'ru')
        
        if not title and not summary:
            raise HTTPException(
                status_code=400,
                detail="Title or summary required"
            )
        
        # Create a single-item list for translation
        news_item = {
            'title': title,
            'summary': summary,
            'language': source_lang
        }
        
        # Translate using free translator (limit to 1 item)
        translated_items = translate_and_summarize_news(
            [news_item],
            target_language=target_lang,
            provider="free",
            max_items=1
        )
        
        if not translated_items or len(translated_items) == 0:
            raise HTTPException(
                status_code=500,
                detail="Translation failed"
            )
        
        translated = translated_items[0]
        
        return {
            "success": True,
            "translated": {
                "title": translated.get('title', title),
                "summary": translated.get('summary', summary)
            }
        }
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@app.get("/api/news/db/stats")
async def get_database_stats():
    """
    Get news database statistics.
    
    Returns:
    - Total items count
    - Items per category
    - Top sources
    - Controversy distribution
    """
    try:
        with NewsDatabase() as db:
            stats = db.get_statistics()
        
        return {
            'success': True,
            'stats': stats
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stats retrieval failed: {str(e)}"
        )


@app.get("/api/news/trending/keywords")
async def get_trending_keywords(
    limit: int = Query(default=20, le=50, description="Max keywords")
):
    """
    Get trending keywords from stored news.
    
    Useful for:
    - Tag clouds
    - Trending topics
    - Popular themes
    """
    try:
        with NewsDatabase() as db:
            keywords = db.get_trending_keywords(limit=limit)
        
        return {
            'success': True,
            'count': len(keywords),
            'keywords': keywords
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trending keywords failed: {str(e)}"
        )


@app.get("/api/news/db/recent")
async def get_recent_news_from_db(
    category: str = Query(default="all", description="Filter by category"),
    limit: int = Query(default=20, le=100, description="Max results"),
    min_controversy: Optional[int] = Query(
        default=None,
        description="Minimum controversy score"
    )
):
    """
    Get recent news from database.
    
    Much faster than fetching from RSS feeds.
    """
    try:
        with NewsDatabase() as db:
            results = db.get_recent(
                category=category if category != 'all' else None,
                limit=limit,
                min_controversy=min_controversy
            )
        
        return {
            'success': True,
            'count': len(results),
            'results': results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recent news retrieval failed: {str(e)}"
        )


@app.get("/api/news/db/controversial")
async def get_controversial_news_from_db(
    category: str = Query(default="all", description="Filter by category"),
    limit: int = Query(default=10, le=50, description="Max results"),
    days: Optional[int] = Query(
        default=None,
        description="Only from last N days"
    )
):
    """
    Get most controversial news from database.
    """
    try:
        with NewsDatabase() as db:
            results = db.get_top_controversial(
                category=category if category != 'all' else None,
                limit=limit,
                days=days
            )
        
        return {
            'success': True,
            'count': len(results),
            'results': results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Controversial news retrieval failed: {str(e)}"
        )


@app.post("/api/news/db/store")
async def store_news_batch(
    request: Request,
    fetch_fresh: bool = Query(
        default=True,
        description="Fetch fresh news or use dummy data"
    )
):
    """
    Fetch and store news in database.
    
    This endpoint:
    1. Fetches news from RSS feeds
    2. Scores controversy
    3. Translates to Russian
    4. Stores in database
    
    Run this periodically to keep database updated.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if fetch_fresh:
            logger.info("Fetching fresh news from RSS feeds...")
            
            # Fetch news
            aggregator = NewsAggregator(timeout=5)
            news_items = aggregator.fetch_trending_topics(
                include_russian=True,
                include_ai=True,
                max_per_source=2,
                parallel=True
            )
            
            logger.info(f"Fetched {len(news_items)} items")
            
            # Score controversy
            scorer = ControversyScorer()
            scored_items = scorer.score_batch(news_items)
            
            # Store in database
            with NewsDatabase() as db:
                inserted = db.bulk_insert(scored_items)
                stats = db.get_statistics()
            
            return {
                'success': True,
                'fetched': len(news_items),
                'inserted': inserted,
                'total_in_db': stats['total_items']
            }
        
        else:
            # Just return current stats
            with NewsDatabase() as db:
                stats = db.get_statistics()
            
            return {
                'success': True,
                'message': 'No fetch requested',
                'total_in_db': stats['total_items']
            }
    
    except Exception as e:
        logger.error(f"Store news failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Store news failed: {str(e)}"
        )
