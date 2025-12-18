# Test Coverage Improvement Plan

## Current Coverage Status

**Overall Coverage: 23%** (2063/2687 statements uncovered)

### Coverage by Module

#### Well Covered (80%+)
- `src/app/__init__.py` - 100%
- `src/app/api/__init__.py` - 100%
- `src/app/core/__init__.py` - 100%
- `src/app/core/settings.py` - 95%
- `src/app/config.py` - 87%
- `src/app/api/schemas.py` - 69%
- `src/app/core/error_handler.py` - 64%
- `src/app/core/exceptions.py` - 62%
- `src/app/core/dependencies.py` - 58%

#### Partially Covered (40-79%)
- `src/app/api/main.py` - 53%
- `src/app/api/routers/email.py` - 39%
- `src/app/api/routers/telegram.py` - 41%
- `src/app/api/routers/tts.py` - 30%
- `src/app/core/container.py` - 40%
- `src/app/utils/text_processing.py` - 33%

#### Poorly Covered (<40%)
- `src/app/api/routers/admin.py` - 23%
- `src/app/api/routers/news.py` - 25%
- `src/app/api/routers/rutube.py` - 23%
- `src/app/api/routers/__init__.py` - 22%
- `src/app/api/websocket_manager.py` - 0%
- `src/app/core/repositories.py` - 0%
- `src/app/services/cache_service.py` - 16%
- `src/app/services/categorization_service.py` - 27%
- `src/app/services/email_service.py` - 20%
- `src/app/services/news_service.py` - 18%
- `src/app/services/telegram_service.py` - 17%
- `src/app/services/task_queue.py` - 0%
- `src/app/services/background_tasks.py` - 28%
- `src/app/storage/news_db.py` - 17%
- `src/app/ingest/news_sources.py` - 0%
- `src/app/ingest/news_sources_async.py` - 11%
- `src/app/ingest/rutube_processor.py` - 0%
- `src/app/nlp/transcriber.py` - 0%
- `src/app/nlp/translator.py` - 16%
- `src/app/tts/gtts_provider.py` - 20%
- `src/app/tts/pyttsx3_provider.py` - 10%
- `src/app/tts/tts_service.py` - 12%
- `src/app/utils/encoding.py` - 10%

## Priority Areas for Improvement

### Phase 1: Critical Services (Target: 60%+ coverage)
1. **API Routers** (Currently 22-53%)
   - `admin.py` - Add tests for all admin endpoints
   - `news.py` - Test all news feed/search endpoints
   - `rutube.py` - Test Rutube video processing
   - `tts.py` - Expand TTS endpoint tests
   - `email.py` - Test email sending functionality
   - `telegram.py` - Test Telegram posting

2. **Core Services** (Currently 16-28%)
   - `cache_service.py` - Test caching logic
   - `news_service.py` - Test news aggregation
   - `email_service.py` - Test email operations
   - `telegram_service.py` - Test Telegram operations
   - `categorization_service.py` - Test categorization logic

3. **Storage Layer** (Currently 17%)
   - `news_db.py` - Test database operations
   - Add repository pattern tests

### Phase 2: Integration & E2E (Target: 50%+ coverage)
1. **Ingest Services** (Currently 0-11%)
   - `news_sources.py` - Test RSS fetching
   - `news_sources_async.py` - Test async news fetching
   - `rutube_processor.py` - Test Rutube processing

2. **NLP Services** (Currently 0-16%)
   - `transcriber.py` - Test transcription
   - `translator.py` - Test translation

3. **TTS Services** (Currently 10-20%)
   - `gtts_provider.py` - Test gTTS provider
   - `pyttsx3_provider.py` - Test pyttsx3 provider
   - `tts_service.py` - Test TTS service orchestration

### Phase 3: Infrastructure (Target: 70%+ coverage)
1. **WebSocket** (Currently 0%)
   - `websocket_manager.py` - Test WebSocket connections

