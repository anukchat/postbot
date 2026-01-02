"""
Supabase authentication provider implementation.

Implements the AuthProvider interface for Supabase Auth.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from supabase import Client, create_client
from ..base import AuthProvider, AuthUser, AuthSession
from src.backend.exceptions import AuthenticationException
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseAuthProvider(AuthProvider):
    """Supabase implementation of AuthProvider interface"""
    
    def __init__(self, url: str, key: str):
        """
        Initialize Supabase auth provider.
        
        Args:
            url: Supabase project URL
            key: Supabase anon/service role key
        """
        if not url or not key:
            raise AuthenticationException(
                "Supabase URL and key are required for Supabase auth provider"
            )
        
        self.client: Client = create_client(url, key)
        logger.info("Initialized Supabase auth provider")
    
    def _map_supabase_user_to_auth_user(self, supabase_user: Any) -> AuthUser:
        """Convert Supabase user object to standardized AuthUser"""
        return AuthUser(
            id=supabase_user.id,
            email=supabase_user.email or "",
            email_verified=supabase_user.email_confirmed_at is not None,
            full_name=supabase_user.user_metadata.get("full_name"),
            avatar_url=supabase_user.user_metadata.get("avatar_url"),
            provider=supabase_user.app_metadata.get("provider", "email"),
            metadata={
                "user_metadata": supabase_user.user_metadata,
                "app_metadata": supabase_user.app_metadata
            }
        )
    
    def _map_supabase_session(self, session: Any) -> AuthSession:
        """Convert Supabase session to standardized AuthSession"""
        return AuthSession(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type=session.token_type or "bearer",
            expires_at=datetime.fromtimestamp(session.expires_at) if session.expires_at else None,
            user=self._map_supabase_user_to_auth_user(session.user) if session.user else None
        )
    
    async def sign_up(self, email: str, password: str, **kwargs) -> AuthSession:
        """Create new user account with Supabase"""
        try:
            logger.info(f"Sign up attempt for email: {email}")
            
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": kwargs.get("options", {})
            })
            
            if not response.session:
                raise AuthenticationException("Sign up failed: No session returned")
            
            logger.info(f"User registered successfully: {response.user.id}")
            return self._map_supabase_session(response.session)
            
        except Exception as e:
            logger.error(f"Sign up failed: {e}", exc_info=True)
            raise AuthenticationException(f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str, **kwargs) -> AuthSession:
        """Authenticate user with email/password"""
        try:
            logger.info(f"Sign in attempt for email: {email}")
            
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.session:
                raise AuthenticationException("Sign in failed: No session returned")
            
            logger.info(f"Sign in successful for email: {email}")
            return self._map_supabase_session(response.session)
            
        except Exception as e:
            logger.error(f"Sign in failed for {email}: {e}")
            raise AuthenticationException(f"Sign in failed: {str(e)}")
    
    async def sign_in_with_oauth(
        self, 
        provider: str, 
        redirect_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Initiate OAuth sign-in flow"""
        try:
            logger.info(f"OAuth sign-in initiated: provider={provider}")
            
            response = self.client.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": redirect_url,
                    **kwargs.get("options", {})
                }
            })
            
            return {
                "url": response.url,
                "provider": provider
            }
            
        except Exception as e:
            logger.error(f"OAuth sign-in failed: {e}")
            raise AuthenticationException(f"OAuth sign-in failed: {str(e)}")
    
    async def exchange_code_for_session(self, code: str, **kwargs) -> AuthSession:
        """Exchange OAuth code for session"""
        try:
            logger.debug("Exchanging OAuth code for session")
            
            response = self.client.auth.exchange_code_for_session(code)
            
            if not response.session:
                raise AuthenticationException("Code exchange failed: No session returned")
            
            return self._map_supabase_session(response.session)
            
        except Exception as e:
            logger.error(f"Code exchange failed: {e}")
            raise AuthenticationException(f"Code exchange failed: {str(e)}")
    
    async def verify_token(self, access_token: str) -> AuthUser:
        """Verify access token and return user"""
        try:
            if not access_token:
                raise AuthenticationException("Access token is required")
            
            response = self.client.auth.get_user(access_token)
            
            if not response.user:
                raise AuthenticationException("Invalid or expired token")
            
            return self._map_supabase_user_to_auth_user(response.user)
            
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationException(f"Token verification failed: {str(e)}")
    
    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """Refresh expired access token"""
        try:
            logger.debug("Refreshing session")
            
            response = self.client.auth.refresh_session({
                "refresh_token": refresh_token
            })
            
            if not response.session:
                raise AuthenticationException("Session refresh failed: No session returned")
            
            return self._map_supabase_session(response.session)
            
        except Exception as e:
            logger.error(f"Session refresh failed: {e}")
            raise AuthenticationException(f"Session refresh failed: {str(e)}")
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user"""
        try:
            logger.info("User sign out")
            self.client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Sign out failed: {e}")
            return False
    
    async def reset_password(self, email: str, **kwargs) -> bool:
        """Send password reset email"""
        try:
            self.client.auth.reset_password_email(
                email,
                options=kwargs.get("options", {})
            )
            return True
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise AuthenticationException(f"Password reset failed: {str(e)}")
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password"""
        try:
            # Set the token first
            self.client.auth._bearer_token = access_token
            self.client.auth.update_user({"password": new_password})
            return True
        except Exception as e:
            logger.error(f"Password update failed: {e}")
            raise AuthenticationException(f"Password update failed: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "supabase"
