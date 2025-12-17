"""
Async news sources aggregator.
Uses async httpx for better performance.
"""
import re
import logging
from typing import List, Dict, Any, Optional
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



class AsyncNewsAggregator:
    """Async news aggregator with better performance."""
    
    # Import source lists from sync version
    def __init__(self, timeout: Optional[int] = None):
        # Import here to avoid circular imports
        from .news_sources import NewsAggregator
        self.RUSSIAN_SOURCES = NewsAggregator.RUSSIAN_SOURCES
        self.RUSSIAN_TECH_SOURCES = NewsAggregator.RUSSIAN_TECH_SOURCES
        self.RUSSIAN_POLITICS_SOURCES = NewsAggregator.RUSSIAN_POLITICS_SOURCES
        self.RUSSIAN_REGIONAL_SOURCES = getattr(NewsAggregator, 'RUSSIAN_REGIONAL_SOURCES', [])
        self.INTERNATIONAL_SOURCES = NewsAggregator.INTERNATIONAL_SOURCES
        self.INTERNATIONAL_ASIA_SOURCES = getattr(NewsAggregator, 'INTERNATIONAL_ASIA_SOURCES', [])
        self.INTERNATIONAL_AFRICA_SOURCES = getattr(NewsAggregator, 'INTERNATIONAL_AFRICA_SOURCES', [])
        self.EUROPEAN_SOURCES = NewsAggregator.EUROPEAN_SOURCES
        self.AI_SOURCES = NewsAggregator.AI_SOURCES
        self.US_SOURCES = NewsAggregator.US_SOURCES
        self.LEGAL_SOURCES = getattr(NewsAggregator, 'LEGAL_SOURCES', [])
        self.SOCIAL_MEDIA_SOURCES = getattr(NewsAggregator, 'SOCIAL_MEDIA_SOURCES', [])
    
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
                headers={"Accept-Charset": "utf-8", "User-Agent": "Mozilla/5.0"}
            )
        else:
            self.client = None
    
    async def fetch_rss_feed(
        self,
        url: str,
        max_items: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed asynchronously.
        
        Args:
            url: RSS feed URL
            max_items: Maximum items to fetch
            
        Returns:
            List of news items
        """
        if max_items is None:
            max_items = NEWS_MAX_ITEMS_PER_FEED
        if not self.client:
            logger.warning("httpx not available, cannot fetch async")
            return []
        
        if not feedparser:
            logger.warning("feedparser not available")
            return []
        
        try:
            logger.debug(f"Fetching RSS feed: {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.text)
            
            items = []
            for entry in feed.entries[:max_items]:
                try:
                    # Extract title and fix encoding
                    title = self._fix_encoding(entry.get('title', '').strip())
                    if not title:
                        continue
                    
                    # Extract summary/description and fix encoding
                    summary = self._fix_encoding(entry.get('summary', entry.get('description', '')).strip())
                    
                    # Clean HTML from summary
                    if summary and BeautifulSoup:
                        try:
                            soup = BeautifulSoup(summary, 'html.parser')
                            summary = soup.get_text(separator=' ', strip=True)
                            # Remove extra whitespace
                            summary = ' '.join(summary.split())
                        except Exception as e:
                            logger.debug(f"HTML cleaning error for {url}: {e}")
                            # Fallback: simple regex-based HTML tag removal
                            import re
                            summary = re.sub(r'<[^>]+>', '', summary)
                            summary = ' '.join(summary.split())
                    
                    # Extract link
                    link = entry.get('link', '')
                    
                    # Extract published date
                    published = entry.get('published', entry.get('updated', ''))
                    published_date = None
                    if published:
                        try:
                            published_date = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    
                    # Extract source and fix encoding
                    source = fix_double_encoding(feed.feed.get('title', ''))
                    if not source:
                        # Try to extract from URL
                        source = self._extract_source(url)
                    
                    item = {
                        'title': title,
                        'summary': summary[:500] if summary else '',  # Limit summary length
                        'link': link,
                        'source': source,
                        'published': published_date.isoformat() if published_date else None,
                        'category': self._extract_category(url)
                    }
                    
                    items.append(item)
                    
                except Exception as e:
                    logger.debug(f"Error parsing entry from {url}: {e}")
                    continue
            
            logger.debug(f"Fetched {len(items)} items from {url}")
            return items
            
        except httpx.HTTPError as e:
            logger.debug(f"HTTP error fetching {url}: {e}")
            return []
        except Exception as e:
            logger.debug(f"Error fetching {url}: {type(e).__name__}: {e}")
            return []
    
    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        # Simple extraction
        if 'lenta.ru' in url:
            return 'Lenta.ru'
        elif 'kommersant.ru' in url:
            return 'Kommersant'
        elif 'vedomosti.ru' in url:
            return 'Vedomosti'
        elif 'tass.ru' in url:
            return 'TASS'
        elif 'habr.com' in url:
            return 'Habr'
        elif 'vc.ru' in url:
            return 'VC.ru'
        elif 'nytimes.com' in url:
            return 'New York Times'
        elif 'bbc.co.uk' in url:
            return 'BBC'
        elif 'theguardian.com' in url:
            return 'The Guardian'
        elif 'euronews.com' in url:
            return 'Euronews'
        elif 'politico.eu' in url:
            return 'Politico EU'
        elif 'dw.com' in url:
            return 'Deutsche Welle'
        else:
            # Extract domain name
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                return domain.replace('www.', '').split('.')[0].title()
            except:
                return 'Unknown'
    
    def _extract_category(self, url: str) -> str:
        """Extract category from URL."""
        if any(x in url for x in ['tech', 'ai', 'habr', 'vc.ru', 'dtf']):
            return 'tech'
        elif any(x in url for x in ['politics', 'gazeta', 'meduza', 'interfax']):
            return 'politics'
        elif any(x in url for x in ['eu', 'europe', 'euronews', 'politico']):
            return 'europe'
        elif any(x in url for x in ['asia', 'china', 'japan']):
            return 'asia'
        elif any(x in url for x in ['africa']):
            return 'africa'
        else:
            return 'general'
    
    def _fix_encoding(self, text: str) -> str:
        """
        Fix encoding issues including double-encoded UTF-8 (mojibake).
        
        DEPRECATED: Use fix_double_encoding from utils.encoding instead.
        Kept for backward compatibility.
        """
        return fix_double_encoding(text)
    
    async def fetch_trending_topics(
        self,
        include_russian: bool = True,
        include_international: bool = True,
        include_ai: bool = True,
        include_politics: bool = True,
        include_us: bool = True,
        include_eu: bool = True,
        include_legal: bool = False,
        include_regional: bool = False,
        include_asia: bool = False,
        include_africa: bool = False,
        include_social: bool = False,
        max_per_source: int = 5,
        max_workers: int = 50  # Higher for async
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
            include_regional: Include Russian regional sources
            include_asia: Include Asian sources
            include_africa: Include African sources
            include_social: Include social media sources
            max_per_source: Maximum items per source
            max_workers: Maximum concurrent requests (async handles this automatically)
            
        Returns:
            List of unique news items
        """
        all_urls = []
        
        if include_russian:
            all_urls.extend(self.RUSSIAN_SOURCES)
            all_urls.extend(self.RUSSIAN_TECH_SOURCES)
        
        if include_politics:
            all_urls.extend(self.RUSSIAN_POLITICS_SOURCES)
        
        if include_regional:
            all_urls.extend(self.RUSSIAN_REGIONAL_SOURCES)
        
        if include_international:
            all_urls.extend(self.INTERNATIONAL_SOURCES)
        
        if include_asia:
            all_urls.extend(self.INTERNATIONAL_ASIA_SOURCES)
        
        if include_africa:
            all_urls.extend(self.INTERNATIONAL_AFRICA_SOURCES)
        
        if include_eu:
            all_urls.extend(self.EUROPEAN_SOURCES)
        
        if include_ai:
            all_urls.extend(self.AI_SOURCES)
        
        if include_us:
            all_urls.extend(self.US_SOURCES)
        
        if include_legal:
            all_urls.extend(self.LEGAL_SOURCES)
        
        if include_social:
            all_urls.extend(self.SOCIAL_MEDIA_SOURCES)
        
        logger.info(f"Fetching from {len(all_urls)} sources asynchronously...")
        
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
        
        logger.info(f"Fetched {len(unique_items)} unique items from {len(all_urls)} sources")
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

