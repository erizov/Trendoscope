"""
FastAPI dependencies for dependency injection.
Provides dependency functions for service injection.
"""
from fastapi import Depends
from .container import get_container, Container


def get_tts_service(
    container: Container = Depends(get_container)
) -> 'TTSService':
    """
    Dependency function to get TTS service.

    Args:
        container: DI container instance

    Returns:
        TTSService instance
    """
    return container.tts_service


def get_email_service(
    container: Container = Depends(get_container)
) -> 'EmailService':
    """
    Dependency function to get Email service.

    Args:
        container: DI container instance

    Returns:
        EmailService instance
    """
    return container.email_service


def get_telegram_service(
    container: Container = Depends(get_container)
) -> 'TelegramService':
    """
    Dependency function to get Telegram service.

    Args:
        container: DI container instance

    Returns:
        TelegramService instance
    """
    return container.telegram_service


def get_news_service(
    container: Container = Depends(get_container)
) -> 'NewsService':
    """
    Dependency function to get NewsService.

    Args:
        container: DI container instance

    Returns:
        NewsService class (static methods)
    """
    return container.news_service


def get_cache_service(
    container: Container = Depends(get_container)
) -> 'CacheService':
    """
    Dependency function to get CacheService.

    Args:
        container: DI container instance

    Returns:
        CacheService instance
    """
    return container.cache_service
