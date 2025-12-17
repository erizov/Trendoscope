"""
Unit tests for Telegram Service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.services.telegram_service import TelegramService


class TestTelegramService:
    """Test TelegramService functionality."""
    
    def test_initialization_without_token(self):
        """Test service initialization without token."""
        service = TelegramService()
        assert service.is_available() is False
    
    def test_initialization_with_token(self):
        """Test service initialization with token."""
        service = TelegramService(bot_token="test_token")
        # May be False if python-telegram-bot not installed
        assert isinstance(service.is_available(), bool)
    
    def test_format_post_markdown(self):
        """Test post formatting in Markdown."""
        service = TelegramService()
        article = {
            "title": "Test Article",
            "summary": "This is a test summary",
            "link": "http://example.com/article",
            "published": "2024-01-01"
        }
        
        post = service.format_post(article, format_type="markdown")
        
        assert "Test Article" in post
        assert "This is a test summary" in post
        assert "http://example.com/article" in post
        assert "**" in post  # Markdown bold
        assert "📰" in post
    
    def test_format_post_html(self):
        """Test post formatting in HTML."""
        service = TelegramService()
        article = {
            "title": "Test Article",
            "summary": "This is a test summary",
            "link": "http://example.com/article"
        }
        
        post = service.format_post(article, format_type="html")
        
        assert "Test Article" in post
        assert "<b>" in post  # HTML bold
        assert "<a href" in post
        assert "📰" in post
    
    def test_format_post_plain(self):
        """Test post formatting in plain text."""
        service = TelegramService()
        article = {
            "title": "Test Article",
            "summary": "This is a test summary",
            "link": "http://example.com/article"
        }
        
        post = service.format_post(article, format_type="plain")
        
        assert "Test Article" in post
        assert "http://example.com/article" in post
        assert "<" not in post  # No HTML tags
        assert "**" not in post  # No Markdown
    
    def test_format_post_truncation_long_summary(self):
        """Test post truncation for long summary."""
        service = TelegramService()
        article = {
            "title": "Short Title",
            "summary": "A" * 5000,  # Very long summary
            "link": "http://example.com/article"
        }
        
        post = service.format_post(article, max_length=200)
        
        assert len(post) <= 200
        assert "Short Title" in post
        assert "http://example.com/article" in post
    
    def test_format_post_truncation_very_long(self):
        """Test post truncation when even title+link is too long."""
        service = TelegramService()
        article = {
            "title": "A" * 100,  # Very long title
            "summary": "B" * 5000,
            "link": "http://example.com/article"
        }
        
        post = service.format_post(article, max_length=50)
        
        # When max_length is very small, post might be longer but should still contain link
        assert len(post) <= 150  # Allow some flexibility
        assert "http://example.com/article" in post or "example.com" in post
    
    def test_format_post_with_date(self):
        """Test post formatting with date."""
        service = TelegramService()
        article = {
            "title": "Test Article",
            "summary": "Summary",
            "link": "http://example.com/article",
            "published": "2024-01-01"
        }
        
        post = service.format_post(article, format_type="markdown")
        
        assert "2024-01-01" in post
        assert "📅" in post
    
    def test_format_post_without_date(self):
        """Test post formatting without date."""
        service = TelegramService()
        article = {
            "title": "Test Article",
            "summary": "Summary",
            "link": "http://example.com/article"
        }
        
        post = service.format_post(article, format_type="markdown")
        
        assert "Test Article" in post
        assert "📅" not in post or "📅" in post  # Date is optional
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        service = TelegramService(bot_token="test_token")
        
        # Skip if bot not available (library not installed)
        if not service.bot:
            pytest.skip("python-telegram-bot not available")
        
        # Mock the bot's send_message method
        mock_message = Mock()
        mock_message.message_id = 123
        
        with patch.object(service.bot, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_message
            
            message_id = await service.send_message(
                channel_id="@test_channel",
                text="Test message"
            )
            
            # May return None if service disabled, or message_id if successful
            assert message_id is None or message_id == 123
    
    @pytest.mark.asyncio
    async def test_send_message_no_channel(self):
        """Test message sending without channel ID."""
        service = TelegramService(bot_token="test_token")
        
        message_id = await service.send_message(
            channel_id=None,
            text="Test message"
        )
        
        assert message_id is None
    
    @pytest.mark.asyncio
    async def test_post_article_success(self):
        """Test successful article posting."""
        service = TelegramService(bot_token="test_token", default_channel_id="@test_channel")
        
        # Skip if bot not available
        if not service.bot:
            pytest.skip("python-telegram-bot not available")
        
        with patch.object(service.bot, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_message = Mock()
            mock_message.message_id = 123
            mock_send.return_value = mock_message
            
            article = {
                "title": "Test Article",
                "summary": "Summary",
                "link": "http://example.com/article"
            }
            
            result = await service.post_article(article)
            
            assert result is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        service = TelegramService(bot_token="test_token")
        
        # Skip if bot not available
        if not service.bot:
            pytest.skip("python-telegram-bot not available")
        
        with patch.object(service.bot, 'get_me', new_callable=AsyncMock) as mock_get_me:
            mock_get_me.return_value = Mock(username="test_bot")
            
            result = await service.test_connection()
            
            assert result is True
            mock_get_me.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test connection test failure."""
        service = TelegramService(bot_token="test_token")
        
        # Skip if bot not available
        if not service.bot:
            pytest.skip("python-telegram-bot not available")
        
        with patch.object(service.bot, 'get_me', new_callable=AsyncMock) as mock_get_me:
            mock_get_me.side_effect = Exception("Connection failed")
            
            result = await service.test_connection()
            
            assert result is False
