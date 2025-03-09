from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.backend.api.formatters import format_parameter_value
from src.backend.db.repositories import template
from src.backend.api.datamodel import ParameterModel, ParameterValueModel, TemplateParameter, SourceListResponse, TemplateParameterValue, TemplateResponse
from src.backend.db.repositories import ParameterRepository, SourceRepository
from src.backend.api.dependencies import get_current_user_profile
from uuid import UUID
from fastapi import Body
from typing import Optional, Dict, Any

router = APIRouter(tags=["Parameters"])

# Initialize repositories
parameter_repository = ParameterRepository()
source_repository = SourceRepository()


@router.get("/parameters/all", response_model=List[ParameterModel])
def get_all_parameters_with_values(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get all parameters with their values."""
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        if not parameters:
            return []
        # Convert raw parameters into ParameterWithValues schema
        formatted_parameters = []
        for param in parameters:
            formatted_param = ParameterModel(
                parameter_id=str(param.parameter_id),
                name=param.name,
                display_name=param.display_name,
                description=param.description,
                is_required=param.is_required,
                created_at=param.created_at,
                values=[
                    ParameterValueModel(
                        value_id=str(value.value_id),
                        value=value.value, 
                        display_order=value.display_order,
                        created_at=value.created_at
                    )
                    for value in param.values
                ]
            )
            formatted_parameters.append(formatted_param)
        return formatted_parameters
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/parameters/{parameter_id}", response_model=ParameterModel)
def get_parameter(
    parameter_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get a parameter by ID."""
    try:
        result = parameter_repository.get_parameter_with_values(parameter_id)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/parameters/{parameter_id}/values", response_model=List[ParameterValueModel])
async def get_parameter_values(
    parameter_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        values = parameter_repository.get_parameter_values(parameter_id)
        return [ParameterValueModel(value_id=str(value.value_id),value=value.value,display_order=value.display_order,created_at=value.created_at) for value in values]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameter management endpoints
@router.post("/parameters", response_model=ParameterModel)
def create_parameter(
    name: str = Body(...),
    display_name: str = Body(...),
    description: Optional[str] = Body(None),
    is_required: bool = Body(True),
    current_user: dict = Depends(get_current_user_profile),
):
    """Create a new parameter."""
    try:
        result = parameter_repository.create_parameter({
            "name": name,
            "display_name": display_name,
            "description": description,
            "is_required": is_required
        })
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create parameter")
        return ParameterModel(
            parameter_id=result.parameter_id,
            name=result.name,
            display_name=result.display_name,
            description=result.description,
            is_required=result.is_required,
            created_at=result.created_at,
            values=[ParameterValueModel(
                value_id=value.value_id,
                value=value.value,
                display_order=value.display_order,
                created_at=value.created_at
            ) for value in result.values
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/parameters/{parameter_id}", response_model=ParameterModel)
def update_parameter(
    parameter_id: UUID,
    name: Optional[str] = Body(None),
    display_name: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    is_required: Optional[bool] = Body(None),
    current_user: dict = Depends(get_current_user_profile)
):
    """Update a parameter."""
    try:
        update_data = {k: v for k, v in {
            "name": name,
            "display_name": display_name,
            "description": description,
            "is_required": is_required
        }.items() if v is not None}

        result = parameter_repository.update_parameter(parameter_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return ParameterModel(
            parameter_id=str(result.parameter_id),
            name=result.name,
            display_name=result.display_name,
            description=result.description,
            is_required=result.is_required,
            created_at=result.created_at,
            values=[ParameterValueModel(
                value_id=str(value.value_id),
                value=value.value,
                display_order=value.display_order,
                created_at=value.created_at
            ) for value in result.values]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/parameters/{parameter_id}")
def delete_parameter(
    parameter_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Delete a parameter and its values."""
    try:
        success = parameter_repository.delete_parameter(parameter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return {"message": "Parameter and associated values deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameter values management endpoints
@router.post("/parameters/{parameter_id}/values", response_model=ParameterValueModel)
def create_parameter_value(
    parameter_id: UUID,
    value: str = Body(...),
    display_order: int = Body(0),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a new parameter value."""
    try:
        result = parameter_repository.create_parameter_value(parameter_id, value, display_order)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create parameter value")
        
        return format_parameter_value(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/parameters/{parameter_id}/values/{value_id}", response_model=ParameterValueModel)
def update_parameter_value(
    parameter_id: UUID,
    value_id: UUID,
    value: Optional[str] = Body(None),
    display_order: Optional[int] = Body(None),
    current_user: dict = Depends(get_current_user_profile)
):
    """Update a parameter value."""
    try:
        update_data = {k: v for k, v in {
            "value": value,
            "display_order": display_order
        }.items() if v is not None}

        result = parameter_repository.update_parameter_value(value_id, parameter_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return ParameterValueModel(
            value_id=str(result.value_id),
            value=result.value,
            display_order=result.display_order,
            created_at=result.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/parameters/{parameter_id}/values/{value_id}")
def delete_parameter_value(
    parameter_id: UUID,
    value_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Delete a parameter value."""
    try:
        success = parameter_repository.delete_parameter_value(value_id, parameter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return {"message": "Parameter value deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/parameters/{template_id}/duplicate", response_model=TemplateResponse, tags=["templates"])
def duplicate_template(
    template_id: UUID, 
    new_name: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a copy of an existing template."""
    try:
        result = template.duplicate_template(template_id, current_user.profile_id, new_name)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return template.get_template_with_parameters(result["template_id"], UUID(current_user.profile_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

