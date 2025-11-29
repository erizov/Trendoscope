# ⚡ Quick Growth Plan - Start Today!

**Goal**: Get your first 1,000 users in 30 days  
**Focus**: Top 5 highest-impact, lowest-effort tactics

---

## 🎯 Top 5 Priorities (In Order)

### **1. Telegram Bot** 🤖 ⭐⭐⭐⭐⭐
**Why**: 70% of Russians use Telegram. Instant distribution.  
**Time**: 1-2 days  
**Impact**: 500+ users in first month

**Implementation**:
```bash
pip install python-telegram-bot

# Create bot: @BotFather on Telegram
# Get token
# Create bot.py
```

**Features to add**:
- `/start` - Subscribe to hot news
- `/hot` - Get 5 most controversial news now
- `/tech`, `/politics` - Category-specific
- Daily digest at 8am Moscow time
- Share button creates Telegram post

**Growth hack**: 
- Post in tech Telegram channels (ask permission)
- Share in your network
- "Invite 3 friends → unlock premium"

**Expected**: 100 users week 1, 500 by month 1

---

### **2. Social Sharing Buttons** 📤 ⭐⭐⭐⭐⭐
**Why**: Viral growth. Each user brings 2-3 more.  
**Time**: 2-3 hours  
**Impact**: 3x user growth

**Add to each news card**:
```html
<!-- Beautiful share preview -->
<meta property="og:title" content="[News Title]">
<meta property="og:description" content="[Summary]">
<meta property="og:image" content="[Auto-generated card]">

<!-- Share buttons -->
[📱 Telegram] [📘 VK] [🐦 Twitter] [📋 Copy]
```

**Auto-generate share images**:
```python
from PIL import Image, ImageDraw, ImageFont

def create_share_image(title, controversy_score, category):
    # Create 1200x630 image
    # Add gradient background
    # Add title (big font)
    # Add controversy meter
    # Add logo + category icon
    # Save to /static/share/{news_id}.jpg
```

**Growth hack**:
- "Share to unlock full text" (soft gate)
- Track who shares most (leaderboard)
- Reward top sharers

**Expected**: Each user shares 0.5 times → viral coefficient 1.5

---

### **3. Controversy Leaderboard** 🔥 ⭐⭐⭐⭐⭐
**Why**: Shareable, unique, fun  
**Time**: 3-4 hours  
**Impact**: Increases engagement 2x

**Add to homepage**:
```
🔥 САМЫЕ ПРОВОКАЦИОННЫЕ НОВОСТИ НЕДЕЛИ

1. 💥 94% "Трамп начинает войну с..."
2. 🔥 89% "GPT-5 заменит программистов"
3. 🔥 87% "Санкции провалились?"
4. 🌶️  78% "Байден vs Путин: кто прав?"
5. 🌶️  76% "Крипта возвращается"

[📤 Share Leaderboard]
```

**Growth hack**:
- Update daily (creates urgency)
- "You read #2 most controversial news!"
- Weekly "Controversy King" badge

**Expected**: 30% of users share leaderboard

---

### **4. Email Daily Digest** 📧 ⭐⭐⭐⭐
**Why**: Direct channel, high engagement  
**Time**: 1 day  
**Impact**: 40% retention boost

**Setup**:
```bash
pip install sendgrid  # or mailchimp

# Add email signup form
# Send daily at 6am Moscow time
```

**Email format**:
```
Subject: 🔥 5 самых провокационных новостей дня

Привет! Вот что взорвало интернет за последние 24 часа:

1. 💥 [94%] GPT-5 released: программисты в шоке
   [Summary 100 chars]
   [Read more →]

2. 🔥 [89%] Трамп vs Байден: кто победит?
   ...

[View all on Trendoscope →]

---
Не нравятся письма? [Unsubscribe]
```

**Growth hack**:
- "Invite friend → both get week of Premium"
- Forward-to-friend button
- "This newsletter saved me 2 hours of scrolling"

**Expected**: 60% open rate, 15% click rate

---

### **5. Chrome Extension** 🔌 ⭐⭐⭐⭐
**Why**: Always visible, sticky  
**Time**: 2 days  
**Impact**: 10x engagement

