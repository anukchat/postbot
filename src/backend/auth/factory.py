"""
Authentication provider factory.

Creates and manages auth provider instances based on configuration.
"""
import os
from typing import Optional
from functools import lru_cache
from .base import AuthProvider
from .providers.supabase import SupabaseAuthProvider
from .providers.auth0 import Auth0AuthProvider
from .providers.clerk import ClerkAuthProvider
from src.backend.exceptions import ConfigurationException
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthProviderFactory:
    """
    Factory for creating authentication provider instances.
    
    Supports multiple providers (Supabase, Auth0, Clerk) with 
    configuration-based switching via environment variables.
    """
    
    SUPPORTED_PROVIDERS = ["supabase", "auth0", "clerk"]
    
    @staticmethod
    def create_provider(provider_name: Optional[str] = None) -> AuthProvider:
        """
        Create auth provider instance based on configuration.
        
        Args:
            provider_name: Override provider name (defaults to AUTH_PROVIDER env var)
            
        Returns:
            AuthProvider instance
            
        Raises:
            ConfigurationException: If provider not supported or config invalid
        """
        # Get provider from environment or parameter
        provider = (provider_name or os.getenv("AUTH_PROVIDER", "supabase")).lower()
        
        logger.info(f"Creating auth provider: {provider}")
        
        if provider not in AuthProviderFactory.SUPPORTED_PROVIDERS:
            raise ConfigurationException(
                f"Unsupported auth provider: {provider}. "
                f"Supported providers: {', '.join(AuthProviderFactory.SUPPORTED_PROVIDERS)}"
            )
        
        # Create provider based on type
        if provider == "supabase":
            return AuthProviderFactory._create_supabase_provider()
        elif provider == "auth0":
            return AuthProviderFactory._create_auth0_provider()
        elif provider == "clerk":
            return AuthProviderFactory._create_clerk_provider()
        else:
            raise ConfigurationException(f"Provider {provider} not implemented")
    
    @staticmethod
    def _create_supabase_provider() -> SupabaseAuthProvider:
        """Create Supabase auth provider from environment"""
        url = os.getenv("SUPABASE_URL") or os.getenv("AUTH_PROVIDER_URL")
        key = os.getenv("SUPABASE_KEY") or os.getenv("AUTH_PROVIDER_KEY")
        
        if not url or not key:
            raise ConfigurationException(
                "Supabase provider requires SUPABASE_URL and SUPABASE_KEY "
                "(or AUTH_PROVIDER_URL and AUTH_PROVIDER_KEY) environment variables"
            )
        
        return SupabaseAuthProvider(url=url, key=key)
    
    @staticmethod
    def _create_auth0_provider() -> Auth0AuthProvider:
        """Create Auth0 auth provider from environment"""
        domain = os.getenv("AUTH0_DOMAIN")
        client_id = os.getenv("AUTH0_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        audience = os.getenv("AUTH0_AUDIENCE")
        
        if not domain or not client_id or not client_secret:
            raise ConfigurationException(
                "Auth0 provider requires AUTH0_DOMAIN, AUTH0_CLIENT_ID, "
                "and AUTH0_CLIENT_SECRET environment variables"
            )
        
        return Auth0AuthProvider(
            domain=domain,
            client_id=client_id,
            client_secret=client_secret,
            audience=audience
        )
    
    @staticmethod
    def _create_clerk_provider() -> ClerkAuthProvider:
        """Create Clerk auth provider from environment"""
        secret_key = os.getenv("CLERK_SECRET_KEY")
        publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")
        
        if not secret_key or not publishable_key:
            raise ConfigurationException(
                "Clerk provider requires CLERK_SECRET_KEY and CLERK_PUBLISHABLE_KEY "
                "environment variables"
            )
        
        return ClerkAuthProvider(
            secret_key=secret_key,
            publishable_key=publishable_key
        )


@lru_cache()
def get_auth_provider() -> AuthProvider:
    """
    Get singleton auth provider instance.
    
    Uses LRU cache to ensure only one provider instance is created
    per application lifecycle.
    
    Returns:
        Configured AuthProvider instance
    """
    return AuthProviderFactory.create_provider()
