# 🎥 Rutube Video to Text Generator

## 📋 Overview

A standalone webpage that accepts a Rutube video URL and generates text content based on the video's audio transcription. Works with Russian and English videos.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS)                    │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Input: Rutube URL                               │  │
│  │  Display: Video Embed + Transcript + Generated   │  │
│  │           Text (all on same page)                │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────┬──────────────────────────────────┘
                     │ HTTP POST
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend Endpoint                     │
│  POST /api/rutube/generate                                │
└────────────────────┬──────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│ Video Download │      │  Audio Extraction   │
│  (yt-dlp)      │      │  (ffmpeg)           │
└───────┬────────┘      └─────────┬──────────┘
        │                         │
        └────────────┬─────────────┘
                     ▼
        ┌────────────────────────┐
        │  Transcription         │
        │  (Whisper - Local)      │
        └───────────┬────────────┘
                    ▼
        ┌────────────────────────┐
        │  Text Generation       │
        │  (Demo Generator)      │
        └───────────┬────────────┘
                    ▼
        ┌────────────────────────┐
        │  Response:             │
        │  - Video Info          │
        │  - Transcript          │
        │  - Generated Text      │
        └────────────────────────┘
```

---

## 🔧 Technology Stack

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (modern, responsive)
- **Vanilla JavaScript** - No frameworks needed
- **Rutube Embed API** - Video player

### Backend
- **FastAPI** - API endpoint
- **yt-dlp** - Video download (supports Rutube)
- **ffmpeg** - Audio extraction
- **Whisper (OpenAI)** - Free, local transcription
- **Existing Demo Generator** - Text generation

### Dependencies
```python
# New dependencies needed
yt-dlp>=2023.12.30  # Video download
openai-whisper>=20231117  # Transcription
ffmpeg-python>=0.2.0  # Audio processing (or subprocess)
```

---

## 📐 Component Architecture

### 1. Frontend Component (`frontend/rutube_generator.html`)

**Structure:**
```html
┌─────────────────────────────────────────┐
│  Rutube Video to Text Generator         │
├─────────────────────────────────────────┤
│  [Input: Rutube URL] [Generate Button]  │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │  Video Player (Embed)              │ │
│  └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │  Transcript                         │ │
│  │  [Scrollable text area]             │ │
│  └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │  Generated Text                    │ │
│  │  [Formatted article]               │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Features:**
- URL input validation
- Loading states
- Error handling
- Responsive design
- Copy-to-clipboard buttons

### 2. Backend API (`src/trendascope/api/rutube.py`)

**Endpoint:**
```python
POST /api/rutube/generate
Body: {"url": "https://rutube.ru/video/..."}
Response: {
    "video_info": {...},
    "transcript": "...",
    "generated_text": {...},
    "language": "ru" | "en"
}
```

**Processing Flow:**
1. Validate Rutube URL
2. Download video (yt-dlp)
3. Extract audio (ffmpeg)
4. Transcribe audio (Whisper)
5. Detect language
6. Generate text (demo generator)
7. Return results

### 3. Video Processing Module (`src/trendascope/ingest/rutube_processor.py`)

**Responsibilities:**
- URL validation
- Video download
- Audio extraction
- Temporary file management

### 4. Transcription Module (`src/trendascope/nlp/transcriber.py`)

**Responsibilities:**
- Audio transcription using Whisper
- Language detection
- Timestamp generation (optional)
- Text cleaning

---

## 🚀 Implementation Steps

### Phase 1: Setup & Dependencies (30 min)

#### Step 1.1: Install Dependencies
```bash
pip install yt-dlp openai-whisper ffmpeg-python
```

**Note**: `ffmpeg` binary must be installed separately:
- Windows: Download from https://ffmpeg.org/download.html
- Or use: `choco install ffmpeg` (if Chocolatey installed)

#### Step 1.2: Verify Rutube Support
```bash
yt-dlp --list-extractors | grep rutube
# Should show: rutube
```

#### Step 1.3: Test Video Download
```bash
yt-dlp --get-url "https://rutube.ru/video/..."
```

---

### Phase 2: Backend Implementation (2-3 hours)

#### Step 2.1: Create Video Processor Module

**File**: `src/trendascope/ingest/rutube_processor.py`

