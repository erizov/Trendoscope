"""
Error monitoring and metrics collection.
"""
import time
from typing import Dict, Any, Optional
from functools import wraps
from ..utils.logger import get_logger

logger = get_logger(__name__)

# In-memory metrics storage (can be replaced with Prometheus)
_metrics = {
    "requests_total": 0,
    "requests_by_endpoint": {},
    "errors_total": 0,
    "errors_by_type": {},
    "response_times": [],
    "cost_total": 0.0,
    "posts_generated": 0,
}


def track_request(endpoint: str, duration: float, success: bool, error: Optional[str] = None):
    """Track API request metrics."""
    _metrics["requests_total"] += 1
    _metrics["requests_by_endpoint"][endpoint] = _metrics["requests_by_endpoint"].get(endpoint, 0) + 1
    
    if not success:
        _metrics["errors_total"] += 1
        if error:
            error_type = error.split(":")[0] if ":" in error else error
            _metrics["errors_by_type"][error_type] = _metrics["errors_by_type"].get(error_type, 0) + 1
    
    _metrics["response_times"].append(duration)
    # Keep only last 1000 response times
    if len(_metrics["response_times"]) > 1000:
        _metrics["response_times"] = _metrics["response_times"][-1000:]


def track_cost(amount: float):
    """Track cost."""
    _metrics["cost_total"] += amount


def track_post_generation():
    """Track post generation."""
    _metrics["posts_generated"] += 1


def get_metrics() -> Dict[str, Any]:
    """Get all metrics."""
    response_times = _metrics["response_times"]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "requests": {
            "total": _metrics["requests_total"],
            "by_endpoint": _metrics["requests_by_endpoint"],
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "p95_response_time_ms": round(sorted(response_times)[int(len(response_times) * 0.95)] * 1000, 2) if response_times else 0
        },
        "errors": {
            "total": _metrics["errors_total"],
            "by_type": _metrics["errors_by_type"],
            "error_rate": round(_metrics["errors_total"] / _metrics["requests_total"] * 100, 2) if _metrics["requests_total"] > 0 else 0
        },
        "cost": {
            "total_usd": round(_metrics["cost_total"], 4),
            "avg_per_post": round(_metrics["cost_total"] / _metrics["posts_generated"], 4) if _metrics["posts_generated"] > 0 else 0
        },
        "posts": {
            "generated": _metrics["posts_generated"]
        }
    }


def monitor_endpoint(func):
    """Decorator to monitor endpoint performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        error = None
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error = str(e)
            logger.error("endpoint_error", extra={"error": str(e), "endpoint": func.__name__}, exc_info=True)
            raise
        finally:
            duration = time.time() - start_time
            track_request(func.__name__, duration, success, error)
    
    return wrapper

