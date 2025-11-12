# Changelog

## [2.1.0] - 2025-11-12

### 🎯 New Feature: Topic Focus

#### Topic-Focused Post Generation
- **5 topic areas**: AI, Politics, US Affairs, Russian History, Science
- **Smart filtering**: Automatic news filtering by keywords (RU + EN)
- **LLM guidance**: Topic-specific instructions in prompts
- **Fallback**: Uses all news if no topic matches

#### Topics Available
1. 🤖 **Искусственный интеллект (AI)**
   - Machine learning, neural networks, algorithms
2. 🏛️ **Политика и международные отношения**
   - Geopolitics, government, diplomacy
3. 🇺🇸 **США и американская политика**
   - American politics, Washington, White House
4. 🇷🇺 **Российская история**
   - USSR, historical parallels, Russian events
5. 🔬 **Наука и технологии**
   - Research, discoveries, space, physics

#### UI Improvements
- New dropdown "Тема поста" with 6 options
- Emoji indicators for topics
- Better UX and visual hierarchy

#### Technical Implementation
- `TOPIC_DEFINITIONS` dictionary with keywords and instructions
- `_filter_news_by_topic()` - smart filtering helper
- `_get_topic_instruction()` - instruction builder
- Topic parameter throughout the stack (UI → API → Generator)

### 📚 Documentation
- `TOPIC_FOCUS_GUIDE.md` - Complete guide with examples
- `GIT_SETUP.md` - Git push instructions
- `RELEASE_NOTES_v2.0.0.md` - v2.0 release notes

### 🔧 Bug Fixes
- Improved JSON parsing robustness
- Fixed control character issues
- Better error messages

---

## [2.0.0] - 2025-11-12

### 🎉 Major Features

#### Post Generator with Author's Style
- **Generate posts in civil-engineer.livejournal.com style** based on trending news
- 4 generation styles: Philosophical, Ironic, Analytical, Provocative
- Automatic news aggregation from Russian and international sources
- RAG-based style learning from author's posts

#### Persistent Storage
- **FAISS Vector DB persistence** - saves to disk automatically
- **Style guide storage** - remembers author's writing patterns
- **Automatic loading** on startup - no need to re-analyze
- Posts available immediately after first analysis

#### Always-Available UI
- **Post generator section visible from start**
- **Status indicator** shows if style guide is ready
- **Generate button always active** - uses stored data
- Smart error messages if style guide missing

### 🔧 Technical Improvements

#### Storage System
- `storage/style_storage.py` - Style guide persistence
- `index/vector_db.py` - FAISS with disk persistence
- Auto-save after analysis
- Auto-load on startup

#### News Aggregation
- `ingest/news_sources.py` - Multi-source news aggregator
- Russian sources: Lenta.ru, Kommersant, Vedomosti, TASS
- International sources: NY Times, BBC, The Guardian
- Topic extraction from news

#### API Endpoints
- `GET /api/style/status` - Check if style guide exists
- `POST /api/post/generate` - Generate post (works with/without current analysis)
- `GET /api/post/styles` - List available styles

#### Bug Fixes
- Fixed JSON parsing for post generation (was using wrong schema)
- Fixed favicon 404 error
- Improved error handling

### 📚 Documentation
- `POST_GENERATOR_GUIDE.md` - Complete guide for post generation
- `WHATS_NEW.md` - Summary of new features
- Updated `README.md` with new capabilities
- This `CHANGELOG.md`

### 🗂️ File Structure Changes
```
+ src/trendascope/storage/          # Persistent storage
+ src/trendascope/ingest/news_sources.py  # News aggregator
+ data/                              # Persistent data directory
  + faiss_index.bin                  # Vector index
  + faiss_docs.json                  # Document storage
  + style_guide.json                 # Author's style
  + posts_metadata.json              # Posts metadata
```

### 🔄 Migration Notes
- First run will show "Style guide not found"
- Run analysis once to populate storage
- Subsequent runs will use saved data
- Can generate posts immediately after first analysis

---

## [1.0.0] - 2025-11-10

### Initial Release

#### Core Features
- LiveJournal scraper (RSS + HTML)
- NLP analysis (keywords, sentiment, entities)
- Style analyzer
- Vector DB (FAISS/Qdrant)
- Trend engine
- LLM content generation (6 modes)
- Viral potential scoring
- Web UI

#### Supported LLM Providers
- OpenAI (with ProxyAPI support)
- Anthropic
- Local (Ollama)
- Demo mode

#### Infrastructure
- FastAPI backend
- React-free vanilla JS frontend
- Optional Redis caching
- PostgreSQL support

