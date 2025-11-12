# 📁 Project Structure - Trendoscope v2.1.0

Complete overview of the project organization.

---

## 📂 Directory Structure

```
trendoscope/
│
├── 📚 documents/              # All documentation (13 files)
│   ├── QUICKSTART.md          # 5-minute setup guide
│   ├── RAG_STORAGE_GUIDE.md   # Complete RAG guide
│   ├── TOPIC_FOCUS_GUIDE.md   # Topic focus feature
│   ├── MCP_CONFIG.md          # MCP browser testing
│   ├── PROJECT_COMPLETE.md    # Project summary
│   ├── PROJECT_STRUCTURE.md   # This file
│   ├── USAGE_GUIDE.md         # Complete usage guide
│   ├── POST_GENERATOR_GUIDE.md # Post generation guide
│   ├── CHANGELOG.md           # Version history
│   ├── GIT_SETUP.md           # Git configuration
│   ├── QUICK_REFERENCE.md     # Command cheat sheet
│   ├── ANSWER_HOW_RAG_KEEPS_DATA.md # RAG internals
│   └── CURRENT_RAG_STATUS.md  # RAG status report
│
├── 🎯 demo/                   # Demo scripts (2 files)
│   ├── demo.py                # Full demo with all features
│   └── demo_simple.py         # Simple demo without dependencies
│
├── 🧪 tests/                  # Test suite
│   ├── test_api.py            # API testing script
│   ├── test_pipeline.py       # Pipeline tests (if exists)
│   └── __init__.py
│
├── 🚀 deploy/                 # Deployment configurations (6 files)
│   ├── README.md              # Complete deployment guide
│   ├── railway.json           # Railway platform config
│   ├── render.yaml            # Render platform config
│   ├── fly.toml               # Fly.io platform config
│   ├── trendoscope.service    # Systemd service file
│   └── nginx.conf             # Nginx reverse proxy config
│
├── 💻 src/                    # Source code
│   ├── frontend/              # Web UI
│   │   └── index.html         # Main web interface
│   │
│   └── trendascope/           # Python package
│       ├── __init__.py
│       │
│       ├── api/               # FastAPI endpoints
│       │   ├── __init__.py
│       │   └── main.py        # API routes
│       │
│       ├── gen/               # Content generation
│       │   ├── __init__.py
│       │   ├── generate.py    # Main generation logic
│       │   ├── parser.py      # JSON parser
│       │   ├── post_generator.py # Post generation
│       │   ├── prompts.json   # LLM prompts
│       │   ├── rag_facts.py   # Fact checking
│       │   └── llm/           # LLM providers
│       │       ├── __init__.py
│       │       └── providers.py # OpenAI, Anthropic, etc.
│       │
│       ├── index/             # Vector database
│       │   ├── __init__.py
│       │   ├── vector_db.py   # FAISS implementation
│       │   └── search_stub.py # Search stub
│       │
│       ├── ingest/            # Data ingestion
│       │   ├── __init__.py
│       │   ├── livejournal.py # LiveJournal scraper
│       │   └── news_sources.py # News aggregator
│       │
│       ├── nlp/               # NLP processing
│       │   ├── __init__.py
│       │   ├── analyzer.py    # Text analysis
│       │   └── style_analyzer.py # Style extraction
│       │
│       ├── pipeline/          # Orchestration
│       │   ├── __init__.py
│       │   └── orchestrator.py # Pipeline coordinator
│       │
│       ├── storage/           # Persistent storage
│       │   ├── __init__.py
│       │   └── style_storage.py # Style guide storage
│       │
│       ├── trends/            # Trend detection
│       │   ├── __init__.py
│       │   └── engine.py      # Trend engine
│       │
│       ├── utils/             # Utilities
│       │   ├── __init__.py
│       │   └── cache.py       # Caching utilities
│       │
│       └── config.py          # Configuration loader
│
├── 💾 data/                   # RAG storage (gitignored except structure)
│   ├── faiss_index.bin        # FAISS vector index (93+ MB)
│   ├── faiss_docs.json        # Document metadata (118 posts)
│   ├── style_guide.json       # Analyzed style data
│   └── posts_metadata.json    # Post metadata
│
├── 🐳 Docker files
│   ├── Dockerfile             # Docker image definition
│   ├── docker-compose.yml     # Docker Compose orchestration
│   └── .dockerignore          # Docker build exclusions
│
├── 📝 Root files
│   ├── README.md              # Main readme
│   ├── DEPLOY_QUICK.md        # Quick deployment guide
│   ├── DEPLOYMENT_SUMMARY.txt # Complete deployment overview
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Server start script
│   ├── pytest.ini             # Pytest configuration
│   ├── VERSION.txt            # Version number
│   ├── .env.example           # Environment template
│   ├── .env                   # Environment variables (gitignored)
│   ├── .gitignore             # Git exclusions
│   ├── start_web.bat          # Windows launcher (web UI)
│   ├── start_demo.bat         # Windows launcher (demo)
│   ├── check_rag.py           # RAG status checker
│   ├── load_full_blog.py      # Blog loader script
│   └── HOW_RAG_WORKS.txt      # RAG explanation (plain text)
│
└── 📊 Generated files (not in repo)
    └── demo_results.json      # Demo output

```

---

## 🗂️ File Organization Logic

### Why This Structure?

1. **`documents/`** - All markdown documentation in one place
   - Easy to find
   - Clean root directory
   - Logical grouping

2. **`demo/`** - Demo scripts separated from main code
   - Clear examples
   - Won't clutter root
   - Easy to run

