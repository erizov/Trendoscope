"""
Platform integration endpoints.
Allows publishing to various platforms.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import logging

from ..storage.post_storage import PostStorage
from ..utils.response import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post("/telegram/publish")
async def publish_to_telegram(
    post_id: str,
    chat_id: Optional[str] = Body(None, embed=True),
    bot_token: Optional[str] = Body(None, embed=True)
):
    """
    Publish post to Telegram channel.
    
    Args:
        post_id: Post ID to publish
        chat_id: Telegram chat/channel ID
        bot_token: Telegram bot token
        
    Returns:
        Publication result
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # In production, would use python-telegram-bot
        # For now, return formatted message
        message = f"*{post.get('title', '')}*\n\n{post.get('text', '')[:4000]}"
        
        return APIResponse.success_response(
            data={
                'message': message,
                'formatted': True,
                'note': 'Telegram integration requires bot token configuration'
            },
            message="Post formatted for Telegram"
        )
        
    except Exception as e:
        logger.error(f"Telegram publish error: {e}", exc_info=True)
        return APIResponse.error_response(f"Publish failed: {str(e)}")


@router.post("/wordpress/export")
async def export_to_wordpress(
    post_id: str,
    format: str = Body("xml", embed=True)
):
    """
    Export post to WordPress format.
    
    Args:
        post_id: Post ID to export
        format: Export format (xml, json, html)
        
    Returns:
        Exported content
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if format == "xml":
            # WordPress WXR format
            content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <item>
        <title>{post.get('title', '')}</title>
        <content:encoded><![CDATA[{post.get('text', '')}]]></content:encoded>
        <excerpt:encoded><![CDATA[{post.get('text', '')[:200]}]]></excerpt:encoded>
        <wp:post_type>post</wp:post_type>
        <wp:status>draft</wp:status>
    </item>
</channel>
</rss>"""
        elif format == "json":
            import json
            content = json.dumps({
                'title': post.get('title', ''),
                'content': post.get('text', ''),
                'excerpt': post.get('text', '')[:200],
                'status': 'draft'
            }, ensure_ascii=False, indent=2)
        else:  # html
            content = f"""<html>
<head><title>{post.get('title', '')}</title></head>
<body>
    <h1>{post.get('title', '')}</h1>
    <div>{post.get('text', '').replace(chr(10), '<br>')}</div>
</body>
</html>"""
        
        return APIResponse.success_response(
            data={
                'content': content,
                'format': format,
                'post_id': post_id
            },
            message="Post exported successfully"
        )
        
    except Exception as e:
        logger.error(f"WordPress export error: {e}", exc_info=True)
        return APIResponse.error_response(f"Export failed: {str(e)}")


@router.post("/livejournal/publish")
async def publish_to_livejournal(
    post_id: str,
    username: Optional[str] = Body(None, embed=True),
    password: Optional[str] = Body(None, embed=True)
):
    """
    Publish post to LiveJournal.
    
    Args:
        post_id: Post ID to publish
        username: LiveJournal username
        password: LiveJournal password
        
    Returns:
        Publication result
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # In production, would use LiveJournal API
        # For now, return formatted data
        return APIResponse.success_response(
            data={
                'title': post.get('title', ''),
                'text': post.get('text', ''),
                'tags': post.get('tags', []),
                'note': 'LiveJournal integration requires credentials'
            },
            message="Post formatted for LiveJournal"
        )
        
    except Exception as e:
        logger.error(f"LiveJournal publish error: {e}", exc_info=True)
        return APIResponse.error_response(f"Publish failed: {str(e)}")


@router.get("/formats")
async def get_export_formats():
    """
    Get available export formats.
    
    Returns:
        List of supported formats
    """
    return APIResponse.success_response(
        data={
            'formats': [
                {
                    'id': 'telegram',
                    'name': 'Telegram',
                    'description': 'Publish to Telegram channel'
                },
                {
                    'id': 'wordpress',
                    'name': 'WordPress',
                    'description': 'Export as WordPress XML/JSON/HTML'
                },
                {
                    'id': 'livejournal',
                    'name': 'LiveJournal',
                    'description': 'Publish to LiveJournal blog'
                },
                {
                    'id': 'markdown',
                    'name': 'Markdown',
                    'description': 'Export as Markdown file'
                }
            ]
        },
        message="Available export formats"
    )

