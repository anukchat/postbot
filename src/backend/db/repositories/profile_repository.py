from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, func
from ..models import Profile, RateLimit, Quota, QuotaUsage
from ..sqlalchemy_repository import SQLAlchemyRepository

class ProfileRepository(SQLAlchemyRepository[Profile]):
    def __init__(self):
        super().__init__(Profile)

    def get_profile_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID"""
        session = self.db.get_session()
        try:
            profile = session.query(Profile).filter(Profile.user_id == user_id).first()
            if profile:
                session.refresh(profile)
                session.commit()
                return profile
            return None
        except Exception as e:
            session.rollback()
            raise e

    def get_with_generation_limits(self, profile_id: UUID) -> Optional[Dict]:
        """Get profile with generation limits info"""
        session = self.db.get_session()
        try:
            profile = (
                session.query(Profile)
                .filter(
                    Profile.profile_id == profile_id,
                    Profile.is_deleted.is_(False)
                )
                .first()
            )
            
            session.commit()
            if profile:
                return {
                    "role": profile.role,
                    "generation_limit": profile.generation_limit,
                    "generations_used": profile.generations_used
                }
            return None
        except Exception as e:
            session.rollback()
            raise e

    def increment_generation_count(self, profile_id: UUID) -> bool:
        """Increment the generation count for a profile"""
        session = self.db.get_session()
        try:
            profile = session.query(Profile).get(profile_id)
            if profile:
                profile.generations_used += 1
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def reset_generation_count(self, profile_id: UUID) -> bool:
        """Reset the generation count for a profile"""
        session = self.db.get_session()
        try:
            profile = session.query(Profile).get(profile_id)
            if profile:
                profile.generations_used = 0
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def update_role(self, profile_id: UUID, new_role: str, new_limit: Optional[int] = None) -> bool:
        """Update profile role and optionally the generation limit"""
        session = self.db.get_session()
        try:
            profile = session.query(Profile).get(profile_id)
            if profile:
                profile.role = new_role
                if new_limit is not None:
                    profile.generation_limit = new_limit
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e

    def get_rate_limits(self, profile_id: UUID, action_type: str, window_minutes: int) -> int:
        """Get rate limit count for a specific action"""
        session = self.db.get_session()
        try:
            window_start = datetime.now() - timedelta(minutes=window_minutes)
            count = (
                session.query(func.count(RateLimit.rate_limit_id))
                .filter(
                    RateLimit.profile_id == profile_id,
                    RateLimit.action_type == action_type,
                    RateLimit.created_at >= window_start
                )
                .scalar()
            )
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e

    def get_quota_usage(self, profile_id: UUID, quota_type: str, period_start: datetime) -> Dict[str, int]:
        """Get quota usage and limit"""
        session = self.db.get_session()
        try:
            # Get quota limit
            quota = (
                session.query(Quota)
                .filter(
                    Quota.profile_id == profile_id,
                    Quota.quota_type == quota_type
                )
                .first()
            )
            
            # Get usage count
            usage_count = (
                session.query(func.count(QuotaUsage.usage_id))
                .filter(
                    QuotaUsage.profile_id == profile_id,
                    QuotaUsage.quota_type == quota_type,
                    QuotaUsage.created_at >= period_start
                )
                .scalar()
            )
            
            session.commit()
            return {
                "limit": quota.limit if quota else 0,
                "used": usage_count
            }
        except Exception as e:
            session.rollback()
            raise e