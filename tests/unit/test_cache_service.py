"""
Unit tests for cache service.
Tests Redis and in-memory caching functionality.
"""
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.services.cache_service import (
    CacheService, get_cache_service, cached
)


class TestCacheService:
    """Test CacheService functionality."""
    
    def test_init_without_redis(self):
        """Test initialization without Redis."""
        with patch('trendoscope2.services.cache_service.USE_REDIS', False):
            with patch('trendoscope2.services.cache_service.REDIS_AVAILABLE', False):
                service = CacheService()
                assert service._use_redis is False
                assert service._redis_client is None
    
    def test_init_with_redis_available(self):
        """Test initialization with Redis available."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        
        with patch('trendoscope2.services.cache_service.USE_REDIS', True):
            with patch('trendoscope2.services.cache_service.REDIS_AVAILABLE', True):
                with patch('trendoscope2.services.cache_service.redis') as mock_redis_module:
                    mock_redis_module.Redis.from_url.return_value = mock_redis
                    service = CacheService()
                    assert service._use_redis is True
    
    def test_set_and_get_in_memory(self):
        """Test set and get with in-memory cache."""
        service = CacheService()
        service._use_redis = False
        
        key = "test:key"
        value = {"test": "data"}
        
        result = service.set(key, value, ttl=60)
        assert result is True
        
        cached_value = service.get(key)
        assert cached_value == value
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        service = CacheService()
        service._use_redis = False
        
        result = service.get("nonexistent:key")
        assert result is None
    
    def test_delete_key(self):
        """Test deleting a key."""
        service = CacheService()
        service._use_redis = False
        
        key = "test:delete"
        value = "test_value"
        
        service.set(key, value, ttl=60)
        assert service.get(key) == value
        
        result = service.delete(key)
        assert result is True
        assert service.get(key) is None
    
    def test_delete_pattern(self):
        """Test deleting keys by pattern."""
        service = CacheService()
        service._use_redis = False
        
        # Set multiple keys
        service.set("news:feed:tech", {"data": 1}, ttl=60)
        service.set("news:feed:politics", {"data": 2}, ttl=60)
        service.set("other:key", {"data": 3}, ttl=60)
        
        # Delete all news:feed:* keys
        deleted = service.delete_pattern("news:feed:*")
        assert deleted == 2
        
        assert service.get("news:feed:tech") is None
        assert service.get("news:feed:politics") is None
        assert service.get("other:key") is not None
    
    def test_clear_cache(self):
        """Test clearing all cache."""
        service = CacheService()
        service._use_redis = False
        
        service.set("key1", "value1", ttl=60)
        service.set("key2", "value2", ttl=60)
        
        result = service.clear()
        assert result is True
        assert service.get("key1") is None
        assert service.get("key2") is None
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        service = CacheService()
        service._use_redis = False
        
        key = "test:expire"
        value = "test_value"
        
        service.set(key, value, ttl=1)  # 1 second TTL
        assert service.get(key) == value
        
        time.sleep(1.1)  # Wait for expiration
        assert service.get(key) is None
    
    def test_get_stats(self):
        """Test getting cache statistics."""
        service = CacheService()
        service._use_redis = False
        
        service.set("test:key", "value", ttl=60)
        
        stats = service.get_stats()
        assert 'redis_enabled' in stats
        assert 'memory_cache_size' in stats
        assert stats['memory_cache_size'] > 0
    
    def test_make_key(self):
        """Test cache key generation."""
        service = CacheService()
        
        key1 = service._make_key("namespace", "arg1", kwarg1="value1")
        key2 = service._make_key("namespace", "arg1", kwarg1="value1")
        key3 = service._make_key("namespace", "arg2", kwarg1="value1")
        
        # Same parameters should generate same key
        assert key1 == key2
        # Different parameters should generate different key
        assert key1 != key3
        # Key should start with namespace
        assert key1.startswith("namespace:")


class TestCacheDecorator:
    """Test @cached decorator."""
    
    def test_cached_sync_function(self):
        """Test caching sync function results."""
        call_count = 0
        
        @cached("test:namespace", ttl=60)
        def sync_function(x: int, y: int = 10):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call - should execute function
        result1 = sync_function(5, y=10)
        assert result1 == 15
        assert call_count == 1
        
        # Second call with same args - should use cache
        result2 = sync_function(5, y=10)
        assert result2 == 15
        assert call_count == 1  # Function not called again
        
        # Different args - should execute function
        result3 = sync_function(5, y=20)
        assert result3 == 25
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cached_async_function(self):
        """Test caching async function results."""
        call_count = 0
        
        @cached("test:async", ttl=60)
        async def async_function(x: int):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = await async_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = await async_function(5)
        assert result2 == 10
        assert call_count == 1


class TestGetCacheService:
    """Test get_cache_service singleton."""
    
    def test_singleton_pattern(self):
        """Test that get_cache_service returns same instance."""
        service1 = get_cache_service()
        service2 = get_cache_service()
        
        assert service1 is service2


class TestCacheServiceWithRedis:
    """Test CacheService with Redis (mocked)."""
    
    def test_set_and_get_with_redis(self):
        """Test set and get with Redis."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = '{"test": "data"}'
        mock_redis.setex.return_value = True
        
        service = CacheService()
        service._use_redis = True
        service._redis_client = mock_redis
        
        # Test set
        result = service.set("test:key", {"test": "data"}, ttl=60)
        assert result is True
        mock_redis.setex.assert_called_once()
        
        # Test get
        value = service.get("test:key")
        assert value == {"test": "data"}
        mock_redis.get.assert_called_once()
    
    def test_redis_fallback_to_memory(self):
        """Test fallback to memory when Redis fails."""
        mock_redis = MagicMock()
        mock_redis.get.side_effect = Exception("Redis error")
        mock_redis.setex.side_effect = Exception("Redis error")
        
        service = CacheService()
        service._use_redis = True
        service._redis_client = mock_redis
        
        # Should fallback to memory
        result = service.set("test:key", "value", ttl=60)
        assert result is True
        
        value = service.get("test:key")
        assert value == "value"
