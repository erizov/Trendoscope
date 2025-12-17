# 🎤 Avatar Text-to-Speech Implementation Plan

## Overview

Add avatar feature with text-to-speech (TTS) that can read news articles in Russian/English using male or female voices.

---

## 📋 Phase 1: Backend TTS Service

### 1.1 TTS Library Selection

**Options:**
1. **gTTS (Google Text-to-Speech)** - Free, cloud-based, good quality
   - Pros: Free, good Russian/English support, easy to use
   - Cons: Requires internet, rate limits, no voice selection
   
2. **pyttsx3** - Offline, system voices
   - Pros: Offline, uses system voices, no API keys
   - Cons: Quality depends on system, limited voice options
   
3. **Azure Cognitive Services TTS** - Professional quality
   - Pros: High quality, many voices, neural TTS
   - Cons: Requires API key, paid service
   
4. **Google Cloud TTS** - Professional quality
   - Pros: High quality, many voices, good Russian support
   - Cons: Requires API key, paid service

**Recommendation:** Start with **gTTS** (✅ FREE) + **pyttsx3** (✅ FREE, offline fallback). All services are FREE - no paid options needed for MVP.

### 1.2 Implementation Structure

```
trendoscope2/src/trendoscope2/
├── tts/
│   ├── __init__.py
│   ├── tts_service.py      # Main TTS service
│   ├── gtts_provider.py    # Google TTS provider
│   ├── pyttsx3_provider.py # Offline TTS provider
│   └── voice_config.py     # Voice configuration
```

### 1.3 TTS Service Features

**Core Functionality:**
- Text-to-speech conversion
- Language detection (ru/en)
- Voice gender selection (male/female)
- Audio format: MP3 or WAV
- Caching of generated audio files
- Async support for non-blocking generation

**Voice Configuration:**
```python
VOICE_CONFIG = {
    "ru": {
        "male": "ru-RU-DmitryNeural",  # Azure example
        "female": "ru-RU-SvetlanaNeural"
    },
    "en": {
        "male": "en-US-GuyNeural",
        "female": "en-US-AriaNeural"
    }
}
```

**For gTTS:**
- Russian: `lang='ru'` (default female voice)
- English: `lang='en'` (default female voice)
- Note: gTTS doesn't support gender selection directly

**For pyttsx3:**
- Use system voices (Windows SAPI5)
- Filter by gender if available
- Fallback to default voice

---

## 📋 Phase 2: Avatar Visualization

### 2.1 Avatar Options

**Option A: Simple Animated Avatar (Recommended for MVP)**
- CSS/JavaScript animated face
- Lip-sync animation based on audio playback
- Simple, lightweight, no external dependencies

**Option B: 3D Avatar (Advanced)**
- Three.js or similar library
- More realistic, but heavier
- Better for production

**Option C: Video Avatar**
- Pre-recorded avatar videos
- Most realistic, but large file sizes
- Complex to implement

**Recommendation:** Start with **Option A** (simple animated avatar).

### 2.2 Avatar Design

**Visual Elements:**
- Face (circle/oval)
- Eyes (blinking animation)
- Mouth (lip-sync during speech)
- Optional: Hair, glasses, etc.

**States:**
- Idle (breathing animation)
- Speaking (lip-sync)
- Listening (if interactive)

**Styling:**
- Modern, clean design
- Dark theme compatible
- Responsive (mobile-friendly)

---

## 📋 Phase 3: API Endpoints

### 3.1 New Endpoints

```python
# POST /api/tts/generate
# Generate audio from text
{
    "text": "Text to convert",
    "language": "ru" | "en" | "auto",
    "voice_gender": "male" | "female",
    "provider": "gtts" | "pyttsx3" | "azure" | "auto"
}

# Response:
{
    "success": true,
    "audio_url": "/api/tts/audio/{audio_id}",
    "audio_id": "uuid",
    "duration": 12.5,
    "language": "ru",
    "voice_gender": "female"
}

# GET /api/tts/audio/{audio_id}
# Stream audio file

# POST /api/news/{article_id}/read
# Generate TTS for specific news article
{
    "voice_gender": "male" | "female",
    "language": "ru" | "en" | "auto"
}
```

### 3.2 Integration with Existing Endpoints

**Enhance `/api/news/feed`:**
- Add optional `include_audio` parameter
- Return `audio_url` for each news item if available

