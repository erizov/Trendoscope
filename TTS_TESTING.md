# 🎤 TTS Testing Guide - Complete

## Обзор

Полное руководство по тестированию Text-to-Speech (TTS) функциональности в Trendoscope2.

---

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [API Тестирование](#api-тестирование)
3. [Audio Quality тесты](#audio-quality-тесты)
4. [Performance тесты](#performance-тесты)
5. [Integration тесты](#integration-тесты)
6. [Примеры использования](#примеры-использования)

---

## 🚀 Быстрый старт

### Запуск всех TTS тестов

```bash
cd trendoscope2
pytest tests/e2e/test_tts.py tests/e2e/test_tts_quality.py -v
```

### Запуск конкретных тестов

```bash
# Основные TTS тесты
pytest tests/e2e/test_tts.py -v

# Quality и Performance тесты
pytest tests/e2e/test_tts_quality.py -v

# Конкретный тест
pytest tests/e2e/test_tts.py::TestTTS::test_generate_russian -v
```

---

## 🔌 API Тестирование

### Endpoints

- `POST /api/tts/generate` - Генерация аудио
- `GET /api/tts/audio/{audio_id}` - Получение аудио файла
- `GET /api/tts/stats` - Статистика TTS сервиса

### Примеры запросов

#### Генерация TTS (Русский)

```bash
curl -X POST http://localhost:8004/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Привет, это тестовое сообщение на русском языке.",
    "language": "ru",
    "voice_gender": "female"
  }'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "audio_id": "uuid-here",
  "audio_url": "/api/tts/audio/uuid-here",
  "language": "ru",
  "duration": 2.5,
  "provider": "gtts",
  "used_fallback": false,
  "created_at": "2024-..."
}
```

#### Генерация TTS (Английский)

```bash
curl -X POST http://localhost:8004/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test message in English.",
    "language": "en",
    "voice_gender": "male"
  }'
```

#### Получение аудио файла

```bash
curl http://localhost:8004/api/tts/audio/{audio_id} --output test.mp3
```

**Проверка:**
- Content-Type: `audio/mpeg` или `audio/mp3`
- Размер файла > 0
- Файл можно воспроизвести

#### Статистика TTS

```bash
curl http://localhost:8004/api/tts/stats
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "cache_enabled": true,
  "cache_size": 10,
  "cache_hits": 5,
  "cache_misses": 3
}
```

---

## 🎵 Audio Quality тесты

### Тест 1: Формат аудио

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSAudioQuality::test_audio_format_mp3 -v
```

**Проверяет:**
- ✅ Аудио в формате MP3
- ✅ Правильный MIME type (`audio/mpeg`)
- ✅ Размер файла > 0

### Тест 2: Длительность аудио

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSAudioQuality::test_audio_duration_reasonable -v
```

**Проверяет:**
- ✅ Длительность соответствует длине текста
- ✅ Метаданные аудио присутствуют

### Тест 3: Разные языки

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSAudioQuality::test_different_languages -v
```

**Проверяет:**
- ✅ Русский язык (`ru`)
- ✅ Английский язык (`en`)
- ✅ Автоопределение языка (`auto`)

### Тест 4: Разные голоса

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSAudioQuality::test_different_voice_genders -v
```

**Проверяет:**
- ✅ Мужской голос (`male`)
- ✅ Женский голос (`female`)

### Тест 5: Длинные тексты

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSAudioQuality::test_long_text_handling -v
```

**Проверяет:**
- ✅ Обработка длинных текстов
- ✅ Ограничение длины (если есть)

---

## ⚡ Performance тесты

### Тест 1: Время генерации

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSPerformance::test_generation_time -v
```

**Проверяет:**
- ✅ Время генерации < 10 секунд для короткого текста

### Тест 2: Кэширование

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSPerformance::test_caching_works -v
```

**Проверяет:**
- ✅ Повторные запросы используют кэш
- ✅ Второй запрос быстрее первого
- ✅ Кэш работает корректно

**Как работает кэширование:**
1. Первый запрос генерирует аудио и сохраняет в кэш
2. Второй запрос с тем же текстом использует кэш
3. Время второго запроса значительно меньше

### Тест 3: Параллельная генерация

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSPerformance::test_parallel_generation -v
```

**Проверяет:**
- ✅ Параллельная генерация работает
- ✅ Все запросы завершаются успешно
- ✅ Время выполнения разумное

---

## 🔗 Integration тесты

### TTS + News Feed

```bash
pytest tests/e2e/test_tts_quality.py::TestTTSIntegration::test_tts_with_news_feed -v
```

**Проверяет:**
- ✅ Генерация TTS из новостных статей
- ✅ Интеграция с news feed API
- ✅ Корректная обработка данных

### TTS + Email

```bash
pytest tests/e2e/test_voice_email_telegram.py::TestIntegrations::test_tts_and_email_integration -v
```

**Проверяет:**
- ✅ TTS аудио может быть включено в email
- ✅ Интеграция работает корректно

### TTS + Telegram

```bash
pytest tests/e2e/test_voice_email_telegram.py::TestIntegrations::test_tts_and_telegram_integration -v
```

**Проверяет:**
- ✅ TTS аудио может быть включено в Telegram пост
- ✅ Интеграция работает корректно

---

## 📝 Примеры использования

### Пример 1: Базовое использование

```python
import requests

# Генерация TTS
response = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={
        "text": "Hello, world!",
        "language": "en",
        "voice_gender": "female"
    }
)

data = response.json()
audio_id = data["audio_id"]

# Получение аудио
audio_response = requests.get(
    f"http://localhost:8004/api/tts/audio/{audio_id}"
)

# Сохранение файла
with open("output.mp3", "wb") as f:
    f.write(audio_response.content)
```

### Пример 2: Использование кэша

```python
# Первый запрос (генерирует аудио)
response1 = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={"text": "Test caching", "language": "en"}
)

# Второй запрос (использует кэш, быстрее)
response2 = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={"text": "Test caching", "language": "en"}
)
```

### Пример 3: Разные провайдеры

```python
# Использование gTTS
response = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={
        "text": "Test",
        "language": "en",
        "provider": "gtts"
    }
)

# Использование pyttsx3 (офлайн)
response = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={
        "text": "Test",
        "language": "en",
        "provider": "pyttsx3"
    }
)

# Автоматический выбор (auto)
response = requests.post(
    "http://localhost:8004/api/tts/generate",
    json={
        "text": "Test",
        "language": "en",
        "provider": "auto"
    }
)
```

---

## 🔧 Конфигурация

### Environment Variables

```env
# TTS Configuration
TTS_PROVIDER=auto              # gtts, pyttsx3, or auto
TTS_CACHE_ENABLED=true         # Enable caching
TTS_FALLBACK_ENABLED=true      # Enable fallback to pyttsx3
TTS_CACHE_TTL_DAYS=30         # Cache TTL in days
TTS_MAX_TEXT_LENGTH=5000      # Maximum text length
```

### Провайдеры

1. **gTTS** (Google Text-to-Speech)
   - ✅ Требует интернет
   - ✅ Высокое качество
   - ✅ Поддержка ru, en

2. **pyttsx3** (Offline TTS)
   - ✅ Работает офлайн
   - ✅ Системные голоса
   - ✅ Поддержка ru, en (зависит от системы)

3. **auto** (Автоматический)
   - ✅ Пробует gTTS сначала
   - ✅ Fallback на pyttsx3 при ошибке

---

## 🐛 Устранение проблем

### Проблема: TTS не генерируется

**Решение:**
1. Проверьте интернет соединение (для gTTS)
2. Проверьте установку `gtts` и `pyttsx3`
3. Проверьте логи API

### Проблема: Аудио файл не воспроизводится

**Решение:**
1. Проверьте формат файла (должен быть MP3)
2. Проверьте размер файла (> 0)
3. Попробуйте другой аудио плеер

### Проблема: Кэш не работает

**Решение:**
1. Проверьте `TTS_CACHE_ENABLED=true`
2. Проверьте права на запись в `data/audio/tts/cache`
3. Проверьте логи

---

## 📊 Статистика и мониторинг

### Получение статистики

```bash
curl http://localhost:8004/api/tts/stats
```

**Метрики:**
- `cache_enabled` - Включен ли кэш
- `cache_size` - Количество файлов в кэше
- `cache_hits` - Количество попаданий в кэш
- `cache_misses` - Количество промахов кэша

---

## ✅ Чеклист тестирования

### Базовые тесты
- [ ] Генерация TTS для русского текста
- [ ] Генерация TTS для английского текста
- [ ] Получение аудио файла
- [ ] Проверка формата (MP3)
- [ ] Проверка размера файла

### Quality тесты
- [ ] Разные языки (ru, en)
- [ ] Разные голоса (male, female)
- [ ] Длинные тексты
- [ ] Специальные символы
- [ ] Unicode символы

### Performance тесты
- [ ] Время генерации
- [ ] Кэширование работает
- [ ] Параллельная генерация

### Integration тесты
- [ ] TTS + News Feed
- [ ] TTS + Email
- [ ] TTS + Telegram

---

## 📚 Дополнительная информация

### Скрипты для автоматизации

- `scripts/test_tts.ps1` - Автоматическое тестирование TTS
- `scripts/start_and_test_tts.ps1` - Запуск API + тесты
- `scripts/check_api.ps1` - Проверка состояния API

### Конфигурация

См. `SETUP_EMAIL_TELEGRAM.md` для настройки сервисов.

---

**Последнее обновление:** 2024  
**Статус:** ✅ Все тесты реализованы
