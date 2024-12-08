from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Tweet Metadata
class TweetUrl(BaseModel):
    tweet_id: str
    index: int
    original_url: HttpUrl
    downloaded_path: Optional[str]
    type: Optional[str]
    domain: Optional[str]
    content_type: Optional[str]
    file_category: Optional[str]
    downloaded_at: Optional[datetime]

class TweetMedia(BaseModel):
    tweet_id: str
    type: str
    original_url: HttpUrl
    final_url: Optional[HttpUrl]
    downloaded_path: Optional[str]
    content_type: Optional[str]
    thumbnail: Optional[HttpUrl]
    downloaded_at: Optional[datetime]

class Tweet(BaseModel):
    tweet_id: str
    created_at: datetime
    full_text: str
    language: Optional[str] = "unknown"
    favorite_count: int
    retweet_count: int
    bookmark_count: int
    quote_count: int
    reply_count: int
    views_count: int
    screen_name: str
    user_name: str
    profile_image_url: HttpUrl
    urls: Optional[List[TweetUrl]] = []
    media: Optional[List[TweetMedia]] = []
    is_retweet: bool
    is_quote: bool
    possibly_sensitive: bool

# Agent model

class AgentStatus(str, Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    failed = "failed"

class AgentBase(BaseModel):
    name: str
    status: AgentStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: Optional[List[str]] = []

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    status: AgentStatus
    completed_at: Optional[datetime] = None

class AgentResponse(AgentBase):
    id: int