from typing import Any, Optional, List, Dict
from uuid import UUID

from ..repository import BaseRepository
from datetime import datetime

class SourceRepository(BaseRepository):
    def __init__(self):
        super().__init__("sources")

    def list_sources_with_related(self, profile_id: UUID, type: Optional[str] = None, source_identifier: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[Dict]:
        with self.db.connection() as conn:
            # Build base query with related data
            query = conn.table(self.table_name).select(
                "*,source_types(source_type_id,name),content_sources(content:content_id(content_id,title,thread_id,content_types(name))),url_references(*)"
            ).eq('profile_id', str(profile_id)).order("created_at", desc=True)
            
            # Apply filters
            if type:
                source_type_query = conn.table("source_types").select("source_type_id").eq("name", type).execute()
                if source_type_query.data:
                    source_type_id = source_type_query.data[0]["source_type_id"]
                    query = query.eq("source_type_id", source_type_id)
                else:
                    return []
            
            if source_identifier:
                query = query.ilike("source_identifier", f"%{source_identifier}%")
            
            # Get total count first
            count_response = query.execute()
            total_count = len(count_response.data)
            
            # Then get paginated data
            response = query.range(skip, skip + limit - 1).execute()
            
            # Transform response
            transformed_data = []
            for item in response.data:
                source_type_name = item["source_types"]["name"] if item.get("source_types") else None
                
                # Check if blog content exists and get thread_id
                has_blog = False
                thread_id = None
                for content in item.get("content_sources", []):
                    if content.get("content") and content["content"].get("content_types", {}).get("name") == "blog":
                        has_blog = True
                        thread_id = content["content"].get("thread_id")
                        break

                # Check if source has any URL references
                has_url = bool(item.get("url_references") and len(item["url_references"]) > 0)

                transformed_item = {
                    **item,
                    "source_type": source_type_name,
                    "has_blog": has_blog,
                    "has_url": has_url,
                    "thread_id": thread_id
                }
                del transformed_item["source_types"]
                del transformed_item["content_sources"]
                del transformed_item["url_references"]
                
                transformed_data.append(transformed_item)
                
            return {
                "items": transformed_data,
                "total": total_count,
                "page": skip // limit + 1,
                "size": limit
            }

    def create_source(self, source_data: Dict[str, Any], profile_id: UUID) -> Optional[Dict]:
        source_data['profile_id'] = str(profile_id)
        with self.db.connection() as conn:
            response = conn.table(self.table_name).insert(source_data).execute()
            return response.data[0] if response.data else None

    def soft_delete(self, source_id: UUID, profile_id: UUID) -> bool:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).update({
                "deleted_at": datetime.now().isoformat(),
                "is_deleted": True
            }).eq("source_id", str(source_id)).eq("profile_id", str(profile_id)).execute()
            
            return bool(response.data)