---

## 📋 Phase 4: Frontend Integration

### 4.1 Avatar Component

**Location:** `trendoscope2/src/frontend/avatar_player.html` or integrate into `news_feed.html`

**Features:**
- Avatar visualization
- Play/pause controls
- Voice selection (male/female)
- Language selection (ru/en)
- Progress bar
- Speed control (0.5x - 2x)

**UI Elements:**
```html
<div class="avatar-container">
    <div class="avatar-face">
        <div class="avatar-eyes">
            <div class="eye left"></div>
            <div class="eye right"></div>
        </div>
        <div class="avatar-mouth"></div>
    </div>
    <div class="avatar-controls">
        <button class="play-pause">▶</button>
        <select class="voice-gender">...</select>
        <select class="language">...</select>
        <input type="range" class="speed" min="0.5" max="2" step="0.1">
    </div>
</div>
```

### 4.2 Integration with News Feed

**Add to each news card:**
- "Read Aloud" button (🔊 icon)
- Opens avatar player modal
- Pre-fills with article text

---

## 📋 Phase 5: Storage and Caching

### 5.1 Audio File Storage

**Structure:**
```
data/
├── audio/
│   ├── tts/
│   │   ├── {audio_id}.mp3
│   │   └── cache/
│   │       └── {hash}.mp3  # Cached by text hash
```

**Caching Strategy:**
- Hash text + language + voice_gender
- Check cache before generating
- TTL: 30 days (configurable)
- Cleanup old files periodically

### 5.2 Database Schema (Optional)

**Table: `tts_audio`**
```sql
CREATE TABLE tts_audio (
    id TEXT PRIMARY KEY,
    text_hash TEXT UNIQUE,
    language TEXT,
    voice_gender TEXT,
    provider TEXT,
    file_path TEXT,
    duration REAL,
    created_at TIMESTAMP,
    accessed_at TIMESTAMP
);
```

---

## 📋 Phase 6: Implementation Steps

### Step 1: Setup TTS Service (Backend)
1. Create `tts/` module
2. Implement `tts_service.py` with provider abstraction
3. Implement `gtts_provider.py`
4. Implement `pyttsx3_provider.py` (optional)
5. Add voice configuration
6. Add audio caching

### Step 2: Add API Endpoints
1. Create `/api/tts/generate` endpoint
2. Create `/api/tts/audio/{audio_id}` endpoint
3. Add TTS to news feed endpoint (optional)
4. Add error handling and validation

### Step 3: Create Avatar Component (Frontend)
1. Design avatar HTML/CSS
2. Implement lip-sync animation
3. Add audio player controls
4. Implement voice/language selection

### Step 4: Integrate with News Feed
1. Add "Read Aloud" button to news cards
2. Create modal for avatar player
3. Connect to TTS API
4. Handle loading states

### Step 5: Testing
1. Unit tests for TTS service
2. Integration tests for API endpoints
3. E2E tests for avatar player
4. Test with Russian and English text
5. Test male/female voices

### Step 6: Documentation
1. API documentation
2. Usage guide
3. Configuration guide
4. Troubleshooting

---

## 📋 Phase 7: Dependencies

### Backend
```txt
# Add to requirements.txt
gtts>=2.5.0          # Google Text-to-Speech
pyttsx3>=2.90        # Offline TTS (optional)
pydub>=0.25.1        # Audio manipulation
```

### Frontend
- No new dependencies (use vanilla JS/CSS)
- Or consider:
  - `wavesurfer.js` for audio visualization
  - `howler.js` for better audio control

---

## 📋 Phase 8: Configuration

### Environment Variables
```env
# TTS Configuration
TTS_PROVIDER=auto  # gtts, pyttsx3, azure, auto
TTS_CACHE_ENABLED=true
TTS_CACHE_TTL_DAYS=30
TTS_AUDIO_FORMAT=mp3  # mp3, wav

# Azure TTS (if using)
AZURE_TTS_KEY=
AZURE_TTS_REGION=

# Google Cloud TTS (if using)
GOOGLE_TTS_KEY=
```

### Config File
```python
# config.py additions
TTS_AUDIO_DIR = DATA_DIR / "audio" / "tts"
TTS_CACHE_DIR = TTS_AUDIO_DIR / "cache"
TTS_MAX_TEXT_LENGTH = 5000  # characters
```

---