```python
"""
Rutube video processing module.
Downloads video and extracts audio for transcription.
"""
import os
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def validate_rutube_url(url: str) -> bool:
    """Validate Rutube URL format."""
    return "rutube.ru" in url.lower() and "/video/" in url.lower()


def download_video(url: str, output_dir: Optional[Path] = None) -> Tuple[Path, Dict]:
    """
    Download video from Rutube.
    
    Returns:
        Tuple of (video_path, video_info)
    """
    if not validate_rutube_url(url):
        raise ValueError(f"Invalid Rutube URL: {url}")
    
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp())
    
    # Download video
    video_path = output_dir / "video.mp4"
    
    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",  # Best quality MP4
        "-o", str(video_path),
        "--no-playlist",
        url
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout
        )
        
        # Extract video info
        info_cmd = [
            "yt-dlp",
            "--dump-json",
            url
        ]
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        import json
        video_info = json.loads(info_result.stdout)
        
        return video_path, video_info
        
    except subprocess.TimeoutExpired:
        raise TimeoutError("Video download timed out")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to download video: {e.stderr}")


def extract_audio(video_path: Path, output_dir: Optional[Path] = None) -> Path:
    """
    Extract audio from video using ffmpeg.
    
    Returns:
        Path to audio file (WAV format)
    """
    if output_dir is None:
        output_dir = video_path.parent
    
    audio_path = output_dir / "audio.wav"
    
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",  # 16kHz sample rate (Whisper standard)
        "-ac", "1",  # Mono
        "-y",  # Overwrite
        str(audio_path)
    ]
    
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=120
        )
        return audio_path
    except subprocess.TimeoutExpired:
        raise TimeoutError("Audio extraction timed out")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract audio: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")


def process_rutube_video(url: str) -> Tuple[Path, Path, Dict]:
    """
    Download video and extract audio.
    
    Returns:
        Tuple of (video_path, audio_path, video_info)
    """
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="rutube_"))
    
    try:
        # Download video
        video_path, video_info = download_video(url, temp_dir)
        
        # Extract audio
        audio_path = extract_audio(video_path, temp_dir)
        
        return video_path, audio_path, video_info
        
    except Exception as e:
        # Cleanup on error
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise
```

#### Step 2.2: Create Transcription Module

**File**: `src/trendascope/nlp/transcriber.py`

```python
"""
Audio transcription using OpenAI Whisper.
Free, local, supports multiple languages.
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

logger = logging.getLogger(__name__)

# Global model instance (lazy load)
_whisper_model = None


def get_whisper_model(model_size: str = "base"):
    """
    Get or load Whisper model.
    
    Model sizes: tiny, base, small, medium, large
    - tiny: Fastest, least accurate
    - base: Good balance (recommended)
    - large: Most accurate, slowest
    """
    global _whisper_model
    
    if not WHISPER_AVAILABLE:
        raise ImportError("openai-whisper not installed. Run: pip install openai-whisper")
    
    if _whisper_model is None:
        logger.info(f"Loading Whisper model: {model_size}")
        _whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded")
    
    return _whisper_model


def transcribe_audio(
    audio_path: Path,
    language: Optional[str] = None,
    model_size: str = "base"
) -> Dict[str, any]:
    """
    Transcribe audio file using Whisper.
    
    Args:
        audio_path: Path to audio file
        language: Language code (ru, en) or None for auto-detect
        model_size: Whisper model size
        
    Returns:
        Dictionary with:
        - text: Full transcript
        - language: Detected language
        - segments: List of segments with timestamps
    """
    model = get_whisper_model(model_size)
    
    # Transcribe
    logger.info(f"Transcribing audio: {audio_path}")
    result = model.transcribe(
        str(audio_path),
        language=language,
        task="transcribe"
    )
    
    # Clean up transcript
    text = result["text"].strip()
    
    return {
        "text": text,
        "language": result["language"],
        "segments": result.get("segments", []),
        "full_result": result
    }


def detect_language(audio_path: Path) -> str:
    """Detect language of audio file."""
    model = get_whisper_model("base")
    audio = whisper.load_audio(str(audio_path))
    audio = whisper.pad_or_trim(audio)
    
    # Make log-Mel spectrogram
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    
    # Detect language
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)
    
    return detected_lang
```

#### Step 2.3: Create API Endpoint

**File**: `src/trendascope/api/rutube.py`

