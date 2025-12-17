"""
News API endpoints.
Handles news feed, translation, and related operations.
"""
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import Dict, Any, Optional
import logging

from ...config import NEWS_DB_DEFAULT_LIMIT
from ...services.news_service import NewsService
from ...core.dependencies import get_news_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/feed")
async def get_news_feed(
    category: str = Query(default="all", description="Category filter"),
    limit: Optional[int] = Query(default=None, ge=5, le=100, description="Maximum items"),
    language: str = Query(default="all", description="Language filter (all, ru, en)"),
    translate_to: str = Query(default="none", description="Translate to (none, ru, en)"),
    use_cache: bool = Query(default=True, description="Use cached news if available"),
    news_service: NewsService = Depends(get_news_service)
):
    """Get news feed (async with caching)."""
    try:
        if limit is None:
            limit = NEWS_DB_DEFAULT_LIMIT
        logger.info(
            f"Fetching news: category={category}, limit={limit}, "
            f"use_cache={use_cache}"
        )

        result = await news_service.get_news_feed(
            category=category,
            limit=limit,
            language=language,
            translate_to=translate_to,
            use_cache=use_cache
        )

        return result
    except Exception as e:
        logger.error(f"Error fetching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_article(
    article: Dict[str, Any] = Body(...),
    target_language: str = Query(..., description="Target language (ru, en)"),
    news_service: NewsService = Depends(get_news_service)
):
    """Translate a single article."""
    try:
        result = await news_service.translate_article(article, target_language)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
