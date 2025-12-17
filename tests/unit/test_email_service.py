"""
Unit tests for Email Service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.services.email_service import EmailService


class TestEmailService:
    """Test EmailService functionality."""
    
    def test_initialization_without_credentials(self):
        """Test service initialization without credentials."""
        service = EmailService()
        assert service.is_available() is False
        assert service.smtp_user is None
        assert service.smtp_password is None
    
    def test_initialization_with_credentials(self):
        """Test service initialization with credentials."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        assert service.is_available() is True
        assert service.smtp_user == "test@example.com"
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        service = EmailService()
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert service.validate_email(email) is True, f"{email} should be valid"
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        service = EmailService()
        
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test@example",  # Note: some validators accept this
            "test @example.com",
            ""
        ]
        
        for email in invalid_emails:
            result = service.validate_email(email)
            # Some edge cases might pass validation, but most should fail
            if email in ["test..test@example.com"]:
                # This might pass some validators
                pass
            else:
                assert result is False, f"{email} should be invalid"
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            text_content="Test content"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "password")
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_with_html(self, mock_smtp):
        """Test email sending with HTML content."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<h1>Test</h1>",
            text_content="Test"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error."""
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            text_content="Test content"
        )
        
        assert result is False
    
    def test_send_email_invalid_email(self):
        """Test email sending with invalid email address."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        result = service.send_email(
            to_email="invalid-email",
            subject="Test Subject",
            text_content="Test content"
        )
        
        assert result is False
    
    def test_send_email_service_disabled(self):
        """Test email sending when service is disabled."""
        service = EmailService()  # No credentials
        
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            text_content="Test content"
        )
        
        assert result is False
    
    def test_format_digest_html(self):
        """Test HTML digest formatting."""
        service = EmailService()
        news_items = [
            {
                "title": "News 1",
                "summary": "Summary 1",
                "link": "http://example.com/1"
            },
            {
                "title": "News 2",
                "summary": "Summary 2",
                "link": "http://example.com/2"
            }
        ]
        
        html = service._format_digest_html(news_items, "en")
        
        assert "News 1" in html
        assert "News 2" in html
        assert "http://example.com/1" in html
        assert "http://example.com/2" in html
        assert "<html>" in html
        assert "<h1>" in html
    
    def test_format_digest_text(self):
        """Test text digest formatting."""
        service = EmailService()
        news_items = [
            {
                "title": "News 1",
                "summary": "Summary 1",
                "link": "http://example.com/1"
            }
        ]
        
        text = service._format_digest_text(news_items, "en")
        
        assert "News 1" in text
        assert "Summary 1" in text
        assert "http://example.com/1" in text
        assert "Daily News Digest" in text
    
    @patch('smtplib.SMTP')
    def test_send_daily_digest_success(self, mock_smtp):
        """Test successful daily digest sending."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
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
        
        result = service.send_daily_digest(
            to_email="recipient@example.com",
            news_items=news_items,
            language="en"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
    
    def test_send_daily_digest_empty_items(self):
        """Test daily digest with empty news items."""
        service = EmailService(
            smtp_user="test@example.com",
            smtp_password="password"
        )
        
        result = service.send_daily_digest(
            to_email="recipient@example.com",
            news_items=[],
            language="en"
        )
        
        assert result is False
    
    def test_send_daily_digest_limits_to_5(self):
        """Test daily digest limits to 5 items."""
        service = EmailService()
        news_items = [
            {"title": f"News {i}", "summary": f"Summary {i}", "link": f"http://example.com/{i}"}
            for i in range(10)
        ]
        
        html = service._format_digest_html(news_items, "en")
        
        # Should only include first 5
        assert "News 0" in html
        assert "News 4" in html
        assert "News 5" not in html
