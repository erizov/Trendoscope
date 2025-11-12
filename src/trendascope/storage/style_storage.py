"""
Persistent storage for author's style guide and analyzed posts.
Uses vector DB (RAG) for posts and JSON for style metadata.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class StyleStorage:
    """Store and retrieve author's style guide."""

    def __init__(self, storage_dir: str = "data"):
        """
        Initialize style storage.

        Args:
            storage_dir: Directory for storage files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.style_file = self.storage_dir / "style_guide.json"
        self.posts_meta_file = self.storage_dir / "posts_metadata.json"

    def save_style_guide(
        self,
        style_data: Dict[str, Any],
        blog_url: str
    ) -> None:
        """
        Save style guide to disk.

        Args:
            style_data: Style analysis results
            blog_url: Source blog URL
        """
        data = {
            "blog_url": blog_url,
            "style": style_data,
            "saved_at": __import__('datetime').datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(self.style_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_style_guide(self) -> Optional[Dict[str, Any]]:
        """
        Load style guide from disk.

        Returns:
            Style guide data or None if not found
        """
        if not self.style_file.exists():
            return None

        try:
            with open(self.style_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def has_style_guide(self) -> bool:
        """Check if style guide exists."""
        return self.style_file.exists()

    def save_posts_metadata(
        self,
        posts: List[Dict[str, Any]],
        blog_url: str
    ) -> None:
        """
        Save posts metadata (not full text, just references).

        Args:
            posts: List of analyzed posts
            blog_url: Source blog URL
        """
        # Save only essential metadata, not full text
        metadata = {
            "blog_url": blog_url,
            "post_count": len(posts),
            "post_urls": [p.get('url', '') for p in posts],
            "saved_at": __import__('datetime').datetime.now().isoformat(),
        }

        with open(self.posts_meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def get_posts_metadata(self) -> Optional[Dict[str, Any]]:
        """Get saved posts metadata."""
        if not self.posts_meta_file.exists():
            return None

        try:
            with open(self.posts_meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def clear(self) -> None:
        """Clear all stored data."""
        if self.style_file.exists():
            self.style_file.unlink()
        if self.posts_meta_file.exists():
            self.posts_meta_file.unlink()


# Global storage instance
_storage = None


def get_storage() -> StyleStorage:
    """Get or create global storage instance."""
    global _storage
    if _storage is None:
        _storage = StyleStorage()
    return _storage


def save_analysis_results(
    posts: List[Dict[str, Any]],
    style_data: Dict[str, Any],
    blog_url: str
) -> None:
    """
    Save analysis results (convenience function).

    Args:
        posts: Analyzed posts
        style_data: Style analysis
        blog_url: Source blog URL
    """
    storage = get_storage()
    storage.save_style_guide(style_data, blog_url)
    storage.save_posts_metadata(posts, blog_url)


def load_style_guide() -> Optional[Dict[str, Any]]:
    """Load saved style guide."""
    return get_storage().load_style_guide()


def has_saved_style() -> bool:
    """Check if style guide is saved."""
    return get_storage().has_style_guide()

