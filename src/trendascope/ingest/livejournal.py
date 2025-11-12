"""
LiveJournal scraper module.
Fetches posts via RSS and HTML parsing, including hidden posts.
"""
import re
import time
from typing import List, Dict, Optional, Any
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

try:
    from trafilatura import extract
except ImportError:
    extract = None


class LiveJournalScraper:
    """Scraper for LiveJournal blogs."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize scraper.

        Args:
            username: LJ username for accessing hidden posts
            password: LJ password for accessing hidden posts
            timeout: HTTP request timeout in seconds
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)
        self.authenticated = False

        if username and password:
            self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with LiveJournal to access hidden posts."""
        try:
            login_url = "https://www.livejournal.com/login.bml"
            data = {
                "user": self.username,
                "password": self.password,
                "action:login": "Log in",
            }
            response = self.client.post(login_url, data=data)
            self.authenticated = response.status_code == 200
        except Exception:
            self.authenticated = False

    def fetch_rss(
        self,
        blog_url: str,
        max_entries: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch posts from RSS feed.

        Args:
            blog_url: Blog URL (e.g., https://username.livejournal.com)
            max_entries: Maximum number of entries to fetch

        Returns:
            List of post dictionaries with basic metadata
        """
        if not blog_url.endswith('/'):
            blog_url += '/'

        rss_url = f"{blog_url}data/rss"
        posts = []

        try:
            response = self.client.get(rss_url)
            feed = feedparser.parse(response.text)

            for entry in feed.entries[:max_entries]:
                post = {
                    "url": entry.get("link", ""),
                    "title": entry.get("title", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "author": entry.get("author", ""),
                }
                posts.append(post)

        except Exception as e:
            pass

        return posts

    def fetch_archive_urls(
        self,
        blog_url: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[str]:
        """
        Fetch all post URLs from archive pages.

        Args:
            blog_url: Blog URL
            start_year: Starting year (optional)
            end_year: Ending year (optional)

        Returns:
            List of post URLs
        """
        if not blog_url.endswith('/'):
            blog_url += '/'

        current_year = datetime.now().year
        start_year = start_year or 2000
        end_year = end_year or current_year

        all_urls = []

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                archive_url = f"{blog_url}{year}/{month:02d}/"
                try:
                    response = self.client.get(archive_url)
                    if response.status_code != 200:
                        continue

                    soup = BeautifulSoup(response.text, 'lxml')

                    # Find post links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if '.livejournal.com/' in href and '/html' in href:
                            if href not in all_urls:
                                all_urls.append(href)

                    time.sleep(0.5)

                except Exception:
                    continue

        return all_urls

    def fetch_post(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a single post.

        Args:
            url: Post URL

        Returns:
            Dictionary with post content and metadata
        """
        try:
            response = self.client.get(url)
            if response.status_code != 200:
                return None

            html = response.text
            soup = BeautifulSoup(html, 'lxml')

            # Extract with trafilatura
            text_plain = extract(
                html,
                include_comments=False,
                include_tables=True,
                include_images=False
            ) or ""

            # Extract metadata
            title = ""
            title_tag = soup.find('h1', class_='entry-title')
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Extract date
            published = ""
            date_tag = soup.find('time', class_='published')
            if date_tag:
                published = date_tag.get('datetime', '')

            # Extract tags
            tags = []
            tag_links = soup.find_all('a', rel='tag')
            for tag in tag_links:
                tags.append(tag.get_text(strip=True))

            # Extract comment count
            comments_count = 0
            comments_link = soup.find('a', href=re.compile(r'\?thread='))
            if comments_link:
                match = re.search(r'(\d+)\s*комментари', 
                                comments_link.get_text())
                if match:
                    comments_count = int(match.group(1))

            # Extract likes if available
            likes_count = 0

            return {
                "url": url,
                "title": title,
                "text_plain": text_plain,
                "text_html": html,
                "published": published,
                "tags": tags,
                "comments_count": comments_count,
                "likes_count": likes_count,
                "author": self._extract_author(url),
            }

        except Exception:
            return None

    def _extract_author(self, url: str) -> str:
        """Extract author username from URL."""
        match = re.search(r'https?://([^.]+)\.livejournal\.com', url)
        return match.group(1) if match else ""

    def fetch_all_posts(
        self,
        blog_url: str,
        max_posts: int = 100,
        use_rss: bool = True,
        use_archive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch all posts from a blog.

        Args:
            blog_url: Blog URL
            max_posts: Maximum number of posts to fetch
            use_rss: Whether to use RSS feed
            use_archive: Whether to crawl archive

        Returns:
            List of post dictionaries
        """
        urls = set()
        posts = []

        # Get URLs from RSS
        if use_rss:
            rss_posts = self.fetch_rss(blog_url, max_entries=max_posts)
            for post in rss_posts:
                urls.add(post["url"])

        # Get URLs from archive
        if use_archive:
            archive_urls = self.fetch_archive_urls(blog_url)
            urls.update(archive_urls[:max_posts])

        # Fetch full posts
        for i, url in enumerate(list(urls)[:max_posts]):
            post = self.fetch_post(url)
            if post:
                posts.append(post)

            # Rate limiting
            if (i + 1) % 10 == 0:
                time.sleep(2)
            else:
                time.sleep(0.5)

        return posts

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def scrape_livejournal(
    blog_url: str,
    max_posts: int = 50,
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_rss: bool = True,
    use_archive: bool = False
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape LiveJournal blog.
    
    Args:
        blog_url: Blog URL to scrape
        max_posts: Maximum number of posts to fetch
        username: Optional username for hidden posts
        password: Optional password for hidden posts
        use_rss: Whether to use RSS feed (default: True)
        use_archive: Whether to crawl archive (default: False)
    
    Returns:
        List of post dictionaries
    
    Example:
        >>> posts = scrape_livejournal(
        ...     "https://civil-engineer.livejournal.com",
        ...     max_posts=100
        ... )
    """
    with LiveJournalScraper(username=username, password=password) as scraper:
        return scraper.fetch_all_posts(
            blog_url=blog_url,
            max_posts=max_posts,
            use_rss=use_rss,
            use_archive=use_archive
        )

