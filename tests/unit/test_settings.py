"""
Unit tests for settings module.
"""
import os
import pytest
from unittest.mock import patch
from src.backend.settings import Settings, get_settings
from src.backend.exceptions import ConfigurationException


class TestSettings:
    """Test Settings class and validation."""
    
    def test_settings_requires_database_url(self):
        """Test that DATABASE_URL is required."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationException) as exc_info:
                Settings()
            assert "DATABASE_URL" in str(exc_info.value)
    
    def test_settings_default_auth_provider(self):
        """Test default auth provider is supabase."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.auth_provider == "supabase"
    
    def test_settings_supabase_provider(self):
        """Test Supabase provider configuration."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "AUTH_PROVIDER": "supabase",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.supabase_url == "https://test.supabase.co"
            assert settings.supabase_key == "test_key"
    
    def test_settings_missing_supabase_config(self):
        """Test error when Supabase config is missing."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "AUTH_PROVIDER": "supabase"
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigurationException) as exc_info:
                Settings()
            assert "SUPABASE_URL" in str(exc_info.value) or "SUPABASE_KEY" in str(exc_info.value)
    
    def test_settings_auth0_provider(self):
        """Test Auth0 provider configuration."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "AUTH_PROVIDER": "auth0",
            "AUTH0_DOMAIN": "test.auth0.com",
            "AUTH0_CLIENT_ID": "client_id",
            "AUTH0_CLIENT_SECRET": "client_secret"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.auth0_domain == "test.auth0.com"
            assert settings.auth0_client_id == "client_id"
    
    def test_settings_clerk_provider(self):
        """Test Clerk provider configuration."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "AUTH_PROVIDER": "clerk",
            "CLERK_SECRET_KEY": "sk_test_xxx",
            "CLERK_PUBLISHABLE_KEY": "pk_test_xxx"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.clerk_secret_key == "sk_test_xxx"
            assert settings.clerk_publishable_key == "pk_test_xxx"
    
    def test_settings_environment_detection(self):
        """Test environment detection."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key",
            "ENVIRONMENT": "production"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.is_production()
            assert not settings.is_development()
    
    def test_settings_default_values(self):
        """Test default values are set correctly."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key"
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.log_level == "INFO"
            assert settings.environment == "development"
            assert settings.auth_cache_ttl == 300
            assert settings.auth_cache_size == 100
    
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        env = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test_key"
        }
        with patch.dict(os.environ, env, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2  # Same instance
