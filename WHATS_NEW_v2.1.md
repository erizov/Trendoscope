# 🚀 What's New in Trendoscope v2.1

**Release Date**: 2025-11-29  
**Major Update**: Full News Feed with Real API Integration

---

## 🎉 New Features

### **1. Full-Featured News Feed** ✨

**File**: `src/frontend/news_feed_full.html`  
**URL**: http://localhost:8003/static/news_feed_full.html

A complete, production-ready news aggregation interface with:

- ✅ **40+ Real News Sources** via RSS feeds
- ✅ **Modal Windows** for full-text reading
- ✅ **Controversy Scoring** (0-100% provocation meter)
- ✅ **Category Filtering** (AI, Politics, US, EU, Russia)
- ✅ **Smart Translation** (English → Russian with LLM)
- ✅ **Dark Theme** (Twitter/X-style design)
- ✅ **Mobile Responsive** (touch-friendly)
- ✅ **Share Functionality** (native share + clipboard)
- ✅ **Real-time Updates** (floating refresh button)

### **2. Controversy Scoring Algorithm** 🔥

**File**: `src/trendascope/nlp/controversy_scorer.py`

Multi-factor algorithm that scores news provocation level:

**Scoring Factors**:
1. **Keywords (30%)**: война, санкции, трамп, байден, скандал, заменит, угроза
2. **Patterns (25%)**: Questions, CAPS, vs/against, contrasts
3. **Questions (20%)**: Provocative question usage
4. **Emotion (15%)**: шок, ужас, сенсация, катастрофа
5. **Length (10%)**: Shorter = more provocative

**Labels**:
- 💥 **Explosive** (75-100%): Extremely provocative
- 🔥 **Hot** (60-74%): Very provocative
- 🌶️ **Spicy** (40-59%): Interesting/engaging
- 📰 **Mild** (0-39%): Neutral news

**Usage**:
```python
from trendascope.nlp.controversy_scorer import ControversyScorer

scorer = ControversyScorer()
news = {'title': 'Трамп vs Байден?', 'summary': '...'}
result = scorer.score_news(news)
print(result['controversy']['score'])  # 85
```

### **3. Enhanced News Aggregation** 📰

**File**: `src/trendascope/ingest/news_sources.py`

**Added 20+ New Sources**:

**Russian**:
- Roem.ru (tech)
- РИА Новости (general)
- Интерфакс (general)

**US**:
- NY Times Politics RSS
- Washington Post Politics
- NPR News

**EU**:
- Euronews
- Politico Europe
- Deutsche Welle

**AI**:
- DeepLearning.AI
- ML Mastery

**Politics**:
- Brookings Institute

**Total**: 40+ sources across 6 categories

### **4. REST API Endpoint** 🌐

**File**: `src/trendascope/api/main.py`

**New Endpoint**: `GET /api/news/feed`

**Parameters**:
- `category`: all|ai|politics|us|eu|russia (default: all)
- `limit`: 5-100 (default: 20)
- `translate`: true|false (default: true)

**Response**:
```json
{
  "success": true,
  "count": 20,
  "category": "ai",
  "news": [
    {
      "title": "GPT-5 Released",
      "summary": "...",
      "source": "OpenAI Blog",
      "link": "https://...",
      "published": "2025-11-29T10:00:00Z",
      "category": "ai",
      "controversy": {
        "score": 85,
        "label": "hot",
        "emoji": "🔥",
        "breakdown": {...}
      },
      "is_hot": true
    }
  ]
}
```

**Example**:
```bash
curl "http://localhost:8003/api/news/feed?category=ai&limit=10"
```

### **5. Smart Translation Module** 🌍

**File**: `src/trendascope/nlp/translator.py`

**Features**:
- Automatic language detection (Cyrillic % threshold)
- Batch translation (5 items at a time)
- Context preservation with LLM
- Graceful fallback if translation fails
- Maintains emotional tone and provocation level

**Usage**:
```python
from trendascope.nlp.translator import translate_and_summarize_news

news = [{'title': 'GPT-5 Released', 'summary': '...'}]
translated = translate_and_summarize_news(news, provider="openai")
# Result: [{'title': 'GPT-5 выпущен', 'summary': '...', 'translated': True}]
```

