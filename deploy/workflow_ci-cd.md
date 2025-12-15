# Deployment / CI-CD Workflow Log

This log captures CI/CD steps run with Docker available.

## Environment
- Docker: running (`docker info` ok)
- Compose: v2.40 (`docker compose` CLI, no legacy `version` key)
- FastAPI port: 8004

## Steps Executed
1) Start Redis (Docker)
   - `cd trendoscope2`
   - `docker compose -f docker/docker-compose.local.yml up -d redis`
   - Health: `docker inspect ... trendoscope2-redis` → **healthy**
   - Health: `docker inspect ... trendoscope2-redis` → **healthy**

2) Start API (local process)
   - `Start-Process python run.py` (pid captured)
   - Health: `curl http://localhost:8004/health` → `{"status":"healthy","redis":"ok","database":"ok"}`

3) Full E2E Test Suite
   - `cd trendoscope2`
   - `pytest tests/e2e/test_minimal_setup.py -v --tb=short`
   - Result: **10 passed, 0 failed, 0 skipped**
   - Log: `data/logs/e2e_docker_run.log`

4) Teardown
   - `cd trendoscope2`
   - `docker compose -f docker/docker-compose.local.yml down`
   - `Stop-Process <pid>`

## Status
- Docker services: start/stop cleanly
- API endpoints: healthy (with Redis)
- Tests: full suite passing
- CI reference: see `.github/workflows/ci.yml` for lint + tests with Redis service
- Logging: level set via `LOG_LEVEL` env (default `warning` in env template)
- Monitoring endpoints (production compose under `deploy/docker/docker-compose.prod.yml`):
  - Prometheus: `http://localhost:9090/targets`
  - Grafana: `http://localhost:3000/`

## Production Deploy Stack (`deploy/`)

- `deploy/docker/docker-compose.prod.yml`
  - Services: `api` (FastAPI), `redis`, `postgres`, `prometheus`, `grafana`
  - Networks: `backend`, `monitoring`
- `deploy/docker/Dockerfile.api`
  - Builds the FastAPI image used by the `api` service
- `deploy/prometheus/prometheus.yml`
  - Scrapes the FastAPI, Redis, and Postgres endpoints
- `deploy/grafana/`
  - `provisioning/datasources/datasource.yml`
  - `provisioning/dashboards/dashboard.yml`
  - `dashboards/placeholder.json`
- `deploy/env_template.md`
  - Template for `.env.prod` with `DATABASE_URL`, `REDIS_URL`, `LOG_LEVEL`, and Grafana admin credentials

### Local Production-Style Run (all services)

From the repository root:

- Start stack:
  - `cd deploy`
  - `docker compose -f docker/docker-compose.prod.yml up -d`
- Check logs:
  - API: `docker logs -f deploy-api-1` (name may vary, check `docker ps`)
  - Redis/Postgres: `docker logs -f deploy-redis-1`, `docker logs -f deploy-postgres-1`
  - Prometheus: `docker logs -f deploy-prometheus-1`
  - Grafana: `docker logs -f deploy-grafana-1`
- Monitoring UIs:
  - Prometheus targets: `http://localhost:9090/targets`
  - Grafana UI: `http://localhost:3000/`
- Stop stack:
  - `cd deploy`
  - `docker compose -f docker/docker-compose.prod.yml down`

## CI/CD Status

✅ **GitHub Actions CI Pipeline** (`.github/workflows/ci.yml`):
- **Job `test`**: Lint (flake8, black, mypy) + unit tests with coverage
- **Job `e2e-docker`**: Minimal Docker + API E2E tests (`test_minimal_setup.py`)
- **Job `prod-stack-e2e`**: Full production stack E2E (`test_prod_stack.py`)
  - Validates `deploy/docker/docker-compose.prod.yml` stack
  - Tests API health, Prometheus targets, Grafana UI

All jobs run automatically on push/PR to `main` or `develop` branches.

## URL & Logs Reference

- **API (local / production-style stack)**  
  - Base: `http://localhost:8004/`  
  - Health: `http://localhost:8004/health`  
  - OpenAPI docs: `http://localhost:8004/docs`  
  - ReDoc docs: `http://localhost:8004/redoc`

- **Monitoring (from `deploy/docker/docker-compose.prod.yml`)**  
  - Prometheus targets: `http://localhost:9090/targets`  
  - Prometheus UI: `http://localhost:9090/graph`  
  - Grafana UI: `http://localhost:3000/` (credentials from `.env.prod`, see `deploy/env_template.md`)

- **E2E tests**  
  - Local (minimal stack, API started separately):  
    - From repo root:  
      - `cd trendoscope2`  
      - `pytest tests/e2e/test_minimal_setup.py -v --tb=short`  
  - Local (full production stack from `deploy/docker/docker-compose.prod.yml`):  
    - From repo root (requires Docker and compose):  
      - `pytest trendoscope2/tests/e2e/test_prod_stack.py -v --tb=short`  
  - GitHub Actions (see `.github/workflows/ci.yml`):  
    - Job `e2e-docker`: minimal Docker + API E2E  
    - Job `prod-stack-e2e`: full production `deploy/docker/docker-compose.prod.yml` E2E

- **Logs**  
  - Application/test logs (local): `trendoscope2/data/logs/`  
    - E2E Docker run log: `trendoscope2/data/logs/e2e_docker_run.log`  
  - Docker container logs (production-style):  
    - API: `docker logs -f deploy-api-1`  
    - Redis: `docker logs -f deploy-redis-1`  
    - Postgres: `docker logs -f deploy-postgres-1`  
    - Prometheus: `docker logs -f deploy-prometheus-1`  
    - Grafana: `docker logs -f deploy-grafana-1`

