from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, cast, Date
from sqlalchemy.dialects.postgresql import JSONB
from ..models import Content, Profile
from ..sqlalchemy_repository import SQLAlchemyRepository

class AnalyticsRepository(SQLAlchemyRepository[Content]):
    def __init__(self):
        super().__init__(Content)

    def record_content_view(self, content_id: UUID, viewer_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Record a content view"""
        with self.db.transaction() as session:
            content = self.find_by_id(session, "content_id", content_id)
            if not content:
                raise ValueError("Content not found")
            
            view_data = {
                'event_type': 'view',
                'viewer_id': str(viewer_id) if viewer_id else None,
                'timestamp': datetime.now().isoformat()
            }
            
            if not content.content_metadata:
                content.content_metadata = {}
            
            if 'analytics' not in content.content_metadata:
                content.content_metadata['analytics'] = []
            
            content.content_metadata['analytics'].append(view_data)
            content.updated_at = datetime.now()
            session.flush()
            
            return view_data

    def record_content_interaction(self, content_id: UUID, event_type: str, 
                                metadata: Dict[str, Any], viewer_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Record a content interaction (like, share, comment)"""
        with self.db.transaction() as session:
            content = self.find_by_id(session, "content_id", content_id)
            if not content:
                raise ValueError("Content not found")
            
            interaction_data = {
                'event_type': event_type,
                'viewer_id': str(viewer_id) if viewer_id else None,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            if not content.content_metadata:
                content.content_metadata = {}
            
            if 'analytics' not in content.content_metadata:
                content.content_metadata['analytics'] = []
            
            content.content_metadata['analytics'].append(interaction_data)
            content.updated_at = datetime.now()
            session.flush()
            
            return interaction_data

    def get_content_analytics(self, content_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific content item"""
        with self.db.session() as session:
            content = self.find_by_id(session, "content_id", content_id)
            if not content or not content.content_metadata or 'analytics' not in content.content_metadata:
                return {
                    'daily_data': [],
                    'total_events': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'total_shares': 0
                }
            
            since = datetime.now() - timedelta(days=days)
            analytics = content.content_metadata['analytics']
            
            # Filter events within time window
            recent_events = [
                event for event in analytics 
                if datetime.fromisoformat(event['timestamp']) >= since
            ]
            
            # Group by date and event type
            daily_data = {}
            for event in recent_events:
                date = datetime.fromisoformat(event['timestamp']).date().isoformat()
                event_type = event['event_type']
                
                if date not in daily_data:
                    daily_data[date] = {}
                
                if event_type not in daily_data[date]:
                    daily_data[date][event_type] = {
                        'count': 0,
                        'unique_viewers': set()
                    }
                
                daily_data[date][event_type]['count'] += 1
                if event['viewer_id']:
                    daily_data[date][event_type]['unique_viewers'].add(event['viewer_id'])
            
            # Format response
            formatted_daily_data = []
            for date, events in daily_data.items():
                for event_type, data in events.items():
                    formatted_daily_data.append({
                        'date': date,
                        'event_type': event_type,
                        'count': data['count'],
                        'unique_viewers': len(data['unique_viewers'])
                    })
            
            # Calculate totals
            total_events = len(recent_events)
            total_views = sum(1 for e in recent_events if e['event_type'] == 'view')
            total_likes = sum(1 for e in recent_events if e['event_type'] == 'like')
            total_shares = sum(1 for e in recent_events if e['event_type'] == 'share')
            
            return {
                'daily_data': formatted_daily_data,
                'total_events': total_events,
                'total_views': total_views,
                'total_likes': total_likes,
                'total_shares': total_shares
            }

    def get_profile_analytics(self, profile_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get analytics across all content for a profile"""
        with self.db.session() as session:
            since = datetime.now() - timedelta(days=days)
            
            # Get all content for profile
            contents = (
                session.query(Content)
                .filter(
                    Content.profile_id == profile_id,
                    Content.is_deleted.is_(False)
                )
                .all()
            )
            
            # Aggregate analytics
            daily_data = {}
            total_events = 0
            total_views = 0
            total_likes = 0
            total_shares = 0
            
            for content in contents:
                if not content.content_metadata or 'analytics' not in content.content_metadata:
                    continue
                
                analytics = content.content_metadata['analytics']
                recent_events = [
                    event for event in analytics 
                    if datetime.fromisoformat(event['timestamp']) >= since
                ]
                
                for event in recent_events:
                    date = datetime.fromisoformat(event['timestamp']).date().isoformat()
                    event_type = event['event_type']
                    
                    if date not in daily_data:
                        daily_data[date] = {}
                    
                    if event_type not in daily_data[date]:
                        daily_data[date][event_type] = {
                            'count': 0,
                            'unique_viewers': set(),
                            'content_count': set()
                        }
                    
                    daily_data[date][event_type]['count'] += 1
                    if event['viewer_id']:
                        daily_data[date][event_type]['unique_viewers'].add(event['viewer_id'])
                    daily_data[date][event_type]['content_count'].add(str(content.content_id))
                    
                    # Update totals
                    total_events += 1
                    if event_type == 'view':
                        total_views += 1
                    elif event_type == 'like':
                        total_likes += 1
                    elif event_type == 'share':
                        total_shares += 1
            
            # Format response
            formatted_daily_data = []
            for date, events in daily_data.items():
                for event_type, data in events.items():
                    formatted_daily_data.append({
                        'date': date,
                        'event_type': event_type,
                        'count': data['count'],
                        'unique_viewers': len(data['unique_viewers']),
                        'content_count': len(data['content_count'])
                    })
            
            # Calculate average daily views
            avg_daily_views = (
                total_views / days if total_views > 0 else 0
            )
            
            return {
                'daily_data': formatted_daily_data,
                'total_events': total_events,
                'total_views': total_views,
                'total_likes': total_likes,
                'total_shares': total_shares,
                'avg_daily_views': avg_daily_views
            }

    def get_trending_content(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending content based on recent engagement"""
        with self.db.session() as session:
            since = datetime.now() - timedelta(days=days)
            
            # Query content with analytics content_metadata
            contents = (
                session.query(Content)
                .filter(
                    Content.is_deleted.is_(False),
                    Content.content_metadata.has_key('analytics')  # type: ignore
                )
                .all()
            )
            
            # Calculate engagement scores
            content_scores = []
            for content in contents:
                analytics = content.content_metadata.get('analytics', [])
                recent_events = [
                    event for event in analytics 
                    if datetime.fromisoformat(event['timestamp']) >= since
                ]
                
                if not recent_events:
                    continue
                
                # Calculate engagement score
                views = sum(1 for e in recent_events if e['event_type'] == 'view')
                likes = sum(1 for e in recent_events if e['event_type'] == 'like')
                shares = sum(1 for e in recent_events if e['event_type'] == 'share')
                comments = sum(1 for e in recent_events if e['event_type'] == 'comment')
                
                score = (views * 1 + likes * 2 + shares * 3 + comments * 2)
                
                content_scores.append({
                    'content': content,
                    'score': score,
                    'views': views,
                    'likes': likes,
                    'shares': shares,
                    'comments': comments
                })
            
            # Sort by score and limit results
            content_scores.sort(key=lambda x: x['score'], reverse=True)
            return content_scores[:limit]

    def get_user_activity_stats(self, profile_id: UUID) -> Dict[str, Any]:
        """Get user activity statistics"""
        with self.db.session() as session:
            # Get all content created by user
            contents = (
                session.query(Content)
                .filter(
                    Content.profile_id == profile_id,
                    Content.is_deleted.is_(False)
                )
                .all()
            )
            
            total_content = len(contents)
            total_views = 0
            total_likes = 0
            total_shares = 0
            total_comments = 0
            engagement_rate = 0
            
            for content in contents:
                if not content.content_metadata or 'analytics' not in content.content_metadata:
                    continue
                
                analytics = content.content_metadata['analytics']
                
                views = sum(1 for e in analytics if e['event_type'] == 'view')
                likes = sum(1 for e in analytics if e['event_type'] == 'like')
                shares = sum(1 for e in analytics if e['event_type'] == 'share')
                comments = sum(1 for e in analytics if e['event_type'] == 'comment')
                
                total_views += views
                total_likes += likes
                total_shares += shares
                total_comments += comments
            
            if total_views > 0:
                engagement_rate = ((total_likes + total_shares + total_comments) / total_views) * 100
            
            return {
                'total_content': total_content,
                'total_views': total_views,
                'total_likes': total_likes,
                'total_shares': total_shares,
                'total_comments': total_comments,
                'engagement_rate': round(engagement_rate, 2),
                'avg_views_per_content': round(total_views / total_content if total_content > 0 else 0, 2)
            }