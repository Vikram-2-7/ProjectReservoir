"""
Custom exceptions for BrookStream.Ai
Provides specific exception types for better error handling.
"""

class BrookStreamException(Exception):
    """Base exception for BrookStream.Ai application."""
    pass


class WeatherAPIError(BrookStreamException):
    """Exception raised when weather API calls fail."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class DataProcessingError(BrookStreamException):
    """Exception raised during data processing operations."""
    pass


class MLModelError(BrookStreamException):
    """Exception raised during ML model operations."""
    pass


class DamDataError(BrookStreamException):
    """Exception raised when dam data operations fail."""
    pass


class ConfigurationError(BrookStreamException):
    """Exception raised when configuration is invalid."""
    pass


class ValidationError(BrookStreamException):
    """Exception raised when data validation fails."""
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class AlertError(BrookStreamException):
    """Exception raised during alert operations."""
    pass


class NotificationError(BrookStreamException):
    """Exception raised during notification operations."""
    pass
