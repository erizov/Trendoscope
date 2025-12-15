# 🖥️ Local Infrastructure Plan for Trendoscope

## 📊 System Specifications

- **RAM**: 40 GB (20 GB free)
- **CPU**: Intel Core i5-10210U (4 cores, 8 threads)
- **Storage**: 2TB SSD + 512GB NVMe
- **Docker**: Installed ✅

**Assessment**: Excellent for local development! Can run multiple services comfortably.

---

## 🏗️ Recommended Local Architecture

### Option 1: Lightweight Docker Compose (Recommended)

**Best for**: Development, testing, and small-scale production simulation.

```yaml
# docker-compose.local.yml
version: '3.8'

services:
  # Main FastAPI Application
  trendoscope-api:
    build: .
    ports:
      - "8003:8003"
    volumes:
      - ./trendascope:/app/trendascope
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/trendoscope.db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  # Redis for caching and background jobs
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # PostgreSQL (optional, for production-like testing)
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=trendoscope
      - POSTGRES_USER=trendoscope
      - POSTGRES_PASSWORD=trendoscope_dev
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    profiles:
      - postgres  # Only start if needed

  # Prometheus for metrics (optional)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    profiles:
      - monitoring

  # Grafana for dashboards (optional)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
    profiles:
      - monitoring

volumes:
  redis-data:
  postgres-data:
  prometheus-data:
  grafana-data:
```

### Option 2: All-in-One Local Setup (Simplest)

**Best for**: Quick development, minimal resource usage.

```python
# Run everything in one process:
# - FastAPI app (main process)
# - SQLite database (file-based)
# - In-memory Redis (using fakeredis for dev)
# - Background tasks (asyncio tasks)
```

---

## 📁 Directory Structure

```
E:\Python\FastAPI\Trendoscope\
├── trendascope/              # Main application code
│   ├── src/
│   ├── tests/
│   └── data/                 # Local data storage
│       ├── databases/        # SQLite databases
│       │   ├── news.db
│       │   ├── posts.db
│       │   └── styles.db
│       ├── cache/            # Local cache files
│       ├── logs/             # Application logs
│       └── temp/             # Temporary files
│
├── docker/                    # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.local.yml
│   └── docker-compose.prod.yml
│
├── monitoring/                # Monitoring configs
│   ├── prometheus.yml
│   └── grafana/
│
├── scripts/                  # Utility scripts
│   ├── setup_local.sh
│   ├── start_services.sh
│   └── backup_data.sh
│
└── .env.local                # Local environment variables
```

---

## 🔧 Service Configuration

### 1. Database Strategy

**Development (Current)**: SQLite
- ✅ Zero configuration
- ✅ File-based (easy backup)
- ✅ Fast for small-medium datasets
- ✅ Perfect for local development

**Production Simulation**: PostgreSQL (Docker)
- Use when testing production features
- Only start when needed (`docker-compose --profile postgres up`)

```python
# config.py - Database selection
import os

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")  # sqlite or postgres

if DATABASE_TYPE == "sqlite":
    DATABASE_URL = "sqlite:///./data/databases/trendoscope.db"
elif DATABASE_TYPE == "postgres":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://trendoscope:trendoscope_dev@localhost:5432/trendoscope")
```

### 2. Caching Strategy

**Development**: 
- **L1**: In-memory (Python dict with LRU)
- **L2**: Redis (Docker) or fakeredis (no Docker)
- **L3**: SQLite database

```python
# utils/cache.py
import os
from typing import Optional

if os.getenv("USE_REDIS", "true").lower() == "true":
    try:
        import redis
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True
        )
        USE_REDIS = True
    except:
        USE_REDIS = False
        print("Redis not available, using in-memory cache")
else:
    USE_REDIS = False

if not USE_REDIS:
    # Fallback to in-memory cache
    from cachetools import LRUCache
    memory_cache = LRUCache(maxsize=1000)
```

### 3. Background Jobs

