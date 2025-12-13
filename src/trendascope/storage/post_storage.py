"""
Post storage for saving and managing generated posts.
"""
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)

POSTS_DIR = Path("data/posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)

POSTS_FILE = POSTS_DIR / "saved_posts.json"


class PostStorage:
    """Storage for generated posts."""
    
    def __init__(self):
        """Initialize post storage."""
        self.posts_file = POSTS_FILE
        self._load_posts()
    
    def _load_posts(self) -> List[Dict[str, Any]]:
        """Load posts from file."""
        if not self.posts_file.exists():
            return []
        
        try:
            with open(self.posts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning("failed_to_load_posts", extra={"error": str(e)})
            return []
    
    def _save_posts(self, posts: List[Dict[str, Any]]):
        """Save posts to file."""
        try:
            with open(self.posts_file, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("failed_to_save_posts", extra={"error": str(e)})
            raise
    
    def save_post(self, post: Dict[str, Any]) -> str:
        """
        Save a post.
        
        Args:
            post: Post data
            
        Returns:
            Post ID
        """
        posts = self._load_posts()
        
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(posts)}"
        post_data = {
            "id": post_id,
            "created_at": datetime.now().isoformat(),
            **post
        }
        
        posts.insert(0, post_data)  # Add to beginning
        self._save_posts(posts)
        
        logger.info("post_saved", extra={"post_id": post_id})
        return post_id
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a post by ID."""
        posts = self._load_posts()
        for post in posts:
            if post.get("id") == post_id:
                return post
        return None
    
    def list_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all posts, most recent first."""
        posts = self._load_posts()
        return posts[:limit]
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        posts = self._load_posts()
        original_count = len(posts)
        posts = [p for p in posts if p.get("id") != post_id]
        
        if len(posts) < original_count:
            self._save_posts(posts)
            logger.info("post_deleted", extra={"post_id": post_id})
            return True
        return False
    
    def update_post(self, post_id: str, updates: Dict[str, Any]) -> bool:
        """Update a post."""
        posts = self._load_posts()
        for post in posts:
            if post.get("id") == post_id:
                post.update(updates)
                post["updated_at"] = datetime.now().isoformat()
                self._save_posts(posts)
                logger.info("post_updated", extra={"post_id": post_id})
                return True
        return False

