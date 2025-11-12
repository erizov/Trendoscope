# 📚 RAG Storage Guide

## Обзор системы хранения

Trendoscope использует **двухуровневую систему хранения**:

1. **Vector DB (FAISS)** - для семантического поиска постов
2. **JSON Files** - для метаданных и style guide

---

## 🗂️ Структура хранения

```
data/
├── faiss_index.bin          # FAISS vector embeddings (binary)
├── faiss_docs.json          # Полные тексты постов + метаданные
├── style_guide.json         # Стиль автора (phrases, vocabulary)
└── posts_metadata.json      # Метаданные (URLs, count, timestamp)
```

### 1. Vector DB (FAISS) - RAG основа

**Файл**: `data/faiss_index.bin`  
**Что хранит**: Vector embeddings всех постов

```python
# Как создаются embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
embeddings = model.encode(post_texts)
faiss_index.add(embeddings)
```

**Размер**: ~1-2 KB на пост (зависит от модели)

**Пример**:
- 100 постов ≈ 150 KB
- 500 постов ≈ 750 KB
- 1000 постов ≈ 1.5 MB

### 2. Documents Storage

**Файл**: `data/faiss_docs.json`  
**Что хранит**: Полный текст + метаданные каждого поста

```json
[
  {
    "url": "https://civil-engineer.livejournal.com/12345.html",
    "title": "Заголовок поста",
    "text": "Полный текст поста...",
    "text_plain": "Чистый текст без HTML...",
    "published": "2024-01-15T10:30:00",
    "keywords": ["ключевое слово 1", "ключевое слово 2"],
    "sentiment": {"label": "positive", "score": 0.75},
    "entities": ["Организация", "Персона"]
  },
  ...
]
```

**Размер**: ~5-10 KB на пост (зависит от длины)

### 3. Style Guide

**Файл**: `data/style_guide.json`  
**Что хранит**: Анализ стиля автора

```json
{
  "blog_url": "https://civil-engineer.livejournal.com",
  "saved_at": "2025-11-12T15:30:00",
  "version": "1.0",
  "style": {
    "common_phrases": [
      "в конце концов",
      "с другой стороны",
      "как говорится"
    ],
    "vocabulary": [
      "амбивалентный",
      "дискурс",
      "парадигма"
    ],
    "avg_length": 2500,
    "avg_sentiment": {
      "label": "neutral",
      "score": 0.52
    },
    "typical_tags": ["философия", "политика", "история"],
    "examples": [
      "Пример типичного текста автора...",
      "Еще один пример..."
    ]
  }
}
```

### 4. Posts Metadata

**Файл**: `data/posts_metadata.json`  
**Что хранит**: Легковесные метаданные

```json
{
  "blog_url": "https://civil-engineer.livejournal.com",
  "post_count": 473,
  "post_urls": [
    "https://civil-engineer.livejournal.com/1.html",
    "https://civil-engineer.livejournal.com/2.html",
    ...
  ],
  "saved_at": "2025-11-12T15:30:00"
}
```

---

## 🔄 Как работает загрузка

### Текущий процесс (39 постов)

```python
# В pipeline/orchestrator.py
posts = scrape_livejournal(blog_url, max_posts=39)
analyzed = [analyze_text(p['text']) for p in posts]

# Add to FAISS
store = get_store()
store.add_documents(analyzed)  # Автосохранение на диск!

# Save style guide
style = analyze_style(analyzed)
save_analysis_results(posts, style, blog_url)
```

### Загрузка полного блога (500+ постов)

```bash
# Используйте новый скрипт
python load_full_blog.py

# Или с параметрами
python load_full_blog.py --max-posts 1000
python load_full_blog.py --blog-url https://другой-блог.livejournal.com
```

**Процесс**:
1. 🔍 Scraping всех постов (5-10 мин)
2. 📝 NLP анализ каждого (2-5 мин)
3. 🎨 Анализ стиля (10 сек)
4. 💾 Создание embeddings (1-2 мин)
5. 📁 Сохранение на диск (5 сек)

**Общее время**: ~10-20 минут для 500 постов

---

## 🚀 Использование RAG

### При запуске сервера

```python
# В api/main.py при старте
store = get_store()  # Автоматически загружает из data/faiss_index.bin

if store.documents:
    print(f"✅ Loaded {len(store.documents)} posts from RAG")
else:
    print("⚠️  RAG empty, run analysis first")
```

### При генерации постов

```python
# generate_post_from_storage() в post_generator.py

# 1. Проверяет style guide
if not has_saved_style():
    return error("Style guide not found")

# 2. Загружает из RAG
store = get_store()
analyzed_posts = store.documents  # Уже в памяти!

# 3. Semantic search (опционально)
similar = store.search("тема поста", top_k=5)

# 4. Генерирует пост
return generate_post(analyzed_posts, style, topic)
```

### Semantic Search

```python
# Пример поиска похожих постов
from trendascope.index.vector_db import get_store

store = get_store()

# Поиск постов на тему "искусственный интеллект"
results = store.search(
    query="искусственный интеллект и будущее",
    top_k=5
)

for doc in results:
    print(f"- {doc['title']}")
    print(f"  Similarity: {doc['score']:.2f}")
```

---

## 💡 Преимущества текущей системы

### 1. Персистентность
- ✅ Данные сохраняются автоматически
- ✅ Загружаются при старте сервера
- ✅ Не нужно повторно анализировать

### 2. Быстрый доступ
- ✅ FAISS index в памяти
- ✅ Все документы доступны мгновенно
- ✅ Semantic search < 100ms

