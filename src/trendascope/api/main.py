"""
FastAPI application for Trendoscope.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
import os

from ..gen.generate import generate_summary
from ..pipeline.orchestrator import run_pipeline

app = FastAPI(
    title="Trendoscope API",
    description="Analyze LiveJournal posts and generate viral content",
    version="1.0.0"
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


@app.post("/api/post/generate")
async def generate_post_endpoint(
    analyzed_posts: Optional[List[Dict]] = None,
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
    )
):
    """
    Generate a new post in author's style based on trending news.

    Args:
        analyzed_posts: Previously analyzed blog posts (optional, loads from storage)
        style: Post style (philosophical, ironic, analytical, provocative)
        topic: Topic focus (any, ai, politics, us_affairs, russian_history, science)
        provider: LLM provider
        model: Model name

    Returns:
        Generated post with title, text, and tags
    """
    try:
        from ..gen.post_generator import generate_post_from_storage

        # If no posts provided, use stored posts from vector DB
        if not analyzed_posts:
            result = generate_post_from_storage(
                style=style,
                topic=topic,
                provider=provider,
                model=model
            )
        else:
            from ..gen.post_generator import generate_post
            result = generate_post(
                analyzed_posts=analyzed_posts,
                style=style,
                topic=topic,
                provider=provider,
                model=model
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Post generation failed: {str(e)}"
        )
