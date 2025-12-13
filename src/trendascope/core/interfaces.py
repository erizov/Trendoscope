"""
Abstract interfaces for core components.
Enables dependency inversion and easy testing.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class INewsRepository(ABC):
    """Abstract news repository interface."""
    
    @abstractmethod
    def save(self, item: Dict[str, Any]) -> Optional[int]:
        """Save news item. Returns ID or None if duplicate."""
        pass
    
    @abstractmethod
    def find_by_language(
        self,
        language: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find news items by language."""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search news items."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        pass


class IPostRepository(ABC):
    """Abstract post repository interface."""
    
    @abstractmethod
    def save(self, post: Dict[str, Any]) -> str:
        """Save generated post. Returns post ID."""
        pass
    
    @abstractmethod
    def get(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post by ID."""
        pass
    
    @abstractmethod
    def list(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List posts."""
        pass
    
    @abstractmethod
    def update(self, post_id: str, updates: Dict[str, Any]) -> bool:
        """Update post."""
        pass
    
    @abstractmethod
    def delete(self, post_id: str) -> bool:
        """Delete post."""
        pass


class ILLMProvider(ABC):
    """Abstract LLM provider interface."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @abstractmethod
    def call(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Call LLM with prompt."""
        pass
    
    @abstractmethod
    def check_balance(self) -> bool:
        """Check if provider has available balance/credits."""
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000
    ) -> float:
        """Estimate cost for call."""
        pass


class ITranslator(ABC):
    """Abstract translator interface."""
    
    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate text from source to target language."""
        pass
    
    @abstractmethod
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[str]:
        """Translate multiple texts."""
        pass


class INewsAggregator(ABC):
    """Abstract news aggregator interface."""
    
    @abstractmethod
    def fetch_trending_topics(
        self,
        include_russian: bool = False,
        include_ai: bool = False,
        include_politics: bool = False,
        max_per_source: int = 5,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch trending news topics."""
        pass
    
    @abstractmethod
    def fetch_rss_feed(
        self,
        url: str,
        max_items: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch RSS feed."""
        pass


class ICache(ABC):
    """Abstract cache interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """Set value in cache with TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache."""
        pass