## 📋 Phase 9: Advanced Features (Future)

### 9.1 Voice Cloning
- Train custom voices
- Match author's voice style

### 9.2 SSML Support
- Advanced speech markup
- Pauses, emphasis, pitch control

### 9.3 Real-time Streaming
- Stream audio as it's generated
- Lower latency

### 9.4 Multiple Avatars
- Different avatar designs
- Customizable appearance

### 9.5 Interactive Avatar
- Respond to user questions
- Conversation mode

---

## 📋 Phase 10: Performance Considerations

### 10.1 Optimization
- Async audio generation
- Background job queue for long texts
- CDN for audio files (production)
- Compression (MP3 vs WAV)

### 10.2 Rate Limiting
- Limit TTS requests per user
- Queue system for high load
- Caching to reduce API calls

### 10.3 Monitoring
- Track TTS generation time
- Monitor cache hit rate
- Track provider usage
- Error rate monitoring

---

## 📋 Implementation Priority

### MVP (Minimum Viable Product)
1. ✅ gTTS provider
2. ✅ Basic API endpoints
3. ✅ Simple avatar visualization
4. ✅ Integration with news feed
5. ✅ Russian/English support

### Phase 2
1. ✅ Audio caching
2. ✅ pyttsx3 offline fallback
3. ✅ Voice gender selection (where possible)
4. ✅ Better avatar animations

### Phase 3
1. ⭐ Azure/Google Cloud TTS (premium)
2. ⭐ Advanced avatar features
3. ⭐ Performance optimization
4. ⭐ Analytics and monitoring

---

## 📋 File Structure

```
trendoscope2/
├── src/
│   ├── frontend/
│   │   ├── avatar_player.html      # Avatar component
│   │   └── avatar.js               # Avatar logic
│   └── trendoscope2/
│       ├── tts/
│       │   ├── __init__.py
│       │   ├── tts_service.py
│       │   ├── gtts_provider.py
│       │   ├── pyttsx3_provider.py
│       │   └── voice_config.py
│       └── api/
│           └── main.py             # Add TTS endpoints
├── data/
│   └── audio/
│       └── tts/                    # Generated audio files
└── requirements.txt                # Add TTS dependencies
```

---

## 📋 Testing Checklist

- [ ] TTS generates audio for Russian text
- [ ] TTS generates audio for English text
- [ ] Language auto-detection works
- [ ] Voice gender selection works (where supported)
- [ ] Audio caching works
- [ ] API endpoints return correct responses
- [ ] Avatar displays correctly
- [ ] Avatar lip-sync works
- [ ] Play/pause controls work
- [ ] Speed control works
- [ ] Integration with news feed works
- [ ] Error handling works (invalid text, API failures)
- [ ] Performance is acceptable (< 5s for generation)

---

## 📋 Estimated Timeline

- **Phase 1-2 (Backend TTS)**: 2-3 days
- **Phase 3 (API Endpoints)**: 1 day
- **Phase 4 (Frontend Avatar)**: 2-3 days
- **Phase 5 (Integration)**: 1 day
- **Testing & Polish**: 1-2 days

**Total: ~7-10 days** for MVP

---

## 📋 Notes

1. **gTTS Limitations:**
   - No direct gender selection
   - Requires internet connection
   - Rate limits (but generous for free tier)

2. **pyttsx3 Limitations:**
   - Quality depends on system voices
   - Windows: SAPI5 voices
   - Linux: espeak or festival
   - macOS: NSSpeechSynthesizer

3. **Voice Gender:**
   - gTTS: Default voices (typically female-sounding)
   - pyttsx3: Can filter system voices by gender
   - Azure/Google: Full control over voice selection

4. **Audio Format:**
   - MP3: Smaller file size, good quality
   - WAV: Larger, but better quality
   - Recommend MP3 for web delivery

---

## 📋 Success Criteria

✅ Users can click "Read Aloud" on any news article  
✅ Avatar appears and reads the text  
✅ Users can select language (ru/en)  
✅ Users can select voice gender (where supported)  
✅ Audio plays smoothly with lip-sync  
✅ Works offline (with pyttsx3 fallback)  
✅ Performance is acceptable (< 5s generation time)  
✅ Caching reduces redundant API calls  

---

## 📋 Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Backend TTS Service)
3. Implement MVP features first
4. Iterate based on feedback
5. Add advanced features in later phases
