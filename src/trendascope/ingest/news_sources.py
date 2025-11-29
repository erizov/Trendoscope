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
        max_per_source: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending topics from all sources.

        Args:
            include_russian: Include Russian general sources
            include_international: Include international general sources
            include_ai: Include AI-specialized sources
            include_politics: Include politics-specialized sources
            include_us: Include US-specific sources
            include_eu: Include European sources
            max_per_source: Max items per source

        Returns:
            List of all news items
        """
        all_items = []

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

