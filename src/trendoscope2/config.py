"""
Configuration module for Trendoscope2.
Provides backward-compatible access to settings via Pydantic Settings.
All variables are lazy-loaded to avoid circular imports.
"""
from pathlib import Path
from typing import Optional

# Base directory (computed directly, no import needed)
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "databases").mkdir(exist_ok=True)
(DATA_DIR / "cache").mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)
(DATA_DIR / "temp").mkdir(exist_ok=True)

# Lazy import to avoid circular dependencies
_settings = None


def _get_settings():
    """Get settings instance (lazy import)."""
    global _settings
    if _settings is None:
        from .core.settings import get_settings
        _settings = get_settings()
    return _settings


# Lazy property functions for all config variables
def _get_app_config():
    """Get application config from settings."""
    s = _get_settings()
    return s.log_level, s.environment, s.debug

def _get_openai_config():
    """Get OpenAI config from settings."""
    s = _get_settings()
    return s.openai_api_key, s.openai_api_base

def _get_redis_config():
    """Get Redis config from settings."""
    s = _get_settings()
    return s.redis.host, s.redis.port, s.redis.url or f'redis://{s.redis.host}:{s.redis.port}/0', s.redis.use_redis

def _get_db_config():
    """Get database config from settings."""
    s = _get_settings()
    db_url = s.database.url or f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}"
    return s.database.type, db_url

def _get_qdrant_config():
    """Get Qdrant config from settings."""
    s = _get_settings()
    return s.qdrant_url, s.qdrant_api_key

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

def _get_email_config():
    """Get email config from settings."""
    s = _get_settings()
    return (
        s.email.smtp_host, s.email.smtp_port, s.email.smtp_user,
        s.email.smtp_password, s.email.from_email or s.email.smtp_user,
        s.email.enabled, s.email.rate_limit_per_minute
    )

def _get_telegram_config():
    """Get Telegram config from settings."""
    s = _get_settings()
    return (
        s.telegram.bot_token, s.telegram.channel_id, s.telegram.enabled,
        s.telegram.post_format, s.telegram.max_post_length,
        s.telegram.rate_limit_per_minute
    )

def _get_news_db_config():
    """Get news DB config from settings."""
    s = _get_settings()
    return s.news.db_max_records, s.news.db_auto_cleanup, s.news.db_default_limit

def _get_news_fetch_config():
    """Get news fetch config from settings."""
    s = _get_settings()
    return (
        s.news.fetch_timeout, s.news.max_per_source,
        s.news.max_items_per_feed, s.news.translation_max_items
    )


# Application Configuration (lazy properties)
@property
def LOG_LEVEL():
    return _get_app_config()[0]

@property
def ENVIRONMENT():
    return _get_app_config()[1]

@property
def DEBUG():
    return _get_app_config()[2]

# OpenAI Configuration
@property
def OPENAI_API_KEY():
    return _get_openai_config()[0]

@property
def OPENAI_API_BASE():
    return _get_openai_config()[1]

# Anthropic Configuration
@property
def ANTHROPIC_API_KEY():
    return _get_settings().anthropic_api_key

# Redis Configuration
@property
def REDIS_HOST():
    return _get_redis_config()[0]

@property
def REDIS_PORT():
    return _get_redis_config()[1]

@property
def REDIS_URL():
    return _get_redis_config()[2]

@property
def USE_REDIS():
    return _get_redis_config()[3]

# Database Configuration
@property
def DATABASE_TYPE():
    return _get_db_config()[0]

@property
def DATABASE_URL():
    return _get_db_config()[1]

# Qdrant Configuration
@property
def QDRANT_URL():
    return _get_qdrant_config()[0]

@property
def QDRANT_API_KEY():
    return _get_qdrant_config()[1]

# Local LLM Configuration
@property
def OLLAMA_URL():
    return _get_settings().ollama_url

# TTS Configuration
@property
def TTS_PROVIDER():
    return _get_tts_config()[0]

@property
def TTS_CACHE_ENABLED():
    return _get_tts_config()[1]

@property
def TTS_FALLBACK_ENABLED():
    return _get_tts_config()[2]

@property
def TTS_CACHE_TTL_DAYS():
    return _get_tts_config()[3]

@property
def TTS_AUDIO_DIR():
    return _get_tts_config()[4]

@property
def TTS_CACHE_DIR():
    return _get_tts_config()[5]

@property
def TTS_MAX_TEXT_LENGTH():
    return _get_tts_config()[6]

@property
def TTS_CLEANUP_MAX_AGE_DAYS():
    return _get_tts_config()[7]

# Email Configuration
@property
def EMAIL_SMTP_HOST():
    return _get_email_config()[0]

@property
def EMAIL_SMTP_PORT():
    return _get_email_config()[1]

@property
def EMAIL_SMTP_USER():
    return _get_email_config()[2]

@property
def EMAIL_SMTP_PASSWORD():
    return _get_email_config()[3]

@property
def EMAIL_FROM():
    return _get_email_config()[4]

@property
def EMAIL_ENABLED():
    return _get_email_config()[5]

@property
def EMAIL_RATE_LIMIT_PER_MINUTE():
    return _get_email_config()[6]

# Telegram Configuration
@property
def TELEGRAM_BOT_TOKEN():
    return _get_telegram_config()[0]

@property
def TELEGRAM_CHANNEL_ID():
    return _get_telegram_config()[1]

@property
def TELEGRAM_ENABLED():
    return _get_telegram_config()[2]

@property
def TELEGRAM_POST_FORMAT():
    return _get_telegram_config()[3]

@property
def TELEGRAM_MAX_POST_LENGTH():
    return _get_telegram_config()[4]

@property
def TELEGRAM_RATE_LIMIT_PER_MINUTE():
    return _get_telegram_config()[5]

# News Database Configuration
@property
def NEWS_DB_MAX_RECORDS():
    return _get_news_db_config()[0]

@property
def NEWS_DB_AUTO_CLEANUP():
    return _get_news_db_config()[1]

@property
def NEWS_DB_DEFAULT_LIMIT():
    return _get_news_db_config()[2]

# News Fetching Configuration
@property
def NEWS_FETCH_TIMEOUT():
    return _get_news_fetch_config()[0]

@property
def NEWS_MAX_PER_SOURCE():
    return _get_news_fetch_config()[1]

@property
def NEWS_MAX_ITEMS_PER_FEED():
    return _get_news_fetch_config()[2]

@property
def NEWS_TRANSLATION_MAX_ITEMS():
    return _get_news_fetch_config()[3]

# HTTP Configuration
@property
def HTTP_MAX_KEEPALIVE_CONNECTIONS():
    return _get_settings().http_max_keepalive_connections
