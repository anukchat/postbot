from typing import Optional, List, Dict, Any
from uuid import UUID
from ..repository import BaseRepository, QuotaExceeded
from datetime import datetime

class ProfileRepository(BaseRepository):
    def __init__(self):
        super().__init__("profiles")

    def get_with_generation_limits(self, profile_id: UUID) -> Optional[Dict]:
        """Get profile with generation limits and usage"""
        with self.db.connection() as conn:
            # First get profile details
            response = conn.table(self.table_name).select("*").eq("id", str(profile_id)).single().execute()
            if not response.data:
                return None
                
            profile = response.data
            
            # Get generation limit for the profile's role
            limits_response = conn.table("generation_limits").select("max_generations").eq("tier", profile["role"]).single().execute()
            if not limits_response.data:
                return None
                
            profile["generation_limit"] = limits_response.data["max_generations"]
            return profile

    def increment_generation_count(self, profile_id: UUID) -> bool:
        """Increment the generation count and check against limits"""
        with self.db.connection() as conn:
            # Get current profile with limits
            profile = self.get_with_generation_limits(profile_id)
            if not profile:
                return False
                
            current_count = profile.get("generations_used", 0)
            generation_limit = profile.get("generation_limit", 0)
            
            # Check if user has reached their limit
            if current_count >= generation_limit:
                raise QuotaExceeded(f"Generation limit of {generation_limit} reached for {profile['role']} tier")
            
            # Increment count
            update_response = conn.table(self.table_name).update({
                "generations_used": current_count + 1,
                "updated_at": datetime.now().isoformat()
            }).eq("id", str(profile_id)).execute()
            
            return bool(update_response.data)

    def reset_generation_count(self, profile_id: UUID) -> bool:
        """Reset the generation count for a profile (useful for monthly resets)"""
        with self.db.connection() as conn:
            update_response = conn.table(self.table_name).update({
                "generations_used": 0,
                "updated_at": datetime.now().isoformat()
            }).eq("id", str(profile_id)).execute()
            
            return bool(update_response.data)

    def create(self, profile_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new profile with default values"""
        profile_data.setdefault("generations_used", 0)
        profile_data.setdefault("role", "free")
        profile_data.setdefault("subscription_status", "none")
        profile_data.setdefault("is_deleted", False)
        
        with self.db.connection() as conn:
            response = conn.table(self.table_name).insert(profile_data).execute()
            return response.data[0] if response.data else None

    def update(self, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Dict]:
        """Update a profile ensuring certain fields cannot be directly modified"""
        protected_fields = {"generations_used", "role", "subscription_status"}
        update_data = {k: v for k, v in data.items() if k not in protected_fields}
        update_data["updated_at"] = datetime.now().isoformat()
        
        with self.db.connection() as conn:
            response = conn.table(self.table_name).update(update_data).eq(id_field, str(id_value)).execute()
            return response.data[0] if response.data else None

    def filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Dict]:
        """Filter profiles based on criteria"""
        with self.db.connection() as conn:
            query = conn.table(self.table_name).select("*").eq("is_deleted", False)
            
            # Apply filters
            for field, value in filters.items():
                query = query.eq(field, value)
                
            # Apply pagination
            query = query.range(skip, skip + limit - 1)
            response = query.execute()
            return response.data if response.data else []