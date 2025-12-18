"""
Cache service with Redis and in-memory fallback.
Provides multi-tier caching for better performance.
"""
import logging
import json
import hashlib
import time
from typing import Optional, Any, Dict
from functools import wraps
from ..config import REDIS_URL, USE_REDIS, REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# In-memory cache as fallback
_memory_cache: Dict[str, Any] = {}
_memory_cache_ttl: Dict[str, float] = {}
_memory_cache_max_size = 1000


class CacheService:
    """
    Multi-tier cache service.
    Uses Redis if available, falls back to in-memory cache.
    """
    
    def __init__(self):
        """Initialize cache service."""
        self._redis_client: Optional[redis.Redis] = None
        self._use_redis = USE_REDIS and REDIS_AVAILABLE
        
        if self._use_redis:
            try:
                if REDIS_URL:
                    self._redis_client = redis.Redis.from_url(
                        REDIS_URL,
                        decode_responses=True
                    )
                else:
                    self._redis_client = redis.Redis(
                        host=REDIS_HOST,
                        port=REDIS_PORT,
                        decode_responses=True
                    )
                # Test connection
                self._redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory cache: {e}")
                self._use_redis = False
                self._redis_client = None
        else:
            logger.info("Using in-memory cache (Redis disabled or unavailable)")
    
    def _make_key(self, namespace: str, *args, **kwargs) -> str:
        """
        Generate cache key from namespace and parameters.
        
        Args:
            namespace: Cache namespace
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create hash from parameters
        key_data = json.dumps(
            {'args': args, 'kwargs': kwargs},
            sort_keys=True,
            ensure_ascii=False
        )
        key_hash = hashlib.sha256(key_data.encode('utf-8')).hexdigest()[:16]
        return f"{namespace}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        # Try Redis first
        if self._use_redis and self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Fallback to in-memory
        if key in _memory_cache:
            expiry = _memory_cache_ttl.get(key, 0)
            if expiry > time.time():
                return _memory_cache[key]
            else:
                # Expired, remove it
                _memory_cache.pop(key, None)
                _memory_cache_ttl.pop(key, None)
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        # Serialize value
        try:
            serialized = json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            # If not JSON serializable, store as string
            serialized = str(value)
        
        # Try Redis first
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.setex(key, ttl, serialized)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Fallback to in-memory
        _memory_cache[key] = value
        _memory_cache_ttl[key] = time.time() + ttl
        
        # Cleanup if cache too large
        if len(_memory_cache) > _memory_cache_max_size:
            self._cleanup_memory_cache()
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        deleted = False
        
        # Delete from Redis
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.delete(key)
                deleted = True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # Delete from memory
        if key in _memory_cache:
            _memory_cache.pop(key, None)
            _memory_cache_ttl.pop(key, None)
            deleted = True
        
        return deleted
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., 'news:*')
            
        Returns:
            Number of keys deleted
        """
        deleted = 0
        
        # Delete from Redis
        if self._use_redis and self._redis_client:
            try:
                keys = self._redis_client.keys(pattern)
                if keys:
                    deleted += self._redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis delete_pattern error: {e}")
        
        # Delete from memory
        import fnmatch
        keys_to_delete = [
            k for k in _memory_cache.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        for key in keys_to_delete:
            _memory_cache.pop(key, None)
            _memory_cache_ttl.pop(key, None)
            deleted += 1
        
        return deleted
    
    def clear(self) -> bool:
        """
        Clear all cache.
        
        Returns:
            True if successful
        """
        # Clear Redis
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        # Clear memory
        _memory_cache.clear()
        _memory_cache_ttl.clear()
        
        return True
    
    def _cleanup_memory_cache(self):
        """Remove expired entries from memory cache."""
        current_time = time.time()
        expired_keys = [
            k for k, expiry in _memory_cache_ttl.items()
            if expiry < current_time
        ]
        
        # Remove expired entries
        for key in expired_keys[:100]:  # Remove up to 100 at a time
            _memory_cache.pop(key, None)
            _memory_cache_ttl.pop(key, None)
        
        # If still too large, remove oldest entries
        if len(_memory_cache) > _memory_cache_max_size:
            sorted_keys = sorted(
                _memory_cache_ttl.items(),
                key=lambda x: x[1]
            )
            keys_to_remove = [
                k for k, _ in sorted_keys[:100]
            ]
            for key in keys_to_remove:
                _memory_cache.pop(key, None)
                _memory_cache_ttl.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'redis_enabled': self._use_redis,
            'memory_cache_size': len(_memory_cache),
            'memory_cache_max_size': _memory_cache_max_size
        }
        
        if self._use_redis and self._redis_client:
            try:
                info = self._redis_client.info()
                stats['redis_connected'] = True
                stats['redis_keys'] = info.get('db0', {}).get('keys', 0)
                stats['redis_memory'] = info.get('used_memory_human', 'N/A')
            except Exception:
                stats['redis_connected'] = False
        
        return stats


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get global cache service instance (singleton).
    
    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(
    namespace: str,
    ttl: int = 3600
):
    """
    Decorator for caching function results.
    
    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_service()
            cache_key = cache._make_key(namespace, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache_service()
            cache_key = cache._make_key(namespace, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
