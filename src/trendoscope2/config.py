"""
Configuration module for Trendoscope2.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "databases").mkdir(exist_ok=True)
(DATA_DIR / "cache").mkdir(exist_ok=True)
(DATA_DIR / "logs").mkdir(exist_ok=True)
(DATA_DIR / "temp").mkdir(exist_ok=True)

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE: Optional[str] = os.getenv('OPENAI_API_BASE')

# Anthropic Configuration
ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')

# Redis Configuration
REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
REDIS_URL: str = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
USE_REDIS: bool = os.getenv('USE_REDIS', 'true').lower() == 'true'

# Database Configuration
DATABASE_TYPE: str = os.getenv('DATABASE_TYPE', 'sqlite')
if DATABASE_TYPE == 'sqlite':
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'databases' / 'trendoscope2.db'}"
else:
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://trendoscope:trendoscope@localhost:5432/trendoscope2')

# Application Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

# Qdrant Configuration
QDRANT_URL: str = os.getenv('QDRANT_URL', ':memory:')
QDRANT_API_KEY: Optional[str] = os.getenv('QDRANT_API_KEY')

# Local LLM Configuration
OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# TTS Configuration
TTS_PROVIDER: str = os.getenv('TTS_PROVIDER', 'auto')
TTS_CACHE_ENABLED: bool = os.getenv('TTS_CACHE_ENABLED', 'true').lower() == 'true'
TTS_FALLBACK_ENABLED: bool = os.getenv('TTS_FALLBACK_ENABLED', 'true').lower() == 'true'
TTS_CACHE_TTL_DAYS: int = int(os.getenv('TTS_CACHE_TTL_DAYS', '30'))
TTS_AUDIO_DIR: Path = DATA_DIR / "audio" / "tts"
TTS_CACHE_DIR: Path = TTS_AUDIO_DIR / "cache"
TTS_MAX_TEXT_LENGTH: int = int(os.getenv('TTS_MAX_TEXT_LENGTH', '5000'))

# Ensure TTS directories exist
TTS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
if TTS_CACHE_ENABLED:
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Email Configuration
EMAIL_SMTP_HOST: str = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
EMAIL_SMTP_PORT: int = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_SMTP_USER: Optional[str] = os.getenv('EMAIL_SMTP_USER')
EMAIL_SMTP_PASSWORD: Optional[str] = os.getenv('EMAIL_SMTP_PASSWORD')
EMAIL_FROM: Optional[str] = os.getenv('EMAIL_FROM', EMAIL_SMTP_USER)
EMAIL_ENABLED: bool = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'

# Telegram Configuration
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID: Optional[str] = os.getenv('TELEGRAM_CHANNEL_ID')
TELEGRAM_ENABLED: bool = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_POST_FORMAT: str = os.getenv('TELEGRAM_POST_FORMAT', 'markdown')
TELEGRAM_MAX_POST_LENGTH: int = int(os.getenv('TELEGRAM_MAX_POST_LENGTH', '4096'))
TELEGRAM_RATE_LIMIT_PER_MINUTE: int = int(os.getenv('TELEGRAM_RATE_LIMIT_PER_MINUTE', '20'))

# Email Rate Limiting
EMAIL_RATE_LIMIT_PER_MINUTE: int = int(os.getenv('EMAIL_RATE_LIMIT_PER_MINUTE', '10'))

# News Database Configuration
NEWS_DB_MAX_RECORDS: int = int(os.getenv('NEWS_DB_MAX_RECORDS', '10000'))
NEWS_DB_AUTO_CLEANUP: bool = os.getenv('NEWS_DB_AUTO_CLEANUP', 'true').lower() == 'true'
NEWS_DB_DEFAULT_LIMIT: int = int(os.getenv('NEWS_DB_DEFAULT_LIMIT', '20'))

# News Fetching Configuration
NEWS_FETCH_TIMEOUT: int = int(os.getenv('NEWS_FETCH_TIMEOUT', '10'))
NEWS_MAX_PER_SOURCE: int = int(os.getenv('NEWS_MAX_PER_SOURCE', '2'))
NEWS_MAX_ITEMS_PER_FEED: int = int(os.getenv('NEWS_MAX_ITEMS_PER_FEED', '10'))
NEWS_TRANSLATION_MAX_ITEMS: int = int(os.getenv('NEWS_TRANSLATION_MAX_ITEMS', '3'))

# HTTP Configuration
HTTP_MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv('HTTP_MAX_KEEPALIVE_CONNECTIONS', '20'))

# TTS Cleanup Configuration
TTS_CLEANUP_MAX_AGE_DAYS: int = int(os.getenv('TTS_CLEANUP_MAX_AGE_DAYS', '30'))

