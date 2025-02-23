import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import Parameter, ParameterValue
from ..sqlalchemy_repository import SQLAlchemyRepository

logger = logging.getLogger(__name__)

class ParameterRepository(SQLAlchemyRepository[Parameter]):
    def __init__(self):
        super().__init__(Parameter)

    def get_parameter_with_values(self, parameter_id: UUID) -> Optional[Parameter]:
        """Get a parameter with its values"""
        try:
            with self.db.session() as session:
                parameter = session.query(Parameter)\
                    .options(joinedload(Parameter.values))\
                    .filter(Parameter.parameter_id == parameter_id)\
                    .first()
                
                if not parameter:
                    return None
                    
                return {
                    "parameter_id": parameter.parameter_id,
                    "name": parameter.name,
                    "display_name": parameter.display_name,
                    "description": parameter.description,
                    "is_required": parameter.is_required,
                    "created_at": parameter.created_at,
                    "values": [
                        {
                            "value_id": value.value_id,
                            "value": value.value,
                            "display_order": value.display_order,
                            "created_at": value.created_at
                        }
                        for value in parameter.values
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting parameter with values: {str(e)}")
            return None

    def list_parameters_with_values(self, skip: int = 0, limit: int = 100) -> List[Parameter]:
        """List all parameters with their values"""
        with self.db.session() as session:
            return (
                session.query(Parameter)
                .options(joinedload(Parameter.values))
                .order_by(desc(Parameter.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

    def create_parameter_value(self, parameter_id: UUID, value: str, display_order: int = 0) -> Optional[ParameterValue]:
        """Create a new parameter value"""
        with self.db.transaction() as session:
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
            session.flush()
            return param_value

    def update_parameter_value(self, value_id: UUID, parameter_id: UUID, data: Dict[str, Any]) -> Optional[ParameterValue]:
        """Update a parameter value"""
        with self.db.transaction() as session:
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
            
            session.flush()
            return value

    def delete_parameter_value(self, value_id: UUID, parameter_id: UUID) -> bool:
        """Delete a parameter value"""
        with self.db.transaction() as session:
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
                session.flush()
                return True
            return False

    def get_parameter_values(self, parameter_id: UUID) -> List[ParameterValue]:
        """Get all values for a parameter"""
        with self.db.session() as session:
            return (
                session.query(ParameterValue)
                .filter(ParameterValue.parameter_id == parameter_id)
                .order_by(ParameterValue.display_order)
                .all()
            )

    def create_parameter(self, data: Dict[str, Any]) -> Parameter:
        """Create a new parameter"""
        with self.db.transaction() as session:
            return self.create(session, data)

    def update_parameter(self, parameter_id: UUID, data: Dict[str, Any]) -> Optional[Parameter]:
        """Update a parameter"""
        with self.db.transaction() as session:
            return self.update(session, "parameter_id", parameter_id, data)

    def delete_parameter(self, parameter_id: UUID) -> bool:
        """Delete a parameter and its values"""
        with self.db.transaction() as session:
            # First delete all associated values
            session.query(ParameterValue).filter(
                ParameterValue.parameter_id == parameter_id
            ).delete()
            
            # Then delete the parameter
            return self.delete(session, "parameter_id", parameter_id)