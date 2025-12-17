# 📱 Telegram Integration Plan

## Overview

Add Telegram integration to automatically post selected news articles and text posts to your Telegram channel. All services are **FREE** using Telegram Bot API.

---

## 🎯 Goals

1. ✅ Create Telegram channel for news posts
2. ✅ Post selected news articles to channel
3. ✅ Format posts nicely (title, summary, link, tags)
4. ✅ Support Russian and English posts
5. ✅ Manual selection of posts to publish
6. ✅ Optional: Auto-posting based on filters
7. ✅ Integration with existing news feed

---

## 📋 Phase 1: Telegram Setup (Free)

### 1.1 Create Telegram Bot

**Steps:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create bot
4. Save the **Bot Token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Cost:** ✅ **FREE**

### 1.2 Create Telegram Channel

**Steps:**
1. Open Telegram → New Channel
2. Set channel name (e.g., "Trendoscope News")
3. Set description
4. Make channel **Public** (optional, for easier access)
5. Get channel username (e.g., `@trendoscope_news`)

**Alternative:** Private channel (use channel ID instead)

### 1.3 Add Bot to Channel as Admin

**Steps:**
1. Go to channel settings
2. Administrators → Add Administrator
3. Search for your bot (by username)
4. Grant permissions:
   - ✅ Post Messages
   - ✅ Edit Messages (optional)
   - ✅ Delete Messages (optional)

**Cost:** ✅ **FREE**

---

## 📋 Phase 2: Backend Telegram Service

### 2.1 Implementation Structure

```
trendoscope2/src/trendoscope2/
├── telegram/
│   ├── __init__.py
│   ├── telegram_service.py    # Main Telegram service
│   ├── bot_client.py          # Telegram Bot API client
│   ├── channel_manager.py    # Channel management
│   └── post_formatter.py     # Format posts for Telegram
```

### 2.2 Telegram Service Features

**Core Functionality:**
- Send text posts to channel
- Format posts with Markdown/HTML
- Support images (if available)
- Handle long posts (split if needed)
- Error handling and retries
- Rate limiting (Telegram limits: 30 messages/second)

**Post Formatting:**
```python
POST_FORMAT = """
📰 {title}

{summary}

🔗 {link}
📅 {date}
🏷️ {tags}
"""
```

### 2.3 Telegram Bot API Client

**Library:** `python-telegram-bot` (official, free)

**Features:**
- Send messages to channel
- Upload images/media
- Format text (Markdown/HTML)
- Handle errors gracefully
- Async support

---

## 📋 Phase 3: API Endpoints

### 3.1 New Endpoints

```python
# POST /api/telegram/post
# Post selected article to Telegram channel
{
    "article_id": "uuid" | "news_item_object",
    "channel_id": "@trendoscope_news" | "channel_id",
    "format": "markdown" | "html" | "plain",
    "include_image": true | false
}

# Response:
{
    "success": true,
    "message_id": 12345,
    "channel": "@trendoscope_news",
    "posted_at": "2025-12-16T18:00:00Z"
}

# GET /api/telegram/channels
# List available channels
# Response:
{
    "channels": [
        {
            "id": "@trendoscope_news",
            "name": "Trendoscope News",
            "type": "channel"
        }
    ]
}

# POST /api/telegram/test
# Test connection to Telegram
{
    "channel_id": "@trendoscope_news"
}

# POST /api/telegram/batch
# Post multiple articles
{
    "article_ids": ["id1", "id2", "id3"],
    "channel_id": "@trendoscope_news",
    "delay_seconds": 5  # Delay between posts
}
```

### 3.2 Integration with News Feed

**Enhance `/api/news/feed`:**
- Add "Post to Telegram" button in frontend
- Return `can_post_to_telegram: true` flag
- Store selected articles for posting

---

## 📋 Phase 4: Frontend Integration

### 4.1 News Feed Enhancements

**Add to each news card:**
- 📱 "Post to Telegram" button
- Opens confirmation modal
- Shows preview of formatted post
- Select channel (if multiple)
- Format options (Markdown/HTML/Plain)

### 4.2 Telegram Settings Page

**Features:**
- Configure bot token
- Add/remove channels
- Test connection
- View posting history
- Set auto-posting rules (optional)

**UI Elements:**
```html
<div class="telegram-settings">
    <input type="text" placeholder="Bot Token" />
    <input type="text" placeholder="Channel ID/Username" />
    <button class="test-connection">Test Connection</button>
    <div class="channels-list">...</div>
</div>
```

