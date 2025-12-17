"""
Telegram API endpoints.
Handles Telegram posting and connection testing.
"""
from fastapi import APIRouter, HTTPException
import logging

from ..schemas import TelegramPostRequest
from ...services.telegram_service import TelegramService
from ...config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID,
    TELEGRAM_RATE_LIMIT_PER_MINUTE
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

# Telegram service instance (will be injected via DI later)
telegram_service = TelegramService(
    bot_token=TELEGRAM_BOT_TOKEN,
    default_channel_id=TELEGRAM_CHANNEL_ID,
    rate_limit_per_minute=TELEGRAM_RATE_LIMIT_PER_MINUTE
)


@router.post("/post")
async def post_to_telegram(request: TelegramPostRequest):
    """
    Post article to Telegram channel.
    
    Args:
        request: Telegram post request with article and format_type
        
    Returns:
        Success status with message ID
    """
    try:
        result = telegram_service.post_article(
            article=request.article,
            channel_id=request.channel_id,
            format_type=request.format_type
        )
        
        if not result or not result.get('success'):
            error_msg = (
                result.get('error', 'Telegram post failed')
                if result else 'Unknown error'
            )
            raise HTTPException(
                status_code=503,
                detail=f"Failed to post to Telegram: {error_msg}"
            )
        
        return {
            "success": True,
            "message_id": result.get('message_id'),
            "message": "Posted to Telegram successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram post error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Failed to post to Telegram: {str(e)}"
        )


@router.get("/test")
async def test_telegram_connection():
    """
    Test Telegram bot connection.
    
    Returns:
        Connection status
    """
    try:
        if not telegram_service.is_available():
            return {
                "success": False,
                "message": "Telegram service is not configured",
                "available": False
            }
        
        connected = await telegram_service.test_connection()
        
        return {
            "success": connected,
            "message": "Connected successfully" if connected else "Connection failed",
            "available": telegram_service.is_available()
        }
    except Exception as e:
        logger.error(f"Telegram test error: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "available": False
        }


@router.get("/status")
async def get_telegram_status():
    """
    Get Telegram service status.
    
    Returns:
        Telegram service configuration and status
    """
    from ...config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
    return {
        "success": True,
        "enabled": telegram_service.is_available(),
        "configured": bool(TELEGRAM_BOT_TOKEN),
        "default_channel": TELEGRAM_CHANNEL_ID
    }
