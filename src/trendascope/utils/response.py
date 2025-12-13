"""
Standardized API response format.
"""
from typing import Any, Optional, Dict
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response format."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create success response."""
        return {
            "success": True,
            "data": data,
            "error": None,
            "metadata": metadata or {}
        }

    @classmethod
    def error_response(
        cls,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create error response."""
        return {
            "success": False,
            "data": None,
            "error": error,
            "metadata": metadata or {}
        }

