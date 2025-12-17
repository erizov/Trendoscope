"""
Admin API endpoints.
Handles database management and statistics.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from ...storage.news_db import NewsDatabase
from ...config import NEWS_DB_MAX_RECORDS

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
