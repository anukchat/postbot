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

    @contextmanager
    def get_session(self):
        """Get database session with context management"""
        with self.db.session() as session:
            yield session

    def find_by_id(self, id_field: str, id_value: UUID) -> Optional[Model]:
        """Find a record by ID field"""
        with self.get_session() as session:
            stmt = select(self.model).where(getattr(self.model, id_field) == id_value)
            return session.execute(stmt).scalar_one_or_none()

    def create(self, data: Dict[str, Any]) -> Model:
        """Create a new record"""
        with self.get_session() as session:
            instance = self.model(**data)
            session.add(instance)
            return instance

    def update(self, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Model]:
        """Update a record"""
        with self.get_session() as session:
            instance = self.find_by_id(id_field, id_value)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                session.flush()
            return instance

    def delete(self, id_field: str, id_value: UUID) -> bool:
        """Hard delete a record"""
        with self.get_session() as session:
            instance = self.find_by_id(id_field, id_value)
            if instance:
                session.delete(instance)
                session.flush()
                return True
            return False

    def filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Model]:
        """Filter records based on criteria"""
        with self.get_session() as session:
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
            return list(session.execute(stmt).scalars().all())

    def exists(self, id_field: str, id_value: UUID) -> bool:
        """Check if a record exists"""
        with self.get_session() as session:
            stmt = select(self.model).where(getattr(self.model, id_field) == id_value)
            return session.execute(stmt).first() is not None

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records optionally filtered"""
        with self.get_session() as session:
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
            return session.execute(stmt).scalar()

    def soft_delete(self, id_field: str, id_value: UUID) -> bool:
        """Soft delete a record"""
        with self.get_session() as session:
            instance = self.find_by_id(id_field, id_value)
            if instance and hasattr(instance, 'is_deleted'):
                instance.is_deleted = True
                instance.deleted_at = datetime.now()
                instance.updated_at = datetime.now()
                session.flush()
                return True
            return False

    def batch_create(self, records: List[Dict[str, Any]]) -> List[Model]:
        """Create multiple records in a single transaction"""
        with self.get_session() as session:
            instances = []
            for record in records:
                instance = self.model(**record)
                session.add(instance)
                instances.append(instance)
            session.flush()
            return instances

    def batch_update(self, id_field: str, records: List[Dict[str, Any]]) -> List[Model]:
        """Update multiple records in a single transaction"""
        with self.get_session() as session:
            updated = []
            for record in records:
                if id_field in record:
                    id_value = record[id_field]
                    del record[id_field]
                    instance = self.update(id_field, id_value, record)
                    if instance:
                        updated.append(instance)
            return updated

    def batch_delete(self, id_field: str, ids: List[UUID]) -> bool:
        """Delete multiple records in a single transaction"""
        with self.get_session() as session:
            result = session.query(self.model).filter(getattr(self.model, id_field).in_(ids)).delete(synchronize_session=False)
            session.flush()
            return result > 0

    def check_rate_limit(self, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if an action is within rate limits"""
        with self.get_session() as session:
            from .models import RateLimit
            window_start = datetime.now() - timedelta(minutes=window_minutes)
            stmt = select(func.count(RateLimit.rate_limit_id)).where(
                RateLimit.profile_id == profile_id,
                RateLimit.action_type == action_type,
                RateLimit.created_at >= window_start
            )
            return session.execute(stmt).scalar() < limit

    def increment_rate_limit(self, profile_id: UUID, action_type: str) -> None:
        """Record a rate-limited action"""
        with self.get_session() as session:
            from .models import RateLimit
            rate_limit = RateLimit(profile_id=profile_id, action_type=action_type)
            session.add(rate_limit)
            session.flush()