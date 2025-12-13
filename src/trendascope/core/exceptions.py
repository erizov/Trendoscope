"""
Custom exception hierarchy.
Provides structured error handling.
"""


class TrendoscopeException(Exception):
    """Base exception for all Trendoscope errors."""
    pass


class ConfigurationError(TrendoscopeException):
    """Configuration-related errors."""
    pass


class ValidationError(TrendoscopeException):
    """Validation errors."""
    pass


class RepositoryError(TrendoscopeException):
    """Repository/data access errors."""
    pass


class LLMProviderError(TrendoscopeException):
    """LLM provider errors."""
    pass


class TranslationError(TrendoscopeException):
    """Translation errors."""
    pass


class NewsAggregationError(TrendoscopeException):
    """News aggregation errors."""
    pass


class ServiceUnavailableError(TrendoscopeException):
    """Service unavailable errors."""
    pass


class RateLimitError(TrendoscopeException):
    """Rate limit exceeded."""
    pass

