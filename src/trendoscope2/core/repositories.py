"""
Repository pattern for data access abstraction.
Provides interfaces for swapping storage backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


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
