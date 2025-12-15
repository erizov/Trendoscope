# Trendoscope2

Improved version of Trendoscope with expanded news sources and better architecture.

## Features

- **100+ News Sources**: Expanded from 40 to 100+ sources including regional, business, tech, and social media
- **Redis Caching**: Docker-based Redis for improved performance
- **SQLite Database**: File-based database for local development
- **Translation**: Free Google Translate integration
- **Rutube Extractor**: Video to text extraction

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis (Docker)

```powershell
# Windows PowerShell
.\scripts\start.ps1
```

Or manually:
```bash
docker-compose -f docker/docker-compose.local.yml up -d redis
```

### 3. Run Application

```bash
python run.py
```

API will be available at: http://localhost:8004

## Scripts

- `scripts/start.ps1` - Start Redis and FastAPI app
- `scripts/stop.ps1` - Stop Redis container
- `scripts/restart.ps1` - Restart services

## E2E Test

Run the E2E test to verify everything works:

```bash
python tests/e2e/test_minimal_setup.py
```

Or with pytest:
```bash
pytest tests/e2e/test_minimal_setup.py -v
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/news/feed` - Get news feed
- `POST /api/news/translate` - Translate article
- `POST /api/rutube/generate` - Extract text from Rutube video

## Architecture

- **FastAPI**: Local Python process (port 8004)
- **Redis**: Docker container (port 6379)
- **SQLite**: File-based database in `data/databases/`

## Data Storage

All data is stored in the `data/` directory:
- `data/databases/` - SQLite databases
- `data/cache/` - Cache files
- `data/logs/` - Application logs
- `data/temp/` - Temporary files

