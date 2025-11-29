# 🚀 Quick Start: News Feed

**Time to setup**: 30 seconds  
**Difficulty**: Easy  

---

## Step 1: Start Server

```bash
cd trendascope
python run.py
```

Wait for:
```
INFO:     Uvicorn running on http://localhost:8003
```

---

## Step 2: Open News Feed

Click or copy:

**Full Version** (recommended):
```
http://localhost:8003/static/news_feed_full.html
```

**Demo Version** (simple):
```
http://localhost:8003/static/news_feed.html
```

---

## Step 3: Use the Feed

### **Filter News**
- Click category buttons: 🌍 Все | 🤖 ИИ | 🏛️ Политика | 🇺🇸 США | 🇪🇺 ЕС | 🇷🇺 Россия

### **Read Full News**
- Click any news card
- Modal window opens with full text
- Click [×] or press ESC to close

### **Share News**
- Click 📤 Share button
- On mobile: native share dialog
- On desktop: copies to clipboard

### **Refresh**
- Click floating 🔄 button (bottom-right)
- Fetches fresh news from 40+ sources

---

## 🎯 What You'll See

### **News Sources** (40+)

**Russian**:
- Lenta.ru, Коммерсантъ, Ведомости, ТАСС
- Habr, VC.ru, Roem.ru
- Meduza, РИА Новости, Интерфакс

**US**:
- NY Times, Washington Post, NPR
- Politico, TechCrunch

**EU**:
- Euronews, Politico Europe
- Deutsche Welle

**AI**:
- MIT Tech Review, OpenAI Blog
- DeepLearning.AI, AI News

**Politics**:
- Foreign Policy, Foreign Affairs
- Brookings Institute

### **Controversy Scores**

- **💥 Explosive**: 75-100% (very provocative)
- **🔥 Hot**: 60-74% (provocative)
- **🌶️ Spicy**: 40-59% (interesting)
- **📰 Mild**: 0-39% (neutral)

---

## 🧪 Test API Manually

```bash
# Get all news
curl "http://localhost:8003/api/news/feed?category=all&limit=5"

# Get AI news only
curl "http://localhost:8003/api/news/feed?category=ai&limit=10"

# Get hot political news
curl "http://localhost:8003/api/news/feed?category=politics&limit=20"
```

---

## 📱 Mobile Test

1. Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Open on phone: `http://YOUR_IP:8003/static/news_feed_full.html`
3. Test touch gestures, share functionality

---

## ⚙️ Configuration

### **Disable Translation** (faster)

Add `?translate=false` to URL:
```
http://localhost:8003/static/news_feed_full.html?translate=false
```

Or edit JavaScript:
```javascript
// Line ~180 in news_feed_full.html
const response = await fetch(
    `${API_URL}/api/news/feed?category=${category}&limit=30&translate=false`
);
```

### **Adjust Controversy Threshold**

Edit `src/trendascope/nlp/controversy_scorer.py`:
```python
# Show more as "hot"
if total_score >= 50:  # was 60
    label = 'hot'
```

### **Add More Sources**

Edit `src/trendascope/ingest/news_sources.py`:
```python
RUSSIAN_TECH_SOURCES = [
    "https://habr.com/ru/rss/best/",
    "https://your-source.com/rss",  # add here
]
```

---

## ❓ FAQ

### **Q: Why is it loading slowly?**

A: First load fetches from 40+ RSS feeds. Subsequent loads are faster (cached).

**Solution**: Add `&limit=10` to fetch fewer items.

### **Q: Why am I seeing English news?**

A: Translation is optional. Set `translate=true` to enable (requires OpenAI key).

**Solution**: Use demo mode or add API key in `.env`.

### **Q: Can I use without internet?**

A: No, news feeds require internet connection.

**Solution**: Use cached data or create offline mode.

### **Q: How often are news updated?**

A: RSS feeds cached for 5 minutes. Click refresh for fresh news.

---

## 🎉 You're Ready!

Open: **http://localhost:8003/static/news_feed_full.html**

Enjoy your provocative news feed! 🔥

---

## 📚 More Info

- **Full Documentation**: `NEWS_FEED_FULL_README.md`
- **8 Presentation Formats**: `NEWS_PRESENTATION_CONCEPTS.md`
- **Visual Reference**: `QUICK_NEWS_FORMATS.txt`

---

**Time to first news**: < 2 seconds  
**Sources**: 40+  
**Languages**: Russian + English  
**Categories**: 6 (All, AI, Politics, US, EU, Russia)  

✅ **Ready to use!**

