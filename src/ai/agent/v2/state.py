import operator
from dataclasses import dataclass, field
from typing import Dict
from pydantic import BaseModel, Field
from typing_extensions import Annotated, List

class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    content: str = Field(
        description="The content of the section."
    )   
    main_body: bool = Field(
        description="Whether this is a main body section."
    )   

class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the report.",
    )


# class AgentState(TypedDict):
#     """Extended state to include thread messages and human intervention flags"""

#     tweet: Dict
#     # tweet_type: list[str] | None
#     tags: list
#     blog_style: str
#     blog_title:str
#     blog_content: str
#     status: str
#     publication_schedule: Dict[str, Any]
#     messages: list[BaseMessage]  # Thread messages
#     # approval_to_generate: bool
#     approval_to_publish: bool
    # agent_id: str

@dataclass(kw_only=True)
class BlogState:
    tweet: Dict   
    # tags: list
    # style: str
    # agent_id:str
    sections: list[Section] = field(default_factory=list) 
    completed_sections: Annotated[list, operator.add] # Send() API key
    blog_main_body_sections: str = field(default=None) # Main body sections from research
    final_blog: str = field(default=None) # Final report
    twitter_post: str = field(default=None) # Twitter post
    linkedin_post: str = field(default=None) # LinkedIn post
    
@dataclass(kw_only=True)
class BlogStateInput:
    tweet: Dict # Blog notes
    # urls: List[str] = field(default_factory=list) # List of urls     

@dataclass(kw_only=True)
class BlogStateOutput:
    final_blog: str = field(default=None) # Final report
    blog_title: str = field(default=None)
    twitter_post: str = field(default=None)
    linkedin_post: str = field(default=None)

@dataclass(kw_only=True)
class SectionState:
    section: Section # Report section   
    tweet: Dict
    urls: List[str] = field(default_factory=list) # List of urls 
    blog_main_body_sections: str = field(default=None) # Main body sections from research
    completed_sections: list[Section] = field(default_factory=list) # Final key we duplicate in outer state for Send() API
    
@dataclass(kw_only=True)
class SectionOutputState:
    completed_sections: list[Section] = field(default_factory=list) # Final key we duplicate in outer state for Send() API