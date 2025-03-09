from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.backend.api.datamodel import ContentType, ContentTypeCreate, ContentTypeUpdate
from src.backend.db.repositories import ContentTypeRepository
from src.backend.api.dependencies import get_current_user_profile
from uuid import UUID
from typing import Optional


router = APIRouter(tags=["Content Types"])

# ContentType Repository
content_type_repository = ContentTypeRepository()


@router.post("/content_types", response_model=ContentType)
def create_content_type(content_type: ContentTypeCreate, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.create(content_type.dict())
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create content type")
    return result

@router.get("/content_types/{content_type_id}", response_model=ContentType)
def read_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.find_by_field("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@router.put("/content_types/{content_type_id}", response_model=ContentType)
def update_content_type(content_type_id: UUID, content_type: ContentTypeUpdate, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.update(
        id_field="content_type_id",
        id_value=content_type_id,
        data=content_type.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@router.delete("/content_types/{content_type_id}")
def delete_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.delete("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return {"message": "ContentType deleted"}

@router.get("/content_types", response_model=List[ContentType])
def filter_content_types(name: Optional[str] = None, skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user_profile)):
    query_filters = {}
    if name:
        query_filters["name"] = name
    result = content_type_repository.filter(query_filters, skip, limit)
    return result
