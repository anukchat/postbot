from typing import Any, Optional, List, Dict, Type, Generic, Union, TypeVar, ContextManager
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from .connection import DatabaseConnectionManager, db_retry
from .models import Base

Model = TypeVar('Model', bound=DeclarativeMeta)

class SQLAlchemyRepository(Generic[Model]):
    def __init__(self, model: Type[Model]):
        self.model = model
        self.db = DatabaseConnectionManager()

    def find_by_id(self, id_field: str, id_value: UUID) -> Optional[Model]:
        """Find a record by ID field"""
        session = self.db.get_session()
        try:
            stmt = select(self.model).where(getattr(self.model, id_field) == id_value)
            result = session.execute(stmt).scalar_one_or_none()
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def create(self, data: Dict[str, Any]) -> Model:
        """Create a new record"""
        session = self.db.get_session()
        try:
            instance = self.model(**data)
            session.add(instance)
            session.flush()
            session.commit()
            return instance
        except Exception as e:
            session.rollback()
            raise e

    def update(self, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Model]:
        """Update a record"""
        session = self.db.get_session()
        try:
            instance = self.find_by_id(id_field, id_value)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                session.flush()
                session.commit()
            return instance
        except Exception as e:
            session.rollback()
            raise e

    def delete(self, id_field: str, id_value: UUID) -> bool:
        """Hard delete a record"""
        session = self.db.get_session()
        try:
            instance = self.find_by_id(id_field, id_value)
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Model]:
        """Filter records based on criteria"""
        session = self.db.get_session()
        try:
            stmt = select(self.model)
            if filters and isinstance(filters, dict):
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, (list, tuple)):
                            stmt = stmt.where(getattr(self.model, field).in_(value))
                        elif value is None:
                            stmt = stmt.where(getattr(self.model, field).is_(None))
                        else:
                            stmt = stmt.where(getattr(self.model, field) == value)
            stmt = stmt.offset(skip).limit(limit)
            result = list(session.execute(stmt).scalars().all())
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def exists(self, id_field: str, id_value: UUID) -> bool:
        """Check if a record exists"""
        session = self.db.get_session()
        try:
            stmt = select(self.model).where(getattr(self.model, id_field) == id_value)
            result = session.execute(stmt).first() is not None
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records optionally filtered"""
        session = self.db.get_session()
        try:
            pk_name = list(self.model.__table__.primary_key)[0].name
            stmt = select(func.count(getattr(self.model, pk_name)))
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, (list, tuple)):
                            stmt = stmt.where(getattr(self.model, field).in_(value))
                        elif value is None:
                            stmt = stmt.where(getattr(self.model, field).is_(None))
                        else:
                            stmt = stmt.where(getattr(self.model, field) == value)
            result = session.execute(stmt).scalar()
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def soft_delete(self, id_field: str, id_value: UUID) -> bool:
        """Soft delete a record"""
        session = self.db.get_session()
        try:
            instance = self.find_by_id(id_field, id_value)
            if instance and hasattr(instance, 'is_deleted'):
                instance.is_deleted = True
                instance.deleted_at = datetime.now()
                instance.updated_at = datetime.now()
                session.flush()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def batch_create(self, records: List[Dict[str, Any]]) -> List[Model]:
        """Create multiple records in a single transaction"""
        session = self.db.get_session()
        try:
            instances = []
            for record in records:
                instance = self.model(**record)
                session.add(instance)
                instances.append(instance)
            session.flush()
            session.commit()
            return instances
        except Exception as e:
            session.rollback()
            raise e

    def batch_update(self, id_field: str, records: List[Dict[str, Any]]) -> List[Model]:
        """Update multiple records in a single transaction"""
        session = self.db.get_session()
        try:
            updated = []
            for record in records:
                if id_field in record:
                    id_value = record[id_field]
                    del record[id_field]
                    instance = self.update(id_field, id_value, record)
                    if instance:
                        updated.append(instance)
            session.commit()
            return updated
        except Exception as e:
            session.rollback()
            raise e

    def batch_delete(self, id_field: str, ids: List[UUID]) -> bool:
        """Delete multiple records in a single transaction"""
        session = self.db.get_session()
        try:
            result = session.query(self.model).filter(
                getattr(self.model, id_field).in_(ids)
            ).delete(synchronize_session=False)
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            raise e

    def check_rate_limit(self, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if an action is within rate limits"""
        session = self.db.get_session()
        try:
            from .models import RateLimit
            window_start = datetime.now() - timedelta(minutes=window_minutes)
            stmt = select(func.count(RateLimit.rate_limit_id)).where(
                RateLimit.profile_id == profile_id,
                RateLimit.action_type == action_type,
                RateLimit.created_at >= window_start
            )
            result = session.execute(stmt).scalar() < limit
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def increment_rate_limit(self, profile_id: UUID, action_type: str) -> None:
        """Record a rate-limited action"""
        session = self.db.get_session()
        try:
            from .models import RateLimit
            rate_limit = RateLimit(profile_id=profile_id, action_type=action_type)
            session.add(rate_limit)
            session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e