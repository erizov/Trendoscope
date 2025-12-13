# 🔍 Trendoscope v2.2.0

**AI-Powered Content Generation Platform**

Generate viral blog posts in your unique writing style using AI, powered by real-time news aggregation and advanced RAG technology.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys (optional - demo mode works without)
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Run server
python run.py

# 4. Open browser
http://localhost:8003
```

**Windows Users**: Use `start.bat`, `stop.bat`, or `restart.bat` scripts.

---

## ✨ Key Features

### 🎯 Content Generation
- **Post Generator** - Generate posts in author's unique style
- **4 Writing Styles** - Philosophical, Ironic, Analytical, Provocative
- **6 Topic Focuses** - AI, Politics, US Affairs, Russian History, Science, Any
- **Quality Tiers** - Draft (fast/cheap), Standard (balanced), Premium (best)

### 📰 News Integration
- **40+ News Sources** - Russian, US, EU, AI, Politics
- **Real-time Aggregation** - Parallel fetching, 5-10 second load times
- **Controversy Scoring** - AI-powered provocation detection
- **Smart Categorization** - Auto-categorize by topic
- **Category Filtering** - Filter by type (tech, politics, business, etc.)

### 💾 Advanced Storage
- **RAG System** - FAISS vector DB with semantic search
- **Style Learning** - Learn from historical blog posts
- **Post Management** - Save, edit, delete generated posts
- **News Database** - SQLite with full-text search

### 💰 Cost Optimization
- **Auto-fallback** - Uses demo mode if no AI balance
- **Smart Model Selection** - GPT-3.5 for most tasks (20x cheaper)
- **Translation Control** - Skip translation to save costs
- **Cost Tracking** - Real-time cost monitoring
- **80-95% Cost Reduction** - Optimized prompts and caching

### 🛡️ Production Ready
- **Health Checks** - `/health` endpoint with component status
- **Metrics Dashboard** - `/metrics` for monitoring
- **Rate Limiting** - Per-endpoint protection
- **Structured Logging** - JSON logs with request IDs
- **Error Monitoring** - Comprehensive error tracking
- **API Standardization** - Consistent response format

---

## 📚 Documentation

### Quick Guides
- **[QUICKSTART.md](documents/QUICKSTART.md)** - 5-minute setup guide
- **[POST_GENERATOR_GUIDE.md](documents/POST_GENERATOR_GUIDE.md)** - Post generation guide
- **[RAG_STORAGE_GUIDE.md](documents/RAG_STORAGE_GUIDE.md)** - RAG system guide
- **[TOPIC_FOCUS_GUIDE.md](documents/TOPIC_FOCUS_GUIDE.md)** - Topic filtering guide

### Technical Documentation
- **[PROJECT_STRUCTURE.md](documents/PROJECT_STRUCTURE.md)** - Architecture overview
- **[API Reference](http://localhost:8003/docs)** - Interactive API docs
- **[DEPLOYMENT.md](deploy/README.md)** - Deployment guides

---

## 🐳 Deployment

### Docker (Recommended)

```bash
docker-compose up -d
```

### Cloud Platforms

- **Railway** - One-click deploy
- **Render** - Free tier available
- **Fly.io** - Global edge deployment
- **VPS** - Manual deployment guide

See **[deploy/README.md](deploy/README.md)** for details.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_services.py -v

# With coverage
pytest tests/ --cov=src/trendascope
```

---

## 📊 Project Structure

```
trendascope/
├── src/
│   ├── trendascope/          # Main package
│   │   ├── api/              # FastAPI endpoints
│   │   ├── gen/              # Content generation & LLM
│   │   ├── ingest/           # Data collection (RSS, LiveJournal)
│   │   ├── index/            # Vector DB (FAISS)
│   │   ├── nlp/              # Text analysis & style
│   │   ├── services/         # Business logic layer
│   │   ├── storage/          # Persistent storage
│   │   └── utils/            # Utilities (cache, logging, etc.)
│   └── frontend/             # Web UI
├── data/                     # RAG storage & posts
├── documents/                # Documentation
├── deploy/                   # Deployment configs
├── tests/                    # Test suite
└── requirements.txt          # Dependencies
```

---

## 🎨 Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Vector DB**: FAISS (384d embeddings)
- **LLM**: OpenAI GPT-3.5/4, Anthropic Claude, Demo mode
- **Frontend**: Vanilla JS, Modern CSS
- **Storage**: SQLite, FAISS, JSON
- **Caching**: Redis (optional, in-memory fallback)
- **Testing**: Pytest, MCP Browser

---

## 🔧 API Endpoints

### Content Generation
- `POST /api/post/generate` - Generate post
- `GET /api/post/styles` - Available styles
- `GET /api/style/status` - Style guide status

### News Feed
- `GET /api/news/feed` - Get news feed
- `GET /api/news/search` - Search news
- `GET /api/news/db/stats` - Database statistics

### Post Management
- `POST /api/posts/save` - Save post
- `GET /api/posts/list` - List saved posts
- `GET /api/posts/{id}` - Get post
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

### System
- `GET /health` - Health check
- `GET /metrics` - Application metrics
- `GET /api/balance/check` - Check AI provider balance

**Full API Docs**: http://localhost:8003/docs

---

## 💡 Usage Examples

### Generate Post (API)

```bash
curl -X POST "http://localhost:8003/api/post/generate?style=philosophical&topic=ai&quality=standard"
```

### Generate Post (Web UI)

1. Open http://localhost:8003/static/posts_generator.html
2. Select style, topic, provider
3. Click "Сгенерировать пост"
4. View and save generated posts

### News Feed

1. Open http://localhost:8003/static/news_feed_full.html
2. Filter by category
3. Click news cards to read full articles
4. Share to social media

---

## 📈 Status

- **Version**: 2.2.0
- **Status**: ✅ Production Ready
- **RAG Posts**: 118+ (93.3 MB)
- **Test Coverage**: 80%+
- **Cost Reduction**: 80-95% vs baseline

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Credits

- OpenAI for GPT models
- FAISS for vector search
- FastAPI for the framework
- All news sources for RSS feeds

---

## 📞 Support

- **Documentation**: `/documents` folder
- **API Docs**: http://localhost:8003/docs
- **Issues**: GitHub Issues
- **Deployment**: `/deploy/README.md`

---

**Ready to generate viral content!** 🚀

**Last Updated**: 2025-01-XX  
**Version**: 2.2.0
