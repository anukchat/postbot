from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, and_
from ..models import Template, Parameter, ParameterValue
from ..sqlalchemy_repository import SQLAlchemyRepository
from ...formatters import format_template_response

class TemplateRepository(SQLAlchemyRepository[Template]):
    def __init__(self):
        super().__init__(Template)

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

    def get_template_with_parameters(self, template_id: UUID, profile_id: UUID):
        """Get template with its parameters"""
        session = self.db.get_session()

        try:
            template = session.query(Template)\
                .options(
                    joinedload(Template.parameters)
                    .joinedload(Parameter.values)
                )\
                .filter(
                    Template.template_id == template_id,
                    Template.profile_id == profile_id,
                    Template.is_deleted == False
                ).first()
                
            if not template:
                return None

            return format_template_response(template)
        except Exception as e:
            raise e

    def list_templates_for_profile(
        self,
        profile_id: UUID,
        skip: int = 0,
        limit: int = 10,
        template_type: Optional[str] = None,
        include_deleted: bool = False
    ):
        """List all templates for a profile"""
        session = self.db.get_session()
        try:
            query = session.query(Template)\
                .options(joinedload(Template.parameters).joinedload(Parameter.values))\
                .filter(Template.profile_id == profile_id)

            if not include_deleted:
                query = query.filter(Template.is_deleted == False)
                
            if template_type:
                query = query.filter(Template.template_type == template_type)

            templates = query.order_by(desc(Template.created_at))\
                .offset(skip)\
                .limit(limit)\
                .all()

            session.commit()
            return [format_template_response(template) for template in templates]
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
        """Update a template and its parameters"""
        session = self.db.get_session()
        try:
            template = (
                session.query(Template)
                .filter(
                    Template.template_id == template_id,
                    Template.profile_id == profile_id
                )
                .first()
            )
            
            if not template:
                return None
            
            # Update template fields
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            # Update parameters if provided
            if parameters is not None:
                # Clear existing parameters
                template.parameters = []
                
                # Add new parameters
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

    def duplicate_template(self, template_id: UUID, profile_id: UUID, new_name: str) -> Optional[Template]:
        """Create a copy of an existing template"""
        session = self.db.get_session()
        try:
            # Get original template with parameters
            original = self.get_template_with_parameters(template_id, profile_id)
            if not original:
                return None
            
            # Create new template
            new_template = Template(
                profile_id=profile_id,
                name=new_name,
                description=original.description,
                template_type=original.template_type,
                template_image_url=original.template_image_url
            )
            session.add(new_template)
            
            # Copy parameters
            new_template.parameters = original.parameters.copy()
            
            session.commit()
            return new_template
        except Exception as e:
            session.rollback()
            raise e

    def filter_templates(
        self,
        profile_id: UUID,
        parameters: List[Dict[str, UUID]],
        template_type: Optional[str] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 10
    ) -> List[Template]:
        """Filter templates by parameters"""
        session = self.db.get_session()
        try:
            query = (
                session.query(Template)
                .join(Template.parameters)
                .filter(Template.profile_id == profile_id)
            )
            
            if not include_deleted:
                query = query.filter(Template.is_deleted.is_(False))
            
            if template_type:
                query = query.filter(Template.template_type == template_type)
            
            # Filter by parameters
            for param in parameters:
                param_id = param.get('parameter_id')
                value_id = param.get('value_id')
                if param_id and value_id:
                    query = query.filter(
                        and_(
                            Parameter.parameter_id == param_id,
                            ParameterValue.value_id == value_id
                        )
                    )
            
            query = (
                query.options(
                    joinedload(Template.parameters).joinedload(Parameter.values)
                )
                .order_by(desc(Template.created_at))
                .offset(skip)
                .limit(limit)
            )
            
            session.commit()
            return query.all()
        except Exception as e:
            session.rollback()
            raise e

    def count_templates(
        self,
        profile_id: UUID,
        template_type: Optional[str] = None,
        include_deleted: bool = False
    ) -> int:
        """Count templates for a profile"""
        with self.db.session() as session:
            query = session.query(Template).filter(Template.profile_id == profile_id)
            
            if not include_deleted:
                query = query.filter(Template.is_deleted.is_(False))
            
            if template_type:
                query = query.filter(Template.template_type == template_type)
            
            return query.count()