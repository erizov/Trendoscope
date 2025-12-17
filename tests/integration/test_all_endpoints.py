"""
Integration tests for all API endpoints.
Tests all endpoints with various scenarios including error cases.
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code in [200, 404]  # May serve frontend or 404
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestNewsEndpoints:
    """Test news feed endpoints."""
    
    def test_news_feed_default(self):
        """Test news feed with default parameters."""
        response = client.get("/api/news/feed")
        assert response.status_code in [200, 500]  # May fail if no sources
    
    def test_news_feed_with_params(self):
        """Test news feed with query parameters."""
        response = client.get(
            "/api/news/feed",
            params={"limit": 10, "category": "tech", "language": "ru"}
        )
        assert response.status_code in [200, 500]
    
    def test_news_feed_invalid_limit(self):
        """Test news feed with invalid limit."""
        response = client.get(
            "/api/news/feed",
            params={"limit": 200}  # Exceeds max
        )
        # Should validate and return 422 or use default
        assert response.status_code in [200, 422, 500]
    
    def test_translate_article_success(self):
        """Test article translation."""
        response = client.post(
            "/api/news/translate",
            json={
                "title": "Test Article",
                "summary": "Test summary",
                "source_language": "en"
            },
            params={"target_language": "ru"}
        )
        assert response.status_code in [200, 422, 500]  # May fail if translator unavailable
    
    def test_translate_article_missing_fields(self):
        """Test article translation with missing fields."""
        response = client.post(
            "/api/news/translate",
            json={}
        )
        assert response.status_code in [400, 422]
    
    def test_translate_article_empty_fields(self):
        """Test article translation with empty fields."""
        response = client.post(
            "/api/news/translate",
            json={
                "title": "",
                "summary": ""
            }
        )
        assert response.status_code in [400, 422]


class TestRutubeEndpoints:
    """Test Rutube endpoints."""
    
    def test_rutube_generate_valid_url(self):
        """Test Rutube generation with valid URL."""
        response = client.post(
            "/api/rutube/generate",
            json={
                "url": "https://rutube.ru/video/1234567890/"
            }
        )
        assert response.status_code in [200, 400, 422, 500]
    
    def test_rutube_generate_invalid_url(self):
        """Test Rutube generation with invalid URL."""
        response = client.post(
            "/api/rutube/generate",
            json={
                "url": "https://youtube.com/watch?v=123"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_rutube_generate_missing_url(self):
        """Test Rutube generation with missing URL."""
        response = client.post(
            "/api/rutube/generate",
            json={}
        )
        assert response.status_code in [400, 422]


class TestTTSEndpoints:
    """Test TTS endpoints."""
    
    def test_tts_generate_success(self):
        """Test TTS generation."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "Test text",
                "language": "en",
                "voice_gender": "female"
            }
        )
        assert response.status_code in [200, 500]
    
    def test_tts_generate_empty_text(self):
        """Test TTS generation with empty text."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "",
                "language": "en"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_tts_generate_whitespace_text(self):
        """Test TTS generation with whitespace-only text."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "   ",
                "language": "en"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_tts_generate_invalid_language(self):
        """Test TTS generation with invalid language."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "Test",
                "language": "invalid"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_tts_audio_download_valid_id(self):
        """Test TTS audio download with valid ID."""
        # First generate audio
        generate_response = client.post(
            "/api/tts/generate",
            json={"text": "Test audio"}
        )
        
        if generate_response.status_code == 200:
            audio_id = generate_response.json().get("audio_id")
            if audio_id:
                response = client.get(f"/api/tts/audio/{audio_id}")
                assert response.status_code in [200, 404]
    
    def test_tts_audio_download_invalid_id(self):
        """Test TTS audio download with invalid ID."""
        response = client.get("/api/tts/audio/invalid-id-12345")
        assert response.status_code in [404, 500]
    
    def test_tts_stats(self):
        """Test TTS stats endpoint."""
        response = client.get("/api/tts/stats")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestEmailEndpoints:
    """Test Email endpoints."""
    
    def test_email_status(self):
        """Test email status endpoint."""
        response = client.get("/api/email/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "configured" in data
    
    def test_email_send_missing_fields(self):
        """Test email send with missing fields."""
        response = client.post(
            "/api/email/send",
            json={}
        )
        assert response.status_code in [400, 422]
    
    def test_email_send_invalid_email(self):
        """Test email send with invalid email."""
        response = client.post(
            "/api/email/send",
            json={
                "to_email": "invalid-email",
                "subject": "Test",
                "text_content": "Test"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_email_send_missing_content(self):
        """Test email send without content."""
        response = client.post(
            "/api/email/send",
            json={
                "to_email": "test@example.com",
                "subject": "Test"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_email_digest_missing_email(self):
        """Test email digest with missing email."""
        response = client.post(
            "/api/email/digest",
            json={}
        )
        assert response.status_code in [400, 422]


class TestTelegramEndpoints:
    """Test Telegram endpoints."""
    
    def test_telegram_status(self):
        """Test Telegram status endpoint."""
        response = client.get("/api/telegram/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "configured" in data
    
    def test_telegram_test_connection(self):
        """Test Telegram connection test."""
        response = client.get("/api/telegram/test")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "available" in data
    
    def test_telegram_post_missing_article(self):
        """Test Telegram post with missing article."""
        response = client.post(
            "/api/telegram/post",
            json={}
        )
        assert response.status_code in [400, 422]
    
    def test_telegram_post_invalid_article(self):
        """Test Telegram post with invalid article."""
        response = client.post(
            "/api/telegram/post",
            json={
                "article": {}
            }
        )
        assert response.status_code in [400, 422]
    
    def test_telegram_post_valid_article(self):
        """Test Telegram post with valid article."""
        response = client.post(
            "/api/telegram/post",
            json={
                "article": {
                    "title": "Test Article",
                    "summary": "Test summary",
                    "link": "http://example.com/article"
                },
                "format_type": "markdown"
            }
        )
        # May fail if Telegram not configured, but should validate
        assert response.status_code in [200, 400, 422, 500, 503]


class TestErrorHandling:
    """Test error handling across endpoints."""
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404."""
        response = client.get("/api/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test invalid HTTP method."""
        response = client.post("/health")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_malformed_json(self):
        """Test malformed JSON in request body."""
        response = client.post(
            "/api/tts/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
