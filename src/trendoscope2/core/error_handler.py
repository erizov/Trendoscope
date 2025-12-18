"""
Global error handler for FastAPI application.
Provides consistent error responses.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import TrendoscopeException

logger = logging.getLogger(__name__)


async def trendoscope_exception_handler(
    request: Request,
    exc: TrendoscopeException
) -> JSONResponse:
    """
    Handle TrendoscopeException with structured response.
    
    Args:
        request: FastAPI request
        exc: TrendoscopeException instance
        
    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"TrendoscopeException: {exc.error_code} - {exc.message}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "detail": exc.message,
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle general exceptions with structured response.
    
    Args:
        request: FastAPI request
        exc: Exception instance
        
    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "detail": "An internal error occurred",
            "path": str(request.url.path)
        }
    )
