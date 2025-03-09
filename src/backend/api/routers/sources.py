from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List,Optional
from src.backend.api.datamodel import Source, SourceCreate, SourceUpdate, SourceListResponse
from src.backend.db.repositories import SourceRepository
from src.backend.api.dependencies import get_current_user_profile
from src.backend.api.formatters import format_source_list_response
from uuid import UUID

router = APIRouter(tags=["Sources"])

# Source Repository
source_repository = SourceRepository()


@router.post("/sources", response_model=Source)
def create_source(source: SourceCreate, current_user: dict = Depends(get_current_user_profile)):
    """Create a new source"""
    try:
        result = source_repository.create_source(source.dict(), current_user.profile_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create source")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sources", response_model=SourceListResponse)
def filter_sources(
    type: Optional[str] = None, 
    source_identifier: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: dict = Depends(get_current_user_profile)
):
    result = source_repository.list_sources_with_related(
        profile_id=current_user.profile_id,
        type=type,
        source_identifier=source_identifier,
        skip=skip,
        limit=limit
    )
    return result

@router.get("/sources/{source_id}", response_model=Source)
def read_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.find_by_field("source_id", source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@router.put("/sources/{source_id}", response_model=Source)
def update_source(source_id: UUID, source: SourceUpdate, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.update(
        id_field="source_id",
        id_value=source_id,
        data=source.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@router.delete("/sources/{source_id}")
def delete_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.soft_delete(source_id, current_user.profile_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted"}


@router.get("/sources/list", response_model=SourceListResponse, tags=["sources"])
async def list_sources(
    skip: int = 0,
    limit: int = 10,
    type: Optional[str] = None,
    source_identifier: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        result = source_repository.list_sources_with_related(
            UUID(current_user.profile_id),
            type,
            source_identifier,
            skip,
            limit
        )
        return format_source_list_response(
            items=result,
            total=len(result),
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
