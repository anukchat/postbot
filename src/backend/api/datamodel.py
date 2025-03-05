from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional, List, Dict, Union
from uuid import UUID

#region Profile Pydantic Model
class ProfileBase(BaseModel):
    user_id: UUID
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "free"
    subscription_status: str = "none"
    subscription_end: Optional[datetime] = None
    preferences: Dict = Field(default={"theme": "light", "defaultView": "blog", "emailNotifications": True})

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_end: Optional[datetime] = None
    preferences: Optional[Dict] = None

class Profile(ProfileBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region ContentType Pydantic Model
class ContentTypeBase(BaseModel):
    name: str

class ContentTypeCreate(ContentTypeBase):
    pass

class ContentTypeUpdate(BaseModel):
    name: Optional[str] = None

class ContentType(ContentTypeBase):
    content_type_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
#endregion

#region Content Pydantic Model
class ContentBase(BaseModel):
    profile_id: UUID  # Changed from Optional[UUID] to required UUID
    content_type_id: UUID
    title: Optional[str] = None
    body: Optional[str] = None
    status: str = "draft"
    thread_id: Optional[UUID] = None
    is_public: bool = False  # New field for public/private visibility
    shared_with: List[UUID] = []  # New field for specific user sharing

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    thread_id: Optional[UUID] = None

class Content(ContentBase):
    content_id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
#endregion

#region SourceType Pydantic Model
class SourceTypeBase(BaseModel):
    name: str

class SourceTypeCreate(SourceTypeBase):
    pass

class SourceTypeUpdate(BaseModel):
    name: Optional[str] = None

class SourceType(SourceTypeBase):
    source_type_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Source Pydantic Model
class SourceBase(BaseModel):
    batch_id: Optional[UUID] = None
    source_type_id: UUID
    source_identifier: str

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    batch_id: Optional[UUID] = None
    source_type_id: Optional[UUID] = None
    source_identifier: Optional[str] = None

class Source(SourceBase):
    source_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#endregion

#region ContentSource Pydantic Model
class ContentSourceBase(BaseModel):
    content_id: UUID
    source_id: UUID

class ContentSourceCreate(ContentSourceBase):
    pass

class ContentSourceUpdate(BaseModel):
    content_id: Optional[UUID] = None
    source_id: Optional[UUID] = None

class ContentSource(ContentSourceBase):
    content_source_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region URLReference Pydantic Model
class URLReferenceBase(BaseModel):
    source_id: UUID
    url: str
    type: Optional[str] = None
    domain: Optional[str] = None
    content_type: Optional[str] = None
    file_category: Optional[str] = None
    description: Optional[str] = None

class URLReferenceCreate(URLReferenceBase):
    pass

class URLReferenceUpdate(BaseModel):
    source_id: Optional[UUID] = None
    url: Optional[str] = None
    type: Optional[str] = None
    domain: Optional[str] = None
    content_type: Optional[str] = None
    file_category: Optional[str] = None
    description: Optional[str] = None

class URLReference(URLReferenceBase):
    url_reference_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Media Pydantic Model
class MediaBase(BaseModel):
    source_id: UUID
    media_url: str
    media_type: str

class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    source_id: Optional[UUID] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class Media(MediaBase):
    media_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Tag Pydantic Model
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None

class Tag(TagBase):
    tag_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region ContentTag Pydantic Model
class ContentTagBase(BaseModel):
    content_id: UUID
    tag_id: UUID

class ContentTagCreate(ContentTagBase):
    pass

class ContentTagUpdate(BaseModel):
    content_id: Optional[UUID] = None
    tag_id: Optional[UUID] = None

class ContentTag(ContentTagBase):
    content_tag_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region SourceMetadata Pydantic Model
class SourceMetadataBase(BaseModel):
    source_id: UUID
    key: str
    value: Optional[str] = None

class SourceMetadataCreate(SourceMetadataBase):
    pass

class SourceMetadataUpdate(BaseModel):
    source_id: Optional[UUID] = None
    key: Optional[str] = None
    value: Optional[str] = None

class SourceMetadata(SourceMetadataBase):
    metadata_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region ContentAnalytics Pydantic Model
class ContentAnalyticsBase(BaseModel):
    content_id: UUID
    views: int = 0
    likes: int = 0
    shares: int = 0

class ContentAnalyticsCreate(ContentAnalyticsBase):
    pass

class ContentAnalyticsUpdate(BaseModel):
    content_id: Optional[UUID] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None

class ContentAnalytics(ContentAnalyticsBase):
    analytics_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#endregion

#region UserActivity Pydantic Model
class UserActivityBase(BaseModel):
    profile_id: UUID
    activity_type: str
    activity_details: Optional[Dict] = None

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityUpdate(BaseModel):
    profile_id: Optional[UUID] = None
    activity_type: Optional[str] = None
    activity_details: Optional[Dict] = None

class UserActivity(UserActivityBase):
    activity_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Plan Pydantic Model
class PlanBase(BaseModel):
    name: str
    price: float
    features: Optional[Dict] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    features: Optional[Dict] = None

class Plan(PlanBase):
    plan_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Subscription Pydantic Model
class SubscriptionBase(BaseModel):
    profile_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    profile_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

class Subscription(SubscriptionBase):
    subscription_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

#region Payment Pydantic Model
class PaymentBase(BaseModel):
    subscription_id: UUID
    amount: float
    payment_method: str
    status: str = "pending"

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    subscription_id: Optional[UUID] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None

class Payment(PaymentBase):
    payment_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

#endregion

# Response Models (moved from api.py)
class ContentListItem(BaseModel):
    id: str
    thread_id: str
    source_identifier: Optional[str] = None
    title: Optional[str] = None
    content: str
    tags: List[str]
    createdAt: str
    updatedAt: str
    status: str
    twitter_post: Optional[str]
    linkedin_post: Optional[str]
    urls: List[dict]
    media: List[dict]
    source_type: Optional[str]

class ContentListResponse(BaseModel):
    items: List[ContentListItem]
    total: int
    page: int
    size: int

class SourceListResponse(BaseModel):
    items: List[Dict]
    total: int
    page: int
    size: int

class RedditResponse(BaseModel):
    data: Dict[str, Any]
    status: str
    error: Optional[str] = None

# Token Generation Models
class TokenRequest(BaseModel):
    grant_type: str
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    provider: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    provider: Optional[str] = None

class CallbackResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None

# Model for a Templates
class TemplateParameterValue(BaseModel):
    value_id: UUID
    value: str
    display_order: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TemplateParameterValueCreate(BaseModel):
    value_id: UUID
    value: str

class TemplateParameter(BaseModel):
    parameter_id: UUID
    name: str  # Parameter name (e.g., "persona")
    display_name: str  # Friendly name for UI
    description: Optional[str] = ''
    is_required: bool = True
    created_at: datetime
    values: Optional[TemplateParameterValue]=None

    class Config:
        from_attributes = True

class TemplateParameterCreate(BaseModel):
    parameter_id: UUID
    name: str
    display_name: str
    is_required: bool = True
    values: Optional[TemplateParameterValueCreate] = None

# Model for a single template
class TemplateResponse(BaseModel):
    template_id: UUID
    name: str
    description: Optional[str] = ''
    template_type: str
    template_image_url: Optional[str] = ''
    parameters: Optional[List[TemplateParameter]]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True

# Model for creating a template
class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: Optional[str] = "default"
    template_image_url: Optional[str] = None
    parameters: Optional[List[TemplateParameterCreate]] = None

# Model for updating a template
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    template_image_url: Optional[str] = None
    parameters: Optional[List[TemplateParameterCreate]] = None  # Optional list of updated parameters

# Model for parameters
class ParameterValueModel(BaseModel):
    value_id: UUID
    value: str
    display_order: int
    created_at: datetime

class ParameterModel(BaseModel):
    parameter_id: UUID
    name: str
    display_name: str
    description: Optional[str]
    is_required: bool
    created_at: datetime
    values: List[ParameterValueModel]


class SaveContentRequest(BaseModel):
    # thread_id: UUID
    title: Optional[str] = None
    content: Optional[str] = None
    twitter_post: Optional[str] = None
    linkedin_post: Optional[str] = None
    status: str = "Draft"

class ScheduleContentRequest(BaseModel):
    thread_id: UUID
    status: str = "scheduled"
    schedule_date: datetime
    platform: str

class GeneratePostRequestModel(BaseModel):
    thread_id: str = None
    post_types: List[str]
    tweet_id: Optional[str] = None
    url: Optional[str] = None
    topic: Optional[str] = None
    feedback: Optional[str] = None  # Add this field
    reddit_query: Optional[str] = None
    subreddit: Optional[str] = None
    template_id: Optional[str] = None

class RedditRequest(BaseModel):
    subreddits: Optional[List[str]] = None
    category: Optional[str] = None
    timeframe: Optional[str] = 'day'
    limit: Optional[int] = 10

class RedditSuggestionsResponse(BaseModel):
    content_ideas: List[str]

class UserProfileResponse(BaseModel):
    id: str  # Original user_id from auth
    profile_id: str  # Profile ID for database relations
    role: str = "free"


class BlogResponse(BaseModel):
    final_blog: Optional[str]
    reviewed_blog: Optional[str]
    blog_title: Optional[str]
    twitter_post: Optional[str]
    linkedin_post: Optional[str]
    tags: Optional[List[str]]
    feedback_applied: Optional[bool]
    linkedin_post_generated: Optional[bool]
    twitter_post_generated: Optional[bool]