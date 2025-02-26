from uuid import UUID
from typing import List
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..models import Media

class MediaRepository(SQLAlchemyRepository[Media]):
    def __init__(self):
        super().__init__(Media)
    
    def _fetch_media(self, source_id: UUID) -> List[Media]:
        """Helper method to fetch media"""
        return self.filter({"source_id": source_id})

    def bulk_insert_media(self, source_id: UUID, media_meta: List[dict]) -> None:
        """Bulk insert media records for a source"""
        if media_meta:
            media_objects = [
                Media(
                    source_id=source_id,
                    media_url=media["original_url"],
                    media_type=media["type"]
                ) for media in media_meta
            ]
            self.bulk_create(media_objects)