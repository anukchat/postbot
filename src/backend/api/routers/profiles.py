from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.backend.api.datamodel import Profile
from src.backend.api.dependencies import get_current_user_profile
from src.backend.db.repositories import ProfileRepository
import uuid
from uuid import UUID
from typing import Dict, Any

router = APIRouter( tags=["Profiles"])

# Profile Repository
profile_repository = ProfileRepository()

# Profile Endpoints
@router.post("/profiles", response_model=Profile)
async def create_profile(
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Create profile with both id and user_id
        return profile_repository.create({
            **profile_data,
            "id": uuid.uuid4(),  # Generate new profile ID
            "user_id": current_user.id  # Set user_id from auth
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: UUID,
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile_repository.update("id", profile_id, profile_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile_repository.soft_delete("id", profile_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profiles", response_model=List[Profile])
async def list_profiles(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user_profile)
):
    try:
        return profile_repository.filter({"id": current_user.profile_id}, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
