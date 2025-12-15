# Production Environment Template

Create a `.env.prod` file (not committed) with the following variables:

```
# Database
POSTGRES_USER=trendoscope
POSTGRES_PASSWORD=trendoscope
POSTGRES_DB=trendoscope
DATABASE_URL=postgresql+psycopg2://trendoscope:trendoscope@postgres:5432/trendoscope

# Redis
REDIS_URL=redis://redis:6379/0

# App
LOG_LEVEL=warning

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

