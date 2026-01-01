"""
Auth0 authentication provider implementation.

Implements the AuthProvider interface for Auth0.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import jwt
from ..base import AuthProvider, AuthUser, AuthSession
from src.backend.exceptions import AuthenticationException
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class Auth0AuthProvider(AuthProvider):
    """Auth0 implementation of AuthProvider interface"""
    
    def __init__(
        self, 
        domain: str, 
        client_id: str, 
        client_secret: str,
        audience: Optional[str] = None
    ):
        """
        Initialize Auth0 auth provider.
        
        Args:
            domain: Auth0 domain (e.g., your-tenant.auth0.com)
            client_id: Auth0 application client ID
            client_secret: Auth0 application client secret
            audience: Auth0 API audience identifier
        """
        if not domain or not client_id or not client_secret:
            raise AuthenticationException(
                "Auth0 domain, client_id, and client_secret are required"
            )
        
        self.domain = domain.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience or f"https://{domain}/api/v2/"
        
        logger.info("Initialized Auth0 auth provider")
    
    async def _make_request(
        self, 
        endpoint: str, 
        method: str = "POST", 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Auth0 API"""
        url = f"https://{self.domain}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "POST":
                    response = await client.post(url, json=data, headers=headers)
                else:
                    response = await client.get(url, headers=headers)
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"Auth0 API request failed: {e}")
                raise AuthenticationException(f"Auth0 request failed: {str(e)}")
    
    def _decode_token(self, access_token: str) -> Dict[str, Any]:
        """Decode JWT token without verification (for user data extraction)"""
        try:
            # Note: In production, you should verify the token signature
            # using Auth0's public keys (JWKS)
            return jwt.decode(
                access_token, 
                options={"verify_signature": False}
            )
        except Exception as e:
            logger.error(f"Token decode failed: {e}")
            raise AuthenticationException("Invalid token format")
    
    def _map_auth0_user_to_auth_user(self, user_data: Dict[str, Any]) -> AuthUser:
        """Convert Auth0 user data to standardized AuthUser"""
        return AuthUser(
            id=user_data.get("sub", ""),
            email=user_data.get("email", ""),
            email_verified=user_data.get("email_verified", False),
            full_name=user_data.get("name"),
            avatar_url=user_data.get("picture"),
            provider=user_data.get("sub", "").split("|")[0] if "|" in user_data.get("sub", "") else "auth0",
            metadata=user_data
        )
    
    async def sign_up(self, email: str, password: str, **kwargs) -> AuthSession:
        """Create new user account with Auth0"""
        try:
            logger.info(f"Sign up attempt for email: {email}")
            
            # Create user via Auth0 Management API
            signup_data = {
                "client_id": self.client_id,
                "email": email,
                "password": password,
                "connection": "Username-Password-Authentication",
                **kwargs
            }
            
            response = await self._make_request("/dbconnections/signup", data=signup_data)
            
            # After signup, sign in to get tokens
            return await self.sign_in(email, password)
            
        except Exception as e:
            logger.error(f"Sign up failed: {e}", exc_info=True)
            raise AuthenticationException(f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str, **kwargs) -> AuthSession:
        """Authenticate user with email/password"""
        try:
            logger.info(f"Sign in attempt for email: {email}")
            
            auth_data = {
                "grant_type": "password",
                "username": email,
                "password": password,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
                "scope": "openid profile email"
            }
            
            response = await self._make_request("/oauth/token", data=auth_data)
            
            # Decode token to get user info
            user_data = self._decode_token(response["access_token"])
            
            logger.info(f"Sign in successful for email: {email}")
            
            return AuthSession(
                access_token=response["access_token"],
                refresh_token=response.get("refresh_token"),
                token_type=response.get("token_type", "Bearer"),
                expires_at=datetime.fromtimestamp(user_data["exp"]) if "exp" in user_data else None,
                user=self._map_auth0_user_to_auth_user(user_data)
            )
            
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
        # Auth0 uses "authorize" endpoint for OAuth
        auth_url = (
            f"https://{self.domain}/authorize?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={redirect_url}&"
            f"scope=openid profile email&"
            f"connection={provider}"
        )
        
        return {
            "url": auth_url,
            "provider": provider
        }
    
    async def exchange_code_for_session(self, code: str, **kwargs) -> AuthSession:
        """Exchange OAuth code for session"""
        try:
            logger.debug("Exchanging OAuth code for session")
            
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": kwargs.get("redirect_uri", "")
            }
            
            response = await self._make_request("/oauth/token", data=token_data)
            
            # Decode token to get user info
            user_data = self._decode_token(response["access_token"])
            
            return AuthSession(
                access_token=response["access_token"],
                refresh_token=response.get("refresh_token"),
                token_type=response.get("token_type", "Bearer"),
                expires_at=datetime.fromtimestamp(user_data["exp"]) if "exp" in user_data else None,
                user=self._map_auth0_user_to_auth_user(user_data)
            )
            
        except Exception as e:
            logger.error(f"Code exchange failed: {e}")
            raise AuthenticationException(f"Code exchange failed: {str(e)}")
    
    async def verify_token(self, access_token: str) -> AuthUser:
        """Verify access token and return user"""
        try:
            if not access_token:
                raise AuthenticationException("Access token is required")
            
            # In production, verify token signature using Auth0's JWKS
            # For now, decode without verification
            user_data = self._decode_token(access_token)
            
            # Check expiration
            if "exp" in user_data:
                exp_time = datetime.fromtimestamp(user_data["exp"])
                if exp_time < datetime.now():
                    raise AuthenticationException("Token expired")
            
            return self._map_auth0_user_to_auth_user(user_data)
            
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationException(f"Token verification failed: {str(e)}")
    
    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """Refresh expired access token"""
        try:
            logger.debug("Refreshing session")
            
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token
            }
            
            response = await self._make_request("/oauth/token", data=refresh_data)
            
            # Decode token to get user info
            user_data = self._decode_token(response["access_token"])
            
            return AuthSession(
                access_token=response["access_token"],
                refresh_token=response.get("refresh_token"),
                token_type=response.get("token_type", "Bearer"),
                expires_at=datetime.fromtimestamp(user_data["exp"]) if "exp" in user_data else None,
                user=self._map_auth0_user_to_auth_user(user_data)
            )
            
        except Exception as e:
            logger.error(f"Session refresh failed: {e}")
            raise AuthenticationException(f"Session refresh failed: {str(e)}")
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user (Auth0 doesn't have server-side logout for tokens)"""
        # Auth0 tokens are stateless, so we just return True
        # Client should discard the tokens
        logger.info("User sign out (client-side)")
        return True
    
    async def reset_password(self, email: str, **kwargs) -> bool:
        """Send password reset email"""
        try:
            reset_data = {
                "client_id": self.client_id,
                "email": email,
                "connection": "Username-Password-Authentication"
            }
            
            await self._make_request("/dbconnections/change_password", data=reset_data)
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise AuthenticationException(f"Password reset failed: {str(e)}")
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password (requires Management API)"""
        # This requires Auth0 Management API access
        # Implementation would involve getting Management API token first
        raise NotImplementedError(
            "Password update requires Auth0 Management API. "
            "Use reset_password instead."
        )
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "auth0"
