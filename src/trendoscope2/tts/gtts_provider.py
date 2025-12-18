"""
Google Text-to-Speech (gTTS) provider.
Free TTS service with Russian and English support.
"""
import logging
from pathlib import Path
from typing import Optional, Tuple
from gtts import gTTS
import hashlib
import time

logger = logging.getLogger(__name__)


class GTTSProvider:
    """
    Google TTS provider implementation.
    
    Free TTS service that supports Russian and English.
    Note: gTTS doesn't support direct gender selection.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize gTTS provider.
        
        Args:
            cache_dir: Directory for caching audio files
        """
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text (ru or en).
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code: 'ru' or 'en'
        """
        if not text:
            return 'en'
        
        # Count Cyrillic and Latin characters
        cyrillic_chars = sum(
            1 for c in text if '\u0400' <= c <= '\u04FF'
        )
        latin_chars = sum(
            1 for c in text if c.isalpha() and ord(c) < 128
        )
        total_chars = cyrillic_chars + latin_chars
        
        if total_chars == 0:
            return 'en'
        
        cyrillic_ratio = cyrillic_chars / total_chars
        return 'ru' if cyrillic_ratio > 0.3 else 'en'
    
    def generate_audio(
        self,
        text: str,
        language: Optional[str] = None,
        slow: bool = False
    ) -> Tuple[Path, str]:
        """
        Generate audio file from text using gTTS.
        
        Args:
            text: Text to convert to speech
            language: Language code ('ru' or 'en'), auto-detect if None
            slow: Use slow speech (default: False)
            
        Returns:
            Tuple of (audio_file_path, detected_language)
            
        Raises:
            ValueError: If text is empty or too long
            RuntimeError: If TTS generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Limit text length (gTTS has limits)
        max_length = 5000
        if len(text) > max_length:
            logger.warning(
                f"Text too long ({len(text)} chars), truncating to "
                f"{max_length} chars"
            )
            text = text[:max_length] + "..."
        
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)
        
        # Normalize language code
        lang_code = 'ru' if language == 'ru' else 'en'
        
        # Check cache
        cache_path = None
        if self.cache_dir:
            text_hash = hashlib.md5(
                f"{text}_{lang_code}_{slow}".encode('utf-8')
            ).hexdigest()
            cache_path = self.cache_dir / f"{text_hash}.mp3"
            
            if cache_path.exists():
                logger.info(f"Using cached audio: {cache_path}")
                return cache_path, lang_code
        
        try:
            logger.info(
                f"Generating TTS audio: lang={lang_code}, "
                f"length={len(text)}, slow={slow}"
            )
            
            # Generate TTS
            tts = gTTS(text=text, lang=lang_code, slow=slow)
            
            # Save to file
            if cache_path:
                output_path = cache_path
            else:
                # Use temp file if no cache
                import tempfile
                temp_dir = Path(tempfile.gettempdir())
                output_path = temp_dir / f"tts_{int(time.time())}.mp3"
            
            tts.save(str(output_path))
            
            logger.info(
                f"TTS audio generated: {output_path}, "
                f"size={output_path.stat().st_size} bytes"
            )
            
            return output_path, lang_code
            
        except Exception as e:
            logger.error(f"Failed to generate TTS audio: {e}", exc_info=True)
            raise RuntimeError(f"TTS generation failed: {str(e)}")
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(str(audio_path))
            return len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            logger.warning(
                f"Could not get audio duration: {e}, using estimate"
            )
            # Rough estimate: ~150 words per minute
            return 0.0
