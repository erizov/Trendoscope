# Next Refactoring Steps & Architecture Improvements

## Executive Summary

Based on codebase analysis, here are prioritized, actionable refactoring steps to improve code quality, testability, and maintainability.

**Current State:**
- ✅ Priority 1 completed (circular imports, missing modules)
- ⚠️ Test coverage: 23% (target: 80%+)
- ⚠️ Services use static methods (hard to test/mock)
- ⚠️ Error handling inconsistent
- ⚠️ Business logic mixed in API routers

## Priority 2: Service Layer Refactoring (High Impact)

### 2.1 Convert Static Methods to Instance Methods

**Problem**: `NewsService` uses only static methods, making it hard to:
- Mock dependencies in tests
- Inject different configurations
- Track state
- Use dependency injection properly

**Current Code:**
```python
class NewsService:
    @staticmethod
    async def fetch_news(...):
        # Lazy import inside method
        from ..services.cache_service import get_cache_service
        cache = get_cache_service()
        # ...
```

**Refactored Code:**
```python
class NewsService:
    def __init__(
        self,
        cache_service: Optional[CacheService] = None,
        aggregator: Optional[AsyncNewsAggregator] = None
    ):
        self.cache_service = cache_service or get_cache_service()
        self.aggregator = aggregator
    
    async def fetch_news(self, use_cache: bool = True, ...):
        # Use self.cache_service instead of lazy import
        cached_news = self.cache_service.get(cache_key)
        # ...
```

**Benefits:**
- ✅ Easier to test (can inject mocks)
- ✅ Better dependency injection
- ✅ Clearer dependencies
- ✅ Can track state if needed

**Files to Refactor:**
1. `app/src/app/services/news_service.py` - Convert all static methods
2. `app/src/app/core/dependencies.py` - Update dependency functions
3. `app/src/app/core/container.py` - Update container to create instances
4. `app/src/app/api/routers/news.py` - Already uses DI, no changes needed

**Implementation Steps:**
1. Add `__init__` method accepting dependencies
2. Convert `@staticmethod` to instance methods
3. Replace lazy imports with `self.dependency`
4. Update container to create service instances
5. Add unit tests with mocked dependencies

### 2.2 Extract Processing Logic from NewsService

**Problem**: `NewsService` has multiple responsibilities:
- Fetching news
- Processing (encoding, HTML cleaning)
- Categorization
- Filtering
- Translation
- Caching

**Solution**: Extract into focused classes:

```python
# app/src/app/services/news_processor.py
class NewsProcessor:
    """Processes news items: encoding, HTML cleaning, language detection."""
    
    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process single news item."""
        # Encoding fixes
        # HTML cleaning
        # Language detection
        pass

# app/src/app/services/news_filter.py
class NewsFilter:
    """Filters news items by category, language, etc."""
    
    def filter(self, items: List[Dict], category: str, language: str) -> List[Dict]:
        """Filter news items."""
        pass

# app/src/app/services/news_service.py (refactored)
class NewsService:
    def __init__(
        self,
        cache_service: CacheService,
        aggregator: AsyncNewsAggregator,
        processor: NewsProcessor,
        filter_service: NewsFilter,
        translator: Optional[Translator] = None
    ):
        self.cache_service = cache_service
        self.aggregator = aggregator
        self.processor = processor
        self.filter_service = filter_service
        self.translator = translator
    
    async def get_news_feed(self, ...):
        # Fetch
        news_items = await self.aggregator.fetch_trending_topics(...)
        
        # Process
        for item in news_items:
            self.processor.process_item(item)
        
        # Filter
        news_items = self.filter_service.filter(news_items, category, language)
        
        # Translate
        if translate_to != 'none':
            news_items = await self.translator.translate(news_items, translate_to)
        
        return result
```

**Benefits:**
- ✅ Single Responsibility Principle
- ✅ Easier to test each component
- ✅ Can reuse processors/filters elsewhere
- ✅ Better code organization

### 2.3 Extract Rate Limiting from EmailService

**Problem**: `EmailService` handles:
- Email validation
- SMTP sending
- Rate limiting
- Caching
- HTML/plain text formatting

**Solution**: Extract rate limiting to separate service:

