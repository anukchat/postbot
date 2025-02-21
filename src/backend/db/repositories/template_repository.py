from typing import Any, Optional, List, Dict
from uuid import UUID
from ..repository import BaseRepository
from datetime import datetime

class TemplateRepository(BaseRepository):
    def __init__(self):
        super().__init__("templates")

    def create_template_with_parameters(self, template_data: Dict[str, Any], parameters: List[Dict[str, Any]]) -> Dict:
        with self.db.transaction() as conn:
            # Set defaults and ensure required fields
            template_data.setdefault("template_type", "default")
            template_data.setdefault("is_deleted", False)
            template_data.setdefault("created_at", datetime.now().isoformat())
            template_data.setdefault("updated_at", datetime.now().isoformat())
            
            # Create template
            template_response = conn.table(self.table_name).insert(template_data).execute()
            if not template_response.data:
                return None
            
            template_id = template_response.data[0]["template_id"]
            
            # Create template parameters
            if parameters:
                params_data = [{
                    "template_id": template_id,
                    "parameter_id": str(param["parameter_id"]),
                    "value_id": str(param["value"]["value_id"]),
                    "created_at": datetime.now().isoformat()
                } for param in parameters]
                
                conn.table("template_parameters").insert(params_data).execute()
            
            return template_response.data[0]

    def get_template_with_parameters(self, template_id: UUID, profile_id: UUID) -> Optional[Dict]:
        with self.db.connection() as conn:
            # Get template with validation
            template_response = conn.table(self.table_name).select("*").eq("template_id", template_id).eq("profile_id", profile_id).execute()
            if not template_response.data:
                return None
            
            # Get parameters with full details
            params_response = conn.table("template_parameters").select(
                "parameter_id, value_id, parameters(name, display_name, description, is_required), parameter_values(value, display_order)"
            ).eq("template_id", template_id).execute()
            
            template = template_response.data[0]
            template["parameters"] = []
            
            for param in params_response.data:
                param_info = param["parameters"]
                value_info = param["parameter_values"]
                
                template["parameters"].append({
                    "parameter_id": param["parameter_id"],
                    "name": param_info["name"],
                    "display_name": param_info["display_name"],
                    "description": param_info.get("description"),
                    "is_required": param_info["is_required"],
                    "value": {
                        "parameter_id": param["parameter_id"],
                        "value_id": param["value_id"],
                        "value": value_info["value"],
                        "display_order": value_info["display_order"]
                    }
                })
            
            return template

    def update_template_with_parameters(self, template_id: UUID, profile_id: UUID, template_data: Dict[str, Any], parameters: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict]:
        with self.db.transaction() as conn:
            # Verify template exists and belongs to profile
            existing = conn.table(self.table_name).select("template_id").eq("template_id", template_id).eq("profile_id", profile_id).single().execute()
            if not existing.data:
                return None

            # Update template
            template_data["updated_at"] = datetime.now().isoformat()
            template_response = conn.table(self.table_name).update(template_data).eq("template_id", template_id).eq("profile_id", profile_id).execute()
            if not template_response.data:
                return None
            
            # Update parameters if provided
            if parameters is not None:
                # Delete existing parameters
                conn.table("template_parameters").delete().eq("template_id", template_id).execute()
                
                # Insert new parameters
                params_data = [{
                    "template_id": template_id,
                    "parameter_id": str(param["parameter_id"]),
                    "value_id": str(param["value"]["value_id"]),
                    "created_at": datetime.now().isoformat()
                } for param in parameters]
                
                if params_data:
                    conn.table("template_parameters").insert(params_data).execute()
            
            return template_response.data[0]

    def list_templates_for_profile(self, profile_id: UUID, skip: int = 0, limit: int = 10, template_type: Optional[str] = None, include_deleted: bool = False) -> List[Dict]:
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select("*").eq("profile_id", profile_id)
            
            if not include_deleted:
                query = query.eq("is_deleted", False)
            if template_type:
                query = query.eq("template_type", template_type)
                
            # Add sorting
            query = query.order("created_at", desc=True)
            
            # Add pagination
            query = query.range(skip, skip + limit - 1)
            response = query.execute()
            return response.data if response.data else []

    def filter_templates(self, profile_id: UUID, parameters: Optional[List[Dict]] = None, template_type: Optional[str] = None, include_deleted: bool = False, skip: int = 0, limit: int = 10) -> List[Dict]:
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select("*, template_parameters!inner(*)").eq("profile_id", profile_id)
            
            # Apply parameter filters
            if parameters:
                for param in parameters:
                    query = query.eq("template_parameters.parameter_id", param["parameter_id"])
                    query = query.eq("template_parameters.value_id", param["value_id"])
            
            # Apply other filters
            if template_type:
                query = query.eq("template_type", template_type)
            if not include_deleted:
                query = query.eq("is_deleted", False)
                
            # Add sorting and pagination
            query = query.order("created_at", desc=True)
            query = query.range(skip, skip + limit - 1)
            
            response = query.execute()
            return response.data if response.data else []

    def count_templates(self, profile_id: UUID, template_type: Optional[str] = None, include_deleted: bool = False) -> int:
        """Count templates for a profile with optional filters"""
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select("*", count="exact").eq("profile_id", profile_id)
            
            if not include_deleted:
                query = query.eq("is_deleted", False)
            if template_type:
                query = query.eq("template_type", template_type)
                
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0

    def duplicate_template(self, template_id: UUID, profile_id: UUID, new_name: str) -> Optional[Dict]:
        """Create a copy of an existing template with its parameters"""
        with self.db.transaction() as conn:
            # Get original template
            template = self.get_template_with_parameters(template_id, profile_id)
            if not template:
                return None
                
            # Create new template
            new_template_data = {
                "name": new_name,
                "description": template["description"],
                "template_type": template["template_type"],
                "template_image_url": template["template_image_url"],
                "profile_id": str(profile_id),
                "is_deleted": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Create duplicate with parameters
            return self.create_template_with_parameters(new_template_data, template["parameters"])