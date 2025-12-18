"""
TTS (Text-to-Speech) API endpoints.
Handles audio generation and retrieval.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import mimetypes

from ..schemas import TTSGenerateRequest
from ...tts.tts_service import TTSService
from ...core.dependencies import get_tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.post("/generate")
async def generate_tts(
    request: TTSGenerateRequest,
    tts_service: TTSService = Depends(get_tts_service)
):
    """
    Generate audio from text using TTS with automatic fallback.
    """
    try:
        # Additional validation
        text = request.text.strip() if request.text else ""
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Text cannot be empty"
            )
        
        # Limit text length
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        logger.info(
            f"Generating TTS: length={len(text)}, "
            f"language={request.language}, voice_gender={request.voice_gender}, "
            f"provider={request.provider or 'default'}"
        )
        
        # Generate audio (run in thread pool for pyttsx3 to avoid blocking)
        import asyncio
        result = await asyncio.to_thread(
            tts_service.generate_audio,
            text=text,
            language=request.language if request.language != 'auto' else None,
            voice_gender=request.voice_gender,
            provider=request.provider
        )
        
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate TTS: {str(e)}"
        )


@router.get("/audio/{audio_id}")
async def get_tts_audio(
    audio_id: str = PathParam(..., description="Audio ID"),
    tts_service: TTSService = Depends(get_tts_service)
):
    """Get generated TTS audio file."""
    try:
        audio_path = tts_service.get_audio_path(audio_id)
        
        if not audio_path or not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio not found")
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(audio_path))
        if not mime_type:
            mime_type = "audio/mpeg"  # Default for .mp3
        
        return FileResponse(
            path=str(audio_path),
            media_type=mime_type,
            filename=f"{audio_id}.mp3"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audio: {str(e)}"
        )


@router.get("/stats")
async def get_tts_stats(
    tts_service: TTSService = Depends(get_tts_service)
):
    """Get TTS service statistics."""
    try:
        stats = tts_service.get_cache_stats()
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"TTS stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get TTS stats: {str(e)}"
        )
