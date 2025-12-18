# Docker Deployment Plan

## Overview

This directory contains Docker deployment configurations for Trendoscope2.

## Architecture

### Services
1. **API Service** (FastAPI)
   - Port: 8000
   - Health check: `/health`
   - Main application

2. **Redis** (Optional)
   - Port: 6379
   - Used for caching and task queue

3. **Frontend** (React/Vite)
   - Port: 3000 (dev) or served via API (prod)
   - Built and served as static files in production

4. **Database** (SQLite)
   - File-based, mounted volume
   - Or PostgreSQL for production

## Deployment Strategies

### Development
- Use `docker-compose.dev.yml`
- Hot reload enabled
- Volume mounts for code
- Development dependencies

### Production
- Use `docker-compose.yml`
- Multi-stage builds
- Optimized images
- Health checks
- Resource limits

## File Structure

```
deploy/docker/
├── README.md (this file)
├── docker-compose.yml (production)
├── docker-compose.dev.yml (development)
├── Dockerfile (production API)
├── Dockerfile.dev (development API)
├── Dockerfile.frontend (React build)
├── .env.example (environment template)
└── nginx/
    └── nginx.conf (reverse proxy, optional)
```

## Environment Variables

See `.env.example` for required variables:
- `REDIS_URL`
- `DATABASE_URL`
- `EMAIL_SMTP_*`
- `TELEGRAM_BOT_TOKEN`
- etc.

## Deployment Steps

### Development
```bash
cd deploy/docker
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
cd deploy/docker
docker-compose up -d
```

## Health Checks

- API: `GET /health`
- Redis: Connection test
- Database: Connection test

## Volumes

- `./data` - Application data (database, audio files)
- `./logs` - Application logs

## Networking

- API: `localhost:8000`
- Frontend: `localhost:3000` (dev) or via API (prod)
- Redis: `localhost:6379`

## Security Considerations

- Use secrets management (Docker secrets, env files)
- Limit resource usage
- Network isolation
- Regular security updates

## Monitoring

- Health check endpoints
- Log aggregation
- Metrics collection (optional)

## Scaling

- Horizontal scaling for API (multiple instances)
- Redis cluster for high availability
- Load balancer (nginx) for frontend

## Backup Strategy

- Database backups (automated)
- Volume snapshots
- Configuration backups
