# 🎉 Trendoscope v2.0.0 Release Notes

**Release Date**: November 12, 2025  
**Commit**: 3c9b29e  
**Status**: ✅ Ready to Use

---

## 🚀 What's New in v2.0.0

### 1. 📝 Post Generator in Author's Style
The headline feature! Generate new blog posts in **civil-engineer.livejournal.com** style based on trending news.

**Features:**
- ✅ Learns author's writing style from historical posts
- ✅ Uses trending news as content source
- ✅ 4 generation styles available
- ✅ Persistent storage - works without re-analysis
- ✅ Always-available UI section

**Styles:**
1. 🤔 **Philosophical** - Deep reflections on eternal themes
2. 😏 **Ironic** - Sarcastic observations with sharp commentary  
3. 📊 **Analytical** - Data-driven analysis with conclusions
4. 🔥 **Provocative** - Discussion-provoking content

### 2. 💾 Persistent RAG Storage
No need to re-analyze the blog every time!

**Features:**
- ✅ FAISS vector DB saves to disk automatically
- ✅ Style guide stored in JSON format
- ✅ Auto-loads on server startup
- ✅ Works offline after first analysis

**Files:**
- `data/faiss_index.bin` - Vector embeddings
- `data/faiss_docs.json` - Document storage
- `data/style_guide.json` - Author's style patterns
- `data/posts_metadata.json` - Posts metadata

### 3. 📰 News Aggregation
Automatic news collection from multiple sources.

**Russian Sources:**
- Lenta.ru
- Kommersant
- Vedomosti
- TASS

**International Sources:**
- NY Times
- BBC
- The Guardian

### 4. 🎨 Enhanced UI
- ✅ Post generator section visible from start
- ✅ Style status indicator (ready/not ready)
- ✅ Generate button always active
- ✅ Clear error messages

### 5. 🔧 Technical Improvements

**Robust JSON Parsing:**
- Two-stage parser: JSON → Regex fallback
- Handles LLM output with control characters
- No more "Invalid JSON" errors

**New API Endpoints:**
- `GET /api/style/status` - Check if style guide exists
- `POST /api/post/generate` - Generate post (works with/without analysis)
- `GET /api/post/styles` - List available styles

**Bug Fixes:**
- Fixed JSON schema validation for posts
- Fixed favicon 404 error
- Improved error handling throughout

---

## 📦 Installation & Usage

### Quick Start

```bash
# 1. Install dependencies
cd trendascope
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Start server
python run.py

# 4. Open browser
# http://localhost:8003
```

### First Run

1. **Analyze the blog** (one-time setup):
   - Enter: `https://civil-engineer.livejournal.com`
   - Posts: `39`
   - Click "Анализировать"
   - Wait 2-3 minutes

2. **Generate posts** (anytime after):
   - Scroll to "Генератор постов"
   - Select style
   - Click "Сгенерировать пост"

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Version** | 2.0.0 |
| **Files** | 51 |
| **Lines of Code** | ~7,151 |
| **Modules** | 15+ |
| **API Endpoints** | 10+ |
| **Generation Styles** | 4 (posts) + 6 (summaries) |
| **News Sources** | 7 |
| **Supported Languages** | RU, EN |

---

## 🗂️ Project Structure

```
trendascope/
├── src/
│   ├── trendascope/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── gen/              # LLM generation
│   │   │   ├── post_generator.py  # NEW!
│   │   │   └── llm/          # Provider integrations
│   │   ├── index/            # Vector DB
│   │   │   └── vector_db.py  # FAISS with persistence
│   │   ├── ingest/           # Data collection
│   │   │   ├── livejournal.py
│   │   │   └── news_sources.py  # NEW!
│   │   ├── nlp/              # Text analysis
│   │   │   └── style_analyzer.py
│   │   ├── pipeline/         # Orchestration
│   │   ├── storage/          # Persistent storage (NEW!)
│   │   │   └── style_storage.py
│   │   ├── trends/           # Trend detection
│   │   └── utils/            # Utilities
│   └── frontend/
│       └── index.html        # Web UI
├── data/                     # Persistent data (NEW!)
├── docs/                     # Documentation
├── tests/                    # Tests
├── .env.example              # Config template
├── requirements.txt          # Dependencies
└── run.py                    # Server launcher
```

---

## 🔄 Upgrade from v1.x

If you were using v1.x:

1. **Pull latest code**
2. **Install new dependencies**: `pip install -r requirements.txt`
3. **Run analysis once** to populate storage
4. **Enjoy post generation!**

**Breaking Changes:**
- Server port changed: 8000 → 8003
- New required dependencies: `sentence-transformers`, `faiss-cpu`
- Storage directory: `data/` created automatically

---

## 🐛 Known Issues & Fixes

### Issue: "Ошибка генерации: Missing 'summary' in JSON"
**Fixed in v2.0.0** ✅  
Solution: Proper validation schema for posts

### Issue: "Invalid control character"
**Fixed in v2.0.0** ✅  
Solution: Regex fallback parser

### Issue: Port 8003 in use
**Solution**: Change port in `run.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8004)  # Use any free port
```

---

## 📚 Documentation

- **README.md** - Main documentation
- **QUICKSTART.md** - 5-minute setup guide
- **POST_GENERATOR_GUIDE.md** - Detailed post generation guide
- **CHANGELOG.md** - Version history
- **GIT_SETUP.md** - Git push instructions
- **USAGE_GUIDE.md** - Complete usage guide

---

## 🎯 Roadmap (v2.1+)

### Planned Features
- [ ] More generation styles (humorous, news-style)
- [ ] Manual news topic selection
- [ ] Generated posts history
- [ ] Auto-posting to LiveJournal API
- [ ] Telegram bot integration
- [ ] A/B testing for titles
- [ ] Multi-language support
- [ ] Analytics dashboard

### Under Consideration
- [ ] Fine-tuning on large corpus
- [ ] Integration with VK, Habr
- [ ] Multi-user support
- [ ] Scheduled auto-posting
- [ ] Email notifications

---

## 🙏 Credits

- **OpenAI** for GPT-4
- **ProxyAPI.ru** for Russian API access
- **sentence-transformers** for embeddings
- **FAISS** for vector search
- **civil-engineer.livejournal.com** for the inspiration

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Issues and pull requests welcome!

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit PR

---

## 📞 Support

For issues, questions, or feature requests:
- Check documentation first
- Review CHANGELOG.md
- Search existing issues
- Create new issue with details

---

## 🎉 Thank You!

Thanks for using Trendoscope v2.0.0!

**Now go generate some amazing posts!** 🚀

---

**Version**: 2.0.0  
**Date**: 2025-11-12  
**Commit**: 3c9b29e  
**Status**: Production Ready ✅

