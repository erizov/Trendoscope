# 🏗️ Architecture Analysis & Refactoring Plan

## 📊 Current State Analysis

### Project Structure
```
trendoscope2/
├── src/
│   ├── frontend/              # Frontend HTML files
│   └── trendoscope2/
│       ├── api/               # FastAPI endpoints (main.py - 1115 lines!)
│       ├── config.py          # Configuration (110 lines)
│       ├── ingest/            # News aggregation
│       ├── nlp/               # Translation & transcription
│       ├── services/          # Business logic services
│       ├── storage/           # Database layer
│       └── tts/               # Text-to-speech
└── tests/                     # Test suite
```

### Critical Issues Found

#### 1. **Monolithic API File** ⭐⭐⭐ CRITICAL
- **Problem**: `main.py` has **1115 lines** with 18+ endpoints
- **Issues**:
  - Hard to maintain and navigate
  - Difficult to test individual endpoints
  - Code duplication (encoding fixes, HTML cleaning)
  - Mixed concerns (business logic in API layer)
- **Impact**: High - affects maintainability and scalability

#### 2. **Code Duplication** ⭐⭐⭐ CRITICAL
- **Encoding Fix Logic**: Duplicated in `main.py` and `news_sources_async.py`
- **HTML Cleaning**: Duplicated in `main.py` and `news_sources_async.py`
- **Safe String Conversion**: Repeated `safe_str` helper in multiple places
- **Impact**: High - bugs need to be fixed in multiple places

#### 3. **Missing Abstraction Layers** ⭐⭐⭐ CRITICAL
- **No Dependency Injection**: Services instantiated globally
- **No Repository Pattern**: Direct database access in endpoints
- **No Service Layer**: Business logic mixed with API handlers
- **Impact**: High - hard to test, swap implementations, or mock

#### 4. **Configuration Management** ⭐⭐ IMPORTANT
- **Current**: Flat config.py with many variables
- **Better**: Pydantic-based Settings class with validation
- **Impact**: Medium - improves type safety and validation

#### 5. **Error Handling** ⭐⭐ IMPORTANT
- **Inconsistent**: Mix of try/except, HTTPException, bare except
- **No Error Codes**: Generic error messages
- **No Retry Logic**: Network failures not retried
- **Impact**: Medium - affects reliability and debugging

#### 6. **Helper Functions in main.py** ⭐⭐ IMPORTANT
- **`_categorize_news`**: 160+ lines, should be in separate module
- **`fix_double_encoding`**: Should be in utils
- **`clean_html`**: Should be in utils
- **Impact**: Medium - clutters main.py

#### 7. **Missing Utilities Module** ⭐⭐ IMPORTANT
- No centralized utilities for:
  - Text processing (encoding, HTML cleaning)
  - Validation helpers
  - Common transformations
- **Impact**: Medium - code duplication

---

## 🚀 Refactoring Recommendations

### Phase 1: Extract Utilities (High Impact, Low Risk) ⭐⭐⭐

#### 1.1 Create `utils/` Module
```
src/trendoscope2/utils/
├── __init__.py
├── text_processing.py    # Encoding fixes, HTML cleaning
├── validation.py         # Validation helpers
└── encoding.py           # Encoding utilities
```

**Benefits**:
- ✅ Eliminates code duplication
- ✅ Reusable across modules
- ✅ Easier to test
- ✅ Single source of truth

**Files to Create**:
- `src/trendoscope2/utils/text_processing.py`
- `src/trendoscope2/utils/encoding.py`

**Functions to Extract**:
- `fix_double_encoding()` → `utils/encoding.py`
- `clean_html()` → `utils/text_processing.py`
- `safe_str()` → `utils/encoding.py`

---

### Phase 2: Split API Endpoints (High Impact, Medium Risk) ⭐⭐⭐

#### 2.1 Create Router Modules
```
src/trendoscope2/api/
├── __init__.py
├── main.py              # App setup, lifespan, middleware
├── routers/
│   ├── __init__.py
│   ├── news.py          # News endpoints
│   ├── tts.py           # TTS endpoints
│   ├── email.py         # Email endpoints
│   ├── telegram.py      # Telegram endpoints
│   ├── rutube.py        # Rutube endpoints
│   └── admin.py         # Admin/DB management endpoints
└── schemas.py
```

**Benefits**:
- ✅ Each router ~200-300 lines (manageable)
- ✅ Clear separation of concerns
- ✅ Easier to find and modify endpoints
- ✅ Better testability

**Migration Strategy**:
1. Create router files
2. Move endpoints one by one
3. Update imports in main.py
4. Test after each move

---

### Phase 3: Extract Business Logic (High Impact, Medium Risk) ⭐⭐⭐

#### 3.1 Create Service Layer
```
src/trendoscope2/services/
├── __init__.py
├── news_service.py      # News processing logic
├── categorization_service.py  # News categorization
├── email_service.py     # ✅ Already exists
├── telegram_service.py  # ✅ Already exists
└── background_tasks.py   # ✅ Already exists
```

