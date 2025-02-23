from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import joinedload
from ..models import Content, ContentType, Source, Tag, URLReference, Media
from ..sqlalchemy_repository import SQLAlchemyRepository

class BlogRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)

    def _format_blog_response(self, content: Content) -> Dict[str, Any]:
        """Format blog response consistently"""
        return {
            "id": str(content.content_id),
            "thread_id": str(content.thread_id) if content.thread_id else None,
            "title": content.title,
            "content": content.body,
            "tags": [tag.name for tag in content.tags],
            "createdAt": content.created_at.isoformat(),
            "updatedAt": content.updated_at.isoformat(),
            "status": content.status,
            "metadata": content.content_metadata or {},
            "sources": [{
                "id": str(source.source_id),
                "type": source.source_type.name if source.source_type else None,
                "identifier": source.source_identifier,
                "urls": [ref.url for ref in source.url_references],
                "media": [{"url": m.media_url, "type": m.media_type} for m in source.media]
            } for source in content.sources]
        }

    def store_blog_content(self, result: Dict[str, Any], thread_id: UUID, source_id: UUID, payload: Dict[str, Any], user: Dict[str, Any]) -> None:
        """Store blog content with related data"""
        with self.db.transaction() as session:
            # Get content type for blog
            content_type = (
                session.query(ContentType)
                .filter(ContentType.name == 'blog')
                .first()
            )
            if not content_type:
                raise ValueError("Blog content type not found")

            # Get or create tags
            from .tag_repository import TagRepository
            tag_repo = TagRepository()
            tags = tag_repo.get_or_create_tags(session, result.get('tags', []))

            # Get source
            source = session.query(Source).get(source_id)
            if not source:
                raise ValueError(f"Source {source_id} not found")

            # Create blog content
            blog_data = {
                'thread_id': thread_id,
                'profile_id': user['profile_id'],
                'content_type_id': content_type.content_type_id,
                'title': result.get('blog_title', ''),
                'body': result['final_blog'],
                'status': payload.get('status', 'draft'),
                'content_metadata': {
                    'original_source': str(source_id),
                    'generation_params': payload.get('params', {}),
                    'version': payload.get('version', '1.0')
                }
            }

            blog = self.create(session, blog_data)
            blog.tags = tags
            blog.sources.append(source)
            session.flush()

    def fetch_urls_and_media(self, tweet_id: str) -> Dict[str, Any]:
        """Fetch URLs and media for a tweet source"""
        with self.db.session() as session:
            source = (
                session.query(Source)
                .options(
                    joinedload(Source.url_references),
                    joinedload(Source.media)
                )
                .join(Source.source_type)
                .filter(
                    Source.source_identifier == tweet_id,
                    Source.is_deleted.is_(False)
                )
                .first()
            )
            
            if not source:
                raise ValueError(f"No source found for tweet {tweet_id}")
            
            return {
                "source_id": str(source.source_id),
                "url_references": [
                    {
                        "url": ref.url,
                        "type": ref.type,
                        "domain": ref.domain
                    } for ref in source.url_references
                ],
                "media": [
                    {
                        "url": media.media_url,
                        "type": media.media_type
                    } for media in source.media
                ]
            }

    def get_blog_by_thread(self, thread_id: UUID, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """Get blog content by thread ID"""
        with self.db.session() as session:
            blog = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .join(Content.content_type)
                .filter(
                    Content.thread_id == thread_id,
                    Content.profile_id == profile_id,
                    ContentType.name == 'blog',
                    Content.is_deleted.is_(False)
                )
                .first()
            )
            
            return self._format_blog_response(blog) if blog else None

    def list_blogs(self, profile_id: UUID, skip: int = 0, limit: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        """List blogs with pagination and optional status filter"""
        with self.db.session() as session:
            query = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .join(Content.content_type)
                .filter(
                    Content.profile_id == profile_id,
                    ContentType.name == 'blog',
                    Content.is_deleted.is_(False)
                )
            )

            if status:
                query = query.filter(Content.status == status)

            total = query.count()
            blogs = (
                query
                .order_by(desc(Content.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return {
                "items": [self._format_blog_response(blog) for blog in blogs],
                "total": total,
                "page": skip // limit + 1,
                "size": limit
            }

    def search_blogs(self, profile_id: UUID, query: str, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Search blogs by title or content"""
        with self.db.session() as session:
            search_query = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .join(Content.content_type)
                .filter(
                    Content.profile_id == profile_id,
                    ContentType.name == 'blog',
                    Content.is_deleted.is_(False),
                    or_(
                        Content.title.ilike(f'%{query}%'),
                        Content.body.ilike(f'%{query}%')
                    )
                )
            )

            total = search_query.count()
            blogs = (
                search_query
                .order_by(desc(Content.created_at))
                .offset(skip)
                .limit(limit)
                .all()
            )

            return {
                "items": [self._format_blog_response(blog) for blog in blogs],
                "total": total,
                "page": skip // limit + 1,
                "size": limit
            }

    def update_blog(self, thread_id: UUID, profile_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update blog content"""
        with self.db.transaction() as session:
            blog = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources)
                )
                .join(Content.content_type)
                .filter(
                    Content.thread_id == thread_id,
                    Content.profile_id == profile_id,
                    ContentType.name == 'blog',
                    Content.is_deleted.is_(False)
                )
                .first()
            )

            if not blog:
                return None

            # Update basic fields
            for key in ['title', 'body', 'status']:
                if key in data:
                    setattr(blog, key, data[key])

            # Update tags if provided
            if 'tags' in data:
                from .tag_repository import TagRepository
                tag_repo = TagRepository()
                blog.tags = tag_repo.get_or_create_tags(session, data['tags'])

            # Update metadata if provided
            if 'metadata' in data:
                blog.content_metadata = {**(blog.content_metadata or {}), **data['metadata']}

            blog.updated_at = datetime.now()
            session.flush()

            return self._format_blog_response(blog)