**Features**:
```javascript
// manifest.json
{
  "name": "Trendoscope News",
  "version": "1.0",
  "permissions": ["storage", "notifications"],
  "action": {
    "default_popup": "popup.html"
  }
}

// popup.html - Show 5 hot news
// badge.js - Update count of unread
// newtab.html - Replace new tab with news
```

**Growth hack**:
- "Installed by 1,000+ developers"
- Post on Habr, Reddit r/webdev
- Chrome Web Store SEO

**Expected**: 200 installs first month

---

## 📅 2-Week Sprint Plan

### **Week 1: Foundation**

**Day 1-2: Telegram Bot**
- [ ] Create bot with BotFather
- [ ] Implement `/start`, `/hot`, `/tech`
- [ ] Add daily digest
- [ ] Test with 10 friends

**Day 3: Social Sharing**
- [ ] Add Open Graph meta tags
- [ ] Add share buttons
- [ ] Test on Telegram, VK, Twitter

**Day 4: Share Image Generator**
- [ ] Create auto-image script
- [ ] Design template
- [ ] Test 10 examples

**Day 5: Controversy Leaderboard**
- [ ] Add to homepage
- [ ] Update algorithm
- [ ] Add share button

**Day 6-7: Email Setup**
- [ ] Choose email provider
- [ ] Design email template
- [ ] Set up automation
- [ ] Test send

### **Week 2: Launch & Promote**

**Day 8: Chrome Extension**
- [ ] Create manifest
- [ ] Build popup
- [ ] Test locally

**Day 9: Extension Polish**
- [ ] Add new tab page
- [ ] Add notifications
- [ ] Submit to Chrome Store

**Day 10-11: Content Creation**
- [ ] Write "How Trendoscope Works" blog post
- [ ] Create demo video
- [ ] Design infographics

**Day 12-13: Launch!**
- [ ] Post on Habr
- [ ] Share on Reddit
- [ ] Post in Telegram channels
- [ ] Share on Twitter
- [ ] Email tech bloggers

**Day 14: Analyze & Iterate**
- [ ] Review metrics
- [ ] Read feedback
- [ ] Plan next sprint

---

## 🎯 Success Metrics

**Week 1 Goals**:
- ✅ Telegram bot: 50 subscribers
- ✅ Email list: 30 signups
- ✅ Extension: MVP ready

**Week 2 Goals**:
- ✅ Total users: 200
- ✅ Daily active: 50
- ✅ Shares: 20/day

**Month 1 Goals**:
- ✅ Total users: 1,000
- ✅ Telegram: 500 subscribers
- ✅ Email: 200 subscribers
- ✅ Extension: 100 installs
- ✅ DAU/MAU: 30%

---

## 📢 Distribution Checklist

**Free Channels**:
- [ ] Habr (post article)
- [ ] VC.ru (startup story)
- [ ] Reddit r/russia, r/webdev
- [ ] Telegram channels (ask admins)
- [ ] Twitter tech community
- [ ] VK tech groups
- [ ] LinkedIn post
- [ ] ProductHunt launch

**Paid Channels** (if budget):
- [ ] Targeted Telegram ads (₽5000)
- [ ] VK ads (₽3000)
- [ ] Google Ads (₽5000)

---

## 💬 Launch Messages

### **Habr Post**:
```
Заголовок: Я сделал агрегатор новостей с "метром провокационности" 🔥

Привет! Устал от скучных новостных лент, где все новости одинаково "важные"?

Я создал Trendoscope - агрегатор, который показывает, НАСКОЛЬКО провокационна каждая новость (0-100%).

Алгоритм анализирует:
- Ключевые слова (война, скандал, кризис)
- Паттерны (вопросы, caps, vs/против)
- Эмоциональность

Результат: только самые спорные новости наверху.

[Попробовать →]
[GitHub →]
```

### **Telegram Channels**:
```
🔥 Новый бот для любителей спорных новостей!

@TrendscopeBot - показывает только провокационные новости из 40+ источников

Фичи:
✅ Фильтр по категориям
✅ Ежедневный дайджест
✅ Метр провокационности
✅ Без рекламы

Попробовать: /start в @TrendscopeBot
```

