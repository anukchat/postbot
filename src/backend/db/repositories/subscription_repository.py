from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import desc
from ..models import Content, Profile
from ..sqlalchemy_repository import SQLAlchemyRepository
from ..connection import db_retry

class SubscriptionRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)
    
    @db_retry
    def get_active_subscription(self, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """Get active subscription for a profile"""
        session = self.db.get_session()
        try:
            subscription = (
                session.query(Content)
                .join(Content.profile)
                .filter(
                    Content.profile_id == profile_id,
                    Content.content_type_id == self.get_subscription_type_id(),
                    Content.status == 'active',
                    Content.is_deleted.is_(False)
                )
                .first()
            )
            return subscription.to_dict() if subscription else None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def create_subscription(self, profile_id: UUID, plan_id: UUID, start_date: datetime, 
                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a new subscription"""
        session = self.db.get_session()
        try:
            existing = self.get_active_subscription(profile_id)
            if existing:
                raise ValueError("Active subscription already exists")

            subscription_data = {
                'profile_id': profile_id,
                'content_type_id': self.get_subscription_type_id(),
                'title': f'Subscription Plan {plan_id}',
                'status': 'active',
                'content_metadata': {
                    'plan_id': str(plan_id),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            subscription = super().create(subscription_data)
            return subscription.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def cancel_subscription(self, subscription_id: UUID) -> bool:
        """Cancel a subscription"""
        session = self.db.get_session()
        try:
            subscription = self.find_by_field(session, "content_id", subscription_id)
            if subscription:
                subscription.status = 'cancelled'
                subscription.updated_at = datetime.now()
                session.flush()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def record_payment(self, subscription_id: UUID, amount: float, 
                    payment_method: str) -> Dict[str, Any]:
        """Record a payment for a subscription"""
        session = self.db.get_session()
        try:
            subscription = self.find_by_field(session, "content_id", subscription_id)
            if not subscription:
                raise ValueError("Subscription not found")
            
            payment_data = {
                'amount': amount,
                'payment_method': payment_method,
                'date': datetime.now().isoformat()
            }
            
            if not subscription.content_metadata:
                subscription.content_metadata = {}
            
            if 'payments' not in subscription.content_metadata:
                subscription.content_metadata['payments'] = []
            
            subscription.content_metadata['payments'].append(payment_data)
            subscription.updated_at = datetime.now()
            session.flush()
            
            return subscription.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def get_subscription_stats(self, profile_id: UUID) -> Dict[str, Any]:
        """Get subscription usage statistics"""
        session = self.db.get_session()
        try:
            active_sub = (
                session.query(Content)
                .filter(
                    Content.profile_id == profile_id,
                    Content.content_type_id == self.get_subscription_type_id(),
                    Content.status == 'active',
                    Content.is_deleted.is_(False)
                )
                .first()
            )
            
            if not active_sub:
                return {
                    'has_active_subscription': False,
                    'usage': 0,
                    'limit': 0
                }
            
            metadata = active_sub.content_metadata or {}
            return {
                'has_active_subscription': True,
                'plan_id': metadata.get('plan_id'),
                'start_date': metadata.get('start_date'),
                'end_date': metadata.get('end_date'),
                'payments': metadata.get('payments', []),
                'usage': len(metadata.get('payments', [])),
                'status': active_sub.status
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @db_retry
    def check_subscription_limits(self, profile_id: UUID) -> Dict[str, Any]:
        """Check subscription limits and usage"""
        session = self.db.get_session()
        try:
            profile = session.query(Profile).get(profile_id)
            if not profile:
                raise ValueError("Profile not found")
            
            filters = {
                'profile_id': profile_id,
                'content_type_id': self.get_subscription_type_id(),
                'status': 'active',
                'is_deleted': False
            }
            active_subs = super().filter(filters, limit=1)
            active_sub = active_subs[0] if active_subs else None
            
            if not active_sub:
                return {
                    'can_generate': False,
                    'limit_reached': True,
                    'remaining_generations': 0
                }
            
            metadata = active_sub.content_metadata or {}
            
            # Validate subscription dates
            start_date = datetime.fromisoformat(metadata.get('start_date', ''))
            end_date = metadata.get('end_date')
            if end_date:
                end_date = datetime.fromisoformat(end_date)
                if datetime.now() > end_date:
                    return {
                        'can_generate': False,
                        'limit_reached': True,
                        'remaining_generations': 0,
                        'reason': 'subscription_expired'
                    }
            
            plan_limit = self._get_plan_limit(metadata.get('plan_id'))
            used = profile.generations_used or 0
            
            return {
                'can_generate': used < plan_limit,
                'limit_reached': used >= plan_limit,
                'remaining_generations': max(0, plan_limit - used),
                'total_limit': plan_limit,
                'used': used
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _get_plan_limit(self, plan_id: str) -> int:
        """Get generation limit for a plan"""
        plan_limits = {
            'free': 10,
            'basic': 50,
            'pro': 100,
            'enterprise': 500
        }
        return plan_limits.get(plan_id, 0)

    @db_retry
    def get_subscription_type_id(self) -> UUID:
        """Get the content type ID for subscriptions"""
        session = self.db.get_session()
        try:
            from ..models import ContentType
            content_type = (
                session.query(ContentType)
                .filter(ContentType.name == 'subscription')
                .first()
            )
            if not content_type:
                raise ValueError("Subscription content type not found")
            return content_type.content_type_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()