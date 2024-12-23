from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from db.sql import AgentStatus,BlogStatus,BlogStyleTypes  # Import from enums.py


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


# Selected Complete Blog model

# Agent model

# class AgentStatus(str, Enum):
#     pending = "pending"
#     active = "active"
#     completed = "completed"
#     failed = "failed"

class AgentBase(BaseModel):
    name: str
    status: AgentStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: Optional[List[str]] = []

class AgentCreate(BaseModel):
    name: str

class AgentUpdate(BaseModel):
    status: AgentStatus

class AgentResponse(BaseModel):
    id: str  # Change from int to str to match UUID
    name: str
    status: AgentStatus
    started_at: datetime
    completed_at: datetime
    steps: Optional[List[str]] = []


#Create request model for Blog
class BlogCreateRequest(BaseModel):
    tweet_id: str
    title: str
    content: str
    blog_category: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    style_id: Optional[str] = None

class BlogUpdateRequest(BaseModel):
    content: Optional[str]=None
    status: Optional[BlogStatus]=None
    blog_category: Optional[List[str]]=None
    tags: Optional[List[str]]=None
    style_id: Optional[str]=None

class BlogResponse(BaseModel):  # New Pydantic model for Blogs
    id: str
    tweet_id: str
    title: str
    content: str
    status: BlogStatus
    blog_category: List[str]
    tags: List[str]
    style_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable from_attributes


class BlogStyleResponse(BaseModel):  # New Pydantic model for BlogStyles
    id: str
    style: BlogStyleTypes
    filename: str
    style_prompt: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable from_attributes

class BlogStyleCreateRequest(BaseModel): # New Pydantic model for BlogStyles
    style: BlogStyleTypes
    filename: Optional[str] = None
    style_prompt: str

class BlogStyleUpdateRequest(BaseModel): # New Pydantic model for BlogStyles
    id: str
    style: Optional[BlogStyleTypes]=None
    filename: Optional[str]=None
    style_prompt: Optional[str]=None



class URLModel(BaseModel):
    id: str
    original_url: str
    downloaded_path: Optional[str]
    type: Optional[str]
    domain: Optional[str]

class MediaModel(BaseModel):
    id: str
    original_url: str
    final_url: Optional[str]
    type: str
    thumbnail: Optional[str]

class TweetModel(BaseModel):
    tweet_id: str
    full_text: str
    created_at: datetime
    language: str
    screen_name: str
    user_name: str
    profile_image_url: str

class BlogWithMetadataResponse(BaseModel): # New Pydantic model for Blog
    blog: BlogResponse
    tweet: Optional[TweetModel]
    urls: List[URLModel]
    media: List[MediaModel]