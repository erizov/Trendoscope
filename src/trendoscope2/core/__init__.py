"""
Core module for dependency injection and application infrastructure.
"""
from .container import Container
from .dependencies import (
    get_tts_service,
    get_email_service,
    get_telegram_service,
    get_news_service,
)

__all__ = [
    'Container',
    'get_tts_service',
    'get_email_service',
    'get_telegram_service',
    'get_news_service',
]
