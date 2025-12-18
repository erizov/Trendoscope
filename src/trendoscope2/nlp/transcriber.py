"""
Audio transcription using OpenAI Whisper.
Free, local, supports multiple languages.
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

logger = logging.getLogger(__name__)

# Global model instance (lazy load)
_whisper_model = None
_model_size = None


def get_whisper_model(model_size: str = "base"):
    """
    Get or load Whisper model.
    
    Model sizes: tiny, base, small, medium, large
    - tiny: Fastest, least accurate (~39MB)
    - base: Good balance, recommended (~74MB)
    - small: Better accuracy (~244MB)
    - medium: High accuracy (~769MB)
    - large: Best accuracy, slowest (~1550MB)
    
    Args:
        model_size: Model size to use
        
    Returns:
        Whisper model instance
        
    Raises:
        ImportError: If openai-whisper is not installed
    """
    global _whisper_model, _model_size
    
    if not WHISPER_AVAILABLE:
        raise ImportError(
            "openai-whisper not installed. "
            "Run: pip install openai-whisper"
        )
    
    # Reload model if size changed
    if _whisper_model is None or _model_size != model_size:
        logger.info(f"Loading Whisper model: {model_size}")
        _whisper_model = whisper.load_model(model_size)
        _model_size = model_size
        logger.info("Whisper model loaded successfully")
    
    return _whisper_model


def transcribe_audio(
    audio_path: Path,
    language: Optional[str] = None,
    model_size: str = "base"
) -> Dict[str, Any]:
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
        - full_result: Complete Whisper result
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    model = get_whisper_model(model_size)
    
    # Transcribe
    logger.info(f"Transcribing audio: {audio_path}")
    logger.info(f"Audio file size: {audio_path.stat().st_size} bytes")
    
    result = model.transcribe(
        str(audio_path),
        language=language,
        task="transcribe"
    )
    
    # Clean up transcript
    text = result["text"].strip()
    
    logger.info(
        f"Transcription complete. Language: {result['language']}, "
        f"Text length: {len(text)} characters"
    )
    
    return {
        "text": text,
        "language": result["language"],
        "segments": result.get("segments", []),
        "full_result": result
    }


def detect_language(audio_path: Path, model_size: str = "base") -> str:
    """
    Detect language of audio file.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size for detection
        
    Returns:
        Detected language code (e.g., 'ru', 'en')
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    model = get_whisper_model(model_size)
    
    try:
        import whisper
        audio = whisper.load_audio(str(audio_path))
        audio = whisper.pad_or_trim(audio)
        
        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Detect language
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        logger.info(f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2%})")
        
        return detected_lang
        
    except Exception as e:
        logger.warning(f"Language detection failed: {e}, defaulting to auto-detect")
        return None  # Will auto-detect during transcription

