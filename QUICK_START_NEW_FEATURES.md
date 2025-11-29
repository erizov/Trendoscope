# 🚀 Quick Start - New Features

## TL;DR

Generate and publish posts in Russian about AI/politics from English+Russian sources.

---

## 1️⃣ Generate Enhanced Post

```python
from src.trendascope.gen.post_generator import generate_post_from_storage

post = generate_post_from_storage(
    style="ironic",      # philosophical, ironic, analytical, provocative
    topic="ai",          # ai, politics, us_affairs, russian_history, science
    provider="openai",
    model="gpt-4",
    temperature=0.8
)

print(f"Title: {post['title']}")
print(f"Text: {post['text'][:500]}...")
print(f"Tags: {post['tags']}")
```

**What happens automatically**:
- ✅ Fetches from 22+ news sources (Russian + English)
- ✅ Translates English news to Russian
- ✅ Filters by topic using semantic similarity
- ✅ Aggregates multi-source context
- ✅ Generates in your style with signature phrases

---

## 2️⃣ Preview Before Publishing

```python
from src.trendascope.publish.livejournal import publish_generated_post

# Preview
preview = publish_generated_post(
    post,
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    preview=True
)

print(preview)  # Shows what will be published
```

---

## 3️⃣ Publish to LiveJournal

```python
# Actually publish
result = publish_generated_post(
    post,
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    security="public"  # or "private" or "friends"
)

if result['success']:
    print(f"✅ Published: {result['post_url']}")
else:
    print(f"❌ Error: {result['error']}")
```

---

## 4️⃣ Complete Workflow

```python
from src.trendascope.gen.post_generator import generate_post_from_storage
from src.trendascope.publish.livejournal import publish_generated_post

# 1. Generate
post = generate_post_from_storage(
    style="philosophical",
    topic="politics"
)

# 2. Review (optional)
print(f"\n{'='*70}")
print(f"TITLE: {post['title']}")
print(f"{'='*70}")
print(post['text'])
print(f"{'='*70}")
print(f"TAGS: {', '.join(post['tags'])}")
print(f"{'='*70}\n")

# 3. Confirm
confirm = input("Publish? (y/n): ")

if confirm.lower() == 'y':
    # 4. Publish
    result = publish_generated_post(
        post,
        username="YOUR_USERNAME",
        password="YOUR_PASSWORD"
    )
    
    if result['success']:
        print(f"\n✅ Success! {result['post_url']}")
    else:
        print(f"\n❌ Failed: {result['error']}")
```

---

## 5️⃣ Advanced: Get News Context

```python
from src.trendascope.ingest.news_sources import fetch_trending_news
from src.trendascope.nlp.context_aggregator import ContextAggregator

# Fetch news
news = fetch_trending_news(
    max_items=20,
    include_russian=True,
    include_international=True,
    include_ai=True,
    include_politics=True
)

print(f"Found {news['count']} news items")

# Aggregate context
aggregator = ContextAggregator()
context = aggregator.aggregate_context(
    news['news_items'],
    topic="ai"
)

print(f"\nMain narrative: {context['main_narrative'][:200]}...")
print(f"\nKey facts: {len(context['key_facts'])}")
print(f"Perspectives: {len(context['different_perspectives'])}")
print(f"Sources: {', '.join(context['sources'][:5])}")
```

---

## 6️⃣ Test Individual Features

### Translation

```python
from src.trendascope.nlp.translator import smart_translate_text

russian = smart_translate_text(
    "OpenAI released GPT-5 with groundbreaking AI capabilities",
    provider="openai",
    style="neutral"
)

print(russian)
# Output: "OpenAI выпустила GPT-5 с революционными возможностями ИИ"
```

### Semantic Filtering

```python
from src.trendascope.nlp.semantic_filter import filter_news_by_topic_semantic
from src.trendascope.ingest.news_sources import fetch_trending_news

news = fetch_trending_news(max_items=20)

ai_news = filter_news_by_topic_semantic(
    news['news_items'],
    topic="ai",
    threshold=0.3
)

for item in ai_news[:5]:
    relevance = item.get('topic_relevance', 0)
    print(f"[{relevance:.2f}] {item['title']}")
```

