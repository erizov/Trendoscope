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
LOG_LEVEL = _settings.log_level
ENVIRONMENT = _settings.environment
DEBUG = _settings.debug

# OpenAI Configuration
OPENAI_API_KEY = _settings.openai_api_key
OPENAI_API_BASE = _settings.openai_api_base

# Anthropic Configuration
ANTHROPIC_API_KEY = _settings.anthropic_api_key

# Redis Configuration
REDIS_HOST = _settings.redis.host
REDIS_PORT = _settings.redis.port
REDIS_URL = _settings.redis.url or f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
USE_REDIS = _settings.redis.use_redis

# Database Configuration
DATABASE_TYPE = _settings.database.type
DATABASE_URL = _settings.database.url or (
    f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}"
)

# Qdrant Configuration
QDRANT_URL = _settings.qdrant_url
QDRANT_API_KEY = _settings.qdrant_api_key

# Local LLM Configuration
OLLAMA_URL = _settings.ollama_url

# TTS Configuration
TTS_PROVIDER = _settings.tts.provider
TTS_CACHE_ENABLED = _settings.tts.cache_enabled
TTS_FALLBACK_ENABLED = _settings.tts.fallback_enabled
TTS_CACHE_TTL_DAYS = _settings.tts.cache_ttl_days
TTS_AUDIO_DIR = DATA_DIR / "audio" / "tts"
TTS_CACHE_DIR = TTS_AUDIO_DIR / "cache"
TTS_MAX_TEXT_LENGTH = _settings.tts.max_text_length
TTS_CLEANUP_MAX_AGE_DAYS = _settings.tts.cleanup_max_age_days

# Email Configuration
EMAIL_SMTP_HOST = _settings.email.smtp_host
EMAIL_SMTP_PORT = _settings.email.smtp_port
EMAIL_SMTP_USER = _settings.email.smtp_user
EMAIL_SMTP_PASSWORD = _settings.email.smtp_password
EMAIL_FROM = _settings.email.from_email or _settings.email.smtp_user
EMAIL_ENABLED = _settings.email.enabled
EMAIL_RATE_LIMIT_PER_MINUTE = _settings.email.rate_limit_per_minute

# Telegram Configuration
TELEGRAM_BOT_TOKEN = _settings.telegram.bot_token
TELEGRAM_CHANNEL_ID = _settings.telegram.channel_id
TELEGRAM_ENABLED = _settings.telegram.enabled
TELEGRAM_POST_FORMAT = _settings.telegram.post_format
TELEGRAM_MAX_POST_LENGTH = _settings.telegram.max_post_length
TELEGRAM_RATE_LIMIT_PER_MINUTE = _settings.telegram.rate_limit_per_minute

# News Database Configuration
NEWS_DB_MAX_RECORDS = _settings.news.db_max_records
NEWS_DB_AUTO_CLEANUP = _settings.news.db_auto_cleanup
NEWS_DB_DEFAULT_LIMIT = _settings.news.db_default_limit

# News Fetching Configuration
NEWS_FETCH_TIMEOUT = _settings.news.fetch_timeout
NEWS_MAX_PER_SOURCE = _settings.news.max_per_source
NEWS_MAX_ITEMS_PER_FEED = _settings.news.max_items_per_feed
NEWS_TRANSLATION_MAX_ITEMS = _settings.news.translation_max_items

# HTTP Configuration
HTTP_MAX_KEEPALIVE_CONNECTIONS = _settings.http_max_keepalive_connections
