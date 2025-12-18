"""
Text-to-Speech service.
Main service for TTS functionality with caching and provider management.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import timedelta
from datetime import datetime, timezone

from .gtts_provider import GTTSProvider
from .pyttsx3_provider import Pyttsx3Provider
from ..config import DATA_DIR, TTS_CLEANUP_MAX_AGE_DAYS

logger = logging.getLogger(__name__)


class TTSService:
    """
    Main TTS service that manages providers and audio generation.
    """
    
    def __init__(
        self,
        provider: str = "auto",
        cache_enabled: bool = True,
        audio_dir: Optional[Path] = None,
        fallback_enabled: bool = True
    ):
        """
        Initialize TTS service.
        
        Args:
            provider: TTS provider name ('gtts', 'pyttsx3', or 'auto')
            cache_enabled: Enable audio caching
            audio_dir: Directory for audio files
            fallback_enabled: Enable automatic fallback to offline provider
        """
        self.provider_name = provider
        self.cache_enabled = cache_enabled
        self.fallback_enabled = fallback_enabled
        
        # Setup directories
        if audio_dir:
            self.audio_dir = audio_dir
        else:
            self.audio_dir = DATA_DIR / "audio" / "tts"
        
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache directory
        self.cache_dir = None
        if cache_enabled:
            self.cache_dir = self.audio_dir / "cache"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize providers
        self.gtts_provider = GTTSProvider(cache_dir=self.cache_dir)
        self.pyttsx3_provider = Pyttsx3Provider(cache_dir=self.cache_dir)
        
        # Set primary provider
        if provider == "gtts":
            self.provider = self.gtts_provider
            self.fallback_provider = self.pyttsx3_provider if fallback_enabled else None
        elif provider == "pyttsx3":
            self.provider = self.pyttsx3_provider
            self.fallback_provider = None
        elif provider == "auto":
            # Auto: prefer gTTS, fallback to pyttsx3
            self.provider = self.gtts_provider
            self.fallback_provider = self.pyttsx3_provider if fallback_enabled else None
        else:
            raise ValueError(
                f"Unknown TTS provider: {provider}. "
                f"Use 'gtts', 'pyttsx3', or 'auto'"
            )
        
        logger.info(
            f"TTS Service initialized: provider={provider}, "
            f"cache_enabled={cache_enabled}, fallback_enabled={fallback_enabled}, "
            f"audio_dir={self.audio_dir}"
        )
    
    def generate_audio(
        self,
        text: str,
        language: Optional[str] = None,
        voice_gender: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio from text with automatic fallback.
        
        Args:
            text: Text to convert to speech
            language: Language code ('ru', 'en', or 'auto')
            voice_gender: Voice gender ('male' or 'female')
            provider: Override provider ('gtts', 'pyttsx3', or None for auto)
            
        Returns:
            Dictionary with audio information:
            {
                'audio_id': str,
                'audio_path': Path,
                'audio_url': str,
                'language': str,
                'duration': float,
                'provider': str,
                'used_fallback': bool,
                'created_at': str
            }
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Handle language
        if language == 'auto' or language is None:
            language = None  # Will be auto-detected
        
        # Determine which provider to use
        use_provider = provider or self.provider
        used_fallback = False
        provider_name = "unknown"
        
        # Try primary provider first
        try:
            if use_provider == self.gtts_provider or provider == "gtts":
                audio_path, detected_lang = self.gtts_provider.generate_audio(
                    text=text,
                    language=language
                )
                provider_name = "gtts"
            elif use_provider == self.pyttsx3_provider or provider == "pyttsx3":
                audio_path, detected_lang = self.pyttsx3_provider.generate_audio(
                    text=text,
                    language=language,
                    voice_gender=voice_gender
                )
                provider_name = "pyttsx3"
            else:
                # Auto mode: try gTTS first, fallback to pyttsx3
                try:
                    audio_path, detected_lang = self.gtts_provider.generate_audio(
                        text=text,
                        language=language
                    )
                    provider_name = "gtts"
                except Exception as e:
                    logger.warning(
                        f"gTTS failed: {e}, trying pyttsx3 fallback"
                    )
                    if self.fallback_provider and self.fallback_provider.is_available():
                        audio_path, detected_lang = self.fallback_provider.generate_audio(
                            text=text,
                            language=language,
                            voice_gender=voice_gender
                        )
                        provider_name = "pyttsx3"
                        used_fallback = True
                    else:
                        raise RuntimeError(
                            f"Primary provider failed and fallback unavailable: {e}"
                        )
        
        except Exception as e:
            # If we have a fallback and it's enabled, try it
            if (self.fallback_enabled and 
                self.fallback_provider and 
                self.fallback_provider.is_available() and
                not used_fallback):
                logger.warning(
                    f"Primary provider failed: {e}, trying fallback"
                )
                try:
                    audio_path, detected_lang = self.fallback_provider.generate_audio(
                        text=text,
                        language=language,
                        voice_gender=voice_gender
                    )
                    provider_name = "pyttsx3"
                    used_fallback = True
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback provider also failed: {fallback_error}"
                    )
                    raise RuntimeError(
                        f"Both providers failed. Primary: {e}, "
                        f"Fallback: {fallback_error}"
                    )
            else:
                raise
        
        # Generate unique ID for this audio
        audio_id = str(uuid.uuid4())
        
        # Copy to permanent location with ID
        final_path = self.audio_dir / f"{audio_id}.mp3"
        if audio_path != final_path:
            import shutil
            shutil.copy2(audio_path, final_path)
            # Clean up temp file if it's not in cache
            if not self.cache_dir or audio_path.parent != self.cache_dir:
                try:
                    audio_path.unlink()
                except:
                    pass
        
        # Get duration
        duration_provider = (
            self.pyttsx3_provider if provider_name == "pyttsx3"
            else self.gtts_provider
        )
        duration = duration_provider.get_audio_duration(final_path)
        
        result = {
            'audio_id': audio_id,
            'audio_path': final_path,
            'audio_url': f"/api/tts/audio/{audio_id}",
            'language': detected_lang,
            'duration': duration,
            'provider': provider_name,
            'used_fallback': used_fallback,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            f"TTS audio generated: id={audio_id}, lang={detected_lang}, "
            f"provider={provider_name}, fallback={used_fallback}, "
            f"duration={duration:.2f}s"
        )
        
        return result
    
    def get_audio_path(self, audio_id: str) -> Optional[Path]:
        """
        Get path to audio file by ID.
        
        Args:
            audio_id: Audio file ID
            
        Returns:
            Path to audio file or None if not found
        """
        audio_path = self.audio_dir / f"{audio_id}.mp3"
        if audio_path.exists():
            return audio_path
        return None
    
    def cleanup_old_files(self, max_age_days: Optional[int] = None):
        """
        Clean up old audio files (both main directory and cache).
        
        Args:
            max_age_days: Maximum age in days for files to keep (default: from config)
        """
        if max_age_days is None:
            max_age_days = TTS_CLEANUP_MAX_AGE_DAYS
        import time
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        # Clean main audio directory
        if self.audio_dir.exists():
            for file_path in self.audio_dir.glob("*.mp3"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
        
        # Clean cache directory
        if self.cache_dir and self.cache_dir.exists():
            for file_path in self.cache_dir.glob("*"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete cache {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old audio files")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'cache_enabled': self.cache_enabled,
            'cache_dir': str(self.cache_dir) if self.cache_dir else None,
            'cache_files': 0,
            'cache_size_bytes': 0,
            'main_files': 0,
            'main_size_bytes': 0
        }
        
        if self.cache_dir and self.cache_dir.exists():
            for file_path in self.cache_dir.glob("*"):
                try:
                    stats['cache_files'] += 1
                    stats['cache_size_bytes'] += file_path.stat().st_size
                except:
                    pass
        
        if self.audio_dir.exists():
            for file_path in self.audio_dir.glob("*.mp3"):
                try:
                    stats['main_files'] += 1
                    stats['main_size_bytes'] += file_path.stat().st_size
                except:
                    pass
        
        return stats
