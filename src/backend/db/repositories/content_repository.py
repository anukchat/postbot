from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import and_, or_, desc
from ..models import Content, ContentType, Profile, Source, Tag, URLReference, Media
from ..sqlalchemy_repository import SQLAlchemyRepository
from ...formatters import format_content_list_item, format_content_list_response

class ContentRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)

    def list_content(self, profile_id: UUID, skip: int = 0, limit: int = 10):
        """List all content for a profile with formatting"""
        try:
            with self.db.session() as session:
                query = session.query(Content)\
                    .options(
                        joinedload(Content.content_type),
                        joinedload(Content.content_tags).joinedload(Content.tags),
                        joinedload(Content.sources).joinedload(Source.source_type),
                        joinedload(Content.sources).joinedload(Source.url_references),
                        joinedload(Content.sources).joinedload(Source.media)
                    )\
                    .filter(Content.profile_id == profile_id)\
                    .filter(Content.is_deleted == False)\
                    .order_by(desc(Content.created_at))

                # Get total count
                total = query.count()

                # Get paginated results
                items = query.offset(skip).limit(limit).all()
                
                return {
                    "items": items,
                    "total": total,
                    "page": skip // limit + 1,
                    "size": limit
                }

        except Exception as e:
            raise e

    def get_content_by_thread(self, thread_id: UUID, profile_id: UUID, content_type_id: Optional[UUID] = None):
        """Get content by thread ID with optional content type filter"""
        try:
            with self.db.session() as session:
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
                if not content:
                    return None

                return content
        except Exception as e:
            raise e

    def update_by_thread(self, thread_id: UUID, profile_id: UUID, data: Dict):
        """Update content by thread ID"""
        with self.db.transaction() as session:
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
                session.flush()
                return content
            return None

    def filter_content(self, profile_id: UUID, filters: Dict, skip: int = 0, limit: int = 10):
        """Filter content with complex criteria"""
        with self.db.session() as session:
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

                # Order by created date descending
            total = subquery.count()
            
            # Get paginated results
            contents = query.offset(skip).limit(limit).all()
            
            return {
                "items": contents,
                "total": total,
                "page": skip // limit + 1,
                "size": limit
            }