---

## 📋 Phase 5: Post Formatting

### 5.1 Format Templates

**Markdown Format:**
```markdown
📰 **{title}**

{summary}

🔗 [Read more]({link})
📅 {date}
🏷️ {tags}
```

**HTML Format:**
```html
📰 <b>{title}</b>

{summary}

🔗 <a href="{link}">Read more</a>
📅 {date}
🏷️ {tags}
```

**Plain Text:**
```
📰 {title}

{summary}

🔗 {link}
📅 {date}
🏷️ {tags}
```

### 5.2 Post Length Handling

**Telegram Limits:**
- Max message length: 4096 characters
- If post exceeds limit:
  - Option 1: Truncate summary
  - Option 2: Split into multiple messages
  - Option 3: Post title + link only

**Implementation:**
```python
def format_post(article, max_length=4096):
    post = format_template(article)
    if len(post) > max_length:
        # Truncate summary
        summary_max = max_length - len(title + link + tags) - 100
        article['summary'] = article['summary'][:summary_max] + "..."
        post = format_template(article)
    return post
```

---

## 📋 Phase 6: Configuration

### 6.1 Environment Variables

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
TELEGRAM_MAX_POST_LENGTH=4096
TELEGRAM_RATE_LIMIT_DELAY=1  # seconds between posts
```

### 6.2 Config File

```python
# config.py additions
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID: Optional[str] = os.getenv('TELEGRAM_CHANNEL_ID')
TELEGRAM_ENABLED: bool = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_POST_FORMAT: str = os.getenv('TELEGRAM_POST_FORMAT', 'markdown')
TELEGRAM_MAX_POST_LENGTH: int = int(os.getenv('TELEGRAM_MAX_POST_LENGTH', '4096'))
```

### 6.3 Storage

**Database Schema (Optional):**
```sql
CREATE TABLE telegram_posts (
    id TEXT PRIMARY KEY,
    article_id TEXT,
    channel_id TEXT,
    message_id INTEGER,
    posted_at TIMESTAMP,
    format TEXT,
    success BOOLEAN,
    error_message TEXT
);
```

---

## 📋 Phase 7: Dependencies

### Backend

```txt
# Add to requirements.txt
python-telegram-bot>=20.7  # Official Telegram Bot API library
```

**Note:** `python-telegram-bot` is **FREE** and official library.

---

## 📋 Phase 8: Implementation Steps

### Step 1: Setup Telegram Bot
1. Create bot via @BotFather
2. Create Telegram channel
3. Add bot as admin to channel
4. Save bot token and channel ID

### Step 2: Install Dependencies
```bash
pip install python-telegram-bot>=20.7
```

### Step 3: Create Telegram Service (Backend)
1. Create `telegram/` module
2. Implement `telegram_service.py`
3. Implement `bot_client.py` with python-telegram-bot
4. Implement `post_formatter.py`
5. Add error handling

### Step 4: Add API Endpoints
1. Create `/api/telegram/post` endpoint
2. Create `/api/telegram/channels` endpoint
3. Create `/api/telegram/test` endpoint
4. Add validation and error handling

### Step 5: Frontend Integration
1. Add "Post to Telegram" button to news cards
2. Create posting modal
3. Add Telegram settings page
4. Show posting status/feedback

### Step 6: Testing
1. Test bot connection
2. Test posting to channel
3. Test formatting (Markdown/HTML)
4. Test long posts (truncation)
5. Test error handling

---

## 📋 Phase 9: Advanced Features (Optional)

### 9.1 Auto-Posting
- Schedule posts based on filters
- Post top trending articles
- Post articles with high controversy score
- Time-based posting (e.g., every hour)

### 9.2 Media Support
- Post images if available in article
- Post thumbnails
- Support for video links

### 9.3 Multiple Channels
- Manage multiple channels
- Post to different channels based on category
- Different formatting per channel

### 9.4 Analytics
- Track post performance
- View engagement (views, clicks)
- Posting history

### 9.5 Scheduled Posts
- Queue posts for later
- Schedule posts at specific times
- Bulk posting with delays

---

## 📋 Phase 10: Free Services Summary

### ✅ All Services Are FREE

1. **Telegram Bot API** - ✅ FREE
   - Unlimited messages
   - No rate limits (reasonable use)
   - Official library: `python-telegram-bot`

2. **Telegram Channel** - ✅ FREE
   - Unlimited subscribers
   - Unlimited posts
   - No storage limits

3. **Bot Creation** - ✅ FREE
   - Via @BotFather
   - No costs

**Total Cost:** ✅ **$0.00**

---

## 📋 File Structure

```
trendoscope2/
├── src/
│   ├── frontend/
│   │   └── news_feed.html      # Add Telegram buttons
│   └── trendoscope2/
│       ├── telegram/
│       │   ├── __init__.py
│       │   ├── telegram_service.py
│       │   ├── bot_client.py
│       │   ├── channel_manager.py
│       │   └── post_formatter.py
│       └── api/
│           └── main.py         # Add Telegram endpoints
├── data/
│   └── telegram/
│       └── posts_history.json  # Optional: posting history
└── requirements.txt            # Add python-telegram-bot
```

---

## 📋 Testing Checklist

- [ ] Bot token is valid
- [ ] Bot can send messages to channel
- [ ] Post formatting works (Markdown/HTML)
- [ ] Long posts are handled correctly
- [ ] Error handling works (invalid token, network errors)
- [ ] Frontend "Post to Telegram" button works
- [ ] Post preview shows correctly
- [ ] Multiple posts can be sent
- [ ] Rate limiting works (if implemented)
- [ ] Russian and English posts work

---

## 📋 Quick Start Guide

### 1. Create Bot and Channel

1. Open Telegram → Search `@BotFather`
2. Send `/newbot` → Follow instructions
3. Save bot token
4. Create channel in Telegram
5. Add bot as admin to channel
6. Get channel username or ID

### 2. Configure

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
```

