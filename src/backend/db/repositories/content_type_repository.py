from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import ContentType
from ..sqlalchemy_repository import SQLAlchemyRepository

class ContentTypeRepository(SQLAlchemyRepository[ContentType]):
    def __init__(self):
        super().__init__(ContentType)

    def get_content_type_id_by_name(self, name: str) -> Optional[UUID]:
        """Get content type ID by name"""
        session = self.db.get_session()
        try:
            content_type = (
                session.query(ContentType)
                .filter(
                    ContentType.name == name
                )
                .first()
            )
            session.commit()
            return content_type.content_type_id if content_type else None
        except Exception as e:
            session.rollback()
            raise e

    def list_content_types(self, skip: int = 0, limit: int = 10) -> List[ContentType]:
        """List all content types"""
        session = self.db.get_session()
        try:
            content_types = (
                session.query(ContentType)
                .filter(ContentType.is_deleted.is_(False))
                .order_by(desc(ContentType.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )
            session.commit()
            return content_types
        except Exception as e:
            session.rollback()
            raise e

    def find_by_names(self, names: List[str]) -> List[ContentType]:
        """Find content types by names"""
        session = self.db.get_session()
        try:
            content_types = (
                session.query(ContentType)
                .filter(
                    ContentType.name.in_(names),
                    ContentType.is_deleted.is_(False)
                )
                .all()
            )
            session.commit()
            return content_types
        except Exception as e:
            session.rollback()
            raise e