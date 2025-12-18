# Architecture Improvements

## Overview

This document outlines specific architecture improvements to enhance code quality, maintainability, and scalability.

## Current Architecture Strengths

- ✅ Clear separation: API → Services → Storage
- ✅ Dependency injection container
- ✅ Structured exceptions
- ✅ Error handlers
- ✅ Repository pattern foundation

## Recommended Improvements

### 1. Service Layer Architecture

#### Current Issues
- Services use static methods (hard to test)
- Mixed responsibilities in single classes
- Direct dependencies (hard to mock)
- No clear interfaces

#### Proposed Architecture

```
services/
├── interfaces.py          # Service protocols/interfaces
├── base.py                # Base service classes
├── news/
│   ├── __init__.py
│   ├── news_service.py    # Main orchestrator
│   ├── news_processor.py  # Processing logic
│   ├── news_filter.py     # Filtering logic
│   └── news_fetcher.py    # Fetching logic
├── email/
│   ├── __init__.py
│   ├── email_service.py
│   └── rate_limiter.py    # Shared rate limiting
└── shared/
    ├── rate_limiter.py
    └── cache_manager.py
```

**Benefits:**
- Clear separation of concerns
- Easier to test individual components
- Reusable components
- Better dependency management

### 2. Repository Pattern Implementation

#### Current State
- `core/repositories.py` exists but unused (0% coverage)
- Direct database access in services
- Hard to swap storage backends

#### Proposed Implementation

```python
# app/src/app/core/interfaces.py
from typing import Protocol, List, Dict, Any, Optional

class INewsRepository(Protocol):
    """Repository interface for news storage."""
    
    async def save(self, item: Dict[str, Any]) -> int:
        """Save news item."""
        ...
    
    async def find_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Find by ID."""
        ...
    
    async def find_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find all with filters."""
        ...
    
    async def delete(self, item_id: int) -> bool:
        """Delete by ID."""
        ...

# app/src/app/storage/repositories.py
class NewsRepository(INewsRepository):
    """SQLite implementation."""
    
    def __init__(self, db: NewsDatabase):
        self.db = db
    
    async def save(self, item: Dict[str, Any]) -> int:
        # Implementation
        pass

# Usage in service
class NewsService:
    def __init__(self, repository: INewsRepository):
        self.repository = repository
    
    async def save_news(self, item: Dict[str, Any]) -> int:
        return await self.repository.save(item)
```

**Benefits:**
- Decouple business logic from storage
- Easy to swap SQLite → PostgreSQL
- Testable with mock repositories
- Follows SOLID principles

### 3. Dependency Injection Enhancement

#### Current State
- Container exists but not fully utilized
- Services create dependencies internally
- Hard to test with different configurations

#### Proposed Enhancement

```python
# app/src/app/core/container.py (enhanced)
class Container:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, factory: Callable):
        """Register service factory."""
        self._services[name] = factory
    
    def get(self, name: str) -> Any:
        """Get service instance (singleton)."""
        if name not in self._services:
            raise ValueError(f"Service {name} not registered")
        if name not in self._instances:
            self._instances[name] = self._services[name](self)
        return self._instances[name]

# Usage
container = Container()
container.register("cache", lambda c: CacheService())
container.register("news_repo", lambda c: NewsRepository(NewsDatabase()))
container.register("news_service", lambda c: NewsService(
    cache=c.get("cache"),
    repository=c.get("news_repo")
))
```

### 4. Event-Driven Architecture (Optional)

#### Use Case
- News fetched → trigger categorization
- News categorized → trigger translation
- News translated → trigger TTS generation
- News processed → trigger email digest

#### Implementation

```python
# app/src/app/core/events.py
from typing import Callable, Dict, List
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    NEWS_FETCHED = "news.fetched"
    NEWS_CATEGORIZED = "news.categorized"
    NEWS_TRANSLATED = "news.translated"
    TTS_GENERATED = "tts.generated"

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime

class EventBus:
    """Simple event bus for decoupled communication."""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to event type."""
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: Event):
        """Publish event to all subscribers."""
        for handler in self._handlers.get(event.type, []):
            await handler(event)

# Usage
event_bus = EventBus()

# Subscribe
event_bus.subscribe(EventType.NEWS_FETCHED, categorize_news_handler)
event_bus.subscribe(EventType.NEWS_CATEGORIZED, translate_news_handler)

# Publish
await event_bus.publish(Event(
    type=EventType.NEWS_FETCHED,
    data={"items": news_items}
))
```

