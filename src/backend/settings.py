"""
Application settings and environment validation.
Ensures all required environment variables are present and valid before startup.
Supports multiple authentication providers (Supabase, Auth0, Clerk).
"""
import os
from typing import Optional, List
from functools import lru_cache
from src.backend.exceptions import ConfigurationException


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        self.validate_required_env_vars()
        
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "")
        
        # Authentication Provider Configuration
        self.auth_provider: str = os.getenv("AUTH_PROVIDER", "supabase").lower()

        # For Supabase
        self.supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
        self.supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
        
        # For Auth0
        self.auth0_domain: Optional[str] = os.getenv("AUTH0_DOMAIN")
        self.auth0_client_id: Optional[str] = os.getenv("AUTH0_CLIENT_ID")
        self.auth0_client_secret: Optional[str] = os.getenv("AUTH0_CLIENT_SECRET")
        self.auth0_audience: Optional[str] = os.getenv("AUTH0_AUDIENCE")
        
        # For Clerk
        self.clerk_secret_key: Optional[str] = os.getenv("CLERK_SECRET_KEY")
        self.clerk_publishable_key: Optional[str] = os.getenv("CLERK_PUBLISHABLE_KEY")
        
        # API Configuration
        self.api_url: str = os.getenv("API_URL", "http://localhost:5173")
        self.frontend_url: Optional[str] = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.allowed_origins: list[str] = os.getenv("ALLOWED_ORIGINS", self.api_url).split(",")
        
        # Cache Configuration
        self.auth_cache_ttl: int = int(os.getenv("AUTH_CACHE_TTL", "300"))  # 5 minutes
        self.auth_cache_size: int = int(os.getenv("AUTH_CACHE_SIZE", "100"))
        
        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        # Environment
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        
    @staticmethod
    def validate_required_env_vars():
        """Validate that all required environment variables are set"""
        missing_vars: List[str] = []

        if not os.getenv("DATABASE_URL"):
            missing_vars.append("DATABASE_URL")
        
        # Check auth provider configuration
        auth_provider = os.getenv("AUTH_PROVIDER", "supabase").lower()
        
        if auth_provider == "supabase":
            # Supabase requires URL and key.
            if not os.getenv("SUPABASE_URL"):
                missing_vars.append("SUPABASE_URL")
            if not os.getenv("SUPABASE_KEY"):
                missing_vars.append("SUPABASE_KEY")
        elif auth_provider == "auth0":
            # Auth0 requires domain, client ID, and secret
            for var in ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET"]:
                if not os.getenv(var):
                    missing_vars.append(var)
        elif auth_provider == "clerk":
            # Clerk requires secret and publishable keys
            for var in ["CLERK_SECRET_KEY", "CLERK_PUBLISHABLE_KEY"]:
                if not os.getenv(var):
                    missing_vars.append(var)
        
        if missing_vars:
            raise ConfigurationException(
                f"Missing required environment variables for auth provider '{auth_provider}': {', '.join(missing_vars)}. "
                f"Please check your .env file or environment configuration."
            )
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    def get_auth_provider_name(self) -> str:
        """Get configured auth provider name"""
        return self.auth_provider


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)"""
    return Settings()
