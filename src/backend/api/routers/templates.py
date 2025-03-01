from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.backend.utils.logger import setup_logger
from src.backend.db.repositories import TemplateRepository
from src.backend.api.formatters import format_template_response
from src.backend.api.datamodel import TemplateCreate, TemplateResponse, TemplateUpdate, TemplateFilter, AdvancedTemplateFilter
from src.backend.api.dependencies import get_current_user_profile
from fastapi import Body
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

router = APIRouter(prefix="/templates", tags=["Templates"])

logger = setup_logger(__name__)

# Initialize repositories
template_repository = TemplateRepository()


#Templates endpoints
@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template_data = template.dict()
        template_data["profile_id"] = current_user.profile_id
        parameters = template_data.pop("parameters", [])
        return template_repository.create_template_with_parameters(template_data, parameters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template = template_repository.get_template_with_parameters(template_id, UUID(current_user.profile_id))
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return format_template_response(template)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template: TemplateUpdate,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template_data = template.dict(exclude_unset=True)
        parameters = template_data.pop("parameters", None)
        updated = template_repository.update_template_with_parameters(
            template_id,
            UUID(current_user.profile_id),
            template_data,
            parameters
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TemplateResponse]) 
def list_templates(
    skip: int = 0, 
    limit: int = 10, 
    template_type: Optional[str] = None,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """List all templates for the authenticated user."""
    try:
        templates = template_repository.list_templates_for_profile(
            profile_id=UUID(current_user.profile_id),
            skip=skip,
            limit=limit,
            template_type=template_type,
            include_deleted=include_deleted
        )
        return templates
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: UUID,
    new_name: str = Body(...),
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        duplicated = template_repository.duplicate_template(
            template_id,
            UUID(current_user.profile_id),
            new_name
        )
        if not duplicated:
            raise HTTPException(status_code=404, detail="Template not found")
        return duplicated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/filter", response_model=List[TemplateResponse])
def filter_templates(
    filters: TemplateFilter,
    skip: int = 0,
    limit: int = 10,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates based on parameters."""
    try:
        return template_repository.filter_templates(
            UUID(current_user.profile_id),
            filters.dict(exclude_unset=True),
            filters.template_type,
            include_deleted,
            skip,
            limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{template_id}")
def delete_template(template_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    """Soft delete a template by ID."""
    try:
        result = template_repository.update_template_with_parameters(
            template_id=template_id,
            profile_id=current_user.profile_id,
            template_data={
                "updated_at": datetime.now().isoformat(),
                "is_deleted": True,
                "deleted_at": datetime.now().isoformat()
            }
        )
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/filter", response_model=List[TemplateResponse],)
def filter_templates(
    filter: TemplateFilter, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates based on parameters."""
    try:
        results = template_repository.list_templates_for_profile(
            profile_id=current_user.profile_id,
            skip=skip,
            limit=limit,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted or False
        )
        return [template_repository.get_template_with_parameters(UUID(t["template_id"]), UUID(current_user.profile_id)) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/advanced-filter", response_model=List[TemplateResponse],)
def advanced_filter_templates(
    filter: AdvancedTemplateFilter,
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates by multiple parameters."""
    try:
        results = template_repository.filter_templates(
            profile_id=current_user.profile_id,
            parameters=filter.parameters,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted,
            skip=skip,
            limit=limit
        )
        return [template_repository.get_template_with_parameters(UUID(t["template_id"]), UUID(current_user.profile_id)) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/count", response_model=Dict[str, int], tags=["templates"])
def count_templates(
    template_type: Optional[str] = None,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get count of templates for the current user."""
    try:
        count = template_repository.count_templates(
            profile_id=current_user.profile_id,
            template_type=template_type,
            include_deleted=include_deleted
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))