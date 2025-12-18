"""
Email API endpoints.
Handles email sending and digest functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from ..schemas import EmailSendRequest, EmailDigestRequest
from ...services.email_service import EmailService
from ...core.dependencies import get_email_service, get_news_service
from ...services.news_service import NewsService
from ...config import EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    email_service: EmailService = Depends(get_email_service)
):
    """
    Send email to recipient.
    
    Args:
        request: Email send request with to_email, subject, content
        
    Returns:
        Success status
    """
    try:
        success = email_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        return {
            "success": True,
            "message": "Email sent successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email sending error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/digest")
async def send_daily_digest(
    request: EmailDigestRequest,
    email_service: EmailService = Depends(get_email_service),
    news_service: NewsService = Depends(get_news_service)
):
    """
    Send daily news digest email.
    
    Args:
        request: Digest request with to_email and language
        email_service: Injected EmailService
        news_service: Injected NewsService
        
    Returns:
        Success status
    """
    try:
        # Get top news items using NewsService
        news_result = await news_service.get_news_feed(
            category='all',
            limit=5,
            language='all',
            translate_to='none',
            use_cache=True
        )
        news_items = news_result.get('news', [])
        
        success = await email_service.send_daily_digest_async(
            to_email=request.to_email,
            news_items=news_items,
            language=request.language
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send daily digest"
            )
        
        return {
            "success": True,
            "message": "Daily digest sent successfully",
            "items_count": len(news_items)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily digest error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send daily digest: {str(e)}"
        )


@router.get("/status")
async def get_email_status(
    email_service: EmailService = Depends(get_email_service)
):
    """
    Get email service status.
    
    Args:
        email_service: Injected EmailService
    
    Returns:
        Email service configuration and status
    """
    return {
        "success": True,
        "enabled": email_service.is_available(),
        "configured": bool(EMAIL_SMTP_USER and EMAIL_SMTP_PASSWORD)
    }