### 3. Install

```bash
pip install python-telegram-bot>=20.7
```

### 4. Test

```python
from telegram import Bot

bot = Bot(token="YOUR_TOKEN")
await bot.send_message(
    chat_id="@trendoscope_news",
    text="Test message from Trendoscope!"
)
```

---

## 📋 Example Post Format

**Input (News Article):**
```json
{
    "title": "AI Breakthrough in Natural Language Processing",
    "summary": "Scientists have made significant progress...",
    "link": "https://example.com/news/123",
    "date": "2025-12-16",
    "tags": ["AI", "Technology"]
}
```

**Output (Telegram Post):**
```
📰 AI Breakthrough in Natural Language Processing

Scientists have made significant progress in developing more advanced NLP models that can understand context better than ever before.

🔗 https://example.com/news/123
📅 2025-12-16
🏷️ #AI #Technology
```

---

## 📋 Rate Limits

**Telegram Bot API Limits:**
- **30 messages per second** per bot
- No daily limit
- No monthly limit
- **FREE** for all usage

**Recommendations:**
- Add 1-2 second delay between posts
- Batch posts with delays
- Respect rate limits (30 msg/sec is generous)

---

## 📋 Security Considerations

1. **Bot Token Security:**
   - Store in environment variables
   - Never commit to git
   - Use `.env` file (in `.gitignore`)

2. **Channel Access:**
   - Only authorized bots can post
   - Channel admin controls access

3. **Input Validation:**
   - Validate article data before posting
   - Sanitize user input
   - Check post length

---

## 📋 Success Criteria

✅ Bot can connect to Telegram  
✅ Posts are sent to channel successfully  
✅ Posts are formatted nicely  
✅ Long posts are handled correctly  
✅ Frontend integration works  
✅ Users can select posts to publish  
✅ Error handling works gracefully  
✅ All services are FREE  

---

## 📋 Next Steps

1. ✅ Plan created
2. ⏭️ Create Telegram bot and channel
3. ⏭️ Install dependencies
4. ⏭️ Implement backend Telegram service
5. ⏭️ Add API endpoints
6. ⏭️ Integrate with frontend
7. ⏭️ Test and deploy

---

## 📋 Integration with Avatar TTS

**Future Enhancement:**
- Post audio files (TTS) to Telegram
- Voice messages in channel
- Combine text + audio posts

**Note:** Telegram supports voice messages, so we can post TTS audio files as voice messages!

---

## 📋 Resources

- **Telegram Bot API Docs:** https://core.telegram.org/bots/api
- **python-telegram-bot Docs:** https://python-telegram-bot.org/
- **BotFather:** @BotFather (in Telegram)
- **Telegram API Limits:** https://core.telegram.org/bots/faq#broadcasting-to-users

---

**All services are FREE! No costs involved.** ✅
