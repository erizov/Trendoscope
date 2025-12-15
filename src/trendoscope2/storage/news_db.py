"""
News database for Trendoscope2.
Uses SQLite with FTS5 for full-text search.
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class NewsDatabase:
    """SQLite database for news storage."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize news database."""
        if db_path is None:
            # Use config path
            from ..config import DATA_DIR
            db_path = str(DATA_DIR / "databases" / "news.db")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA encoding = 'UTF-8'")
        self._init_database()
    
    def _init_database(self):
        """Create tables."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE,
                source TEXT,
                category TEXT,
                published_at TEXT,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
                controversy_score INTEGER DEFAULT 0,
                language TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON news(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_published ON news(published_at DESC)
        """)
        
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS news_fts USING fts5(
                title, summary, content=news, content_rowid=id
            )
        """)
        
        self.conn.commit()
    
    def bulk_insert(self, news_items: List[Dict[str, Any]]) -> int:
        """Insert multiple news items."""
        cursor = self.conn.cursor()
        inserted = 0
        
        for item in news_items:
            try:
                cursor.execute("""
                    INSERT INTO news (title, summary, url, source, category, published_at, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('title', ''),
                    item.get('summary', ''),
                    item.get('link', item.get('url', '')),
                    item.get('source', ''),
                    item.get('category', 'general'),
                    item.get('published', datetime.now().isoformat()),
                    item.get('language', 'ru')
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                continue
        
        self.conn.commit()
        return inserted
    
    def get_recent(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent news."""
        cursor = self.conn.cursor()
        sql = "SELECT * FROM news WHERE 1=1"
        params = []
        
        if category and category != 'all':
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY fetched_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM news")
        total = cursor.fetchone()[0]
        return {'total_items': total}
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