### 3. Масштабируемость
- ✅ 100 постов → ~200 KB
- ✅ 1000 постов → ~2 MB
- ✅ 10000 постов → ~20 MB (все еще OK!)

### 4. Гибкость
- ✅ Можно загрузить любой блог
- ✅ Можно обновлять постепенно
- ✅ Можно очищать и перезагружать

---

## 🔧 Продвинутое использование

### Загрузка нескольких блогов

```python
# load_multiple_blogs.py
blogs = [
    "https://civil-engineer.livejournal.com",
    "https://another-blog.livejournal.com"
]

for blog in blogs:
    load_full_blog(blog_url=blog, max_posts=500)
    
# RAG будет содержать посты из обоих блогов!
```

### Инкрементальное обновление

```python
# update_rag.py
from trendascope.ingest.livejournal import scrape_livejournal
from trendascope.index.vector_db import get_store

# Загрузить только новые посты
new_posts = scrape_livejournal(blog_url, max_posts=10)

store = get_store()
# add_documents автоматически добавляет к существующим
store.add_documents(new_posts)

print(f"Total posts in RAG: {len(store.documents)}")
```

### Очистка и перезагрузка

```python
# clear_rag.py
from trendascope.storage.style_storage import get_storage
from trendascope.index.vector_db import get_store
import os

# Очистить style guide
storage = get_storage()
storage.clear()

# Удалить FAISS index
os.remove('data/faiss_index.bin')
os.remove('data/faiss_docs.json')

print("✅ RAG cleared. Run load_full_blog.py again.")
```

### Проверка содержимого

```python
# check_rag.py
from trendascope.index.vector_db import get_store
from trendascope.storage.style_storage import load_style_guide

# Статистика
store = get_store()
print(f"Posts in RAG: {len(store.documents)}")

# Примеры постов
for i, doc in enumerate(store.documents[:3]):
    print(f"\nPost {i+1}:")
    print(f"  Title: {doc['title']}")
    print(f"  URL: {doc['url']}")
    print(f"  Length: {len(doc['text'])} chars")

# Style guide
style = load_style_guide()
if style:
    print(f"\nStyle phrases: {len(style['style']['common_phrases'])}")
    print(f"Examples: {style['style']['common_phrases'][:5]}")
```

---

## ⚡ Performance

### Время загрузки при старте

| Posts | FAISS Load | Docs Load | Total |
|-------|------------|-----------|-------|
| 100   | 50ms       | 100ms     | 150ms |
| 500   | 150ms      | 500ms     | 650ms |
| 1000  | 300ms      | 1s        | 1.3s  |

### Semantic Search

| Posts | Search Time | Top-5 |
|-------|-------------|-------|
| 100   | 10ms        | ✅     |
| 500   | 30ms        | ✅     |
| 1000  | 50ms        | ✅     |
| 5000  | 200ms       | ✅     |

---

## 🎯 Рекомендации

### Для civil-engineer.livejournal.com

```bash
# Загрузите все доступные посты (рекомендуется)
python load_full_blog.py --max-posts 0

# Или первые 500 (быстрее)
python load_full_blog.py --max-posts 500
```

**Результат**:
- 📚 Полная база постов в RAG
- 🎨 Comprehensive style guide
- ⚡ Мгновенная генерация без повторного анализа
- 🔍 Semantic search по всему архиву

### Когда перезагружать

- 📅 Раз в месяц (для новых постов)
- 🔄 После значительных изменений в блоге
- 🐛 Если заметили проблемы со стилем

### Когда НЕ нужно перезагружать

- ✅ При каждой генерации поста (уже в RAG!)
- ✅ При перезапуске сервера (автозагрузка)
- ✅ При смене стиля/темы генерации

---

## 📊 Мониторинг RAG

```bash
# Проверить статус
python load_full_blog.py --status

# Вывод:
# ========================================
# 📊 CURRENT RAG STORAGE STATUS
# ========================================
# 
# ✅ Style Guide: Found
#    - Blog: https://civil-engineer.livejournal.com
#    - Saved: 2025-11-12T15:30:00
#    - Version: 1.0
# 
# ✅ Vector DB (RAG): 473 posts
#    - Storage: data/faiss_index.bin
#    - Size: 847.3 KB
```

---

## ❓ FAQ

**Q: Сколько постов нужно для хорошего style guide?**  
A: Минимум 30-50, оптимально 100-300, можно загрузить все

**Q: Будет ли работать с другими блогами?**  
A: Да! Используйте `--blog-url`

**Q: Можно ли смешать несколько блогов?**  
A: Да, просто загрузите их последовательно

**Q: Как часто обновлять RAG?**  
A: Зависит от частоты публикаций, обычно раз в месяц

**Q: Что делать если RAG поврежден?**  
A: Удалите `data/*.bin` и `data/*.json`, перезагрузите

**Q: Влияет ли размер RAG на скорость?**  
A: Минимально. 1000 постов = ~50ms поиск

**Q: Можно ли экспортировать RAG?**  
A: Да, просто скопируйте папку `data/`

---

## 🚀 Быстрый старт

```bash
# 1. Загрузите полный блог
python load_full_blog.py

# 2. Запустите сервер
python run.py

# 3. Откройте браузер
# http://localhost:8003

# 4. Генерируйте посты!
# Выберите тему, стиль, нажмите "Сгенерировать"
# Все работает из RAG, без повторного анализа!
```

---

**Version**: 2.1.0  
**Feature**: Persistent RAG Storage  
**Model**: all-MiniLM-L6-v2 (384d)  
**Backend**: FAISS (Facebook AI Similarity Search)

