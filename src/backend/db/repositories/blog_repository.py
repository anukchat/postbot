from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import joinedload
from ..models import Content, ContentType, Source, SourceMetadata, Tag, URLReference, Media
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..connection import db_retry

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

    @db_retry
    def store_blog_content(self, result: Dict[str, Any], thread_id: UUID, source_id: UUID, 
                          payload: Dict[str, Any], user: Dict[str, Any]) -> None:
        """Store blog content with related data"""
        session = self.db.get_session()
        try:
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

            # Get source using base repository method
            source = self.find_by_field("source_id", source_id)
            if not source:
                raise ValueError(f"Source not found with ID: {source_id}")

            # Create content record
            content = Content(
                profile_id=user["profile_id"],
                content_type_id=content_type.id,
                thread_id=thread_id,
                title=result.get("blog_title", "").strip(),
                body=result.get("final_blog", "").strip(),
                status="Draft",
                content_metadata=payload.get("metadata", {})
            )

            session.add(content)
            session.flush()

            # Associate tags with content
            content.tags = tags

            # Associate source with content
            content.sources.append(source)

            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def fetch_urls_and_media(self, tweet_id: str) -> Dict[str, Any]:
        """Fetch URLs and media for a tweet source"""
        session = self.db.get_session()
        try:
            source = (
                session.query(Source)
                .options(
                    joinedload(Source.url_references),
                    joinedload(Source.media)
                )
                .filter(Source.source_identifier == tweet_id)
                .first()
            )

            if not source:
                raise ValueError(f"No source found for tweet_id: {tweet_id}")

            return {
                "source_id": str(source.source_id),
                "urls": [{"url": ref.url, "type": ref.type} for ref in source.url_references],
                "media": [{"url": m.media_url, "type": m.media_type} for m in source.media]
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_blog_by_thread(self, thread_id: UUID, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """Get blog content by thread ID"""
        session = self.db.get_session()
        try:
            content = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .filter(
                    Content.thread_id == thread_id,
                    Content.profile_id == profile_id
                )
                .first()
            )
            
            if content:
                return self._format_blog_response(content)
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def list_blogs(self, profile_id: UUID, skip: int = 0, limit: int = 10, 
                   status: Optional[str] = None) -> Dict[str, Any]:
        """List blogs with pagination and optional status filter"""
        session = self.db.get_session()
        try:
            query = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .filter(Content.profile_id == profile_id)
                .order_by(desc(Content.created_at))
            )

            if status:
                query = query.filter(Content.status == status)

            total = query.count()
            blogs = query.offset(skip).limit(limit).all()

            return {
                "total": total,
                "items": [self._format_blog_response(blog) for blog in blogs]
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def search_blogs(self, profile_id: UUID, query: str, skip: int = 0, 
                     limit: int = 10) -> Dict[str, Any]:
        """Search blogs by title or content"""
        session = self.db.get_session()
        try:
            search_query = (
                session.query(Content)
                .options(
                    joinedload(Content.tags),
                    joinedload(Content.sources).joinedload(Source.source_type),
                    joinedload(Content.sources).joinedload(Source.url_references),
                    joinedload(Content.sources).joinedload(Source.media)
                )
                .filter(
                    Content.profile_id == profile_id,
                    or_(
                        Content.title.ilike(f"%{query}%"),
                        Content.body.ilike(f"%{query}%")
                    )
                )
                .order_by(desc(Content.created_at))
            )

            total = search_query.count()
            blogs = search_query.offset(skip).limit(limit).all()

            return {
                "total": total,
                "items": [self._format_blog_response(blog) for blog in blogs]
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def update_blog(self, thread_id: UUID, profile_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update blog content"""
        session = self.db.get_session()
        try:
            content = (
                session.query(Content)
                .filter(
                    Content.thread_id == thread_id,
                    Content.profile_id == profile_id
                )
                .first()
            )

            if not content:
                return None

            # Update allowed fields
            content.title = data.get('title', content.title)
            content.body = data.get('body', content.body)
            content.status = data.get('status', content.status)
            content.content_metadata = data.get('metadata', content.content_metadata)
            content.updated_at = datetime.now()

            # Update tags if provided
            if 'tags' in data:
                from .tag_repository import TagRepository
                tag_repo = TagRepository()
                tags = tag_repo.get_or_create_tags(session, data['tags'])
                content.tags = tags

            session.commit()
            return self._format_blog_response(content)
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry  
    def get_source_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get source by identifier"""
        session = self.db.get_session()
        try:
            source = (
                session.query(Source)
                .filter(Source.source_identifier == identifier)
                .first()
            )
            if source:
                return {
                    "source_id": str(source.source_id),
                    "identifier": source.source_identifier,
                    "type": source.source_type.name if source.source_type else None
                }
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def setup_web_url_source(self, url: str, thread_id: UUID, user: Dict[str, Any], 
                            url_meta: Dict[str, Any], media_meta: List[Dict[str, Any]]) -> UUID:
        """Setup source records for web URL"""
        session = self.db.get_session()
        try:
            # Check existing source
            existing_source = (
                session.query(Source)
                .filter(
                    Source.source_identifier == url,
                    Source.profile_id == user["profile_id"]
                )
                .first()
            )

            if existing_source:
                # Validate no existing content
                if self._has_existing_content(existing_source.source_id):
                    raise ValueError("Content already exists for this URL")
                return existing_source.source_id

            # Create new source
            source = Source(
                source_type_id=self._get_source_type_id("web_url"),
                source_identifier=url,
                batch_id=str(thread_id),
                profile_id=user["profile_id"]
            )
            session.add(source)
            session.flush()

            # Add URL reference
            url_ref = URLReference(
                source_id=source.source_id,
                url=url_meta["original_url"],
                type=url_meta["type"],
                domain=url_meta.get("domain"),
                content_type=url_meta.get("content_type"),
                file_category=url_meta.get("file_category")
            )
            session.add(url_ref)

            # Add media
            for media in media_meta:
                media_obj = Media(
                    source_id=source.source_id,
                    media_url=media["original_url"],
                    media_type=media["type"]
                )
                session.add(media_obj)

            session.commit()
            return source.source_id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _has_existing_content(self, source_id: UUID) -> bool:
        """Check if content exists for source"""
        session = self.db.get_session()
        try:
            return (
                session.query(Content)
                .join(Content.sources)
                .filter(Source.source_id == source_id)
                .first()
            ) is not None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _get_source_type_id(self, type_name: str) -> UUID:
        """Get source type ID by name"""
        session = self.db.get_session()
        try:
            source_type = (
                session.query(ContentType)
                .filter(ContentType.name == type_name)
                .first()
            )
            if not source_type:
                raise ValueError(f"Source type '{type_name}' not found")
            return source_type.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_url_references(self, source_id: UUID) -> List[Dict[str, Any]]:
        """Fetch URL references for a source"""
        session = self.db.get_session()
        try:
            references = (
                session.query(URLReference)
                .filter(URLReference.source_id == source_id)
                .all()
            )
            return [
                {
                    "url": ref.url,
                    "type": ref.type,
                    "domain": ref.domain,
                    "content_type": ref.content_type,
                    "file_category": ref.file_category
                }
                for ref in references
            ]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_media(self, source_id: UUID) -> List[Dict[str, Any]]:
        """Fetch media for a source"""
        session = self.db.get_session()
        try:
            media_list = (
                session.query(Media)
                .filter(Media.source_id == source_id)
                .all()
            )
            return [
                {
                    "url": media.media_url,
                    "type": media.media_type
                }
                for media in media_list
            ]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_source_metadata(self, source_id: UUID) -> List[Dict[str, Any]]:
        """Fetch metadata for a source"""
        session = self.db.get_session()
        try:
            metadata_list = (
                session.query(SourceMetadata)
                .filter(SourceMetadata.source_id == source_id)
                .all()
            )
            return [
                {
                    "key": meta.key,
                    "value": meta.value,
                }
                for meta in metadata_list
            ]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_content_by_source_id(self, source_id: UUID) -> Optional[Dict[str, Any]]:
        """Get content by source ID"""
        session = self.db.get_session()
        try:
            content = (
                session.query(Content)
                .join(Content.sources)
                .filter(Source.source_id == source_id)
                .first()
            )
            return self._format_blog_response(content) if content else None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def setup_topic_source(self, topic: str, urls: List[str], thread_id: UUID, user: Dict[str, Any]) -> UUID:
        """Setup source records for topic-based search"""
        session = self.db.get_session()
        try:
            # Check existing source
            existing_source = (
                session.query(Source)
                .filter(
                    Source.source_identifier == topic,
                    Source.profile_id == user["profile_id"]
                )
                .first()
            )

            if existing_source:
                if self._has_existing_content(existing_source.source_id):
                    raise ValueError("Content already exists for this topic")
                return existing_source.source_id

            # Create new source
            source = Source(
                source_type_id=self._get_source_type_id("topic"),
                source_identifier=topic,
                batch_id=str(thread_id),
                profile_id=user["profile_id"]
            )
            session.add(source)
            session.flush()

            # Add URL references
            for url in urls:
                url_ref = URLReference(
                    source_id=source.source_id,
                    url=url,
                    type="web",
                )
                session.add(url_ref)

            session.commit()
            return source.source_id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def setup_reddit_source(self, payload: Dict[str, Any], thread_id: UUID, user: Dict[str, Any]) -> UUID:
        """Setup source records for Reddit-based content"""
        session = self.db.get_session()
        try:
            query = payload["reddit_query"]
            # Check existing source
            existing_source = (
                session.query(Source)
                .filter(
                    Source.source_identifier == query,
                    Source.profile_id == user["profile_id"]
                )
                .first()
            )

            if existing_source:
                if self._has_existing_content(existing_source.source_id):
                    raise ValueError("Content already exists for this Reddit query")
                return existing_source.source_id

            # Create new source
            source = Source(
                source_type_id=self._get_source_type_id("reddit"),
                source_identifier=query,
                batch_id=str(thread_id),
                profile_id=user["profile_id"]
            )
            session.add(source)
            session.flush()

            session.commit()
            return source.source_id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def setup_tweet_source(self, tweet_id: str, thread_id: UUID, user: Dict[str, Any]) -> UUID:
        """Setup source records for tweet-based content"""
        session = self.db.get_session()
        try:
            # Check existing source
            existing_source = (
                session.query(Source)
                .filter(
                    Source.source_identifier == tweet_id,
                    Source.profile_id == user["profile_id"]
                )
                .first()
            )

            if existing_source:
                if self._has_existing_content(existing_source.source_id):
                    raise ValueError("Content already exists for this tweet")
                return existing_source.source_id

            # Create new source
            source = Source(
                source_type_id=self._get_source_type_id("tweet"),
                source_identifier=tweet_id,
                batch_id=str(thread_id),
                profile_id=user["profile_id"]
            )
            session.add(source)
            session.flush()

            session.commit()
            return source.source_id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def create_url_reference(self, source_id: UUID, url_meta: Dict[str, Any]) -> None:
        """Create URL reference for a source"""
        session = self.db.get_session()
        try:
            url_ref = URLReference(
                source_id=source_id,
                url=url_meta["original_url"],
                type=url_meta["type"],
                domain=url_meta.get("domain"),
                content_type=url_meta.get("content_type"),
                file_category=url_meta.get("file_category")
            )
            session.add(url_ref)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def _handle_media_storage(self, source_id: UUID, media_meta: List[Dict[str, Any]]) -> None:
        """Handle batch media storage in a single transaction"""
        if not media_meta:
            return
            
        session = self.db.get_session()
        try:
            media_records = [
                Media(
                    source_id=source_id,
                    media_url=media["original_url"],
                    media_type=media["type"]
                )
                for media in media_meta
            ]
            session.bulk_save_objects(media_records)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()