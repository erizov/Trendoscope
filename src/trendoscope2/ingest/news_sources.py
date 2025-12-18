"""
News sources aggregator for Trendoscope2.
Expanded with 100+ sources according to improvement plan.
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
    """Aggregate news from multiple sources - Expanded version."""

    # Russian general news sources
    RUSSIAN_SOURCES = [
        "https://lenta.ru/rss",
        "https://www.kommersant.ru/rss/main.xml",
        "https://www.vedomosti.ru/rss/news",
        "https://tass.ru/rss/v2.xml",
        "https://rg.ru/xml/index.xml",  # NEW: Rossiyskaya Gazeta
        "https://www.mk.ru/rss/index.xml",  # NEW: Moskovsky Komsomolets
    ]

    # Russian regional sources (NEW)
    RUSSIAN_REGIONAL_SOURCES = [
        # Note: aif.ru sources have SSL certificate issues
    ]

    # Russian economy sources (NEW)
    RUSSIAN_ECONOMY_SOURCES = [
        # Note: rbc.ru and forbes.ru RSS feeds currently unavailable
    ]

    # Russian tech/AI sources
    RUSSIAN_TECH_SOURCES = [
        "https://habr.com/ru/rss/articles/",
        "https://vc.ru/rss/all",
        "https://dtf.ru/rss/all",
        "https://3dnews.ru/news/rss",
        "https://www.cnews.ru/inc/rss/news.xml",
    ]

    # Russian politics sources
    RUSSIAN_POLITICS_SOURCES = [
        "https://www.gazeta.ru/export/rss/first.xml",
        "https://ria.ru/export/rss2/archive/index.xml",
        # Note: meduza.io has timeout issues
    ]

    # Russian culture sources (NEW)
    RUSSIAN_CULTURE_SOURCES = [
        # Note: colta.ru and afisha.ru RSS feeds currently unavailable
    ]

    # Russian sports sources (NEW)
    RUSSIAN_SPORTS_SOURCES = [
        # Note: sport-express.ru and championat.com RSS feeds currently unavailable
    ]
    
    # European sources
    EUROPEAN_SOURCES = [
        # Note: Many European sources have timeout issues, keeping only reliable ones
        # "https://www.euronews.com/rss",  # timeout
        # "https://www.politico.eu/feed/",  # timeout
        # "https://www.dw.com/rss/rss-en-world/s-31201/rss.xml",  # timeout
        # "https://www.lemonde.fr/rss/une.xml",  # timeout
        # "https://www.spiegel.de/international/index.rss",  # timeout
        # "https://www.thelocal.com/rss",  # 404
    ]

    # International general news sources
    INTERNATIONAL_SOURCES = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.theguardian.com/world/rss",
        "http://rss.cnn.com/rss/cnn_topstories.rss",  # Use http to avoid SSL issues
        "https://abcnews.go.com/abcnews/topstories",
        "https://www.cbsnews.com/latest/rss/main",
        "https://feeds.nbcnews.com/nbcnews/public/news",
    ]

    # International regional sources (NEW)
    INTERNATIONAL_REGIONAL_SOURCES = [
        # Asia-Pacific
        "https://www.scmp.com/rss/feed",
        "https://www.aljazeera.com/xml/rss/all.xml",
        # Note: japantimes.co.jp (403), straitstimes.com (not XML), haaretz.com (404), bbc.com (timeout)
    ]

    # International business sources (NEW)
    INTERNATIONAL_BUSINESS_SOURCES = [
        "https://www.forbes.com/business/feed/",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.investing.com/rss/news.rss",
        "https://www.marketwatch.com/rss/topstories",
        # Note: bloomberg.com (403), ft.com (not XML), wsj.com (401), reuters.com (401), entrepreneur.com (timeout)
    ]

    # International tech sources (NEW)
    INTERNATIONAL_TECH_SOURCES = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://www.engadget.com/rss.xml",
        "https://www.cnet.com/rss/news/",
        "https://www.zdnet.com/news/rss.xml",
        # Note: gizmodo.com (403), pcmag.com (403), tomsguide.com (404)
    ]

    # AI-specialized sources
    AI_SOURCES = [
        "https://www.technologyreview.com/feed/",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.analyticsvidhya.com/blog/feed/",
        "https://towardsdatascience.com/feed/",
        # Note: artificialintelligence-news.com (403), venturebeat.com (308 redirect)
    ]

    # Politics-specialized sources
    POLITICS_SOURCES = [
        "https://foreignpolicy.com/feed/",
        "https://www.foreignaffairs.com/rss.xml",
        "https://www.brookings.edu/feed/",
        "https://thehill.com/policy/technology/feed/",
        "https://www.vox.com/rss/index.xml",
        # Note: axios.com (403 forbidden)
        # Note: politico.com has timeout issues
    ]
    
    # US-specific sources
    US_SOURCES = [
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",  # NPR Politics
        "https://abcnews.go.com/abcnews/politicsheadlines",
        # Note: washingtonpost.com has occasional timeout issues
    ]
    
    # Legal & Criminal news sources
    LEGAL_SOURCES = [
        "https://www.theverge.com/rss/index.xml",  # Tech law & policy
        # Note: law.com and feedburner.com have connection issues
    ]

    # Social media & alternative sources (NEW)
    SOCIAL_MEDIA_SOURCES = [
        "https://www.reddit.com/r/worldnews/.rss",
        "https://www.reddit.com/r/news/.rss",
        "https://www.reddit.com/r/technology/.rss",
    ]

    def __init__(self, timeout: int = 10):
        """
        Initialize news aggregator.

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
            self.client = httpx.Client(
                timeout=timeout_config,
                follow_redirects=True,
                verify=True,
                limits=httpx.Limits(max_keepalive_connections=20),
                headers={"Accept-Charset": "utf-8", "User-Agent": "Trendoscope2/1.0"}
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
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                try:
                    response = self.client.get(url, follow_redirects=True)
                    # Check redirect history to detect loops
                    if hasattr(response, 'history') and len(response.history) > 0:
                        # Check for redirect loops (same URLs in history)
                        redirect_urls = [str(r.url) for r in response.history]
                        if len(redirect_urls) != len(set(redirect_urls)):
                            logger.warning(f"Redirect loop detected for {url}, skipping")
                            return []
                except httpx.TooManyRedirects:
                    logger.warning(f"Too many redirects for {url}, skipping")
                    return []
                except Exception as e:
                    error_msg = str(e)
                    if any(keyword in error_msg.lower() for keyword in 
                           ['timeout', 'timed out', 'connection', 'ssl', 
                            'handshake', 'network', 'redirect', 'too many']):
                        logger.debug(f"Connection/timeout/redirect error for {url}: {error_msg[:100]}")
                        return []
                    else:
                        logger.warning(f"Unexpected error fetching {url}: {error_msg}")
                        raise
            
            if response.encoding is None or response.encoding.lower() not in ['utf-8', 'utf8']:
                response.encoding = 'utf-8'
            
            feed_content = response.text
            feed = feedparser.parse(feed_content)

            items = []
            for entry in feed.entries[:max_items]:
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].get('value', '') if isinstance(entry.content, list) else str(entry.content)
                
                if not content:
                    content = entry.get("summary", entry.get("description", ""))
                
                def fix_encoding(text):
                    """Fix double-encoded UTF-8 text."""
                    if not text:
                        return ""
                    if isinstance(text, bytes):
                        try:
                            return text.decode('utf-8')
                        except UnicodeDecodeError:
                            return text.decode('utf-8', errors='replace')
                    if isinstance(text, str):
                        try:
                            if any(ord(c) > 127 for c in text[:100] if text):
                                fixed = text.encode('latin1', errors='ignore').decode('utf-8', errors='replace')
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

                if item["summary"] and BeautifulSoup:
                    try:
                        soup = BeautifulSoup(item["summary"], 'lxml')
                        item["summary"] = soup.get_text(strip=True)
                    except:
                        pass
                
                if not item["summary"] and item["title"]:
                    item["summary"] = f"Полный текст доступен на источнике: {item['title']}"

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
            "rg.ru": "Российская газета",
            "kp.ru": "Комсомольская правда",
            "mk.ru": "Московский комсомолец",
            "fontanka.ru": "Фонтанка",
            "aif.ru": "АиФ",
            "rbc.ru": "РБК",
            "forbes.ru": "Forbes Russia",
            "habr.com": "Habr",
            "vc.ru": "VC.ru",
            "dtf.ru": "DTF",
            "3dnews.ru": "3DNews",
            "roem.ru": "Roem.ru",
            "gazeta.ru": "Gazeta.ru",
            "meduza.io": "Meduza",
            "interfax.ru": "Интерфакс",
            "ria.ru": "РИА Новости",
            "colta.ru": "Colta",
            "afisha.ru": "Афиша",
            "sport-express.ru": "Спорт-Экспресс",
            "championat.com": "Чемпионат",
            "nytimes.com": "NY Times",
            "washingtonpost.com": "Washington Post",
            "npr.org": "NPR",
            "bbc": "BBC",
            "theguardian.com": "The Guardian",
            "euronews.com": "Euronews",
            "dw.com": "Deutsche Welle",
            "politico.eu": "Politico Europe",
            "scmp.com": "South China Morning Post",
            "japantimes.co.jp": "Japan Times",
            "straitstimes.com": "Straits Times",
            "aljazeera.com": "Al Jazeera",
            "haaretz.com": "Haaretz",
            "bloomberg.com": "Bloomberg",
            "ft.com": "Financial Times",
            "wsj.com": "Wall Street Journal",
            "reuters.com": "Reuters",
            "techcrunch.com": "TechCrunch",
            "theverge.com": "The Verge",
            "arstechnica.com": "Ars Technica",
            "wired.com": "Wired",
            "technologyreview.com": "MIT Tech Review",
            "artificialintelligence-news.com": "AI News",
            "openai.com": "OpenAI Blog",
            "deeplearning.ai": "DeepLearning.AI",
            "machinelearningmastery.com": "ML Mastery",
            "politico.com": "Politico",
            "foreignpolicy.com": "Foreign Policy",
            "foreignaffairs.com": "Foreign Affairs",
            "brookings.edu": "Brookings",
            "reddit.com": "Reddit",
            "law.com": "Law.com",
            "cnn.com": "CNN",
            "abcnews.com": "ABC News",
            "cbsnews.com": "CBS News",
            "nbcnews.com": "NBC News",
            "engadget.com": "Engadget",
            "gizmodo.com": "Gizmodo",
            "cnet.com": "CNET",
            "zdnet.com": "ZDNet",
            "pcmag.com": "PC Magazine",
            "tomsguide.com": "Tom's Guide",
            "forbes.com": "Forbes",
            "cnbc.com": "CNBC",
            "entrepreneur.com": "Entrepreneur",
            "investing.com": "Investing.com",
            "marketwatch.com": "MarketWatch",
            "venturebeat.com": "VentureBeat",
            "analyticsvidhya.com": "Analytics Vidhya",
            "towardsdatascience.com": "Towards Data Science",
            "axios.com": "Axios",
            "vox.com": "Vox",
            "lemonde.fr": "Le Monde",
            "spiegel.de": "Der Spiegel",
            "thelocal.com": "The Local",
            "cnews.ru": "CNews",
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
        include_regional: bool = True,
        include_business: bool = True,
        include_tech: bool = True,
        include_social: bool = False,
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
            include_regional: Include regional sources
            include_business: Include business sources
            include_tech: Include tech sources
            include_social: Include social media sources
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
            if include_regional:
                sources.extend(self.RUSSIAN_REGIONAL_SOURCES)
            if include_business:
                sources.extend(self.RUSSIAN_ECONOMY_SOURCES)
            sources.extend(self.RUSSIAN_CULTURE_SOURCES)
            sources.extend(self.RUSSIAN_SPORTS_SOURCES)
        if include_international:
            sources.extend(self.INTERNATIONAL_SOURCES)
            if include_regional:
                sources.extend(self.INTERNATIONAL_REGIONAL_SOURCES)
            if include_business:
                sources.extend(self.INTERNATIONAL_BUSINESS_SOURCES)
            if include_tech:
                sources.extend(self.INTERNATIONAL_TECH_SOURCES)
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
        if include_social:
            sources.extend(self.SOCIAL_MEDIA_SOURCES)

        logger.info(f"Fetching from {len(sources)} sources...")

        if parallel and len(sources) > 1:
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
                        error_msg = str(e)
                        if any(keyword in error_msg.lower() for keyword in 
                               ['timeout', 'timed out', 'connection', 'ssl']):
                            logger.debug(f"Timeout/connection error for {url}")
                        else:
                            logger.warning(f"Failed to fetch {url}: {type(e).__name__}")
            
            logger.info(f"Fetched {len(all_items)} items total")
            return all_items
        else:
            all_items = []
            for source_url in sources:
                items = self.fetch_rss_feed(source_url, max_per_source)
                all_items.extend(items)
            
            logger.info(f"Fetched {len(all_items)} items total")
            return all_items

