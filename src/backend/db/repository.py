from typing import Any, Optional, List, Dict, TypeVar, Generic, Callable
from uuid import UUID
from .connection import DatabaseConnectionManager, db_retry
from datetime import datetime, timedelta
from contextlib import contextmanager
from postgrest.exceptions import APIError

T = TypeVar('T')

class RateLimitExceeded(Exception):
    """Exception raised when a rate limit is exceeded"""
    pass

class QuotaExceeded(Exception):
    """Exception raised when a quota is exceeded"""
    pass

class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = DatabaseConnectionManager()

    @contextmanager
    def handle_db_errors(self):
        """Context manager for handling database errors consistently"""
        try:
            yield
        except APIError as e:
            # Handle Postgrest specific errors
            if "Foreign key violation" in str(e):
                raise ValueError("Referenced record does not exist")
            if "duplicate key" in str(e):
                raise ValueError("Record already exists")
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    @db_retry(retries=3, delay=1)
    def find_by_id(self, id_field: str, id_value: UUID) -> Optional[Dict]:
        """Find a record by ID field"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                response = conn.table(self.table_name).select("*").eq(id_field, str(id_value)).single().execute()
                return response.data if response.data else None

    @db_retry(retries=3, delay=1)
    def create(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                data.setdefault("created_at", datetime.now().isoformat())
                data.setdefault("updated_at", datetime.now().isoformat())
                response = conn.table(self.table_name).insert(data).execute()
                return response.data[0] if response.data else None

    @db_retry(retries=3, delay=1)
    def update(self, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Dict]:
        """Update a record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                data["updated_at"] = datetime.now().isoformat()
                response = conn.table(self.table_name).update(data).eq(id_field, str(id_value)).execute()
                return response.data[0] if response.data else None

    @db_retry(retries=3, delay=1)
    def delete(self, id_field: str, id_value: UUID) -> bool:
        """Hard delete a record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                response = conn.table(self.table_name).delete().eq(id_field, str(id_value)).execute()
                return bool(response.data)

    @db_retry(retries=3, delay=1)
    def filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Dict]:
        """Filter records based on criteria"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                query = conn.table(self.table_name).select("*")
                
                # Apply filters
                for field, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(field, value)
                    elif value is None:
                        query = query.is_("is", "null")
                    else:
                        query = query.eq(field, value)
                        
                # Apply pagination
                query = query.range(skip, skip + limit - 1)
                response = query.execute()
                return response.data if response.data else []

    @db_retry(retries=3, delay=1)
    def exists(self, id_field: str, id_value: UUID) -> bool:
        """Check if a record exists"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                response = conn.table(self.table_name).select("1").eq(id_field, str(id_value)).execute()
                return bool(response.data)

    @db_retry(retries=3, delay=1)
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records optionally filtered"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                query = conn.table(self.table_name).select("*", count="exact")
                
                if filters:
                    for field, value in filters.items():
                        if isinstance(value, (list, tuple)):
                            query = query.in_(field, value)
                        elif value is None:
                            query = query.is_("is", "null")
                        else:
                            query = query.eq(field, value)
                            
                response = query.execute()
                return response.count if hasattr(response, 'count') else 0

    @db_retry(retries=3, delay=1)
    def soft_delete(self, id_field: str, id_value: UUID) -> bool:
        """Soft delete a record by setting is_deleted=True"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                response = conn.table(self.table_name).update({
                    "is_deleted": True,
                    "deleted_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }).eq(id_field, str(id_value)).execute()
                return bool(response.data)

    def batch_create(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Create multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                now = datetime.now().isoformat()
                for record in records:
                    record.setdefault("created_at", now)
                    record.setdefault("updated_at", now)
                response = conn.table(self.table_name).insert(records).execute()
                return response.data if response.data else []

    def batch_update(self, id_field: str, records: List[Dict[str, Any]]) -> List[Dict]:
        """Update multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                now = datetime.now().isoformat()
                updated = []
                for record in records:
                    if id_field not in record:
                        continue
                    id_value = record[id_field]
                    del record[id_field]
                    record["updated_at"] = now
                    response = conn.table(self.table_name).update(record).eq(id_field, str(id_value)).execute()
                    if response.data:
                        updated.extend(response.data)
                return updated

    def batch_delete(self, id_field: str, ids: List[UUID]) -> bool:
        """Delete multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                response = conn.table(self.table_name).delete().in_(id_field, [str(id_) for id_ in ids]).execute()
                return bool(response.data)

    def check_rate_limit(self, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if an action is within rate limits for a profile"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                window_start = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()
                
                response = conn.table("rate_limits").select(
                    "count", 
                    count="exact"
                ).eq("profile_id", str(profile_id)
                ).eq("action_type", action_type
                ).gte("created_at", window_start).execute()
                
                count = response.count if hasattr(response, 'count') else 0
                return count < limit

    def increment_rate_limit(self, profile_id: UUID, action_type: str) -> None:
        """Record a rate-limited action"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                conn.table("rate_limits").insert({
                    "profile_id": str(profile_id),
                    "action_type": action_type,
                    "created_at": datetime.now().isoformat()
                }).execute()

    def check_quota(self, profile_id: UUID, quota_type: str, current_period_start: datetime) -> tuple[int, int]:
        """Check quota usage and limit for a profile"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                # First get the profile's role
                profile = conn.table("profiles").select(
                    "role"
                ).eq("id", str(profile_id)).single().execute()
                
                if not profile.data:
                    raise ValueError("Profile not found")
                
                # Get quota limit from generation_limits table
                limits = conn.table("generation_limits").select(
                    "max_generations"
                ).eq("tier", profile.data["role"]).single().execute()
                
                if not limits.data:
                    raise ValueError(f"No limits found for tier {profile.data['role']}")

                # Get usage count
                usage = conn.table("quota_usage").select(
                    "count",
                    count="exact"
                ).eq("profile_id", str(profile_id)
                ).eq("quota_type", quota_type
                ).gte("created_at", current_period_start.isoformat()).execute()
                
                limit = limits.data["max_generations"]
                used = usage.count if hasattr(usage, 'count') else 0
                return used, limit

    def increment_quota(self, profile_id: UUID, quota_type: str) -> None:
        """Record quota usage"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                conn.table("quota_usage").insert({
                    "profile_id": str(profile_id),
                    "quota_type": quota_type,
                    "created_at": datetime.now().isoformat()
                }).execute()

    @contextmanager
    def rate_limited_operation(self, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60):
        """Context manager for rate-limited operations"""
        if not self.check_rate_limit(profile_id, action_type, limit, window_minutes):
            raise RateLimitExceeded(f"Rate limit exceeded for {action_type}")
        
        try:
            yield
            self.increment_rate_limit(profile_id, action_type)
        except Exception as e:
            raise e

    @contextmanager
    def quota_limited_operation(self, profile_id: UUID, quota_type: str, period_start: datetime):
        """Context manager for quota-limited operations"""
        used, limit = self.check_quota(profile_id, quota_type, period_start)
        if used >= limit:
            raise QuotaExceeded(f"Quota exceeded for {quota_type}")
        
        try:
            yield
            self.increment_quota(profile_id, quota_type)
        except Exception as e:
            raise e
