"""
News sources aggregator.
Collects trending topics from Russian and international sources.
"""
import re
import logging
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

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


class NewsAggregator:
    """Aggregate news from multiple sources."""

    # Russian general news sources
    RUSSIAN_SOURCES = [
        "https://lenta.ru/rss",
        "https://www.kommersant.ru/RSS/main.xml",
        "https://www.vedomosti.ru/rss/news",
        "https://tass.ru/rss/v2.xml",
    ]

    # Russian tech/AI sources
    RUSSIAN_TECH_SOURCES = [
        "https://habr.com/ru/rss/best/",
        "https://vc.ru/rss/all",
        "https://dtf.ru/rss/all",
        "https://3dnews.ru/news/rss",
        "https://roem.ru/feed/",
    ]

    # Russian politics sources
    RUSSIAN_POLITICS_SOURCES = [
        "https://www.gazeta.ru/export/rss/first.xml",
        "https://meduza.io/rss/all",
        "https://www.interfax.ru/rss.asp",
        "https://ria.ru/export/rss2/archive/index.xml",
    ]
    
    # European sources
    EUROPEAN_SOURCES = [
        "https://www.euronews.com/rss",
        "https://www.politico.eu/feed/",
        "https://www.dw.com/rss/rss-en-world/s-31201/rss.xml",
    ]

    # International general news sources
    INTERNATIONAL_SOURCES = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
    ]

    # AI-specialized sources
    AI_SOURCES = [
        "https://www.technologyreview.com/feed/",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://www.artificialintelligence-news.com/feed/",
        "https://openai.com/blog/rss.xml",
        "https://www.deeplearning.ai/the-batch/feed/",
        "https://machinelearningmastery.com/feed/",
    ]

    # Politics-specialized sources
    POLITICS_SOURCES = [
        "https://www.politico.com/rss/politics08.xml",
        "https://foreignpolicy.com/feed/",
        "https://www.foreignaffairs.com/rss.xml",
        "https://www.brookings.edu/feed/",
    ]
    
    # US-specific sources
    US_SOURCES = [
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://www.washingtonpost.com/rss/politics",
        "https://feeds.npr.org/1001/rss.xml",
    ]
    
    # Legal & Criminal news sources
    LEGAL_SOURCES = [
        "https://www.theverge.com/rss/index.xml",  # Tech law & policy
        "https://www.law.com/dailyreport/rss/",
        "https://feeds.feedburner.com/scl/scl",  # Supreme Court
    ]

    def __init__(self, timeout: int = 10):
        """
        Initialize news aggregator.

        Args:
            timeout: HTTP request timeout (reduced to 10s for faster response)
        """
        self.timeout = timeout
        if httpx:
            # Configure timeout with separate connect and read timeouts
            # SSL handshake is part of connect timeout
            timeout_config = httpx.Timeout(
                connect=5.0,  # 5s for connection + SSL handshake
                read=timeout,  # Read timeout
                write=5.0,     # Write timeout
                pool=10.0      # Pool timeout
            )
            self.client = httpx.Client(
                timeout=timeout_config,
                follow_redirects=True,
                verify=True,  # SSL verification
                limits=httpx.Limits(max_keepalive_connections=20),
                headers={"Accept-Charset": "utf-8"}  # Request UTF-8
            )
        else:
            self.client = None

    def fetch_rss_feed(self, url: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed with timeout and error handling.

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
            # Suppress SSL warnings for timeout errors
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                try:
                    # Add retry logic for network requests
                    from ..core.resilience import retry_with_backoff
                    
                    @retry_with_backoff(max_attempts=2, initial_delay=0.5)
                    def _fetch():
                        return self.client.get(url)
                    
                    response = _fetch()
                except Exception as e:
                    # Handle various timeout and connection errors
                    error_type = type(e).__name__
                    error_msg = str(e)
                    
                    # Check for timeout/connection errors
                    if any(keyword in error_msg.lower() for keyword in 
                           ['timeout', 'timed out', 'connection', 'ssl', 
                            'handshake', 'network']):
                        # Log at debug level to avoid cluttering output
                        logger.debug(
                            f"Connection/timeout error for {url}: "
                            f"{error_type} - {error_msg[:100]}"
                        )
                        return []
                    else:
                        # Re-raise unexpected errors
                        logger.warning(
                            f"Unexpected error fetching {url}: "
                            f"{error_type} - {error_msg}"
                        )
                        raise
            
            # Ensure UTF-8 encoding for proper Russian character handling
            if response.encoding is None or response.encoding.lower() not in ['utf-8', 'utf8']:
                response.encoding = 'utf-8'
            
            # Parse feed with explicit encoding handling
            feed_content = response.text
            feed = feedparser.parse(feed_content)

            items = []
            for entry in feed.entries[:max_items]:
                # Try multiple fields for content
                content = ""
                
                # Try to get the most detailed content available
                if hasattr(entry, 'content') and entry.content:
                    # Some feeds have content field with full text
                    content = entry.content[0].get('value', '') if isinstance(entry.content, list) else str(entry.content)
                
                if not content:
                    # Fallback to summary or description
                    content = entry.get("summary", entry.get("description", ""))
                
                # Fix encoding issues (mojibake - double-encoded UTF-8)
                def fix_encoding(text):
                    """Fix double-encoded UTF-8 text (mojibake)."""
                    if not text:
                        return ""
                    if isinstance(text, bytes):
                        try:
                            return text.decode('utf-8')
                        except UnicodeDecodeError:
                            return text.decode('utf-8', errors='replace')
                    if isinstance(text, str):
                        # Check if it looks like mojibake (common Russian chars)
                        # If text contains patterns like "Р"Рё" instead of "Ди", it's double-encoded
                        try:
                            # Try to detect and fix double encoding
                            # Common pattern: UTF-8 bytes interpreted as Latin-1
                            if any(ord(c) > 127 for c in text[:100] if text):
                                # Try to fix: encode as latin1 then decode as utf8
                                fixed = text.encode('latin1', errors='ignore').decode('utf-8', errors='replace')
                                # Only use if it looks better (has fewer replacement chars)
                                if fixed and '\ufffd' not in fixed[:50]:
                                    return fixed
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            pass
                        return text
                    return str(text)
                
                item = {
                    "title": fix_encoding(entry.get("title", "")),
                    "summary": fix_encoding(content),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": self._extract_source(url),
                }

                # Clean HTML from summary
                if item["summary"] and BeautifulSoup:
                    try:
                        soup = BeautifulSoup(item["summary"], 'lxml')
                        item["summary"] = soup.get_text(strip=True)
                    except:
                        # If cleaning fails, keep original
                        pass
                
                # Ensure we have at least title
                if not item["summary"] and item["title"]:
                    # If no summary, use title as fallback message
                    item["summary"] = f"Полный текст доступен на источнике: {item['title']}"

                # Only add if has title
                if item["title"]:
                    items.append(item)

            logger.debug(f"Fetched {len(items)} items from {url}")
            return items

        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return []

    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        patterns = {
            "lenta.ru": "Lenta.ru",
            "kommersant.ru": "Коммерсантъ",
            "vedomosti.ru": "Ведомости",
            "tass.ru": "ТАСС",
            "habr.com": "Habr",
            "vc.ru": "VC.ru",
            "dtf.ru": "DTF",
            "3dnews.ru": "3DNews",
            "roem.ru": "Roem.ru",
            "gazeta.ru": "Gazeta.ru",
            "meduza.io": "Meduza",
            "interfax.ru": "Интерфакс",
            "ria.ru": "РИА Новости",
            "nytimes.com": "NY Times",
            "washingtonpost.com": "Washington Post",
            "npr.org": "NPR",
            "bbc": "BBC",
            "theguardian.com": "The Guardian",
            "euronews.com": "Euronews",
            "dw.com": "Deutsche Welle",
            "politico.eu": "Politico Europe",
            "technologyreview.com": "MIT Tech Review",
            "techcrunch.com": "TechCrunch",
            "theverge.com": "The Verge",
            "artificialintelligence-news.com": "AI News",
            "openai.com": "OpenAI Blog",
            "deeplearning.ai": "DeepLearning.AI",
            "machinelearningmastery.com": "ML Mastery",
            "politico.com": "Politico",
            "foreignpolicy.com": "Foreign Policy",
            "foreignaffairs.com": "Foreign Affairs",
            "brookings.edu": "Brookings",
        }

        for pattern, name in patterns.items():
            if pattern in url:
                return name

        return "Unknown"

    def fetch_trending_topics(
        self,
        include_russian: bool = True,
        include_international: bool = True,
        include_ai: bool = True,
        include_politics: bool = True,
        include_us: bool = True,
        include_eu: bool = True,
        include_legal: bool = False,
        max_per_source: int = 5,
        parallel: bool = True,
        max_workers: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending topics from all sources with parallel fetching.

        Args:
            include_russian: Include Russian general sources
            include_international: Include international general sources
            include_ai: Include AI-specialized sources
            include_politics: Include politics-specialized sources
            include_us: Include US-specific sources
            include_eu: Include European sources
            include_legal: Include legal/criminal news sources
            max_per_source: Max items per source
            parallel: Use parallel fetching (faster)
            max_workers: Max parallel threads

        Returns:
            List of all news items
        """
        sources = []
        if include_russian:
            sources.extend(self.RUSSIAN_SOURCES)
            sources.extend(self.RUSSIAN_TECH_SOURCES)
            sources.extend(self.RUSSIAN_POLITICS_SOURCES)
        if include_international:
            sources.extend(self.INTERNATIONAL_SOURCES)
        if include_ai:
            sources.extend(self.AI_SOURCES)
        if include_politics:
            sources.extend(self.POLITICS_SOURCES)
        if include_us:
            sources.extend(self.US_SOURCES)
        if include_eu:
            sources.extend(self.EUROPEAN_SOURCES)
        if include_legal:
            sources.extend(self.LEGAL_SOURCES)

        logger.info(f"Fetching from {len(sources)} sources...")

        if parallel and len(sources) > 1:
            # Parallel fetching for speed
            all_items = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.fetch_rss_feed, url, max_per_source): url
                    for url in sources
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        items = future.result()
                        all_items.extend(items)
                    except Exception as e:
                        # Log at debug level for timeout/connection errors
                        error_msg = str(e)
                        if any(keyword in error_msg.lower() for keyword in 
                               ['timeout', 'timed out', 'connection', 'ssl']):
                            logger.debug(f"Timeout/connection error for {url}")
                        else:
                            logger.warning(f"Failed to fetch {url}: {type(e).__name__}")
            
            logger.info(f"Fetched {len(all_items)} items total")
            return all_items
        else:
            # Sequential fetching (fallback)
            all_items = []
            for source_url in sources:
                items = self.fetch_rss_feed(source_url, max_per_source)
                all_items.extend(items)
            
            logger.info(f"Fetched {len(all_items)} items total")
            return all_items

    def extract_key_topics(
        self,
        news_items: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[str]:
        """
        Extract most common topics from news.

        Args:
            news_items: List of news items
            top_n: Number of top topics

        Returns:
            List of topic strings
        """
        from collections import Counter

        # Extract keywords from titles
        words = []
        for item in news_items:
            title = item.get("title", "")
            # Simple tokenization
            title_words = re.findall(r'\b\w{4,}\b', title.lower())
            words.extend(title_words)

        # Count frequencies
        word_counts = Counter(words)

        # Filter common stop words
        stop_words = {
            'quot', 'nbsp', 'this', 'that', 'with', 'from',
            'have', 'been', 'were', 'said', 'says', 'будет',
            'может', 'года', 'более', 'также', 'сообщает'
        }

        topics = [
            word for word, count in word_counts.most_common(top_n * 3)
            if word not in stop_words
        ]

        return topics[:top_n]

    def close(self):
        """Close HTTP client."""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def fetch_trending_news(
    max_items: int = 20,
    include_russian: bool = True,
    include_international: bool = True,
    include_ai: bool = True,
    include_politics: bool = True
) -> Dict[str, Any]:
    """
    Fetch trending news (convenience function).

    Args:
        max_items: Maximum total items
        include_russian: Include Russian sources
        include_international: Include international sources
        include_ai: Include AI-specialized sources
        include_politics: Include politics-specialized sources

    Returns:
        Dictionary with news and topics
    """
    with NewsAggregator() as aggregator:
        items_per_source = max(2, max_items // 10)

        news_items = aggregator.fetch_trending_topics(
            include_russian=include_russian,
            include_international=include_international,
            include_ai=include_ai,
            include_politics=include_politics,
            max_per_source=items_per_source
        )

        topics = aggregator.extract_key_topics(news_items[:max_items])

        return {
            "news_items": news_items[:max_items],
            "top_topics": topics,
            "count": len(news_items[:max_items])
        }

