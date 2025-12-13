"""
Async news sources aggregator.
Uses async httpx for better performance.
"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:
    httpx = None

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class AsyncNewsAggregator:
    """Async news aggregator with better performance."""
    
    # Import source lists from sync version
    from .news_sources import (
        RUSSIAN_SOURCES,
        RUSSIAN_TECH_SOURCES,
        RUSSIAN_POLITICS_SOURCES,
        EUROPEAN_SOURCES,
        INTERNATIONAL_SOURCES,
        AI_SOURCES,
        US_SOURCES,
        LEGAL_SOURCES
    )
    
    def __init__(self, timeout: int = 10):
        """
        Initialize async news aggregator.
        
        Args:
            timeout: HTTP request timeout
        """
        self.timeout = timeout
        if httpx:
            timeout_config = httpx.Timeout(
                connect=5.0,
                read=timeout,
                write=5.0,
                pool=10.0
            )
            self.client = httpx.AsyncClient(
                timeout=timeout_config,
                follow_redirects=True,
                verify=True,
                limits=httpx.Limits(max_keepalive_connections=20),
                headers={"Accept-Charset": "utf-8"}
            )
        else:
            self.client = None
    
    async def fetch_rss_feed(
        self,
        url: str,
        max_items: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed asynchronously.
        
        Args:
            url: RSS feed URL
            max_items: Maximum items to fetch
            
        Returns:
            List of news items
        """
        if not feedparser or not self.client:
            return []
        
        try:
            logger.debug(f"Fetching RSS: {url}")
            
            try:
                response = await self.client.get(url)
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                
                if any(keyword in error_msg.lower() for keyword in 
                       ['timeout', 'timed out', 'connection', 'ssl', 
                        'handshake', 'network']):
                    logger.debug(
                        f"Connection/timeout error for {url}: "
                        f"{error_type} - {error_msg[:100]}"
                    )
                    return []
                else:
                    logger.warning(
                        f"Unexpected error fetching {url}: "
                        f"{error_type} - {error_msg}"
                    )
                    raise
            
            # Ensure UTF-8 encoding
            if response.encoding is None or response.encoding.lower() not in ['utf-8', 'utf8']:
                response.encoding = 'utf-8'
            
            # Parse RSS feed
            feed = feedparser.parse(response.text)
            
            if feed.bozo and feed.bozo_exception:
                logger.debug(f"Feed parse warning for {url}: {feed.bozo_exception}")
            
            items = []
            for entry in feed.entries[:max_items]:
                # Fix encoding issues
                title = self._fix_encoding(entry.get("title", ""))
                summary = entry.get("summary", "") or entry.get("description", "")
                content = self._fix_encoding(summary)
                
                # Extract published date
                published = entry.get("published", "")
                if published:
                    try:
                        published_dt = feedparser._parse_date(published)
                        published = published_dt.isoformat() if published_dt else ""
                    except:
                        published = ""
                
                item = {
                    "title": title,
                    "summary": content,
                    "full_text": content,
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", url),
                    "published": published,
                    "fetched_at": datetime.now().isoformat()
                }
                items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return []
    
    def _fix_encoding(self, text: str) -> str:
        """Fix encoding issues (mojibake)."""
        if not text:
            return ""
        
        try:
            # Try to detect and fix double-encoded UTF-8
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # Check for mojibake patterns
            if 'Р' in text and 'РІ' in text:
                # Likely double-encoded, try to fix
                try:
                    text = text.encode('latin-1').decode('utf-8')
                except:
                    pass
            
            return text
        except Exception as e:
            logger.debug(f"Encoding fix failed: {e}")
            return str(text)
    
    async def fetch_trending_topics(
        self,
        include_russian: bool = True,
        include_international: bool = True,
        include_ai: bool = True,
        include_politics: bool = True,
        include_us: bool = True,
        include_eu: bool = True,
        include_legal: bool = False,
        max_per_source: int = 5,
        max_workers: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending topics from all sources asynchronously.
        
        Args:
            include_russian: Include Russian sources
            include_international: Include international sources
            include_ai: Include AI sources
            include_politics: Include politics sources
            include_us: Include US sources
            include_eu: Include EU sources
            include_legal: Include legal sources
            max_per_source: Maximum items per source
            max_workers: Maximum concurrent requests
            
        Returns:
            List of news items
        """
        all_urls = []
        
        if include_russian:
            all_urls.extend(self.RUSSIAN_SOURCES)
            all_urls.extend(self.RUSSIAN_TECH_SOURCES)
        
        if include_politics:
            all_urls.extend(self.RUSSIAN_POLITICS_SOURCES)
        
        if include_international:
            all_urls.extend(self.INTERNATIONAL_SOURCES)
        
        if include_eu:
            all_urls.extend(self.EUROPEAN_SOURCES)
        
        if include_ai:
            all_urls.extend(self.AI_SOURCES)
        
        if include_us:
            all_urls.extend(self.US_SOURCES)
        
        if include_legal:
            all_urls.extend(self.LEGAL_SOURCES)
        
        # Fetch all feeds concurrently
        tasks = [
            self.fetch_rss_feed(url, max_per_source)
            for url in all_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_items = []
        for result in results:
            if isinstance(result, Exception):
                logger.debug(f"Feed fetch exception: {result}")
                continue
            all_items.extend(result)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            url = item.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
        
        return unique_items
    
    async def close(self):
        """Close async HTTP client."""
        if self.client:
            await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

