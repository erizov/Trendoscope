"""
News database with full-text search.
Uses SQLite FTS5 for fast keyword and phrase search in Russian/English.
Auto-maintains 50,000 most recent items.
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class NewsDatabase:
    """
    SQLite database optimized for news storage and full-text search.
    
    Features:
    - FTS5 full-text search (fast phrase matching)
    - Auto-cleanup (keeps 50k most recent)
    - Supports Russian and English
    - Controversy scoring integration
    - Category filtering
    """
    
    def __init__(self, db_path: str = "data/news.db"):
        """
        Initialize news database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Create data directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
        
        self._init_database()
    
    def _init_database(self):
        """Create tables with optimized schema."""
        cursor = self.conn.cursor()
        
        # Main news table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                full_text TEXT,
                url TEXT UNIQUE,
                source TEXT,
                category TEXT,
                published_at TEXT,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- Controversy scoring
                controversy_score INTEGER DEFAULT 0,
                controversy_label TEXT,
                
                -- Metadata
                language TEXT,  -- 'ru' or 'en'
                
                -- Indexes for fast filtering
                UNIQUE(url)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON news(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_published 
            ON news(published_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_controversy 
            ON news(controversy_score DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source 
            ON news(source)
        """)
        
        # FTS5 virtual table for full-text search
        # tokenize='unicode61' handles Russian and English
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS news_fts USING fts5(
                title,
                summary,
                full_text,
                keywords,
                content=news,
                content_rowid=id,
                tokenize='unicode61 remove_diacritics 0'
            )
        """)
        
        # Triggers to keep FTS5 in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS news_ai AFTER INSERT ON news BEGIN
                INSERT INTO news_fts(rowid, title, summary, full_text, keywords)
                VALUES (new.id, new.title, new.summary, new.full_text, 
                        new.category || ' ' || new.source);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS news_ad AFTER DELETE ON news BEGIN
                DELETE FROM news_fts WHERE rowid = old.id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS news_au AFTER UPDATE ON news BEGIN
                UPDATE news_fts 
                SET title = new.title,
                    summary = new.summary,
                    full_text = new.full_text,
                    keywords = new.category || ' ' || new.source
                WHERE rowid = new.id;
            END
        """)
        
        # Keywords table for tag-like filtering
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_keyword 
            ON keywords(keyword)
        """)
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_news(
        self,
        title: str,
        summary: str,
        full_text: str = "",
        url: str = "",
        source: str = "",
        category: str = "general",
        published_at: Optional[str] = None,
        controversy_score: int = 0,
        controversy_label: str = "mild",
        keywords: Optional[List[str]] = None,
        language: str = "ru"
    ) -> Optional[int]:
        """
        Add news item to database.
        
        Args:
            title: News title
            summary: Short summary
            full_text: Full article text
            url: Source URL
            source: Source name
            category: Category (tech, politics, etc.)
            published_at: Publication timestamp
            controversy_score: 0-100
            controversy_label: explosive/hot/spicy/mild
            keywords: List of keywords/tags
            language: 'ru' or 'en'
        
        Returns:
            News ID if inserted, None if duplicate
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO news (
                    title, summary, full_text, url, source, category,
                    published_at, controversy_score, controversy_label, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, summary, full_text, url, source, category,
                published_at or datetime.now().isoformat(),
                controversy_score, controversy_label, language
            ))
            
            news_id = cursor.lastrowid
            
            # Add keywords
            if keywords:
                for keyword in keywords:
                    cursor.execute("""
                        INSERT INTO keywords (news_id, keyword)
                        VALUES (?, ?)
                    """, (news_id, keyword.lower()))
            
            self.conn.commit()
            
            # Auto-cleanup if exceeds 50k
            self._cleanup_old_news()
            
            logger.debug(f"Added news: {title[:50]}... (ID: {news_id})")
            return news_id
            
        except sqlite3.IntegrityError:
            # Duplicate URL
            logger.debug(f"Duplicate news: {url}")
            return None
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
        min_controversy: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Full-text search in news.
        
        Args:
            query: Search phrase (Russian or English)
            category: Filter by category
            limit: Max results
            min_controversy: Minimum controversy score
        
        Returns:
            List of matching news items
        """
        cursor = self.conn.cursor()
        
        # Build FTS5 query
        # Support phrase search with quotes, AND/OR operators
        fts_query = query.replace("'", "''")  # Escape quotes
        
        sql = """
            SELECT 
                news.*,
                news_fts.rank
            FROM news_fts
            JOIN news ON news.id = news_fts.rowid
            WHERE news_fts MATCH ?
        """
        
        params = [fts_query]
        
        # Add filters
        if category and category != 'all':
            sql += " AND news.category = ?"
            params.append(category)
        
        if min_controversy is not None:
            sql += " AND news.controversy_score >= ?"
            params.append(min_controversy)
        
        # Order by relevance (rank) then controversy
        sql += """
            ORDER BY news_fts.rank, news.controversy_score DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        logger.info(f"Search '{query}': {len(results)} results")
        return results
    
    def get_recent(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        min_controversy: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent news items.
        
        Args:
            category: Filter by category
            limit: Max results
            min_controversy: Minimum controversy score
        
        Returns:
            List of recent news
        """
        cursor = self.conn.cursor()
        
        sql = "SELECT * FROM news WHERE 1=1"
        params = []
        
        if category and category != 'all':
            sql += " AND category = ?"
            params.append(category)
        
        if min_controversy is not None:
            sql += " AND controversy_score >= ?"
            params.append(min_controversy)
        
        sql += " ORDER BY published_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_keyword(
        self,
        keyword: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get news by exact keyword tag.
        
        Args:
            keyword: Keyword to search
            limit: Max results
        
        Returns:
            List of matching news
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT news.*
            FROM news
            JOIN keywords ON news.id = keywords.news_id
            WHERE keywords.keyword = ?
            ORDER BY news.published_at DESC
            LIMIT ?
        """, (keyword.lower(), limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_top_controversial(
        self,
        category: Optional[str] = None,
        limit: int = 10,
        days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most controversial news.
        
        Args:
            category: Filter by category
            limit: Max results
            days: Only from last N days
        
        Returns:
            List of most controversial news
        """
        cursor = self.conn.cursor()
        
        sql = "SELECT * FROM news WHERE 1=1"
        params = []
        
        if category and category != 'all':
            sql += " AND category = ?"
            params.append(category)
        
        if days:
            sql += " AND published_at >= datetime('now', '-' || ? || ' days')"
            params.append(days)
        
        sql += " ORDER BY controversy_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM news")
        total = cursor.fetchone()[0]
        
        # By category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM news
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By source
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM news
            GROUP BY source
            ORDER BY count DESC
            LIMIT 10
        """)
        top_sources = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Controversy distribution
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN controversy_score >= 75 THEN 1 ELSE 0 END) as explosive,
                SUM(CASE WHEN controversy_score >= 60 AND controversy_score < 75 THEN 1 ELSE 0 END) as hot,
                SUM(CASE WHEN controversy_score >= 40 AND controversy_score < 60 THEN 1 ELSE 0 END) as spicy,
                SUM(CASE WHEN controversy_score < 40 THEN 1 ELSE 0 END) as mild
            FROM news
        """)
        row = cursor.fetchone()
        controversy_dist = {
            'explosive': row[0] or 0,
            'hot': row[1] or 0,
            'spicy': row[2] or 0,
            'mild': row[3] or 0
        }
        
        return {
            'total_items': total,
            'by_category': by_category,
            'top_sources': top_sources,
            'controversy_distribution': controversy_dist
        }
    
    def _cleanup_old_news(self, max_items: int = 50000):
        """
        Remove oldest news if exceeds max_items.
        Keeps the most recent items.
        
        Args:
            max_items: Maximum items to keep (default: 50,000)
        """
        cursor = self.conn.cursor()
        
        # Check count
        cursor.execute("SELECT COUNT(*) FROM news")
        count = cursor.fetchone()[0]
        
        if count <= max_items:
            return
        
        # Delete oldest items
        to_delete = count - max_items
        
        cursor.execute("""
            DELETE FROM news
            WHERE id IN (
                SELECT id FROM news
                ORDER BY published_at ASC
                LIMIT ?
            )
        """, (to_delete,))
        
        self.conn.commit()
        
        # Optimize database
        cursor.execute("VACUUM")
        
        logger.info(f"Cleaned up {to_delete} old news items. Now: {max_items}")
    
    def bulk_insert(
        self,
        news_items: List[Dict[str, Any]]
    ) -> int:
        """
        Insert multiple news items efficiently.
        
        Args:
            news_items: List of news dictionaries
        
        Returns:
            Number of items inserted
        """
        cursor = self.conn.cursor()
        inserted = 0
        
        for item in news_items:
            try:
                cursor.execute("""
                    INSERT INTO news (
                        title, summary, full_text, url, source, category,
                        published_at, controversy_score, controversy_label, language
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('title', ''),
                    item.get('summary', ''),
                    item.get('full_text', item.get('summary', '')),
                    item.get('link', item.get('url', '')),
                    item.get('source', ''),
                    item.get('category', 'general'),
                    item.get('published', datetime.now().isoformat()),
                    item.get('controversy', {}).get('score', 0),
                    item.get('controversy', {}).get('label', 'mild'),
                    item.get('language', 'ru')
                ))
                
                news_id = cursor.lastrowid
                
                # Add keywords if present
                if 'keywords' in item and item['keywords']:
                    for kw in item['keywords']:
                        cursor.execute(
                            "INSERT INTO keywords (news_id, keyword) VALUES (?, ?)",
                            (news_id, kw.lower())
                        )
                
                inserted += 1
                
            except sqlite3.IntegrityError:
                # Duplicate URL, skip
                continue
        
        self.conn.commit()
        
        # Cleanup if needed
        self._cleanup_old_news()
        
        logger.info(f"Bulk inserted {inserted}/{len(news_items)} news items")
        return inserted
    
    def search_similar(
        self,
        news_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar news items using FTS5.
        
        Args:
            news_id: ID of news to find similar to
            limit: Max results
        
        Returns:
            List of similar news
        """
        cursor = self.conn.cursor()
        
        # Get original news
        cursor.execute("SELECT title, summary FROM news WHERE id = ?", (news_id,))
        row = cursor.fetchone()
        
        if not row:
            return []
        
        # Use title + summary as query
        query = f"{row[0]} {row[1]}"
        
        # Search excluding the original
        results = self.search(query, limit=limit + 1)
        return [r for r in results if r['id'] != news_id][:limit]
    
    def get_trending_keywords(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most frequent keywords.
        
        Args:
            limit: Max keywords to return
        
        Returns:
            List of {keyword, count} dicts
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT keyword, COUNT(*) as count
            FROM keywords
            GROUP BY keyword
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        return [{'keyword': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    def delete_old(self, days: int = 30) -> int:
        """
        Delete news older than N days.
        
        Args:
            days: Delete news older than this
        
        Returns:
            Number of items deleted
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM news
            WHERE published_at < datetime('now', '-' || ? || ' days')
        """, (days,))
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        logger.info(f"Deleted {deleted} news items older than {days} days")
        return deleted
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()


# Convenience functions

def create_news_database(db_path: str = "data/news.db") -> NewsDatabase:
    """Create and initialize news database."""
    return NewsDatabase(db_path)


def search_news(
    query: str,
    db_path: str = "data/news.db",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function for searching news.
    
    Args:
        query: Search phrase
        db_path: Database path
        **kwargs: Additional arguments for search()
    
    Returns:
        List of matching news items
    """
    with NewsDatabase(db_path) as db:
        return db.search(query, **kwargs)





