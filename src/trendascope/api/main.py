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
        
        # Map new categories to source types
        category_map = {
            'tech': {'ai': True, 'russian': True},
            'business': {'russian': True, 'international': True},
            'politics': {'politics': True, 'us': True, 'russian': True},
            'conflict': {'politics': True, 'international': True},
            'society': {'russian': True, 'international': True},
            'science': {'ai': True, 'international': True},
            'all': {'ai': True, 'politics': True, 'us': True, 'eu': True, 
                   'russian': True, 'international': True}
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
            max_per_source=2,  # Reduced for speed
            parallel=True,  # Enable parallel fetching
            max_workers=10  # 10 parallel requests
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
    """Categorize news item based on content - 7 main categories."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    
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
        'biden', 'trump', 'putin', 'путин', 'parliament', 'senate', 'закон', 'law'
    ]
    
    # Society (social issues, people, rights)
    society_keywords = [
        'social', 'people', 'society', 'protest', 'rights', 'law', 'court', 'justice',
        'социальн', 'общество', 'люди', 'права', 'закон', 'суд', 'справедлив'
    ]
    
    # Science & Research
    science_keywords = [
        'science', 'research', 'study', 'university', 'scientist', 'discovery',
        'наука', 'исследован', 'ученые', 'университет', 'открыти', 'experiment',
        'climate', 'energy', 'environment', 'климат', 'энергия', 'экология'
    ]
    
    # Check categories (order matters - most specific first)
    if any(kw in text for kw in conflict_keywords):
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
