"""
Email service for sending daily digests and notifications.
Uses SMTP (free) for sending emails.
Supports async processing and caching.
"""
import logging
import smtplib
import asyncio
import hashlib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails via SMTP.
    Supports HTML and plain text emails.
    """
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        cache_enabled: bool = True,
        rate_limit_per_minute: int = 10
    ):
        """
        Initialize email service.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username (email)
            smtp_password: SMTP password or app password
            from_email: From email address
            cache_enabled: Enable email caching
            rate_limit_per_minute: Max emails per minute per recipient
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user
        self.enabled = bool(smtp_user and smtp_password)
        self.cache_enabled = cache_enabled
        self.rate_limit_per_minute = rate_limit_per_minute
        
        # Caching: track sent emails to avoid duplicates
        self._sent_cache: Dict[str, datetime] = {}
        
        # Rate limiting: track emails per recipient
        self._rate_limit_tracker: Dict[str, List[datetime]] = defaultdict(list)
        
        if not self.enabled:
            logger.warning(
                "Email service disabled: SMTP credentials not provided"
            )
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _get_email_hash(
        self,
        to_email: str,
        subject: str,
        content: str
    ) -> str:
        """Generate hash for email caching."""
        content_str = f"{to_email}:{subject}:{content}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _check_rate_limit(self, to_email: str) -> bool:
        """Check if rate limit is exceeded for recipient."""
        now = datetime.now()
        # Remove old entries (older than 1 minute)
        self._rate_limit_tracker[to_email] = [
            ts for ts in self._rate_limit_tracker[to_email]
            if (now - ts).total_seconds() < 60
        ]
        
        # Check if limit exceeded
        if len(self._rate_limit_tracker[to_email]) >= self.rate_limit_per_minute:
            return False
        return True
    
    def _check_cache(self, email_hash: str) -> bool:
        """Check if email was already sent (within last hour)."""
        if not self.cache_enabled:
            return False
        
        if email_hash in self._sent_cache:
            sent_time = self._sent_cache[email_hash]
            if (datetime.now() - sent_time).total_seconds() < 3600:  # 1 hour
                return True
            else:
                # Remove old cache entry
                del self._sent_cache[email_hash]
        return False
    
    def _update_cache(self, email_hash: str):
        """Update cache with sent email."""
        if self.cache_enabled:
            self._sent_cache[email_hash] = datetime.now()
            # Clean old cache entries (older than 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            self._sent_cache = {
                k: v for k, v in self._sent_cache.items()
                if v > cutoff
            }
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email to recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email service is disabled")
            return False
        
        if not self.validate_email(to_email):
            logger.error(f"Invalid email address: {to_email}")
            return False
        
        # Check rate limit
        if not self._check_rate_limit(to_email):
            logger.warning(f"Rate limit exceeded for {to_email}")
            return False
        
        # Check cache
        content = html_content or text_content or ""
        email_hash = self._get_email_hash(to_email, subject, content)
        if self._check_cache(email_hash):
            logger.info(f"Email already sent recently (cached): {to_email}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            elif text_content:
                # If only text, use it for both
                html_part = MIMEText(
                    f"<pre>{text_content}</pre>", 'html', 'utf-8'
                )
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            
            # Update cache and rate limit tracker
            self._update_cache(email_hash)
            self._rate_limit_tracker[to_email].append(datetime.now())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email asynchronously (non-blocking).
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            True if sent successfully, False otherwise
        """
        return await asyncio.to_thread(
            self.send_email,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_daily_digest_async(
        self,
        to_email: str,
        news_items: List[Dict[str, Any]],
        language: str = "ru"
    ) -> bool:
        """
        Send daily news digest email asynchronously.
        
        Args:
            to_email: Recipient email address
            news_items: List of news items to include
            language: Language for email (ru, en)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not news_items:
            logger.warning("No news items to send in digest")
            return False
        
        # Format email
        subject = (
            "🔥 5 самых провокационных новостей дня"
            if language == "ru"
            else "🔥 Top 5 Most Controversial News Today"
        )
        
        html_content = self._format_digest_html(news_items, language)
        text_content = self._format_digest_text(news_items, language)
        
        return await self.send_email_async(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def send_daily_digest(
        self,
        to_email: str,
        news_items: List[Dict[str, Any]],
        language: str = "ru"
    ) -> bool:
        """
        Send daily news digest email.
        
        Args:
            to_email: Recipient email address
            news_items: List of news items to include
            language: Language for email (ru, en)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not news_items:
            logger.warning("No news items to send in digest")
            return False
        
        # Format email
        subject = (
            "🔥 5 самых провокационных новостей дня"
            if language == "ru"
            else "🔥 Top 5 Most Controversial News Today"
        )
        
        html_content = self._format_digest_html(news_items, language)
        text_content = self._format_digest_text(news_items, language)
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _format_digest_html(
        self,
        news_items: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Format daily digest as HTML."""
        items_html = []
        for i, item in enumerate(news_items[:5], 1):
            title = item.get('title', '')
            summary = item.get('summary', '')[:200] + "..."
            link = item.get('link', '#')
            
            items_html.append(f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 3px solid #ff6b6b;">
                <h3 style="margin-top: 0;">{i}. {title}</h3>
                <p>{summary}</p>
                <a href="{link}" style="color: #4a90e2;">Read more →</a>
            </div>
            """)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔥 Daily News Digest</h1>
                {"".join(items_html)}
                <hr>
                <p style="color: #666; font-size: 12px;">
                    <a href="http://localhost:8004">View all on Trendoscope →</a>
                </p>
            </div>
        </body>
        </html>
        """
    
    def _format_digest_text(
        self,
        news_items: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Format daily digest as plain text."""
        lines = ["🔥 Daily News Digest", ""]
        
        for i, item in enumerate(news_items[:5], 1):
            title = item.get('title', '')
            summary = item.get('summary', '')[:200] + "..."
            link = item.get('link', '#')
            
            lines.append(f"{i}. {title}")
            lines.append(f"   {summary}")
            lines.append(f"   Read more: {link}")
            lines.append("")
        
        lines.append("View all: http://localhost:8004")
        return "\n".join(lines)
    
    def is_available(self) -> bool:
        """Check if email service is available."""
        return self.enabled
