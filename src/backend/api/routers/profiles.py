from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from src.backend.api.datamodel import Profile
from src.backend.api.dependencies import get_current_user_profile, verify_auth_token
from src.backend.db.repositories import ProfileRepository
from src.backend.exceptions import DatabaseException, ResourceNotFoundException, AuthorizationException
from src.backend.utils.logger import setup_logger
import uuid
from uuid import UUID
from typing import Dict, Any
from pydantic import BaseModel

logger = setup_logger(__name__)

router = APIRouter( tags=["Profiles"])

# Profile Repository
profile_repository = ProfileRepository()

# Request Models
class ProfileCreateRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
class ProfileSyncRequest(BaseModel):
    """Request model for syncing user profile from OAuth provider to application database"""
    user_id: str  # OAuth provider user ID (from Supabase/Auth0/Clerk)
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "google"  # OAuth provider used (google, github, etc.)

# OAuth Callback Endpoint - Creates or gets profile for authenticated user
@router.post("/profiles/sync", response_model=Profile)
async def sync_profile(
    profile_data: ProfileSyncRequest,
    current_user: Dict = Depends(verify_auth_token)
):
    """
    Sync user profile from OAuth provider (Supabase/Auth0/Clerk) to application database.
    
    This endpoint enables database flexibility - users can use ANY PostgreSQL database
    while keeping their chosen OAuth provider for authentication only.
    
    Flow:
    1. User authenticates with OAuth provider (Supabase/Auth0/Clerk)
    2. Frontend receives user data and auth token
    3. Frontend calls this endpoint with user data
    4. Backend creates/updates profile in YOUR PostgreSQL database
    
    Args:
        profile_data: User information from OAuth provider
        current_user: Authenticated user from JWT token
        
    Returns:
        Created or updated profile
        
    Raises:
        AuthorizationException: If user_id doesn't match authenticated user
        DatabaseException: If database operation fails
    """
    try:
        # Verify the authenticated user matches the profile being synced
        if current_user["id"] != profile_data.user_id:
            raise AuthorizationException("Cannot sync profile for different user")
        
        logger.info(f"Syncing profile for user {profile_data.user_id} from {profile_data.provider}")
        
        # Check if profile already exists
        existing_profile = profile_repository.find_by_field("user_id", profile_data.user_id)
        
        if existing_profile:
            logger.info(f"Profile exists for user {profile_data.user_id}, updating if needed")
            # Update profile with latest data from auth provider
            update_data = {}
            if profile_data.email != existing_profile.email:
                update_data["email"] = profile_data.email
            if profile_data.full_name and profile_data.full_name != existing_profile.full_name:
                update_data["full_name"] = profile_data.full_name
            if profile_data.avatar_url and profile_data.avatar_url != existing_profile.avatar_url:
                update_data["avatar_url"] = profile_data.avatar_url
            
            if update_data:
                logger.info(f"Updating profile {existing_profile.id} with: {update_data.keys()}")
                updated_profile = profile_repository.update("id", existing_profile.id, update_data)
                return updated_profile
            else:
                logger.info(f"Profile {existing_profile.id} is up to date")
                return existing_profile
        else:
            # Create new profile
            logger.info(f"Creating new profile for user {profile_data.user_id}")
            new_profile = profile_repository.create({
                "id": uuid.uuid4(),
                "user_id": profile_data.user_id,
                "email": profile_data.email,
                "full_name": profile_data.full_name,
                "avatar_url": profile_data.avatar_url,
                "role": "free",
                "subscription_status": "none",
                "generations_used": 0,
                "preferences": {},
                "is_deleted": False
            })
            logger.info(f"Profile created successfully: {new_profile.id}")
            return new_profile
            
    except AuthorizationException as e:
        logger.error(f"Authorization error syncing profile: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except DatabaseException as e:
        logger.error(f"Database error syncing profile: {e}")
        raise HTTPException(status_code=500, detail="Database error creating/updating profile")
    except Exception as e:
        logger.error(f"Unexpected error syncing profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Profile Endpoints
@router.get("/profiles/check")
async def check_profile_exists(email: str):
    """
    Check if a profile exists for the given email.
    
    Args:
        email: Email address to check
        
    Returns:
        {"exists": true/false}
    """
    try:
        logger.info(f"Checking if profile exists for email: {email}")
        profile = profile_repository.get_by_email(email)
        exists = profile is not None
        logger.info(f"Profile exists check result: {exists}")
        return {"exists": exists}
    except ResourceNotFoundException:
        return {"exists": False}
    except Exception as e:
        logger.error(f"Error checking profile existence: {e}", exc_info=True)
        return {"exists": False}

@router.post("/profiles", response_model=Profile)
async def create_profile(
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        logger.info(f"Creating profile for user {current_user.id}")
        # Create profile with both id and user_id
        profile = profile_repository.create({
            **profile_data,
            "id": uuid.uuid4(),  # Generate new profile ID
            "user_id": current_user.id  # Set user_id from auth
        })
        logger.info(f"Profile created successfully: {profile.id}")
        return profile
    except DatabaseException as e:
        logger.error(f"Database error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error creating profile: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Profile {profile_id} not found")
        if profile.user_id != current_user.id:
            logger.warning(f"Unauthorized access attempt to profile {profile_id} by user {current_user.id}")
            raise AuthorizationException("Not authorized to access this profile")
        return profile
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Profile not found")
    except AuthorizationException:
        raise HTTPException(status_code=403, detail="Not authorized")
    except DatabaseException as e:
        logger.error(f"Database error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error fetching profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: UUID,
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Profile {profile_id} not found")
        if profile.user_id != current_user.id:
            logger.warning(f"Unauthorized update attempt on profile {profile_id} by user {current_user.id}")
            raise AuthorizationException("Not authorized to update this profile")
        
        logger.info(f"Updating profile {profile_id}")
        updated_profile = profile_repository.update("id", profile_id, profile_data)
        return updated_profile
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Profile not found")
    except AuthorizationException:
        raise HTTPException(status_code=403, detail="Not authorized")
    except DatabaseException as e:
        logger.error(f"Database error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile:
            raise ResourceNotFoundException(f"Profile {profile_id} not found")
        if profile.user_id != current_user.id:
            logger.warning(f"Unauthorized delete attempt on profile {profile_id} by user {current_user.id}")
            raise AuthorizationException("Not authorized to delete this profile")
        
        logger.info(f"Soft deleting profile {profile_id}")
        profile_repository.soft_delete("id", profile_id)
        return {"message": "Profile deleted successfully"}
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Profile not found")
    except AuthorizationException:
        raise HTTPException(status_code=403, detail="Not authorized")
    except DatabaseException as e:
        logger.error(f"Database error deleting profile: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error deleting profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/profiles", response_model=List[Profile])
async def list_profiles(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user_profile)
):
    try:
        logger.debug(f"Listing profiles for user {current_user.id}")
        profiles = profile_repository.filter({"id": current_user.profile_id}, skip, limit)
        return profiles
    except DatabaseException as e:
        logger.error(f"Database error listing profiles: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error listing profiles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
