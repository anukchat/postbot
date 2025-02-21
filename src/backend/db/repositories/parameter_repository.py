from typing import Optional, List, Dict, Any
from uuid import UUID
from ..repository import BaseRepository
from datetime import datetime

class ParameterRepository(BaseRepository):
    def __init__(self):
        super().__init__("parameters")

    def get_parameter_with_values(self, parameter_id: UUID) -> Optional[Dict]:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).select("*, parameter_values(*)").eq("parameter_id", parameter_id).execute()
            return response.data[0] if response.data else None

    def list_parameters_with_values(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).select("*, parameter_values(*)").range(skip, skip + limit - 1).execute()
            return response.data if response.data else []

    def create_parameter_value(self, parameter_id: UUID, value: str, display_order: int = 0) -> Optional[Dict]:
        with self.db.transaction() as conn:
            if display_order == 0:
                # Get max display order
                response = conn.table("parameter_values").select("display_order").eq("parameter_id", str(parameter_id)).order("display_order", desc=True).limit(1).execute()
                max_order = response.data[0]["display_order"] if response.data else 0
                display_order = max_order + 1
            else:
                # Check if display order exists
                existing = conn.table("parameter_values").select("value_id").eq("parameter_id", str(parameter_id)).eq("display_order", display_order).execute()
                if existing.data:
                    raise ValueError(f"Display order {display_order} already exists for this parameter")

            response = conn.table("parameter_values").insert({
                "parameter_id": str(parameter_id),
                "value": value,
                "display_order": display_order
            }).execute()
            return response.data[0] if response.data else None

    def update_parameter_value(self, value_id: UUID, parameter_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict]:
        with self.db.connection() as conn:
            if "display_order" in update_data:
                # Check if new display order exists
                existing = conn.table("parameter_values").select("value_id").eq("parameter_id", str(parameter_id)).eq("display_order", update_data["display_order"]).execute()
                if existing.data and str(existing.data[0]["value_id"]) != str(value_id):
                    raise ValueError(f"Display order {update_data['display_order']} already exists for this parameter")

            response = conn.table("parameter_values").update(update_data).eq("value_id", str(value_id)).execute()
            return response.data[0] if response.data else None
            
    def delete_parameter_value(self, value_id: UUID, parameter_id: UUID) -> bool:
        with self.db.connection() as conn:
            response = conn.table("parameter_values").delete().eq("value_id", str(value_id)).eq("parameter_id", str(parameter_id)).execute()
            return bool(response.data)
            
    def create_parameter(self, parameter_data: Dict[str, Any]) -> Optional[Dict]:
        parameter_data.setdefault("is_required", True)
        with self.db.connection() as conn:
            response = conn.table(self.table_name).insert(parameter_data).execute()
            return response.data[0] if response.data else None
            
    def update_parameter(self, parameter_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict]:
        with self.db.connection() as conn:
            response = conn.table(self.table_name).update(update_data).eq("parameter_id", str(parameter_id)).execute()
            return response.data[0] if response.data else None
            
    def delete_parameter(self, parameter_id: UUID) -> bool:
        with self.db.transaction() as conn:
            # Delete parameter values first
            conn.table("parameter_values").delete().eq("parameter_id", str(parameter_id)).execute()
            # Delete parameter
            response = conn.table(self.table_name).delete().eq("parameter_id", str(parameter_id)).execute()
            return bool(response.data)