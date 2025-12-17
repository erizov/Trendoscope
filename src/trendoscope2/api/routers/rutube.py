"""
Rutube API endpoints.
Handles video processing and transcription.
"""
from fastapi import APIRouter, HTTPException
import logging
import asyncio
from pathlib import Path
import shutil

from ..schemas import RutubeGenerateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rutube", tags=["rutube"])


@router.post("/generate")
async def generate_text_from_rutube(
    request: RutubeGenerateRequest
):
    """Generate text from Rutube video."""
    try:
        # Import here to avoid errors if dependencies missing
        from ...ingest.rutube_processor import (
            process_rutube_video, validate_rutube_url
        )
        from ...nlp.transcriber import transcribe_audio, detect_language
        
        url = request.url
        if not validate_rutube_url(url):
            raise HTTPException(status_code=400, detail="Invalid Rutube URL")
        
        temp_dir = None
        try:
            logger.info(f"Processing Rutube video: {url}")
            video_path, audio_path, video_info = await asyncio.to_thread(
                process_rutube_video, url
            )
            temp_dir = video_path.parent
            
            # Detect language
            try:
                audio_path_obj = (
                    Path(audio_path) if not isinstance(audio_path, Path)
                    else audio_path
                )
                language = await asyncio.to_thread(
                    detect_language, audio_path_obj, "base"
                )
                lang_code = "ru" if language == "ru" else "en"
            except Exception:
                language = None
                lang_code = "auto"
            
            # Transcribe
            audio_path_obj = (
                Path(audio_path) if not isinstance(audio_path, Path)
                else audio_path
            )
            transcript_result = await asyncio.to_thread(
                transcribe_audio,
                audio_path_obj,
                language=language,
                model_size="base"
            )
            transcript = transcript_result["text"]
            detected_lang = transcript_result.get("language", language or "en")
            lang_code = "ru" if detected_lang == "ru" else "en"
            
            return {
                "success": True,
                "video_info": video_info,
                "transcript": transcript,
                "language": lang_code,
                "transcript_length": len(transcript)
            }
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    await asyncio.to_thread(
                        shutil.rmtree, temp_dir, ignore_errors=True
                    )
                except Exception:
                    pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rutube processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to process video: {str(e)}"
        )
