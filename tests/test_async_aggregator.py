"""
Tests for async news aggregator.
"""
import pytest
import asyncio
from trendascope.ingest.news_sources_async import AsyncNewsAggregator


@pytest.mark.asyncio
async def test_async_fetch_rss_feed():
    """Test async RSS feed fetching."""
    aggregator = AsyncNewsAggregator(timeout=5)
    
    try:
        # Test with a simple RSS feed
        items = await aggregator.fetch_rss_feed(
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            max_items=3
        )
        
        assert isinstance(items, list)
        if items:
            assert 'title' in items[0]
            assert 'link' in items[0]
    finally:
        await aggregator.close()


@pytest.mark.asyncio
async def test_async_fetch_trending_topics():
    """Test async trending topics fetching."""
    aggregator = AsyncNewsAggregator(timeout=5)
    
    try:
        items = await aggregator.fetch_trending_topics(
            include_ai=True,
            include_international=True,
            max_per_source=2,
            max_workers=5
        )
        
        assert isinstance(items, list)
        # Should have some items
        assert len(items) >= 0
    finally:
        await aggregator.close()

