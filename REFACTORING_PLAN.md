# Refactoring Plan

## Overview

This document outlines a comprehensive refactoring plan to improve code quality, maintainability, and architecture of the Trendoscope project.

## Current Architecture Analysis

### Strengths
- ✅ Clear separation of concerns (API, services, storage)
- ✅ Dependency injection pattern
- ✅ Type hints in public APIs
- ✅ Error handling structure
- ✅ Repository pattern foundation

### Weaknesses
- ❌ Low test coverage (23%)
- ❌ Circular import issues
- ❌ Missing module implementations (news_search)
- ❌ Inconsistent error handling
- ❌ Large service classes
- ❌ Mixed sync/async patterns
- ❌ Limited logging
- ❌ No API versioning

## Refactoring Priorities

### Priority 1: Critical Issues (Immediate)

#### 1.1 Fix Circular Imports
**Problem**: Circular dependencies between modules
**Impact**: High - prevents proper testing and causes runtime issues

**Solution**:
- [ ] Refactor `core/container.py` to use lazy imports
- [ ] Move service initialization to factory functions
- [ ] Use dependency injection more consistently
- [ ] Break circular dependencies with interfaces

**Files to modify**:
- `src/app/core/container.py`
- `src/app/services/cache_service.py`
- `src/app/config.py`

#### 1.2 Fix Missing Modules
**Problem**: `app.storage.news_search` module doesn't exist
**Impact**: High - test failures

**Solution**:
- [ ] Create `src/app/storage/news_search.py` or
- [ ] Update test to use correct import path
- [ ] Implement missing functionality

**Files to modify**:
- `tests/unit/test_news_search.py`
- Create or update storage module

#### 1.3 Improve Error Handling
**Problem**: Inconsistent error handling across modules
**Impact**: Medium - poor user experience

**Solution**:
- [ ] Standardize exception types
- [ ] Add proper error messages
- [ ] Implement error logging
- [ ] Add error recovery mechanisms

**Files to modify**:
- `src/app/core/exceptions.py`
- `src/app/core/error_handler.py`
- All service modules

### Priority 2: Code Quality (Short-term)

#### 2.1 Service Layer Refactoring
**Problem**: Large service classes with multiple responsibilities
**Impact**: Medium - hard to test and maintain

**Solution**:
- [ ] Split large services into smaller, focused classes
- [ ] Extract common functionality to base classes
- [ ] Use composition over inheritance
- [ ] Implement service interfaces

**Services to refactor**:
- `news_service.py` (147 lines, 18% coverage)
- `email_service.py` (133 lines, 20% coverage)
- `telegram_service.py` (132 lines, 17% coverage)
- `cache_service.py` (164 lines, 16% coverage)

#### 2.2 API Router Organization
**Problem**: Routers have mixed concerns
**Impact**: Medium - harder to maintain

**Solution**:
- [ ] Group related endpoints
- [ ] Extract business logic to services
- [ ] Add request/response validation
- [ ] Implement API versioning

**Routers to refactor**:
- `api/routers/news.py`
- `api/routers/admin.py`
- `api/routers/tts.py`

#### 2.3 Async/Sync Pattern Consistency
**Problem**: Mixed async and sync code
**Impact**: Medium - performance and complexity

**Solution**:
- [ ] Standardize on async for I/O operations
- [ ] Convert sync services to async where appropriate
- [ ] Use async context managers
- [ ] Proper async error handling

**Files to refactor**:
- `ingest/news_sources.py` (sync) vs `news_sources_async.py` (async)
- Service layer async consistency

### Priority 3: Architecture Improvements (Medium-term)

#### 3.1 Repository Pattern Enhancement
**Problem**: Repository pattern not fully implemented
**Impact**: Medium - tight coupling to storage

**Solution**:
- [ ] Complete repository implementation
- [ ] Add repository interfaces
- [ ] Implement unit of work pattern
- [ ] Add repository tests

**Files to create/modify**:
- `src/app/core/repositories.py` (currently 0% coverage)
- Repository implementations
- Repository tests

#### 3.2 Dependency Injection Improvements
**Problem**: DI container not fully utilized
**Impact**: Low - but affects testability

**Solution**:
- [ ] Complete DI container implementation
- [ ] Use DI for all dependencies
- [ ] Add lifecycle management
- [ ] Improve test fixtures

