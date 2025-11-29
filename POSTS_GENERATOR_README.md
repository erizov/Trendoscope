# 🚀 Posts Generator - Simple Interface

**Generate 3 posts with one click!**

---

## ⚡ Quick Start (3 Steps)

### 1. Start Server

**Windows**:
```bash
start_posts_generator.bat
```

**or manually**:
```bash
python run.py
```

### 2. Open Browser

Go to: http://localhost:8003/static/posts_generator.html

### 3. Generate Posts

1. Select style (Философский, Ироничный, etc.)
2. Select topic (ИИ, Политика, etc.)
3. Click "Сгенерировать 3 поста"
4. Wait 30-60 seconds
5. Done! 3 beautiful posts appear

---

## 📸 Screenshot

```
┌─────────────────────────────────────────────┐
│  🚀 Генератор Постов                        │
│  Автоматическая генерация постов            │
├─────────────────────────────────────────────┤
│  Стиль: [Философский ▼]                     │
│  Тема:  [ИИ ▼]                              │
│  Модель: [OpenAI ▼]                         │
│  [✨ Сгенерировать 3 поста]                 │
├─────────────────────────────────────────────┤
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ Post 1    │ │ Post 2    │ │ Post 3    │ │
│  │ Title...  │ │ Title...  │ │ Title...  │ │
│  │ Text...   │ │ Text...   │ │ Text...   │ │
│  │ #tags     │ │ #tags     │ │ #tags     │ │
│  └───────────┘ └───────────┘ └───────────┘ │
└─────────────────────────────────────────────┘
```

---

## ✨ Features

- ✅ **One-click generation** - no complex setup
- ✅ **3 posts at once** - compare and pick best
- ✅ **Beautiful UI** - gradient design, smooth animations
- ✅ **22+ news sources** - Russian + English
- ✅ **Auto-translation** - English news → Russian
- ✅ **Your style** - matches your blog writing
- ✅ **4 styles available** - philosophical, ironic, analytical, provocative
- ✅ **6 topics** - AI, politics, US, Russia, science, any

---

## 🎯 What Makes It Different

### vs Main UI (`index.html`)
- **Simpler**: Just posts, no analysis
- **Faster**: Click and go
- **Focused**: One task done well

### vs Command Line
- **Visual**: Beautiful cards
- **Easy**: No code needed
- **Compare**: See 3 posts side-by-side

---

## 🔥 Usage Tips

### 1. Generate Multiple Batches

Click button several times to generate 9, 12, or 15 posts. Pick the best!

### 2. Try Different Combinations

- **Morning**: Analytical + Politics
- **Afternoon**: Ironic + AI
- **Evening**: Philosophical + Science

### 3. Use Demo Mode First

Select "Demo" model to test without API key.

### 4. Then Switch to OpenAI

For real high-quality posts, use OpenAI (requires API key).

---

## ⚙️ Setup

### Minimal (Demo Mode)

Works immediately - no setup needed!

### Full (OpenAI)

1. Create `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

2. Restart server

3. Select "OpenAI" in dropdown

---

## 🎨 Styles Explained

### 🧘 Философский (Philosophical)
Deep reflections on meaning and consequences of events.
**Use for**: Thoughtful analysis

### 😏 Ироничный (Ironic)
Sarcastic take with historical parallels.
**Use for**: Entertainment, satire

### 📊 Аналитический (Analytical)
Logical breakdown with predictions.
**Use for**: Serious analysis

### 🔥 Провокационный (Provocative)
Controversial opinions to spark discussion.
**Use for**: Engagement, debates

---

## 🌍 Topics Explained

### 🤖 ИИ (AI)
Latest AI developments, GPT, neural networks.

### 🏛️ Политика (Politics)
Political events, geopolitics, international relations.

### 🇺🇸 США (US Affairs)
American politics and US influence.

### 🇷🇺 Российская история (Russian History)
Russian history and historical parallels.

### 🔬 Наука (Science)
Scientific discoveries and breakthroughs.

### 🌍 Любая (Any)
Mix of all topics.

---

## 📊 Performance

**Generation Time per Post**:
- Demo mode: ~5 seconds
- OpenAI mode: ~15-20 seconds

**Total for 3 Posts**:
- Demo: ~15 seconds
- OpenAI: ~30-60 seconds

**Why so long?**
- Fetching news from 22+ sources
- Translating English → Russian
- Semantic filtering
- Context aggregation
- LLM generation

Worth the wait! 🎉

---

## 🐛 Troubleshooting

### Page not loading?

**Check**: Is server running?
```bash
python run.py
```

**URL**: http://localhost:8003/static/posts_generator.html

### "Сервер не отвечает"?

**Solution**: Start server first
```bash
cd trendascope
python run.py
```

### "Ошибка генерации"?

**Possible causes**:

1. **No API key** (OpenAI mode)
   - Solution: Use Demo mode OR add API key to `.env`

2. **No RAG data**
   - Solution: Run `python load_full_blog.py`

3. **Network issue**
   - Solution: Check internet connection

### Posts are generic?

**Solution**: Make sure RAG has your blog data
```bash
python check_rag.py
```

Should show 68+ posts loaded.

---

## 📱 Mobile Friendly

Works on tablets and phones!
- Responsive design
- Touch-friendly buttons
- Scrollable posts

---

## 🚀 Advanced

### Automate Daily Generation

Create `auto_generate.py`:

```python
from src.trendascope.gen.post_generator import generate_post_from_storage
import random

styles = ["philosophical", "ironic", "analytical"]
topics = ["ai", "politics", "us_affairs"]

# Generate 3 posts
for i in range(3):
    post = generate_post_from_storage(
        style=random.choice(styles),
        topic=random.choice(topics)
    )
    print(f"\n=== Post {i+1} ===")
    print(f"Title: {post['title']}")
    print(f"Style: {post['style_name']}")
    print(f"Length: {len(post['text'])} chars\n")
```

Run daily:
```bash
python auto_generate.py
```

### Save to File

Add to script:

```python
import json
from datetime import datetime

posts = []
for i in range(3):
    post = generate_post_from_storage(...)
    posts.append(post)

# Save to file
filename = f"posts_{datetime.now().strftime('%Y%m%d')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"Saved to {filename}")
```

### Export to LiveJournal Format

```python
# Export ready for LJ
def format_for_lj(post):
    lj_post = f"""
<lj-cut text="Читать далее">
{post['text']}
</lj-cut>

<small>
Теги: {', '.join(f'#{tag}' for tag in post['tags'])}
</small>
"""
    return lj_post

formatted = format_for_lj(post)
print(formatted)
```

---

## 📚 Related Docs

- **Full guide**: `HOW_TO_USE_POSTS_GENERATOR.md`
- **All improvements**: `IMPROVEMENTS_COMPLETE.md`
- **Quick start**: `QUICK_START_NEW_FEATURES.md`
- **Main README**: `README.md`

---

## 💡 Pro Tips

1. **Generate in batches**: 3-6 posts, pick best
2. **Try all styles**: Each produces different quality
3. **Specific topics work better**: "AI" > "Any"
4. **Check post length**: 400-700 words is optimal
5. **Read tags**: They suggest the focus
6. **Edit if needed**: Posts are starting points

---

## 🎉 That's It!

Super simple interface for generating posts.

**Just 3 steps**:
1. Start server
2. Open page
3. Click button

**Enjoy!** 🚀

---

**URL**: http://localhost:8003/static/posts_generator.html

**Questions?** See `HOW_TO_USE_POSTS_GENERATOR.md`

