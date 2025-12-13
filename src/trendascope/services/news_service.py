"""
News service - business logic for news operations.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import time

from ..ingest.news_sources import NewsAggregator
from ..nlp.controversy_scorer import ControversyScorer
from ..nlp.translator import translate_and_summarize_news
from ..storage.news_db import NewsDatabase
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NewsService:
    """Service for news operations."""
    
    def __init__(self):
        """Initialize news service."""
        self.aggregator = NewsAggregator(timeout=5)
        self.scorer = ControversyScorer()
    
    def fetch_news_feed(
        self,
        category: str = "all",
        limit: int = 20,
        translate: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch and process news feed.
        
        Args:
            category: Category filter
            limit: Maximum items
            translate: Translate to Russian
            
        Returns:
            Processed news items
        """
        logger.info("fetching_news_feed", extra={"category": category, "limit": limit})
        
        # Map categories to sources
        category_map = {
            'tech': {'ai': True, 'russian': True},
            'business': {'russian': True, 'international': True},
            'politics': {'politics': True, 'us': True, 'russian': True},
            'conflict': {'politics': True, 'international': True},
            'legal': {'legal': True, 'international': True, 'russian': True},
            'society': {'russian': True, 'international': True},
            'science': {'ai': True, 'international': True},
            'all': {'ai': True, 'politics': True, 'us': True, 'eu': True, 
                   'russian': True, 'international': True, 'legal': True}
        }
        
        sources = category_map.get(category, category_map['all'])
        
        # Fetch news
        news_items = self.aggregator.fetch_trending_topics(
            include_ai=sources.get('ai', False),
            include_politics=sources.get('politics', False),
            include_us=sources.get('us', False),
            include_eu=sources.get('eu', False),
            include_russian=sources.get('russian', False),
            include_international=sources.get('international', False),
            include_legal=sources.get('legal', False),
            max_per_source=2,
            parallel=True,
            max_workers=10
        )
        
        logger.info("news_fetched", extra={"count": len(news_items)})
        
        # Translate if requested
        if translate and news_items:
            try:
                news_items = translate_and_summarize_news(
                    news_items,
                    provider="openai"
                )
            except Exception as e:
                logger.warning("translation_failed", extra={"error": str(e)})
        
        # Categorize and score
        for item in news_items:
            item['category'] = self._categorize_news(item)
        
        # Filter by category
        if category != 'all':
            news_items = [
                item for item in news_items
                if item['category'] == category
            ]
        
        # Score controversy
        scored_items = self.scorer.score_batch(news_items)
        
        # Add timestamps for sorting
        fetch_timestamp = time.time()
        for item in scored_items:
            if 'fetched_at' not in item:
                item['fetched_at'] = fetch_timestamp
            if 'published' not in item or not item['published']:
                item['published'] = item.get('published_at', fetch_timestamp)
        
        # Sort by most recent
        scored_items.sort(
            key=lambda x: (
                x.get('fetched_at', 0) if isinstance(x.get('fetched_at'), (int, float)) else 0,
                x.get('published', '') or ''
            ),
            reverse=True
        )
        
        # Limit results
        scored_items = scored_items[:limit]
        
        return {
            'count': len(scored_items),
            'category': category,
            'news': scored_items
        }
    
    def _categorize_news(self, item: Dict[str, Any]) -> str:
        """Categorize news item."""
        title = (item.get('title', '') or '').lower()
        summary = (item.get('summary', '') or '').lower()
        text = f"{title} {summary}"
        
        # Check categories (order matters - most specific first)
        if any(word in text for word in ['ai', 'искусственный интеллект', 'нейросет', 'gpt', 'chatgpt', 'машинное обучение']):
            return 'ai'
        elif any(word in text for word in ['политика', 'политик', 'выборы', 'президент', 'правительство']):
            return 'politics'
        elif any(word in text for word in ['сша', 'америк', 'usa', 'united states', 'вашингтон', 'белый дом']):
            return 'us'
        elif any(word in text for word in ['евросоюз', 'eu', 'europe', 'брюссель', 'германия', 'франция']):
            return 'eu'
        elif any(word in text for word in ['россия', 'российск', 'russia', 'кремль', 'путин', 'москва']):
            return 'russia'
        else:
            return 'other'
    
    def store_news_batch(self, fetch_fresh: bool = True) -> Dict[str, Any]:
        """
        Fetch and store news in database.
        
        Args:
            fetch_fresh: Fetch fresh news or use existing
            
        Returns:
            Storage statistics
        """
        if fetch_fresh:
            logger.info("fetching_fresh_news")
            news_items = self.aggregator.fetch_trending_topics(
                include_russian=True,
                include_ai=True,
                max_per_source=2,
                parallel=True
            )
            
            logger.info("news_fetched_for_storage", extra={"count": len(news_items)})
            
            # Score controversy
            scored_items = self.scorer.score_batch(news_items)
            
            # Store in database
            with NewsDatabase() as db:
                inserted = db.bulk_insert(scored_items)
                stats = db.get_statistics()
            
            return {
                'fetched': len(news_items),
                'inserted': inserted,
                'total_in_db': stats['total_items']
            }
        else:
            with NewsDatabase() as db:
                stats = db.get_statistics()
            return {
                'total_in_db': stats['total_items']
            }

