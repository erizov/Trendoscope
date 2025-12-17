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
# Lazy import to avoid circular dependencies
def _get_news_db_config():
    """Get news DB config (lazy import)."""
    from ..config import NEWS_DB_MAX_RECORDS, NEWS_DB_AUTO_CLEANUP, NEWS_DB_DEFAULT_LIMIT
    return NEWS_DB_MAX_RECORDS, NEWS_DB_AUTO_CLEANUP, NEWS_DB_DEFAULT_LIMIT

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
    
    def bulk_insert(self, news_items: List[Dict[str, Any]], auto_cleanup: bool = True, max_records: int = 10000) -> int:
        """
        Insert multiple news items.
        
        Args:
            news_items: List of news dictionaries
            auto_cleanup: Automatically cleanup old records if exceeds max_records (default: True)
            max_records: Maximum records to keep if auto_cleanup is True (default: 10000)
            
        Returns:
            Number of items inserted
        """
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
        
        # Auto-cleanup if enabled and exceeds limit
        if auto_cleanup:
            try:
                cursor.execute("SELECT COUNT(*) FROM news")
                total_count = cursor.fetchone()[0]
                if total_count > max_records:
                    logger.info(f"Auto-cleanup: {total_count} records exceed limit {max_records}, cleaning up...")
                    self.cleanup_old_records(keep_count=max_records)
            except Exception as e:
                logger.warning(f"Auto-cleanup failed: {e}")
        
        return inserted
    
    def get_recent(self, category: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent news."""
        if limit is None:
            limit = NEWS_DB_DEFAULT_LIMIT
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
    
    def cleanup_old_records(self, keep_count: Optional[int] = None) -> int:
        """
        Remove old records, keeping only the most recent N records.
        
        Args:
            keep_count: Number of most recent records to keep (default: from config)
            
        Returns:
            Number of records deleted
        """
        if keep_count is None:
            keep_count = NEWS_DB_MAX_RECORDS
        cursor = self.conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM news")
        total_count = cursor.fetchone()[0]
        
        if total_count <= keep_count:
            logger.info(f"Database has {total_count} records, no cleanup needed (limit: {keep_count})")
            return 0
        
        # Get IDs of records to keep (most recent by fetched_at or published_at)
        cursor.execute("""
            SELECT id FROM news 
            ORDER BY COALESCE(fetched_at, published_at, '1970-01-01') DESC 
            LIMIT ?
        """, (keep_count,))
        keep_ids = [row[0] for row in cursor.fetchall()]
        
        if not keep_ids:
            logger.warning("No records to keep, skipping cleanup")
            return 0
        
        # Delete old records (not in keep_ids)
        placeholders = ','.join(['?'] * len(keep_ids))
        cursor.execute(f"""
            DELETE FROM news 
            WHERE id NOT IN ({placeholders})
        """, keep_ids)
        
        deleted_count = cursor.rowcount
        
        # Also clean up FTS index
        cursor.execute(f"""
            DELETE FROM news_fts 
            WHERE rowid NOT IN ({placeholders})
        """, keep_ids)
        
        # Vacuum to reclaim space
        self.conn.execute("VACUUM")
        self.conn.commit()
        
        logger.info(f"Cleaned up database: kept {len(keep_ids)} records, deleted {deleted_count} old records")
        return deleted_count
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