**Files to modify**:
- `src/app/core/container.py`
- `src/app/core/dependencies.py`

#### 3.3 Configuration Management
**Problem**: Configuration scattered across files
**Impact**: Low - but affects maintainability

**Solution**:
- [ ] Centralize configuration
- [ ] Add configuration validation
- [ ] Environment-specific configs
- [ ] Configuration documentation

**Files to modify**:
- `src/app/core/settings.py`
- `src/app/config.py`

### Priority 4: Testing Infrastructure (Ongoing)

#### 4.1 Test Infrastructure
**Problem**: Test setup issues and low coverage
**Impact**: High - prevents confident refactoring

**Solution**:
- [ ] Fix test import issues
- [ ] Add test fixtures
- [ ] Create test utilities
- [ ] Add test data factories
- [ ] Implement test coverage goals

**See**: `TEST_COVERAGE_IMPROVEMENT_PLAN.md`

#### 4.2 Mocking Strategy
**Problem**: No consistent mocking approach
**Impact**: Medium - affects test reliability

**Solution**:
- [ ] Create mock factories
- [ ] Standardize mock patterns
- [ ] Add integration test helpers
- [ ] Document mocking guidelines

### Priority 5: Documentation & Standards (Ongoing)

#### 5.1 Code Documentation
**Problem**: Inconsistent docstrings and comments
**Impact**: Low - but affects maintainability

**Solution**:
- [ ] Add docstrings to all public APIs
- [ ] Document complex algorithms
- [ ] Add type hints everywhere
- [ ] Create architecture documentation

#### 5.2 Code Standards
**Problem**: Some PEP 8 violations
**Impact**: Low - but affects code quality

**Solution**:
- [ ] Run automated linting
- [ ] Fix all linting errors
- [ ] Add pre-commit hooks
- [ ] Document coding standards

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Fix circular imports
- [ ] Fix missing modules
- [ ] Improve error handling
- [ ] Set up test infrastructure

### Phase 2: Service Layer (Weeks 3-4)
- [ ] Refactor large services
- [ ] Extract common functionality
- [ ] Add service interfaces
- [ ] Improve service tests

### Phase 3: API Layer (Weeks 5-6)
- [ ] Refactor API routers
- [ ] Add API versioning
- [ ] Improve validation
- [ ] Enhance error responses

### Phase 4: Architecture (Weeks 7-8)
- [ ] Complete repository pattern
- [ ] Enhance DI container
- [ ] Improve configuration
- [ ] Add monitoring

### Phase 5: Testing & Documentation (Ongoing)
- [ ] Increase test coverage to 80%+
- [ ] Add comprehensive documentation
- [ ] Create developer guides
- [ ] Document architecture decisions

## Refactoring Principles

1. **Incremental**: Small, focused changes
2. **Tested**: Tests before and after refactoring
3. **Documented**: Document all changes
4. **Reversible**: Keep ability to rollback
5. **Measured**: Track metrics (coverage, complexity)

## Metrics to Track

- Test coverage percentage
- Code complexity (cyclomatic complexity)
- Number of circular dependencies
- Average class size
- Number of public APIs
- Documentation coverage

## Risk Mitigation

1. **Feature Freeze**: Pause new features during major refactoring
2. **Feature Flags**: Use flags for gradual rollout
3. **Comprehensive Testing**: Ensure all tests pass
4. **Code Reviews**: Review all refactoring changes
5. **Staging Environment**: Test in staging before production

## Success Criteria

- [ ] Test coverage > 80%
- [ ] No circular import errors
- [ ] All tests passing
- [ ] Code complexity reduced
- [ ] Documentation complete
- [ ] Performance maintained or improved
- [ ] Zero breaking changes to public API

## Tools & Automation

### Linting
```bash
flake8 src/ tests/
black --check src/ tests/
mypy src/
```

### Testing
```bash
pytest tests/ --cov=src --cov-report=html
pytest tests/ --cov=src --cov-fail-under=80
```

### Complexity Analysis
```bash
radon cc src/ -a
radon mi src/
```

### Dependency Analysis
```bash
pydeps src/app --show-deps
```

## Notes

- Refactoring should be done incrementally
- Each refactoring should be committed separately
- All refactoring should maintain backward compatibility
- Performance should not degrade
- Focus on high-impact, low-risk changes first
