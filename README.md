<<<<<<< HEAD
# Trendoscope Project

**AI-Powered News Aggregation & Content Generation Platform**

## Project Structure

```
Trendoscope/
├── app/                   # ✅ ACTIVE APPLICATION
│   ├── src/               # Source code
│   ├── tests/             # Test suite
│   ├── frontend/          # React frontend
│   └── run.py             # Entry point
├── archive/               # Archived legacy versions
│   ├── trendoscope/      # Old version
│   └── trendascope/       # Old version
├── deploy/                # Deployment configurations
│   └── docker/           # Docker deployment plan
└── README.md             # This file
```

## Active Application

The current active application is **`app/`**.

See `app/README.md` for detailed documentation.

## Quick Start

```bash
cd app
python run.py
```

Access:
- API: http://localhost:8004
- Docs: http://localhost:8004/docs

## Docker Deployment

See `deploy/docker/README.md` for Docker deployment instructions.

## Archive

Legacy versions are stored in `archive/` for reference only.

=======
# Trendoscope2

**AI-Powered News Aggregation & Content Generation Platform**

FastAPI-based application for aggregating news from multiple sources, processing content, and generating text-to-speech audio.

## Features

- 📰 **News Aggregation**: Fetch news from 40+ RSS sources
- 🔍 **Full-Text Search**: Advanced search with filters (category, language, source, date)
- 💾 **Redis Caching**: Multi-tier caching for 50-80% performance improvement
- ⚡ **Real-time Updates**: WebSocket support for live news feed
- 🎙️ **Text-to-Speech**: Generate audio from text with multiple providers
- 📧 **Email Integration**: Send daily digests and notifications
- 📱 **Telegram Bot**: Post news to Telegram channels
- 🎯 **Task Queue**: Background job processing with RQ/Celery
- ⚛️ **React Frontend**: Modern SPA with real-time updates

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for caching and task queue)
- Node.js 18+ (for frontend)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (optional)
cd frontend && npm install
```

### Configuration

Copy `env_template.txt` to `.env` and configure:

```bash
# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
USE_REDIS=true

# Email (optional)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
```

### Run

```bash
# Backend
python run.py

# Frontend (in separate terminal)
cd frontend && npm run dev
```

Access:
- API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## API Endpoints

### News
- `GET /api/news/feed` - Get news feed
- `GET /api/news/search` - Search news
- `GET /api/news/filters` - Get available filters
- `GET /api/news/trending` - Get trending topics
- `POST /api/news/translate` - Translate article
- `WS /api/news/ws` - WebSocket for real-time updates

### TTS
- `POST /api/tts/generate` - Generate audio
- `GET /api/tts/audio/{id}` - Get audio file
- `GET /api/tts/stats` - Get statistics

### Email
- `POST /api/email/send` - Send email
- `POST /api/email/digest` - Send daily digest
- `GET /api/email/status` - Get status

### Telegram
- `POST /api/telegram/post` - Post to Telegram
- `GET /api/telegram/test` - Test connection
- `GET /api/telegram/status` - Get status

### Admin
- `POST /api/db/cleanup` - Cleanup database
- `GET /api/db/stats` - Get statistics
- `POST /api/db/tasks/enqueue` - Enqueue task
- `GET /api/db/tasks/{id}` - Get task status

## Architecture

```
src/trendoscope2/
├── api/              # FastAPI routers
├── core/              # DI, settings, exceptions
├── services/          # Business logic
├── storage/           # Database & repositories
├── ingest/            # News aggregation
├── nlp/               # NLP processing
├── tts/               # Text-to-speech
└── utils/             # Utilities
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/trendoscope2 --cov-report=html

# Specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # E2E tests
```

## Development

### Code Style

- PEP 8 compliance
- Type hints for public APIs
- Docstrings (PEP 257)
- Max line length: 79 characters

### Project Structure

- **Phase 1-4**: Completed (Utilities, Routers, Services, DI)
- **Phase 5**: Pydantic Settings ✅
- **Phase 6**: Structured Error Handling ✅
- **Phase 7**: Repository Pattern ✅
- **Enhancements**: Redis caching, DB optimization, search, WebSocket, task queue, React frontend ✅

## License

MIT
>>>>>>> 92c1d8dedd7c9a7e7a17cffa2df14bb543d7c4bf
