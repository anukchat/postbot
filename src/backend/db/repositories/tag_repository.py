from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from ..models import Tag
from ..sqlalchemy_repository import SQLAlchemyRepository

class TagRepository(SQLAlchemyRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)

    def get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """Get existing tags or create new ones"""
        session = self.db.get_session()
        try:
            # Get existing tags
            existing_tags = (
                session.query(Tag)
                .filter(
                    Tag.name.in_(tag_names),
                    Tag.is_deleted.is_(False)
                )
                .all()
            )
            
            existing_names = {tag.name for tag in existing_tags}
            new_names = set(tag_names) - existing_names
            
            # Create new tags
            for name in new_names:
                tag = Tag(name=name)
                session.add(tag)
                existing_tags.append(tag)
            
            session.commit()
            return existing_tags
        except Exception as e:
            session.rollback()
            raise e

    def get_popular_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used tags"""
        session = self.db.get_session()
        try:
            from ..models import content_tags
            from sqlalchemy import func
            
            result = (
                session.query(
                    Tag,
                    func.count(content_tags.c.tag_id).label('usage_count')
                )
                .join(content_tags)
                .filter(Tag.is_deleted.is_(False))
                .group_by(Tag.tag_id)
                .order_by(desc('usage_count'))
                .limit(limit)
                .all()
            )
            
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def search_tags(self, query: str, limit: int = 10) -> List[Tag]:
        """Search tags by name"""
        session = self.db.get_session()
        try:
            tags = (
                session.query(Tag)
                .filter(
                    Tag.name.ilike(f'%{query}%'),
                    Tag.is_deleted.is_(False)
                )
                .order_by(Tag.name)
                .limit(limit)
                .all()
            )
            
            session.commit()
            return tags
        except Exception as e:
            session.rollback()
            raise e

    def merge_tags(self, source_tag_id: UUID, target_tag_id: UUID) -> bool:
        """Merge one tag into another"""
        session = self.db.get_session()
        try:
            from ..models import content_tags
            
            # Update content_tags references
            session.execute(
                content_tags.update()
                .where(content_tags.c.tag_id == source_tag_id)
                .values(tag_id=target_tag_id)
            )
            
            # Soft delete the source tag
            return self.soft_delete("tag_id", source_tag_id)
        except Exception as e:
            session.rollback()
            raise e