### **Reddit Post**:
```
Title: [Project] I built a news aggregator that scores controversy (0-100%)

I got tired of boring news feeds where everything is equally "important."

So I built Trendoscope - shows how controversial each news item is.

The algorithm checks:
- Keywords (war, scandal, crisis)
- Patterns (questions, CAPS, vs/against)
- Emotional language

Result: Only the spiciest news on top 🔥

Live demo: [link]
Tech stack: FastAPI, Python, 40+ RSS sources

What do you think?
```

---

## 🎁 Growth Hacks

### **Referral Program**:
```
Invite friends → Unlock features

1 friend = Remove ads for 1 week
3 friends = Premium for 1 month  
10 friends = Lifetime premium

Your referral link: trendoscope.ru/?ref=YOUR_ID
```

### **"Controversy Challenge"**:
```
Guess the controversy score before revealing!

News: "GPT-5 заменит программистов"

Your guess: [_____]%
Actual: 89% 

Closest guess wins Premium for 1 month!
Share challenge: [button]
```

### **"News Bingo"**:
```
Weekly Bingo Card:
☑️ Trump mentioned
☑️ AI controversy  
☐ Market crash
☐ Russia/Ukraine
☑️ Tech scandal

3/5 complete!
Share to unlock next week's card
```

---

## 🔧 Technical Implementation

### **Telegram Bot (bot.py)**:
```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Welcome to Trendoscope!\n\n"
        "/hot - 5 most controversial news\n"
        "/tech - Tech news\n"
        "/politics - Politics news\n"
    )

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch from API
    response = requests.get('http://localhost:8003/api/news/feed?category=all&limit=5')
    news = response.json()['news']
    
    message = "🔥 MOST CONTROVERSIAL:\n\n"
    for item in news[:5]:
        score = item['controversy']['score']
        emoji = item['controversy']['emoji']
        message += f"{emoji} [{score}%] {item['title']}\n{item['link']}\n\n"
    
    await update.message.reply_text(message)

app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hot", hot))
app.run_polling()
```

### **Daily Digest (cron job)**:
```python
import schedule
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_daily_digest():
    # Get top 5 news
    news = get_top_news(limit=5)
    
    # Format email
    html = format_email(news)
    
    # Send to all subscribers
    for subscriber in get_subscribers():
        message = Mail(
            from_email='news@trendoscope.ru',
            to_emails=subscriber['email'],
            subject=f"🔥 5 самых провокационных новостей дня",
            html_content=html
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)

# Run daily at 6am
schedule.every().day.at("06:00").do(send_daily_digest)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📊 Tracking Setup

```python
# Add to every page
import mixpanel
mp = mixpanel.Mixpanel("YOUR_TOKEN")

# Track events
mp.track(user_id, 'News Viewed', {
    'category': 'tech',
    'controversy': 89,
    'source': 'TechCrunch'
})

mp.track(user_id, 'News Shared', {
    'platform': 'telegram',
    'news_id': 123
})

mp.track(user_id, 'Category Clicked', {
    'category': 'politics'
})
```

---

## 🎯 Summary

**Start with these 3 things TODAY**:

1. **Telegram bot** (biggest Russian audience)
2. **Social sharing** (viral growth)
3. **Email signup** (retention)

**Expected results**:
- Week 1: 100 users
- Week 2: 300 users
- Month 1: 1,000 users
- Month 3: 10,000 users

**Key insight**: 
You have a UNIQUE feature (controversy scoring).
Focus all marketing on that.

"Tinder для новостей" = Perfect positioning! 🔥

---

## ✅ Next Actions

Pick ONE to start RIGHT NOW:

- [ ] Create Telegram bot (2 hours)
- [ ] Add share buttons (1 hour)
- [ ] Build controversy leaderboard (2 hours)

Then iterate. Good luck! 🚀

---

**Full strategy**: See `GROWTH_STRATEGY.md`  
**Questions**: Open GitHub issue or email

Let's make Trendoscope viral! 🔥

