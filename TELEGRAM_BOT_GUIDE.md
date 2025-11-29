# 📱 Telegram Bot Setup Guide

**Goal**: Create @TrendscopeBot to deliver hot news directly to users  
**Time**: 2-3 hours  
**Difficulty**: Easy

---

## 🚀 Step-by-Step Instructions

### **Step 1: Create Bot with BotFather** (5 minutes)

1. **Open Telegram** on your phone or desktop

2. **Search for** `@BotFather` (official bot with blue checkmark)

3. **Start conversation**: Click "Start" or type `/start`

4. **Create new bot**: Type `/newbot`

5. **Choose name**: 
   ```
   BotFather: Alright, a new bot. How are we going to call it? 
              Please choose a name for your bot.
   
   You: Trendoscope News
   ```

6. **Choose username** (must end with 'bot'):
   ```
   BotFather: Good. Now let's choose a username for your bot. 
              It must end in `bot`. Like this, for example: 
              TetrisBot or tetris_bot.
   
   You: TrendscopeBot
   ```

7. **Get your token**:
   ```
   BotFather: Done! Congratulations on your new bot. 
              You will find it at t.me/TrendscopeBot. 
              You can now add a description...
   
              Use this token to access the HTTP API:
              1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   
              Keep your token secure and store it safely...
   ```

8. **SAVE THE TOKEN!** Copy it to a safe place. You'll need it.

---

### **Step 2: Customize Bot** (5 minutes)

While still talking to @BotFather:

1. **Set description** (shown when user opens bot):
   ```
   /setdescription
   Select: @TrendscopeBot
   
   Type:
   🔥 Провокационные новости из 40+ источников
   
   ✅ Самые спорные новости дня
   ✅ Метр провокационности (0-100%)
   ✅ Фильтр по категориям
   ✅ Ежедневный дайджест
   ```

2. **Set about text** (shown in bot profile):
   ```
   /setabouttext
   Select: @TrendscopeBot
   
   Type:
   Агрегатор провокационных новостей с AI-оценкой спорности каждой новости
   ```

3. **Set profile picture**:
   ```
   /setuserpic
   Select: @TrendscopeBot
   Upload: logo image (512x512 PNG)
   ```

4. **Set commands** (shown in menu):
   ```
   /setcommands
   Select: @TrendscopeBot
   
   Type:
   start - Начать работу с ботом
   hot - Топ-5 провокационных новостей
   tech - Технологии и AI
   politics - Политика
   business - Экономика
   subscribe - Подписаться на дайджест
   unsubscribe - Отписаться от дайджеста
   help - Помощь
   ```

---

### **Step 3: Install Python Library** (2 minutes)

Open terminal/PowerShell:

```bash
cd trendascope
pip install python-telegram-bot --upgrade
```

---

### **Step 4: Create Bot File** (30 minutes)

Create `telegram_bot.py` in `trendascope` folder:

