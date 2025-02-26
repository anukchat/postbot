from typing import Optional
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..models import Tag

class TagsRepository(SQLAlchemyRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)
    
    def find_by_name(self, name: str) -> Optional[Tag]:
        """Find a tag by name"""
        results = self.filter({"name": name}, limit=1)
        return results[0] if results else None

    def find_or_create(self, name: str) -> Tag:
        """Find a tag by name or create if not exists"""
        tag = self.find_by_name(name)
        if not tag:
            tag = self.create({"name": name})
        return tag
