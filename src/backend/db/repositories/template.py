from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, and_

from src.backend.api.datamodel import TemplateParameter, TemplateParameterValue, TemplateResponse
from ..models import Template, Parameter, ParameterValue, template_parameters
from ..sqlalchemy_repository import SQLAlchemyRepository

class TemplateRepository(SQLAlchemyRepository[Template]):
    def __init__(self):
        super().__init__(Template)

    def list_templates_for_profile(self, profile_id: UUID):
        """List all active templates for a profile with their parameters and values"""
        session = self.db.get_session()
        try:
            # Get templates with parameters loaded
            templates = session.query(Template)\
                .options(joinedload(Template.parameters))\
                .filter(
                    Template.profile_id == profile_id,
                    Template.is_deleted == False
                )\
                .order_by(desc(Template.created_at))\
                .all()
            
            formatted_templates = []
            for template in templates:
                # Format parameters with their values
                formatted_parameters = []
                for param in template.parameters:
                    # Get the selected value from template_parameters association table
                    selected_value = session.query(template_parameters)\
                        .filter(
                            template_parameters.c.template_id == template.template_id,
                            template_parameters.c.parameter_id == param.parameter_id
                        ).first()

                    # Get the parameter value details if there's a selected value
                    value_details = None
                    if selected_value and selected_value.value_id:
                        value = session.query(ParameterValue)\
                            .filter(ParameterValue.value_id == selected_value.value_id)\
                            .first()
                        if value:
                            value_details = TemplateParameterValue(
                                value_id= value.value_id,
                                value= value.value,
                                display_order= value.display_order,
                                created_at= value.created_at
                            )
                    
                    formatted_parameters.append(TemplateParameter(
                        parameter_id= param.parameter_id,
                        name= param.name,
                        display_name= param.display_name,
                        description= param.description,
                        is_required= param.is_required,
                        created_at= param.created_at,
                        values= value_details
                    ))

                # Format template response
                formatted_templates.append( TemplateResponse(
                    template_id= template.template_id,
                    name= template.name,
                    description= template.description,
                    template_type= template.template_type,
                    template_image_url= template.template_image_url,
                    parameters= formatted_parameters,
                    created_at= template.created_at,
                    updated_at= template.updated_at,
                    is_deleted= template.is_deleted
                ))
            
            return formatted_templates
        except Exception as e:
            session.rollback()
            raise e

    def list_templates(self):
        """List all active templates with their parameters and values"""
        session = self.db.get_session()
        try:
            templates = session.query(Template)\
                .options(joinedload(Template.parameters))\
                .filter(Template.is_deleted == False)\
                .order_by(desc(Template.created_at))\
                .all()
            
            formatted_templates = []
            for template in templates:
                formatted_parameters = []
                for param in template.parameters:
                    selected_value = session.query(template_parameters)\
                        .filter(
                            template_parameters.c.template_id == template.template_id,
                            template_parameters.c.parameter_id == param.parameter_id
                        ).first()

                    value_details = None
                    if selected_value and selected_value.value_id:
                        value = session.query(ParameterValue)\
                            .filter(ParameterValue.value_id == selected_value.value_id)\
                            .first()
                        if value:
                            value_details = TemplateParameterValue(
                                value_id= value.value_id,
                                value= value.value,
                                display_order= value.display_order,
                                created_at= value.created_at
                            )
                    
                    formatted_parameters.append(TemplateParameter(
                        parameter_id= param.parameter_id,
                        name= param.name,
                        display_name= param.display_name,
                        description= param.description,
                        is_required= param.is_required,
                        created_at= param.created_at,
                        values= value_details
                    ))

                formatted_templates.append(TemplateResponse(
                    template_id= template.template_id,
                    name= template.name,
                    description= template.description,
                    template_type= template.template_type,
                    template_image_url= template.template_image_url,
                    parameters= formatted_parameters,
                    created_at= template.created_at,
                    updated_at= template.updated_at,
                    is_deleted= template.is_deleted
                ))
            
            return formatted_templates
        except Exception as e:
            session.rollback()
            raise e
        
    def get_template_with_parameters(self, template_id: UUID):
        """Get a single template with its parameters and values"""
        session = self.db.get_session()
        try:
            template = session.query(Template)\
                .options(joinedload(Template.parameters))\
                .filter(
                    Template.template_id == template_id,
                    Template.is_deleted == False
                ).first()
                
            if not template:
                return None
                
            # Format parameters with their values
            formatted_parameters = []
            for param in template.parameters:
                # Get the selected value from template_parameters association table
                selected_value = session.query(template_parameters)\
                    .filter(
                        template_parameters.c.template_id == template_id,
                        template_parameters.c.parameter_id == param.parameter_id
                    ).first()

                # Get the parameter value details if there's a selected value
                value_details = None
                if selected_value and selected_value.value_id:
                    value = session.query(ParameterValue)\
                        .filter(ParameterValue.value_id == selected_value.value_id)\
                        .first()
                    if value:
                        value_details = TemplateParameterValue(
                            value_id= value.value_id,
                            value= value.value,
                            display_order= value.display_order,
                            created_at= value.created_at
                        )
                        
                formatted_parameters.append(
                    TemplateParameter(
                        parameter_id= param.parameter_id,
                        name= param.name,
                        display_name= param.display_name,
                        description= param.description,
                        is_required= param.is_required,
                        created_at= param.created_at,
                        values= value_details
                    )
                )
            
            # Return formatted response
            return TemplateResponse(
                template_id= template.template_id,
                name= template.name,
                description= template.description,
                template_type= template.template_type,
                template_image_url= template.template_image_url,
                parameters= formatted_parameters,
                created_at= template.created_at,
                updated_at= template.updated_at,
                is_deleted= template.is_deleted
            )
        except Exception as e:
            session.rollback()
            raise e

    def create_template_with_parameters(self, template_data: Dict[str, Any], parameters: List[Dict[str, Any]]) -> Template:
        """Create a template with its parameters"""
        session = self.db.get_session()
        try:
            # Create template
            template = self.create(template_data)
            
            # Add parameters if provided
            if parameters:
                for param_data in parameters:
                    param_id = param_data.get('parameter_id')
                    if param_id:
                        param = session.query(Parameter).get(param_id)
                        if param:
                            template.parameters.append(param)
            
            session.commit()
            return template
        except Exception as e:
            session.rollback()
            raise e

    def update_template_with_parameters(
        self,
        template_id: UUID,
        profile_id: UUID,
        template_data: Dict[str, Any],
        parameters: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Template]:
        """Update a template and optionally its parameters"""
        session = self.db.get_session()
        try:
            template = session.query(Template)\
                .filter(
                    Template.template_id == template_id,
                    Template.profile_id == profile_id
                ).first()
            
            if not template:
                return None
            
            # Update template fields
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            # Update parameters if provided
            if parameters is not None:
                template.parameters = []
                for param_data in parameters:
                    param_id = param_data.get('parameter_id')
                    if param_id:
                        param = session.query(Parameter).get(param_id)
                        if param:
                            template.parameters.append(param)
            
            session.commit()
            return template
        except Exception as e:
            session.rollback()
            raise e