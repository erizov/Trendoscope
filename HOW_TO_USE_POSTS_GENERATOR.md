# 🚀 How to Use Posts Generator

Simple web interface for generating posts with one click.

---

## Quick Start

### 1. Start the Server

```bash
cd trendascope
python run.py
```

Server will start at http://localhost:8003

### 2. Open the Posts Generator

Open in your browser:

```
http://localhost:8003/static/posts_generator.html
```

### 3. Generate Posts

1. **Select Style**: 
   - 🧘 Философский (Philosophical)
   - 😏 Ироничный (Ironic)
   - 📊 Аналитический (Analytical)
   - 🔥 Провокационный (Provocative)

2. **Select Topic**:
   - 🌍 Любая (Any)
   - 🤖 Искусственный интеллект (AI)
   - 🏛️ Политика (Politics)
   - 🇺🇸 США (US Affairs)
   - 🇷🇺 Российская история (Russian History)
   - 🔬 Наука (Science)

3. **Select Model**:
   - OpenAI (GPT-4) - requires API key
   - Demo (test mode) - works without API key

4. **Click "Сгенерировать 3 поста"**

---

## Features

✅ **Generate 3 posts at once**  
✅ **Beautiful card layout**  
✅ **Automatic news fetching** (22+ sources)  
✅ **English → Russian translation**  
✅ **Semantic topic filtering**  
✅ **Style matching** from your blog  
✅ **One-click generation**

---

## What Happens Behind the Scenes

When you click "Generate":

1. **Fetches latest news** from 22+ sources
2. **Translates English news** to Russian
3. **Filters by topic** using semantic similarity
4. **Aggregates context** from multiple sources
5. **Generates 3 posts** in your style
6. **Displays results** in beautiful cards

Takes about **30-60 seconds** for 3 posts.

---

## Tips

### 🎯 Best Results

- **Use OpenAI model** for best quality (requires API key)
- **Try different styles** - each generates unique content
- **Specific topics** work better than "Any"
- **Generate multiple batches** to pick the best post

### 🔑 Setup API Key

Create `.env` file:

```bash
# In trendascope/.env
OPENAI_API_KEY=sk-your-key-here
```

Restart server after adding key.

### 📊 Post Display

Each post shows:
- **Style badge** (Философский, Ироничный, etc.)
- **Topic badge** (ИИ, Политика, etc.)
- **Title** - catchy and relevant
- **Full text** - 400-700 words
- **Tags** - for categorization

---

## Keyboard Shortcuts

- **Enter** while in select fields - Start generation
- **Scroll** in post text - Read full content

---

## Troubleshooting

### "Сервер не отвечает"

**Solution**: Start the server
```bash
cd trendascope
python run.py
```

### "Ошибка генерации"

**Possible causes**:

1. **No API key** - Add to `.env` or use Demo mode
2. **No RAG data** - Run `python load_full_blog.py` first
3. **API limit reached** - Wait a minute and retry

### "Генерация долго"

**Normal!** Each post takes 10-20 seconds:
- Fetching news
- Translation
- Semantic filtering
- Context aggregation
- LLM generation

3 posts = 30-60 seconds total.

---

## Advanced Usage

### Generate Different Combinations

Try these combinations for different results:

**1. Daily News Digest**
- Style: Аналитический
- Topic: Любая
- Result: Balanced analysis of current events

**2. AI Commentary**
- Style: Философский
- Topic: ИИ
- Result: Deep thoughts on AI developments

**3. Political Satire**
- Style: Ироничный
- Topic: Политика
- Result: Sarcastic take on politics

**4. Provocative Opinion**
- Style: Провокационный
- Topic: США
- Result: Controversial perspective

### Generate Many, Pick Best

1. Click "Generate" multiple times
2. Review all posts
3. Pick the best one
4. Copy to LiveJournal

---

## Example Output

### Philosophical Post about AI

```
Title: GPT-5 и экзистенциальный кризис человечества

Text:
OpenAI анонсировала GPT-5, и снова весь мир замер в ожидании
очередного технологического прорыва. Но если честно, вопрос не в том,
насколько умной станет нейросеть, а в том, когда мы наконец поймём,
что делегируя машинам всё больше функций, мы не столько освобождаем
себя от рутины, сколько добровольно отказываемся от того, что делает
нас людьми...

[Continue for 500+ words]

Tags: #искусственныйинтеллект #технологии #философия
```

---

## Next Steps

### Save to LiveJournal

Currently: **Manual copy-paste**

Coming soon: **Direct publishing**
```python
# Will be available
from trendascope.publish.livejournal import publish_generated_post
result = publish_generated_post(post, username, password)
```

### Automate Daily

Create script to generate automatically:

```python
# daily_posts.py
from src.trendascope.gen.post_generator import generate_post_from_storage
import random

topics = ["ai", "politics", "us_affairs"]
styles = ["philosophical", "ironic", "analytical"]

post = generate_post_from_storage(
    style=random.choice(styles),
    topic=random.choice(topics)
)

print(f"Title: {post['title']}")
print(f"Text: {post['text']}")
```

Run daily with cron:
```bash
0 9 * * * cd /path/to/trendascope && python daily_posts.py
```

---

## FAQ

**Q: Can I generate more than 3 posts?**  
A: Yes! Click the button multiple times. Each click generates 3 new posts.

**Q: How is this different from the main UI?**  
A: This is simpler - just posts. Main UI has full analysis pipeline.

**Q: Can I customize the styles?**  
A: Yes! Edit `src/trendascope/gen/post_generator.py` to add new styles.

**Q: Where are the news sources?**  
A: 22+ sources defined in `src/trendascope/ingest/news_sources.py`

**Q: Can I use it without internet?**  
A: Demo mode works offline but with fake data. OpenAI requires internet.

---

## Performance

**Generation Speed**:
- Demo mode: ~5 seconds/post
- OpenAI mode: ~15-20 seconds/post

**Resource Usage**:
- RAM: ~500 MB
- CPU: Moderate during generation
- Network: ~2 MB per generation

---

## Enjoy! 🎉

Generate amazing posts with one click.

**URL**: http://localhost:8003/static/posts_generator.html

**Questions?** Check the main docs:
- `IMPROVEMENTS_COMPLETE.md`
- `QUICK_START_NEW_FEATURES.md`