**Functions to Extract**:
- `_categorize_news()` → `services/categorization_service.py`
- News processing logic from `get_news_feed()` → `services/news_service.py`

**Benefits**:
- ✅ Business logic separated from API
- ✅ Reusable across different interfaces
- ✅ Easier to test
- ✅ Can be used by background tasks

---

### Phase 4: Dependency Injection (Medium Impact, High Value) ⭐⭐

#### 4.1 Create Dependency Container
```
src/trendoscope2/core/
├── __init__.py
├── container.py         # DI container
└── dependencies.py      # FastAPI dependencies
```

**Implementation**:
```python
# core/container.py
class Container:
    def __init__(self):
        self.news_aggregator = AsyncNewsAggregator(timeout=NEWS_FETCH_TIMEOUT)
        self.tts_service = TTSService(...)
        self.email_service = EmailService(...)
        self.telegram_service = TelegramService(...)
        self.news_db = NewsDatabase()

# Use in endpoints
@app.get("/api/news/feed")
async def get_news_feed(
    container: Container = Depends(get_container)
):
    return await container.news_service.get_feed(...)
```

**Benefits**:
- ✅ Centralized dependency management
- ✅ Easy to mock for tests
- ✅ Lifecycle management
- ✅ Configuration-driven

---

### Phase 5: Configuration Refactoring (Medium Impact, Low Risk) ⭐⭐

#### 5.1 Pydantic Settings
```python
# config.py → core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # News Configuration
    news_db_max_records: int = 10000
    news_fetch_timeout: int = 10
    news_max_per_source: int = 2
    
    # TTS Configuration
    tts_provider: str = "auto"
    tts_cache_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**Benefits**:
- ✅ Type safety
- ✅ Validation on startup
- ✅ IDE autocomplete
- ✅ Documentation generation

---

### Phase 6: Error Handling Improvements (Medium Impact) ⭐⭐

#### 6.1 Structured Error Handling
```python
# core/exceptions.py
class TrendoscopeException(Exception):
    """Base exception."""
    error_code: str
    status_code: int = 500

class NewsFetchError(TrendoscopeException):
    error_code = "NEWS_FETCH_ERROR"
    status_code = 503

# core/error_handler.py
@app.exception_handler(TrendoscopeException)
async def handle_trendoscope_error(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "detail": str(exc)
        }
    )
```

**Benefits**:
- ✅ Consistent error responses
- ✅ Error codes for client handling
- ✅ Better debugging
- ✅ User-friendly messages

---

### Phase 7: Repository Pattern (Low Priority, High Value) ⭐

#### 7.1 Abstract Repository
```python
# core/repositories.py
from abc import ABC, abstractmethod

class NewsRepository(ABC):
    @abstractmethod
    async def get_recent(self, category: str, limit: int) -> List[Dict]:
        pass
    
    @abstractmethod
    async def save(self, item: Dict) -> None:
        pass

class SQLiteNewsRepository(NewsRepository):
    def __init__(self, db: NewsDatabase):
        self.db = db
    
    async def get_recent(self, category: str, limit: int):
        return self.db.get_recent(category, limit)
```

**Benefits**:
- ✅ Easy to swap storage backends
- ✅ In-memory repository for testing
- ✅ Clear data access contracts

---

## 📋 Implementation Priority

### Immediate (Week 1)
1. ✅ Extract utilities (`utils/text_processing.py`, `utils/encoding.py`)
2. ✅ Extract `_categorize_news` to `services/categorization_service.py`
3. ✅ Create Pydantic Settings class

### Short-term (Week 2-3)
4. ✅ Split API into routers
5. ✅ Create news service layer
6. ✅ Implement dependency injection

### Medium-term (Month 2)
7. ✅ Structured error handling
8. ✅ Repository pattern
9. ✅ Retry logic and circuit breakers

---

## 🎯 Specific Refactoring Tasks

### Task 1: Extract Text Processing Utilities

**Create**: `src/trendoscope2/utils/__init__.py`
**Create**: `src/trendoscope2/utils/encoding.py`
**Create**: `src/trendoscope2/utils/text_processing.py`

**Move from `main.py`**:
- `fix_double_encoding()` → `utils/encoding.py`
- `clean_html()` → `utils/text_processing.py`
- `safe_str()` → `utils/encoding.py`

**Update imports in**:
- `main.py`
- `news_sources_async.py`

---

### Task 2: Extract Categorization Service

**Create**: `src/trendoscope2/services/categorization_service.py`

**Move from `main.py`**:
- `_categorize_news()` → `CategorizationService.categorize()`

**Benefits**:
- Can be reused by background tasks
- Easier to test
- Can be extended with ML models

---

### Task 3: Split API Routers

**Create routers**:
- `api/routers/news.py` - News endpoints (~300 lines)
- `api/routers/tts.py` - TTS endpoints (~200 lines)
- `api/routers/email.py` - Email endpoints (~150 lines)
- `api/routers/telegram.py` - Telegram endpoints (~150 lines)
- `api/routers/rutube.py` - Rutube endpoints (~100 lines)
- `api/routers/admin.py` - Admin endpoints (~100 lines)

**Keep in `main.py`**:
- App initialization
- Lifespan management
- Middleware setup
- Router registration

---

### Task 4: Create News Service

**Create**: `src/trendoscope2/services/news_service.py`

**Extract from `get_news_feed()`**:
- News fetching logic
- Encoding fixes
- HTML cleaning
- Categorization
- Translation

**API endpoint becomes thin**:
```python
@app.get("/api/news/feed")
async def get_news_feed(
    category: str = Query(...),
    limit: int = Query(...),
    service: NewsService = Depends(get_news_service)
):
    return await service.get_feed(category, limit)
