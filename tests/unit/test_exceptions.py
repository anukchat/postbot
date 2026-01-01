"""
Unit tests for custom exceptions.
"""
import pytest
from src.backend.exceptions import (
    PostBotException,
    DatabaseException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    ConfigurationException,
    ExternalServiceException,
    ResourceNotFoundException
)


class TestExceptions:
    """Test custom exception hierarchy."""
    
    def test_base_exception(self):
        """Test base PostBotException."""
        exc = PostBotException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
    
    def test_database_exception(self):
        """Test DatabaseException inherits from base."""
        exc = DatabaseException("Database error")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Database error"
    
    def test_authentication_exception(self):
        """Test AuthenticationException."""
        exc = AuthenticationException("Auth failed")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Auth failed"
    
    def test_authorization_exception(self):
        """Test AuthorizationException."""
        exc = AuthorizationException("Access denied")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Access denied"
    
    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Invalid input")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Invalid input"
    
    def test_configuration_exception(self):
        """Test ConfigurationException."""
        exc = ConfigurationException("Config missing")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Config missing"
    
    def test_external_service_exception(self):
        """Test ExternalServiceException."""
        exc = ExternalServiceException("API call failed")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "API call failed"
    
    def test_resource_not_found_exception(self):
        """Test ResourceNotFoundException."""
        exc = ResourceNotFoundException("Resource not found")
        assert isinstance(exc, PostBotException)
        assert str(exc) == "Resource not found"
    
    def test_exception_can_be_raised(self):
        """Test exceptions can be raised and caught."""
        with pytest.raises(DatabaseException) as exc_info:
            raise DatabaseException("Test database error")
        
        assert "Test database error" in str(exc_info.value)
    
    def test_exception_inheritance_chain(self):
        """Test exception inheritance works correctly."""
        exc = DatabaseException("Test")
        
        # Should be catchable as base exception
        assert isinstance(exc, PostBotException)
        assert isinstance(exc, Exception)
        
        # Should be catchable as PostBotException
        try:
            raise exc
        except PostBotException:
            pass  # Should catch
