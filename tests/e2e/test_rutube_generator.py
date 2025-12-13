"""
E2E test for Rutube video to text generator.
Tests the complete flow: video download -> transcription -> text generation.
"""
import pytest
import sys
import os
import subprocess
import shutil
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import httpx
from typing import Dict, Any


# Test configuration
RUTUBE_URL = "https://rutube.ru/video/ec56b2172a1743077d951c79ac46eee6/"
API_URL = "http://localhost:8003"
TIMEOUT = 600  # 10 minutes for video processing


def check_dependency(command: str, package_name: str = None) -> bool:
    """Check if a command-line tool is available."""
    # First check if command exists in PATH
    cmd_path = shutil.which(command)
    if cmd_path is None:
        return False
    # Then verify it actually works
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False
        )
        # On Windows, some commands return non-zero but still work
        # Check if we got any output as a sign it works
        if result.returncode == 0:
            return True
        # If exit code is non-zero but we got output, it might still work
        if result.stdout or result.stderr:
            return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def install_python_package(package: str) -> bool:
    """Install a Python package using pip."""
    try:
        print(f"Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✓ {package} installed successfully")
            return True
        else:
            print(f"✗ Failed to install {package}: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error installing {package}: {e}")
        return False


def check_and_install_dependencies():
    """Check and install all required dependencies."""
    print("=" * 80)
    print("Checking Dependencies")
    print("=" * 80)
    
    dependencies_ok = True
    
    # Check Python packages
    python_packages = {
        "yt-dlp": "yt-dlp",
        "openai-whisper": "openai-whisper",
    }
    
    for import_name, package_name in python_packages.items():
        try:
            __import__(import_name.replace("-", "_"))
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            if not install_python_package(package_name):
                dependencies_ok = False
    
    # Check system tools
    system_tools = {
        "ffmpeg": "ffmpeg",
        "yt-dlp": "yt-dlp",
    }
    
    for tool_name, command in system_tools.items():
        if check_dependency(command):
            print(f"✓ {tool_name} is available")
        else:
            print(f"✗ {tool_name} is NOT available")
            if tool_name == "ffmpeg":
                print(
                    "\n⚠ ffmpeg must be installed manually:\n"
                    "  Windows: Download from https://ffmpeg.org/download.html\n"
                    "  Linux: sudo apt-get install ffmpeg\n"
                    "  macOS: brew install ffmpeg\n"
                )
                dependencies_ok = False
    
    print("=" * 80)
    return dependencies_ok


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    print(f"Waiting for server at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(f"{url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✓ Server is ready")
                return True
        except Exception:
            pass
        time.sleep(2)
    
    print("✗ Server is not responding")
    return False


@pytest.fixture(scope="module")
def api_client():
    """Create HTTP client for API calls."""
    return httpx.Client(base_url=API_URL, timeout=TIMEOUT)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    print("\n" + "=" * 80)
    print("Rutube Video to Text Generator - E2E Test")
    print("=" * 80)
    
    # Check dependencies
    if not check_and_install_dependencies():
        pytest.skip("Required dependencies are missing")
    
    # Wait for server
    if not wait_for_server(API_URL):
        pytest.skip("Server is not available")
    
    yield
    
    print("\n" + "=" * 80)
    print("E2E Test Complete")
    print("=" * 80)


class TestRutubeGenerator:
    """Test suite for Rutube video to text generator."""
    
    def test_process_rutube_video(self, api_client):
        """Test processing a Rutube video end-to-end."""
        print("\n" + "-" * 80)
        print("Test: Process Rutube Video")
        print("-" * 80)
        print(f"URL: {RUTUBE_URL}")
        
        # Make API call
        print("\nSending request to API...")
        start_time = time.time()
        
        try:
            response = api_client.post(
                "/api/rutube/generate",
                json={"url": RUTUBE_URL},
                timeout=TIMEOUT
            )
            
            elapsed_time = time.time() - start_time
            print(f"Response received in {elapsed_time:.2f} seconds")
            
            # Check response
            assert response.status_code == 200, \
                f"API returned {response.status_code}: {response.text}"
            
            data = response.json()
            assert data.get("success") is True, "API returned success=false"
            
            # Validate response structure
            assert "video_info" in data, "Missing video_info"
            assert "transcript" in data, "Missing transcript"
            assert "generated_text" in data, "Missing generated_text"
            assert "language" in data, "Missing language"
            
            # Validate video info
            video_info = data["video_info"]
            assert "title" in video_info, "Missing video title"
            assert "url" in video_info, "Missing video URL"
            
            print(f"\n✓ Video Title: {video_info.get('title', 'N/A')}")
            print(f"✓ Duration: {video_info.get('duration', 0)} seconds")
            print(f"✓ Views: {video_info.get('view_count', 0)}")
            print(f"✓ Language: {data.get('language', 'N/A')}")
            print(f"✓ Transcript Length: {len(data.get('transcript', ''))} characters")
            
            # Validate transcript
            transcript = data.get("transcript", "")
            assert len(transcript) > 0, "Transcript is empty"
            print(f"\n✓ Transcript Preview (first 200 chars):")
            print(f"  {transcript[:200]}...")
            
            # Validate generated text
            generated = data.get("generated_text", {})
            assert "title" in generated, "Missing generated title"
            assert "text" in generated, "Missing generated text"
            
            print(f"\n✓ Generated Article Title: {generated.get('title', 'N/A')}")
            print(f"✓ Generated Text Length: {len(generated.get('text', ''))} characters")
            
            # Save to file
            output_file = project_root / "test_results" / "rutube_output.txt"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("Rutube Video to Text Generator - Output\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Video URL: {RUTUBE_URL}\n")
                f.write(f"Video Title: {video_info.get('title', 'N/A')}\n")
                f.write(f"Duration: {video_info.get('duration', 0)} seconds\n")
                f.write(f"Views: {video_info.get('view_count', 0)}\n")
                f.write(f"Language: {data.get('language', 'N/A')}\n")
                f.write(f"Processing Time: {elapsed_time:.2f} seconds\n")
                f.write("\n" + "=" * 80 + "\n")
                f.write("TRANSCRIPT\n")
                f.write("=" * 80 + "\n\n")
                f.write(transcript)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("GENERATED ARTICLE\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Title: {generated.get('title', 'N/A')}\n\n")
                f.write(generated.get('text', ''))
                f.write("\n\n")
                if generated.get('tags'):
                    f.write(f"Tags: {', '.join(generated.get('tags', []))}\n")
            
            print(f"\n✓ Output saved to: {output_file}")
            
            # Print to terminal
            print("\n" + "=" * 80)
            print("TRANSCRIPT")
            print("=" * 80)
            print(transcript)
            print("\n" + "=" * 80)
            print("GENERATED ARTICLE")
            print("=" * 80)
            print(f"Title: {generated.get('title', 'N/A')}\n")
            print(generated.get('text', ''))
            if generated.get('tags'):
                print(f"\nTags: {', '.join(generated.get('tags', []))}")
            
            return data
            
        except httpx.TimeoutException:
            pytest.fail(f"Request timed out after {TIMEOUT} seconds")
        except Exception as e:
            pytest.fail(f"Test failed with error: {e}")
    
    def test_invalid_url(self, api_client):
        """Test with invalid URL."""
        print("\n" + "-" * 80)
        print("Test: Invalid URL Handling")
        print("-" * 80)
        
        invalid_url = "https://invalid-url.com/video/123"
        
        response = api_client.post(
            "/api/rutube/generate",
            json={"url": invalid_url},
            timeout=30
        )
        
        assert response.status_code == 400, \
            f"Expected 400 for invalid URL, got {response.status_code}"
        
        print("✓ Invalid URL correctly rejected")


if __name__ == "__main__":
    """Run tests directly."""
    # Check dependencies first
    if not check_and_install_dependencies():
        print("\n❌ Dependencies check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Wait for server
    if not wait_for_server(API_URL):
        print("\n❌ Server is not available. Please start the server first:")
        print("   python run.py")
        sys.exit(1)
    
    # Run tests
    pytest.main([__file__, "-v", "-s"])

