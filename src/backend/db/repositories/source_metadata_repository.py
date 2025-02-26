from uuid import UUID
from typing import List
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..models import SourceMetadata

class SourceMetadataRepository(SQLAlchemyRepository[SourceMetadata]):
    def __init__(self):
        super().__init__(SourceMetadata)
    
    def _fetch_content_metadata(self, source_id: UUID) -> List[SourceMetadata]:
        """Helper method to fetch content metadata"""
        return self.filter({"source_id": source_id})
