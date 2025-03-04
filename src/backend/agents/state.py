from dataclasses import dataclass, field
from typing import List, Optional, Dict
from typing_extensions import Annotated
from operator import add

@dataclass
class Section:
    name: str
    description: str
    content: Optional[str] = field(default=None)
    main_body: bool = field(default=True)

@dataclass
class Sections:
    sections: List[Section]

@dataclass
class BlogState:
    sections: List[Section] = field(default_factory=list)
    completed_sections: Annotated[List[Section], add] = field(default_factory=list)
    blog_main_body_sections: Optional[str] = field(default=None)
    final_blog: Optional[str] = field(default=None)
    reviewed_blog: Optional[str] = field(default=None)
    twitter_post: Optional[str] = field(default=None)
    linkedin_post: Optional[str] = field(default=None)
    tags: Optional[List[str]] = field(default=None)
    feedback: Optional[str] = field(default=None)
    input_reddit: Optional[str] = field(default=None)
    input_topic: Optional[str] = field(default=None)
    input_url: Optional[str] = field(default=None)
    input_content: Optional[str] = field(default=None)
    urls: Optional[List[str]] = field(default_factory=list)
    post_types: List[str] = field(default_factory=list)
    thread_id: Optional[str] = field(default=None)
    media_markdown: Optional[str] = field(default=None)
    # media_meta: Optional[List[Dict]] = field(default_factory=list)
    linkedin_post_generated: Optional[bool] = field(default=False)
    twitter_post_generated: Optional[bool] = field(default=False)
    template: Optional[Dict] = field(default=None)

@dataclass
class BlogStateInput:
    input_reddit: Optional[str] = field(default=None)
    input_topic: Optional[str] = field(default=None)
    input_url: Optional[str] = field(default=None)
    input_content: Optional[str] = field(default=None)
    post_types: List[str] = field(default_factory=list)
    feedback: Optional[str] = field(default=None)
    thread_id: Optional[str] = field(default=None)
    media_markdown: Optional[str] = field(default=None)
    template: Optional[Dict] = field(default=None)
    # media_meta: Optional[List[Dict]] = field(default_factory=list)

@dataclass
class BlogStateOutput:
    final_blog: Optional[str] = field(default=None)
    reviewed_blog: Optional[str] = field(default=None)
    blog_title: Optional[str] = field(default=None)
    twitter_post: Optional[str] = field(default=None)
    linkedin_post: Optional[str] = field(default=None)
    tags: Optional[List[str]] = field(default_factory=list)
    feedback_applied: Optional[bool] = field(default=False)
    linkedin_post_generated: Optional[bool] = field(default=False)
    twitter_post_generated: Optional[bool] = field(default=False)

@dataclass
class SectionState:
    section: Section
    input_url: Optional[str] = field(default=None)
    input_content: Optional[str] = field(default=None)
    urls: Optional[List[str]] = field(default_factory=list)
    completed_sections: List[Section] = field(default_factory=list)
    blog_main_body_sections: Optional[str] = field(default=None)
    # media_meta: Optional[List[Dict]] = field(default_factory=list)
    media_markdown: Optional[str] = field(default=None)
    template: Optional[Dict] = field(default=None)

@dataclass
class StreamUpdate:
    node: str
    progress: int
    status: str = "processing"
    message: Optional[str] = field(default=None)