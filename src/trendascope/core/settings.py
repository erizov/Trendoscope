"""
Centralized configuration management.
Uses Pydantic for validation and type safety.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    news_db_path: str = Field(
        default="data/news.db",
        description="Path to news SQLite database"
    )
    post_storage_path: str = Field(
        default="data/posts",
        description="Path to post storage directory"
    )
    connection_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    
    class Config:
        env_prefix = "DB_"
        extra = "ignore"  # Ignore extra fields


class LLMSettings(BaseSettings):
    """LLM provider configuration."""
    
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_api_base: Optional[str] = Field(
        default=None,
        description="OpenAI API base URL (for proxy support)"
    )
    openai_model: str = Field(
        default="gpt-3.5-turbo",
        description="Default OpenAI model"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    default_provider: str = Field(
        default="free",
        description="Default LLM provider (free, openai, anthropic, demo)"
    )
    max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens per request"
    )
    temperature: float = Field(
        default=0.8,
        ge=0.0,
        le=2.0,
        description="Default temperature"
    )
    
    @validator('default_provider')
    def validate_provider(cls, v):
        allowed = ['free', 'openai', 'anthropic', 'demo']
        if v not in allowed:
            raise ValueError(f"Provider must be one of {allowed}")
        return v
    
    class Config:
        env_prefix = "LLM_"


class CacheSettings(BaseSettings):
    """Cache configuration."""
    
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL (e.g., redis://localhost:6379/0)"
    )
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        description="Default cache TTL in seconds"
    )
    enable_cache: bool = Field(
        default=True,
        description="Enable caching"
    )
    
    class Config:
        env_prefix = "CACHE_"
        extra = "ignore"  # Ignore extra fields


class NewsSettings(BaseSettings):
    """News aggregation configuration."""
    
    fetch_timeout: int = Field(
        default=5,
        ge=1,
        le=30,
        description="HTTP request timeout in seconds"
    )
    max_workers: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum parallel workers for fetching"
    )
    max_items_per_source: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum items per RSS source"
    )
    translation_batch_size: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Translation batch size"
    )
    max_translate_items: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum items to translate at once"
    )
    
    class Config:
        env_prefix = "NEWS_"
        extra = "ignore"  # Ignore extra fields


class AppSettings(BaseSettings):
    """Application-wide settings."""
    
    # Application
    app_name: str = Field(default="Trendoscope")
    app_version: str = Field(default="2.2.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003, ge=1, le=65535)
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=30,
        ge=1,
        description="Default rate limit per minute"
    )
    
    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    news: NewsSettings = Field(default_factory=NewsSettings)
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """Reload settings from environment."""
    global _settings
    _settings = AppSettings()
    return _settings

