"""
FastAPI application for Trendoscope.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
import os

from ..gen.generate import generate_summary
from ..pipeline.orchestrator import run_pipeline
from ..gen.post_generator import generate_post_from_storage, get_available_styles
from ..ingest.news_sources import NewsAggregator
from ..nlp.controversy_scorer import ControversyScorer
from ..nlp.translator import translate_and_summarize_news

app = FastAPI(
    title="Trendoscope API",
    description="Analyze LiveJournal posts and generate viral content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def generate(
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


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "trendoscope"}


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
async def get_news_feed(
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
    translate: bool = Query(
        default=True,
        description="Translate English news to Russian"
    )
):
    """
    Get news feed with controversy scoring.
    
    Args:
        category: Filter by category
        limit: Maximum items
        translate: Translate English to Russian
    
    Returns:
        List of scored news items
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Fetching news: category={category}, limit={limit}")
        
        # Determine which sources to include
        include_ai = category in ['all', 'ai']
        include_politics = category in ['all', 'politics']
        include_us = category in ['all', 'us']
        include_eu = category in ['all', 'eu']
        include_russia = category in ['all', 'russia']
        
        # Fetch news
        aggregator = NewsAggregator()
        news_items = aggregator.fetch_trending_topics(
            include_ai=include_ai,
            include_politics=include_politics,
            include_us=include_us,
            include_eu=include_eu,
            include_russian=include_russia,
            max_per_source=3
        )
        
        logger.info(f"Fetched {len(news_items)} news items")
        
        # Translate if requested
        if translate and news_items:
            try:
                news_items = translate_and_summarize_news(
                    news_items,
                    provider="openai"
                )
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
        
        # Sort by controversy score (hot first)
        scored_items.sort(
            key=lambda x: x['controversy']['score'],
            reverse=True
        )
        
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
    """Categorize news item based on content."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    
    # AI/ML keywords
    ai_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'neural',
        'gpt', 'chatgpt', 'llm', 'нейросет', 'ии', 'искусственный интеллект'
    ]
    
    # Politics keywords
    politics_keywords = [
        'politics', 'government', 'election', 'president', 'minister',
        'политик', 'правительств', 'выборы', 'президент', 'министр'
    ]
    
    # US keywords
    us_keywords = [
        'usa', 'america', 'washington', 'biden', 'trump', 'congress',
        'сша', 'америк', 'вашингтон'
    ]
    
    # EU keywords
    eu_keywords = [
        'europe', 'european union', 'brussels', 'eu',
        'европ', 'брюссель', 'евросоюз'
    ]
    
    # Russia keywords
    russia_keywords = [
        'russia', 'moscow', 'putin', 'kremlin',
        'россия', 'москва', 'путин', 'кремль'
    ]
    
    # Check categories (order matters - specific to general)
    if any(kw in text for kw in ai_keywords):
        return 'ai'
    elif any(kw in text for kw in us_keywords):
        return 'us'
    elif any(kw in text for kw in eu_keywords):
        return 'eu'
    elif any(kw in text for kw in russia_keywords):
        return 'russia'
    elif any(kw in text for kw in politics_keywords):
        return 'politics'
    else:
        return 'general'


@app.post("/api/post/generate")
async def generate_post_endpoint(
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
        description="Model name"
    ),
    temperature: float = Query(
        default=0.8,
        description="Generation temperature"
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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from ..gen.post_generator import generate_post_from_storage
        
        logger.info(f"Generating post: style={style}, topic={topic}, provider={provider}")

        result = generate_post_from_storage(
            style=style,
            topic=topic,
            provider=provider,
            model=model,
            temperature=temperature
        )
        
        logger.info(f"Post generated successfully: {result.get('title', 'No title')[:50]}")

        return result

    except Exception as e:
        logger.error(f"Post generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Post generation failed: {str(e)}"
        )
