"""
Pydantic Settings for type-safe configuration.
Replaces flat config.py with structured, validated settings.
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class TTSSettings(BaseSettings):
    """TTS configuration settings."""
    
    provider: str = Field(default='auto', description='TTS provider')
    cache_enabled: bool = Field(default=True, description='Enable TTS cache')
    fallback_enabled: bool = Field(default=True, description='Enable fallback')
    cache_ttl_days: int = Field(default=30, ge=1, description='Cache TTL in days')
    max_text_length: int = Field(default=5000, ge=1, le=100000, description='Max text length')
    cleanup_max_age_days: int = Field(default=30, ge=1, description='Cleanup max age')
    
    model_config = SettingsConfigDict(
        env_prefix='TTS_',
        case_sensitive=False
    )


class EmailSettings(BaseSettings):
    """Email configuration settings."""
    
    smtp_host: str = Field(default='smtp.gmail.com', description='SMTP host')
    smtp_port: int = Field(default=587, ge=1, le=65535, description='SMTP port')
    smtp_user: Optional[str] = Field(default=None, description='SMTP username')
    smtp_password: Optional[str] = Field(default=None, description='SMTP password')
    from_email: Optional[str] = Field(default=None, description='From email address')
    enabled: bool = Field(default=False, description='Enable email service')
    rate_limit_per_minute: int = Field(
        default=10, ge=1, description='Rate limit per minute'
    )
    
    model_config = SettingsConfigDict(
        env_prefix='EMAIL_',
        case_sensitive=False
    )
    
    def model_post_init(self, __context):
        """Set from_email to smtp_user if not provided."""
        if self.from_email is None and self.smtp_user:
            object.__setattr__(self, 'from_email', self.smtp_user)


class TelegramSettings(BaseSettings):
    """Telegram configuration settings."""
    
    bot_token: Optional[str] = Field(default=None, description='Bot token')
    channel_id: Optional[str] = Field(default=None, description='Channel ID')
    enabled: bool = Field(default=False, description='Enable Telegram service')
    post_format: str = Field(default='markdown', description='Post format')
    max_post_length: int = Field(
        default=4096, ge=1, le=10000, description='Max post length'
    )
    rate_limit_per_minute: int = Field(
        default=20, ge=1, description='Rate limit per minute'
    )
    
    model_config = SettingsConfigDict(
        env_prefix='TELEGRAM_',
        case_sensitive=False
    )


class NewsSettings(BaseSettings):
    """News configuration settings."""
    
    db_max_records: int = Field(
        default=10000, ge=1000, description='Max records in DB'
    )
    db_auto_cleanup: bool = Field(
        default=True, description='Auto cleanup old records'
    )
    db_default_limit: int = Field(
        default=20, ge=5, le=100, description='Default limit for queries'
    )
    fetch_timeout: int = Field(
        default=10, ge=1, le=300, description='Fetch timeout in seconds'
    )
    max_per_source: int = Field(
        default=2, ge=1, le=50, description='Max items per source'
    )
    max_items_per_feed: int = Field(
        default=10, ge=1, le=100, description='Max items per feed'
    )
    translation_max_items: int = Field(
        default=3, ge=1, le=20, description='Max items to translate'
    )
    
    model_config = SettingsConfigDict(
        env_prefix='NEWS_',
        case_sensitive=False
    )


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    type: str = Field(default='sqlite', description='Database type')
    url: Optional[str] = Field(default=None, description='Database URL')
    
    model_config = SettingsConfigDict(
        env_prefix='DATABASE_',
        case_sensitive=False
    )


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default='localhost', description='Redis host')
    port: int = Field(default=6379, ge=1, le=65535, description='Redis port')
    url: Optional[str] = Field(default=None, description='Redis URL')
    use_redis: bool = Field(default=True, description='Use Redis')
    
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
        case_sensitive=False
    )
    
    def model_post_init(self, __context):
        """Set Redis URL from host and port if not provided."""
        if self.url is None:
            self.url = f'redis://{self.host}:{self.port}/0'


class AppSettings(BaseSettings):
    """Main application settings."""
    
    # Base paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent
    )
    data_dir: Path = Field(default_factory=lambda: Path())
    
    # Application
    log_level: str = Field(default='INFO', description='Log level')
    environment: str = Field(default='development', description='Environment')
    debug: bool = Field(default=False, description='Debug mode')
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description='OpenAI API key')
    openai_api_base: Optional[str] = Field(default=None, description='OpenAI API base')
    anthropic_api_key: Optional[str] = Field(
        default=None, description='Anthropic API key'
    )
    
    # External services
    qdrant_url: str = Field(default=':memory:', description='Qdrant URL')
    qdrant_api_key: Optional[str] = Field(default=None, description='Qdrant API key')
    ollama_url: str = Field(
        default='http://localhost:11434', description='Ollama URL'
    )
    
    # HTTP
    http_max_keepalive_connections: int = Field(
        default=20, ge=1, description='Max keepalive connections'
    )
    
    # Sub-settings
    tts: TTSSettings = Field(default_factory=TTSSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    news: NewsSettings = Field(default_factory=NewsSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and set up data directories."""
        super().__init__(**kwargs)
        # Set data_dir if not provided
        if not self.data_dir or str(self.data_dir) == '.':
            self.data_dir = self.base_dir / 'data'
        
        # Ensure data directories exist
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / 'databases').mkdir(exist_ok=True)
        (self.data_dir / 'cache').mkdir(exist_ok=True)
        (self.data_dir / 'logs').mkdir(exist_ok=True)
        (self.data_dir / 'temp').mkdir(exist_ok=True)
        
        # Set up TTS directories
        tts_audio_dir = self.data_dir / 'audio' / 'tts'
        tts_audio_dir.mkdir(parents=True, exist_ok=True)
        if self.tts.cache_enabled:
            (tts_audio_dir / 'cache').mkdir(parents=True, exist_ok=True)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    def model_post_init(self, __context):
        """Set database URL after initialization."""
        if self.database.type == 'sqlite' and not self.database.url:
            self.database.url = (
                f"sqlite:///{self.data_dir / 'databases' / 'trendoscope2.db'}"
            )
        elif not self.database.url:
            self.database.url = (
                'postgresql://trendoscope:trendoscope@localhost:5432/trendoscope2'
            )


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """
    Get global settings instance (singleton pattern).
    
    Returns:
        AppSettings instance
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reset_settings():
    """Reset global settings (useful for testing)."""
    global _settings
    _settings = None
