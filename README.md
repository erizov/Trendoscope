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

## License

MIT