```python
"""
Rutube video to text generation API.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging
from pathlib import Path
import shutil

from ..ingest.rutube_processor import (
    process_rutube_video,
    validate_rutube_url
)
from ..nlp.transcriber import transcribe_audio, detect_language
from ..gen.demo_generator import generate_demo_post

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rutube", tags=["rutube"])


@router.post("/generate")
async def generate_text_from_rutube(
    url: str = Body(..., embed=True, description="Rutube video URL")
):
    """
    Generate text from Rutube video.
    
    Process:
    1. Download video
    2. Extract audio
    3. Transcribe audio
    4. Generate text from transcript
    
    Returns:
        - video_info: Video metadata
        - transcript: Full transcript
        - generated_text: Generated article/post
        - language: Detected language
    """
    # Validate URL
    if not validate_rutube_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Rutube URL. Expected format: https://rutube.ru/video/..."
        )
    
    temp_dir = None
    try:
        # Step 1: Download video and extract audio
        logger.info(f"Processing Rutube video: {url}")
        video_path, audio_path, video_info = process_rutube_video(url)
        temp_dir = video_path.parent
        
        # Step 2: Detect language
        language = detect_language(audio_path)
        lang_code = "ru" if language == "ru" else "en"
        logger.info(f"Detected language: {language}")
        
        # Step 3: Transcribe audio
        transcript_result = transcribe_audio(
            audio_path,
            language=language,
            model_size="base"  # Use base for speed
        )
        transcript = transcript_result["text"]
        
        logger.info(f"Transcript length: {len(transcript)} characters")
        
        # Step 4: Generate text from transcript
        # Use demo generator with transcript as context
        generated_post = generate_demo_post(
            style="analytical",  # Default style
            topic="any",
            news_items=[{
                "title": video_info.get("title", "Video Content"),
                "summary": transcript[:1000],  # Use transcript as summary
                "link": url
            }]
        )
        
        return {
            "success": True,
            "video_info": {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0),
                "url": url
            },
            "transcript": transcript,
            "generated_text": generated_post,
            "language": lang_code,
            "transcript_length": len(transcript)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=f"Processing timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing Rutube video: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )
    finally:
        # Cleanup temp files
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
```

#### Step 2.4: Register Router in Main App

**File**: `src/trendascope/api/main.py`

Add to imports:
```python
from .rutube import router as rutube_router
```

Add after other routers:
```python
app.include_router(rutube_router)
```

---

### Phase 3: Frontend Implementation (2-3 hours)

#### Step 3.1: Create HTML Page

**File**: `src/frontend/rutube_generator.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rutube Video to Text Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .input-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .input-group input {
            flex: 1;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
        }
        
        .btn:disabled {
            background: #adb5bd;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .video-container {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 */
            height: 0;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .text-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .copy-btn {
            margin-top: 10px;
            padding: 8px 16px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .copy-btn:hover {
            background: #218838;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
        }
        
        .generated-article {
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 25px;
        }
        
        .generated-article h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .generated-article .tags {
            margin-top: 15px;
        }
        
        .generated-article .tags span {
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 Rutube Video to Text Generator</h1>
            <p>Generate articles from Rutube video content</p>
        </div>
        
        <div class="input-section">
            <div class="input-group">
                <input 
                    type="text" 
                    id="rutubeUrl" 
                    placeholder="Enter Rutube video URL (e.g., https://rutube.ru/video/...)"
                    value=""
                >
                <button class="btn" id="generateBtn" onclick="generateText()">
                    Generate Text
                </button>
            </div>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing video... This may take a few minutes.</p>
            </div>
        </div>
        
        <div class="content" id="content" style="display: none;">
            <div class="section">
                <h2>📹 Video</h2>
                <div class="video-container" id="videoContainer"></div>
            </div>
            
            <div class="section">
                <h2>📝 Transcript</h2>
                <div class="text-box" id="transcript"></div>
                <button class="copy-btn" onclick="copyToClipboard('transcript')">
                    Copy Transcript
                </button>
            </div>
            
            <div class="section">
                <h2>✍️ Generated Article</h2>
                <div class="generated-article" id="generatedText"></div>
                <button class="copy-btn" onclick="copyToClipboard('generatedText')">
                    Copy Article
                </button>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = 'http://localhost:8003';
        
        async function generateText() {
            const url = document.getElementById('rutubeUrl').value.trim();
            const loading = document.getElementById('loading');
            const content = document.getElementById('content');
            const generateBtn = document.getElementById('generateBtn');
            
            if (!url) {
                alert('Please enter a Rutube URL');
                return;
            }
            
            // Validate URL
            if (!url.includes('rutube.ru/video/')) {
                alert('Invalid Rutube URL. Please enter a valid Rutube video URL.');
                return;
            }
            
            // Show loading, hide content
            loading.classList.add('active');
            content.style.display = 'none';
            generateBtn.disabled = true;
            
            try {
                const response = await fetch(`${API_URL}/api/rutube/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                // Display results
                displayResults(data, url);
                
            } catch (error) {
                showError(error.message);
            } finally {
                loading.classList.remove('active');
                generateBtn.disabled = false;
            }
        }
        
        function displayResults(data, videoUrl) {
            const content = document.getElementById('content');
            const videoContainer = document.getElementById('videoContainer');
            const transcriptDiv = document.getElementById('transcript');
            const generatedDiv = document.getElementById('generatedText');
            
            // Extract video ID from URL
            const videoId = extractVideoId(videoUrl);
            
            // Embed video
            if (videoId) {
                videoContainer.innerHTML = `
                    <iframe 
                        src="https://rutube.ru/play/embed/${videoId}" 
                        frameborder="0" 
                        allow="clipboard-write; autoplay" 
                        webkitAllowFullScreen 
                        mozallowfullscreen 
                        allowFullScreen>
                    </iframe>
                `;
            }
            
            // Display transcript
            transcriptDiv.textContent = data.transcript || 'No transcript available';
            
            // Display generated text
            const generated = data.generated_text || {};
            generatedDiv.innerHTML = `
                <h3>${generated.title || 'Generated Article'}</h3>
                <div>${(generated.text || '').replace(/\n/g, '<br>')}</div>
                ${generated.tags ? `
                    <div class="tags">
                        ${generated.tags.map(tag => `<span>${tag}</span>`).join('')}
                    </div>
                ` : ''}
            `;
            
            // Show content
            content.style.display = 'block';
            
            // Scroll to content
            content.scrollIntoView({ behavior: 'smooth' });
        }
        
        function extractVideoId(url) {
            // Rutube URL format: https://rutube.ru/video/abc123def456/
            const match = url.match(/rutube\.ru\/video\/([a-zA-Z0-9]+)/);
            return match ? match[1] : null;
        }
        
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent || element.innerText;
            
            navigator.clipboard.writeText(text).then(() => {
                alert('Copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
                alert('Failed to copy to clipboard');
            });
        }
        
        function showError(message) {
            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="error">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            content.style.display = 'block';
        }
        
        // Allow Enter key to submit
        document.getElementById('rutubeUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                generateText();
            }
        });
    </script>
