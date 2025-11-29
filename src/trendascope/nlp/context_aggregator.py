"""
Context aggregator for multi-source narratives.
Combines multiple news sources into coherent context for post generation.
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
import re


class ContextAggregator:
    """Aggregate multiple news sources into coherent context."""
    
    def __init__(self):
        """Initialize context aggregator."""
        self.min_cluster_size = 2
    
    def aggregate_context(
        self,
        news_items: List[Dict[str, Any]],
        topic: str = "any",
        max_items: int = 10
    ) -> Dict[str, Any]:
        """
        Aggregate news into structured context.
        
        Args:
            news_items: List of news items
            topic: Topic focus
            max_items: Maximum items to include
        
        Returns:
            {
                'main_narrative': str,
                'key_facts': List[str],
                'different_perspectives': List[Dict],
                'timeline': List[Dict],
                'sources': List[str],
                'context_summary': str
            }
        """
        if not news_items:
            return self._empty_context()
        
        # Limit items
        news_items = news_items[:max_items]
        
        # Cluster related news
        clusters = self._cluster_related_news(news_items)
        
        # Extract main narrative from largest cluster
        main_cluster = max(clusters, key=len) if clusters else news_items
        main_narrative = self._extract_narrative(main_cluster)
        
        # Extract key facts
        key_facts = self._extract_key_facts(news_items)
        
        # Find different perspectives
        perspectives = self._extract_perspectives(clusters)
        
        # Build timeline
        timeline = self._build_timeline(news_items)
        
        # Get unique sources
        sources = list(set(item.get('source', 'Unknown') for item in news_items))
        
        # Create context summary
        context_summary = self._create_summary(
            main_narrative,
            key_facts,
            perspectives,
            sources
        )
        
        return {
            'main_narrative': main_narrative,
            'key_facts': key_facts,
            'different_perspectives': perspectives,
            'timeline': timeline,
            'sources': sources,
            'context_summary': context_summary,
            'news_count': len(news_items),
        }
    
    def _cluster_related_news(
        self,
        news_items: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Cluster news items by topic similarity."""
        if not news_items:
            return []
        
        # Simple clustering by keyword overlap
        clusters = []
        used_indices = set()
        
        for i, item in enumerate(news_items):
            if i in used_indices:
                continue
            
            cluster = [item]
            used_indices.add(i)
            
            # Find related items
            item_keywords = self._extract_keywords(item)
            
            for j, other_item in enumerate(news_items):
                if j in used_indices or i == j:
                    continue
                
                other_keywords = self._extract_keywords(other_item)
                
                # Check overlap
                overlap = len(item_keywords & other_keywords)
                if overlap >= 2:  # At least 2 common keywords
                    cluster.append(other_item)
                    used_indices.add(j)
            
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def _extract_keywords(self, item: Dict[str, Any]) -> set:
        """Extract keywords from news item."""
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        
        # Simple keyword extraction
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Filter stop words
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'been',
            'will', 'would', 'could', 'should', 'может', 'будет',
            'было', 'есть', 'году', 'года'
        }
        
        return set(word for word in words if word not in stop_words)
    
    def _extract_narrative(
        self,
        cluster: List[Dict[str, Any]]
    ) -> str:
        """Extract main narrative from cluster."""
        if not cluster:
            return ""
        
        # Use the most recent or most detailed item
        sorted_cluster = sorted(
            cluster,
            key=lambda x: len(x.get('summary', '')),
            reverse=True
        )
        
        main_item = sorted_cluster[0]
        
        narrative = f"{main_item.get('title', '')}\n\n"
        narrative += main_item.get('summary', '')
        
        # Add supporting details from other items
        if len(cluster) > 1:
            narrative += "\n\nДополнительно:\n"
            for item in sorted_cluster[1:3]:  # Add up to 2 more
                narrative += f"- {item.get('title', '')} ({item.get('source', '')})\n"
        
        return narrative
    
    def _extract_key_facts(
        self,
        news_items: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract key facts from news items."""
        facts = []
        
        for item in news_items:
            # Extract sentences with numbers (often factual)
            summary = item.get('summary', '')
            
            # Find sentences with numbers or specific markers
            sentences = re.split(r'[.!?]+', summary)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Keep sentences with numbers, quotes, or specific markers
                if (re.search(r'\d+', sentence) or
                    '"' in sentence or
                    '«' in sentence or
                    re.search(r'\b(сообщи|заяви|объяви|подтверди)\b', sentence, re.IGNORECASE)):
                    
                    if len(sentence) > 20 and len(sentence) < 200:
                        facts.append(sentence)
        
        # Remove duplicates and limit
        unique_facts = []
        seen = set()
        
        for fact in facts:
            # Normalize for comparison
            normalized = re.sub(r'\s+', ' ', fact.lower())
            if normalized not in seen:
                seen.add(normalized)
                unique_facts.append(fact)
        
        return unique_facts[:10]
    
    def _extract_perspectives(
        self,
        clusters: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, str]]:
        """Extract different perspectives from news clusters."""
        perspectives = []
        
        for i, cluster in enumerate(clusters[:3]):  # Max 3 perspectives
            if not cluster:
                continue
            
            # Get representative sources
            sources = list(set(item.get('source', 'Unknown') for item in cluster))
            
            # Get main point
            main_item = max(cluster, key=lambda x: len(x.get('summary', '')))
            
            perspectives.append({
                'perspective': f"Точка зрения {i+1}",
                'sources': sources,
                'description': main_item.get('summary', '')[:300] + '...',
                'key_point': main_item.get('title', '')
            })
        
        return perspectives
    
    def _build_timeline(
        self,
        news_items: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Build chronological timeline of events."""
        timeline = []
        
        for item in news_items:
            published = item.get('published', '')
            
            timeline.append({
                'time': published,
                'event': item.get('title', ''),
                'source': item.get('source', 'Unknown')
            })
        
        # Sort by time if possible
        timeline.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        return timeline[:8]
    
    def _create_summary(
        self,
        main_narrative: str,
        key_facts: List[str],
        perspectives: List[Dict],
        sources: List[str]
    ) -> str:
        """Create comprehensive context summary."""
        summary = f"""КОНТЕКСТ ДЛЯ ГЕНЕРАЦИИ ПОСТА:

ОСНОВНАЯ ТЕМА:
{main_narrative[:500]}...

КЛЮЧЕВЫЕ ФАКТЫ ({len(key_facts)}):
{chr(10).join(f"- {fact}" for fact in key_facts[:5])}

РАЗНЫЕ ТОЧКИ ЗРЕНИЯ ({len(perspectives)}):
{chr(10).join(f"- {p['key_point']} (Источники: {', '.join(p['sources'][:2])})" for p in perspectives)}

ИСТОЧНИКИ ({len(sources)}):
{', '.join(sources)}

Используй эту информацию для создания информативного и обоснованного поста."""
        
        return summary
    
    def _empty_context(self) -> Dict[str, Any]:
        """Return empty context structure."""
        return {
            'main_narrative': '',
            'key_facts': [],
            'different_perspectives': [],
            'timeline': [],
            'sources': [],
            'context_summary': 'Контекст отсутствует',
            'news_count': 0,
        }
    
    def get_enriched_news_context(
        self,
        news_items: List[Dict[str, Any]],
        topic: str = "any"
    ) -> str:
        """
        Get enriched context as formatted string for prompts.
        
        Args:
            news_items: List of news items
            topic: Topic focus
        
        Returns:
            Formatted context string
        """
        context = self.aggregate_context(news_items, topic)
        
        formatted = f"""=== НОВОСТНОЙ КОНТЕКСТ ===

{context['main_narrative']}

КЛЮЧЕВЫЕ ФАКТЫ:
{chr(10).join(f"{i+1}. {fact}" for i, fact in enumerate(context['key_facts'][:8]))}

ИСТОЧНИКИ: {', '.join(context['sources'])}

КОЛИЧЕСТВО НОВОСТЕЙ: {context['news_count']}
"""
        
        return formatted
    
    def merge_with_rag(
        self,
        news_context: Dict[str, Any],
        rag_posts: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        Merge news context with RAG posts.
        
        Args:
            news_context: Aggregated news context
            rag_posts: Similar posts from RAG
            query: Search query
        
        Returns:
            Combined context dictionary
        """
        # Find relevant historical posts
        relevant_posts = []
        for post in rag_posts[:3]:  # Top 3
            relevant_posts.append({
                'title': post.get('title', ''),
                'excerpt': post.get('text', '')[:200] + '...',
                'url': post.get('url', '')
            })
        
        combined = {
            **news_context,
            'historical_context': relevant_posts,
            'combined_summary': self._create_combined_summary(
                news_context,
                relevant_posts
            )
        }
        
        return combined
    
    def _create_combined_summary(
        self,
        news_context: Dict[str, Any],
        historical_posts: List[Dict[str, Any]]
    ) -> str:
        """Create summary combining news and historical context."""
        summary = news_context.get('context_summary', '')
        
        if historical_posts:
            summary += "\n\nИСТОРИЧЕСКИЙ КОНТЕКСТ ИЗ ТВОИХ ПОСТОВ:\n"
            for i, post in enumerate(historical_posts):
                summary += f"{i+1}. {post['title']}\n   {post['excerpt']}\n"
        
        return summary


def aggregate_news_context(
    news_items: List[Dict[str, Any]],
    topic: str = "any",
    format_for_prompt: bool = True
) -> str:
    """
    Convenience function to aggregate news context.
    
    Args:
        news_items: List of news items
        topic: Topic focus
        format_for_prompt: Return formatted string for prompts
    
    Returns:
        Formatted context string or dictionary
    """
    aggregator = ContextAggregator()
    
    if format_for_prompt:
        return aggregator.get_enriched_news_context(news_items, topic)
    else:
        return aggregator.aggregate_context(news_items, topic)

