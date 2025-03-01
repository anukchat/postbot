import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

from src.backend.api.datamodel import TemplateParameter, TemplateParameterValue
from ..models import Parameter, ParameterValue
from ..sqlalchemy_repository import SQLAlchemyRepository

logger = logging.getLogger(__name__)

class ParameterRepository(SQLAlchemyRepository[Parameter]):
    def __init__(self):
        super().__init__(Parameter)

    def get_parameter_with_values(self, parameter_id: UUID) -> Optional[Parameter]:
        """Get a parameter with its values"""
        session = self.db.get_session()
        try:
            parameter = session.query(Parameter)\
                .options(joinedload(Parameter.values))\
                .filter(Parameter.parameter_id == parameter_id)\
                .first()
            
            session.commit()    
            if not parameter:
                return None
                
            return TemplateParameter(
                parameter_id= parameter.parameter_id,
                name= parameter.name,
                display_name= parameter.display_name,
                description= parameter.description,
                is_required= parameter.is_required,
                created_at= parameter.created_at,
                values= [
                    TemplateParameterValue(
                        value_id= value.value_id,
                        value= value.value,
                        display_order= value.display_order,
                        created_at= value.created_at
                    )
                    for value in parameter.values
                ]
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting parameter with values: {str(e)}")
            raise e

    def list_parameters_with_values(self, skip: int = 0, limit: int = 100) -> List[Parameter]:
        """List all parameters with their values"""
        session = self.db.get_session()
        try:
            parameters = (
                session.query(Parameter)
                .options(joinedload(Parameter.values))
                .order_by(desc(Parameter.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )
            session.commit()
            return parameters
        except Exception as e:
            session.rollback()
            raise e

    def create_parameter_value(self, parameter_id: UUID, value: str, display_order: int = 0) -> Optional[ParameterValue]:
        """Create a new parameter value"""
        session = self.db.get_session()
        try:
            # First check if parameter exists
            parameter = session.query(Parameter).get(parameter_id)
            if not parameter:
                raise ValueError("Parameter not found")

            # Create new value
            param_value = ParameterValue(
                parameter_id=parameter_id,
                value=value,
                display_order=display_order
            )
            session.add(param_value)
            session.commit()
            return param_value
        except Exception as e:
            session.rollback()
            raise e

    def update_parameter_value(self, value_id: UUID, parameter_id: UUID, data: Dict[str, Any]) -> Optional[ParameterValue]:
        """Update a parameter value"""
        session = self.db.get_session()
        try:
            value = (
                session.query(ParameterValue)
                .filter(
                    ParameterValue.value_id == value_id,
                    ParameterValue.parameter_id == parameter_id
                )
                .first()
            )
            
            if not value:
                return None

            for key, val in data.items():
                if hasattr(value, key):
                    setattr(value, key, val)
            
            session.commit()
            return value
        except Exception as e:
            session.rollback()
            raise e

    def delete_parameter_value(self, value_id: UUID, parameter_id: UUID) -> bool:
        """Delete a parameter value"""
        session = self.db.get_session()
        try:
            value = (
                session.query(ParameterValue)
                .filter(
                    ParameterValue.value_id == value_id,
                    ParameterValue.parameter_id == parameter_id
                )
                .first()
            )
            
            if value:
                session.delete(value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def get_parameter_values(self, parameter_id: UUID) -> List[ParameterValue]:
        """Get all values for a parameter"""
        session = self.db.get_session()
        try:
            values = (
                session.query(ParameterValue)
                .filter(ParameterValue.parameter_id == parameter_id)
                .order_by(ParameterValue.display_order)
                .all()
            )
            session.commit()
            return values
        except Exception as e:
            session.rollback()
            raise e

    def create_parameter(self, data: Dict[str, Any]) -> Parameter:
        """Create a new parameter"""
        session = self.db.get_session()
        try:
            parameter = self.create(session, data)
            session.commit()
            return parameter
        except Exception as e:
            session.rollback()
            raise e

    def update_parameter(self, parameter_id: UUID, data: Dict[str, Any]) -> Optional[Parameter]:
        """Update a parameter"""
        session = self.db.get_session()
        try:
            parameter = self.update(session, "parameter_id", parameter_id, data)
            session.commit()
            return parameter
        except Exception as e:
            session.rollback()
            raise e

    def delete_parameter(self, parameter_id: UUID) -> bool:
        """Delete a parameter and its values"""
        session = self.db.get_session()
        try:
            # First delete all associated values
            session.query(ParameterValue).filter(
                ParameterValue.parameter_id == parameter_id
            ).delete()
            
            # Then delete the parameter
            result = self.delete(session, "parameter_id", parameter_id)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e