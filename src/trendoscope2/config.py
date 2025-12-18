"""
Configuration module for Trendoscope2.
Provides backward-compatible access to settings via Pydantic Settings.
Uses __getattr__ for lazy loading to avoid circular imports.
"""
from pathlib import Path
from typing import Optional, Any

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


# Configuration variable mapping
_CONFIG_MAP = {
    # Application
    'LOG_LEVEL': lambda s: s.log_level,
    'ENVIRONMENT': lambda s: s.environment,
    'DEBUG': lambda s: s.debug,
    
    # OpenAI
    'OPENAI_API_KEY': lambda s: s.openai_api_key,
    'OPENAI_API_BASE': lambda s: s.openai_api_base,
    
    # Anthropic
    'ANTHROPIC_API_KEY': lambda s: s.anthropic_api_key,
    
    # Redis
    'REDIS_HOST': lambda s: s.redis.host,
    'REDIS_PORT': lambda s: s.redis.port,
    'REDIS_URL': lambda s: s.redis.url or f'redis://{s.redis.host}:{s.redis.port}/0',
    'USE_REDIS': lambda s: s.redis.use_redis,
    
    # Database
    'DATABASE_TYPE': lambda s: s.database.type,
    'DATABASE_URL': lambda s: s.database.url or f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}",
    
    # Qdrant
    'QDRANT_URL': lambda s: s.qdrant_url,
    'QDRANT_API_KEY': lambda s: s.qdrant_api_key,
    
    # Local LLM
    'OLLAMA_URL': lambda s: s.ollama_url,
    
    # TTS
    'TTS_PROVIDER': lambda s: s.tts.provider,
    'TTS_CACHE_ENABLED': lambda s: s.tts.cache_enabled,
    'TTS_FALLBACK_ENABLED': lambda s: s.tts.fallback_enabled,
    'TTS_CACHE_TTL_DAYS': lambda s: s.tts.cache_ttl_days,
    'TTS_AUDIO_DIR': lambda s: DATA_DIR / "audio" / "tts",
    'TTS_CACHE_DIR': lambda s: DATA_DIR / "audio" / "tts" / "cache",
    'TTS_MAX_TEXT_LENGTH': lambda s: s.tts.max_text_length,
    'TTS_CLEANUP_MAX_AGE_DAYS': lambda s: s.tts.cleanup_max_age_days,
    
    # Email
    'EMAIL_SMTP_HOST': lambda s: s.email.smtp_host,
    'EMAIL_SMTP_PORT': lambda s: s.email.smtp_port,
    'EMAIL_SMTP_USER': lambda s: s.email.smtp_user,
    'EMAIL_SMTP_PASSWORD': lambda s: s.email.smtp_password,
    'EMAIL_FROM': lambda s: s.email.from_email or s.email.smtp_user,
    'EMAIL_ENABLED': lambda s: s.email.enabled,
    'EMAIL_RATE_LIMIT_PER_MINUTE': lambda s: s.email.rate_limit_per_minute,
    
    # Telegram
    'TELEGRAM_BOT_TOKEN': lambda s: s.telegram.bot_token,
    'TELEGRAM_CHANNEL_ID': lambda s: s.telegram.channel_id,
    'TELEGRAM_ENABLED': lambda s: s.telegram.enabled,
    'TELEGRAM_POST_FORMAT': lambda s: s.telegram.post_format,
    'TELEGRAM_MAX_POST_LENGTH': lambda s: s.telegram.max_post_length,
    'TELEGRAM_RATE_LIMIT_PER_MINUTE': lambda s: s.telegram.rate_limit_per_minute,
    
    # News DB
    'NEWS_DB_MAX_RECORDS': lambda s: s.news.db_max_records,
    'NEWS_DB_AUTO_CLEANUP': lambda s: s.news.db_auto_cleanup,
    'NEWS_DB_DEFAULT_LIMIT': lambda s: s.news.db_default_limit,
    
    # News Fetching
    'NEWS_FETCH_TIMEOUT': lambda s: s.news.fetch_timeout,
    'NEWS_MAX_PER_SOURCE': lambda s: s.news.max_per_source,
    'NEWS_MAX_ITEMS_PER_FEED': lambda s: s.news.max_items_per_feed,
    'NEWS_TRANSLATION_MAX_ITEMS': lambda s: s.news.translation_max_items,
    
    # HTTP
    'HTTP_MAX_KEEPALIVE_CONNECTIONS': lambda s: s.http_max_keepalive_connections,
}

# Cache for computed values
_config_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """
    Lazy loading of configuration variables.
    
    Args:
        name: Configuration variable name
        
    Returns:
        Configuration value
    """
    if name in _CONFIG_MAP:
        if name not in _config_cache:
            s = _get_settings()
            value = _CONFIG_MAP[name](s)
            # Special handling for TTS directories
            if name == 'TTS_AUDIO_DIR':
                value.mkdir(parents=True, exist_ok=True)
            elif name == 'TTS_CACHE_DIR':
                s = _get_settings()
                if s.tts.cache_enabled:
                    value.mkdir(parents=True, exist_ok=True)
            _config_cache[name] = value
        return _config_cache[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
