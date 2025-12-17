"""
FastAPI application for Trendoscope2.
Main application setup with router registration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ..config import DATA_DIR
from ..services.background_tasks import background_manager
from ..storage.news_db import NewsDatabase
from ..core.exceptions import TrendoscopeException
from ..core.error_handler import (
    trendoscope_exception_handler,
    general_exception_handler
)

# Import routers
from .routers import news, tts, email, telegram, rutube, admin

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

# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
frontend_dist = frontend_path / "dist"
frontend_src = Path(__file__).parent.parent.parent / "src" / "frontend"

# Try dist first (built React app), then src (legacy HTML)
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")
elif frontend_src.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_src)), name="static")

# Register routers
app.include_router(news.router)
app.include_router(tts.router)
app.include_router(email.router)
app.include_router(telegram.router)
app.include_router(rutube.router)
app.include_router(admin.router)

# Register exception handlers
app.add_exception_handler(
    TrendoscopeException,
    trendoscope_exception_handler
)
app.add_exception_handler(
    Exception,
    general_exception_handler
)


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



