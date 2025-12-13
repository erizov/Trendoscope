"""
Standalone script to run Rutube E2E test with full installation and output.
"""
import sys
import subprocess
import shutil
import time
import httpx
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configuration
RUTUBE_URL = "https://rutube.ru/video/ec56b2172a1743077d951c79ac46eee6/"
API_URL = "http://localhost:8003"
TIMEOUT = 600  # 10 minutes


def check_dependency(command: str) -> bool:
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
            print(f"✗ Failed to install {package}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error installing {package}: {e}")
        return False


def check_and_install_dependencies():
    """Check and install all required dependencies."""
    print("=" * 80)
    print("Checking and Installing Dependencies")
    print("=" * 80)
    
    all_ok = True
    
    # Check Python packages
    packages = {
        "yt_dlp": "yt-dlp",
        "whisper": "openai-whisper",
    }
    
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            if not install_python_package(package_name):
                all_ok = False
    
    # Check system tools
    if check_dependency("ffmpeg"):
        print("✓ ffmpeg is available")
    else:
        print("✗ ffmpeg is NOT available")
        print(
            "\n⚠ ffmpeg must be installed manually:\n"
            "  Windows: Download from https://ffmpeg.org/download.html\n"
            "  Linux: sudo apt-get install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
        )
        all_ok = False
    
    if check_dependency("yt-dlp"):
        print("✓ yt-dlp command is available")
    else:
        print("✗ yt-dlp command is NOT available")
        all_ok = False
    
    print("=" * 80)
    return all_ok


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    print(f"\nWaiting for server at {url}...")
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
        print(".", end="", flush=True)
    
    print("\n✗ Server is not responding")
    return False


def process_video():
    """Process the Rutube video and get text output."""
    print("\n" + "=" * 80)
    print("Processing Rutube Video")
    print("=" * 80)
    print(f"URL: {RUTUBE_URL}\n")
    
    client = httpx.Client(base_url=API_URL, timeout=TIMEOUT)
    
    try:
        print("Sending request to API...")
        print("(This may take 2-5 minutes depending on video length)")
        start_time = time.time()
        
        response = client.post(
            "/api/rutube/generate",
            json={"url": RUTUBE_URL},
            timeout=TIMEOUT
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"\n✗ API Error: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        
        if not data.get("success"):
            print(f"\n✗ API returned success=false")
            print(data.get("detail", "Unknown error"))
            return None
        
        print(f"\n✓ Processing completed in {elapsed_time:.2f} seconds")
        
        # Extract data
        video_info = data.get("video_info", {})
        transcript = data.get("transcript", "")
        generated = data.get("generated_text", {})
        language = data.get("language", "unknown")
        
        # Print summary
        print("\n" + "-" * 80)
        print("Video Information")
        print("-" * 80)
        print(f"Title: {video_info.get('title', 'N/A')}")
        print(f"Duration: {video_info.get('duration', 0)} seconds")
        print(f"Views: {video_info.get('view_count', 0)}")
        print(f"Language: {language}")
        print(f"Transcript Length: {len(transcript)} characters")
        
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
            f.write(f"Language: {language}\n")
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
        print(f"\n✗ Request timed out after {TIMEOUT} seconds")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        client.close()


def main():
    """Main function."""
    print("=" * 80)
    print("Rutube Video to Text Generator - E2E Test")
    print("=" * 80)
    
    # Check dependencies
    if not check_and_install_dependencies():
        print("\n❌ Dependencies check failed.")
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Wait for server
    if not wait_for_server(API_URL):
        print("\n❌ Server is not available.")
        print("Please start the server first:")
        print("  python run.py")
        print("\nOr use the start script:")
        print("  start.bat (Windows)")
        sys.exit(1)
    
    # Process video
    result = process_video()
    
    if result:
        print("\n" + "=" * 80)
        print("✓ E2E Test Completed Successfully")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("✗ E2E Test Failed")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()

