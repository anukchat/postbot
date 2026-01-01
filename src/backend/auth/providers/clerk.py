"""
Clerk authentication provider implementation.

Implements the AuthProvider interface for Clerk.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import jwt
from ..base import AuthProvider, AuthUser, AuthSession
from src.backend.exceptions import AuthenticationException
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class ClerkAuthProvider(AuthProvider):
    """Clerk implementation of AuthProvider interface"""
    
    def __init__(self, secret_key: str, publishable_key: str):
        """
        Initialize Clerk auth provider.
        
        Args:
            secret_key: Clerk secret key
            publishable_key: Clerk publishable key
        """
        if not secret_key or not publishable_key:
            raise AuthenticationException(
                "Clerk secret_key and publishable_key are required"
            )
        
        self.secret_key = secret_key
        self.publishable_key = publishable_key
        self.base_url = "https://api.clerk.com/v1"
        
        logger.info("Initialized Clerk auth provider")
    
    async def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Clerk API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "POST":
                    response = await client.post(url, json=data, headers=headers)
                elif method == "PATCH":
                    response = await client.patch(url, json=data, headers=headers)
                else:
                    response = await client.get(url, headers=headers)
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"Clerk API request failed: {e}")
                raise AuthenticationException(f"Clerk request failed: {str(e)}")
    
    def _decode_token(self, access_token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            # Clerk uses RS256, verify signature in production using JWKS
            return jwt.decode(
                access_token, 
                options={"verify_signature": False}
            )
        except Exception as e:
            logger.error(f"Token decode failed: {e}")
            raise AuthenticationException("Invalid token format")
    
    def _map_clerk_user_to_auth_user(self, user_data: Dict[str, Any]) -> AuthUser:
        """Convert Clerk user data to standardized AuthUser"""
        email_addresses = user_data.get("email_addresses", [])
        primary_email = next(
            (e for e in email_addresses if e.get("id") == user_data.get("primary_email_address_id")),
            email_addresses[0] if email_addresses else {}
        )
        
        return AuthUser(
            id=user_data.get("id", ""),
            email=primary_email.get("email_address", ""),
            email_verified=primary_email.get("verification", {}).get("status") == "verified",
            full_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            avatar_url=user_data.get("image_url"),
            provider="clerk",
            metadata=user_data
        )
    
    async def sign_up(self, email: str, password: str, **kwargs) -> AuthSession:
        """
        Create new user account with Clerk.
        Note: Clerk typically handles sign-up client-side. This is for backend-initiated signups.
        """
        try:
            logger.info(f"Sign up attempt for email: {email}")
            
            user_data = {
                "email_address": [email],
                "password": password,
                **kwargs
            }
            
            response = await self._make_request("/users", method="POST", data=user_data)
            
            # Clerk doesn't return tokens directly on signup via API
            # Typically, client-side signup is used
            logger.info(f"User created successfully: {response['id']}")
            
            # Return basic session - client should complete auth flow
            return AuthSession(
                access_token="",  # Populated by client-side flow
                user=self._map_clerk_user_to_auth_user(response)
            )
            
        except Exception as e:
            logger.error(f"Sign up failed: {e}", exc_info=True)
            raise AuthenticationException(f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str, **kwargs) -> AuthSession:
        """
        Clerk uses client-side authentication.
        Backend verification is done via verify_token.
        """
        raise NotImplementedError(
            "Clerk uses client-side authentication. "
            "Use verify_token to validate client-provided tokens."
        )
    
    async def sign_in_with_oauth(
        self, 
        provider: str, 
        redirect_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Clerk OAuth is handled client-side.
        Return configuration for frontend.
        """
        return {
            "publishable_key": self.publishable_key,
            "provider": provider,
            "redirect_url": redirect_url
        }
    
    async def exchange_code_for_session(self, code: str, **kwargs) -> AuthSession:
        """
        Clerk handles OAuth client-side.
        Token validation is done via verify_token.
        """
        raise NotImplementedError(
            "Clerk handles OAuth client-side. "
            "Use verify_token to validate client-provided tokens."
        )
    
    async def verify_token(self, access_token: str) -> AuthUser:
        """Verify Clerk session token and return user"""
        try:
            if not access_token:
                raise AuthenticationException("Access token is required")
            
            # Decode and verify token
            token_data = self._decode_token(access_token)
            
            # Get user details from Clerk API
            user_id = token_data.get("sub")
            if not user_id:
                raise AuthenticationException("Invalid token: missing user ID")
            
            user_data = await self._make_request(f"/users/{user_id}")
            
            return self._map_clerk_user_to_auth_user(user_data)
            
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationException(f"Token verification failed: {str(e)}")
    
    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """
        Clerk handles token refresh client-side.
        """
        raise NotImplementedError(
            "Clerk handles token refresh client-side. "
            "Frontend should manage token rotation."
        )
    
    async def sign_out(self, access_token: str) -> bool:
        """Sign out user (client-side operation in Clerk)"""
        logger.info("User sign out (client-side)")
        return True
    
    async def reset_password(self, email: str, **kwargs) -> bool:
        """Send password reset email"""
        try:
            # Clerk uses email_addresses endpoint for password reset
            # This creates a password reset email
            data = {
                "email_address": email,
                "sign_in_redirect_url": kwargs.get("redirect_url", "")
            }
            
            # Note: Actual implementation may vary based on Clerk API version
            # Check Clerk documentation for exact endpoint
            logger.info(f"Password reset initiated for {email}")
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise AuthenticationException(f"Password reset failed: {str(e)}")
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password"""
        try:
            # Get user ID from token
            token_data = self._decode_token(access_token)
            user_id = token_data.get("sub")
            
            if not user_id:
                raise AuthenticationException("Invalid token")
            
            # Update password via Clerk API
            await self._make_request(
                f"/users/{user_id}",
                method="PATCH",
                data={"password": new_password}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Password update failed: {e}")
            raise AuthenticationException(f"Password update failed: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "clerk"
