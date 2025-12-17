# 🔧 Setup Guide: Email & Telegram Configuration

## Пошаговые инструкции по настройке Email и Telegram

---

## 📧 Часть 1: Настройка Email (SMTP)

### Шаг 1: Выберите SMTP провайдера

**Рекомендуемые бесплатные варианты:**

1. **Gmail** (рекомендуется для начала)
   - SMTP Host: `smtp.gmail.com`
   - SMTP Port: `587` (TLS) или `465` (SSL)
   - Требуется: App Password (не обычный пароль)

2. **Outlook/Hotmail**
   - SMTP Host: `smtp-mail.outlook.com`
   - SMTP Port: `587`
   - Требуется: App Password

3. **Yahoo Mail**
   - SMTP Host: `smtp.mail.yahoo.com`
   - SMTP Port: `587`
   - Требуется: App Password

4. **Другие провайдеры**
   - Проверьте документацию вашего email провайдера

---

### Шаг 2: Настройка Gmail (пример)

#### 2.1. Включите двухфакторную аутентификацию

1. Откройте [Google Account](https://myaccount.google.com/)
2. Перейдите в **Security** (Безопасность)
3. Включите **2-Step Verification** (Двухэтапная аутентификация)
4. Следуйте инструкциям для настройки

#### 2.2. Создайте App Password

1. В том же разделе **Security** найдите **App passwords** (Пароли приложений)
2. Нажмите **Select app** → выберите **Mail**
3. Нажмите **Select device** → выберите **Other (Custom name)**
4. Введите название: `Trendoscope2`
5. Нажмите **Generate**
6. **Скопируйте 16-значный пароль** (он показывается только один раз!)

**Важно:** Используйте этот App Password, а не ваш обычный пароль Gmail.

---

### Шаг 3: Создайте файл .env

1. Перейдите в директорию проекта:
   ```bash
   cd trendoscope2
   ```

2. Создайте файл `.env` (если его нет):
   ```bash
   # Windows PowerShell
   New-Item .env -ItemType File
   
   # Linux/Mac
   touch .env
   ```

3. **Альтернатива:** Скопируйте шаблон:
   ```bash
   # Windows PowerShell
   Copy-Item env_template.txt .env
   
   # Linux/Mac
   cp env_template.txt .env
   ```

4. Откройте файл `.env` в текстовом редакторе

---

### Шаг 4: Добавьте Email конфигурацию в .env

Добавьте следующие строки в файл `.env`:

```env
# Email Configuration (Gmail example)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_16_digit_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_ENABLED=true
```

**Пример заполнения:**
```env
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=trendoscope@gmail.com
EMAIL_SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=trendoscope@gmail.com
EMAIL_ENABLED=true
```

**Важно:**
- Замените `your_email@gmail.com` на ваш реальный email
- Замените `your_16_digit_app_password` на App Password из шага 2.2
- Не используйте пробелы в App Password (удалите их)

---

### Шаг 5: Проверка Email настройки

#### 5.1. Проверьте статус сервиса

Запустите API и проверьте статус:
```bash
# Запустите API
python run.py

# В другом терминале проверьте статус
curl http://localhost:8004/api/email/status
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "enabled": true,
  "configured": true
}
```

#### 5.2. Отправьте тестовый email

```bash
curl -X POST http://localhost:8004/api/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "recipient@example.com",
    "subject": "Test Email",
    "text_content": "This is a test email from Trendoscope2"
  }'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

---

### Шаг 6: Настройка для других провайдеров

#### Outlook/Hotmail

```env
EMAIL_SMTP_HOST=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@outlook.com
EMAIL_SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@outlook.com
EMAIL_ENABLED=true
```

#### Yahoo Mail

```env
EMAIL_SMTP_HOST=smtp.mail.yahoo.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@yahoo.com
EMAIL_SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@yahoo.com
EMAIL_ENABLED=true
```

---

## 📱 Часть 2: Настройка Telegram

### Шаг 1: Создайте Telegram бота

1. Откройте Telegram и найдите **@BotFather**
2. Начните диалог: `/start`
3. Создайте нового бота: `/newbot`
4. Введите имя бота (например: `Trendoscope News Bot`)
5. Введите username бота (должен заканчиваться на `bot`, например: `trendoscope_news_bot`)
6. **Скопируйте токен**, который даст вам BotFather

**Пример ответа BotFather:**
```
Done! Congratulations on your new bot. You will find it at t.me/trendoscope_news_bot. Use this token to access the HTTP API:

123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**Важно:** Сохраните токен в безопасном месте!

---

### Шаг 2: Создайте Telegram канал

1. Откройте Telegram
2. Нажмите **New Channel** (Новый канал)
3. Введите название канала (например: `Trendoscope News`)
4. Введите описание (опционально)
5. Выберите тип: **Public** (публичный) или **Private** (приватный)
6. Если публичный, введите username (например: `@trendoscope_news`)
7. Нажмите **Create** (Создать)

---

### Шаг 3: Добавьте бота как администратора канала

1. Откройте созданный канал
2. Нажмите на название канала вверху
3. Перейдите в **Administrators** (Администраторы)
4. Нажмите **Add Administrator** (Добавить администратора)
5. Найдите вашего бота по username (например: `@trendoscope_news_bot`)
6. Выберите бота
7. Дайте права:
   - ✅ **Post Messages** (Публиковать сообщения) - обязательно!
   - ✅ **Edit Messages** (Редактировать сообщения) - опционально
   - ✅ **Delete Messages** (Удалять сообщения) - опционально
8. Нажмите **Done** (Готово)

---

### Шаг 4: Получите Channel ID

#### Вариант A: Публичный канал

Если канал публичный, используйте username с `@`:
```
@trendoscope_news
```

#### Вариант B: Приватный канал

Для приватного канала нужно получить числовой ID:

1. Добавьте бота в канал (если еще не добавили)
2. Отправьте любое сообщение в канал
3. Используйте этот URL (замените `YOUR_BOT_TOKEN` на ваш токен):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Найдите в ответе `"chat":{"id":-1001234567890}` - это ваш Channel ID
5. Используйте его как: `-1001234567890`

**Пример ответа API:**
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "channel_post": {
        "chat": {
          "id": -1001234567890,
          "title": "Trendoscope News",
          "type": "channel"
        },
        "message_id": 1,
        "text": "Test message"
      }
    }
  ]
}
```

В этом случае Channel ID = `-1001234567890`

---

### Шаг 5: Добавьте Telegram конфигурацию в .env

Откройте файл `.env` и добавьте:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
TELEGRAM_MAX_POST_LENGTH=4096
```

