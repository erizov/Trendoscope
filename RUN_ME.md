# 🚀 QUICK START - See Executive Summaries NOW

## For Browser View (Recommended):

```bash
# 1. Open PowerShell in this directory
cd E:\Python\FastAPI\Trendoscope\trendascope

# 2. Install minimal dependencies (one time)
pip install fastapi uvicorn numpy sentence-transformers

# 3. Start server
python run.py

# 4. Open browser to:
http://localhost:8000

# 5. In the web form:
#    - Leave URL as: https://civil-engineer.livejournal.com
#    - Set posts to: 20
#    - Select style: Логосфера (or any other)
#    - Select provider: Demo
#    - Click: "Запустить анализ"
```

## For Terminal View:

```bash
# 1. Same directory
cd E:\Python\FastAPI\Trendoscope\trendascope

# 2. Install minimal dependencies
pip install numpy sentence-transformers

# 3. Run demo
python demo.py
```

## What You'll See:

### Executive Summary Example:
```
РЕЗЮМЕ:
Искусственный интеллект и технологии стремительно 
меняют наш мир. Эксперты обсуждают влияние нейросетей
на различные сферы жизни. Ключевые вопросы: этика AI,
будущее образования, экономические последствия...
```

### Title Suggestions:
```
1. Искусственный интеллект: угроза или возможность?
2. Как нейросети меняют наш мир
3. Технологии будущего: что нас ждёт
```

### Post Ideas:
```
Идея 1: "AI в образовании"
- Краткое пояснение идеи
- Формат: лонгрид
- CTA: Обсудить в комментариях
- Timing: вечер
```

### Viral Potential:
```
Уровень: MEDIUM
Оценка: 0.65
Факторы: Трендовые темы, эмоциональный окрас, вопросы
```

---

## Troubleshooting:

**If you get "Module not found":**
```bash
pip install -r requirements.txt
```

**If port 8000 is busy:**
```bash
# Edit run.py and change port to 8001
# Or kill process on port 8000
```

**If browser shows nothing:**
```bash
# Make sure server is running (check terminal)
# Try: http://127.0.0.1:8000
```

---

## Next Steps After First Run:

1. **Try real LLM** (better quality):
   - Add to .env: `OPENAI_API_KEY=sk-...`
   - Select provider: OpenAI
   
2. **Analyze more posts** for better trends:
   - Increase max_posts to 50-100
   
3. **Try different styles**:
   - Provocative (for discussions)
   - Humorous (for entertainment)
   - Philosophical (for deep thoughts)

---

Ready? Run the commands above! 🚀

