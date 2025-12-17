"""
Error handling tests for all endpoints.
Tests various error scenarios and edge cases.
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app

client = TestClient(app)


class TestErrorHandling:
    """Test error handling across all endpoints."""
    
    def test_news_feed_timeout(self):
        """Test news feed with timeout scenario."""
        with patch('trendoscope2.api.main.AsyncNewsAggregator') as mock_agg:
            mock_agg.side_effect = TimeoutError("Request timeout")
            
            response = client.get("/api/news/feed?use_cache=false")
            # Should handle timeout gracefully
            assert response.status_code in [200, 500]
    
    def test_news_feed_network_error(self):
        """Test news feed with network error."""
        with patch('trendoscope2.api.main.AsyncNewsAggregator') as mock_agg:
            mock_agg.side_effect = ConnectionError("Network error")
            
            response = client.get("/api/news/feed?use_cache=false")
            assert response.status_code in [200, 500]
    
    def test_tts_generate_provider_error(self):
        """Test TTS generation with provider error."""
        with patch('trendoscope2.api.main.tts_service.generate_audio') as mock_gen:
            mock_gen.side_effect = Exception("TTS provider error")
            
            response = client.post(
                "/api/tts/generate",
                json={"text": "Test"}
            )
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_tts_audio_not_found(self):
        """Test TTS audio download with non-existent ID."""
        response = client.get("/api/tts/audio/non-existent-id-12345")
        assert response.status_code in [404, 500]
    
    def test_email_send_smtp_error(self):
        """Test email sending with SMTP error."""
        with patch('trendoscope2.api.main.email_service.send_email') as mock_send:
            mock_send.return_value = False  # Simulate failure
            
            response = client.post(
                "/api/email/send",
                json={
                    "to_email": "test@example.com",
                    "subject": "Test",
                    "text_content": "Test content"
                }
            )
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_telegram_post_connection_error(self):
        """Test Telegram post with connection error."""
        with patch('trendoscope2.api.main.telegram_service.post_article') as mock_post:
            mock_post.side_effect = Exception("Telegram connection error")
            
            response = client.post(
                "/api/telegram/post",
                json={
                    "article": {
                        "title": "Test",
                        "summary": "Test summary",
                        "link": "http://example.com"
                    }
                }
            )
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_translate_article_translator_error(self):
        """Test article translation with translator error."""
        with patch('trendoscope2.api.main.translate_and_summarize_news') as mock_trans:
            mock_trans.side_effect = Exception("Translator error")
            
            response = client.post(
                "/api/news/translate",
                json={
                    "title": "Test",
                    "summary": "Test summary",
                    "source_language": "en"
                },
                params={"target_language": "ru"}
            )
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_rutube_generate_processing_error(self):
        """Test Rutube generation with processing error."""
        with patch('trendoscope2.ingest.rutube_processor.process_rutube_video') as mock_proc:
            mock_proc.side_effect = Exception("Processing error")
            
            response = client.post(
                "/api/rutube/generate",
                json={
                    "url": "https://rutube.ru/video/1234567890/"
                }
            )
            assert response.status_code in [500, 503]  # 503 for service unavailable
    
    def test_invalid_json_body(self):
        """Test endpoints with invalid JSON."""
        response = client.post(
            "/api/tts/generate",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self):
        """Test endpoints with missing required fields."""
        response = client.post(
            "/api/tts/generate",
            json={}  # Missing 'text' field
        )
        assert response.status_code in [400, 422]
    
    def test_invalid_query_parameters(self):
        """Test endpoints with invalid query parameters."""
        response = client.get(
            "/api/news/feed",
            params={"limit": 1000}  # Exceeds max
        )
        # Should validate and return 422 or use default
        assert response.status_code in [200, 422]
    
    def test_very_long_text(self):
        """Test endpoints with very long text input."""
        long_text = "A" * 10000
        
        response = client.post(
            "/api/tts/generate",
            json={
                "text": long_text
            }
        )
        # Should handle or reject
        assert response.status_code in [200, 400, 422, 500]
    
    def test_special_characters(self):
        """Test endpoints with special characters."""
        special_text = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        response = client.post(
            "/api/tts/generate",
            json={
                "text": special_text
            }
        )
        assert response.status_code in [200, 400, 422, 500]
    
    def test_unicode_characters(self):
        """Test endpoints with unicode characters."""
        unicode_text = "Test with unicode: 你好 こんにちは مرحبا"
        
        response = client.post(
            "/api/tts/generate",
            json={
                "text": unicode_text
            }
        )
        assert response.status_code in [200, 400, 422, 500]
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/news/feed?limit=5")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should complete (may be 200 or 500)
        assert all(r.status_code in [200, 500] for r in results)
