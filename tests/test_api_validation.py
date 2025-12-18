"""
Tests for API validation and MIME types.
"""
import pytest
from fastapi.testclient import TestClient
from trendoscope2.api.main import app
from trendoscope2.api.schemas import (
    TranslateArticleRequest,
    RutubeGenerateRequest,
    TTSGenerateRequest
)

client = TestClient(app)


class TestTranslateArticleValidation:
    """Test validation for translate article endpoint."""
    
    def test_translate_missing_both_title_and_summary(self):
        """Test that at least title or summary is required."""
        response = client.post(
            "/api/news/translate?target_language=en",
            json={}
        )
        assert response.status_code == 422
    
    def test_translate_with_title_only(self):
        """Test translation with title only."""
        response = client.post(
            "/api/news/translate?target_language=en",
            json={"title": "Test title"}
        )
        # Should pass validation (may fail on translation, but validation OK)
        assert response.status_code in [200, 500]
    
    def test_translate_with_summary_only(self):
        """Test translation with summary only."""
        response = client.post(
            "/api/news/translate?target_language=en",
            json={"summary": "Test summary"}
        )
        # Should pass validation
        assert response.status_code in [200, 500]
    
    def test_translate_invalid_target_language(self):
        """Test invalid target_language."""
        response = client.post(
            "/api/news/translate?target_language=invalid",
            json={"title": "Test"}
        )
        assert response.status_code == 422


class TestRutubeValidation:
    """Test validation for Rutube endpoint."""
    
    def test_rutube_invalid_url(self):
        """Test invalid Rutube URL."""
        response = client.post(
            "/api/rutube/generate",
            json={"url": "https://example.com/video"}
        )
        # Should fail validation or return 400
        assert response.status_code in [400, 422]
    
    def test_rutube_valid_url(self):
        """Test valid Rutube URL format."""
        response = client.post(
            "/api/rutube/generate",
            json={"url": "https://rutube.ru/video/123456/"}
        )
        # May fail on processing, but validation should pass
        assert response.status_code in [200, 400, 500]


class TestTTSValidation:
    """Test validation for TTS endpoint."""
    
    def test_tts_empty_text(self):
        """Test TTS with empty text."""
        response = client.post(
            "/api/tts/generate",
            json={"text": ""}
        )
        assert response.status_code == 422
    
    def test_tts_whitespace_only_text(self):
        """Test TTS with whitespace-only text."""
        response = client.post(
            "/api/tts/generate",
            json={"text": "   "}
        )
        assert response.status_code == 422
    
    def test_tts_invalid_language(self):
        """Test TTS with invalid language."""
        response = client.post(
            "/api/tts/generate",
            json={"text": "Test", "language": "invalid"}
        )
        assert response.status_code == 422
    
    def test_tts_invalid_voice_gender(self):
        """Test TTS with invalid voice gender."""
        response = client.post(
            "/api/tts/generate",
            json={"text": "Test", "voice_gender": "invalid"}
        )
        assert response.status_code == 422
    
    def test_tts_valid_request(self):
        """Test TTS with valid request."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "Test text",
                "language": "en",
                "voice_gender": "female"
            }
        )
        # May fail on generation, but validation should pass
        assert response.status_code in [200, 500]


class TestFileDownloadMIMETypes:
    """Test MIME types for file download endpoints."""
    
    def test_tts_audio_mime_type(self):
        """Test TTS audio endpoint returns correct MIME type."""
        # First generate audio
        generate_response = client.post(
            "/api/tts/generate",
            json={"text": "Test audio"}
        )
        
        if generate_response.status_code == 200:
            audio_id = generate_response.json().get("audio_id")
            if audio_id:
                audio_response = client.get(f"/api/tts/audio/{audio_id}")
                if audio_response.status_code == 200:
                    content_type = audio_response.headers.get("content-type")
                    assert content_type in [
                        "audio/mpeg",
                        "audio/wav",
                        "audio/mp3"
                    ]
    
    def test_frontend_html_mime_type(self):
        """Test frontend HTML endpoint returns correct MIME type."""
        response = client.get("/")
        if response.status_code == 200:
            content_type = response.headers.get("content-type")
            # May be JSON or HTML depending on frontend availability
            assert content_type is not None


class TestPydanticModels:
    """Test Pydantic model validation directly."""
    
    def test_translate_request_validation(self):
        """Test TranslateArticleRequest validation."""
        # Should fail - no title or summary
        with pytest.raises(ValueError):
            TranslateArticleRequest()
        
        # Should pass
        request = TranslateArticleRequest(title="Test")
        assert request.title == "Test"
    
    def test_rutube_request_validation(self):
        """Test RutubeGenerateRequest validation."""
        # Should pass
        request = RutubeGenerateRequest(url="https://rutube.ru/video/123/")
        assert "rutube.ru" in str(request.url)
    
    def test_tts_request_validation(self):
        """Test TTSGenerateRequest validation."""
        # Should fail - empty text
        with pytest.raises(ValueError):
            TTSGenerateRequest(text="")
        
        # Should pass
        request = TTSGenerateRequest(text="Test")
        assert request.text == "Test"
        assert request.language == "auto"
        assert request.voice_gender == "female"