```python
import os
import asyncio
import logging
from datetime import time
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"  # Replace with your token from Step 1
API_URL = "http://localhost:8003"

# Store subscribers (in production, use database)
subscribers = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🔥 Добро пожаловать в Trendoscope!\n\n"
        "Я показываю самые провокационные новости с оценкой спорности.\n\n"
        "Команды:\n"
        "/hot - Топ-5 провокационных новостей\n"
        "/tech - Новости технологий\n"
        "/politics - Политические новости\n"
        "/business - Экономика и бизнес\n"
        "/subscribe - Подписаться на ежедневный дайджест\n"
        "/help - Помощь\n\n"
        "Просто отправьте /hot чтобы начать! 🚀"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🔥 *Trendoscope Bot Помощь*\n\n"
        "*Команды:*\n"
        "/hot - Топ-5 самых спорных новостей\n"
        "/tech - Технологии, AI, ML\n"
        "/politics - Политика, выборы, власть\n"
        "/business - Экономика, рынки, стартапы\n"
        "/subscribe - Ежедневный дайджест в 8:00\n"
        "/unsubscribe - Отписаться от дайджеста\n\n"
        "*Метр провокационности:*\n"
        "💥 90-100% - Взрывные\n"
        "🔥 70-89% - Горячие\n"
        "🌶️ 50-69% - Острые\n"
        "📰 0-49% - Спокойные\n\n"
        "Вопросы? Пишите @your_username",
        parse_mode='Markdown'
    )


async def hot_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get top 5 most controversial news"""
    await update.message.reply_text("🔍 Ищу самые провокационные новости...")
    
    try:
        # Fetch from API
        response = requests.get(f'{API_URL}/api/news/feed?category=all&limit=20')
        data = response.json()
        
        if not data['success'] or not data['news']:
            await update.message.reply_text(
                "❌ Не удалось загрузить новости. Попробуйте позже."
            )
            return
        
        # Get top 5 by controversy score
        news_items = sorted(
            data['news'], 
            key=lambda x: x['controversy']['score'], 
            reverse=True
        )[:5]
        
        message = "🔥 *ТОП-5 ПРОВОКАЦИОННЫХ НОВОСТЕЙ:*\n\n"
        
        for i, item in enumerate(news_items, 1):
            score = item['controversy']['score']
            emoji = item['controversy']['emoji']
            title = item['title']
            link = item['link']
            source = item['source']
            
            message += f"{i}. {emoji} *{score}%* - {title}\n"
            message += f"   _Источник: {source}_\n"
            message += f"   [Читать полностью]({link})\n\n"
        
        message += "🔄 /hot - Обновить список"
        
        await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        await update.message.reply_text(
            "❌ Ошибка при загрузке новостей. Убедитесь, что сервер запущен."
        )


async def tech_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get tech news"""
    await send_category_news(update, 'tech', '🤖 Технологии и AI')


async def politics_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get politics news"""
    await send_category_news(update, 'politics', '🏛️ Политика')


async def business_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get business news"""
    await send_category_news(update, 'business', '💼 Экономика')


async def send_category_news(update: Update, category: str, title: str):
    """Helper to send news by category"""
    await update.message.reply_text(f"🔍 Загружаю новости: {title}...")
    
    try:
        response = requests.get(f'{API_URL}/api/news/feed?category={category}&limit=10')
        data = response.json()
        
        if not data['success'] or not data['news']:
            await update.message.reply_text(
                f"❌ Нет новостей в категории {title}"
            )
            return
        
        # Get top 5
        news_items = data['news'][:5]
        
        message = f"*{title}*\n\n"
        
        for i, item in enumerate(news_items, 1):
            score = item['controversy']['score']
            emoji = item['controversy']['emoji']
            title_text = item['title']
            link = item['link']
            
            message += f"{i}. {emoji} *{score}%* - {title_text}\n"
            message += f"   [Читать]({link})\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Ошибка загрузки")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to daily digest"""
    user_id = update.effective_user.id
    subscribers.add(user_id)
    
    await update.message.reply_text(
        "✅ Вы подписаны на ежедневный дайджест!\n\n"
        "Будете получать топ-5 провокационных новостей каждый день в 8:00 по Москве.\n\n"
        "/unsubscribe - Отписаться"
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from daily digest"""
    user_id = update.effective_user.id
    subscribers.discard(user_id)
    
    await update.message.reply_text(
        "✅ Вы отписаны от дайджеста.\n\n"
        "Команды работают как обычно!\n\n"
        "/subscribe - Подписаться снова"
    )


async def send_daily_digest(context: ContextTypes.DEFAULT_TYPE):
    """Send daily digest to all subscribers"""
    try:
        # Fetch top news
        response = requests.get(f'{API_URL}/api/news/feed?category=all&limit=20')
        data = response.json()
        
        if not data['success'] or not data['news']:
            logger.error("Failed to fetch news for digest")
            return
        
        # Get top 5
        news_items = sorted(
            data['news'], 
            key=lambda x: x['controversy']['score'], 
            reverse=True
        )[:5]
        
        message = "🔥 *ДАЙДЖЕСТ ДНЯ*\n"
        message += "_Топ-5 провокационных новостей:_\n\n"
        
        for i, item in enumerate(news_items, 1):
            score = item['controversy']['score']
            emoji = item['controversy']['emoji']
            title = item['title']
            link = item['link']
            
            message += f"{i}. {emoji} *{score}%*\n{title}\n[→]({link})\n\n"
        
        message += "———————————\n"
        message += "📱 [Открыть Trendoscope](http://localhost:8003/static/news_feed_full.html)\n"
        message += "/unsubscribe - Отписаться"
        
        # Send to all subscribers
        for user_id in subscribers:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
        
        logger.info(f"Digest sent to {len(subscribers)} subscribers")
        
    except Exception as e:
        logger.error(f"Error in daily digest: {e}")


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hot", hot_news))
    application.add_handler(CommandHandler("tech", tech_news))
    application.add_handler(CommandHandler("politics", politics_news))
    application.add_handler(CommandHandler("business", business_news))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    
    # Schedule daily digest at 8:00 Moscow time (UTC+3)
    job_queue = application.job_queue
    job_queue.run_daily(
        send_daily_digest,
        time=time(hour=5, minute=0),  # 8:00 Moscow = 5:00 UTC
        days=(0, 1, 2, 3, 4, 5, 6)     # Every day
    )
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
```

**Important**: Replace `YOUR_TOKEN_HERE` with your actual token from Step 1!

---

### **Step 5: Test Bot Locally** (10 minutes)

1. **Make sure your web server is running**:
   ```bash
   # In one terminal
   python run.py
   ```