3. **`tests/`** - Test files in standard location
   - Follows Python conventions
   - Easy for test runners to find
   - Separated from source

4. **`deploy/`** - Deployment configs grouped
   - All deployment options in one place
   - Clear separation of concerns
   - Production-ready configs

5. **`src/`** - Source code remains unchanged
   - Standard Python package structure
   - Imports still work
   - No breaking changes

6. **`data/`** - Persistent storage
   - RAG vector database
   - Style guides
   - Cached data

---

## 📄 Key Files

### Root Level

| File | Purpose | Use Case |
|------|---------|----------|
| `README.md` | Main project overview | First file to read |
| `DEPLOY_QUICK.md` | Quick deployment guide | Deploy in 3 minutes |
| `DEPLOYMENT_SUMMARY.txt` | Complete deployment overview | Choose platform |
| `requirements.txt` | Python dependencies | `pip install -r requirements.txt` |
| `run.py` | Start web server | `python run.py` |
| `docker-compose.yml` | Docker deployment | `docker-compose up -d` |
| `Dockerfile` | Docker image | Production builds |

### Documentation (`documents/`)

| File | Purpose | Reader |
|------|---------|--------|
| `QUICKSTART.md` | 5-minute setup | New users |
| `USAGE_GUIDE.md` | Complete usage guide | All users |
| `RAG_STORAGE_GUIDE.md` | RAG internals | Advanced users |
| `TOPIC_FOCUS_GUIDE.md` | Topic filtering | Content creators |
| `MCP_CONFIG.md` | Browser testing | Developers |
| `PROJECT_COMPLETE.md` | Project summary | Everyone |

### Deployment (`deploy/`)

| File | Purpose | Platform |
|------|---------|----------|
| `README.md` | Deployment guide | All platforms |
| `railway.json` | Railway config | Railway |
| `render.yaml` | Render config | Render |
| `fly.toml` | Fly.io config | Fly.io |
| `trendoscope.service` | Systemd service | VPS/Linux |
| `nginx.conf` | Reverse proxy | VPS/Linux |

### Demos (`demo/`)

| File | Purpose | Dependencies |
|------|---------|--------------|
| `demo_simple.py` | Basic demo | None (works always) |
| `demo.py` | Full demo | All requirements |

### Tests (`tests/`)

| File | Purpose | Use |
|------|---------|-----|
| `test_api.py` | API testing | `python tests/test_api.py` |
| `test_pipeline.py` | Pipeline tests | `pytest tests/` |

---

## 🔄 Migration Notes

### Path Updates Made

All scripts updated to work with new structure:

1. **`demo/demo.py`**
   - ✅ Path updated: `../ parent / src`
   - ✅ UTF-8 encoding added
   - ✅ Imports fixed

2. **`demo/demo_simple.py`**
   - ✅ Path updated: `../ parent / src`
   - ✅ UTF-8 encoding (already had)
   - ✅ Works without dependencies

3. **`tests/test_api.py`**
   - ✅ Path updated: `../ parent / src`
   - ✅ UTF-8 encoding added
   - ✅ Works correctly

### No Breaking Changes

- ✅ Web UI still works: `python run.py`
- ✅ Docker still works: `docker-compose up`
- ✅ All imports unchanged in `src/`
- ✅ All demos and tests verified

---

## 📊 Statistics

| Category | Count | Size |
|----------|-------|------|
| Total Files | 60+ | - |
| Documentation | 13 | ~200 KB |
| Source Files | 30+ | ~500 KB |
| Demo Scripts | 2 | ~50 KB |
| Test Files | 2+ | ~20 KB |
| Deployment Configs | 6 | ~30 KB |
| RAG Data | 118 posts | 93.3 MB |

---

## 🚀 Quick Commands

### Run Application

```bash
# Web UI
python run.py

# Demo (full)
python demo/demo.py

# Demo (simple, no dependencies)
python demo/demo_simple.py

# Check RAG status
python check_rag.py

# Load full blog into RAG
python load_full_blog.py
```

### Testing

```bash
# Test API
python tests/test_api.py

# Run all tests
pytest tests/ -v
```

### Deployment

```bash
# Docker (local)
docker-compose up -d

# Fly.io (cloud)
fly launch && fly deploy

# Railway (cloud)
railway up
```

---

## 📚 Documentation Index

For quick access to specific topics:

- **Getting Started**: `documents/QUICKSTART.md`
- **Usage Guide**: `documents/USAGE_GUIDE.md`
- **RAG Storage**: `documents/RAG_STORAGE_GUIDE.md`
- **Post Generation**: `documents/POST_GENERATOR_GUIDE.md`
- **Topic Focus**: `documents/TOPIC_FOCUS_GUIDE.md`
- **Deployment**: `deploy/README.md`
- **MCP Testing**: `documents/MCP_CONFIG.md`
- **Project Summary**: `documents/PROJECT_COMPLETE.md`

---

## ✅ Organization Benefits

### Before Reorganization
```
trendascope/
├── 20+ .md files in root
├── demo.py (root)
├── test_api.py (root)
└── ... cluttered root
```

### After Reorganization
```
trendascope/
├── documents/    📚 All docs
├── demo/         🎯 All demos
├── tests/        🧪 All tests
├── deploy/       🚀 All configs
└── Clean root!   ✨
```

**Result**: 
- ✅ Clean root directory
- ✅ Logical grouping
- ✅ Easy navigation
- ✅ Professional structure
- ✅ No breaking changes

---

**Status**: ✅ Production Ready  
**Version**: 2.1.0  
**Date**: 2025-11-13

All files organized, documented, and tested! 🎉

