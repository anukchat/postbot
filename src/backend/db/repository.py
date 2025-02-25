from typing import Dict, List, Optional, Any, ContextManager
from uuid import UUID
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from .connection import DatabaseConnectionManager, db_retry

class RateLimitExceeded(Exception):
    """Exception raised when a rate limit is exceeded"""
    pass

class QuotaExceeded(Exception):
    """Exception raised when a quota is exceeded"""
    pass

class BaseRepository:
    def __init__(self):
        self.db = DatabaseConnectionManager()

    def _format_error_response(self, error: Exception) -> Dict[str, Any]:
        """Format error responses consistently"""
        return {
            "error": str(error),
            "type": error.__class__.__name__,
            "status": "error"
        }

    def _format_success_response(self, data: Any) -> Dict[str, Any]:
        """Format success responses consistently"""
        return {
            "data": data,
            "status": "success"
        }

    def _validate_response(self, data: Dict[str, Any], response_model: Optional[Type] = None) -> Dict[str, Any]:
        """Validate response against a pydantic model if provided"""
        if response_model and data:
            return response_model(**data).dict()
        return data

    @contextmanager
    def handle_db_errors(self):
        """Context manager for handling database errors consistently"""
        try:
            yield
        except SQLAlchemyError as e:
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    @db_retry(retries=3, delay=1)
    def find_by_id(self, id_field: str, id_value: UUID) -> Optional[Dict]:
        """Find a record by ID field"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT * FROM {self.table_name} WHERE {id_field} = %s",
                        (str(id_value),)
                    )
                    result = cur.fetchone()
                    return result

    @db_retry(retries=3, delay=1)
    def create(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    now = datetime.now()
                    data.setdefault("created_at", now)
                    data.setdefault("updated_at", now)
                    
                    columns = list(data.keys())
                    values = [data[col] for col in columns]
                    placeholders = [f"%s" for _ in columns]
                    
                    query = f"""
                        INSERT INTO {self.table_name} ({', '.join(columns)})
                        VALUES ({', '.join(placeholders)})
                        RETURNING *
                    """
                    cur.execute(query, values)
                    return cur.fetchone()

    @db_retry(retries=3, delay=1)
    def update(self, id_field: str, id_value: UUID, data: Dict[str, Any]) -> Optional[Dict]:
        """Update a record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    data["updated_at"] = datetime.now()
                    set_pairs = [f"{k} = %s" for k in data.keys()]
                    values = list(data.values()) + [str(id_value)]
                    
                    query = f"""
                        UPDATE {self.table_name}
                        SET {', '.join(set_pairs)}
                        WHERE {id_field} = %s
                        RETURNING *
                    """
                    cur.execute(query, values)
                    return cur.fetchone()

    @db_retry(retries=3, delay=1)
    def delete(self, id_field: str, id_value: UUID) -> bool:
        """Hard delete a record"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM {self.table_name} WHERE {id_field} = %s",
                        (str(id_value),)
                    )
                    return cur.rowcount > 0

    @db_retry(retries=3, delay=1)
    def filter(self, filters: Dict[str, Any], skip: int = 0, limit: int = 10) -> List[Dict]:
        """Filter records based on criteria"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    conditions = []
                    values = []
                    
                    for field, value in filters.items():
                        if isinstance(value, (list, tuple)):
                            placeholders = ', '.join(['%s'] * len(value))
                            conditions.append(f"{field} = ANY(%s)")
                            values.append(value)
                        elif value is None:
                            conditions.append(f"{field} IS NULL")
                        else:
                            conditions.append(f"{field} = %s")
                            values.append(value)
                    
                    where_clause = " AND ".join(conditions) if conditions else "TRUE"
                    query = f"""
                        SELECT * FROM {self.table_name}
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                    """
                    values.extend([limit, skip])
                    
                    cur.execute(query, values)
                    return cur.fetchall()

    @db_retry(retries=3, delay=1)
    def exists(self, id_field: str, id_value: UUID) -> bool:
        """Check if a record exists"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT 1 FROM {self.table_name} WHERE {id_field} = %s",
                        (str(id_value),)
                    )
                    return cur.fetchone() is not None

    @db_retry(retries=3, delay=1)
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records optionally filtered"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    conditions = []
                    values = []
                    
                    if filters:
                        for field, value in filters.items():
                            if isinstance(value, (list, tuple)):
                                placeholders = ', '.join(['%s'] * len(value))
                                conditions.append(f"{field} = ANY(%s)")
                                values.append(value)
                            elif value is None:
                                conditions.append(f"{field} IS NULL")
                            else:
                                conditions.append(f"{field} = %s")
                                values.append(value)
                    
                    where_clause = " AND ".join(conditions) if conditions else "TRUE"
                    query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
                    
                    cur.execute(query, values)
                    result = cur.fetchone()
                    return result[0] if result else 0

    @db_retry(retries=3, delay=1)
    def soft_delete(self, id_field: str, id_value: UUID) -> bool:
        """Soft delete a record by setting is_deleted=True"""
        with self.handle_db_errors():
            with self.db.connection() as conn:
                with conn.cursor() as cur:
                    now = datetime.now()
                    query = f"""
                        UPDATE {self.table_name}
                        SET is_deleted = TRUE,
                            deleted_at = %s,
                            updated_at = %s
                        WHERE {id_field} = %s
                    """
                    cur.execute(query, (now, now, str(id_value)))
                    return cur.rowcount > 0

    def batch_create(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Create multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                with conn.cursor() as cur:
                    now = datetime.now()
                    results = []
                    
                    for record in records:
                        record.setdefault("created_at", now)
                        record.setdefault("updated_at", now)
                        
                        columns = list(record.keys())
                        values = [record[col] for col in columns]
                        placeholders = [f"%s" for _ in columns]
                        
                        query = f"""
                            INSERT INTO {self.table_name} ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            RETURNING *
                        """
                        cur.execute(query, values)
                        results.append(cur.fetchone())
                    
                    return results

    def batch_update(self, id_field: str, records: List[Dict[str, Any]]) -> List[Dict]:
        """Update multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                with conn.cursor() as cur:
                    now = datetime.now()
                    results = []
                    
                    for record in records:
                        if id_field not in record:
                            continue
                            
                        id_value = record[id_field]
                        del record[id_field]
                        record["updated_at"] = now
                        
                        set_pairs = [f"{k} = %s" for k in record.keys()]
                        values = list(record.values()) + [str(id_value)]
                        
                        query = f"""
                            UPDATE {self.table_name}
                            SET {', '.join(set_pairs)}
                            WHERE {id_field} = %s
                            RETURNING *
                        """
                        cur.execute(query, values)
                        result = cur.fetchone()
                        if result:
                            results.append(result)
                    
                    return results

    def batch_delete(self, id_field: str, ids: List[UUID]) -> bool:
        """Delete multiple records in a single transaction"""
        with self.handle_db_errors():
            with self.db.transaction() as conn:
                with conn.cursor() as cur:
                    id_strings = [str(id_) for id_ in ids]
                    placeholders = ', '.join(['%s'] * len(id_strings))
                    query = f"DELETE FROM {self.table_name} WHERE {id_field} IN ({placeholders})"
                    cur.execute(query, id_strings)
                    return cur.rowcount > 0

    def check_rate_limit(self, profile_id: UUID, action_type: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if an action is within rate limits"""
        session = self.db.get_session()
        try:
            from .models import RateLimit
            window_start = datetime.now() - timedelta(minutes=window_minutes)
            stmt = select(func.count(RateLimit.rate_limit_id)).where(
                RateLimit.profile_id == profile_id,
                RateLimit.action_type == action_type,
                RateLimit.created_at >= window_start
            )
            result = session.execute(stmt).scalar() < limit
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    def increment_rate_limit(self, profile_id: UUID, action_type: str) -> None:
        """Record a rate-limited action"""
        session = self.db.get_session()
        try:
            from .models import RateLimit
            rate_limit = RateLimit(profile_id=profile_id, action_type=action_type)
            session.add(rate_limit)
            session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def check_quota(self, profile_id: UUID, quota_type: str, period_start: datetime) -> tuple[int, int]:
        """Check quota usage and limit for a profile"""
        session = self.db.get_session()
        try:
            from .models import Quota, QuotaUsage
            # Get quota limit
            quota = session.query(Quota).filter(
                Quota.profile_id == profile_id,
                Quota.quota_type == quota_type
            ).first()
            
            if not quota:
                session.commit()
                return 0, 0

            # Get usage count
            usage = session.query(func.count(QuotaUsage.quota_usage_id)).filter(
                QuotaUsage.profile_id == profile_id,
                QuotaUsage.quota_type == quota_type,
                QuotaUsage.created_at >= period_start
            ).scalar()

            session.commit()
            return usage, quota.limit
        except Exception as e:
            session.rollback()
            raise e

    def increment_quota(self, profile_id: UUID, quota_type: str) -> None:
        """Record quota usage"""
        session = self.db.get_session()
        try:
            from .models import QuotaUsage
            usage = QuotaUsage(profile_id=profile_id, quota_type=quota_type)
            session.add(usage)
            session.flush()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

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