---

## 📁 New Files

### **Core Components**

1. **`src/trendascope/nlp/controversy_scorer.py`** (220 lines)
   - Controversy scoring algorithm
   - Multi-factor analysis
   - Label assignment

2. **`src/frontend/news_feed_full.html`** (600+ lines)
   - Full-featured UI with modals
   - Real API integration
   - Mobile responsive

### **Documentation**

3. **`NEWS_FEED_FULL_README.md`** (800+ lines)
   - Complete documentation
   - API reference
   - Usage examples
   - Troubleshooting

4. **`START_NEWS_FEED.md`** (200+ lines)
   - Quick start guide
   - Configuration tips
   - FAQ

5. **`NEWS_PRESENTATION_CONCEPTS.md`** (from previous update)
   - 8 presentation formats
   - Strategy recommendations

6. **`QUICK_NEWS_FORMATS.txt`** (from previous update)
   - Visual ASCII art comparisons

7. **`WHATS_NEW_v2.1.md`** (this file)
   - Version summary

### **Testing**

8. **`test_news_feed.py`** (300+ lines)
   - Automated test suite
   - Component verification
   - API testing

---

## 🔄 Modified Files

### **Enhanced Files**

1. **`src/trendascope/ingest/news_sources.py`**
   - Added 20+ new RSS sources
   - Added US_SOURCES and EUROPEAN_SOURCES
   - Enhanced source name extraction
   - Updated fetch_trending_topics parameters

2. **`src/trendascope/api/main.py`**
   - Added `/api/news/feed` endpoint
   - Added `_categorize_news()` helper
   - Integrated ControversyScorer
   - Integrated Translator

3. **`src/trendascope/nlp/translator.py`**
   - Already complete from previous update
   - Batch translation support
   - Context preservation

---

## 🎯 Use Cases

### **1. Browse Provocative News**

```
1. Start server: python run.py
2. Open: http://localhost:8003/static/news_feed_full.html
3. Click categories to filter
4. Click cards to read full text
5. Share interesting news
```

### **2. API Integration**

```python
import requests

response = requests.get(
    'http://localhost:8003/api/news/feed',
    params={'category': 'ai', 'limit': 10}
)

news = response.json()['news']
for item in news:
    if item['controversy']['score'] >= 70:
        print(f"🔥 {item['title']}")
```

### **3. Score Custom News**

```python
from trendascope.nlp.controversy_scorer import ControversyScorer

scorer = ControversyScorer()

my_news = {
    'title': 'Your provocative title?',
    'summary': 'Your controversial content...'
}

result = scorer.score_news(my_news)
print(f"Provocation: {result['controversy']['score']}%")
```

### **4. Fetch from Specific Sources**

```python
from trendascope.ingest.news_sources import NewsAggregator

agg = NewsAggregator()

# Only AI news
ai_news = agg.fetch_trending_topics(
    include_ai=True,
    include_politics=False,
    include_russian=False,
    max_per_source=10
)

print(f"Found {len(ai_news)} AI articles")
```

---

## 📊 Statistics

### **Code Added**

- **Python**: ~800 lines
- **HTML/CSS/JS**: ~600 lines
- **Documentation**: ~2,000 lines
- **Total**: ~3,400 lines

### **Features**

- **New Modules**: 1 (controversy_scorer)
- **New Endpoints**: 1 (/api/news/feed)
- **New Pages**: 1 (news_feed_full.html)
- **New Sources**: 20+ RSS feeds
- **Total Sources**: 40+

### **Test Coverage**

- ✅ News aggregation
- ✅ Controversy scoring
- ✅ Categorization
- ✅ API endpoint (optional)

---

## 🚀 Getting Started

### **Quick Start (30 seconds)**

```bash
# 1. Start server
cd trendascope
python run.py

# 2. Open browser
# http://localhost:8003/static/news_feed_full.html

# 3. Done! Browse news with controversy scoring
```

### **Run Tests**

```bash
# Test all components
python test_news_feed.py

# Expected output:
# ✅ PASS  Aggregation
# ✅ PASS  Scoring
# ✅ PASS  Categorization
# ⚠️  SKIP  API (if server not running)
```

### **Manual API Test**

