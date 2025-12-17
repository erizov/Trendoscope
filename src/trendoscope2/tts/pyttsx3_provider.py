"""
pyttsx3 TTS provider for offline text-to-speech.
Uses system voices (Windows SAPI5, Linux espeak, macOS NSSpeechSynthesizer).
"""
import logging
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import time

logger = logging.getLogger(__name__)


class Pyttsx3Provider:
    """
    pyttsx3 TTS provider implementation.
    
    Offline TTS using system voices.
    Supports voice gender selection where available.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize pyttsx3 provider.
        
        Args:
            cache_dir: Directory for caching audio files
        """
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize engine
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.available = True
            
            # Get available voices
            self.voices = self.engine.getProperty('voices')
            logger.info(
                f"pyttsx3 initialized: {len(self.voices)} voices available"
            )
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {e}")
            self.engine = None
            self.available = False
            self.voices = []
    
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
    
    def _select_voice_by_gender(
        self,
        gender: Optional[str] = None,
        language: str = 'en'
    ) -> Optional[int]:
        """
        Select voice by gender if available.
        
        Args:
            gender: 'male' or 'female'
            language: Language code ('ru' or 'en')
            
        Returns:
            Voice index or None
        """
        if not self.voices or not gender:
            return None
        
        # Try to find voice matching gender
        # Note: Voice gender detection is platform-dependent
        gender_lower = gender.lower()
        
        for i, voice in enumerate(self.voices):
            voice_name = str(voice.name).lower()
            voice_id = str(voice.id).lower()
            
            # Check for gender indicators in voice name/id
            # This is heuristic and may not work on all systems
            if gender_lower == 'female':
                if any(indicator in voice_name or indicator in voice_id
                       for indicator in ['female', 'woman', 'zira', 'susan',
                                        'kate', 'samantha']):
                    # Also check language if possible
                    if language == 'ru' and 'russian' in voice_id:
                        return i
                    elif language == 'en' and ('english' in voice_id or
                                               'en' in voice_id):
                        return i
                    elif language == 'ru' or language == 'en':
                        return i  # Fallback to any matching gender
            
            elif gender_lower == 'male':
                if any(indicator in voice_name or indicator in voice_id
                       for indicator in ['male', 'man', 'david', 'mark',
                                        'james', 'richard']):
                    if language == 'ru' and 'russian' in voice_id:
                        return i
                    elif language == 'en' and ('english' in voice_id or
                                               'en' in voice_id):
                        return i
                    elif language == 'ru' or language == 'en':
                        return i  # Fallback to any matching gender
        
        return None
    
    def generate_audio(
        self,
        text: str,
        language: Optional[str] = None,
        voice_gender: Optional[str] = None,
        slow: bool = False
    ) -> Tuple[Path, str]:
        """
        Generate audio file from text using pyttsx3.
        
        Args:
            text: Text to convert to speech
            language: Language code ('ru' or 'en'), auto-detect if None
            voice_gender: Voice gender ('male' or 'female')
            slow: Use slow speech (default: False)
            
        Returns:
            Tuple of (audio_file_path, detected_language)
            
        Raises:
            ValueError: If text is empty
            RuntimeError: If TTS generation fails
        """
        if not self.available or not self.engine:
            raise RuntimeError("pyttsx3 is not available")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Limit text length
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
        import hashlib
        cache_path = None
        if self.cache_dir:
            text_hash = hashlib.md5(
                f"{text}_{lang_code}_{voice_gender}_{slow}".encode('utf-8')
            ).hexdigest()
            cache_path = self.cache_dir / f"pyttsx3_{text_hash}.wav"
            
            if cache_path.exists():
                logger.info(f"Using cached audio: {cache_path}")
                # Convert to MP3 if needed
                mp3_path = self._convert_to_mp3(cache_path)
                return mp3_path, lang_code
        
        try:
            logger.info(
                f"Generating TTS audio with pyttsx3: lang={lang_code}, "
                f"length={len(text)}, gender={voice_gender}"
            )
            
            # Set voice if gender specified
            voice_index = self._select_voice_by_gender(voice_gender, lang_code)
            if voice_index is not None:
                self.engine.setProperty('voice', self.voices[voice_index].id)
                logger.info(f"Selected voice: {self.voices[voice_index].name}")
            
            # Set speech rate (words per minute)
            # Normal: ~150-200 WPM, Slow: ~100-120 WPM
            rate = 150 if not slow else 100
            self.engine.setProperty('rate', rate)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)
            
            # Generate audio to temporary WAV file
            if cache_path:
                output_path = cache_path
            else:
                temp_dir = Path(tempfile.gettempdir())
                output_path = temp_dir / f"pyttsx3_{int(time.time())}.wav"
            
            # Save to file
            self.engine.save_to_file(text, str(output_path))
            
            # Run with timeout to prevent hanging
            import threading
            import time as time_module
            
            def run_engine():
                """Run engine in separate thread."""
                try:
                    self.engine.runAndWait()
                except Exception as e:
                    logger.error(f"pyttsx3 runAndWait error: {e}")
            
            engine_thread = threading.Thread(target=run_engine, daemon=True)
            engine_thread.start()
            engine_thread.join(timeout=60)  # 60 second timeout for voice selection
            
            if engine_thread.is_alive():
                logger.warning("pyttsx3 runAndWait timed out after 60s, waiting for file...")
                # Give it a bit more time for file creation
                time_module.sleep(3)
            
            # Wait for file to be created
            max_wait = 10  # seconds
            waited = 0
            while not output_path.exists() and waited < max_wait:
                time_module.sleep(0.1)
                waited += 0.1
            
            if not output_path.exists():
                raise RuntimeError(
                    f"Audio file was not created after {max_wait} seconds. "
                    "pyttsx3 may have timed out or failed."
                )
            
            logger.info(
                f"pyttsx3 audio generated: {output_path}, "
                f"size={output_path.stat().st_size} bytes"
            )
            
            # Convert to MP3 for web compatibility
            mp3_path = self._convert_to_mp3(output_path)
            
            return mp3_path, lang_code
            
        except Exception as e:
            logger.error(
                f"Failed to generate pyttsx3 audio: {e}",
                exc_info=True
            )
            raise RuntimeError(f"pyttsx3 TTS generation failed: {str(e)}")
    
    def _convert_to_mp3(self, wav_path: Path) -> Path:
        """
        Convert WAV file to MP3.
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Path to MP3 file
        """
        try:
            from pydub import AudioSegment
            
            mp3_path = wav_path.with_suffix('.mp3')
            
            # Convert WAV to MP3
            audio = AudioSegment.from_wav(str(wav_path))
            audio.export(str(mp3_path), format="mp3")
            
            # Remove original WAV if it's not in cache
            if self.cache_dir and wav_path.parent != self.cache_dir:
                try:
                    wav_path.unlink()
                except:
                    pass
            
            return mp3_path
            
        except Exception as e:
            logger.warning(
                f"Could not convert to MP3: {e}, using WAV"
            )
            return wav_path
    
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
            
            if audio_path.suffix == '.mp3':
                audio = AudioSegment.from_mp3(str(audio_path))
            else:
                audio = AudioSegment.from_wav(str(audio_path))
            
            return len(audio) / 1000.0  # Convert to seconds
            
        except Exception as e:
            logger.warning(
                f"Could not get audio duration: {e}, using estimate"
            )
            return 0.0
    
    def is_available(self) -> bool:
        """
        Check if pyttsx3 is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.available
