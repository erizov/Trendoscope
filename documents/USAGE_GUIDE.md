# 📖 Руководство по использованию Трендоскоп

## ✅ Что уже работает (без установки зависимостей)

Даже без установки внешних библиотек работает:
- ✅ NLP анализ текста (ключевые слова, сентимент, entity extraction)
- ✅ Анализ стиля автора
- ✅ Метрики читаемости
- ✅ Базовая структура pipeline

**Протестировано:** `python demo_simple.py` ✓ РАБОТАЕТ

## 📦 Быстрый старт

### Вариант 1: Минимальная демонстрация (без установки)

```bash
cd trendascope
python demo_simple.py
```

Это покажет базовую функциональность без внешних зависимостей.

### Вариант 2: Полная функциональность

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить полную демонстрацию
python demo.py

# 3. Запустить Web UI
python run.py
```

Затем откройте: http://localhost:8000

## 🎯 Основные сценарии использования

### Сценарий 1: Анализ блога civil-engineer.livejournal.com

#### Через Web UI:
1. Запустите: `python run.py`
2. Откройте: http://localhost:8000
3. Введите URL: `https://civil-engineer.livejournal.com`
4. Выберите количество постов: `20-50`
5. Выберите стиль: `Логосфера` (или другой)
6. Выберите провайдер: 
   - `Demo` - для тестирования без API ключей
   - `OpenAI` - если есть ключ OpenAI
   - `Anthropic` - если есть ключ Anthropic
7. Нажмите "Запустить анализ"

#### Через Python API:
```python
from src.trendascope.pipeline.orchestrator import Pipeline

pipeline = Pipeline()
result = pipeline.run_full_pipeline(
    blog_url="https://civil-engineer.livejournal.com",
    max_posts=30,
    mode="analytical",  # или другой стиль
    provider="demo"  # или openai, anthropic, local
)

# Результаты
print(f"Проанализировано постов: {result['stats']['analyzed_posts']}")
print(f"Найдено трендов: {len(result['trends'])}")
print(f"\nРезюме:\n{result['generated']['summary']}")
print(f"\nВарианты заголовков:")
for i, title in enumerate(result['generated']['titles'], 1):
    print(f"  {i}. {title}")
```

### Сценарий 2: Анализ конкретных постов

```python
from src.trendascope.nlp.analyzer import analyze_text

text = """
Ваш текст для анализа здесь.
Может быть несколько абзацев.
Система извлечёт ключевые слова, определит сентимент.
"""

analysis = analyze_text(text)

print("Ключевые слова:", [kw['text'] for kw in analysis['keywords']])
print("Сентимент:", analysis['sentiment']['label'])
print("Слов:", analysis['readability']['words'])
print("Предложений:", analysis['readability']['sentences'])
```

### Сценарий 3: Анализ стиля написания

```python
from src.trendascope.nlp.style_analyzer import (
    analyze_style,
    get_style_prompt
)

posts = [
    {"text_plain": "Ваш первый пост..."},
    {"text_plain": "Ваш второй пост..."},
    {"text_plain": "Ваш третий пост..."},
]

# Получить метрики стиля
style = analyze_style(posts)
print("Средняя длина предложения:", style['avg_sentence_length'])
print("Частота вопросов:", style['question_ratio'])
print("Типичные opening фразы:", style['common_openings'])

# Получить prompt для LLM
prompt = get_style_prompt(posts)
print("\nОписание стиля для LLM:")
print(prompt)
```

### Сценарий 4: Генерация контента

```python
from src.trendascope.gen.generate import generate_summary

analyzed_posts = [
    {
        "title": "Заголовок поста",
        "text_plain": "Текст поста...",
        "analysis": {...}  # результат analyze_text()
    },
    # ... ещё посты
]

generated = generate_summary(
    analyzed_posts,
    mode="provocative",  # стиль генерации
    provider="demo",  # или openai, anthropic
    temperature=0.7
)

print("Резюме:", generated['summary'])
print("Заголовки:", generated['titles'])
print("Идеи:", generated['ideas'])
print("Вирусный потенциал:", generated['viral_potential'])
```

