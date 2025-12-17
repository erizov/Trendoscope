"""
Unit tests for news search functionality.
"""
import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.storage.news_search import NewsSearch
from trendoscope2.storage.news_db import NewsDatabase


class TestNewsSearch:
    """Test NewsSearch functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Initialize database
        db = NewsDatabase(db_path=db_path)
        
        # Insert test data
        test_news = [
            {
                'title': 'Artificial Intelligence Breakthrough',
                'summary': 'New AI model achieves state-of-the-art results',
                'link': 'http://test.com/ai1',
                'source': 'TechNews',
                'category': 'tech',
                'language': 'en',
                'published': '2025-01-15T10:00:00'
            },
            {
                'title': 'Политические новости',
                'summary': 'Важные политические события',
                'link': 'http://test.com/pol1',
                'source': 'NewsRU',
                'category': 'politics',
                'language': 'ru',
                'published': '2025-01-14T10:00:00'
            },
            {
                'title': 'Tech Industry Update',
                'summary': 'Latest updates from tech industry',
                'link': 'http://test.com/tech1',
                'source': 'TechNews',
                'category': 'tech',
                'language': 'en',
                'published': '2025-01-13T10:00:00'
            }
        ]
        
        db.bulk_insert(test_news, auto_cleanup=False)
        db.close()
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_search_basic(self, temp_db):
        """Test basic search."""
        search = NewsSearch(db_path=temp_db)
        
        result = search.search(query="Artificial Intelligence", limit=10)
        
        assert result['total'] >= 1
        assert len(result['results']) >= 1
        assert 'Artificial Intelligence' in result['results'][0]['title']
    
    def test_search_with_category(self, temp_db):
        """Test search with category filter."""
        search = NewsSearch(db_path=temp_db)
        
        result = search.search(query="tech", category="tech", limit=10)
        
        assert all(item['category'] == 'tech' for item in result['results'])
    
    def test_search_with_language(self, temp_db):
        """Test search with language filter."""
        search = NewsSearch(db_path=temp_db)
        
        result = search.search(query="новости", language="ru", limit=10)
        
        assert all(item['language'] == 'ru' for item in result['results'])
    
    def test_search_with_source(self, temp_db):
        """Test search with source filter."""
        search = NewsSearch(db_path=temp_db)
        
        result = search.search(query="", source="TechNews", limit=10)
        
        assert all(item['source'] == 'TechNews' for item in result['results'])
    
    def test_search_with_date_range(self, temp_db):
        """Test search with date range."""
        search = NewsSearch(db_path=temp_db)
        
        result = search.search(
            query="",
            date_from="2025-01-14",
            date_to="2025-01-15",
            limit=10
        )
        
        assert result['total'] >= 0
        # All results should be within date range
        for item in result['results']:
            if item.get('published_at'):
                assert "2025-01-14" <= item['published_at'] <= "2025-01-15"
    
    def test_search_pagination(self, temp_db):
        """Test search pagination."""
        search = NewsSearch(db_path=temp_db)
        
        result1 = search.search(query="", limit=2, offset=0)
        result2 = search.search(query="", limit=2, offset=2)
        
        assert len(result1['results']) <= 2
        assert len(result2['results']) <= 2
        # Results should be different
        if result1['results'] and result2['results']:
            assert result1['results'][0]['id'] != result2['results'][0]['id']
    
    def test_build_fts_query(self, temp_db):
        """Test FTS query building."""
        search = NewsSearch(db_path=temp_db)
        
        # Simple query
        query1 = search._build_fts_query("artificial intelligence")
        assert "artificial" in query1.lower()
        assert "intelligence" in query1.lower()
        
        # Phrase query
        query2 = search._build_fts_query('"artificial intelligence"')
        assert query2.startswith('"')
        assert query2.endswith('"')
        
        # Empty query
        query3 = search._build_fts_query("")
        assert query3 == ""
    
    def test_get_filters(self, temp_db):
        """Test getting available filters."""
        search = NewsSearch(db_path=temp_db)
        
        filters = search.get_filters()
        
        assert 'categories' in filters
        assert 'sources' in filters
        assert 'languages' in filters
        assert isinstance(filters['categories'], list)
        assert isinstance(filters['sources'], list)
        assert isinstance(filters['languages'], list)
    
    def test_get_trending_topics(self, temp_db):
        """Test getting trending topics."""
        search = NewsSearch(db_path=temp_db)
        
        topics = search.get_trending_topics(days=30, limit=10)
        
        assert isinstance(topics, list)
        for topic in topics:
            assert 'category' in topic
            assert 'count' in topic
            assert isinstance(topic['count'], int)
