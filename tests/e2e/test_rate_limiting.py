"""
Rate Limiting Tests for Email and Telegram services.
"""
import pytest
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app
from trendoscope2.services.email_service import EmailService
from trendoscope2.services.telegram_service import TelegramService

client = TestClient(app)


class TestEmailRateLimiting:
    """Test Email service rate limiting."""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password",
            rate_limit_per_minute=2
        )
        
        # Send 2 emails (should succeed)
        result1 = service._check_rate_limit("test@example.com")
        result2 = service._check_rate_limit("test@example.com")
        
        assert result1 is True
        assert result2 is True
        
        # Update tracker manually
        from datetime import datetime
        service._rate_limit_tracker["test@example.com"].append(datetime.now())
        service._rate_limit_tracker["test@example.com"].append(datetime.now())
        
        # Third should be rate limited
        result3 = service._check_rate_limit("test@example.com")
        assert result3 is False
    
    def test_rate_limit_resets(self):
        """Test that rate limit resets after time window."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password",
            rate_limit_per_minute=1
        )
        
        # Set old timestamp (more than 1 minute ago)
        from datetime import datetime, timedelta
        old_time = datetime.now() - timedelta(seconds=70)
        service._rate_limit_tracker["test@example.com"] = [old_time]
        
        # Should allow new email (old entry removed by _check_rate_limit)
        result = service._check_rate_limit("test@example.com")
        # After check, old entry should be removed, so should allow
        assert result is True
    
    @patch('smtplib.SMTP')
    def test_caching_prevents_duplicates(self, mock_smtp):
        """Test that caching prevents duplicate emails."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password",
            cache_enabled=True
        )
        
        # Send first email
        service.send_email(
            to_email="test@example.com",
            subject="Test",
            text_content="Test content"
        )
        
        # Check cache
        email_hash = service._get_email_hash(
            "test@example.com",
            "Test",
            "Test content"
        )
        assert service._check_cache(email_hash) is True
        
        # Try to send same email again (should be cached)
        call_count_before = mock_server.send_message.call_count
        service.send_email(
            to_email="test@example.com",
            subject="Test",
            text_content="Test content"
        )
        call_count_after = mock_server.send_message.call_count
        
        # Should not send again (cached)
        assert call_count_after == call_count_before


class TestTelegramRateLimiting:
    """Test Telegram service rate limiting."""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        service = TelegramService(
            bot_token="test_token",
            rate_limit_per_minute=2
        )
        
        # Check rate limit
        result1 = service._check_rate_limit("@test_channel")
        result2 = service._check_rate_limit("@test_channel")
        
        assert result1 is True
        assert result2 is True
        
        # Update tracker manually
        from datetime import datetime
        service._rate_limit_tracker["@test_channel"].append(datetime.now())
        service._rate_limit_tracker["@test_channel"].append(datetime.now())
        
        # Third should be rate limited
        result3 = service._check_rate_limit("@test_channel")
        assert result3 is False
    
    def test_caching_prevents_duplicates(self):
        """Test that caching prevents duplicate posts."""
        service = TelegramService(
            bot_token="test_token",
            cache_enabled=True
        )
        
        # Create post hash
        post_text = "Test post"
        post_hash = service._get_post_hash("@test_channel", post_text)
        
        # Add to cache
        service._update_cache(post_hash)
        
        # Check cache
        assert service._check_cache(post_hash) is True
        
        # Old cache entry should be removed
        from datetime import datetime, timedelta
        old_time = datetime.now() - timedelta(hours=25)
        old_hash = "old_hash"
        service._sent_cache[old_hash] = old_time
        
        # Clean cache
        service._update_cache("new_hash")
        
        # Old entry should be removed
        assert old_hash not in service._sent_cache


class TestAsyncProcessing:
    """Test async processing for Email and Telegram."""
    
    @pytest.mark.asyncio
    async def test_email_async_send(self):
        """Test async email sending."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await service.send_email_async(
                to_email="test@example.com",
                subject="Test",
                text_content="Test content"
            )
            
            assert result is True
            mock_server.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_async_digest(self):
        """Test async daily digest sending."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        news_items = [
            {
                "title": "News 1",
                "summary": "Summary 1",
                "link": "http://example.com/1"
            }
        ]
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await service.send_daily_digest_async(
                to_email="test@example.com",
                news_items=news_items,
                language="en"
            )
            
            assert result is True
            mock_server.send_message.assert_called_once()
