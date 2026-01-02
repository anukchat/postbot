"""
Abstract base class for authentication providers.

Defines the interface that all auth providers must implement, enabling
easy switching between Supabase, Auth0, Clerk, or custom providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthUser:
    """Standardized user representation across all auth providers"""
    id: str
    email: str
    email_verified: bool = False
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "email"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AuthSession:
    """Standardized session representation across all auth providers"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    user: Optional[AuthUser] = None


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.
    
    All auth providers (Supabase, Auth0, Clerk, etc.) must implement this interface.
    This ensures the application can switch providers without changing business logic.
    """
    
    @abstractmethod
    async def sign_up(self, email: str, password: str, **kwargs) -> AuthSession:
        """
        Create a new user account.
        
        Args:
            email: User's email address
            password: User's password
            **kwargs: Provider-specific options
            
        Returns:
            AuthSession with user data and tokens
            
        Raises:
            AuthenticationException: If sign up fails
        """
        pass
    
    @abstractmethod
    async def sign_in(self, email: str, password: str, **kwargs) -> AuthSession:
        """
        Authenticate existing user with email/password.
        
        Args:
            email: User's email address
            password: User's password
            **kwargs: Provider-specific options
            
        Returns:
            AuthSession with user data and tokens
            
        Raises:
            AuthenticationException: If authentication fails
        """
        pass
    
    @abstractmethod
    async def sign_in_with_oauth(
        self, 
        provider: str, 
        redirect_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initiate OAuth sign-in flow.
        
        Args:
            provider: OAuth provider name (google, github, etc.)
            redirect_url: URL to redirect after authentication
            **kwargs: Provider-specific options
            
        Returns:
            Dict with authorization URL and state
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_session(self, code: str, **kwargs) -> AuthSession:
        """
        Exchange OAuth authorization code for session tokens.
        
        Args:
            code: OAuth authorization code
            **kwargs: Provider-specific options
            
        Returns:
            AuthSession with user data and tokens
            
        Raises:
            AuthenticationException: If code exchange fails
        """
        pass
    
    @abstractmethod
    async def verify_token(self, access_token: str) -> AuthUser:
        """
        Verify access token and return user information.
        
        Args:
            access_token: JWT access token
            
        Returns:
            AuthUser with validated user data
            
        Raises:
            AuthenticationException: If token is invalid or expired
        """
        pass
    
    @abstractmethod
    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """
        Refresh expired access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            AuthSession with new tokens
            
        Raises:
            AuthenticationException: If refresh fails
        """
        pass
    
    @abstractmethod
    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out user and invalidate tokens.
        
        Args:
            access_token: Current access token
            
        Returns:
            True if sign out successful
        """
        pass
    
    @abstractmethod
    async def reset_password(self, email: str, **kwargs) -> bool:
        """
        Send password reset email to user.
        
        Args:
            email: User's email address
            **kwargs: Provider-specific options (redirect_url, etc.)
            
        Returns:
            True if email sent successfully
        """
        pass
    
    @abstractmethod
    async def update_password(
        self, 
        access_token: str, 
        new_password: str
    ) -> bool:
        """
        Update user's password.
        
        Args:
            access_token: Current valid access token
            new_password: New password
            
        Returns:
            True if password updated successfully
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this auth provider.
        
        Returns:
            Provider name (supabase, auth0, clerk, etc.)
        """
        pass
