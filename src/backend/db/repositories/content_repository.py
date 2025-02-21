from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid
from ..repository import BaseRepository
from datetime import datetime

class ContentRepository(BaseRepository):
    def __init__(self):
        super().__init__("content")

    def get_content_by_thread(self, thread_id: uuid.UUID, profile_id: uuid.UUID) -> Optional[Dict]:
        with self.db.connection() as conn:
            query = (
                conn.table(self.table_name)
                .select("*, content_type:content_type_id(*)")
                .eq("thread_id", thread_id)
                .eq("profile_id", profile_id)
            )
            response = query.execute()
            return response.data[0] if response.data else None

    def list_content(self, profile_id: UUID, skip: int = 0, limit: int = 10) -> List[Dict]:
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select(
                "*, content_types:content_type_id(content_type_id, name), content_tags(tag_id, tags:tag_id(name)), content_sources(content_source_id, sources:source_id(source_id, source_types(name), url_references(url_reference_id, url, type, domain), media(media_id, media_url, media_type)))"
            ).eq("profile_id", profile_id).order("created_at", desc=True).range(skip, skip + limit)
            
            response = query.execute()
            return response.data if response.data else []

    def filter_content(self, profile_id: UUID, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Dict]:
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select(
                "*, content_types:content_type_id(content_type_id, name), content_tags(tag_id, tags:tag_id(name)), content_sources!inner(content_source_id, source:source_id(source_id, source_identifier, source_types(name), url_references(*), media(*)))"
            ).eq("profile_id", profile_id).order("created_at", desc=True)

            # Apply filters
            if filters.get("title_contains"):
                query = query.ilike("title", f"%{filters['title_contains']}%")
            if filters.get("post_type"):
                query = query.eq("content_types.name", filters["post_type"])
            if filters.get("status"):
                query = query.eq("status", filters["status"])
            if filters.get("domain"):
                query = query.ilike("content_sources.source.url_references.domain", f"%{filters['domain']}%")
            if filters.get("tag_name"):
                query = query.contains("content_tags.tags.name", [filters["tag_name"]])
            if filters.get("source_type"):
                query = query.eq("content_sources.source.source_types.name", filters["source_type"])
            if filters.get("created_after"):
                query = query.gte("created_at", filters["created_after"].isoformat())
            if filters.get("created_before"):
                query = query.lte("created_at", filters["created_before"].isoformat())
            if filters.get("updated_after"):
                query = query.gte("updated_at", filters["updated_after"].isoformat())
            if filters.get("updated_before"):
                query = query.lte("updated_at", filters["updated_before"].isoformat())
            if filters.get("media_type"):
                query = query.eq("content_sources.source.media.media_type", filters["media_type"])
            if filters.get("url_type"):
                query = query.eq("content_sources.source.url_references.type", filters["url_type"])

            query = query.range(skip, skip + limit)
            response = query.execute()
            return response.data if response.data else []

    def save_thread_content(self, thread_id: UUID, profile_id: UUID, content_data: Dict[str, Any], content_type_map: Dict[str, UUID]) -> Dict[str, Any]:
        with self.db.transaction() as conn:
            thread_content = conn.table(self.table_name).select("*").eq("thread_id", thread_id).eq("profile_id", profile_id).execute()
            content_by_type = {item["content_type_id"]: item for item in thread_content.data} if thread_content.data else {}
            
            result = {}
            content_fields = {
                "blog": "content",
                "twitter": "twitter_post",
                "linkedin": "linkedin_post"
            }

            for content_type, field in content_fields.items():
                if content_data.get(field):
                    type_id = content_type_map[content_type]
                    if type_id in content_by_type:
                        # Update existing content
                        update_data = {
                            "body": content_data[field],
                            "status": content_data.get("status", "Draft"),
                            "updated_at": datetime.now().isoformat()
                        }
                        response = conn.table(self.table_name).update(update_data).eq("content_id", content_by_type[type_id]["content_id"]).execute()
                        result[content_type] = response.data[0]
                    else:
                        # Create new content
                        insert_data = {
                            "thread_id": str(thread_id),
                            "profile_id": str(profile_id),
                            "content_type_id": str(type_id),
                            "body": content_data[field],
                            "status": content_data.get("status", "Draft")
                        }
                        if content_type == "blog" and content_data.get("title"):
                            insert_data["title"] = content_data["title"]
                            
                        response = conn.table(self.table_name).insert(insert_data).execute()
                        result[content_type] = response.data[0]

            return result