**Option A: Asyncio Tasks (Lightweight)**
```python
# services/background_tasks.py
import asyncio
from typing import List

class BackgroundTaskManager:
    """Manage background tasks using asyncio."""
    
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
    
    async def start_news_fetcher(self):
        """Start background news fetching."""
        while True:
            try:
                await self.fetch_news()
            except Exception as e:
                logger.error(f"News fetch error: {e}")
            await asyncio.sleep(60)  # Fetch every minute
    
    async def start_all(self):
        """Start all background tasks."""
        self.tasks.append(asyncio.create_task(self.start_news_fetcher()))
        # Add more tasks...
    
    async def stop_all(self):
        """Stop all background tasks."""
        for task in self.tasks:
            task.cancel()
```

**Option B: Celery (More Features)**
```python
# Only use if you need advanced features:
# - Task scheduling
# - Task retries
# - Task monitoring
# - Distributed workers

# celery_app.py
from celery import Celery

celery_app = Celery(
    'trendoscope',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
```

### 4. Monitoring (Optional)

**Lightweight Setup**:
- **Prometheus**: Metrics collection (Docker)
- **Grafana**: Dashboards (Docker)
- **Resource Usage**: ~200MB RAM each

**Start only when needed**:
```bash
docker-compose --profile monitoring up
```

---

## 💾 Storage Recommendations

### Data Storage Locations

```python
# config.py
import os
from pathlib import Path

# Base data directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "databases").mkdir(exist_ok=True)
(DATA_DIR / "cache").mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)
(DATA_DIR / "temp").mkdir(exist_ok=True)

# Database paths
NEWS_DB_PATH = DATA_DIR / "databases" / "news.db"
POSTS_DB_PATH = DATA_DIR / "databases" / "posts.db"
STYLES_DB_PATH = DATA_DIR / "databases" / "styles.db"
```

### Storage Size Estimates

- **SQLite Databases**: ~100-500 MB (50,000 news items)
- **Cache Files**: ~50-200 MB
- **Logs**: ~10-50 MB (rotate daily)
- **Temp Files**: ~100 MB (video processing)
- **Total**: ~500 MB - 1 GB

**With 2TB SSD**: Plenty of space! ✅

---

## 🚀 Startup Scripts

### Windows PowerShell Script

```powershell
# scripts/start_local.ps1
Write-Host "Starting Trendoscope Local Infrastructure..." -ForegroundColor Green

# Check if Docker is running
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 10
}

# Start services
Write-Host "Starting Redis..." -ForegroundColor Cyan
docker-compose -f docker/docker-compose.local.yml up -d redis

# Optional: Start PostgreSQL
$usePostgres = Read-Host "Start PostgreSQL? (y/n)"
if ($usePostgres -eq "y") {
    docker-compose -f docker/docker-compose.local.yml --profile postgres up -d postgres
}

# Optional: Start monitoring
$useMonitoring = Read-Host "Start monitoring (Prometheus/Grafana)? (y/n)"
if ($useMonitoring -eq "y") {
    docker-compose -f docker/docker-compose.local.yml --profile monitoring up -d
}

# Start FastAPI app
Write-Host "Starting FastAPI application..." -ForegroundColor Cyan
cd trendascope
python run.py

Write-Host "All services started!" -ForegroundColor Green
```

### Python Startup Script

```python
# scripts/start_local.py
import subprocess
import sys
import time
from pathlib import Path

def check_docker():
    """Check if Docker is available."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except:
        return False

def start_services():
    """Start local services."""
    if not check_docker():
        print("⚠️  Docker not available. Using in-memory alternatives.")
        return
    
    print("🐳 Starting Docker services...")
    
    # Start Redis
    subprocess.run([
        "docker-compose", "-f", "docker/docker-compose.local.yml",
        "up", "-d", "redis"
    ])
    
    print("✅ Services started!")
    print("📊 Redis: http://localhost:6379")
    print("📊 Prometheus: http://localhost:9090 (if enabled)")
    print("📊 Grafana: http://localhost:3000 (if enabled)")

if __name__ == "__main__":
    start_services()
```

---

## 🔄 Resource Management

### Memory Allocation

With 40GB RAM, you can comfortably run:

