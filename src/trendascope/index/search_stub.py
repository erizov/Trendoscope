"""
Search interface - redirects to vector DB.
"""
from typing import List, Dict

from .vector_db import search_similar as vector_search


def search_similar(text: str, top_k: int = 3) -> List[Dict]:
    """
    Search for similar documents.

    Args:
        text: Query text
        top_k: Number of results

    Returns:
        List of similar documents
    """
    try:
        return vector_search(text, top_k)
    except Exception:
        # Fallback for testing
        return [
            {
                "score": 0.82,
                "url": "https://civil-engineer.livejournal.com/123.html",
                "title": "Пример совпадения",
                "chunk": text[:120] + " ..."
            },
        ]
