"""
Admin API endpoints.
Handles database management and statistics.
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
import logging

from ...storage.news_db import NewsDatabase
from ...config import NEWS_DB_MAX_RECORDS
from ...services.task_queue import get_task_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/db", tags=["admin"])


@router.post("/cleanup")
async def cleanup_database(
    keep_count: Optional[int] = Query(
        default=None,
        ge=1000,
        le=100000,
        description="Number of records to keep"
    )
):
    """
    Cleanup database, keeping only the most recent N records.
    
    Args:
        keep_count: Number of most recent records to keep
        
    Returns:
        Cleanup statistics
    """
    try:
        if keep_count is None:
            keep_count = NEWS_DB_MAX_RECORDS
        
        with NewsDatabase() as db:
            # Get statistics before cleanup
            stats_before = db.get_statistics()
            total_before = stats_before.get('total_items', 0)
            
            # Perform cleanup
            deleted_count = db.cleanup_old_records(keep_count=keep_count)
            
            # Get statistics after cleanup
            stats_after = db.get_statistics()
            total_after = stats_after.get('total_items', 0)
            
            logger.info(
                f"Database cleanup completed: kept {total_after} records, "
                f"deleted {deleted_count} records"
            )
            
            return {
                "success": True,
                "message": "Database cleanup completed successfully",
                "kept_records": total_after,
                "deleted_records": deleted_count,
                "total_before": total_before,
                "total_after": total_after,
                "keep_limit": keep_count
            }
    except Exception as e:
        logger.error(f"Database cleanup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup database: {str(e)}"
        )


@router.get("/stats")
async def get_database_stats():
    """
    Get database statistics.
    
    Returns:
        Database statistics including record counts
    """
    try:
        with NewsDatabase() as db:
            stats = db.get_statistics()
            return {
                "success": True,
                **stats
            }
    except Exception as e:
        logger.error(f"Database stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database statistics: {str(e)}"
        )


@router.post("/tasks/enqueue")
async def enqueue_task(
    task_name: str = Body(..., description="Task name"),
    args: list = Body(default=[], description="Task arguments"),
    kwargs: Dict[str, Any] = Body(default={}, description="Task keyword arguments")
):
    """
    Enqueue a background task.
    
    Returns:
        Job ID
    """
    try:
        task_queue = get_task_queue()
        
        # Map task names to functions
        task_map = {
            "fetch_news": "trendoscope2.services.news_service.NewsService.fetch_news",
            "process_news": "trendoscope2.services.news_service.NewsService.process_news_items",
            "cleanup_db": "trendoscope2.storage.news_db.NewsDatabase.cleanup_old_records"
        }
        
        if task_name not in task_map:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {task_name}"
            )
        
        # Import and enqueue
        module_path, func_name = task_map[task_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[func_name])
        func = getattr(module, func_name)
        
        job_id = task_queue.enqueue(func, *args, **kwargs)
        
        if not job_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to enqueue task"
            )
        
        return {
            "success": True,
            "job_id": job_id,
            "task": task_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task enqueue error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enqueue task: {str(e)}"
        )


@router.get("/tasks/{job_id}")
async def get_task_status(job_id: str):
    """
    Get task status.
    
    Args:
        job_id: Job ID
        
    Returns:
        Task status
    """
    try:
        task_queue = get_task_queue()
        status = task_queue.get_job_status(job_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        
        return {
            "success": True,
            **status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/tasks/queue/stats")
async def get_queue_stats():
    """Get task queue statistics."""
    try:
        task_queue = get_task_queue()
        stats = task_queue.get_queue_stats()
        
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Queue stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue stats: {str(e)}"
        )
