"""
Email API endpoints.
Handles email sending and digest functionality.
"""
from fastapi import APIRouter, HTTPException
import logging

from ..schemas import EmailSendRequest, EmailDigestRequest
from ...services.email_service import EmailService
from ...config import (
    EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, EMAIL_SMTP_USER,
    EMAIL_SMTP_PASSWORD, EMAIL_FROM, EMAIL_RATE_LIMIT_PER_MINUTE,
    NEWS_FETCH_TIMEOUT, NEWS_MAX_PER_SOURCE
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])

# Email service instance (will be injected via DI later)
email_service = EmailService(
    smtp_host=EMAIL_SMTP_HOST,
    smtp_port=EMAIL_SMTP_PORT,
    smtp_user=EMAIL_SMTP_USER,
    smtp_password=EMAIL_SMTP_PASSWORD,
    from_email=EMAIL_FROM,
    rate_limit_per_minute=EMAIL_RATE_LIMIT_PER_MINUTE
)


@router.post("/send")
async def send_email(request: EmailSendRequest):
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
async def send_daily_digest(request: EmailDigestRequest):
    """
    Send daily news digest email.
    
    Args:
        request: Digest request with to_email and language
        
    Returns:
        Success status
    """
    try:
        # Get top news items using NewsService
        from ...services.news_service import NewsService
        news_result = await NewsService.get_news_feed(
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
async def get_email_status():
    """
    Get email service status.
    
    Returns:
        Email service configuration and status
    """
    from ...config import EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD
    return {
        "success": True,
        "enabled": email_service.is_available(),
        "configured": bool(EMAIL_SMTP_USER and EMAIL_SMTP_PASSWORD)
    }
