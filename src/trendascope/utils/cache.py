import os, json, hashlib
from typing import Optional
from functools import lru_cache

try:
    import redis  # type: ignore
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# In-memory cache as fallback (when Redis not available)
_memory_cache: dict = {}
_memory_cache_ttl: dict = {}

def _client():
    if not redis:
        return None
    try:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None

def _key(namespace: str, payload: str) -> str:
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"trendascope:{namespace}:{h}"

def get(namespace: str, payload: str) -> Optional[str]:
    """Get cached value with in-memory fallback."""
    c = _client()
    
    # Try Redis first
    if c:
        try:
            value = c.get(_key(namespace, payload))
            if value:
                return value
        except Exception:
            pass
    
    # Fallback to in-memory cache
    cache_key = _key(namespace, payload)
    if cache_key in _memory_cache:
        import time
        if time.time() < _memory_cache_ttl.get(cache_key, 0):
            return _memory_cache[cache_key]
        else:
            # Expired, remove it
            _memory_cache.pop(cache_key, None)
            _memory_cache_ttl.pop(cache_key, None)
    
    return None

def setex(namespace: str, payload: str, value: str, ttl_seconds: int = 86400) -> None:
    """Set cached value with in-memory fallback."""
    c = _client()
    cache_key = _key(namespace, payload)
    
    # Try Redis first
    if c:
        try:
            c.setex(cache_key, ttl_seconds, value)
            return
        except Exception:
            pass
    
    # Fallback to in-memory cache
    import time
    _memory_cache[cache_key] = value
    _memory_cache_ttl[cache_key] = time.time() + ttl_seconds
    
    # Clean up old entries if cache too large
    if len(_memory_cache) > 1000:
        current_time = time.time()
        expired_keys = [
            k for k, expiry in _memory_cache_ttl.items()
            if expiry < current_time
        ]
        for k in expired_keys[:100]:  # Remove up to 100 expired entries
            _memory_cache.pop(k, None)
            _memory_cache_ttl.pop(k, None)
