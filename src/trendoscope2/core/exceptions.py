"""
Structured exception classes for Trendoscope2.
Provides consistent error handling with error codes.
"""
from typing import Optional


class TrendoscopeException(Exception):
    """Base exception for Trendoscope2."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500
    ):
        """
        Initialize exception.
        
        Args:
            message: Error message
            error_code: Machine-readable error code
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code


class NewsFetchError(TrendoscopeException):
    """Error fetching news from sources."""
    
    def __init__(self, message: str = "Failed to fetch news"):
        super().__init__(message, "NEWS_FETCH_ERROR", 503)


class NewsProcessingError(TrendoscopeException):
    """Error processing news items."""
    
    def __init__(self, message: str = "Failed to process news"):
        super().__init__(message, "NEWS_PROCESSING_ERROR", 500)


class TranslationError(TrendoscopeException):
    """Error translating content."""
    
    def __init__(self, message: str = "Translation failed"):
        super().__init__(message, "TRANSLATION_ERROR", 500)


class TTSError(TrendoscopeException):
    """Error generating TTS audio."""
    
    def __init__(self, message: str = "TTS generation failed"):
        super().__init__(message, "TTS_ERROR", 503)


class EmailError(TrendoscopeException):
    """Error sending email."""
    
    def __init__(self, message: str = "Email sending failed"):
        super().__init__(message, "EMAIL_ERROR", 503)


class TelegramError(TrendoscopeException):
    """Error posting to Telegram."""
    
    def __init__(self, message: str = "Telegram post failed"):
        super().__init__(message, "TELEGRAM_ERROR", 503)


class DatabaseError(TrendoscopeException):
    """Error accessing database."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", 500)


class ValidationError(TrendoscopeException):
    """Validation error."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR", 400)


class ConfigurationError(TrendoscopeException):
    """Configuration error."""
    
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, "CONFIGURATION_ERROR", 500)
