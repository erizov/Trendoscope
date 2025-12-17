# 🎤📱 Complete Integration Plan: Avatar TTS + Telegram

## Overview

Complete plan for adding Avatar TTS (text-to-speech) and Telegram integration to Trendoscope2. **All services are FREE**.

---

## 🎯 Features

### 1. Avatar TTS
- ✅ Read text in Russian/English
- ✅ Male/Female voice selection
- ✅ Animated avatar with lip-sync
- ✅ Integration with news feed

### 2. Telegram Integration
- ✅ Post selected articles to Telegram channel
- ✅ Create and manage Telegram channel
- ✅ Format posts nicely
- ✅ Manual and auto-posting options

---

## 💰 Cost Summary

### ✅ ALL SERVICES ARE FREE

1. **gTTS (Google TTS)** - ✅ FREE
   - Unlimited usage
   - Good quality
   - Russian/English support

2. **pyttsx3 (Offline TTS)** - ✅ FREE
   - System voices
   - No internet required
   - No API keys

3. **Telegram Bot API** - ✅ FREE
   - Unlimited messages
   - Official library
   - No rate limits (reasonable use)

4. **Telegram Channel** - ✅ FREE
   - Unlimited subscribers
   - Unlimited posts
   - No storage limits

**Total Cost: $0.00** ✅

---

## 📋 Implementation Phases

### Phase 1: Avatar TTS (Week 1)
- [ ] Backend TTS service (gTTS)
- [ ] API endpoints
- [ ] Simple avatar visualization
- [ ] Integration with news feed

### Phase 2: Telegram Integration (Week 2)
- [ ] Create Telegram bot and channel
- [ ] Backend Telegram service
- [ ] API endpoints
- [ ] Frontend integration

### Phase 3: Advanced Features (Week 3+)
- [ ] Audio caching
- [ ] pyttsx3 offline fallback
- [ ] Auto-posting to Telegram
- [ ] Post TTS audio to Telegram

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install gtts>=2.5.0 pydub>=0.25.1 python-telegram-bot>=20.7
```

### Step 2: Setup Telegram

1. Create bot via @BotFather
2. Create Telegram channel
3. Add bot as admin
4. Save bot token and channel ID

### Step 3: Configure

```env
# TTS Configuration
TTS_PROVIDER=gtts
TTS_CACHE_ENABLED=true

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
```

### Step 4: File Structure

```
trendoscope2/src/trendoscope2/
├── tts/
│   ├── __init__.py
│   ├── tts_service.py
│   └── gtts_provider.py
├── telegram/
│   ├── __init__.py
│   ├── telegram_service.py
│   └── bot_client.py
└── api/
    └── main.py  # Add TTS and Telegram endpoints
```

---

## 📋 API Endpoints

### TTS Endpoints

```python
POST /api/tts/generate
{
    "text": "Text to convert",
    "language": "ru" | "en" | "auto",
    "voice_gender": "male" | "female"
}

GET /api/tts/audio/{audio_id}
# Returns audio file
```

### Telegram Endpoints

```python
POST /api/telegram/post
{
    "article_id": "uuid",
    "channel_id": "@trendoscope_news",
    "format": "markdown"
}

GET /api/telegram/channels
# List available channels

POST /api/telegram/test
# Test connection
```

---

## 📋 Frontend Features

### News Feed Enhancements

**Each news card will have:**
- 🔊 "Read Aloud" button → Opens avatar player
- 📱 "Post to Telegram" button → Posts to channel
- ⚙️ Settings → Configure TTS and Telegram

### Avatar Player Modal

- Animated avatar
- Audio playback
- Language/voice selection
- Play/pause controls

### Telegram Settings

- Bot token configuration
- Channel management
- Test connection
- Posting history

---

## 📋 Integration Flow

### User Flow: Read Article Aloud

1. User clicks "Read Aloud" on news article
2. Frontend sends text to `/api/tts/generate`
3. Backend generates audio (gTTS)
4. Returns audio URL
5. Avatar player modal opens
6. Avatar animates while audio plays

### User Flow: Post to Telegram

1. User clicks "Post to Telegram" on news article
2. Frontend shows post preview
3. User confirms
4. Frontend sends to `/api/telegram/post`
5. Backend formats post and sends to channel
6. Returns success/error

---

## 📋 Dependencies

```txt
# requirements.txt additions
gtts>=2.5.0                    # Google TTS (FREE)
pydub>=0.25.1                  # Audio manipulation
python-telegram-bot>=20.7      # Telegram Bot API (FREE)
```

---

## 📋 Configuration

### config.py

```python
# TTS Configuration
TTS_AUDIO_DIR = DATA_DIR / "audio" / "tts"
TTS_CACHE_ENABLED = True
TTS_MAX_TEXT_LENGTH = 5000

# Telegram Configuration
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID: Optional[str] = os.getenv('TELEGRAM_CHANNEL_ID')
TELEGRAM_ENABLED: bool = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_POST_FORMAT: str = os.getenv('TELEGRAM_POST_FORMAT', 'markdown')
```

### .env

```env
# TTS
TTS_PROVIDER=gtts
TTS_CACHE_ENABLED=true

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@trendoscope_news
TELEGRAM_ENABLED=true
TELEGRAM_POST_FORMAT=markdown
```

---

## 📋 Testing Checklist

### TTS
- [ ] Generate audio for Russian text
- [ ] Generate audio for English text
- [ ] Avatar displays and animates
- [ ] Audio playback works
- [ ] Language selection works

### Telegram
- [ ] Bot connects successfully
- [ ] Posts are sent to channel
- [ ] Post formatting is correct
- [ ] Long posts are handled
- [ ] Error handling works

### Integration
- [ ] "Read Aloud" button works
- [ ] "Post to Telegram" button works
- [ ] Settings page works
- [ ] Both features work together

---

## 📋 Timeline

- **Week 1:** Avatar TTS (Backend + Frontend)
- **Week 2:** Telegram Integration (Backend + Frontend)
- **Week 3:** Testing, Polish, Advanced Features

**Total: ~3 weeks for complete integration**

---

## 📋 Future Enhancements

### Combined Features
- Post TTS audio to Telegram as voice message
- Auto-generate audio for Telegram posts
- Schedule posts with audio

### Advanced TTS
- Voice cloning
- SSML support
- Multiple avatars

### Advanced Telegram
- Multiple channels
- Auto-posting rules
- Analytics and engagement tracking

---

## 📋 Documentation

- **Avatar TTS Plan:** `AVATAR_TTS_PLAN.md`
- **Telegram Plan:** `TELEGRAM_INTEGRATION_PLAN.md`
- **Quick Start:** `AVATAR_TTS_QUICKSTART.md`

---

## 🎯 Success Criteria

✅ Users can read articles aloud with avatar  
✅ Users can post articles to Telegram  
✅ All services are FREE  
✅ Integration works smoothly  
✅ Error handling is robust  
✅ Performance is acceptable  

---

## 📋 Next Steps

1. ✅ Plans created
2. ⏭️ Start with Avatar TTS (Week 1)
3. ⏭️ Add Telegram integration (Week 2)
4. ⏭️ Test and polish (Week 3)
5. ⏭️ Deploy and monitor

---

**All services are FREE! No costs involved.** ✅