### Style Analysis

```python
from src.trendascope.nlp.advanced_style import AdvancedStyleAnalyzer
from src.trendascope.index.vector_db import get_store

store = get_store()
posts = store.documents

analyzer = AdvancedStyleAnalyzer()
patterns = analyzer.extract_deep_patterns(posts)

print(f"Openings: {patterns['opening_patterns'][:2]}")
print(f"Closings: {patterns['closing_patterns'][:2]}")
print(f"Questions: {patterns['rhetorical_questions'][:3]}")
print(f"Irony: {patterns['irony_markers']['quotation_usage_pct']:.1f}%")
```

---

## 🎯 Common Use Cases

### Daily Automation

```python
# daily_post.py
import random
from src.trendascope.gen.post_generator import generate_post_from_storage
from src.trendascope.publish.livejournal import publish_generated_post

topics = ["ai", "politics", "us_affairs"]
styles = ["philosophical", "ironic", "analytical"]

post = generate_post_from_storage(
    style=random.choice(styles),
    topic=random.choice(topics)
)

result = publish_generated_post(
    post,
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD"
)

print(f"Published: {result.get('post_url', 'Failed')}")
```

Run with cron:
```bash
# Every day at 9 AM
0 9 * * * cd /path/to/trendascope && python daily_post.py
```

### Multiple Posts with Different Styles

```python
from src.trendascope.gen.post_generator import generate_post_from_storage

styles = ["philosophical", "ironic", "analytical"]

posts = []
for style in styles:
    post = generate_post_from_storage(
        style=style,
        topic="ai"
    )
    posts.append(post)

# Review all, pick best
for i, post in enumerate(posts, 1):
    print(f"\n=== Post {i} ({styles[i-1]}) ===")
    print(post['title'])
    print(post['text'][:300] + "...\n")

choice = int(input("Which post to publish? (1-3): "))
selected_post = posts[choice - 1]

# Publish selected
from src.trendascope.publish.livejournal import publish_generated_post
result = publish_generated_post(selected_post, username, password)
```

### Schedule for Optimal Time

```python
from datetime import datetime, timedelta
from src.trendascope.publish.livejournal import schedule_post

# Generate now
post = generate_post_from_storage(style="analytical", topic="politics")

# Schedule for tomorrow 10 AM
tomorrow_10am = datetime.now() + timedelta(days=1)
tomorrow_10am = tomorrow_10am.replace(hour=10, minute=0, second=0)

result = schedule_post(
    post,
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    schedule_time=tomorrow_10am,
    security="public"
)

print(f"Scheduled for {tomorrow_10am}")
```

---

## ⚙️ Configuration

### Set Credentials

Create `.env` file:

```bash
# In trendascope/.env
OPENAI_API_KEY=sk-...
LJ_USERNAME=your_username
LJ_PASSWORD=your_password
```

Then use without passing credentials:

```python
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('LJ_USERNAME')
password = os.getenv('LJ_PASSWORD')

result = publish_generated_post(post, username, password)
```

---

## 🔥 Pro Tips

1. **Preview always**: Use `preview=True` first to check output
2. **Try different styles**: Generate 2-3 versions, pick best
3. **Check topic relevance**: Use semantic filter to see relevance scores
4. **Monitor sources**: Check which sources provided best content
5. **Adjust temperature**: Lower (0.5-0.6) = more factual, Higher (0.8-0.9) = more creative

---

## 🐛 Troubleshooting

### "No posts in RAG"

```python
# Run this first:
python load_full_blog.py

# Or check status:
python check_rag.py
```

### "Translation failed"

Check API key:
```python
import os
print(os.getenv('OPENAI_API_KEY'))
```

### "Publishing failed"

Test connection:
```python
from src.trendascope.publish.livejournal import LiveJournalPublisher

publisher = LiveJournalPublisher(username, password)
if publisher.test_connection():
    print("✅ Connected")
else:
    print("❌ Check credentials")
```

---

## 📚 More Info

See `IMPROVEMENTS_COMPLETE.md` for full documentation.

**Enjoy!** 🎉