### Сценарий 5: Отслеживание трендов

```python
from src.trendascope.trends.engine import (
    get_trending_topics,
    calculate_viral_potential
)

# analyzed_posts = [...ваши проанализированные посты...]

trends = get_trending_topics(analyzed_posts, top_n=10)

print("Топ-10 трендов:")
for trend in trends:
    print(f"  {trend['topic']}: score={trend['score']:.2f}, "
          f"posts={trend['post_count']}, "
          f"trending={trend['trending']}")

# Оценить вирусный потенциал конкретного поста
post = analyzed_posts[0]
viral = calculate_viral_potential(post, trends)
print(f"\nВирусный потенциал поста: {viral['label']}")
print(f"Score: {viral['score']}")
print(f"Факторы: {', '.join(viral['factors'])}")
```

## 🎨 Стили генерации

Система поддерживает 6 стилей:

1. **logospheric** - Краткие тезисы, точные цитаты
   ```python
   mode="logospheric"
   ```

2. **analytical** - Аналитический, для экспертных платформ
   ```python
   mode="analytical"
   ```

3. **provocative** - Провокационный, вызывает дискуссию
   ```python
   mode="provocative"
   ```

4. **humorous** - Юмористический, лёгкий и ироничный
   ```python
   mode="humorous"
   ```

5. **philosophical** - Философский, созерцательный
   ```python
   mode="philosophical"
   ```

6. **journalistic** - Журналистский, структурированный
   ```python
   mode="journalistic"
   ```

## 🔐 Настройка API ключей

### Для OpenAI:

Создайте файл `.env`:
```bash
OPENAI_API_KEY=sk-...
```

Или в коде:
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

Затем используйте:
```python
provider="openai",
model="gpt-4-turbo-preview"  # или gpt-3.5-turbo
```

### Для Anthropic:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

```python
provider="anthropic",
model="claude-3-sonnet-20240229"  # или другая модель
```

### Для локальных моделей (Ollama):

```bash
# Установите Ollama: https://ollama.ai
ollama pull llama2
```

```python
provider="local",
model="llama2"
```

## 🔍 REST API Endpoints

### GET /api/pipeline/run

Запустить полный pipeline.

**Пример:**
```bash
curl "http://localhost:8000/api/pipeline/run?blog_url=https://civil-engineer.livejournal.com&max_posts=20&mode=analytical&provider=demo"
```

**Параметры:**
- `blog_url` - URL блога (default: civil-engineer.livejournal.com)
- `max_posts` - Количество постов 1-100 (default: 20)
- `mode` - Стиль генерации (default: logospheric)
- `provider` - LLM провайдер (default: demo)
- `model` - Название модели (optional)

**Ответ:**
```json
{
  "posts": [...],
  "trends": [...],
  "generated": {...},
  "stats": {...}
}
```

### POST /api/generate/summary

Сгенерировать контент из готовых постов.

**Пример:**
```bash
curl -X POST http://localhost:8000/api/generate/summary \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"title": "...", "text_plain": "..."}],
    "mode": "analytical",
    "provider": "demo"
  }'
```

### GET /api/modes

Получить список стилей.

```bash
curl http://localhost:8000/api/modes
```

### GET /api/health

Health check.

```bash
curl http://localhost:8000/api/health
```

## 🐛 Решение проблем

### Проблема: ModuleNotFoundError

```bash
# Решение: установите зависимости
pip install -r requirements.txt
```

### Проблема: Unicode ошибки в Windows консоли

```bash
# Решение: используйте demo_simple.py вместо demo.py
python demo_simple.py
```

Или настройте консоль:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Проблема: Ошибка импорта src.trendascope

```bash
# Решение: добавьте src в PYTHONPATH
cd trendascope
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
$env:PYTHONPATH="$env:PYTHONPATH;$(pwd)\src"  # Windows PowerShell
```

