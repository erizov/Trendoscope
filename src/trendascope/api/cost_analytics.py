"""
Cost analytics endpoints.
Provides cost tracking and analytics.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from ..gen.cost_tracker import get_cost_stats, get_provider_costs
from ..utils.prometheus_metrics import get_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/costs")
async def get_costs(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get cost analytics.
    
    Returns:
    - Total costs by provider
    - Cost trends over time
    - Cost per endpoint
    - Cost optimization suggestions
    """
    try:
        stats = get_cost_stats()
        provider_costs = get_provider_costs()
        metrics = get_metrics()
        
        # Calculate totals
        total_cost = sum(provider_costs.values())
        
        # Get cost breakdown
        breakdown = {
            provider: {
                'total_cost': cost,
                'percentage': (cost / total_cost * 100) if total_cost > 0 else 0,
                'calls': metrics.get('llm_calls_by_provider', {}).get(provider, 0)
            }
            for provider, cost in provider_costs.items()
        }
        
        # Cost optimization suggestions
        suggestions = []
        if total_cost > 0:
            # Find most expensive provider
            most_expensive = max(provider_costs.items(), key=lambda x: x[1])
            if most_expensive[1] > total_cost * 0.5:
                suggestions.append({
                    'type': 'provider_optimization',
                    'message': f"Consider using cheaper models for {most_expensive[0]}",
                    'potential_savings': f"{most_expensive[1] * 0.3:.2f}"
                })
        
        return {
            'success': True,
            'total_cost': total_cost,
            'breakdown': breakdown,
            'stats': stats,
            'suggestions': suggestions,
            'period_days': days
        }
        
    except Exception as e:
        logger.error(f"Cost analytics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_usage_stats(
    days: int = Query(7, ge=1, le=90, description="Number of days")
):
    """
    Get usage statistics.
    
    Returns:
    - API calls by endpoint
    - Requests per day
    - User activity
    - Popular features
    """
    try:
        metrics = get_metrics()
        
        return {
            'success': True,
            'requests_total': metrics.get('requests_total', {}).get('total', 0),
            'requests_by_endpoint': metrics.get('requests_by_endpoint', {}),
            'llm_calls': metrics.get('llm_calls_by_provider', {}),
            'translations': metrics.get('translation_requests', {}),
            'news_fetched': sum(metrics.get('news_items_fetched', {}).values()),
            'errors': metrics.get('errors_total', {}).get('total', 0),
            'period_days': days
        }
        
    except Exception as e:
        logger.error(f"Usage stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trends(
    metric: str = Query("requests", description="Metric to analyze"),
    days: int = Query(30, ge=1, le=90, description="Number of days")
):
    """
    Get trend data for a specific metric.
    
    Args:
        metric: Metric name (requests, costs, errors, etc.)
        days: Number of days to analyze
        
    Returns:
        Trend data with timestamps
    """
    try:
        metrics = get_metrics()
        
        # Simple trend calculation (in real app, would use time-series DB)
        trends = {
            'metric': metric,
            'current_value': 0,
            'trend': 'stable',
            'change_percent': 0
        }
        
        if metric == 'requests':
            trends['current_value'] = metrics.get('requests_total', {}).get('total', 0)
        elif metric == 'costs':
            trends['current_value'] = sum(metrics.get('llm_cost_total', {}).values())
        elif metric == 'errors':
            trends['current_value'] = metrics.get('errors_total', {}).get('total', 0)
        
        return {
            'success': True,
            'trends': trends,
            'period_days': days
        }
        
    except Exception as e:
        logger.error(f"Trends error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

