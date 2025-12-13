"""
Global error handler for FastAPI.
Provides consistent error responses.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
import logging

from .exceptions import (
    TrendoscopeException,
    ConfigurationError,
    ValidationError,
    RepositoryError,
    LLMProviderError,
    TranslationError,
    NewsAggregationError,
    ServiceUnavailableError,
    RateLimitError
)

logger = logging.getLogger(__name__)


async def trendoscope_exception_handler(
    request: Request,
    exc: TrendoscopeException
) -> JSONResponse:
    """
    Handle Trendoscope custom exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception instance
        
    Returns:
        JSON error response
    """
    status_code = 500
    error_type = type(exc).__name__
    
    # Map exception types to status codes
    if isinstance(exc, ValidationError):
        status_code = 400
    elif isinstance(exc, RateLimitError):
        status_code = 429
    elif isinstance(exc, ServiceUnavailableError):
        status_code = 503
    elif isinstance(exc, ConfigurationError):
        status_code = 500
    elif isinstance(exc, (RepositoryError, LLMProviderError, TranslationError, NewsAggregationError)):
        status_code = 500
    
    logger.error(
        f"Trendoscope exception: {error_type}",
        extra={
            "error_type": error_type,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": str(exc),
            "error_type": error_type,
            "path": request.url.path
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception instance
        
    Returns:
        JSON error response
    """
    logger.exception(
        f"Unexpected error: {type(exc).__name__}",
        extra={
            "error_type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_type": type(exc).__name__,
            "path": request.url.path
        }
    )

