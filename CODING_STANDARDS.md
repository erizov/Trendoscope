## Coding Standards

### 1. General Principles

- **Style guide**: Follow PEP 8 with a maximum line length of 79 characters.
- **Encoding**: All source files use UTF-8.
- **Imports**:
  - Standard library → third‑party → local imports.
  - One import per line.
  - Avoid unused imports.
- **Naming**:
  - Modules, functions, variables: `snake_case`.
  - Classes: `CapWords`.
  - Constants: `UPPER_SNAKE_CASE`.
  - Private helpers: prefix with `_`.

### 2. Type Hints and Docstrings

- **Type hints**:
  - Required for all public functions and methods (arguments and return types).
  - Use `Optional[T]` or `T | None` instead of bare `None` defaults.
- **Docstrings**:
  - Public APIs (routers, services, repositories) must have docstrings.
  - Use PEP 257 style:
    - One-line summary on the first line.
    - For multi-line docstrings, add a blank line after the summary.
  - Explain **why** and important edge cases, not just what.

### 3. Exceptions and Error Handling

- Never use bare `except:`.
- Use `Exception` only at the API boundary; elsewhere catch specific exceptions.
- Use project-specific exception types from `app.core.exceptions`:
  - `TrendoscopeException` base class.
  - Specialized errors: `NewsFetchError`, `TranslationError`, `EmailError`,
    `TelegramError`, `TTSError`, `ValidationError`, `DatabaseError`, etc.
- Prefer guard clauses over deeply nested conditionals.

### 4. Async vs Sync

- Use `async` for I/O-bound operations (database, network, external APIs).
- Keep CPU-bound work in sync helpers or offload to background tasks.
- Do not block the event loop with long `time.sleep`; use `asyncio.sleep`.
- Use async context managers where appropriate (e.g. database sessions,
  async clients).

### 5. Logging

- Use the standard `logging` library; avoid `print` in server code.
- Create a module-level logger:

```python
import logging

logger = logging.getLogger(__name__)
```

- Log errors with `exc_info=True` when useful for debugging.
- Avoid logging secrets (API keys, tokens, passwords).

### 6. Configuration

- Centralize configuration via `app.core.settings` and `app.config`.
- Use environment variables (via Pydantic settings) instead of hardcoding.
- Use the `ConfigManager` for environment-specific configuration and
  validation.

### 7. Testing

- Prefer small, focused tests:
  - Unit tests for services and utilities.
  - Integration tests for API endpoints and storage.
- Use factories from `app.tests.utils.factories` for test data.
- Avoid hitting real external services; use mocks/fakes.

### 8. Linting and Pre-commit

- Linting is configured via `ruff` in `pyproject.toml`.
- Run linters before committing:

```bash
ruff check app/src/app
```

- Pre-commit hooks are configured in `.pre-commit-config.yaml`:
  - `ruff` for Python linting.
  - Basic whitespace and config-file checks.

