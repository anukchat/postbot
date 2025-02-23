from typing import Any, Optional, List, Dict, Type, Generic, Union, TypeVar
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from .connection import DatabaseConnectionManager, db_retry
from .models import Base

Model = TypeVar('Model', bound=DeclarativeMeta)

class SQLAlchemyRepository(Generic[Model]):
    def __init__(self, model: Type[Model]):
        self.model = model
        self.db = DatabaseConnectionManager()

    @db_retry(retries=3, delay=1)
    def find_by_id(self, session: Session, id_field: str, id_value: UUID) -> Optional[Model]:
        """Find a record by ID field"""
        return session.query(self.model).filter(getattr(self.model, id_field) == id_value).first()

    @db_retry(retries=3, delay=1)
    def create(self, session: Session, data: Dict[str, Any]) -> Model:
        """Create a new record"""
        instance = self.model(**data)
        session.add(instance)
        session.flush()
        return instance

    @db_retry(retries=3, delay=1)
    def update(self, session: Session, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Model]:
        """Update a record"""
        instance = self.find_by_id(session, id_field, id_value)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            session.flush()
        return instance

    @db_retry(retries=3, delay=1)
    def delete(self, session: Session, id_field: str, id_value: UUID) -> bool:
        """Hard delete a record"""
        instance = self.find_by_id(session, id_field, id_value)
        if instance:
            session.delete(instance)
            session.flush()
            return True
        return False

    @db_retry(retries=3, delay=1)
    def filter(self, session: Session, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Model]:
        """Filter records based on criteria"""
        query = session.query(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, (list, tuple)):
                    query = query.filter(getattr(self.model, field).in_(value))
                elif value is None:
                    query = query.filter(getattr(self.model, field).is_(None))
                else:
                    query = query.filter(getattr(self.model, field) == value)
        return query.offset(skip).limit(limit).all()

    @db_retry(retries=3, delay=1)
    def exists(self, session: Session, id_field: str, id_value: UUID) -> bool:
        """Check if a record exists"""
        return session.query(self.model).filter(getattr(self.model, id_field) == id_value).first() is not None

    @db_retry(retries=3, delay=1)
    def count(self, session: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records optionally filtered"""
        query = session.query(func.count(getattr(self.model, list(self.model.__table__.primary_key)[0].name)))
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, tuple)):
                        query = query.filter(getattr(self.model, field).in_(value))
                    elif value is None:
                        query = query.filter(getattr(self.model, field).is_(None))
                    else:
                        query = query.filter(getattr(self.model, field) == value)
        return query.scalar()

    @db_retry(retries=3, delay=1)
    def soft_delete(self, session: Session, id_field: str, id_value: UUID) -> bool:
        """Soft delete a record"""
        instance = self.find_by_id(session, id_field, id_value)
        if instance and hasattr(instance, 'is_deleted'):
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.updated_at = datetime.now()
            session.flush()
            return True
        return False

    @db_retry(retries=3, delay=1)
    def batch_create(self, session: Session, records: List[Dict[str, Any]]) -> List[Model]:
        """Create multiple records in a single transaction"""
        instances = []
        for record in records:
            instance = self.model(**record)
            session.add(instance)
            instances.append(instance)
        session.flush()
        return instances

    @db_retry(retries=3, delay=1)
    def batch_update(self, session: Session, id_field: str, records: List[Dict[str, Any]]) -> List[Model]:
        """Update multiple records in a single transaction"""
        updated = []
        for record in records:
            if id_field in record:
                id_value = record[id_field]
                del record[id_field]
                instance = self.update(session, id_field, id_value, record)
                if instance:
                    updated.append(instance)
        return updated

    @db_retry(retries=3, delay=1)
    def batch_delete(self, session: Session, id_field: str, ids: List[UUID]) -> bool:
        """Delete multiple records in a single transaction"""
        result = session.query(self.model).filter(getattr(self.model, id_field).in_(ids)).delete(synchronize_session=False)
        session.flush()
        return result > 0

    def check_rate_limit(self, session: Session, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if an action is within rate limits"""
        from .models import RateLimit
        window_start = datetime.now() - timedelta(minutes=window_minutes)
        count = session.query(func.count(RateLimit.rate_limit_id)).filter(
            RateLimit.profile_id == profile_id,
            RateLimit.action_type == action_type,
            RateLimit.created_at >= window_start
        ).scalar()
        return count < limit

    def increment_rate_limit(self, session: Session, profile_id: UUID, action_type: str) -> None:
        """Record a rate-limited action"""
        from .models import RateLimit
        rate_limit = RateLimit(profile_id=profile_id, action_type=action_type)
        session.add(rate_limit)
        session.flush()