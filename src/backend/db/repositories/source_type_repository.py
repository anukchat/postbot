from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import SourceType
from ..sqlalchemy_repository import SQLAlchemyRepository

class SourceTypeRepository(SQLAlchemyRepository[SourceType]):
    def __init__(self):
        super().__init__(SourceType)

    def get_source_type_by_name(self, name: str) -> Optional[SourceType]:
        """Get source type by name"""
        with self.db.session() as session:
            return (
                session.query(SourceType)
                .filter(
                    SourceType.name == name,
                    SourceType.is_deleted.is_(False)
                )
                .first()
            )

    def list_source_types(self, skip: int = 0, limit: int = 10) -> List[SourceType]:
        """List all source types"""
        with self.db.session() as session:
            return (
                session.query(SourceType)
                .filter(SourceType.is_deleted.is_(False))
                .order_by(desc(SourceType.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

    def find_by_names(self, names: List[str]) -> List[SourceType]:
        """Find source types by names"""
        with self.db.session() as session:
            return (
                session.query(SourceType)
                .filter(
                    SourceType.name.in_(names),
                    SourceType.is_deleted.is_(False)
                )
                .all()
            )