"""
Rutube video processing module.
Downloads video and extracts audio for transcription.
"""
import os
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def validate_rutube_url(url: str) -> bool:
    """Validate Rutube URL format."""
    return "rutube.ru" in url.lower() and "/video/" in url.lower()


def download_video(url: str, output_dir: Optional[Path] = None) -> Tuple[Path, Dict]:
    """
    Download video from Rutube.
    
    Args:
        url: Rutube video URL
        output_dir: Directory to save video (creates temp if None)
        
    Returns:
        Tuple of (video_path, video_info)
        
    Raises:
        ValueError: If URL is invalid
        TimeoutError: If download times out
        RuntimeError: If download fails
    """
    if not validate_rutube_url(url):
        raise ValueError(f"Invalid Rutube URL: {url}")
    
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp())
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download video
    video_path = output_dir / "video.mp4"
    
    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",  # Best quality MP4
        "-o", str(video_path),
        "--no-playlist",
        "--quiet",  # Less verbose output
        url
    ]
    
    try:
        logger.info(f"Downloading video from: {url}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout
        )
        
        if not video_path.exists():
            raise RuntimeError("Video file was not created")
        
        # Extract video info
        info_cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            url
        ]
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        import json
        video_info = json.loads(info_result.stdout)
        
        logger.info(f"Video downloaded: {video_path}, size: {video_path.stat().st_size} bytes")
        return video_path, video_info
        
    except subprocess.TimeoutExpired:
        raise TimeoutError("Video download timed out after 5 minutes")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        raise RuntimeError(f"Failed to download video: {error_msg}")
    except FileNotFoundError:
        raise RuntimeError(
            "yt-dlp not found. Please install it: pip install yt-dlp"
        )


def extract_audio(video_path: Path, output_dir: Optional[Path] = None) -> Path:
    """
    Extract audio from video using ffmpeg.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save audio (uses video dir if None)
        
    Returns:
        Path to audio file (WAV format)
        
    Raises:
        TimeoutError: If extraction times out
        RuntimeError: If extraction fails or ffmpeg not found
    """
    if output_dir is None:
        output_dir = video_path.parent
    
    audio_path = output_dir / "audio.wav"
    
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",  # 16kHz sample rate (Whisper standard)
        "-ac", "1",  # Mono
        "-y",  # Overwrite
        str(audio_path)
    ]
    
    try:
        logger.info(f"Extracting audio from: {video_path}")
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=120,
            stderr=subprocess.DEVNULL  # Suppress ffmpeg verbose output
        )
        
        if not audio_path.exists():
            raise RuntimeError("Audio file was not created")
        
        logger.info(f"Audio extracted: {audio_path}, size: {audio_path.stat().st_size} bytes")
        return audio_path
        
    except subprocess.TimeoutExpired:
        raise TimeoutError("Audio extraction timed out after 2 minutes")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract audio: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg:\n"
            "Windows: Download from https://ffmpeg.org/download.html\n"
            "Linux: apt-get install ffmpeg\n"
            "macOS: brew install ffmpeg"
        )


def process_rutube_video(url: str) -> Tuple[Path, Path, Dict]:
    """
    Download video and extract audio.
    
    Args:
        url: Rutube video URL
        
    Returns:
        Tuple of (video_path, audio_path, video_info)
        
    Raises:
        ValueError: If URL is invalid
        TimeoutError: If processing times out
        RuntimeError: If processing fails
    """
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="rutube_"))
    
    try:
        # Download video
        video_path, video_info = download_video(url, temp_dir)
        
        # Extract audio
        audio_path = extract_audio(video_path, temp_dir)
        
        return video_path, audio_path, video_info
        
    except Exception as e:
        # Cleanup on error
        import shutil
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
        raise

