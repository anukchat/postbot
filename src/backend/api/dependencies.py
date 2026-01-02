from fastapi import HTTPException, Request, Security, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from cachetools import TTLCache
from uuid import UUID
from src.backend.agents.blogs import AgentWorkflow
from src.backend.api.datamodel import UserProfileResponse
from src.backend.auth import get_auth_provider
from src.backend.db.repositories.profile import ProfileRepository
from src.backend.exceptions import AuthenticationException
from typing import Optional


auth_cache = TTLCache(maxsize=100, ttl=300)  # 300 seconds = 5 minutes
security = HTTPBearer()

# Get auth provider (configured via AUTH_PROVIDER env var)
auth_provider = get_auth_provider()
profile_repository = ProfileRepository()

# Agent Workflow Endpoint
def get_workflow() -> AgentWorkflow:
    """Dependency to get a AgentWorkflow instance."""
    return AgentWorkflow()


async def verify_auth_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Verify authentication token without requiring profile to exist.
    Used for profile sync endpoint where profile is being created.
    """
    from src.backend.utils.logger import setup_logger
    logger = setup_logger(__name__)
    
    try:
        access_token = credentials.credentials
        logger.info(f"[PROFILE_SYNC] Received token (first 30 chars): {access_token[:30]}... (length: {len(access_token)})")
        
        # Validate token with configured auth provider (Supabase/Auth0/Clerk)
        auth_user = await auth_provider.verify_token(access_token)
        
        if not auth_user:
            logger.warning("[PROFILE_SYNC] Token verification returned no user")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token or expired"
            )
        
        logger.info(f"[PROFILE_SYNC] Token verified successfully for user: {auth_user.id}")
        return {"id": auth_user.id, "email": auth_user.email}
        
    except AuthenticationException as e:
        logger.error(f"[PROFILE_SYNC] Authentication exception: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[PROFILE_SYNC] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again."
        )


async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    try:
        # Get access token from authorization header
        access_token = credentials.credentials

        # Check cache first
        if access_token in auth_cache:
            return auth_cache[access_token]

        # Validate token with configured auth provider (Supabase/Auth0/Clerk)
        auth_user = await auth_provider.verify_token(access_token)
        
        if not auth_user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid token or expired"
            )

        # Get associated profile from YOUR database
        profile = profile_repository.get_profile_by_user_id(UUID(auth_user.id))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_profile = UserProfileResponse(
            id=auth_user.id,
            profile_id=str(profile.id),
            role=profile.role,
        )
        
        # Store in cache
        auth_cache[access_token] = user_profile
                
        return user_profile
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        if "Invalid token or expired" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Session expired. Please log in again."
            )
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