2. **Start the bot** (in another terminal):
   ```bash
   python telegram_bot.py
   ```

3. **Test in Telegram**:
   - Open Telegram
   - Search for your bot (`@TrendscopeBot`)
   - Click "Start"
   - Try commands:
     - `/start`
     - `/hot`
     - `/tech`
     - `/subscribe`

4. **Check terminal** for logs and errors

---

### **Step 6: Deploy Bot** (30 minutes)

#### **Option A: Run on Your Server** (Easiest)

```bash
# Install screen or tmux
sudo apt install screen

# Start screen session
screen -S trendoscope-bot

# Run bot
python telegram_bot.py

# Detach: Ctrl+A, then D
# Reattach: screen -r trendoscope-bot
```

#### **Option B: Use systemd** (Production)

Create `/etc/systemd/system/trendoscope-bot.service`:

```ini
[Unit]
Description=Trendoscope Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/trendoscope
ExecStart=/usr/bin/python3 /path/to/trendoscope/telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable trendoscope-bot
sudo systemctl start trendoscope-bot
sudo systemctl status trendoscope-bot
```

#### **Option C: Use PM2** (Node.js process manager)

```bash
npm install -g pm2
pm2 start telegram_bot.py --name trendoscope-bot --interpreter python3
pm2 save
pm2 startup
```

---

## 🎯 Next Steps

### **1. Add Inline Buttons** (Advanced)

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def hot_news_with_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔄 Обновить", callback_data='refresh'),
            InlineKeyboardButton("📱 Поделиться", switch_inline_query='hot_news')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "News here...",
        reply_markup=reply_markup
    )
```

### **2. Store Subscribers in Database**

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers
                 (user_id INTEGER PRIMARY KEY, subscribed_at TEXT)''')
    conn.commit()
    conn.close()

def add_subscriber(user_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO subscribers VALUES (?, datetime("now"))',
              (user_id,))
    conn.commit()
    conn.close()
```

### **3. Add Analytics**

```python
import logging

logger.info(f"User {user_id} requested /hot")
# Track most used commands
# Track popular categories
# Track sharing
```

---

## 📈 Promotion Strategy

### **1. Announce on Social Media**

**Telegram Channels** (ask admins):
```
🔥 Запустил бота для провокационных новостей!

@TrendscopeBot - показывает только самые спорные новости с оценкой провокационности (0-100%)

Что умеет:
✅ Топ-5 горячих новостей
✅ Фильтр по категориям (Tech, Politics, Business)
✅ Ежедневный дайджест в 8:00
✅ Бесплатно и без рекламы

Попробовать: @TrendscopeBot

#новости #telegram #бот
```

**Twitter**:
```
🔥 Launched @TrendscopeBot - delivers most controversial news with controversy score (0-100%)

Features:
✅ Top 5 hot news on demand
✅ Category filters
✅ Daily digest
✅ Free

Try: t.me/TrendscopeBot

#TelegramBot #News #AI
```

### **2. Create Channel**

1. Create `@TrendscopeNews` channel
2. Auto-post hot news every hour
3. Link to bot in channel description
4. Bot promotes channel

### **3. Add to Bot Lists**

- https://tlgrm.ru/bots
- https://combot.org/telegram/bots
- https://botlist.co/

---

## 🐛 Troubleshooting

### **Problem**: "Unauthorized" error

**Solution**: Check your token is correct

### **Problem**: Bot doesn't respond

**Solution**: 
1. Check bot is running (`python telegram_bot.py`)
2. Check web server is running (`python run.py`)
3. Check firewall/ports

### **Problem**: "Connection error" in bot

**Solution**: Make sure API_URL is correct and server is accessible

### **Problem**: Daily digest not sending

**Solution**: Check timezone (Moscow = UTC+3, so use hour=5)

---

## 📊 Expected Results

**Week 1**: 50-100 subscribers  
**Week 2**: 200-300 subscribers  
**Month 1**: 500-1000 subscribers  

**Engagement**:
- 40% daily active users
- `/hot` most popular command
- Morning digest has 60% open rate

---

## ✅ Checklist

- [ ] Created bot with BotFather
- [ ] Saved token securely
- [ ] Set description and commands
- [ ] Installed python-telegram-bot
- [ ] Created telegram_bot.py
- [ ] Replaced token in code
- [ ] Tested locally
- [ ] Deployed to server
- [ ] Announced on social media
- [ ] Added to bot directories

---

## 🎉 You're Done!

Your Telegram bot is now live! 🚀

**Share it**:
- t.me/YourBotName
- Add link to website
- Post on social media
- Tell friends

**Monitor**:
- Check logs daily
- Read user feedback
- Track command usage
- Iterate and improve

---

**Questions?** Check the logs or ask in the community!

Good luck with your bot! 📱🔥