Или используйте скрипты `run.py` и `demo.py` которые делают это автоматически.

### Проблема: LLM API ошибки

```python
# Решение: используйте demo провайдер для тестирования
provider="demo"
```

Или проверьте API ключи:
```bash
echo $OPENAI_API_KEY  # должен показать ваш ключ
```

### Проблема: Медленная работа

1. Уменьшите количество постов: `max_posts=10`
2. Используйте кеширование (Redis)
3. Используйте FAISS вместо Qdrant (in-memory быстрее)

## 📊 Структура результатов

### Результат pipeline:

```python
{
  "posts": [
    {
      "title": "...",
      "text_plain": "...",
      "url": "...",
      "published": "...",
      "tags": [...],
      "comments_count": 42,
      "analysis": {
        "keywords": [{" text": "...", "score": 0.9}],
        "sentiment": {"label": "positive", "score": 0.8},
        "entities": [{"text": "...", "type": "..."}],
        "readability": {
          "words": 350,
          "sentences": 15,
          "avg_words_per_sentence": 23.3,
          "avg_word_length": 5.2
        }
      },
      "viral_potential": {
        "label": "high",
        "score": 0.78,
        "factors": ["Оптимальная длина текста", ...]
      }
    }
  ],
  "trends": [
    {
      "topic": "технологии",
      "score": 15.3,
      "post_count": 8,
      "trend_slope": 0.42,
      "trending": true
    }
  ],
  "generated": {
    "summary": "...",
    "titles": ["...", "...", "..."],
    "ideas": [
      {
        "title": "...",
        "explanation": "...",
        "format": "лонгрид",
        "cta": "Обсудить",
        "timing": "вечер"
      }
    ],
    "leads": {
      "short": "...",
      "long": "..."
    },
    "viral_potential": {
      "label": "medium",
      "score": 0.55,
      "why": "..."
    }
  },
  "stats": {
    "total_posts": 50,
    "analyzed_posts": 48,
    "top_trends": 10
  }
}
```

## 💡 Советы и лучшие практики

1. **Для быстрого тестирования:**
   - Используйте `provider="demo"`
   - Ограничьте `max_posts=10-20`
   - Используйте `demo_simple.py`

2. **Для production использования:**
   - Настройте Redis для кеширования
   - Используйте Qdrant для векторной БД
   - Используйте OpenAI/Anthropic для качественной генерации
   - Увеличьте `max_posts=50-100` для лучшего анализа трендов

3. **Для анализа стиля:**
   - Используйте минимум 10-20 постов автора
   - Выберите репрезентативные посты
   - Регулярно обновляйте стиль на новых постах

4. **Для генерации вирусного контента:**
   - Изучите топ-тренды
   - Используйте `provocative` или `humorous` стили
   - Обращайте внимание на viral_potential score
   - Экспериментируйте с разными заголовками

## 📚 Дополнительные ресурсы

- **Полная документация:** `README.md`
- **Быстрый старт:** `QUICKSTART.md`
- **Итоговый отчёт:** `PROJECT_SUMMARY.md`
- **API документация:** http://localhost:8000/docs (после запуска)

## ❓ FAQ

**Q: Можно ли использовать без интернета?**  
A: Да, с demo провайдером и FAISS векторной БД. Но для scraping нужен интернет.

**Q: Сколько стоит использование OpenAI?**  
A: ~$0.01-0.05 за один pipeline run (зависит от max_posts и модели).

**Q: Можно ли анализировать другие блоги?**  
A: Да, любой LiveJournal блог. Просто укажите другой `blog_url`.

**Q: Поддерживается ли batch обработка?**  
A: Да, можно запускать pipeline в цикле для разных блогов.

**Q: Как экспортировать результаты?**  
A: Результаты возвращаются в JSON. Сохраните в файл:
```python
import json
with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## ✉️ Поддержка

При возникновении проблем:
1. Проверьте логи
2. Запустите тесты: `pytest -v`
3. Попробуйте demo режим
4. Проверьте установку зависимостей

