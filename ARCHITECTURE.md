# 🏗️ Trendoscope Architecture

## Overview

Trendoscope is a modern, scalable AI content generation platform built with FastAPI and Python 3.11+.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  (Web UI, API Clients, Mobile Apps)                     │
└────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│                  API Layer (FastAPI)                    │
│  • Rate Limiting  • Request ID Tracking                │
│  • Error Handling • Response Standardization           │
└────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│                Service Layer                            │
│  • NewsService    • PostService                        │
│  • Business Logic • Validation                          │
└────────────────────┬──────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐      ┌──────────▼──────────┐
│  Data Layer    │      │   AI/LLM Layer      │
│  • News DB     │      │  • OpenAI           │
│  • RAG/FAISS   │      │  • Anthropic       │
│  • Post Storage│      │  • Demo Generator  │
└────────────────┘      └────────────────────┘
```

---

## Core Components

### 1. API Layer (`src/trendascope/api/`)

**Responsibilities**:
- HTTP request handling
- Rate limiting
- Request/response validation
- Error handling

**Key Files**:
- `main.py` - Main FastAPI app, endpoints
- `posts.py` - Post management endpoints
- `schemas.py` - Pydantic validation models

### 2. Service Layer (`src/trendascope/services/`)

**Responsibilities**:
- Business logic
- Data transformation
- Provider selection
- Cost optimization

**Key Files**:
- `news_service.py` - News aggregation and processing
- `post_service.py` - Post generation logic

### 3. Generation Layer (`src/trendascope/gen/`)

**Responsibilities**:
- Content generation
- LLM provider management
- Template-based generation (demo mode)
- Cost tracking

**Key Files**:
- `post_generator.py` - Main post generation
- `llm/providers.py` - LLM provider abstraction
- `demo_generator.py` - Template-based demo generation
- `model_selector.py` - Smart model selection
- `cost_tracker.py` - Cost tracking

### 4. Data Layer

#### News Storage (`src/trendascope/storage/news_db.py`)
- SQLite database
- Full-text search (FTS5)
- Controversy scoring
- Category filtering

#### Post Storage (`src/trendascope/storage/post_storage.py`)
- JSON-based persistence
- CRUD operations
- Metadata tracking

#### RAG Storage (`src/trendascope/index/vector_db.py`)
- FAISS vector database
- Semantic search
- Style learning

### 5. NLP Layer (`src/trendascope/nlp/`)

**Responsibilities**:
- Text analysis
- Style extraction
- Translation
- Controversy scoring

**Key Files**:
- `style_analyzer.py` - Extract writing style
- `translator.py` - News translation
- `controversy_scorer.py` - Provocation detection
- `context_aggregator.py` - News context building

### 6. Ingestion Layer (`src/trendascope/ingest/`)

**Responsibilities**:
- RSS feed fetching
- LiveJournal scraping
- Parallel processing
- Error handling

**Key Files**:
- `news_sources.py` - News aggregation
- `livejournal.py` - Blog scraping

### 7. Utilities (`src/trendascope/utils/`)

**Key Files**:
- `cache.py` - Caching (Redis + in-memory)
- `logger.py` - Structured logging
- `monitoring.py` - Metrics collection
- `response.py` - API response standardization
- `balance_checker.py` - AI balance checking
- `preferences.py` - User preferences

---

## Data Flow

### Post Generation Flow

```
1. User Request
   ↓
2. API Endpoint (rate limited, validated)
   ↓
3. PostService (balance check, provider selection)
   ↓
4. PostGenerator
   ├─→ Fetch News (NewsAggregator)
   ├─→ Translate (if needed, with balance check)
   ├─→ Filter by Topic (SemanticFilter)
   ├─→ Get Style Context (RAG search)
   └─→ Generate Post (LLM Provider)
   ↓
5. Post Storage (save if requested)
   ↓
6. Response (standardized format)
```

### News Feed Flow

```
1. User Request
   ↓
2. API Endpoint
   ↓
3. NewsService
   ├─→ Fetch News (parallel, 40+ sources)
   ├─→ Categorize
   ├─→ Score Controversy
   ├─→ Translate (if balance available)
   └─→ Sort by Recency
   ↓
4. Response (with metadata)
```

---

## Design Patterns

### Service Layer Pattern
- Business logic separated from API
- Testable components
- Reusable services

### Dependency Injection
- Services injected via FastAPI Depends
- Easy to mock for testing
- Flexible configuration

### Repository Pattern
- Data access abstracted
- Storage-agnostic business logic
- Easy to swap implementations

### Strategy Pattern
- Multiple LLM providers
- Different generation strategies
- Pluggable components

---

## Performance Optimizations

### Caching
- Redis for distributed caching
- In-memory fallback
- TTL-based expiration
- Cache invalidation strategies

### Parallel Processing
- News fetching: 10 parallel workers
- ThreadPoolExecutor for I/O
- Async endpoints ready

### Database Optimization
- Indexed queries
- Connection pooling
- Query optimization

### Cost Optimization
- Smart model selection (GPT-3.5 vs GPT-4)
- Reduced prompt sizes
- Translation skipping
- Balance checking before calls

---

## Security

### Rate Limiting
- Per-endpoint limits
- Per-IP tracking
- Configurable thresholds

### Input Validation
- Pydantic schemas
- Type checking
- Sanitization

### Error Handling
- Structured error responses
- No sensitive data leakage
- Comprehensive logging

---

## Monitoring & Observability

### Metrics
- Request counts
- Response times (avg, p95)
- Error rates
- Cost tracking
- Post generation stats

### Logging
- Structured JSON logs
- Request ID tracking
- Context-aware logging
- Log levels configurable

### Health Checks
- Component status
- Database connectivity
- Cache availability
- LLM provider status

---

## Deployment Architecture

### Development
```
Local Machine
├─→ Python 3.11+
├─→ SQLite (local)
├─→ FAISS (file-based)
└─→ In-memory cache
```

### Production
```
Cloud Platform / VPS
├─→ Docker container
├─→ PostgreSQL (optional)
├─→ Redis (optional)
├─→ FAISS (persistent)
└─→ Nginx reverse proxy
```

---

## Scalability Considerations

### Horizontal Scaling
- Stateless API layer
- Shared cache (Redis)
- Database connection pooling

### Vertical Scaling
- Async operations
- Parallel processing
- Efficient algorithms

### Future Enhancements
- Message queue (Celery)
- Distributed RAG
- CDN for static assets
- Load balancing

---

## Technology Choices

### Why FastAPI?
- High performance
- Automatic API docs
- Type validation
- Async support

### Why FAISS?
- Fast vector search
- Efficient memory usage
- Easy integration
- Production-ready

### Why SQLite?
- Zero configuration
- File-based (portable)
- FTS5 for search
- Easy backup

---

## Code Quality

### Standards
- Type hints throughout
- Pydantic validation
- Comprehensive error handling
- Structured logging

### Testing
- Unit tests for services
- Integration tests for API
- Test coverage tracking

### Documentation
- Docstrings for all functions
- API documentation (OpenAPI)
- Architecture documentation
- User guides

---

**Last Updated**: 2025-01-XX  
**Version**: 2.2.0

