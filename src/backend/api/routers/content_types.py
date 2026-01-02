from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.backend.api.datamodel import ContentType, ContentTypeCreate, ContentTypeUpdate
from src.backend.db.repositories import ContentTypeRepository
from src.backend.api.dependencies import get_current_user_profile
from src.backend.exceptions import DatabaseException, ResourceNotFoundException
from src.backend.utils.logger import setup_logger
from uuid import UUID
from typing import Optional

logger = setup_logger(__name__)


router = APIRouter(tags=["Content Types"])

# ContentType Repository
content_type_repository = ContentTypeRepository()


@router.post("/content_types", response_model=ContentType)
async def create_content_type(content_type: ContentTypeCreate, current_user: dict = Depends(get_current_user_profile)):
    try:
        logger.info(f"Creating content type: {content_type.name}")
        result = content_type_repository.create(content_type.dict())
        return result
    except DatabaseException as e:
        logger.error(f"Database error creating content type: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Error creating content type: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/content_types/{content_type_id}", response_model=ContentType)
async def read_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    try:
        result = content_type_repository.find_by_field("content_type_id", content_type_id)
        if not result:
            raise ResourceNotFoundException(f"ContentType {content_type_id} not found")
        return result
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="ContentType not found")
    except DatabaseException as e:
        logger.error(f"Database error reading content type: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/content_types/{content_type_id}", response_model=ContentType)
async def update_content_type(content_type_id: UUID, content_type: ContentTypeUpdate, current_user: dict = Depends(get_current_user_profile)):
    try:
        logger.info(f"Updating content type {content_type_id}")
        result = content_type_repository.update(
            id_field="content_type_id",
            id_value=content_type_id,
            data=content_type.dict(exclude_unset=True)
        )
        return result
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="ContentType not found")
    except DatabaseException as e:
        logger.error(f"Database error updating content type: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/content_types/{content_type_id}")
async def delete_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    try:
        logger.info(f"Deleting content type {content_type_id}")
        result = content_type_repository.delete("content_type_id", content_type_id)
        if not result:
            raise ResourceNotFoundException(f"ContentType {content_type_id} not found")
        return {"message": "ContentType deleted"}
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="ContentType not found")
    except DatabaseException as e:
        logger.error(f"Database error deleting content type: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/content_types", response_model=List[ContentType])
async def filter_content_types(name: Optional[str] = None, skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user_profile)):
    try:
        query_filters = {}
        if name:
            query_filters["name"] = name
        result = content_type_repository.filter(query_filters, skip, limit)
        return result
    except DatabaseException as e:
        logger.error(f"Database error filtering content types: {e}")
        raise HTTPException(status_code=500, detail="Database error")
