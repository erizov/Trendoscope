"""
FastAPI dependencies for dependency injection.
Provides reusable dependencies for endpoints.
"""
from fastapi import Depends
from typing import Optional

from .container import get_container
from .settings import get_settings
from ..services.news_service import NewsService
from ..services.post_service import PostService
from ..storage.news_db import NewsDatabase
from ..ingest.news_sources import NewsAggregator
from ..nlp.controversy_scorer import ControversyScorer


def get_config():
    """Get application settings."""
    return get_settings()


def get_news_service() -> NewsService:
    """Get news service instance."""
    container = get_container()
    
    if container.has("news_service"):
        return container.get("news_service")
    
    # Create and register if not exists
    config = get_settings()
    aggregator = NewsAggregator(timeout=config.news.fetch_timeout)
    scorer = ControversyScorer()
    db = NewsDatabase(config.database.news_db_path)
    
    service = NewsService()
    service.aggregator = aggregator
    service.scorer = scorer
    
    container.register_singleton("news_service", service)
    return service


def get_post_service() -> PostService:
    """Get post service instance."""
    container = get_container()
    
    if container.has("post_service"):
        return container.get("post_service")
    
    # Create and register if not exists
    service = PostService()
    container.register_singleton("post_service", service)
    return service


def get_news_database() -> NewsDatabase:
    """Get news database instance."""
    container = get_container()
    
    if container.has("news_database"):
        return container.get("news_database")
    
    # Create and register if not exists
    config = get_settings()
    db = NewsDatabase(config.database.news_db_path)
    container.register_singleton("news_database", db)
    return db

