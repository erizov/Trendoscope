# 📱 Telegram Setup Guide - Step by Step

## Quick Setup (5 minutes)

### Step 1: Create Telegram Bot

1. Open Telegram app (mobile or desktop)
2. Search for `@BotFather` in search bar
3. Click on `@BotFather` (verified, blue checkmark)
4. Click **Start** button
5. Send command: `/newbot`
6. BotFather will ask for bot name:
   - Enter: `Trendoscope News Bot` (or any name)
7. BotFather will ask for username:
   - Enter: `trendoscope_news_bot` (must end with `_bot`)
   - If taken, try: `trendoscope_bot_123` or similar
8. BotFather will respond with:
   ```
   Done! Congratulations on your new bot.
   Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
9. **SAVE THE TOKEN** - you'll need it later!

✅ **Bot created!**

---

### Step 2: Create Telegram Channel

1. In Telegram, click **New Channel** (or menu → New Channel)
2. Enter channel name: `Trendoscope News` (or your choice)
3. Add description (optional): `Latest news and articles from Trendoscope`
4. Choose visibility:
   - **Public** (recommended) - users can find by username
   - **Private** - only invited users
5. If Public, set username: `@trendoscope_news` (or your choice)
6. Click **Create**

✅ **Channel created!**

---

### Step 3: Add Bot as Admin

1. Open your channel
2. Click channel name at top
3. Click **Administrators** (or **Manage Channel** → **Administrators**)
4. Click **Add Administrator**
5. Search for your bot: `trendoscope_news_bot` (or the username you created)
6. Click on your bot
7. Grant permissions:
   - ✅ **Post Messages** (REQUIRED)
   - ✅ **Edit Messages** (optional)
   - ✅ **Delete Messages** (optional)
8. Click **Save** or **Done**

✅ **Bot is now admin!**

---

### Step 4: Get Channel ID (if needed)

**For Public Channels:**
- Use username: `@trendoscope_news` (already have it)

**For Private Channels:**
1. Add bot `@userinfobot` to your channel
2. Bot will send channel ID (e.g., `-1001234567890`)
3. Save this ID
4. Remove `@userinfobot` if you want

---

### Step 5: Test Connection

**Option 1: Using Telegram App**
1. Open your channel
2. Type a test message
3. If bot is admin, you can post (but you'll post as yourself)

**Option 2: Using Python (after implementation)**
```python
from telegram import Bot
import asyncio

async def test():
    bot = Bot(token="YOUR_TOKEN_HERE")
    await bot.send_message(
        chat_id="@trendoscope_news",  # or channel ID
        text="Test message from Trendoscope!"
    )

asyncio.run(test())
```

---

## Configuration

### Save Your Credentials

**Create `.env` file:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
```

**Or use environment variables:**
```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHANNEL_ID="@trendoscope_news"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHANNEL_ID="@trendoscope_news"
```

---

## Troubleshooting

### Bot can't post to channel

**Problem:** Bot sends message but nothing appears in channel

**Solutions:**
1. ✅ Make sure bot is **admin** of channel
2. ✅ Check bot has **Post Messages** permission
3. ✅ Try posting from bot directly (not as yourself)
4. ✅ For private channels, use channel ID instead of username

### Invalid token error

**Problem:** `Unauthorized` or `Invalid token`

**Solutions:**
1. ✅ Check token is correct (no spaces, complete)
2. ✅ Token format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
3. ✅ Get new token from @BotFather: `/token`

### Channel not found

**Problem:** `Chat not found` error

**Solutions:**
1. ✅ For public channels: Use `@channel_username`
2. ✅ For private channels: Use channel ID (e.g., `-1001234567890`)
3. ✅ Make sure bot is added to channel
4. ✅ Make sure channel exists and is accessible

---

## Quick Reference

### Bot Commands (via @BotFather)

- `/newbot` - Create new bot
- `/token` - Get bot token
- `/setdescription` - Set bot description
- `/setabouttext` - Set bot about text
- `/setuserpic` - Set bot profile picture
- `/deletebot` - Delete bot

### Channel Settings

- **Public Channel:** Use `@username` format
- **Private Channel:** Use numeric ID (e.g., `-1001234567890`)
- **Bot must be admin** to post messages

---

## Security Notes

⚠️ **IMPORTANT:**
- Never share your bot token publicly
- Don't commit token to git
- Use `.env` file (add to `.gitignore`)
- Token gives full access to your bot

---

## Next Steps

After setup:
1. ✅ Save bot token and channel ID
2. ✅ Configure in `.env` file
3. ✅ Install `python-telegram-bot` library
4. ✅ Test connection
5. ✅ Start implementing (see `TELEGRAM_INTEGRATION_PLAN.md`)

---

## Example: Complete Setup

```
1. Bot Token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
2. Channel: @trendoscope_news
3. Bot Username: @trendoscope_news_bot
4. Bot is admin: ✅ Yes
5. Permissions: Post Messages ✅
```

**Configuration:**
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
```

✅ **Ready to use!**

---

## Resources

- **@BotFather:** Create and manage bots
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **python-telegram-bot:** https://python-telegram-bot.org/
- **Full Integration Plan:** `TELEGRAM_INTEGRATION_PLAN.md`

---

**All services are FREE!** ✅