```
FastAPI App:        ~500 MB
Redis:              ~100 MB
PostgreSQL:         ~200 MB (if used)
Prometheus:         ~200 MB (if used)
Grafana:            ~200 MB (if used)
Background Tasks:   ~100 MB
─────────────────────────────────
Total:              ~1.3 GB (with all services)
```

**Plenty of headroom!** ✅

### CPU Usage

- **News Fetching**: CPU-intensive during fetch (parallel requests)
- **Translation**: CPU-intensive (NLP processing)
- **Background Tasks**: Low CPU (mostly I/O wait)

**Recommendation**: Limit concurrent background tasks to 4-6 to avoid overwhelming CPU.

---

## 📦 Docker Compose File

Create `docker/docker-compose.local.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: trendoscope-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  postgres:
    image: postgres:15-alpine
    container_name: trendoscope-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=trendoscope
      - POSTGRES_USER=trendoscope
      - POSTGRES_PASSWORD=trendoscope_dev
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    profiles:
      - postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trendoscope"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis-data:
    driver: local
  postgres-data:
    driver: local
```

---

## 🎯 Recommended Setup for Your Laptop

### Minimal Setup (Recommended for Development)

```bash
# 1. Start Redis only
docker-compose -f docker/docker-compose.local.yml up -d redis

# 2. Run FastAPI app locally
cd trendascope
python run.py
```

**Services Running**:
- ✅ FastAPI (localhost:8003)
- ✅ Redis (localhost:6379)
- ✅ SQLite databases (file-based)

**Resource Usage**: ~600 MB RAM

### Full Setup (For Production Testing)

```bash
# Start all services
docker-compose -f docker/docker-compose.local.yml --profile postgres --profile monitoring up -d

# Run FastAPI app
cd trendascope
python run.py
```

**Services Running**:
- ✅ FastAPI (localhost:8003)
- ✅ Redis (localhost:6379)
- ✅ PostgreSQL (localhost:5432)
- ✅ Prometheus (localhost:9090)
- ✅ Grafana (localhost:3000)

**Resource Usage**: ~1.5 GB RAM

---

## 🔒 Security Considerations

### Local Development
- ✅ Use weak passwords (dev only)
- ✅ Expose ports only to localhost
- ✅ No SSL/TLS needed locally

### Production
- ❌ Never use local setup for production
- ✅ Use proper authentication
- ✅ Use SSL/TLS
- ✅ Use secrets management

---

## 📝 Environment Variables

Create `.env.local`:

```bash
# Database
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/databases/trendoscope.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
USE_REDIS=true

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# API Keys (optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

## 🚀 Quick Start Guide

1. **Create data directories**:
   ```bash
   mkdir -p data/databases data/cache data/logs data/temp
   ```

2. **Start Redis**:
   ```bash
   docker-compose -f docker/docker-compose.local.yml up -d redis
   ```

3. **Run application**:
   ```bash
   cd trendascope
   python run.py
   ```

4. **Access services**:
   - API: http://localhost:8003
   - API Docs: http://localhost:8003/docs
   - Redis: localhost:6379

---

## 💡 Tips

1. **Use SQLite for development**: Faster, simpler, no Docker needed
2. **Start services on-demand**: Only start what you need
3. **Monitor resource usage**: Use Task Manager to check RAM/CPU
4. **Backup data regularly**: SQLite files are easy to backup
5. **Use profiles**: Docker Compose profiles let you start services selectively

---

## 📊 Resource Monitoring

### Check Docker Resource Usage

```bash
docker stats
```

### Check Disk Usage

```bash
# Windows
Get-ChildItem -Path .\data -Recurse | Measure-Object -Property Length -Sum
```

---

## 🎯 Summary

**Your laptop is perfect for local development!**

- ✅ 40GB RAM: Can run all services comfortably
- ✅ 2TB SSD: Plenty of storage space
- ✅ Docker installed: Ready for containerized services
- ✅ 4 cores: Good for parallel processing

**Recommended Setup**:
- Redis (Docker) for caching
- SQLite for databases (development)
- FastAPI app (local Python)
- Optional: PostgreSQL, Prometheus, Grafana (when needed)

**Total Resource Usage**: ~1-2 GB RAM (with all services)

You have plenty of headroom for development! 🚀