```bash
# Test endpoint
curl "http://localhost:8003/api/news/feed?category=all&limit=5"

# Expected: JSON with news array and controversy scores
```

---

## 📚 Documentation

### **For Users**

- **Quick Start**: `START_NEWS_FEED.md`
- **Full Guide**: `NEWS_FEED_FULL_README.md`
- **Concepts**: `NEWS_PRESENTATION_CONCEPTS.md`

### **For Developers**

- **API Reference**: See `NEWS_FEED_FULL_README.md` → API Reference section
- **Algorithm Details**: See `controversy_scorer.py` docstrings
- **Testing**: See `test_news_feed.py`

---

## 🔧 Configuration

### **Adjust Controversy Threshold**

Edit `src/trendascope/nlp/controversy_scorer.py`:

```python
# Line ~70: Make more news "hot"
if total_score >= 50:  # was 60
    label = 'hot'
    emoji = '🔥'
```

### **Add More Keywords**

```python
# Line ~25-40: Add to CONTROVERSIAL_KEYWORDS
CONTROVERSIAL_KEYWORDS = {
    'your_keyword': 3,  # weight 1-3
    ...
}
```

### **Add News Sources**

Edit `src/trendascope/ingest/news_sources.py`:

```python
# Add to appropriate list
US_SOURCES = [
    "https://existing-source.com/rss",
    "https://your-new-source.com/rss",  # add here
]
```

---

## 🐛 Known Issues & Limitations

### **1. Translation Requires OpenAI**

- **Issue**: Translation needs OpenAI API key
- **Workaround**: Use `translate=false` parameter
- **Fix**: Set OPENAI_API_KEY in .env

### **2. Some RSS Feeds May Be Slow**

- **Issue**: 40+ feeds can take 2-5 seconds
- **Workaround**: Reduce max_per_source or use fewer sources
- **Fix**: Implement caching (5-minute TTL)

### **3. Controversy Scoring is Heuristic**

- **Issue**: Not perfect semantic understanding
- **Workaround**: Adjust weights/keywords for your use case
- **Future**: Use ML model for semantic controversy detection

---

## 🗓️ Roadmap

### **v2.2 (Next)**

- [ ] User accounts (save favorites)
- [ ] Comments system
- [ ] Sharing analytics
- [ ] Email notifications

### **v2.3 (Future)**

- [ ] Mobile app (React Native)
- [ ] Telegram bot
- [ ] AI-generated summaries
- [ ] Multi-language support

### **v3.0 (Vision)**

- [ ] ML-based controversy scoring
- [ ] Personalized feeds
- [ ] Real-time updates (WebSockets)
- [ ] Analytics dashboard

---

## 💬 Feedback

Found a bug? Have a suggestion?

- **Issues**: Create GitHub issue
- **Questions**: Check documentation first
- **Contributing**: Pull requests welcome!

---

## 🏆 Summary

### **What You Get**

✅ **40+ news sources** from Russia, US, EU  
✅ **Intelligent controversy scoring** (0-100%)  
✅ **Beautiful dark-themed UI** (Twitter/X style)  
✅ **Modal windows** for full-text reading  
✅ **Category filtering** (6 categories)  
✅ **Smart translation** (English → Russian)  
✅ **REST API** for integration  
✅ **Mobile responsive** design  
✅ **Share functionality** (native + clipboard)  
✅ **Automated tests** for reliability  

### **Ready to Use**

```
URL: http://localhost:8003/static/news_feed_full.html
Time to setup: 30 seconds
Difficulty: Easy
```

### **Perfect For**

- 📰 Reading provocative news aggregated from many sources
- 🔥 Finding hottest/most controversial topics
- 🌐 Integrating news feed into your app via API
- 📱 Mobile news browsing with modern UX
- 🤖 Building AI-powered news analysis tools

---

## 🎉 Get Started Now!

```bash
cd trendascope
python run.py
```

Then open: **http://localhost:8003/static/news_feed_full.html**

**Enjoy your provocative news feed!** 🚀🔥

---

**Version**: 2.1.0  
**Release Date**: 2025-11-29  
**Status**: ✅ Production Ready  
**Authors**: Trendoscope Team  
**License**: MIT