```python
# app/src/app/services/rate_limiter.py
class RateLimiter:
    """Generic rate limiting service."""
    
    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self._tracker: Dict[str, List[datetime]] = defaultdict(list)
    
    def check_rate_limit(self, key: str) -> bool:
        """Check if rate limit allows operation."""
        now = datetime.now()
        # Clean old entries
        self._tracker[key] = [
            ts for ts in self._tracker[key]
            if (now - ts).total_seconds() < 60
        ]
        
        if len(self._tracker[key]) >= self.max_per_minute:
            return False
        
        self._tracker[key].append(now)
        return True

# EmailService uses RateLimiter
class EmailService:
    def __init__(self, ..., rate_limiter: Optional[RateLimiter] = None):
        self.rate_limiter = rate_limiter or RateLimiter(rate_limit_per_minute)
    
    async def send_email(self, to: str, ...):
        if not self.rate_limiter.check_rate_limit(to):
            raise EmailError("Rate limit exceeded")
        # Send email...
```

**Benefits:**
- ✅ Reusable rate limiting for other services
- ✅ Easier to test
- ✅ Clear separation of concerns

## Priority 3: Error Handling Standardization (Medium Impact)

### 3.1 Use Custom Exceptions Consistently

**Problem**: Services catch generic `Exception` and log, but don't raise structured exceptions.

**Current Code:**
```python
except Exception as e:
    logger.warning(f"Translation failed: {e}")
    return news_items  # Silent failure
```

**Refactored Code:**
```python
from ..core.exceptions import TranslationError, NewsProcessingError

try:
    translated = await self.translator.translate(items, target_language)
except TranslationError as e:
    logger.warning(f"Translation failed: {e}")
    raise  # Re-raise to let error handler deal with it
except Exception as e:
    logger.error(f"Unexpected translation error: {e}", exc_info=True)
    raise TranslationError(f"Translation failed: {str(e)}")
```

**Files to Update:**
1. `app/src/app/services/news_service.py` - Use `NewsFetchError`, `TranslationError`
2. `app/src/app/services/email_service.py` - Use `EmailError`
3. `app/src/app/services/telegram_service.py` - Use `TelegramError`
4. `app/src/app/tts/tts_service.py` - Use `TTSError`
5. `app/src/app/api/routers/*.py` - Let exceptions bubble up, remove try/except

**Benefits:**
- ✅ Consistent error responses
- ✅ Better error tracking
- ✅ Error handler automatically formats responses
- ✅ Easier debugging

### 3.2 Add Error Recovery Mechanisms

**Problem**: Services fail silently or return empty results.

**Solution**: Add retry logic and fallbacks:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class NewsService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(NewsFetchError)
    )
    async def fetch_news(self, ...):
        try:
            return await self.aggregator.fetch_trending_topics(...)
        except TimeoutError:
            # Fallback to cache even if stale
            cached = self.cache_service.get(cache_key)
            if cached:
                logger.warning("Using stale cache due to timeout")
                return cached
            raise NewsFetchError("Failed to fetch news and no cache available")
```

## Priority 4: API Router Improvements (Medium Impact)

### 4.1 Extract Business Logic from Routers

**Problem**: Routers contain business logic mixed with HTTP handling.

**Current Code:**
```python
@router.get("/search")
async def search_news(...):
    try:
        from ...storage.news_search import NewsSearch
        search = NewsSearch()
        result = search.search(...)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
```

**Refactored Code:**
```python
# In news_service.py
class NewsService:
    def search_news(
        self,
        query: str,
        category: Optional[str] = None,
        ...
    ) -> Dict[str, Any]:
        """Search news with full-text search."""
        search = NewsSearch()
        result = search.search(
            query=query,
            category=category,
            ...
        )
        return {"success": True, **result}

# In router
@router.get("/search")
async def search_news(
    q: str = Query(...),
    ...,
    news_service: NewsService = Depends(get_news_service)
):
    """Search news with full-text search."""
    return await news_service.search_news(query=q, ...)
```

**Benefits:**
- ✅ Business logic testable without HTTP layer
- ✅ Routers become thin HTTP adapters
- ✅ Can reuse search logic elsewhere

### 4.2 Add Request/Response Models

**Problem**: Routers use raw dictionaries and Query parameters.

**Solution**: Use Pydantic models:

```python
# app/src/app/api/schemas.py
class NewsSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    language: Optional[str] = None
    source: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class NewsSearchResponse(BaseModel):
    success: bool
    total: int
    results: List[NewsItem]