2. **Task Queue** (Currently 0%)
   - `task_queue.py` - Test background task processing

3. **Background Tasks** (Currently 28%)
   - `background_tasks.py` - Test scheduled tasks

4. **Utilities** (Currently 10-33%)
   - `encoding.py` - Test encoding utilities
   - `text_processing.py` - Test text processing

## Implementation Plan

### Step 1: Fix Existing Test Issues
- [ ] Fix `test_news_search.py` import error
- [ ] Fix circular import in `test_cache_service.py`
- [ ] Register `@pytest.mark.slow` marker in `pytest.ini`

### Step 2: Add Unit Tests for Core Services
- [ ] `services/cache_service.py` - Test all cache operations
- [ ] `services/news_service.py` - Test news fetching and processing
- [ ] `services/email_service.py` - Test email sending and validation
- [ ] `services/telegram_service.py` - Test Telegram posting
- [ ] `services/categorization_service.py` - Test categorization logic

### Step 3: Add Integration Tests for API Endpoints
- [ ] `api/routers/admin.py` - Test all admin endpoints
- [ ] `api/routers/news.py` - Test all news endpoints
- [ ] `api/routers/rutube.py` - Test Rutube endpoints
- [ ] `api/routers/tts.py` - Expand TTS endpoint tests
- [ ] `api/routers/email.py` - Test email endpoints
- [ ] `api/routers/telegram.py` - Test Telegram endpoints

### Step 4: Add Tests for Ingest Services
- [ ] `ingest/news_sources.py` - Test RSS fetching with mocks
- [ ] `ingest/news_sources_async.py` - Test async fetching
- [ ] `ingest/rutube_processor.py` - Test Rutube processing

### Step 5: Add Tests for NLP Services
- [ ] `nlp/transcriber.py` - Test transcription with mocks
- [ ] `nlp/translator.py` - Test translation with mocks

### Step 6: Add Tests for TTS Services
- [ ] `tts/gtts_provider.py` - Test gTTS with mocks
- [ ] `tts/pyttsx3_provider.py` - Test pyttsx3 provider
- [ ] `tts/tts_service.py` - Test service orchestration

### Step 7: Add Tests for Infrastructure
- [ ] `api/websocket_manager.py` - Test WebSocket connections
- [ ] `services/task_queue.py` - Test task queue operations
- [ ] `services/background_tasks.py` - Test background tasks
- [ ] `utils/encoding.py` - Test encoding utilities

### Step 8: Add E2E Tests
- [ ] Full news aggregation flow
- [ ] TTS generation flow
- [ ] Email sending flow
- [ ] Telegram posting flow
- [ ] WebSocket real-time updates

## Testing Best Practices

### Unit Tests
- Use mocks for external dependencies (HTTP, Redis, DB)
- Test edge cases and error conditions
- Test validation logic
- Keep tests fast (<100ms each)

### Integration Tests
- Use TestClient for API endpoints
- Test with real dependencies when possible
- Test error handling
- Test authentication/authorization

### E2E Tests
- Test complete user workflows
- Use real services (with test credentials)
- Test performance under load
- Test failure scenarios

## Coverage Goals

- **Phase 1 (Month 1)**: 40% overall coverage
- **Phase 2 (Month 2)**: 60% overall coverage
- **Phase 3 (Month 3)**: 80% overall coverage
- **Target**: 85%+ overall coverage

## Tools & Commands

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run specific test category
pytest tests/unit/ --cov=src/app/services
pytest tests/integration/ --cov=src/app/api
pytest tests/e2e/

# Check coverage threshold
pytest tests/ --cov=src --cov-fail-under=60

# Generate HTML report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html
```

## Notes

- Some modules (like `news_sources.py`) require mocking external HTTP calls
- TTS tests may require actual TTS libraries or mocks
- WebSocket tests require async test setup
- Database tests should use test database or mocks
- Redis tests should use test Redis instance or mocks
