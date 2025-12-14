"""
Rutube video to text generation API.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging
import asyncio
from pathlib import Path
import shutil

from ..ingest.rutube_processor import (
    process_rutube_video,
    validate_rutube_url
)
from ..nlp.transcriber import transcribe_audio, detect_language
from ..gen.demo_generator import generate_demo_post

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rutube", tags=["rutube"])


@router.post("/generate")
async def generate_text_from_rutube(
    url: str = Body(..., embed=True, description="Rutube video URL")
):
    """
    Generate text from Rutube video.
    
    Process:
    1. Download video
    2. Extract audio
    3. Transcribe audio
    4. Generate text from transcript
    
    Returns:
        - video_info: Video metadata
        - transcript: Full transcript
        - generated_text: Generated article/post
        - language: Detected language
    """
    # Validate URL
    if not validate_rutube_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Rutube URL. Expected format: https://rutube.ru/video/..."
        )
    
    temp_dir = None
    try:
        # Step 1: Download video and extract audio (run in thread pool)
        logger.info(f"Processing Rutube video: {url}")
        video_path, audio_path, video_info = await asyncio.to_thread(
            process_rutube_video, url
        )
        temp_dir = video_path.parent
        
        # Step 2: Detect language (run in thread pool)
        try:
            language = await asyncio.to_thread(detect_language, audio_path)
            lang_code = "ru" if language == "ru" else "en"
            logger.info(f"Detected language: {language}")
        except Exception as e:
            logger.warning(
                f"Language detection failed: {e}, "
                "will auto-detect during transcription"
            )
            language = None
            lang_code = "auto"
        
        # Step 3: Transcribe audio (run in thread pool)
        transcript_result = await asyncio.to_thread(
            transcribe_audio,
            audio_path,
            language=language,
            model_size="base"  # Use base for speed
        )
        transcript = transcript_result["text"]
        
        # Update language from transcription result
        detected_lang = transcript_result.get("language", language or "en")
        lang_code = "ru" if detected_lang == "ru" else "en"
        
        logger.info(f"Transcript length: {len(transcript)} characters")
        
        # Step 4: Generate text from transcript (run in thread pool)
        # Use demo generator with transcript as context
        # Limit transcript to first 1000 chars for context
        transcript_summary = (
            transcript[:1000] if len(transcript) > 1000 else transcript
        )
        
        generated_post = await asyncio.to_thread(
            generate_demo_post,
            style="analytical",  # Default style
            topic="any",
            news_items=[{
                "title": video_info.get("title", "Video Content"),
                "summary": transcript_summary,
                "link": url
            }]
        )
        
        return {
            "success": True,
            "video_info": {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0),
                "url": url
            },
            "transcript": transcript,
            "generated_text": generated_post,
            "language": lang_code,
            "transcript_length": len(transcript)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"Processing timeout: {str(e)}"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Required tool not found: {str(e)}. "
                "Please install yt-dlp and ffmpeg."
            )
        )
    except Exception as e:
        logger.error(f"Error processing Rutube video: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )
    finally:
        # Cleanup temp files (run in thread pool to avoid blocking)
        if temp_dir and temp_dir.exists():
            try:
                await asyncio.to_thread(
                    shutil.rmtree, temp_dir, ignore_errors=True
                )
                logger.info(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")