</body>
</html>
```

#### Step 3.2: Add Route to Serve HTML

**File**: `src/trendascope/api/main.py`

Add static file serving:
```python
# Add after other static mounts
app.mount("/static", StaticFiles(directory="src/frontend"), name="static")
```

Or add route:
```python
@app.get("/rutube", response_class=HTMLResponse)
async def rutube_generator_page():
    """Serve Rutube generator page."""
    with open("src/frontend/rutube_generator.html", "r", encoding="utf-8") as f:
        return f.read()
```

---

### Phase 4: Testing & Optimization (1-2 hours)

#### Step 4.1: Test with Sample Videos
- Test with Russian Rutube video
- Test with English Rutube video (if available)
- Test error handling (invalid URL, network errors)

#### Step 4.2: Performance Optimization
- Add caching for processed videos (by URL)
- Optimize Whisper model size (base vs small)
- Add progress updates via WebSocket (optional)

#### Step 4.3: Error Handling
- Handle missing ffmpeg
- Handle missing yt-dlp
- Handle video download failures
- Handle transcription failures

---

## 📦 Dependencies to Add

**File**: `requirements.txt`

```txt
# Video processing
yt-dlp>=2023.12.30
openai-whisper>=20231117
ffmpeg-python>=0.2.0  # Optional, can use subprocess instead
```

**Note**: `ffmpeg` binary must be installed separately:
- Windows: Download from https://ffmpeg.org/download.html
- Or: `choco install ffmpeg` (Chocolatey)
- Linux: `apt-get install ffmpeg` or `yum install ffmpeg`
- macOS: `brew install ffmpeg`

---

## 🎯 Quick Start Checklist

- [ ] Install dependencies: `pip install yt-dlp openai-whisper`
- [ ] Install ffmpeg binary
- [ ] Create `rutube_processor.py` module
- [ ] Create `transcriber.py` module
- [ ] Create `rutube.py` API router
- [ ] Register router in `main.py`
- [ ] Create `rutube_generator.html` frontend
- [ ] Test with sample Rutube URL
- [ ] Optimize and add error handling

---

## 🚨 Important Notes

1. **Whisper Model Download**: First run will download model (~150MB for base model)
2. **Processing Time**: 
   - Video download: 30s - 2min (depends on video size)
   - Audio extraction: 5-10s
   - Transcription: 1-3min (depends on video length)
   - Total: ~2-5 minutes for typical video
3. **Storage**: Temporary files are cleaned up automatically
4. **Language**: Auto-detected, supports Russian and English
5. **Free**: All components are free/open-source

---

## 🔄 Future Enhancements

- WebSocket progress updates
- Batch processing (multiple videos)
- Export options (PDF, DOCX)
- Video chapter detection
- Speaker diarization (who said what)
- Real-time transcription (for live videos)

