"""
Dependency injection container.
Manages service instances and their lifecycle.
"""
import logging
from typing import Optional
from ..tts.tts_service import TTSService
from ..services.email_service import EmailService
from ..services.telegram_service import TelegramService
from ..services.news_service import NewsService
from ..ingest.news_sources_async import AsyncNewsAggregator
from ..storage.news_db import NewsDatabase
from ..config import (
    TTS_PROVIDER, TTS_CACHE_ENABLED, TTS_FALLBACK_ENABLED,
    EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_SMTP_USER,
    EMAIL_SMTP_PASSWORD, EMAIL_FROM, EMAIL_RATE_LIMIT_PER_MINUTE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID,
    TELEGRAM_RATE_LIMIT_PER_MINUTE, NEWS_FETCH_TIMEOUT
)

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency injection container.
    Manages service instances as singletons.
    """

    def __init__(self):
        """Initialize container with all service instances."""
        self._tts_service: Optional[TTSService] = None
        self._email_service: Optional[EmailService] = None
        self._telegram_service: Optional[TelegramService] = None
        self._news_service: Optional[NewsService] = None
        self._news_aggregator: Optional[AsyncNewsAggregator] = None
        self._news_db: Optional[NewsDatabase] = None

    @property
    def tts_service(self) -> TTSService:
        """Get or create TTS service instance."""
        if self._tts_service is None:
            self._tts_service = TTSService(
                provider=TTS_PROVIDER,
                cache_enabled=TTS_CACHE_ENABLED,
                fallback_enabled=TTS_FALLBACK_ENABLED
            )
            logger.debug("Created TTS service instance")
        return self._tts_service

    @property
    def email_service(self) -> EmailService:
        """Get or create Email service instance."""
        if self._email_service is None:
            self._email_service = EmailService(
                smtp_host=EMAIL_SMTP_HOST,
                smtp_port=EMAIL_SMTP_PORT,
                smtp_user=EMAIL_SMTP_USER,
                smtp_password=EMAIL_SMTP_PASSWORD,
                from_email=EMAIL_FROM,
                rate_limit_per_minute=EMAIL_RATE_LIMIT_PER_MINUTE
            )
            logger.debug("Created Email service instance")
        return self._email_service

    @property
    def telegram_service(self) -> TelegramService:
        """Get or create Telegram service instance."""
        if self._telegram_service is None:
            self._telegram_service = TelegramService(
                bot_token=TELEGRAM_BOT_TOKEN,
                default_channel_id=TELEGRAM_CHANNEL_ID,
                rate_limit_per_minute=TELEGRAM_RATE_LIMIT_PER_MINUTE
            )
            logger.debug("Created Telegram service instance")
        return self._telegram_service

    @property
    def news_service(self) -> NewsService:
        """Get NewsService (static class, no instance needed)."""
        return NewsService

    @property
    def news_aggregator(self) -> AsyncNewsAggregator:
        """Get or create NewsAggregator instance."""
        if self._news_aggregator is None:
            self._news_aggregator = AsyncNewsAggregator(
                timeout=NEWS_FETCH_TIMEOUT
            )
            logger.debug("Created NewsAggregator instance")
        return self._news_aggregator

    @property
    def news_db(self) -> NewsDatabase:
        """Get or create NewsDatabase instance."""
        if self._news_db is None:
            self._news_db = NewsDatabase()
            logger.debug("Created NewsDatabase instance")
        return self._news_db

    def reset(self):
        """Reset all service instances (useful for testing)."""
        self._tts_service = None
        self._email_service = None
        self._telegram_service = None
        self._news_service = None
        self._news_aggregator = None
        self._news_db = None
        logger.debug("Reset all service instances")


# Global container instance (singleton)
_container: Optional[Container] = None


def get_container() -> Container:
    """
    Get global container instance (singleton pattern).

    Returns:
        Container instance
    """
    global _container
    if _container is None:
        _container = Container()
        logger.debug("Created global container instance")
    return _container


def reset_container():
    """Reset global container (useful for testing)."""
    global _container
    if _container is not None:
        _container.reset()
    _container = None
