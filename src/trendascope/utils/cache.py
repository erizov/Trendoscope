import os, json, hashlib
from typing import Optional

try:
    import redis  # type: ignore
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

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
    c = _client()
    if not c:
        return None
    try:
        return c.get(_key(namespace, payload))
    except Exception:
        return None

def setex(namespace: str, payload: str, value: str, ttl_seconds: int = 86400) -> None:
    c = _client()
    if not c:
        return
    try:
        c.setex(_key(namespace, payload), ttl_seconds, value)
    except Exception:
        return
