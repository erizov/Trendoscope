"""
Background task manager for async processing.
"""
import asyncio
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manage background tasks using asyncio."""
    
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.running = False
        self._news_cache = []
        self._last_fetch = None
    
    async def fetch_news_async(self):
        """Fetch news asynchronously and cache it."""
        try:
            from ..ingest.news_sources_async import AsyncNewsAggregator
            
            async with AsyncNewsAggregator(timeout=10) as aggregator:
                logger.info("Background: Fetching news...")
                news_items = await aggregator.fetch_trending_topics(
                    include_russian=True,
                    include_international=True,
                    include_ai=True,
                    include_politics=True,
                    include_us=True,
                    include_eu=True,
                    include_regional=True,
                    include_asia=True,
                    max_per_source=3
                )
                
                self._news_cache = news_items
                self._last_fetch = datetime.now()
                logger.info(f"Background: Fetched {len(news_items)} news items")
                
                # Broadcast to WebSocket connections
                try:
                    from ..api.websocket_manager import manager
                    if news_items:
                        await manager.broadcast_news_batch(news_items[:10])  # Top 10
                except Exception as e:
                    logger.debug(f"WebSocket broadcast failed: {e}")
                
        except Exception as e:
            logger.error(f"Background news fetch error: {e}", exc_info=True)
    
    async def start_news_fetcher(self, interval: int = 300):
        """
        Start background news fetching.
        
        Args:
            interval: Fetch interval in seconds (default: 5 minutes)
        """
        logger.info(f"Starting background news fetcher (interval: {interval}s)")
        
        # Initial fetch
        await self.fetch_news_async()
        
        # Periodic fetching
        while self.running:
            try:
                await asyncio.sleep(interval)
                if self.running:
                    await self.fetch_news_async()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background task error: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def start_all(self, news_interval: int = 300):
        """
        Start all background tasks.
        
        Args:
            news_interval: News fetch interval in seconds
        """
        if self.running:
            logger.warning("Background tasks already running")
            return
        
        self.running = True
        logger.info("Starting all background tasks...")
        
        # Start news fetcher
        self.tasks.append(
            asyncio.create_task(self.start_news_fetcher(news_interval))
        )
        
        logger.info(f"Started {len(self.tasks)} background task(s)")
    
    async def stop_all(self):
        """Stop all background tasks."""
        if not self.running:
            return
        
        logger.info("Stopping background tasks...")
        self.running = False
        
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("Background tasks stopped")
    
    def get_cached_news(self) -> List[dict]:
        """Get cached news items."""
        return self._news_cache.copy()
    
    def get_last_fetch_time(self) -> Optional[datetime]:
        """Get last fetch time."""
        return self._last_fetch


# Global instance
background_manager = BackgroundTaskManager()

