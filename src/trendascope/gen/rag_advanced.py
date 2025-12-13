"""
Advanced RAG system with hybrid search, reranking, and multi-query retrieval.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def hybrid_search(
    query: str,
    top_k: int = 5,
    alpha: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic and keyword search.
    
    Args:
        query: Search query
        top_k: Number of results
        alpha: Weight for semantic search (0.0 = keyword only, 1.0 = semantic only)
        
    Returns:
        List of relevant documents with scores
    """
    try:
        from ..index.vector_db import search_similar
        from ..storage.news_db import NewsDatabase
        
        # Semantic search
        semantic_results = search_similar(query, top_k=top_k * 2)
        
        # Keyword search (FTS5)
        db = NewsDatabase()
        keyword_results = db.search(query, limit=top_k * 2)
        db.close()
        
        # Combine results
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            doc_id = result.get('id') or result.get('url', '')
            if doc_id:
                combined[doc_id] = {
                    'item': result,
                    'semantic_score': result.get('score', 0.0),
                    'keyword_score': 0.0
                }
        
        # Add keyword results
        for result in keyword_results:
            doc_id = result.get('url', '') or str(result.get('id', ''))
            if doc_id in combined:
                combined[doc_id]['keyword_score'] = 1.0
            else:
                combined[doc_id] = {
                    'item': result,
                    'semantic_score': 0.0,
                    'keyword_score': 1.0
                }
        
        # Calculate hybrid scores
        scored_results = []
        for doc_id, data in combined.items():
            hybrid_score = (
                alpha * data['semantic_score'] +
                (1 - alpha) * data['keyword_score']
            )
            scored_results.append({
                **data['item'],
                'hybrid_score': hybrid_score,
                'semantic_score': data['semantic_score'],
                'keyword_score': data['keyword_score']
            })
        
        # Sort by hybrid score
        scored_results.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
        
        return scored_results[:top_k]
        
    except Exception as e:
        logger.error(f"Hybrid search error: {e}", exc_info=True)
        # Fallback to simple search
        try:
            from ..index.vector_db import search_similar
            return search_similar(query, top_k=top_k)
        except:
            return []


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Rerank search results using cross-encoder or LLM.
    
    Args:
        query: Original query
        results: Initial search results
        top_k: Number of top results to return
        
    Returns:
        Reranked results
    """
    if not results:
        return []
    
    if len(results) <= top_k:
        return results
    
    # Simple reranking based on relevance signals
    # In production, would use cross-encoder model or LLM
    
    for result in results:
        title = result.get('title', '').lower()
        summary = result.get('summary', '').lower()
        query_lower = query.lower()
        
        # Calculate relevance score
        title_matches = sum(1 for word in query_lower.split() if word in title)
        summary_matches = sum(1 for word in query_lower.split() if word in summary)
        
        relevance = (
            title_matches * 2 +  # Title matches are more important
            summary_matches +
            result.get('hybrid_score', 0) * 10  # Original score
        )
        
        result['relevance_score'] = relevance
    
    # Sort by relevance
    results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return results[:top_k]


def multi_query_retrieval(
    query: str,
    num_queries: int = 3,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate multiple query variations and retrieve results.
    
    Args:
        query: Original query
        num_queries: Number of query variations
        top_k: Results per query
        
    Returns:
        Combined and deduplicated results
    """
    try:
        # Generate query variations (simplified - in production would use LLM)
        query_variations = [query]  # Start with original
        
        # Simple variations
        if '?' in query:
            query_variations.append(query.replace('?', '').strip())
        
        # Add keyword extraction
        keywords = query.split()[:3]  # First 3 words
        if len(keywords) > 1:
            query_variations.append(' '.join(keywords))
        
        # Search with each variation
        all_results = []
        seen_urls = set()
        
        for variation in query_variations[:num_queries]:
            results = hybrid_search(variation, top_k=top_k)
            for result in results:
                url = result.get('url') or result.get('link', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
        
        # Rerank combined results
        return rerank_results(query, all_results, top_k=top_k)
        
    except Exception as e:
        logger.error(f"Multi-query retrieval error: {e}", exc_info=True)
        return hybrid_search(query, top_k=top_k)


def optimize_context(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    max_tokens: int = 2000
) -> str:
    """
    Optimize retrieved context for LLM prompt.
    
    Args:
        query: Original query
        retrieved_docs: Retrieved documents
        max_tokens: Maximum tokens for context
        
    Returns:
        Optimized context string
    """
    if not retrieved_docs:
        return ""
    
    # Sort by relevance
    sorted_docs = sorted(
        retrieved_docs,
        key=lambda x: x.get('relevance_score', x.get('hybrid_score', 0)),
        reverse=True
    )
    
    # Build context with most relevant docs
    context_parts = []
    current_tokens = 0
    
    for doc in sorted_docs:
        title = doc.get('title', '')
        summary = doc.get('summary', '') or doc.get('text', '')
        
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        doc_tokens = len(f"{title} {summary}") // 4
        
        if current_tokens + doc_tokens > max_tokens:
            break
        
        context_parts.append(f"Заголовок: {title}\nСодержание: {summary[:500]}")
        current_tokens += doc_tokens
    
    return "\n\n---\n\n".join(context_parts)

