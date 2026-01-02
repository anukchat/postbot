from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List,Optional
from src.backend.api.datamodel import Source, SourceCreate, SourceUpdate, SourceListResponse
from src.backend.db.repositories import SourceRepository
from src.backend.api.dependencies import get_current_user_profile
from src.backend.api.formatters import format_source_list_response
from src.backend.exceptions import DatabaseException, ResourceNotFoundException
from src.backend.utils.logger import setup_logger
from uuid import UUID

logger = setup_logger(__name__)

router = APIRouter(tags=["Sources"])

# Source Repository
source_repository = SourceRepository()


@router.post("/sources", response_model=Source)
async def create_source(source: SourceCreate, current_user: dict = Depends(get_current_user_profile)):
    """Create a new source"""
    try:
        logger.info(f"Creating source for profile {current_user.profile_id}")
        result = source_repository.create_source(source.dict(), current_user.profile_id)
        return result
    except DatabaseException as e:
        logger.error(f"Database error creating source: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Error creating source: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sources", response_model=SourceListResponse)
async def filter_sources(
    type: Optional[str] = None, 
    source_identifier: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: dict = Depends(get_current_user_profile)
):
    try:
        result = source_repository.list_sources_with_related(
            profile_id=current_user.profile_id,
            type=type,
            source_identifier=source_identifier,
            skip=skip,
            limit=limit
        )
        return result
    except DatabaseException as e:
        logger.error(f"Database error filtering sources: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/sources/{source_id}", response_model=Source)
async def read_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    try:
        result = source_repository.find_by_field("source_id", source_id)
        if not result:
            raise ResourceNotFoundException(f"Source {source_id} not found")
        return result
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Source not found")
    except DatabaseException as e:
        logger.error(f"Database error reading source: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/sources/{source_id}", response_model=Source)
async def update_source(source_id: UUID, source: SourceUpdate, current_user: dict = Depends(get_current_user_profile)):
    try:
        logger.info(f"Updating source {source_id}")
        result = source_repository.update(
            id_field="source_id",
            id_value=source_id,
            data=source.dict(exclude_unset=True)
        )
        return result
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Source not found")
    except DatabaseException as e:
        logger.error(f"Database error updating source: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/sources/{source_id}")
async def delete_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    try:
        logger.info(f"Deleting source {source_id}")
        result = source_repository.soft_delete(source_id, current_user.profile_id)
        if not result:
            raise ResourceNotFoundException(f"Source {source_id} not found")
        return {"message": "Source deleted"}
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Source not found")
    except DatabaseException as e:
        logger.error(f"Database error deleting source: {e}")
        raise HTTPException(status_code=500, detail="Database error")
