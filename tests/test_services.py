"""
Tests for service layer.
"""
import pytest
from src.trendascope.services.news_service import NewsService
from src.trendascope.services.post_service import PostService


class TestNewsService:
    """Test NewsService."""
    
    def test_service_initialization(self):
        """Test service can be initialized."""
        service = NewsService()
        assert service is not None
        assert service.aggregator is not None
        assert service.scorer is not None
    
    def test_categorize_news(self):
        """Test news categorization."""
        service = NewsService()
        
        # Test AI category
        item = {"title": "New AI breakthrough", "summary": "GPT-5 released"}
        category = service._categorize_news(item)
        assert category == "ai"
        
        # Test politics category
        item = {"title": "Election results", "summary": "New president elected"}
        category = service._categorize_news(item)
        assert category == "politics"


class TestPostService:
    """Test PostService."""
    
    def test_service_initialization(self):
        """Test service can be initialized."""
        service = PostService()
        assert service is not None


class TestPostStorage:
    """Test PostStorage."""
    
    def test_storage_initialization(self):
        """Test storage can be initialized."""
        from src.trendascope.storage.post_storage import PostStorage
        storage = PostStorage()
        assert storage is not None
    
    def test_save_and_get_post(self):
        """Test saving and retrieving posts."""
        from src.trendascope.storage.post_storage import PostStorage
        storage = PostStorage()
        
        post = {
            "title": "Test Post",
            "text": "Test content",
            "tags": ["test"]
        }
        
        post_id = storage.save_post(post)
        assert post_id is not None
        
        retrieved = storage.get_post(post_id)
        assert retrieved is not None
        assert retrieved["title"] == "Test Post"

