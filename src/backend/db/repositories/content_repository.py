from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import and_, or_, desc, insert
from ..models import Content, ContentType, Profile, Source, Tag, URLReference, Media, content_tags, content_sources
from ..sqlalchemy_repository import SQLAlchemyRepository
from ...formatters import format_content_list_item, format_content_list_response

class ContentRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)

    def get_content_by_thread(self, thread_id: UUID, profile_id: UUID, content_type_id: Optional[UUID] = None):
        """Get content by thread ID with optional content type filter"""
        session = self.db.get_session()
        try:
            query = session.query(Content)\
                .options(
                    joinedload(Content.content_type),
                    joinedload(Content.content_tags).joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )\
                .filter(Content.thread_id == thread_id)\
                .filter(Content.profile_id == profile_id)

            if content_type_id:
                query = query.filter(Content.content_type_id == content_type_id)

            content = query.first()
            session.commit()
            return content
        except Exception as e:
            session.rollback()
            raise e

    def update_by_thread(self, thread_id: UUID, profile_id: UUID, data: Dict):
        """Update content by thread ID"""
        session = self.db.get_session()
        try:
            content = (
                session.query(Content)
                .options(
                    joinedload(Content.content_type),
                    joinedload(Content.content_tags).joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .filter(
                    Content.thread_id == thread_id,
                    Content.profile_id == profile_id,
                    Content.is_deleted.is_(False)
                )
                .first()
            )
            
            if content:
                for key, value in data.items():
                    if hasattr(content, key):
                        setattr(content, key, value)
                session.commit()
                return content
            return None
        except Exception as e:
            session.rollback()
            raise e

    def filter_content(self, profile_id: UUID, filters: Dict, skip: int = 0, limit: int = 10):
        """Filter content with complex criteria"""
        session = self.db.get_session()
        try:
            subquery = (
                session.query(Content)
                .outerjoin(Content.content_type)
                .outerjoin(Content.tags)
                .outerjoin(Content.sources)
                .outerjoin(Source.source_type)
                .outerjoin(Source.url_references)
                .outerjoin(Source.media)
                .filter(Content.profile_id == profile_id)
                .filter(Content.is_deleted.is_(False))
            )
            
            # Apply filters
            if "content_type" in filters:
                subquery = subquery.filter(ContentType.name == filters["content_type"])
            
            if "status" in filters:
                subquery = subquery.filter(Content.status == filters["status"])
            
            if "search" in filters:
                search_term = f"%{filters['search']}%"
                subquery = subquery.filter(
                    or_(
                        Content.title.ilike(search_term),
                        Content.body.ilike(search_term)
                    )
                )
            
            if "domain" in filters:
                domain_term = f"%{filters['domain']}%"
                subquery = subquery.filter(URLReference.domain.ilike(domain_term))
                
            if "source_type" in filters:
                subquery = subquery.filter(Source.source_type.has(name=filters["source_type"]))
                
            if "media_type" in filters:
                subquery = subquery.filter(Media.media_type == filters["media_type"])
                
            if "url_type" in filters:
                subquery = subquery.filter(URLReference.type == filters["url_type"])

            if "date_from" in filters:
                subquery = subquery.filter(Content.created_at >= filters["date_from"])
            
            if "date_to" in filters:
                subquery = subquery.filter(Content.created_at <= filters["date_to"])
                
            if "updated_after" in filters:
                subquery = subquery.filter(Content.updated_at >= filters["updated_after"])
                
            if "updated_before" in filters:
                subquery = subquery.filter(Content.updated_at <= filters["updated_before"])
            
            if "tags" in filters and filters["tags"]:
                if isinstance(filters["tags"], list):
                    subquery = subquery.filter(Tag.name.in_(filters["tags"]))
                else:
                    subquery = subquery.filter(Tag.name == filters["tags"])
            
            subquery = subquery.distinct()
            
            content_ids = subquery.with_entities(Content.content_id).distinct()

            # Add options for eager loading
            query = (session.query(Content)
            .filter(Content.content_id.in_(content_ids))
            .options(
                joinedload(Content.content_type),
                joinedload(Content.tags),
                joinedload(Content.sources).joinedload(Source.source_type),
                joinedload(Content.sources).joinedload(Source.url_references),
                joinedload(Content.sources).joinedload(Source.media)
            )
            .order_by(desc(Content.created_at))
            )

            total = subquery.count()
            contents = query.offset(skip).limit(limit).all()
            session.commit()
            
            return {
                "items": contents,
                "total": total,
                "page": skip // limit + 1,
                "size": limit
            }
        except Exception as e:
            session.rollback()
            raise e

    def add_content_tag(self, content_id: UUID, tag_id: UUID) -> bool:
        """
        Add a tag to content by inserting into the content_tags association table
        Returns True if successful, False otherwise
        """
        session = self.db.get_session()
        try:
            # Check if the association already exists
            existing = session.query(content_tags).filter(
                content_tags.c.content_id == content_id,
                content_tags.c.tag_id == tag_id,
                content_tags.c.is_deleted == False
            ).first()
            
            if existing:
                # Association already exists and is not deleted
                return True
                
            # Check if there's a soft-deleted record to restore
            soft_deleted = session.query(content_tags).filter(
                content_tags.c.content_id == content_id,
                content_tags.c.tag_id == tag_id,
                content_tags.c.is_deleted == True
            ).first()
            
            if soft_deleted:
                # Update the soft-deleted record
                stmt = (
                    content_tags.update()
                    .where(
                        content_tags.c.content_id == content_id,
                        content_tags.c.tag_id == tag_id
                    )
                    .values(is_deleted=False, deleted_at=None)
                )
                session.execute(stmt)
            else:
                # Insert a new record
                stmt = insert(content_tags).values(
                    content_id=content_id,
                    tag_id=tag_id
                )
                session.execute(stmt)
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e

    def add_content_tags(self, content_id: UUID, tag_ids: List[UUID]) -> bool:
        """
        Add multiple tags to content by inserting into the content_tags association table
        Returns True if successful, False otherwise
        """
        session = self.db.get_session()
        try:
            for tag_id in tag_ids:
                self.add_content_tag(content_id, tag_id)
            return True
        except Exception as e:
            session.rollback()
            raise e

    def remove_content_tag(self, content_id: UUID, tag_id: UUID, hard_delete: bool = False) -> bool:
        """
        Remove a tag from content
        If hard_delete is True, removes the record entirely
        Otherwise performs a soft delete
        """
        session = self.db.get_session()
        try:
            if hard_delete:
                # Hard delete
                stmt = content_tags.delete().where(
                    content_tags.c.content_id == content_id,
                    content_tags.c.tag_id == tag_id
                )
            else:
                # Soft delete
                from datetime import datetime
                stmt = content_tags.update().where(
                    content_tags.c.content_id == content_id,
                    content_tags.c.tag_id == tag_id
                ).values(
                    is_deleted=True,
                    deleted_at=datetime.now()
                )
            
            session.execute(stmt)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
    
    # Content source methods
    def add_content_source(self, content_id: UUID, source_id: UUID) -> bool:
        """
        Add a source to content by inserting into the content_sources association table
        Returns True if successful, False otherwise
        """
        session = self.db.get_session()
        try:
            # Check if the association already exists
            existing = session.query(content_sources).filter(
                content_sources.c.content_id == content_id,
                content_sources.c.source_id == source_id,
                content_sources.c.is_deleted == False
            ).first()
            
            if existing:
                # Association already exists and is not deleted
                return True
                
            # Check if there's a soft-deleted record to restore
            soft_deleted = session.query(content_sources).filter(
                content_sources.c.content_id == content_id,
                content_sources.c.source_id == source_id,
                content_sources.c.is_deleted == True
            ).first()
            
            if soft_deleted:
                # Update the soft-deleted record
                stmt = (
                    content_sources.update()
                    .where(
                        content_sources.c.content_id == content_id,
                        content_sources.c.source_id == source_id
                    )
                    .values(is_deleted=False, deleted_at=None)
                )
                session.execute(stmt)
            else:
                # Insert a new record
                stmt = insert(content_sources).values(
                    content_id=content_id,
                    source_id=source_id
                )
                session.execute(stmt)
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e

    def add_content_sources(self, content_id: UUID, source_ids: List[UUID]) -> bool:
        """
        Add multiple sources to content by inserting into the content_sources association table
        Returns True if successful, False otherwise
        """
        session = self.db.get_session()
        try:
            for source_id in source_ids:
                self.add_content_source(content_id, source_id)
            return True
        except Exception as e:
            session.rollback()
            raise e

    def remove_content_source(self, content_id: UUID, source_id: UUID, hard_delete: bool = False) -> bool:
        """
        Remove a source from content
        If hard_delete is True, removes the record entirely
        Otherwise performs a soft delete
        """
        session = self.db.get_session()
        try:
            if hard_delete:
                # Hard delete
                stmt = content_sources.delete().where(
                    content_sources.c.content_id == content_id,
                    content_sources.c.source_id == source_id
                )
            else:
                # Soft delete
                from datetime import datetime
                stmt = content_sources.update().where(
                    content_sources.c.content_id == content_id,
                    content_sources.c.source_id == source_id
                ).values(
                    is_deleted=True,
                    deleted_at=datetime.now()
                )
            
            session.execute(stmt)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e