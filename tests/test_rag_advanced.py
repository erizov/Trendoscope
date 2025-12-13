"""
Tests for advanced RAG system.
"""
import pytest
from trendascope.gen.rag_advanced import (
    hybrid_search,
    rerank_results,
    multi_query_retrieval,
    optimize_context
)


def test_hybrid_search():
    """Test hybrid search."""
    results = hybrid_search("AI technology", top_k=5)
    assert isinstance(results, list)


def test_rerank_results():
    """Test result reranking."""
    mock_results = [
        {'title': 'AI News', 'summary': 'AI technology advances', 'hybrid_score': 0.5},
        {'title': 'Tech News', 'summary': 'Technology updates', 'hybrid_score': 0.7}
    ]
    
    reranked = rerank_results("AI technology", mock_results, top_k=2)
    assert isinstance(reranked, list)
    assert len(reranked) <= 2


def test_multi_query_retrieval():
    """Test multi-query retrieval."""
    results = multi_query_retrieval("artificial intelligence", num_queries=2, top_k=5)
    assert isinstance(results, list)


def test_optimize_context():
    """Test context optimization."""
    mock_docs = [
        {'title': 'Doc 1', 'summary': 'Content 1', 'relevance_score': 0.9},
        {'title': 'Doc 2', 'summary': 'Content 2', 'relevance_score': 0.7}
    ]
    
    context = optimize_context("query", mock_docs, max_tokens=1000)
    assert isinstance(context, str)
    assert len(context) > 0

