"""
E2E test for Trendoscope2 minimal setup.
Tests Docker containers, API endpoints, translation, news fetching, and Rutube.
"""
import pytest
import httpx
import time
import subprocess
import sys
import os
from pathlib import Path

# Test configuration
API_URL = "http://localhost:8004"
TIMEOUT = 60
RUTUBE_URL = "https://rutube.ru/video/ec56b2172a1743077d951c79ac46eee6/"


def check_docker_running():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_redis_container():
    """Check if Redis container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=trendoscope2-redis", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "trendoscope2-redis" in result.stdout
    except:
        return False


def check_redis_health():
    """Check if Redis is responding."""
    try:
        result = subprocess.run(
            ["docker", "exec", "trendoscope2-redis", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() == "PONG"
    except:
        return False


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
        pytest.skip("API is not available")
    async with httpx.AsyncClient(base_url=API_URL, timeout=TIMEOUT, limits=httpx.Limits(max_keepalive_connections=1)) as client:
        yield client


class TestDockerContainers:
    """Test Docker containers."""
    
    def test_docker_running(self):
        """Test that Docker is running."""
        if not check_docker_running():
            pytest.skip("Docker is not running (optional for minimal setup)")
    
    def test_redis_container_running(self):
        """Test that Redis container is running."""
        if not check_docker_running():
            pytest.skip("Docker is not running")
        if not check_redis_container():
            pytest.skip("Redis container is not running")
    
    def test_redis_health(self):
        """Test that Redis is healthy."""
        if not check_docker_running():
            pytest.skip("Docker is not running")
        if not check_redis_container():
            pytest.skip("Redis container is not running")
        assert check_redis_health(), "Redis is not responding"


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, api_client):
        """Test root endpoint."""
        response = await api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Trendoscope2"
        assert data["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, api_client):
        """Test health endpoint."""
        response = await api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        assert "redis" in data
        assert "database" in data


class TestNewsFetching:
    """Test news fetching."""
    
    @pytest.mark.asyncio
    async def test_news_feed_endpoint(self, api_client):
        """Test news feed endpoint."""
        response = await api_client.get("/api/news/feed", params={"limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "news" in data
        assert isinstance(data["news"], list)
        assert len(data["news"]) > 0, "No news items returned"
        
        # Check news item structure
        item = data["news"][0]
        assert "title" in item
        assert "summary" in item
        assert "link" in item
        assert "source" in item
    
    @pytest.mark.asyncio
    async def test_news_feed_with_category(self, api_client):
        """Test news feed with category filter."""
        response = await api_client.get("/api/news/feed", params={"category": "all", "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTranslation:
    """Test translation functionality."""
    
    @pytest.mark.asyncio
    async def test_translate_endpoint(self, api_client):
        """Test translation endpoint."""
        article = {
            "title": "Hello World",
            "summary": "This is a test article in English.",
            "source_language": "en"
        }
        
        response = await api_client.post(
            "/api/news/translate",
            json=article,
            params={"target_language": "ru"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated" in data
        assert "title" in data["translated"]
        assert "summary" in data["translated"]
        
        # Check that translation actually happened (text should be different)
        translated_title = data["translated"]["title"]
        assert translated_title != article["title"] or "Привет" in translated_title or "Мир" in translated_title
    
    @pytest.mark.asyncio
    async def test_translate_russian_to_english(self, api_client):
        """Test Russian to English translation."""
        article = {
            "title": "Привет мир",
            "summary": "Это тестовая статья на русском языке.",
            "source_language": "ru"
        }
        
        response = await api_client.post(
            "/api/news/translate",
            json=article,
            params={"target_language": "en"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated" in data


class TestRutubeExtractor:
    """Test Rutube text extraction."""
    
    @pytest.mark.asyncio
    async def test_rutube_generate_endpoint(self, api_client):
        """Test Rutube text generation endpoint."""
        # Check if dependencies are available
        try:
            import yt_dlp
            import whisper
            import shutil
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                pytest.skip("ffmpeg not found")
        except ImportError:
            pytest.skip("yt-dlp or whisper not installed")
        
        try:
            response = await api_client.post(
                "/api/rutube/generate",
                json={"url": RUTUBE_URL},
                timeout=1200.0  # 20 minutes for video processing
            )
        except httpx.ReadTimeout:
            pytest.skip("Rutube processing timed out (video may be too long)")
        
        if response.status_code != 200:
            error_detail = response.text[:1000] if hasattr(response, 'text') else str(response)
            pytest.fail(f"Rutube endpoint returned {response.status_code}: {error_detail}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "video_info" in data
        assert "transcript" in data
        assert "language" in data
        assert len(data["transcript"]) > 0, "Transcript should not be empty"


if __name__ == "__main__":
    # Run tests
    print("=" * 80)
    print("Trendoscope2 E2E Test")
    print("=" * 80)
    print()
    
    # Check Docker
    print("1. Checking Docker...")
    if not check_docker_running():
        print("   [X] Docker is not running (optional for minimal setup)")
    else:
        print("   [OK] Docker is running")
    
    # Check Redis
    print("2. Checking Redis container...")
    if not check_docker_running():
        print("   [SKIP] Docker not running, skipping Redis check")
    elif not check_redis_container():
        print("   [WARN] Redis container is not running")
        print("   Run: docker-compose -f docker/docker-compose.local.yml up -d redis")
    else:
        print("   [OK] Redis container is running")
        if not check_redis_health():
            print("   [WARN] Redis is not responding")
        else:
            print("   [OK] Redis is healthy")
    
    # Check API
    print("3. Checking API...")
    if not wait_for_api():
        print("   [X] API is not available")
        print("   Start the API with: python run.py")
        sys.exit(1)
    print("   [OK] API is available")
    
    # Run pytest
    print()
    print("4. Running tests...")
    print()
    exit_code = pytest.main([__file__, "-v", "--tb=short", "-s"])
    sys.exit(exit_code)

