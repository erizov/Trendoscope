"""
Rutube video processing module.
Downloads only audio (no video) for transcription.
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


def download_video_info(url: str) -> Dict:
    """
    Get video info without downloading.
    
    Args:
        url: Rutube video URL
        
    Returns:
        Video info dictionary
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If info fetch fails
    """
    if not validate_rutube_url(url):
        raise ValueError(f"Invalid Rutube URL: {url}")
    
    info_cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        "--quiet",
        url
    ]
    
    try:
        logger.info(f"Fetching video info from: {url}")
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60  # 1 minute for info
        )
        
        import json
        video_info = json.loads(info_result.stdout)
        return video_info
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Video info fetch timed out after 1 minute")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        raise RuntimeError(f"Failed to fetch video info: {error_msg}")
    except FileNotFoundError:
        raise RuntimeError(
            "yt-dlp not found. Please install it: pip install yt-dlp"
        )


def download_audio_direct(url: str, output_dir: Optional[Path] = None) -> Path:
    """
    Download and extract audio directly from Rutube using yt-dlp.
    This is much faster than downloading full video first.
    
    Args:
        url: Rutube video URL
        output_dir: Directory to save audio (creates temp if None)
        
    Returns:
        Path to audio file (WAV format)
        
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
    
    audio_path = output_dir / "audio.%(ext)s"
    
    # Use yt-dlp to extract audio directly (no video download)
    # -x extracts audio only, --no-video ensures no video streams
    cmd = [
        "yt-dlp",
        "-x",  # Extract audio only (no video)
        "--no-video",  # Explicitly skip video streams
        "--audio-format", "wav",  # WAV format
        "--audio-quality", "0",  # Best quality
        "-o", str(audio_path),
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        url
    ]
    
    try:
        logger.info(f"Downloading audio directly from: {url}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=900  # 15 minute timeout (for long videos)
        )
        
        # Find the actual audio file (yt-dlp may add extension)
        audio_files = list(output_dir.glob("audio.*"))
        if not audio_files:
            raise RuntimeError("Audio file was not created")
        
        actual_audio_path = audio_files[0]
        
        # Convert to 16kHz mono if needed (for Whisper)
        # Check if conversion is needed
        final_audio_path = output_dir / "audio_processed.wav"
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", str(actual_audio_path),
            "-ar", "16000",  # 16kHz sample rate (Whisper standard)
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(final_audio_path)
        ]
        
        logger.info(f"Converting audio to Whisper format: {actual_audio_path}")
        subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=300  # 5 minutes for conversion
        )
        
        if not final_audio_path.exists():
            # If conversion fails, use original
            logger.warning("Audio conversion failed, using original")
            final_audio_path = actual_audio_path
        
        logger.info(
            f"Audio downloaded: {final_audio_path}, "
            f"size: {final_audio_path.stat().st_size} bytes"
        )
        return final_audio_path
        
    except subprocess.TimeoutExpired:
        raise TimeoutError("Audio download timed out after 15 minutes")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        raise RuntimeError(f"Failed to download audio: {error_msg}")
    except FileNotFoundError:
        raise RuntimeError(
            "yt-dlp or ffmpeg not found. Please install:\n"
            "pip install yt-dlp\n"
            "ffmpeg: https://ffmpeg.org/download.html"
        )


def process_rutube_video(url: str) -> Tuple[Path, Path, Dict]:
    """
    Download video info and extract audio directly.
    Optimized to extract audio directly without downloading full video.
    
    Args:
        url: Rutube video URL
        
    Returns:
        Tuple of (video_path (dummy), audio_path, video_info)
        Note: video_path is a dummy path for compatibility
        
    Raises:
        ValueError: If URL is invalid
        TimeoutError: If processing times out
        RuntimeError: If processing fails
    """
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="rutube_"))
    
    try:
        # Get video info (fast, doesn't download video)
        video_info = download_video_info(url)
        
        # Download audio directly (much faster than full video)
        audio_path = download_audio_direct(url, temp_dir)
        
        # Create dummy video path for compatibility
        video_path = temp_dir / "video.mp4"
        
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

