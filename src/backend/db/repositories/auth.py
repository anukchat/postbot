from typing import Dict, Optional, Any
from uuid import UUID
import os
from datetime import datetime, timedelta
from supabase import Client, create_client
from ..models import Profile
from ..sqlalchemy_repository import SQLAlchemyRepository

class AuthRepository(SQLAlchemyRepository[Profile]):
    def __init__(self):
        super().__init__(Profile)
        # Initialize Supabase client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user"""
        session = self.db.get_session()
        try:
            # Create user in Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Create profile in database
                profile = Profile(
                    user_id=response.user.id,
                    role='free',
                    generation_limit=10,
                    generations_used=0
                )
                session.add(profile)
                session.flush()
                session.commit()
            
            return response
        except Exception as e:
            session.rollback()
            raise ValueError(f"Sign up failed: {str(e)}")

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            raise ValueError(f"Sign in failed: {str(e)}")

    async def sign_out(self) -> Dict[str, Any]:
        """Sign out the current user"""
        try:
            return self.supabase.auth.sign_out()
        except Exception as e:
            raise ValueError(f"Sign out failed: {str(e)}")

    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the session using a refresh token"""
        try:
            response = self.supabase.auth.refresh_session({
                "refresh_token": refresh_token
            })
            return response
        except Exception as e:
            raise ValueError(f"Session refresh failed: {str(e)}")

    async def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token and refresh token"""
        try:
            if not access_token:
                raise ValueError("Both access_token and refresh_token are required")
            
            return self.supabase.auth.get_user(access_token)
        except Exception as e:
            raise ValueError(f"Failed to get user: {str(e)}")
            
    async def get_user_by_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Try to get user information using only the access token (fallback method)
        
        This is a fallback method that attempts to use just the access token.
        It may work for recently authenticated sessions, but will likely fail
        for older sessions that require refresh.
        """
        try:
            # Set the access token directly without refresh token
            self.supabase.auth._bearer_token = access_token
            return self.supabase.auth.get_user()
        except Exception as e:
            # Silently fail - this is a fallback method
            return None

    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            return self.supabase.auth.reset_password_email(email)
        except Exception as e:
            raise ValueError(f"Password reset failed: {str(e)}")

    async def update_password(self, new_password: str) -> Dict[str, Any]:
        """Update user password"""
        try:
            return self.supabase.auth.update_user({"password": new_password})
        except Exception as e:
            raise ValueError(f"Password update failed: {str(e)}")

    async def exchange_code_for_session(self, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for session"""
        try:
            return self.supabase.auth.exchange_code_for_session(code)
        except Exception as e:
            raise ValueError(f"Code exchange failed: {str(e)}")

    def verify_session(self, session: Dict[str, Any]) -> bool:
        """Verify if a session is valid"""
        try:
            expiry = datetime.fromisoformat(session['expires_at'])
            return expiry > datetime.now()
        except (KeyError, ValueError):
            return False