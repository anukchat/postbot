from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from src.backend.utils.logger import setup_logger
from src.backend.db.repositories import TemplateRepository
from src.backend.api.datamodel import TemplateResponse, TemplateCreate, TemplateUpdate
from src.backend.api.dependencies import get_current_user_profile
from datetime import datetime
from uuid import UUID

router = APIRouter( tags=["Templates"])
logger = setup_logger(__name__)
template_repository = TemplateRepository()

@router.get("/templates", response_model=List[TemplateResponse])
def list_templates(current_user: dict = Depends(get_current_user_profile)):
    """List all templates with their parameters for the authenticated user."""
    try:
        templates = template_repository.list_templates_for_profile(profile_id=UUID(current_user.profile_id))
        return templates
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    """Get a specific template by ID."""
    try:
        template = template_repository.get_template_with_parameters(template_id, UUID(current_user.profile_id))
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/templates", response_model=TemplateResponse)
def create_template(template: TemplateCreate, current_user: dict = Depends(get_current_user_profile)):
    """Create a new template."""
    try:
        template_data = template.dict()
        template_data["profile_id"] = current_user.profile_id
        parameters = template_data.pop("parameters", [])
        created = template_repository.create_template_with_parameters(template_data, parameters)
        return template_repository.get_template_with_parameters(created.template_id, UUID(current_user.profile_id))
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/templates/{template_id}", response_model=TemplateResponse)
def update_template(template_id: UUID, template: TemplateUpdate, current_user: dict = Depends(get_current_user_profile)):
    """Update an existing template."""
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
        return template_repository.get_template_with_parameters(template_id, UUID(current_user.profile_id))
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/templates/{template_id}")
def delete_template(template_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    """Soft delete a template."""
    try:
        result = template_repository.update_template_with_parameters(
            template_id=template_id,
            profile_id=UUID(current_user.profile_id),
            template_data={
                "is_deleted": True,
                "deleted_at": datetime.now()
            }
        )
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))