"""
Integration tests for cache service with news service.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.services.cache_service import get_cache_service, CacheService
from trendoscope2.services.news_service import NewsService


class TestCacheIntegration:
    """Test cache integration with news service."""
    
    @pytest.mark.asyncio
    async def test_news_feed_caching(self):
        """Test that news feed is cached."""
        cache = get_cache_service()
        cache.clear()  # Clear cache before test
        
        # Mock news fetching to avoid actual API calls
        mock_news = [
            {"title": "Test News 1", "link": "http://test.com/1"},
            {"title": "Test News 2", "link": "http://test.com/2"}
        ]
        
        with patch.object(
            NewsService,
            'fetch_news',
            return_value=mock_news
        ):
            # First call - should fetch and cache
            result1 = await NewsService.get_news_feed(
                category='all',
                limit=10,
                use_cache=True
            )
            assert result1['success'] is True
            assert len(result1['news']) == 2
            
            # Check cache
            cache_key = "news:feed:all:all:none:10"
            cached = cache.get(cache_key)
            assert cached is not None
            assert cached['count'] == 2
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = get_cache_service()
        cache.clear()
        
        # Set cache manually
        cache_key = "news:feed:tech:all:none:20"
        cache.set(cache_key, {"success": True, "count": 0, "news": []}, ttl=300)
        
        # Verify cached
        assert cache.get(cache_key) is not None
        
        # Invalidate
        cache.delete(cache_key)
        assert cache.get(cache_key) is None
    
    @pytest.mark.asyncio
    async def test_cache_pattern_deletion(self):
        """Test deleting cache by pattern."""
        cache = get_cache_service()
        cache.clear()
        
        # Set multiple cache keys
        cache.set("news:feed:tech:all:none:10", {"data": 1}, ttl=300)
        cache.set("news:feed:politics:all:none:10", {"data": 2}, ttl=300)
        cache.set("news:feed:tech:ru:none:20", {"data": 3}, ttl=300)
        cache.set("other:key", {"data": 4}, ttl=300)
        
        # Delete all news:feed:* keys
        deleted = cache.delete_pattern("news:feed:*")
        assert deleted >= 3
        
        # Verify deletion
        assert cache.get("news:feed:tech:all:none:10") is None
        assert cache.get("news:feed:politics:all:none:10") is None
        assert cache.get("other:key") is not None
