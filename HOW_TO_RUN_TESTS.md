# 🧪 How to Run Tests - Trendoscope2

## Обзор

Этот документ содержит примеры запуска всех тестов для Voice (TTS), Email и Telegram интеграций.

---

## 📋 Быстрый старт

### Запуск всех тестов Voice, Email, Telegram

```bash
cd trendoscope2
pytest tests/e2e/test_voice_email_telegram.py -v
```

**Ожидаемый результат:** 17 тестов должны пройти успешно.

---

## 🎯 Примеры запуска тестов

### 1. Все тесты (Voice + Email + Telegram)

```bash
# Полный запуск всех тестов
pytest tests/e2e/test_voice_email_telegram.py -v

# С подробным выводом
pytest tests/e2e/test_voice_email_telegram.py -v -s

# С минимальным выводом
pytest tests/e2e/test_voice_email_telegram.py -q
```

### 2. Только Voice (TTS) тесты

```bash
# Все TTS тесты
pytest tests/e2e/test_voice_email_telegram.py::TestVoiceTTS -v

# Конкретный тест
pytest tests/e2e/test_voice_email_telegram.py::TestVoiceTTS::test_tts_generate_russian -v
```

### 3. Только Email тесты

```bash
# Все Email тесты
pytest tests/e2e/test_voice_email_telegram.py::TestEmailService -v

# Конкретный тест
pytest tests/e2e/test_voice_email_telegram.py::TestEmailService::test_email_validation -v
```

### 4. Только Telegram тесты

```bash
# Все Telegram тесты
pytest tests/e2e/test_voice_email_telegram.py::TestTelegramService -v

# Конкретный тест
pytest tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_format_post_markdown -v
```

### 5. Интеграционные тесты

```bash
# Все интеграционные тесты
pytest tests/e2e/test_voice_email_telegram.py::TestIntegrations -v

# Комплексный тест
pytest tests/e2e/test_voice_email_telegram.py::test_all_services_comprehensive -v -s
```

---

## 🔍 Другие тесты проекта

### Валидация API

```bash
# Тесты валидации API
pytest tests/e2e/test_validation_e2e.py -v
```

### TTS тесты (старые)

```bash
# Полные TTS тесты
pytest tests/e2e/test_tts.py -v
```

### Минимальная настройка

```bash
# Тесты минимальной настройки
pytest tests/e2e/test_minimal_setup.py -v
```

### Production stack

```bash
# Тесты production stack
pytest tests/e2e/test_prod_stack.py -v
```

---

## 📊 Параметры pytest

### Полезные флаги

```bash
# -v, --verbose          Подробный вывод
# -s, --capture=no       Показать print() вывод
# -q, --quiet            Минимальный вывод
# -x, --exitfirst        Остановиться на первой ошибке
# --tb=short             Короткий traceback
# --tb=line               Одна строка на ошибку
# --tb=no                 Без traceback
# -k EXPRESSION          Запустить тесты, соответствующие выражению
# -m MARKEXPR            Запустить тесты с маркером
# --maxfail=N            Остановиться после N ошибок
```

### Примеры с параметрами

```bash
# Остановиться на первой ошибке
pytest tests/e2e/test_voice_email_telegram.py -v -x

# Запустить только тесты с "email" в названии
pytest tests/e2e/test_voice_email_telegram.py -v -k "email"

# Запустить только тесты с "tts" в названии
pytest tests/e2e/test_voice_email_telegram.py -v -k "tts"

# Запустить только тесты с "telegram" в названии
pytest tests/e2e/test_voice_email_telegram.py -v -k "telegram"

# С coverage отчетом
pytest tests/e2e/test_voice_email_telegram.py --cov=trendoscope2 --cov-report=html

# С HTML отчетом
pytest tests/e2e/test_voice_email_telegram.py --html=report.html --self-contained-html
```

---

## 🐛 Отладка тестов

### Запуск с отладкой

```bash
# С максимальным выводом
pytest tests/e2e/test_voice_email_telegram.py -v -s --tb=long

# Остановиться на первой ошибке с подробным выводом
pytest tests/e2e/test_voice_email_telegram.py -v -s -x --tb=long

# Запустить конкретный тест с отладкой
pytest tests/e2e/test_voice_email_telegram.py::TestVoiceTTS::test_tts_generate_russian -v -s
```

### Использование pdb

```bash
# Остановиться на ошибке с pdb
pytest tests/e2e/test_voice_email_telegram.py --pdb

# Остановиться на первой ошибке с pdb
pytest tests/e2e/test_voice_email_telegram.py -x --pdb
```

