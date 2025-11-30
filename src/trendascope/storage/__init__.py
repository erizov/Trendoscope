"""Storage module for news persistence."""
from .news_db import NewsDatabase, create_news_database, search_news

__all__ = ['NewsDatabase', 'create_news_database', 'search_news']