**Пример заполнения:**
```env
# Для публичного канала
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
TELEGRAM_MAX_POST_LENGTH=4096

# ИЛИ для приватного канала
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
TELEGRAM_MAX_POST_LENGTH=4096
```

**Важно:**
- Замените `123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890` на ваш реальный токен
- Замените `@trendoscope_news` на username вашего канала (или используйте числовой ID)

---

### Шаг 6: Установите python-telegram-bot

```bash
pip install python-telegram-bot>=20.7
```

Или установите все зависимости:
```bash
pip install -r requirements.txt
```

---

### Шаг 7: Проверка Telegram настройки

#### 7.1. Проверьте статус сервиса

```bash
# Запустите API
python run.py

# В другом терминале проверьте статус
curl http://localhost:8004/api/telegram/status
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "enabled": true,
  "configured": true,
  "default_channel": "@trendoscope_news"
}
```

#### 7.2. Протестируйте подключение

```bash
curl http://localhost:8004/api/telegram/test
```

**Ожидаемый ответ (успех):**
```json
{
  "success": true,
  "message": "Connected successfully",
  "available": true
}
```

**Ожидаемый ответ (ошибка):**
```json
{
  "success": false,
  "message": "Connection failed",
  "available": true
}
```

Если ошибка, проверьте:
- Правильность токена
- Бот добавлен как администратор канала
- Правильность Channel ID

#### 7.3. Отправьте тестовый пост

```bash
curl -X POST http://localhost:8004/api/telegram/post \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "title": "Test News Article",
      "summary": "This is a test article from Trendoscope2",
      "link": "http://example.com/article"
    },
    "format_type": "markdown"
  }'
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "message": "Posted to Telegram successfully"
}
```

Проверьте ваш Telegram канал - должен появиться пост!

---

## 📋 Полный пример .env файла

```env
# ============================================
# Email Configuration (Gmail)
# ============================================
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=trendoscope@gmail.com
EMAIL_SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=trendoscope@gmail.com
EMAIL_ENABLED=true

# ============================================
# Telegram Configuration
# ============================================
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
TELEGRAM_MAX_POST_LENGTH=4096

# ============================================
# Other Configuration (existing)
# ============================================
TTS_PROVIDER=auto
TTS_CACHE_ENABLED=true
LOG_LEVEL=INFO
```

---

## 🔒 Безопасность

### ⚠️ Важные предупреждения

1. **НЕ коммитьте .env файл в Git!**
   - Убедитесь, что `.env` в `.gitignore`
   - Используйте `.env.example` для шаблона

2. **Храните токены в безопасности**
   - Не делитесь токенами
   - Не публикуйте их в коде
   - Используйте переменные окружения в production

3. **Используйте App Passwords**
   - Не используйте основной пароль email
   - Создавайте отдельные App Passwords для каждого приложения

---

## 🐛 Устранение проблем

### Email не отправляется

1. **Проверьте App Password**
   - Убедитесь, что используете App Password, а не обычный пароль
   - Проверьте, что 2FA включена

2. **Проверьте SMTP настройки**
   - Убедитесь, что порт правильный (587 для TLS, 465 для SSL)
   - Проверьте, что хост правильный

3. **Проверьте логи**
   ```bash
   # Запустите API с подробными логами
   LOG_LEVEL=DEBUG python run.py
   ```

### Telegram не работает

1. **Проверьте токен**
   - Убедитесь, что токен правильный
   - Проверьте, что бот активен

2. **Проверьте права бота**
   - Убедитесь, что бот добавлен как администратор
   - Проверьте, что у бота есть право "Post Messages"

3. **Проверьте Channel ID**
   - Для публичного канала используйте `@username`
   - Для приватного канала используйте числовой ID (начинается с `-100`)

4. **Проверьте библиотеку**
   ```bash
   pip install python-telegram-bot>=20.7
   ```

---

## ✅ Чеклист настройки

### Email
- [ ] Выбран SMTP провайдер
- [ ] Включена 2FA (для Gmail)
- [ ] Создан App Password
- [ ] Добавлены настройки в `.env`
- [ ] Проверен статус сервиса
- [ ] Отправлен тестовый email

### Telegram
- [ ] Создан бот через @BotFather
- [ ] Сохранен токен бота
- [ ] Создан канал
- [ ] Бот добавлен как администратор канала
- [ ] Получен Channel ID
- [ ] Добавлены настройки в `.env`
- [ ] Установлен python-telegram-bot
- [ ] Проверен статус сервиса
- [ ] Протестировано подключение
- [ ] Отправлен тестовый пост

---

## 📚 Дополнительные ресурсы

- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **python-telegram-bot:** https://python-telegram-bot.org/

---

**Последнее обновление:** 2024
