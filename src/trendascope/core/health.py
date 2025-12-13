"""
Health check system for monitoring component status.
"""
from typing import Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Health check result."""
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class HealthChecker:
    """Health check registry and executor."""
    
    def __init__(self):
        """Initialize health checker."""
        self._checks: Dict[str, Callable] = {}
    
    def register(self, name: str, check: Callable):
        """
        Register health check.
        
        Args:
            name: Check name
            check: Check function (should return HealthCheckResult)
        """
        self._checks[name] = check
        logger.debug(f"Registered health check: {name}")
    
    async def check_all(self) -> Dict[str, HealthCheckResult]:
        """
        Run all health checks.
        
        Returns:
            Dictionary of check results
        """
        results = {}
        for name, check in self._checks.items():
            try:
                if hasattr(check, '__call__'):
                    # Check if async
                    import asyncio
                    if asyncio.iscoroutinefunction(check):
                        result = await check()
                    else:
                        result = check()
                    results[name] = result
                else:
                    results[name] = HealthCheckResult(
                        status=HealthStatus.UNHEALTHY,
                        message="Invalid check function",
                        details={}
                    )
            except Exception as e:
                logger.error(f"Health check '{name}' failed: {e}")
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                    details={"error": type(e).__name__}
                )
        return results
    
    async def check_overall(self) -> HealthStatus:
        """
        Get overall health status.
        
        Returns:
            Overall health status
        """
        results = await self.check_all()
        if not results:
            return HealthStatus.HEALTHY
        
        statuses = [r.status for r in results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# Health check functions
async def check_database() -> HealthCheckResult:
    """Check database connectivity."""
    try:
        from ...storage.news_db import NewsDatabase
        from .settings import get_settings
        
        settings = get_settings()
        db = NewsDatabase(settings.database.news_db_path)
        stats = db.get_statistics()
        db.close()
        
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="Database accessible",
            details={"total_items": stats.get('total_items', 0)}
        )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"Database error: {str(e)}",
            details={"error": type(e).__name__}
        )


async def check_cache() -> HealthCheckResult:
    """Check cache availability."""
    try:
        # Cache might not be implemented yet, so make it optional
        try:
            from ...utils.cache import get_cache
        except ImportError:
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="Cache not implemented",
                details={}
            )
        
        cache = get_cache()
        # Try to set and get a test value
        test_key = "__health_check__"
        await cache.set(test_key, "test", ttl=1)
        value = await cache.get(test_key)
        await cache.delete(test_key)
        
        if value == "test":
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Cache operational",
                details={"type": cache.__class__.__name__}
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="Cache test failed",
                details={}
            )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            message=f"Cache unavailable: {str(e)}",
            details={"error": type(e).__name__}
        )


async def check_openai_provider() -> HealthCheckResult:
    """Check OpenAI provider availability."""
    try:
        from ..gen.llm.providers import call_openai
        from ..utils.balance_checker import check_openai_balance
        
        has_balance, error = check_openai_balance()
        
        if has_balance:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="OpenAI provider available",
                details={"has_balance": True}
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="OpenAI provider unavailable (no balance/API key)",
                details={"has_balance": False}
            )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            message=f"OpenAI check failed: {str(e)}",
            details={"error": type(e).__name__}
        )


async def check_anthropic_provider() -> HealthCheckResult:
    """Check Anthropic provider availability."""
    try:
        from ...utils.balance_checker import check_anthropic_balance
        
        has_balance = check_anthropic_balance()
        
        if has_balance:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Anthropic provider available",
                details={"has_balance": True}
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="Anthropic provider unavailable (no balance/API key)",
                details={"has_balance": False}
            )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            message=f"Anthropic check failed: {str(e)}",
            details={"error": type(e).__name__}
        )


async def check_translator() -> HealthCheckResult:
    """Check translation service availability."""
    try:
        from ...nlp.translator import FREE_TRANSLATOR_AVAILABLE
        
        if FREE_TRANSLATOR_AVAILABLE:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Free translator available",
                details={"provider": "deep-translator"}
            )
        else:
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="Free translator not available",
                details={"provider": None}
            )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            message=f"Translator check failed: {str(e)}",
            details={"error": type(e).__name__}
        )

