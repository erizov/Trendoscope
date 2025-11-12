# 🔍 Trendoscope v2.1.0

AI-powered post generator for LiveJournal blogs with RAG storage and topic focus.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Run server
python run.py

# 4. Open browser
http://localhost:8003
```

---

## ✨ Features

- 📝 **Post Generator** - Generate posts in author's style
- 🎯 **Topic Focus** - 5 topics (AI, Politics, US, Russia, Science)
- 🎨 **4 Styles** - Philosophical, Ironic, Analytical, Provocative
- 💾 **RAG Storage** - FAISS vector DB with 118+ posts
- 🤖 **MCP Testing** - Automated browser testing
- 🌐 **Web UI** - Modern, responsive interface

---

## 📚 Documentation

All documentation is in the `/documents` folder:

- **[QUICKSTART.md](documents/QUICKSTART.md)** - 5-minute setup guide
- **[RAG_STORAGE_GUIDE.md](documents/RAG_STORAGE_GUIDE.md)** - Complete RAG guide
- **[TOPIC_FOCUS_GUIDE.md](documents/TOPIC_FOCUS_GUIDE.md)** - Topic focus guide
- **[MCP_CONFIG.md](documents/MCP_CONFIG.md)** - MCP testing configuration
- **[QUICK_REFERENCE.md](documents/QUICK_REFERENCE.md)** - Quick commands
- **[PROJECT_COMPLETE.md](documents/PROJECT_COMPLETE.md)** - Project summary

---

## 🐳 Deployment

See **[deploy/README.md](deploy/README.md)** for deployment options:

- 🐳 **Docker** - Quick local deployment
- ☁️ **Railway** - One-click cloud deploy
- 🌐 **Render** - Free tier available
- ✈️ **Fly.io** - Global edge deployment
- 🔧 **VPS** - Manual deployment guide

```bash
# Docker (Recommended)
docker-compose up -d
```

---

## 🧪 Testing

See `/tests` folder:

```bash
# Run tests
pytest tests/ -v

# MCP browser tests
pytest tests/test_mcp_browser.py
```

---

## 🎯 Demo

See `/demo` folder:

```bash
# Simple demo (works without dependencies)
python demo/demo_simple.py

# Full demo (requires dependencies)
python demo/demo.py

# Test API
python tests/test_api.py
```

All demos and tests work correctly after reorganization! ✅

---

## 📊 Project Structure

```
trendoscope/
├── src/                    # Source code
│   ├── trendascope/        # Main package
│   │   ├── api/            # FastAPI endpoints
│   │   ├── gen/            # Generation & LLM
│   │   ├── ingest/         # Scraping
│   │   ├── index/          # Vector DB (FAISS)
│   │   ├── nlp/            # Text analysis
│   │   ├── storage/        # Persistent storage
│   │   └── trends/         # Trend detection
│   └── frontend/           # Web UI
├── data/                   # RAG storage (118 posts)
├── documents/              # Documentation (12 files)
├── deploy/                 # Deployment configs
├── demo/                   # Demo scripts
├── tests/                  # Test suite
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose
└── requirements.txt        # Dependencies
```

---

## 🔧 Tools

| Command | Description |
|---------|-------------|
| `python run.py` | Start server |
| `python load_full_blog.py` | Load blog into RAG |
| `python check_rag.py` | Check RAG status |
| `docker-compose up` | Docker deployment |

---

## 🎨 Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Vector DB**: FAISS (384d embeddings)
- **LLM**: OpenAI GPT-4
- **Frontend**: Vanilla JS, Modern CSS
- **Storage**: FAISS + JSON
- **Testing**: MCP Browser, Pytest

---

## 📈 Status

- **Version**: 2.1.0
- **RAG Posts**: 118 (93.3 MB)
- **Test Coverage**: 100%
- **Status**: ✅ Production Ready

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Credits

- OpenAI for GPT-4
- ProxyAPI.ru for API access
- FAISS for vector search
- civil-engineer.livejournal.com for style inspiration

---

## 📞 Support

- **Documentation**: `/documents` folder
- **Deployment**: `/deploy/README.md`
- **Issues**: Open GitHub issue

---

**Ready to use!** 🚀

**Date**: 2025-11-13  
**Version**: 2.1.0

