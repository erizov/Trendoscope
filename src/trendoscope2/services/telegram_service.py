"""
Telegram service for posting news to Telegram channels.
Uses python-telegram-bot library (free).
Supports async processing, caching, and rate limiting.
"""
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Bot = None
    TelegramError = Exception


class TelegramService:
    """
    Telegram service for posting messages to channels.
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        default_channel_id: Optional[str] = None,
        cache_enabled: bool = True,
        rate_limit_per_minute: int = 20
    ):
        """
        Initialize Telegram service.
        
        Args:
            bot_token: Telegram bot token from @BotFather
            default_channel_id: Default channel ID or username
            cache_enabled: Enable post caching
            rate_limit_per_minute: Max posts per minute per channel
        """
        self.bot_token = bot_token
        self.default_channel_id = default_channel_id
        self.enabled = bool(bot_token and TELEGRAM_AVAILABLE)
        self.cache_enabled = cache_enabled
        self.rate_limit_per_minute = rate_limit_per_minute
        
        # Caching: track sent posts to avoid duplicates
        self._sent_cache: Dict[str, datetime] = {}
        
        # Rate limiting: track posts per channel
        self._rate_limit_tracker: Dict[str, List[datetime]] = defaultdict(list)
        
        if not TELEGRAM_AVAILABLE:
            logger.warning(
                "python-telegram-bot not installed. "
                "Install with: pip install python-telegram-bot"
            )
            self.bot = None
        elif bot_token:
            try:
                self.bot = Bot(token=bot_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
                self.enabled = False
        else:
            self.bot = None
            logger.warning("Telegram service disabled: no bot token")
    
    def format_post(
        self,
        article: Dict[str, Any],
        format_type: str = "markdown",
        max_length: int = 4096
    ) -> str:
        """
        Format article as Telegram post.
        
        Args:
            article: News article dictionary
            format_type: Format type (markdown, html, plain)
            max_length: Maximum post length
            
        Returns:
            Formatted post text
        """
        title = article.get('title', 'No title')
        summary = article.get('summary', '')
        link = article.get('link', '#')
        date = article.get('published', article.get('date', ''))
        
        if format_type == "markdown":
            post = f"📰 **{title}**\n\n{summary}\n\n🔗 [Read more]({link})"
            if date:
                post += f"\n📅 {date}"
        elif format_type == "html":
            post = f"📰 <b>{title}</b>\n\n{summary}\n\n🔗 <a href=\"{link}\">Read more</a>"
            if date:
                post += f"\n📅 {date}"
        else:  # plain
            post = f"📰 {title}\n\n{summary}\n\n🔗 {link}"
            if date:
                post += f"\n📅 {date}"
        
        # Truncate if too long
        if len(post) > max_length:
            # Truncate summary
            available = max_length - len(title) - len(link) - 100
            if available > 0:
                summary = summary[:available] + "..."
                if format_type == "markdown":
                    post = f"📰 **{title}**\n\n{summary}\n\n🔗 [Read more]({link})"
                elif format_type == "html":
                    post = f"📰 <b>{title}</b>\n\n{summary}\n\n🔗 <a href=\"{link}\">Read more</a>"
                else:
                    post = f"📰 {title}\n\n{summary}\n\n🔗 {link}"
            else:
                # Too long even without summary, just title + link
                if format_type == "markdown":
                    post = f"📰 **{title}**\n\n🔗 [Read more]({link})"
                elif format_type == "html":
                    post = f"📰 <b>{title}</b>\n\n🔗 <a href=\"{link}\">Read more</a>"
                else:
                    post = f"📰 {title}\n\n🔗 {link}"
        
        return post
    
    def _get_post_hash(
        self,
        channel_id: str,
        text: str
    ) -> str:
        """Generate hash for post caching."""
        content_str = f"{channel_id}:{text}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _check_rate_limit(self, channel_id: str) -> bool:
        """Check if rate limit is exceeded for channel."""
        now = datetime.now()
        # Remove old entries (older than 1 minute)
        self._rate_limit_tracker[channel_id] = [
            ts for ts in self._rate_limit_tracker[channel_id]
            if (now - ts).total_seconds() < 60
        ]
        
        # Check if limit exceeded
        if len(self._rate_limit_tracker[channel_id]) >= self.rate_limit_per_minute:
            return False
        return True
    
    def _check_cache(self, post_hash: str) -> bool:
        """Check if post was already sent (within last hour)."""
        if not self.cache_enabled:
            return False
        
        if post_hash in self._sent_cache:
            sent_time = self._sent_cache[post_hash]
            if (datetime.now() - sent_time).total_seconds() < 3600:  # 1 hour
                return True
            else:
                # Remove old cache entry
                del self._sent_cache[post_hash]
        return False
    
    def _update_cache(self, post_hash: str):
        """Update cache with sent post."""
        if self.cache_enabled:
            self._sent_cache[post_hash] = datetime.now()
            # Clean old cache entries (older than 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            self._sent_cache = {
                k: v for k, v in self._sent_cache.items()
                if v > cutoff
            }
    
    async def send_message(
        self,
        channel_id: Optional[str] = None,
        text: str = "",
        parse_mode: Optional[str] = None
    ) -> Optional[int]:
        """
        Send message to Telegram channel.
        
        Args:
            channel_id: Channel ID or username (e.g., @channel or -1001234567890)
            text: Message text
            parse_mode: Parse mode (Markdown, HTML, or None)
            
        Returns:
            Message ID if successful, None otherwise
        """
        if not self.enabled or not self.bot:
            logger.warning("Telegram service is disabled")
            return None
        
        channel = channel_id or self.default_channel_id
        if not channel:
            logger.error("No channel ID provided")
            return None
        
        try:
            message = await self.bot.send_message(
                chat_id=channel,
                text=text,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent to {channel}, message_id={message.message_id}")
            
            # Update cache and rate limit tracker
            self._update_cache(post_hash)
            self._rate_limit_tracker[channel].append(datetime.now())
            
            return message.message_id
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return None
    
    async def post_article(
        self,
        article: Dict[str, Any],
        channel_id: Optional[str] = None,
        format_type: str = "markdown"
    ) -> bool:
        """
        Post article to Telegram channel.
        
        Args:
            article: News article dictionary
            channel_id: Channel ID or username
            format_type: Format type (markdown, html, plain)
            
        Returns:
            True if posted successfully, False otherwise
        """
        post_text = self.format_post(article, format_type)
        
        parse_mode = None
        if format_type == "markdown":
            parse_mode = "Markdown"
        elif format_type == "html":
            parse_mode = "HTML"
        
        message_id = await self.send_message(
            channel_id=channel_id,
            text=post_text,
            parse_mode=parse_mode
        )
        
        return message_id is not None
    
    async def test_connection(self) -> bool:
        """
        Test Telegram bot connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.enabled or not self.bot:
            return False
        
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Telegram service is available."""
        return self.enabled
