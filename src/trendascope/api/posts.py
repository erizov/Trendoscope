"""
Post management API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..storage.post_storage import PostStorage
from ..utils.response import APIResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/posts", tags=["posts"])

limiter = Limiter(key_func=get_remote_address)
post_storage = PostStorage()


@router.post("/save")
async def save_post(
    request: Request,
    post: PostSaveRequest
):
    """Save a generated post."""
    try:
        limiter.check("20/minute", request)
    except RateLimitExceeded:
        return APIResponse.error_response("Rate limit exceeded")
    
    try:
        post_id = post_storage.save_post(post.dict())
        return APIResponse.success_response(
            data={"post_id": post_id},
            metadata={"request_id": getattr(request.state, "request_id", None)}
        )
    except Exception as e:
        logger.error("save_post_failed", extra={"error": str(e)}, exc_info=True)
        return APIResponse.error_response(f"Failed to save post: {str(e)}")


@router.get("/list")
async def list_posts(
    request: Request,
    limit: int = Query(default=50, le=100)
):
    """List saved posts."""
    try:
        limiter.check("30/minute", request)
    except RateLimitExceeded:
        return APIResponse.error_response("Rate limit exceeded")
    
    try:
        posts = post_storage.list_posts(limit=limit)
        return APIResponse.success_response(
            data={"posts": posts, "count": len(posts)},
            metadata={"request_id": getattr(request.state, "request_id", None)}
        )
    except Exception as e:
        logger.error("list_posts_failed", extra={"error": str(e)}, exc_info=True)
        return APIResponse.error_response(f"Failed to list posts: {str(e)}")


@router.get("/{post_id}")
async def get_post(
    request: Request,
    post_id: str
):
    """Get a specific post."""
    try:
        limiter.check("30/minute", request)
    except RateLimitExceeded:
        return APIResponse.error_response("Rate limit exceeded")
    
    try:
        post = post_storage.get_post(post_id)
        if not post:
            return APIResponse.error_response("Post not found")
        
        return APIResponse.success_response(
            data=post,
            metadata={"request_id": getattr(request.state, "request_id", None)}
        )
    except Exception as e:
        logger.error("get_post_failed", extra={"error": str(e)}, exc_info=True)
        return APIResponse.error_response(f"Failed to get post: {str(e)}")


@router.put("/{post_id}")
async def update_post(
    request: Request,
    post_id: str,
    updates: PostUpdateRequest
):
    """Update a post."""
    try:
        limiter.check("20/minute", request)
    except RateLimitExceeded:
        return APIResponse.error_response("Rate limit exceeded")
    
    try:
        # Only include non-None fields
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        success = post_storage.update_post(post_id, update_dict)
        if not success:
            return APIResponse.error_response("Post not found")
        
        return APIResponse.success_response(
            data={"post_id": post_id, "updated": True},
            metadata={"request_id": getattr(request.state, "request_id", None)}
        )
    except Exception as e:
        logger.error("update_post_failed", extra={"error": str(e)}, exc_info=True)
        return APIResponse.error_response(f"Failed to update post: {str(e)}")


@router.delete("/{post_id}")
async def delete_post(
    request: Request,
    post_id: str
):
    """Delete a post."""
    try:
        limiter.check("20/minute", request)
    except RateLimitExceeded:
        return APIResponse.error_response("Rate limit exceeded")
    
    try:
        success = post_storage.delete_post(post_id)
        if not success:
            return APIResponse.error_response("Post not found")
        
        return APIResponse.success_response(
            data={"post_id": post_id, "deleted": True},
            metadata={"request_id": getattr(request.state, "request_id", None)}
        )
    except Exception as e:
        logger.error("delete_post_failed", extra={"error": str(e)}, exc_info=True)
        return APIResponse.error_response(f"Failed to delete post: {str(e)}")

