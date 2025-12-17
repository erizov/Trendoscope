# ⚡ TTS Quick Test Guide

## 🚀 Быстрый старт тестирования

### 1. Запустите приложение

```bash
cd trendoscope2
python run.py
```

Приложение должно быть доступно на: `http://localhost:8004`

### 2. Быстрый тест API (PowerShell)

```powershell
# Test 1: Генерация TTS (Русский)
$response = Invoke-RestMethod -Uri "http://localhost:8004/api/tts/generate" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text": "Привет, это тест.", "language": "ru", "voice_gender": "female"}'

Write-Host "Audio ID: $($response.audio_id)"
Write-Host "Language: $($response.language)"
Write-Host "Provider: $($response.provider)"

# Test 2: Получить аудио файл
Invoke-WebRequest -Uri "http://localhost:8004/api/tts/audio/$($response.audio_id)" `
  -OutFile "test_audio.mp3"

Write-Host "Audio saved to test_audio.mp3"

# Test 3: Статистика
$stats = Invoke-RestMethod -Uri "http://localhost:8004/api/tts/stats"
Write-Host "Cache files: $($stats.cache_files)"
Write-Host "Cache size: $([math]::Round($stats.cache_size_bytes / 1MB, 2)) MB"
```

### 3. Запуск E2E тестов

```bash
# Все TTS тесты
pytest tests/e2e/test_tts.py -v

# Только генерация
pytest tests/e2e/test_tts.py::TestTTSGeneration -v

# Только кэширование
pytest tests/e2e/test_tts.py::TestTTSCaching -v

# С подробным выводом
pytest tests/e2e/test_tts.py -v -s
```

### 4. Тест Frontend

1. Откройте: `http://localhost:8004`
2. Нажмите "🔊 Читать вслух" на любой новости
3. Проверьте:
   - Модальное окно открывается
   - Аватар отображается
   - Аудио генерируется
   - Play/Pause работает

---

## ✅ Минимальный тест (30 секунд)

```bash
# 1. Проверка API
curl http://localhost:8004/health

# 2. Генерация TTS
curl -X POST http://localhost:8004/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "language": "en"}'

# 3. Откройте браузер
start http://localhost:8004
```

---

**Готово!** 🎉
