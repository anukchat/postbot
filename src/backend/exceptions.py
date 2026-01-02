"""
Custom exceptions for PostBot application.
Provides specific exception types for better error handling and debugging.
"""


class PostBotException(Exception):
    """Base exception for all PostBot errors"""
    pass


class DatabaseException(PostBotException):
    """Raised when database operations fail"""
    pass


class AuthenticationException(PostBotException):
    """Raised when authentication fails"""
    pass


class AuthorizationException(PostBotException):
    """Raised when user lacks required permissions"""
    pass


class ValidationException(PostBotException):
    """Raised when input validation fails"""
    pass


class ConfigurationException(PostBotException):
    """Raised when configuration is invalid or missing"""
    pass


class ExternalServiceException(PostBotException):
    """Raised when external service calls fail"""
    pass


class ResourceNotFoundException(PostBotException):
    """Raised when requested resource is not found"""
    pass
