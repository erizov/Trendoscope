"""
Text-to-Speech (TTS) module for Trendoscope2.
Provides TTS functionality using free services.
"""
from .tts_service import TTSService
from .gtts_provider import GTTSProvider
from .pyttsx3_provider import Pyttsx3Provider

__all__ = ['TTSService', 'GTTSProvider', 'Pyttsx3Provider']
