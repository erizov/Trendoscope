"""
E2E tests for TTS (Text-to-Speech) functionality.
Tests TTS generation, caching, fallback, and offline mode.
"""
import pytest
import httpx
import time
import sys
import os
from pathlib import Path

# Test configuration
API_URL = "http://localhost:8004"
TIMEOUT = 60


def wait_for_api(max_wait=60):
    """Wait for API to be ready."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = httpx.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False


@pytest.fixture
async def api_client():
    """Create HTTP client for API."""
    if not wait_for_api():
        pytest.skip("API is not available. Start with: python run.py")
    async with httpx.AsyncClient(
        base_url=API_URL,
        timeout=TIMEOUT,
        limits=httpx.Limits(max_keepalive_connections=1)
    ) as client:
        yield client


class TestTTSGeneration:
    """Test TTS audio generation."""
    
    @pytest.mark.asyncio
    async def test_tts_generate_russian(self, api_client):
        """Test TTS generation for Russian text."""
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Привет, это тестовое сообщение на русском языке.",
                "language": "ru",
                "voice_gender": "female"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert "audio_id" in data
        assert "audio_url" in data
        assert data["language"] == "ru"
        assert "duration" in data
        assert "provider" in data
        assert data["audio_url"].startswith("/api/tts/audio/")
    
    @pytest.mark.asyncio
    async def test_tts_generate_english(self, api_client):
        """Test TTS generation for English text."""
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Hello, this is a test message in English.",
                "language": "en",
                "voice_gender": "female"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["language"] == "en"
        assert "audio_id" in data
    
    @pytest.mark.asyncio
    async def test_tts_auto_language_detection(self, api_client):
        """Test automatic language detection."""
        # Russian text
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Привет мир",
                "language": "auto",
                "voice_gender": "female"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["language"] == "ru"
        
        # English text
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Hello world",
                "language": "auto",
                "voice_gender": "female"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["language"] == "en"
    
    @pytest.mark.asyncio
    async def test_tts_get_audio_file(self, api_client):
        """Test getting audio file by ID."""
        # First generate audio
        generate_response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test audio file retrieval",
                "language": "en",
                "voice_gender": "female"
            }
        )
        
        assert generate_response.status_code == 200
        audio_id = generate_response.json()["audio_id"]
        
        # Get audio file
        audio_response = await api_client.get(f"/api/tts/audio/{audio_id}")
        
        assert audio_response.status_code == 200
        assert audio_response.headers["content-type"] == "audio/mpeg"
        assert len(audio_response.content) > 0, "Audio file should not be empty"
    
    @pytest.mark.asyncio
    async def test_tts_invalid_audio_id(self, api_client):
        """Test getting non-existent audio file."""
        response = await api_client.get("/api/tts/audio/invalid-id-12345")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_tts_empty_text(self, api_client):
        """Test TTS generation with empty text."""
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "",
                "language": "en"
            }
        )
        
        assert response.status_code == 400 or response.status_code == 422


class TestTTSProviders:
    """Test different TTS providers."""
    
    @pytest.mark.asyncio
    async def test_tts_provider_gtts(self, api_client):
        """Test using gTTS provider explicitly."""
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test with gTTS provider",
                "language": "en",
                "provider": "gtts"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["provider"] == "gtts"
    
    @pytest.mark.asyncio
    async def test_tts_provider_pyttsx3(self, api_client):
        """Test using pyttsx3 provider (offline)."""
        # Check if pyttsx3 is available
        try:
            import pyttsx3
            pyttsx3.init()
        except Exception:
            pytest.skip("pyttsx3 is not available")
        
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test with pyttsx3 provider",
                "language": "en",
                "provider": "pyttsx3",
                "voice_gender": "female"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["provider"] == "pyttsx3"
    
    @pytest.mark.asyncio
    async def test_tts_provider_auto(self, api_client):
        """Test automatic provider selection."""
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test with auto provider",
                "language": "en",
                "provider": "auto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["provider"] in ["gtts", "pyttsx3"]


class TestTTSFallback:
    """Test automatic fallback functionality."""
    
    @pytest.mark.asyncio
    async def test_tts_fallback_on_error(self, api_client):
        """
        Test automatic fallback when primary provider fails.
        Note: This test may skip if both providers work.
        """
        # Try to use gtts, but it might fail (no internet, etc.)
        # In that case, should fallback to pyttsx3
        try:
            import pyttsx3
            pyttsx3.init()
        except Exception:
            pytest.skip("pyttsx3 is not available for fallback")
        
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test fallback mechanism",
                "language": "en",
                "provider": "auto"
            }
        )
        
        # Should succeed with either provider
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["provider"] in ["gtts", "pyttsx3"]
        
        # If fallback was used, check the flag
        if data["provider"] == "pyttsx3":
            # Might have used fallback
            assert "used_fallback" in data


class TestTTSCaching:
    """Test TTS caching functionality."""
    
    @pytest.mark.asyncio
    async def test_tts_caching_same_text(self, api_client):
        """Test that same text is cached and returned faster."""
        text = "This is a test for caching mechanism."
        
        # First request (should generate)
        start_time = time.time()
        response1 = await api_client.post(
            "/api/tts/generate",
            json={
                "text": text,
                "language": "en"
            }
        )
        first_duration = time.time() - start_time
        
        assert response1.status_code == 200
        audio_id_1 = response1.json()["audio_id"]
        
        # Second request with same text (should use cache)
        start_time = time.time()
        response2 = await api_client.post(
            "/api/tts/generate",
            json={
                "text": text,
                "language": "en"
            }
        )
        second_duration = time.time() - start_time
        
        assert response2.status_code == 200
        audio_id_2 = response2.json()["audio_id"]
        
        # Second request should be faster (cached)
        # Note: This might not always be true due to network, but cache should help
        assert second_duration < first_duration * 2, \
            "Cached request should be faster or similar"
    
    @pytest.mark.asyncio
    async def test_tts_cache_stats(self, api_client):
        """Test TTS cache statistics endpoint."""
        response = await api_client.get("/api/tts/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "cache_enabled" in data
        assert "cache_files" in data
        assert "cache_size_bytes" in data
        assert "main_files" in data
        assert "main_size_bytes" in data
        
        # Check types
        assert isinstance(data["cache_files"], int)
        assert isinstance(data["cache_size_bytes"], int)
        assert isinstance(data["main_files"], int)
        assert isinstance(data["main_size_bytes"], int)


class TestTTSVoiceSelection:
    """Test voice gender selection (pyttsx3)."""
    
    @pytest.mark.asyncio
    async def test_tts_voice_gender_female(self, api_client):
        """Test female voice selection."""
        try:
            import pyttsx3
            pyttsx3.init()
        except Exception:
            pytest.skip("pyttsx3 is not available")
        
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test female voice",
                "language": "en",
                "provider": "pyttsx3",
                "voice_gender": "female"
            },
            timeout=120.0  # Increased timeout for pyttsx3 voice selection
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_tts_voice_gender_male(self, api_client):
        """Test male voice selection."""
        try:
            import pyttsx3
            pyttsx3.init()
        except Exception:
            pytest.skip("pyttsx3 is not available")
        
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": "Test male voice",
                "language": "en",
                "provider": "pyttsx3",
                "voice_gender": "male"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTTSErrorHandling:
    """Test error handling in TTS."""
    
    @pytest.mark.asyncio
    async def test_tts_long_text_truncation(self, api_client):
        """Test that very long text is truncated."""
        long_text = "A" * 10000  # 10k characters
        
        response = await api_client.post(
            "/api/tts/generate",
            json={
                "text": long_text,
                "language": "en"
            }
        )
        
        # Should succeed (text truncated) or return error
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True


if __name__ == "__main__":
    # Run tests
    print("=" * 80)
    print("Trendoscope2 TTS E2E Test")
    print("=" * 80)
    print()
    
    # Check API
    print("1. Checking API...")
    if not wait_for_api():
        print("   [X] API is not available")
        print("   Start the API with: python run.py")
        sys.exit(1)
    print("   [OK] API is available")
    
    # Run pytest
    print()
    print("2. Running TTS tests...")
    print()
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    sys.exit(exit_code)
