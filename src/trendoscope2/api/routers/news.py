"""
News API endpoints.
Handles news feed, translation, and related operations.
"""
from fastapi import APIRouter, HTTPException, Query, Body, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
import logging
import asyncio

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


@router.get("/search")
async def search_news(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    language: Optional[str] = Query(default=None, description="Language filter"),
    source: Optional[str] = Query(default=None, description="Source filter"),
    date_from: Optional[str] = Query(default=None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(default=None, description="End date (ISO format)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Result offset")
):
    """Search news with full-text search."""
    try:
        from ...storage.news_search import NewsSearch
        
        search = NewsSearch()
        result = search.search(
            query=q,
            category=category,
            language=language,
            source=source,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/filters")
async def get_news_filters():
    """Get available filter values."""
    try:
        from ...storage.news_search import NewsSearch
        
        search = NewsSearch()
        filters = search.get_filters()
        
        return {
            "success": True,
            **filters
        }
    except Exception as e:
        logger.error(f"Filters error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get filters: {str(e)}")


@router.get("/trending")
async def get_trending_topics(
    days: int = Query(default=7, ge=1, le=30, description="Days to look back"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum topics")
):
    """Get trending topics."""
    try:
        from ...storage.news_search import NewsSearch
        
        search = NewsSearch()
        topics = search.get_trending_topics(days=days, limit=limit)
        
        return {
            "success": True,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"Trending topics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time news updates.
    
    Clients can subscribe to:
    - news_updates: Real-time news feed updates
    - news_batch: Batch news updates
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "connected",
                "message": "Connected to news feed",
                "connections": manager.get_connection_count()
            },
            websocket
        )
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for client message (with timeout)
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                # Handle client messages
                if data.get("type") == "ping":
                    await manager.send_personal_message(
                        {"type": "pong"},
                        websocket
                    )
                elif data.get("type") == "subscribe":
                    # Client can subscribe to specific channels
                    channel = data.get("channel", "news_updates")
                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "channel": channel
                        },
                        websocket
                    )
                
            except asyncio.TimeoutError:
                # Send keepalive
                await manager.send_personal_message(
                    {"type": "keepalive"},
                    websocket
                )
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        manager.disconnect(websocket)


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
