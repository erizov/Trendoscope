"""
Performance tests for Trendoscope2.
Tests response times and optimization.
"""
import pytest
import time
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app

client = TestClient(app)


class TestPerformance:
    """Test performance of endpoints."""
    
    def test_health_endpoint_speed(self):
        """Test health endpoint response time."""
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.1  # Should be very fast
    
    def test_tts_stats_speed(self):
        """Test TTS stats endpoint response time."""
        start = time.time()
        response = client.get("/api/tts/stats")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should be fast
    
    def test_email_status_speed(self):
        """Test email status endpoint response time."""
        start = time.time()
        response = client.get("/api/email/status")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should be fast
    
    def test_telegram_status_speed(self):
        """Test Telegram status endpoint response time."""
        start = time.time()
        response = client.get("/api/telegram/status")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should be fast
    
    def test_news_feed_cached_speed(self):
        """Test news feed with cache response time."""
        start = time.time()
        response = client.get("/api/news/feed?limit=10&use_cache=true")
        elapsed = time.time() - start
        
        # Cached should be fast
        if response.status_code == 200:
            assert elapsed < 2.0  # Cached should be under 2 seconds
    
    @pytest.mark.slow
    def test_news_feed_fresh_speed(self):
        """Test news feed without cache response time."""
        start = time.time()
        response = client.get("/api/news/feed?limit=5&use_cache=false")
        elapsed = time.time() - start
        
        # Fresh fetch may take longer
        if response.status_code == 200:
            assert elapsed < 30.0  # Should complete within 30 seconds
    
    def test_tts_generate_speed(self):
        """Test TTS generation response time."""
        start = time.time()
        response = client.post(
            "/api/tts/generate",
            json={"text": "Short test text"}
        )
        elapsed = time.time() - start
        
        # TTS generation may take time
        if response.status_code == 200:
            assert elapsed < 10.0  # Should complete within 10 seconds
    
    def test_multiple_requests_throughput(self):
        """Test throughput with multiple requests."""
        start = time.time()
        
        responses = []
        for _ in range(10):
            resp = client.get("/api/email/status")
            responses.append(resp)
        
        elapsed = time.time() - start
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        # Should handle 10 requests reasonably fast
        assert elapsed < 5.0
    
    def test_concurrent_status_checks(self):
        """Test concurrent status endpoint calls."""
        import concurrent.futures
        
        def check_status():
            return client.get("/api/email/status")
        
        start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(check_status) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start
        
        assert all(r.status_code == 200 for r in results)
        assert elapsed < 2.0  # Concurrent should still be fast