**Benefits:**
- Decoupled components
- Easy to add new handlers
- Better scalability
- Clear event flow

### 5. Configuration Management

#### Current State
- Configuration in multiple places
- No validation
- Hard to test with different configs

#### Proposed Solution

```python
# app/src/app/core/settings.py (enhanced)
from pydantic import BaseSettings, validator
from typing import Optional

class Settings(BaseSettings):
    # ... existing settings ...
    
    @validator('REDIS_URL')
    def validate_redis_url(cls, v, values):
        if values.get('USE_REDIS') and not v:
            raise ValueError("REDIS_URL required when USE_REDIS=True")
        return v
    
    @validator('EMAIL_SMTP_USER')
    def validate_email_config(cls, v, values):
        if values.get('EMAIL_ENABLED') and not v:
            raise ValueError("Email credentials required when EMAIL_ENABLED=True")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True

# Environment-specific configs
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
```

### 6. Caching Strategy Enhancement

#### Current State
- Basic Redis + in-memory cache
- No cache invalidation strategy
- No cache warming

#### Proposed Enhancement

```python
# app/src/app/services/cache_strategy.py
from typing import Optional, Callable
from enum import Enum

class CacheStrategy(Enum):
    CACHE_FIRST = "cache_first"  # Try cache, fallback to source
    SOURCE_FIRST = "source_first"  # Try source, cache result
    CACHE_ONLY = "cache_only"  # Only use cache
    NO_CACHE = "no_cache"  # Skip cache

class CacheManager:
    """Enhanced cache manager with strategies."""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    async def get_or_fetch(
        self,
        key: str,
        fetch_fn: Callable,
        strategy: CacheStrategy = CacheStrategy.CACHE_FIRST,
        ttl: int = 300
    ) -> Any:
        """Get from cache or fetch using strategy."""
        if strategy == CacheStrategy.NO_CACHE:
            return await fetch_fn()
        
        if strategy == CacheStrategy.CACHE_ONLY:
            return self.cache.get(key)
        
        cached = self.cache.get(key)
        
        if strategy == CacheStrategy.CACHE_FIRST:
            if cached:
                return cached
            result = await fetch_fn()
            self.cache.set(key, result, ttl=ttl)
            return result
        
        if strategy == CacheStrategy.SOURCE_FIRST:
            result = await fetch_fn()
            self.cache.set(key, result, ttl=ttl)
            return result
```

### 7. API Versioning

#### Current State
- No API versioning
- Breaking changes affect all clients

#### Proposed Solution

```python
# app/src/app/api/v1/__init__.py
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")

# app/src/app/api/v2/__init__.py
v2_router = APIRouter(prefix="/api/v2")

# app/src/app/api/main.py
from .v1 import v1_router
from .v2 import v2_router

app.include_router(v1_router)
app.include_router(v2_router)

# Maintain backward compatibility
app.include_router(v1_router, prefix="/api")  # Legacy
```

### 8. Monitoring & Observability

#### Proposed Additions

```python
# app/src/app/core/middleware.py
from fastapi import Request
import time

async def logging_middleware(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        "Request processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration * 1000
    )
    
    return response

# Add to app
app.middleware("http")(logging_middleware)
```

## Implementation Priority

### High Priority (Immediate)
1. ✅ Fix circular imports (DONE)
2. ✅ Create missing modules (DONE)
3. Convert static methods to instance methods
4. Extract processing logic from services
5. Standardize error handling

### Medium Priority (Next 2-4 weeks)
1. Implement repository pattern
2. Extract business logic from routers
3. Add service interfaces
4. Enhance dependency injection
5. Improve test coverage to 60%+

### Low Priority (Future)
1. Event-driven architecture
2. API versioning
3. Advanced caching strategies
4. Enhanced monitoring

## Migration Strategy

1. **Incremental**: One service at a time
2. **Backward Compatible**: Keep old methods during transition
3. **Tested**: Write tests before refactoring
4. **Documented**: Update docs as you go
5. **Measured**: Track metrics before/after

## Success Metrics

- Test coverage: 23% → 80%+
- Code complexity: Reduce by 30%+
- Static methods in services: 0
- Custom exception usage: 100%
- Repository pattern: Fully implemented
- Service interfaces: All services have protocols
