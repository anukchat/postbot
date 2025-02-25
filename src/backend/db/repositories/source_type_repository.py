from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import SourceType
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..connection import db_retry

class SourceTypeRepository(SQLAlchemyRepository[SourceType]):
    def __init__(self):
        super().__init__(SourceType)

    @db_retry
    def get_source_type_by_name(self, name: str) -> Optional[SourceType]:
        """Get source type by name"""
        filters = {
            'name': name,
            'is_deleted': False
        }
        results = super().filter(filters, limit=1)
        return results[0] if results else None

    @db_retry
    def list_source_types(self, skip: int = 0, limit: int = 10) -> List[SourceType]:
        """List all source types"""
        filters = {'is_deleted': False}
        return super().filter(filters, skip=skip, limit=limit)

    @db_retry
    def find_by_names(self, names: List[str]) -> List[SourceType]:
        """Find source types by names"""
        if not names:
            return []
        filters = {
            'name': names,
            'is_deleted': False
        }
        return super().filter(filters)