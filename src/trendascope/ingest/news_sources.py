"""
News sources aggregator.
Collects trending topics from Russian and international sources.
"""
import re
from typing import List, Dict, Any
from datetime import datetime

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

    # Russian sources
    RUSSIAN_SOURCES = [
        "https://lenta.ru/rss",
        "https://www.kommersant.ru/RSS/main.xml",
        "https://www.vedomosti.ru/rss/news",
        "https://tass.ru/rss/v2.xml",
    ]

    # International sources
    INTERNATIONAL_SOURCES = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
    ]

    def __init__(self, timeout: int = 30):
        """
        Initialize news aggregator.

        Args:
            timeout: HTTP request timeout
        """
        self.timeout = timeout
        if httpx:
            self.client = httpx.Client(timeout=timeout, follow_redirects=True)
        else:
            self.client = None

    def fetch_rss_feed(self, url: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed.

        Args:
            url: RSS feed URL
            max_items: Maximum items to fetch

        Returns:
            List of news items
        """
        if not feedparser or not self.client:
            return []

        try:
            response = self.client.get(url)
            feed = feedparser.parse(response.text)

            items = []
            for entry in feed.entries[:max_items]:
                item = {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": self._extract_source(url),
                }

                # Clean HTML from summary
                if item["summary"] and BeautifulSoup:
                    soup = BeautifulSoup(item["summary"], 'lxml')
                    item["summary"] = soup.get_text(strip=True)

                items.append(item)

            return items

        except Exception:
            return []

    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        patterns = {
            "lenta.ru": "Lenta.ru",
            "kommersant.ru": "Коммерсантъ",
            "vedomosti.ru": "Ведомости",
            "tass.ru": "ТАСС",
            "nytimes.com": "NY Times",
            "bbc": "BBC",
            "theguardian.com": "The Guardian",
        }

        for pattern, name in patterns.items():
            if pattern in url:
                return name

        return "Unknown"

    def fetch_trending_topics(
        self,
        include_russian: bool = True,
        include_international: bool = True,
        max_per_source: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending topics from all sources.

        Args:
            include_russian: Include Russian sources
            include_international: Include international sources
            max_per_source: Max items per source

        Returns:
            List of all news items
        """
        all_items = []

        sources = []
        if include_russian:
            sources.extend(self.RUSSIAN_SOURCES)
        if include_international:
            sources.extend(self.INTERNATIONAL_SOURCES)

        for source_url in sources:
            items = self.fetch_rss_feed(source_url, max_per_source)
            all_items.extend(items)

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
    include_international: bool = True
) -> Dict[str, Any]:
    """
    Fetch trending news (convenience function).

    Args:
        max_items: Maximum total items
        include_russian: Include Russian sources
        include_international: Include international sources

    Returns:
        Dictionary with news and topics
    """
    with NewsAggregator() as aggregator:
        items_per_source = max(2, max_items // 5)

        news_items = aggregator.fetch_trending_topics(
            include_russian=include_russian,
            include_international=include_international,
            max_per_source=items_per_source
        )

        topics = aggregator.extract_key_topics(news_items[:max_items])

        return {
            "news_items": news_items[:max_items],
            "top_topics": topics,
            "count": len(news_items[:max_items])
        }