```

---

## 📊 Metrics & Goals

### Code Quality Goals
- **main.py**: Reduce from 1115 → ~200 lines (app setup only)
- **Max file size**: 300 lines per file
- **Code duplication**: < 5%
- **Test coverage**: > 80%

### Architecture Goals
- ✅ Clear separation of concerns
- ✅ Dependency injection for all services
- ✅ Repository pattern for data access
- ✅ Service layer for business logic
- ✅ Utilities for common operations

---

## 🔍 Additional Improvements

### 1. Add Type Hints Everywhere ⭐⭐
- Full type hints for all functions
- Use `mypy` for type checking
- Better IDE support

### 2. Add Docstrings ⭐⭐
- All public functions need docstrings
- Use Google/NumPy style
- Include examples for complex functions

### 3. Add Request/Response Models ⭐
- Pydantic models for all responses
- Consistent response format
- API documentation generation

### 4. Add Middleware for Logging ⭐
- Request/response logging
- Performance metrics
- Error tracking

### 5. Add Health Checks ⭐
- ✅ Already exists, but can be improved
- Check all dependencies
- Return detailed status

### 6. Add Metrics Endpoint ⭐
- Prometheus metrics
- Performance counters
- Business metrics

### 7. Add API Versioning ⭐
- `/api/v1/...` prefix
- Support multiple versions
- Deprecation strategy

---

## 🚨 Breaking Changes

### None Expected
All refactoring can be done incrementally without breaking existing functionality.

### Migration Path
1. Create new modules alongside old code
2. Update imports gradually
3. Remove old code after verification
4. Run tests after each step

---

## 📝 Summary

### Critical Issues (Must Fix)
1. ⭐⭐⭐ Monolithic `main.py` (1115 lines)
2. ⭐⭐⭐ Code duplication (encoding, HTML cleaning)
3. ⭐⭐⭐ Missing abstraction layers (DI, services)

### Important Improvements
4. ⭐⭐ Configuration management (Pydantic Settings)
5. ⭐⭐ Error handling standardization
6. ⭐⭐ Helper functions extraction

### Nice to Have
7. ⭐ Repository pattern
8. ⭐ API versioning
9. ⭐ Metrics endpoint

---

## 🎬 Next Steps

1. **Start with utilities extraction** (lowest risk, high impact)
2. **Split API routers** (high impact, manageable risk)
3. **Extract business logic** (high value, medium effort)
4. **Add dependency injection** (enables better testing)

**Estimated Time**: 2-3 weeks for critical refactoring

---

**Last Updated**: 2025-01-XX
**Status**: Phase 1 Complete - Utilities Extracted

## ✅ Completed Refactoring (Phase 1)

### 1. Utilities Module Created
- ✅ `src/trendoscope2/utils/encoding.py` - Encoding utilities
- ✅ `src/trendoscope2/utils/text_processing.py` - HTML cleaning
- ✅ `src/trendoscope2/utils/__init__.py` - Module exports

**Functions Extracted**:
- `fix_double_encoding()` - Unified encoding fix (removed duplication)
- `clean_html()` - HTML tag removal
- `safe_str()` - Safe string conversion

**Impact**:
- ✅ Reduced `main.py` from 1115 → 897 lines (-218 lines, -19.5%)
- ✅ Eliminated code duplication between `main.py` and `news_sources_async.py`
- ✅ All tests passing

### 2. Categorization Service Created
- ✅ `src/trendoscope2/services/categorization_service.py`
- ✅ Extracted 160+ lines from `main.py`
- ✅ Reusable service class with keyword-based categorization

**Impact**:
- ✅ Business logic separated from API layer
- ✅ Can be reused by background tasks
- ✅ Easier to test and extend

### Next Steps (Phase 2)
1. Split API into routers (target: reduce main.py to ~200 lines)
2. Create news service layer
3. Implement dependency injection
