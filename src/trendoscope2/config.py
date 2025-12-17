"""
Configuration module for Trendoscope2.
Provides backward-compatible access to settings via Pydantic Settings.
"""
from pathlib import Path
from typing import Optional

# Lazy import to avoid circular dependencies
_settings = None


def _get_settings():
    """Get settings instance (lazy import)."""
    global _settings
    if _settings is None:
        from .core.settings import get_settings
        _settings = get_settings()
    return _settings


# Base directory (for backward compatibility)
def _get_base_dir():
    """Get base directory."""
    return Path(__file__).parent.parent.parent


BASE_DIR = _get_base_dir()
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "databases").mkdir(exist_ok=True)
(DATA_DIR / "cache").mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)
(DATA_DIR / "temp").mkdir(exist_ok=True)

# Application Configuration
def _get_app_config():
    """Get application config from settings."""
    s = _get_settings()
    return s.log_level, s.environment, s.debug

LOG_LEVEL, ENVIRONMENT, DEBUG = _get_app_config()

# OpenAI Configuration
def _get_openai_config():
    """Get OpenAI config from settings."""
    s = _get_settings()
    return s.openai_api_key, s.openai_api_base

OPENAI_API_KEY, OPENAI_API_BASE = _get_openai_config()

# Anthropic Configuration
ANTHROPIC_API_KEY = _get_settings().anthropic_api_key

# Redis Configuration
def _get_redis_config():
    """Get Redis config from settings."""
    s = _get_settings()
    return s.redis.host, s.redis.port, s.redis.url or f'redis://{s.redis.host}:{s.redis.port}/0', s.redis.use_redis

REDIS_HOST, REDIS_PORT, REDIS_URL, USE_REDIS = _get_redis_config()

# Database Configuration
def _get_db_config():
    """Get database config from settings."""
    s = _get_settings()
    db_url = s.database.url or f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}"
    return s.database.type, db_url

DATABASE_TYPE, DATABASE_URL = _get_db_config()

# Qdrant Configuration
def _get_qdrant_config():
    """Get Qdrant config from settings."""
    s = _get_settings()
    return s.qdrant_url, s.qdrant_api_key

QDRANT_URL, QDRANT_API_KEY = _get_qdrant_config()

# Local LLM Configuration
OLLAMA_URL = _get_settings().ollama_url

# TTS Configuration
def _get_tts_config():
    """Get TTS config from settings."""
    s = _get_settings()
    tts_audio_dir = DATA_DIR / "audio" / "tts"
    tts_cache_dir = tts_audio_dir / "cache"
    tts_audio_dir.mkdir(parents=True, exist_ok=True)
    if s.tts.cache_enabled:
        tts_cache_dir.mkdir(parents=True, exist_ok=True)
    return (
        s.tts.provider, s.tts.cache_enabled, s.tts.fallback_enabled,
        s.tts.cache_ttl_days, tts_audio_dir, tts_cache_dir,
        s.tts.max_text_length, s.tts.cleanup_max_age_days
    )

TTS_PROVIDER, TTS_CACHE_ENABLED, TTS_FALLBACK_ENABLED, TTS_CACHE_TTL_DAYS, TTS_AUDIO_DIR, TTS_CACHE_DIR, TTS_MAX_TEXT_LENGTH, TTS_CLEANUP_MAX_AGE_DAYS = _get_tts_config()

# Email Configuration
def _get_email_config():
    """Get email config from settings."""
    s = _get_settings()
    return (
        s.email.smtp_host, s.email.smtp_port, s.email.smtp_user,
        s.email.smtp_password, s.email.from_email or s.email.smtp_user,
        s.email.enabled, s.email.rate_limit_per_minute
    )

EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD, EMAIL_FROM, EMAIL_ENABLED, EMAIL_RATE_LIMIT_PER_MINUTE = _get_email_config()

# Telegram Configuration
def _get_telegram_config():
    """Get Telegram config from settings."""
    s = _get_settings()
    return (
        s.telegram.bot_token, s.telegram.channel_id, s.telegram.enabled,
        s.telegram.post_format, s.telegram.max_post_length,
        s.telegram.rate_limit_per_minute
    )

TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TELEGRAM_ENABLED, TELEGRAM_POST_FORMAT, TELEGRAM_MAX_POST_LENGTH, TELEGRAM_RATE_LIMIT_PER_MINUTE = _get_telegram_config()

# News Database Configuration
def _get_news_db_config():
    """Get news DB config from settings."""
    s = _get_settings()
    return s.news.db_max_records, s.news.db_auto_cleanup, s.news.db_default_limit

NEWS_DB_MAX_RECORDS, NEWS_DB_AUTO_CLEANUP, NEWS_DB_DEFAULT_LIMIT = _get_news_db_config()

# News Fetching Configuration
def _get_news_fetch_config():
    """Get news fetch config from settings."""
    s = _get_settings()
    return (
        s.news.fetch_timeout, s.news.max_per_source,
        s.news.max_items_per_feed, s.news.translation_max_items
    )

NEWS_FETCH_TIMEOUT, NEWS_MAX_PER_SOURCE, NEWS_MAX_ITEMS_PER_FEED, NEWS_TRANSLATION_MAX_ITEMS = _get_news_fetch_config()

# HTTP Configuration
HTTP_MAX_KEEPALIVE_CONNECTIONS = _get_settings().http_max_keepalive_connections