# In router
@router.get("/search", response_model=NewsSearchResponse)
async def search_news(
    request: NewsSearchRequest = Depends(),
    news_service: NewsService = Depends(get_news_service)
):
    return await news_service.search_news(**request.dict())
```

## Priority 5: Architecture Improvements (Long-term)

### 5.1 Implement Service Interfaces (Protocols)

**Problem**: No clear contracts for services, hard to swap implementations.

**Solution**: Use Python Protocols:

```python
# app/src/app/core/interfaces.py
from typing import Protocol, List, Dict, Any, Optional

class INewsService(Protocol):
    """Interface for news service."""
    
    async def fetch_news(
        self,
        use_cache: bool = True,
        force_fresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch news items."""
        ...
    
    async def get_news_feed(
        self,
        category: str = 'all',
        limit: Optional[int] = None,
        ...
    ) -> Dict[str, Any]:
        """Get processed news feed."""
        ...

# NewsService implements the protocol
class NewsService:
    # Implementation matches INewsService protocol
    ...
```

**Benefits:**
- ✅ Clear contracts
- ✅ Can create test doubles easily
- ✅ Better IDE support
- ✅ Documentation of expected behavior

### 5.2 Implement Repository Pattern Properly

**Problem**: `core/repositories.py` exists but is not used (0% coverage).

**Solution**: Create repository interfaces and implementations:

```python
# app/src/app/core/repositories.py
from typing import Protocol, List, Dict, Any, Optional

class INewsRepository(Protocol):
    """Repository interface for news storage."""
    
    async def save(self, item: Dict[str, Any]) -> int:
        """Save news item, return ID."""
        ...
    
    async def find_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Find news item by ID."""
        ...
    
    async def find_all(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find all news items with filters."""
        ...

# app/src/app/storage/news_repository.py
class NewsRepository(INewsRepository):
    """SQLite implementation of news repository."""
    
    def __init__(self, db: NewsDatabase):
        self.db = db
    
    async def save(self, item: Dict[str, Any]) -> int:
        # Implementation using NewsDatabase
        pass
```

**Benefits:**
- ✅ Decouple business logic from storage
- ✅ Can swap SQLite for PostgreSQL easily
- ✅ Easier to test (mock repository)
- ✅ Follows SOLID principles

### 5.3 Add Unit of Work Pattern

**Problem**: Multiple database operations not atomic.

**Solution**: Implement Unit of Work:

```python
# app/src/app/core/unit_of_work.py
class UnitOfWork:
    """Manages database transactions."""
    
    def __init__(self):
        self.news_repo: Optional[INewsRepository] = None
        self._committed = False
    
    async def __aenter__(self):
        self.news_repo = NewsRepository(NewsDatabase())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self._committed:
            await self.commit()
        elif exc_type is not None:
            await self.rollback()
    
    async def commit(self):
        """Commit all changes."""
        # Commit database transaction
        self._committed = True
    
    async def rollback(self):
        """Rollback all changes."""
        # Rollback database transaction
```

## Priority 6: Test Coverage Improvements

### 6.1 Add Service Tests with Mocks

**Target**: Increase coverage from 23% to 40%+

**Priority Services to Test:**
1. `news_service.py` (18% → 60%+)
2. `email_service.py` (20% → 60%+)
3. `telegram_service.py` (17% → 60%+)
4. `cache_service.py` (16% → 80%+) - Already has good tests

**Example Test Structure:**
```python
# tests/unit/test_news_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.news_service import NewsService
from app.core.exceptions import NewsFetchError

class TestNewsService:
    @pytest.fixture
    def mock_cache(self):
        return Mock()
    
    @pytest.fixture
    def mock_aggregator(self):
        return AsyncMock()
    
    @pytest.fixture
    def news_service(self, mock_cache, mock_aggregator):
        return NewsService(
            cache_service=mock_cache,
            aggregator=mock_aggregator
        )
    
    @pytest.mark.asyncio
    async def test_fetch_news_uses_cache(self, news_service, mock_cache):
        """Test that cached news is returned when available."""
        cached_news = [{"title": "Test", "link": "http://test.com"}]
        mock_cache.get.return_value = cached_news
        
        result = await news_service.fetch_news(use_cache=True)
        
        assert result == cached_news
        mock_cache.get.assert_called_once_with("news:feed:all")
        mock_aggregator.fetch_trending_topics.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_fetch_news_fetches_fresh_when_no_cache(
        self, news_service, mock_cache, mock_aggregator
    ):
        """Test that fresh news is fetched when cache is empty."""
        mock_cache.get.return_value = None
        fresh_news = [{"title": "Fresh", "link": "http://fresh.com"}]
        mock_aggregator.fetch_trending_topics.return_value = fresh_news
        
        result = await news_service.fetch_news(use_cache=True)
        
        assert result == fresh_news
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_news_raises_exception_on_error(
        self, news_service, mock_aggregator
    ):
        """Test that NewsFetchError is raised on fetch failure."""
        mock_aggregator.fetch_trending_topics.side_effect = TimeoutError("Timeout")
        
        with pytest.raises(NewsFetchError):
            await news_service.fetch_news(use_cache=False)
```

### 6.2 Add Integration Tests for API Endpoints

**Target**: Test all API endpoints with various scenarios.

**Example:**
```python
# tests/integration/test_news_api.py
class TestNewsAPI:
    def test_search_news_success(self, client):
        """Test successful news search."""
        response = client.get(
            "/api/news/search",
            params={"q": "test", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert "total" in data
    
    def test_search_news_empty_query(self, client):
        """Test search with empty query returns 422."""
        response = client.get("/api/news/search", params={"q": ""})
        assert response.status_code == 422
    
    def test_search_news_with_filters(self, client):
        """Test search with category and language filters."""
        response = client.get(
            "/api/news/search",
            params={
                "q": "tech",
                "category": "tech",
                "language": "en"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Verify filters applied
        for item in data["results"]:
            assert item["category"] == "tech"
            assert item["language"] == "en"
```

## Implementation Roadmap

### Week 1: Service Layer Refactoring
- [ ] Day 1-2: Convert `NewsService` static methods to instance methods
- [ ] Day 3: Extract `NewsProcessor` class
- [ ] Day 4: Extract `NewsFilter` class
- [ ] Day 5: Update tests and verify

### Week 2: Error Handling & API Improvements
- [ ] Day 1-2: Standardize exception usage across services
- [ ] Day 3: Extract business logic from routers
- [ ] Day 4: Add Pydantic request/response models
- [ ] Day 5: Update error handlers and tests

### Week 3: Architecture Improvements
- [ ] Day 1-2: Implement service interfaces (Protocols)
- [ ] Day 3-4: Implement repository pattern
- [ ] Day 5: Add unit of work pattern

### Week 4: Test Coverage
- [ ] Day 1-2: Add unit tests for `NewsService` (target: 60%+)
- [ ] Day 3: Add unit tests for `EmailService` (target: 60%+)
- [ ] Day 4: Add integration tests for API endpoints
- [ ] Day 5: Verify coverage goals met

## Quick Wins (Can Do Immediately)

### 1. Fix Error Handler Docstring
```python
# app/src/app/core/error_handler.py line 48
async def general_exception_handler(...):
    """  # Missing docstring opening
```

### 2. Add Type Hints to All Public Methods
- Services already have some, but ensure 100% coverage
- Add return type hints everywhere

### 3. Extract Constants
```python
# app/src/app/services/news_service.py
CACHE_TTL_SECONDS = 300
CACHE_KEY_PREFIX = "news:feed:"
```

### 4. Add Logging Context
```python
import structlog

logger = structlog.get_logger(__name__)

# Use structured logging
logger.info(
    "Fetching news",
    category=category,
    limit=limit,
    use_cache=use_cache
)
```

## Metrics to Track

- **Test Coverage**: 23% → 40% → 60% → 80%+
- **Code Complexity**: Use `radon cc` to measure
- **Number of Static Methods**: Reduce to 0 in services
- **Exception Usage**: 100% of errors use custom exceptions
- **Service Dependencies**: All injected via constructor

## Success Criteria

- [ ] All services use instance methods (no static methods)
- [ ] All errors use custom exceptions
- [ ] Test coverage > 60%
- [ ] All business logic extracted from routers
- [ ] Service interfaces defined
- [ ] Repository pattern implemented
- [ ] Zero breaking changes to public API

## Notes

- Refactor incrementally, one service at a time
- Write tests before refactoring (TDD approach)
- Keep commits small and focused
- Run tests after each change
- Update documentation as you go
