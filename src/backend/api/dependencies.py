from fastapi import HTTPException, Request, Security, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from cachetools import TTLCache
from uuid import UUID
from src.backend.agents.blogs import AgentWorkflow
from src.backend.api.datamodel import UserProfileResponse
from src.backend.db.repositories.auth import AuthRepository
from src.backend.db.repositories.profile import ProfileRepository
from typing import Optional


auth_cache = TTLCache(maxsize=100, ttl=6000)  # 6000 seconds = 100 minutes
security = HTTPBearer()

auth_repository = AuthRepository()
profile_repository = ProfileRepository()

# Agent Workflow Endpoint
def get_workflow() -> AgentWorkflow:
    """Dependency to get a AgentWorkflow instance."""
    return AgentWorkflow()


async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Security(security),
    request: Request = None,
    x_refresh_token: Optional[str] = Header(None)
):
    try:
        # Get access token from authorization header
        access_token = credentials.credentials
        
        # Try multiple options for refresh token:
        # 1. Check cookies
        refresh_token = request.cookies.get("refresh_token")
        
        # 2. Check header if cookie isn't available
        if not refresh_token and x_refresh_token:
            refresh_token = x_refresh_token
        
        if not refresh_token:
            # Try to recover session without refresh token
            try:
                user = await auth_repository.get_user_by_access_token(access_token)
                if user and user.user:
                    profile = profile_repository.get_profile_by_user_id(UUID(user.user.id))
                    if profile:
                        user_profile = UserProfileResponse(
                            id=user.user.id,
                            profile_id=str(profile.id),
                            role=profile.role,
                        )
                        return user_profile
            except Exception:
                pass
                
            # If recovery fails, raise the exception
            raise HTTPException(status_code=401, detail="Refresh token is required. Please log in again.")
        
        # Create a cache key based on both tokens
        cache_key = f"{access_token}:{refresh_token}"
        
        # Try to get user from cache first
        cached_user_data = auth_cache.get(cache_key)
        if cached_user_data:
            return cached_user_data
        
        # If not in cache, perform the API call
        user = await auth_repository.get_user(access_token, refresh_token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token or expired")

        # Get associated profile using user_id
        profile = profile_repository.get_profile_by_user_id(UUID(user.user.id))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_profile = UserProfileResponse(
            id=user.user.id,
            profile_id=str(profile.id),
            role=profile.role,
        )
        
        # Store in cache
        auth_cache[cache_key] = user_profile
        
        return user_profile
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
