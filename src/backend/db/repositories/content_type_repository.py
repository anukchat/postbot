from typing import Optional, List, Dict, Any
from uuid import UUID
from ..repository import BaseRepository
from datetime import datetime

class ContentTypeRepository(BaseRepository):
    def __init__(self):
        super().__init__("content_types")

    def get_content_type_id_by_name(self, name: str) -> Optional[UUID]:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).select("content_type_id").eq("name", name).single().execute()
            return UUID(response.data["content_type_id"]) if response.data else None

    def get_content_type_map(self, type_names: List[str]) -> Dict[str, UUID]:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).select("*").in_("name", type_names).execute()
            return {ct["name"]: UUID(ct["content_type_id"]) for ct in response.data} if response.data else {}