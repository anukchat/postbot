from uuid import UUID
from typing import List
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..models import URLReference

class URLReferencesRepository(SQLAlchemyRepository[URLReference]):
    def __init__(self):
        super().__init__(URLReference)
    
    def find_by_source_id(self, source_id: UUID) -> List[URLReference]:
        """
        Fetch all URL references for a given source_id
        """
        return self.filter({"source_id": source_id})