---

## 📈 Coverage отчеты

### Генерация coverage отчета

```bash
# Текстовый отчет
pytest tests/e2e/test_voice_email_telegram.py --cov=trendoscope2 --cov-report=term

# HTML отчет
pytest tests/e2e/test_voice_email_telegram.py --cov=trendoscope2 --cov-report=html

# XML отчет (для CI/CD)
pytest tests/e2e/test_voice_email_telegram.py --cov=trendoscope2 --cov-report=xml
```

После генерации HTML отчета, откройте `htmlcov/index.html` в браузере.

---

## ⚡ Быстрые команды

### PowerShell (Windows)

```powershell
# Все тесты Voice, Email, Telegram
cd trendoscope2
pytest tests/e2e/test_voice_email_telegram.py -v

# Только Voice
pytest tests/e2e/test_voice_email_telegram.py::TestVoiceTTS -v

# Только Email
pytest tests/e2e/test_voice_email_telegram.py::TestEmailService -v

# Только Telegram
pytest tests/e2e/test_voice_email_telegram.py::TestTelegramService -v

# Комплексный тест с выводом
pytest tests/e2e/test_voice_email_telegram.py::test_all_services_comprehensive -v -s
```

### Bash (Linux/Mac)

```bash
# Все тесты Voice, Email, Telegram
cd trendoscope2
pytest tests/e2e/test_voice_email_telegram.py -v

# Только Voice
pytest tests/e2e/test_voice_email_telegram.py::TestVoiceTTS -v

# Только Email
pytest tests/e2e/test_voice_email_telegram.py::TestEmailService -v

# Только Telegram
pytest tests/e2e/test_voice_email_telegram.py::TestTelegramService -v

# Комплексный тест с выводом
pytest tests/e2e/test_voice_email_telegram.py::test_all_services_comprehensive -v -s
```

---

## 📝 Ожидаемые результаты

### Успешный запуск

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.0.2
collected 17 items

tests/e2e/test_voice_email_telegram.py::TestVoiceTTS::test_tts_generate_russian PASSED
tests/e2e/test_voice_email_telegram.py::TestVoiceTTS::test_tts_generate_english PASSED
tests/e2e/test_voice_email_telegram.py::TestVoiceTTS::test_tts_audio_download PASSED
tests/e2e/test_voice_email_telegram.py::TestEmailService::test_email_validation PASSED
tests/e2e/test_voice_email_telegram.py::TestEmailService::test_email_service_initialization PASSED
tests/e2e/test_voice_email_telegram.py::TestEmailService::test_send_email_success PASSED
tests/e2e/test_voice_email_telegram.py::TestEmailService::test_format_digest_html PASSED
tests/e2e/test_voice_email_telegram.py::TestEmailService::test_format_digest_text PASSED
tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_telegram_service_initialization PASSED
tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_format_post_markdown PASSED
tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_format_post_html PASSED
tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_format_post_plain PASSED
tests/e2e/test_voice_email_telegram.py::TestTelegramService::test_format_post_truncation PASSED
tests/e2e/test_voice_email_telegram.py::TestIntegrations::test_tts_and_email_integration PASSED
tests/e2e/test_voice_email_telegram.py::TestIntegrations::test_tts_and_telegram_integration PASSED
tests/e2e/test_voice_email_telegram.py::TestIntegrations::test_telegram_connection_test PASSED
tests/e2e/test_voice_email_telegram.py::test_all_services_comprehensive PASSED

======================== 17 passed in 8.62s ========================
```

---

## 🔧 Устранение проблем

### Проблема: ModuleNotFoundError

```bash
# Убедитесь, что вы в правильной директории
cd trendoscope2

# Установите зависимости
pip install -r requirements.txt
```

### Проблема: Тесты не находят модули

```bash
# Убедитесь, что src в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
$env:PYTHONPATH = "$(pwd)/src"  # PowerShell
```

### Проблема: API не запущен

Тесты используют `TestClient`, поэтому API не нужно запускать отдельно.

---

## 📚 Дополнительная информация

- **Файл тестов:** `tests/e2e/test_voice_email_telegram.py`
- **Результаты тестов:** `TESTING_VOICE_EMAIL_TELEGRAM_RESULTS.md`
- **План тестирования:** `TESTING_PLAN_VOICE_EMAIL_TELEGRAM.md`

---

**Последнее обновление:** 2024
