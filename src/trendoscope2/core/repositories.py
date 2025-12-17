"""
Repository pattern for data access abstraction.
Provides interfaces for swapping storage backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio


class NewsRepository(ABC):
    """Abstract repository for news data access."""
    
    @abstractmethod
    async def get_recent(
        self,
        category: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Get recent news items by category.
        
        Args:
            category: News category
            limit: Maximum number of items
            
        Returns:
            List of news items
        """
        pass
    
    @abstractmethod
    async def save(self, item: Dict[str, Any]) -> None:
        """
        Save news item.
        
        Args:
            item: News item dictionary
        """
        pass
    
    @abstractmethod
    async def save_many(self, items: List[Dict[str, Any]]) -> int:
        """
        Save multiple news items.
        
        Args:
            items: List of news item dictionaries
            
        Returns:
            Number of items saved
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        pass
    
    @abstractmethod
    async def cleanup_old_records(self, keep_count: int) -> int:
        """
        Cleanup old records.
        
        Args:
            keep_count: Number of records to keep
            
        Returns:
            Number of deleted records
        """
        pass


class InMemoryNewsRepository(NewsRepository):
    """In-memory repository for testing."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._items: List[Dict[str, Any]] = []
    
    async def get_recent(
        self,
        category: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recent news items."""
        filtered = [
            item for item in self._items
            if item.get('category') == category or category == 'all'
        ]
        return sorted(
            filtered,
            key=lambda x: x.get('published', ''),
            reverse=True
        )[:limit]
    
    async def save(self, item: Dict[str, Any]) -> None:
        """Save news item."""
        self._items.append(item)
    
    async def save_many(self, items: List[Dict[str, Any]]) -> int:
        """Save multiple news items."""
        self._items.extend(items)
        return len(items)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'total_items': len(self._items),
            'categories': {}
        }
    
    async def cleanup_old_records(self, keep_count: int) -> int:
        """Cleanup old records."""
        if len(self._items) <= keep_count:
            return 0
        deleted = len(self._items) - keep_count
        self._items = sorted(
            self._items,
            key=lambda x: x.get('published', ''),
            reverse=True
        )[:keep_count]
        return deleted


class SQLiteNewsRepository(NewsRepository):
    """SQLite implementation of NewsRepository."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite repository.
        
        Args:
            db_path: Optional database path
        """
        from ..storage.news_db import NewsDatabase
        self._db = NewsDatabase(db_path=db_path)
    
    async def get_recent(
        self,
        category: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recent news items."""
        return await asyncio.to_thread(
            self._db.get_recent,
            category=category,
            limit=limit
        )
    
    async def save(self, item: Dict[str, Any]) -> None:
        """Save news item."""
        await asyncio.to_thread(
            self._db.bulk_insert,
            news_items=[item],
            auto_cleanup=False
        )
    
    async def save_many(self, items: List[Dict[str, Any]]) -> int:
        """Save multiple news items."""
        return await asyncio.to_thread(
            self._db.bulk_insert,
            news_items=items,
            auto_cleanup=True
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        return await asyncio.to_thread(
            self._db.get_statistics
        )
    
    async def cleanup_old_records(self, keep_count: int) -> int:
        """Cleanup old records."""
        return await asyncio.to_thread(
            self._db.cleanup_old_records,
            keep_count=keep_count
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self._db, '__exit__'):
            self._db.__exit__(exc_type, exc_val, exc_tb)
