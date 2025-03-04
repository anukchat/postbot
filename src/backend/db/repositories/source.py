from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import Source, SourceType, URLReference, Media, SourceMetadata
from ..sqlalchemy_repository import SQLAlchemyRepository
from ...api.formatters import format_source_list_response

class SourceRepository(SQLAlchemyRepository[Source]):
    def __init__(self):
        super().__init__(Source)

    def create_source(self, data: Dict[str, Any], profile_id: UUID) -> Source:
        """Create a source with related data"""
        session = self.db.get_session()
        try:
            # Extract related data
            url_references = data.pop('url_references', [])
            media_items = data.pop('media', [])
            
            # Set profile ID
            data['profile_id'] = profile_id
            
            # Create source
            source = self.create(data)
            
            # Add URL references
            for url_ref in url_references:
                ref = URLReference(
                    source_id=source.source_id,
                    url=url_ref['url'],
                    type=url_ref.get('type'),
                    domain=url_ref.get('domain')
                )
                session.add(ref)
            
            # Add media
            for media_item in media_items:
                media = Media(
                    source_id=source.source_id,
                    media_url=media_item['media_url'],
                    media_type=media_item.get('media_type')
                )
                session.add(media)
            
            session.commit()
            return source
        except Exception as e:
            session.rollback()
            raise e

    def list_sources_with_related(
        self,
        profile_id: UUID,
        type: Optional[str] = None,
        source_identifier: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ):
        """List sources with related data"""
        session = self.db.get_session()
        try:
            query = session.query(Source)\
                .options(
                    joinedload(Source.source_type),
                    joinedload(Source.url_references),
                    joinedload(Source.media),
                )\
                .filter(Source.profile_id == profile_id)\
                .filter(Source.is_deleted == False)

            if type:
                query = query.join(Source.source_type)\
                    .filter(SourceType.name == type)

            if source_identifier:
                query = query.filter(Source.source_identifier == source_identifier)

            # Get total count
            total = query.count()

            # Get paginated results
            sources = query.order_by(desc(Source.created_at))\
                .offset(skip)\
                .limit(limit)\
                .all()

            # Calculate current page
            page = skip // limit + 1

            session.commit()
            return format_source_list_response(
                items=sources,
                total=total,
                page=page,
                size=limit
            )
        except Exception as e:
            session.rollback()
            raise e

    def get_source_with_references(self, source_id: UUID, profile_id: UUID) -> Optional[Source]:
        """Get a source with all its references"""
        session = self.db.get_session()
        try:
            source = (
                session.query(Source)
                .options(
                    joinedload(Source.source_type),
                    joinedload(Source.url_references),
                    joinedload(Source.media)
                )
                .filter(
                    Source.source_id == source_id,
                    Source.profile_id == profile_id,
                    Source.is_deleted.is_(False)
                )
                .first()
            )
            session.commit()
            return source
        except Exception as e:
            session.rollback()
            raise e

    def update_source_references(
        self,
        source_id: UUID,
        url_references: Optional[List[Dict]] = None,
        media_items: Optional[List[Dict]] = None
    ) -> bool:
        """Update source references (URLs and media)"""
        session = self.db.get_session()
        try:
            source = session.query(Source).get(source_id)
            if not source:
                return False
            
            # Update URL references
            if url_references is not None:
                # Delete existing references
                session.query(URLReference).filter(
                    URLReference.source_id == source_id
                ).delete()
                
                # Add new references
                for url_ref in url_references:
                    ref = URLReference(
                        source_id=source_id,
                        url=url_ref['url'],
                        type=url_ref.get('type'),
                        domain=url_ref.get('domain')
                    )
                    session.add(ref)
            
            # Update media items
            if media_items is not None:
                # Delete existing media
                session.query(Media).filter(
                    Media.source_id == source_id
                ).delete()
                
                # Add new media
                for media_item in media_items:
                    media = Media(
                        source_id=source_id,
                        media_url=media_item['media_url'],
                        media_type=media_item.get('media_type')
                    )
                    session.add(media)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e

    def get_source_by_identifier(self, identifier: str, source_type: str, profile_id: UUID) -> Optional[Source]:
        """Get a source by its identifier and type"""
        session = self.db.get_session()
        try:
            source = (
                session.query(Source)
                .join(Source.source_type)
                .filter(
                    Source.source_identifier == identifier,
                    SourceType.name == source_type,
                    Source.profile_id == profile_id,
                    Source.is_deleted.is_(False)
                )
                .first()
            )
            session.commit()
            return source
        except Exception as e:
            session.rollback()
            raise e

    def soft_delete(self, source_id: UUID, profile_id: UUID) -> bool:
        """Soft delete a source"""
        session = self.db.get_session()
        try:
            source = (
                session.query(Source)
                .filter(
                    Source.source_id == source_id,
                    Source.profile_id == profile_id
                )
                .first()
            )
            
            if source:
                return super().soft_delete("source_id", source_id)
            return False
        except Exception as e:
            session.rollback()
            raise e