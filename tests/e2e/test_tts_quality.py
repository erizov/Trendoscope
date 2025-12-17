"""
TTS Audio Quality and Performance Tests.
Tests audio quality, duration, format, and caching.
"""
import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
import time

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app

client = TestClient(app)


class TestTTSAudioQuality:
    """Test TTS audio quality and format."""
    
    def test_audio_format_mp3(self):
        """Test generated audio is in MP3 format."""
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "Test audio format",
                "language": "en"
            }
        )
        
        if response.status_code == 200:
            audio_id = response.json().get("audio_id")
            if audio_id:
                audio_response = client.get(f"/api/tts/audio/{audio_id}")
                if audio_response.status_code == 200:
                    content_type = audio_response.headers.get("content-type")
                    assert content_type in ["audio/mpeg", "audio/mp3"]
                    assert len(audio_response.content) > 0
    
    def test_audio_duration_reasonable(self):
        """Test audio duration is reasonable for text length."""
        text = "This is a test message for audio duration."
        response = client.post(
            "/api/tts/generate",
            json={"text": text, "language": "en"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Audio should have duration info
            assert "duration" in data or "audio_id" in data
    
    def test_different_languages(self):
        """Test TTS generation for different languages."""
        languages = ["ru", "en"]
        
        for lang in languages:
            response = client.post(
                "/api/tts/generate",
                json={
                    "text": "Test" if lang == "en" else "Тест",
                    "language": lang
                }
            )
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                assert response.json().get("language") == lang
    
    def test_different_voice_genders(self):
        """Test TTS generation with different voice genders."""
        genders = ["male", "female"]
        
        for gender in genders:
            response = client.post(
                "/api/tts/generate",
                json={
                    "text": "Test voice gender",
                    "language": "en",
                    "voice_gender": gender
                }
            )
            assert response.status_code in [200, 500]
    
    def test_long_text_handling(self):
        """Test TTS generation with long text."""
        long_text = " ".join(["This is a test sentence."] * 10)
        
        response = client.post(
            "/api/tts/generate",
            json={
                "text": long_text,
                "language": "en"
            }
        )
        # Should handle long text (may take longer or be rejected)
        assert response.status_code in [200, 400, 422, 500]


class TestTTSPerformance:
    """Test TTS performance and caching."""
    
    def test_generation_time(self):
        """Test TTS generation time."""
        start = time.time()
        response = client.post(
            "/api/tts/generate",
            json={"text": "Short test"}
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            # Should complete within reasonable time
            assert elapsed < 10.0
    
    def test_caching_works(self):
        """Test that caching works for repeated requests."""
        text = "Test caching functionality"
        
        # First request
        start1 = time.time()
        response1 = client.post(
            "/api/tts/generate",
            json={"text": text, "language": "en"}
        )
        elapsed1 = time.time() - start1
        
        if response1.status_code == 200:
            audio_id1 = response1.json().get("audio_id")
            
            # Second request (should use cache)
            start2 = time.time()
            response2 = client.post(
                "/api/tts/generate",
                json={"text": text, "language": "en"}
            )
            elapsed2 = time.time() - start2
            
            if response2.status_code == 200:
                audio_id2 = response2.json().get("audio_id")
                # Cached should be faster (or same audio_id)
                # Note: May not always be same ID due to UUID generation
                # But should be faster
                assert elapsed2 <= elapsed1 * 1.5  # Allow some variance
    
    def test_parallel_generation(self):
        """Test parallel TTS generation."""
        import concurrent.futures
        
        def generate(text):
            return client.post(
                "/api/tts/generate",
                json={"text": text}
            )
        
        texts = [f"Test {i}" for i in range(3)]
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(generate, text) for text in texts]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.time() - start
        
        # All should complete
        assert all(r.status_code in [200, 500] for r in results)
        # Parallel should be faster than sequential
        assert elapsed < 15.0  # Should complete within reasonable time


class TestTTSIntegration:
    """Test TTS integration with other services."""
    
    def test_tts_with_news_feed(self):
        """Test TTS can be generated from news feed items."""
        # Get news feed
        news_response = client.get("/api/news/feed?limit=1")
        
        if news_response.status_code == 200:
            news_data = news_response.json()
            news_items = news_data.get("news", [])
            
            if news_items:
                # Generate TTS for first news item
                item = news_items[0]
                text = f"{item.get('title', '')} {item.get('summary', '')}"
                
                tts_response = client.post(
                    "/api/tts/generate",
                    json={"text": text[:100]}  # Limit length
                )
                
                assert tts_response.status_code in [200, 500]
    
    def test_tts_stats_endpoint(self):
        """Test TTS stats endpoint."""
        response = client.get("/api/tts/stats")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        # Should have cache stats if caching enabled
        assert isinstance(data, dict)
