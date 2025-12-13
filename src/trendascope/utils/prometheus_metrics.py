"""
Prometheus metrics exporter.
Provides metrics for monitoring and analytics.
"""
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime
import time

# Simple in-memory metrics store (can be replaced with Prometheus client)
_metrics = {
    'requests_total': defaultdict(int),
    'requests_by_endpoint': defaultdict(int),
    'requests_by_status': defaultdict(int),
    'request_duration': [],
    'llm_calls_total': defaultdict(int),
    'llm_calls_by_provider': defaultdict(int),
    'llm_cost_total': defaultdict(float),
    'translation_requests': defaultdict(int),
    'news_items_fetched': defaultdict(int),
    'errors_total': defaultdict(int),
    'errors_by_type': defaultdict(int),
}


def increment_counter(metric_name: str, labels: Dict[str, str] = None):
    """Increment a counter metric."""
    key = _format_key(metric_name, labels)
    _metrics['requests_total'][key] += 1


def increment_endpoint_counter(endpoint: str, status_code: int):
    """Increment endpoint-specific counters."""
    _metrics['requests_by_endpoint'][endpoint] += 1
    _metrics['requests_by_status'][f"{endpoint}:{status_code}"] += 1


def record_request_duration(duration: float, endpoint: str):
    """Record request duration."""
    _metrics['request_duration'].append({
        'duration': duration,
        'endpoint': endpoint,
        'timestamp': time.time()
    })
    # Keep only last 1000 measurements
    if len(_metrics['request_duration']) > 1000:
        _metrics['request_duration'] = _metrics['request_duration'][-1000:]


def record_llm_call(provider: str, model: str = None, cost: float = 0.0):
    """Record LLM API call."""
    _metrics['llm_calls_total']['total'] += 1
    _metrics['llm_calls_by_provider'][provider] += 1
    if cost > 0:
        _metrics['llm_cost_total'][provider] += cost


def record_translation(language: str):
    """Record translation request."""
    _metrics['translation_requests'][language] += 1


def record_news_fetch(count: int, source: str = 'unknown'):
    """Record news fetch."""
    _metrics['news_items_fetched'][source] += count


def record_error(error_type: str, endpoint: str = None):
    """Record error."""
    _metrics['errors_total']['total'] += 1
    _metrics['errors_by_type'][error_type] += 1
    if endpoint:
        _metrics['errors_by_type'][f"{error_type}:{endpoint}"] += 1


def _format_key(metric_name: str, labels: Dict[str, str] = None) -> str:
    """Format metric key with labels."""
    if not labels:
        return metric_name
    label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
    return f"{metric_name}{{{label_str}}}"


def get_metrics() -> Dict[str, Any]:
    """Get all metrics in Prometheus format."""
    # Calculate averages
    durations = _metrics['request_duration']
    avg_duration = sum(d['duration'] for d in durations) / len(durations) if durations else 0
    
    return {
        'requests_total': dict(_metrics['requests_total']),
        'requests_by_endpoint': dict(_metrics['requests_by_endpoint']),
        'requests_by_status': dict(_metrics['requests_by_status']),
        'request_duration_avg_seconds': avg_duration,
        'request_duration_count': len(durations),
        'llm_calls_total': dict(_metrics['llm_calls_total']),
        'llm_calls_by_provider': dict(_metrics['llm_calls_by_provider']),
        'llm_cost_total': dict(_metrics['llm_cost_total']),
        'translation_requests': dict(_metrics['translation_requests']),
        'news_items_fetched': dict(_metrics['news_items_fetched']),
        'errors_total': dict(_metrics['errors_total']),
        'errors_by_type': dict(_metrics['errors_by_type']),
    }


def get_prometheus_format() -> str:
    """Get metrics in Prometheus text format."""
    lines = []
    
    # Requests
    for key, value in _metrics['requests_total'].items():
        lines.append(f"trendoscope_requests_total{{{key}}} {value}")
    
    for endpoint, count in _metrics['requests_by_endpoint'].items():
        lines.append(f'trendoscope_requests_by_endpoint{{endpoint="{endpoint}"}} {count}')
    
    # LLM calls
    for provider, count in _metrics['llm_calls_by_provider'].items():
        lines.append(f'trendoscope_llm_calls_total{{provider="{provider}"}} {count}')
    
    for provider, cost in _metrics['llm_cost_total'].items():
        lines.append(f'trendoscope_llm_cost_total{{provider="{provider}"}} {cost}')
    
    # Errors
    for error_type, count in _metrics['errors_by_type'].items():
        lines.append(f'trendoscope_errors_total{{type="{error_type}"}} {count}')
    
    # Duration
    durations = _metrics['request_duration']
    if durations:
        avg = sum(d['duration'] for d in durations) / len(durations)
        lines.append(f'trendoscope_request_duration_seconds {avg}')
    
    return '\n'.join(lines) + '\n'


def reset_metrics():
    """Reset all metrics (for testing)."""
    global _metrics
    _metrics = {
        'requests_total': defaultdict(int),
        'requests_by_endpoint': defaultdict(int),
        'requests_by_status': defaultdict(int),
        'request_duration': [],
        'llm_calls_total': defaultdict(int),
        'llm_calls_by_provider': defaultdict(int),
        'llm_cost_total': defaultdict(float),
        'translation_requests': defaultdict(int),
        'news_items_fetched': defaultdict(int),
        'errors_total': defaultdict(int),
        'errors_by_type': defaultdict(int),
    }

