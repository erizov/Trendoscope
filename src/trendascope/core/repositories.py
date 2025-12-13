"""
Repository implementations following repository pattern.
Provides abstraction over data storage.
"""
from typing import List, Dict, Any, Optional
from ..core.interfaces import INewsRepository, IPostRepository
from ..storage.news_db import NewsDatabase
from ..storage.post_storage import PostStorage
import logging

logger = logging.getLogger(__name__)


class SQLiteNewsRepository(INewsRepository):
    """SQLite implementation of news repository."""
    
    def __init__(self, db_path: str = "data/news.db"):
        """
        Initialize repository.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db = NewsDatabase(db_path)
    
    def save(self, item: Dict[str, Any]) -> Optional[int]:
        """Save news item."""
        try:
            return self.db.add_news(
                title=item.get('title', ''),
                summary=item.get('summary', ''),
                full_text=item.get('full_text', ''),
                url=item.get('link') or item.get('url', ''),
                source=item.get('source', ''),
                category=item.get('category'),
                controversy_score=item.get('controversy_score', 0),
                controversy_label=item.get('controversy_label'),
                keywords=item.get('keywords', []),
                language=item.get('language', 'en')
            )
        except Exception as e:
            logger.error(f"Failed to save news item: {e}")
            return None
    
    def find_by_language(
        self,
        language: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find news items by language."""
        try:
            # Use search with language filter
            results = self.db.search("", limit=limit)
            return [
                item for item in results
                if item.get('language') == language
            ]
        except Exception as e:
            logger.error(f"Failed to find by language: {e}")
            return []
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search news items."""
        try:
            return self.db.search(query, category=category, limit=limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            return self.db.get_statistics()
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'total_items': 0, 'by_category': {}, 'controversy_distribution': {}}
    
    def close(self):
        """Close database connection."""
        if hasattr(self.db, 'close'):
            self.db.close()


class InMemoryNewsRepository(INewsRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        """Initialize in-memory repository."""
        self._items: List[Dict[str, Any]] = []
        self._next_id = 1
    
    def save(self, item: Dict[str, Any]) -> Optional[int]:
        """Save news item."""
        # Check for duplicates
        url = item.get('link') or item.get('url', '')
        if url:
            existing = next(
                (i for i in self._items if i.get('url') == url),
                None
            )
            if existing:
                return None
        
        item['id'] = self._next_id
        item['url'] = url
        self._next_id += 1
        self._items.append(item)
        return item['id']
    
    def find_by_language(
        self,
        language: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find news items by language."""
        results = [
            item for item in self._items
            if item.get('language') == language
        ]
        return results[:limit]
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search news items."""
        query_lower = query.lower()
        results = []
        
        for item in self._items:
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            
            if query_lower in title or query_lower in summary:
                if not category or item.get('category') == category:
                    results.append(item)
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        categories = {}
        for item in self._items:
            cat = item.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_items': len(self._items),
            'by_category': categories,
            'controversy_distribution': {}
        }


class JSONPostRepository(IPostRepository):
    """JSON-based post repository implementation."""
    
    def __init__(self, storage_path: str = "data/posts"):
        """
        Initialize repository.
        
        Args:
            storage_path: Path to post storage directory
        """
        self.storage = PostStorage(storage_path)
    
    def save(self, post: Dict[str, Any]) -> str:
        """Save generated post."""
        try:
            return self.storage.save_post(post)
        except Exception as e:
            logger.error(f"Failed to save post: {e}")
            raise
    
    def get(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post by ID."""
        try:
            return self.storage.get_post(post_id)
        except Exception as e:
            logger.error(f"Failed to get post {post_id}: {e}")
            return None
    
    def list(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List posts."""
        try:
            return self.storage.list_posts(limit=limit, offset=offset)
        except Exception as e:
            logger.error(f"Failed to list posts: {e}")
            return []
    
    def update(self, post_id: str, updates: Dict[str, Any]) -> bool:
        """Update post."""
        try:
            return self.storage.update_post(post_id, updates)
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            return False
    
    def delete(self, post_id: str) -> bool:
        """Delete post."""
        try:
            return self.storage.delete_post(post_id)
        except Exception as e:
            logger.error(f"Failed to delete post {post_id}: {e}")
            return False

