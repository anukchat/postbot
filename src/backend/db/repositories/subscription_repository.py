from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import desc
from ..models import Content, Profile
from ..sqlalchemy_repository import SQLAlchemyRepository

class SubscriptionRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)
    
    def get_active_subscription(self, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """Get active subscription for a profile"""
        with self.db.session() as session:
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

    def create_subscription(self, profile_id: UUID, plan_id: UUID, start_date: datetime, 
                        end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Create a new subscription"""
        with self.db.transaction() as session:
            subscription_data = {
                'profile_id': profile_id,
                'content_type_id': self.get_subscription_type_id(),
                'title': f'Subscription Plan {plan_id}',
                'status': 'active',
                'content_metadata': {
                    'plan_id': str(plan_id),
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat() if end_date else None
                },
                'created_at': datetime.now()
            }
            subscription = self.create(session, subscription_data)
            return subscription.to_dict()

    def cancel_subscription(self, subscription_id: UUID) -> bool:
        """Cancel a subscription"""
        with self.db.transaction() as session:
            subscription = self.find_by_id(session, "content_id", subscription_id)
            if subscription:
                subscription.status = 'cancelled'
                subscription.updated_at = datetime.now()
                session.flush()
                return True
            return False

    def record_payment(self, subscription_id: UUID, amount: float, 
                    payment_method: str) -> Dict[str, Any]:
        """Record a payment for a subscription"""
        with self.db.transaction() as session:
            subscription = self.find_by_id(session, "content_id", subscription_id)
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

    def get_subscription_stats(self, profile_id: UUID) -> Dict[str, Any]:
        """Get subscription usage statistics"""
        with self.db.session() as session:
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

    def check_subscription_limits(self, profile_id: UUID) -> Dict[str, Any]:
        """Check subscription limits and usage"""
        with self.db.session() as session:
            profile = (
                session.query(Profile)
                .filter(Profile.profile_id == profile_id)
                .first()
            )
            
            if not profile:
                raise ValueError("Profile not found")
            
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
                    'can_generate': False,
                    'limit_reached': True,
                    'remaining_generations': 0
                }
            
            metadata = active_sub.content_metadata or {}
            plan_limit = self._get_plan_limit(metadata.get('plan_id'))
            used = profile.generations_used or 0
            
            return {
                'can_generate': used < plan_limit,
                'limit_reached': used >= plan_limit,
                'remaining_generations': max(0, plan_limit - used),
                'total_limit': plan_limit,
                'used': used
            }

    def _get_plan_limit(self, plan_id: str) -> int:
        """Get generation limit for a plan"""
        plan_limits = {
            'free': 10,
            'basic': 50,
            'pro': 100,
            'enterprise': 500
        }
        return plan_limits.get(plan_id, 0)

    def get_subscription_type_id(self) -> UUID:
        """Get the content type ID for subscriptions"""
        with self.db.session() as session:
            from ..models import ContentType
            content_type = (
                session.query(ContentType)
                .filter(ContentType.name == 'subscription')
                .first()
            )
            if not content_type:
                raise ValueError("Subscription content type not found")
            return content_type.content_type_id