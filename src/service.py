from fastapi import FastAPI, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from datetime import datetime
from db.datamodel import AgentCreate, AgentResponse, BlogStyleUpdateRequest
from db.sql import AgentStatus,Agent, get_db, Blogs,BlogStatus,BlogStyles, BlogStyleTypes, Tweets  # Import Blog and BlogStyle models
from db.datamodel import BlogResponse,BlogStyleResponse,BlogStyleCreateRequest,BlogCreateRequest,BlogUpdateRequest,AgentUpdate, BlogWithMetadataResponse,BlogAgentResponse
from ai.agent.workflow import BlogWorkflow
from ai.agent.v2.graph import AgentWorkflow
from typing import Dict, Any
import uvicorn
import uuid
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
import time
import requests

app = FastAPI()

from pydantic import BaseModel

# class BlogMetadata(BaseModel):
#     # Add any specific metadata fields here
#     pass

class BlogModel(BaseModel):
    categories: List[str]
    tags: List[str]
    content: str

class ResponseModel(BaseModel):
    agent_id: str
    blog: Optional[BlogModel] = None
    status: str

class RequestModel(BaseModel):
    tweet_id: str

class SchedulePostRequest(BaseModel):
    platform: str
    content: str
    scheduled_at: datetime

class SchedulePostResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class GenericBlogGenerationRequestModel(BaseModel):
    tweet_id: Optional[str] = None
    url: Optional[str] = None
    topic: Optional[str] = None
    thread_id: Optional[str] = None
    feedback: Optional[str] = None
    post_types: Optional[List[str]] = None

    # document: Optional[]

BUFFER_API_URL = "https://api.bufferapp.com/1/updates/create.json"
BUFFER_ACCESS_TOKEN = "your_buffer_access_token"  # Replace with your Buffer access token


def get_workflow() -> BlogWorkflow:
    """Dependency to get a BlogWorkflow instance."""
    return AgentWorkflow()  # Pass the database session to BlogWorkflow

@app.post("/agents", response_model=AgentResponse,tags=["Agents"])
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent and return the agent ID."""
    status = AgentStatus.PENDING
    db_agent = Agent.create(name=agent.name, status=status, started_at=datetime.now())
    db.add(db_agent)
    db.commit()
    return AgentResponse.model_validate(db_agent)

@app.put("/agents/{agent_id}", response_model=AgentResponse,tags=["Agents"])
def update_agent(agent_id: str,agent: AgentUpdate, db: Session = Depends(get_db)):
    """Create a new agent and return the agent ID."""
    db_agent = Agent.update(id=agent_id, status=agent.status, completed_at=datetime.now())
    db.add(db_agent)
    db.commit()
    return AgentResponse.model_validate(db_agent)

@app.post("/blogs", response_model=BlogResponse,tags=["Blogs"])
def create_blog(blog: BlogCreateRequest, db: Session = Depends(get_db)):
    """Create a new blog entry."""
    db_blog = Blogs.create(
        db, 
        tweet_id=blog.tweet_id, 
        title=blog.title,
        twitter_post=blog.twitter_post,
        linkedin_post=blog.linkedin_post,
        content=blog.content, 
        style_id=blog.style_id,  # Added style_id
        blog_category=blog.blog_category,  # Added blog_category
        tags=blog.tags  # Added tags
    )
    return BlogResponse.model_validate(db_blog)

@app.get("/blogs/details", response_model=List[BlogWithMetadataResponse], tags=["BlogDetails"])
def get_blog_details(
    search_text: Optional[str] = None,
    tags: Optional[str] = None,
    status: Optional[BlogStatus] = None,
    created_before: Optional[datetime] = None,
    created_after: Optional[datetime] = None,
    url_type: Optional[str] = None,
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieve blog details along with associated tweet, URLs, and media with optional filters and pagination."""
    blog_data = Blogs.get_blogs_with_references(db, search_text, tags, status, created_before, created_after, url_type, domain, skip=skip, limit=limit)
    
    if not blog_data:
        raise HTTPException(status_code=404, detail="No blogs found or do not match filters")
    
    return [BlogWithMetadataResponse.model_validate(blog) for blog in blog_data]

@app.get("/blogs",tags= ["Blogs"])
def get_blogs(db: Session = Depends(get_db)):
    """Retrieve all blog styles from the database."""
    blogs = Blogs.get_all(db)  
    return blogs

@app.get("/blogs/{blog_id}", response_model=BlogResponse, tags=["Blogs"])
def read_blog(blog_id: str, db: Session = Depends(get_db)):
    """Retrieve a blog entry by ID."""
    return BlogResponse.model_validate(Blogs.read(db, id=blog_id))

@app.put("/blogs/{blog_id}", response_model=BlogResponse, tags=["Blogs"])
def update_blog(blog_id: str, blog: BlogUpdateRequest, db: Session = Depends(get_db)):
    """Update a blog entry by ID."""
    db_blog = Blogs.read(db, id=blog_id)
    if not db_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    updated_blog = Blogs.update(
        db, 
        id=blog_id, 
        # title=blog.title,
        twitter_post=blog.twitter_post,
        linkedin_post=blog.linkedin_post,
        content=blog.content, 
        status=blog.status,
        style_id=blog.style_id,
        blog_category=blog.blog_category,
        tags=blog.tags
    )
    return BlogResponse.model_validate(updated_blog)

@app.delete("/blogs/{blog_id}", tags=["Blogs"])
def delete_blog(blog_id: str, db: Session = Depends(get_db)):
    """Delete a blog entry by ID."""
    success = Blogs.delete(db, id=blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"detail": "Blog deleted successfully"}

@app.get("/blog_styles", response_model=List[BlogStyleResponse], tags=["BlogStyles"])
def get_blog_styles(db: Session = Depends(get_db)):
    """Retrieve all blog styles from the database."""
    blog_styles = BlogStyles.get_all(db)  # Use the class method to get all blog styles
    return [BlogStyleResponse.model_validate(blog_style) for blog_style in blog_styles]

@app.post("/blog_style", response_model=BlogStyleResponse, tags=["BlogStyles"])
def create_blog_style(style: BlogStyleCreateRequest, db: Session = Depends(get_db)):
    """Create a new blog style entry."""
    db_style = BlogStyles.create(db, style=style.style, filename=style.filename, style_prompt=style.style_prompt)
    return BlogStyleResponse.model_validate(db_style)

@app.get("/blog_styles/{style_id}", response_model=BlogStyleResponse, tags=["BlogStyles"])
def read_blog_style(style_id: str, db: Session = Depends(get_db)):
    """Retrieve a blog style entry by ID."""
    return BlogStyleResponse.model_validate(BlogStyles.read(db, id=style_id))

@app.put("/blog_styles/{style_id}", response_model=BlogStyleResponse, tags=["BlogStyles"])
def update_blog_style(style_id: str, style: BlogStyleUpdateRequest, db: Session = Depends(get_db)):
    """Update a blog style entry by ID."""
    db_style = BlogStyles.read(db, id=style_id)
    if not db_style:
        raise HTTPException(status_code=404, detail="Blog style not found")
    
    updated_style = BlogStyles.update(db, id=style_id, style=style.style, filename=style.filename, style_prompt=style.style_prompt)
    return BlogStyleResponse.model_validate(updated_style)

@app.delete("/blog_styles/{style_id}", tags=["BlogStyles"])
def delete_blog_style(style_id: str, db: Session = Depends(get_db)):
    """Delete a blog style entry by ID."""
    success = BlogStyles.delete(db, id=style_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog style not found")
    return {"detail": "Blog style deleted successfully"}

@app.post("/agents/run_workflow", response_model=BlogResponse, tags=["Agents"])
async def initiate_workflow(
    agent_id: str,
    payload: RequestModel,
    workflow: BlogWorkflow = Depends(get_workflow),
    db: Session = Depends(get_db)
):
    """Initiate the workflow with the provided tweet data."""
    try:
        result = workflow.run_workflow(payload.model_dump(), agent_id)
        
        # Create a new agent record in the database
        db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if db_agent and result.get("status") in ["BlogGenerated"]:
            db_agent.status = AgentStatus.COMPLETED
            db_agent.started_at = datetime.now()
            db.commit()
        else:
            db_agent.status = AgentStatus.IN_PROGRESS
            db.commit()

        # Assuming result contains the blog data
        # blog = BlogModel(
        #     categories=result.get('tweet_type', []),
        #     tags=result.get('tags', []),
        #     content=result.get('blog_content', '')           
        # )
        
        # Store the blog in the database with all relevant fields
        return BlogResponse.model_validate(Blogs.create(
            db,
            tweet_id=payload.tweet_id,
            title=result.get('blog_title', ''),
            content=result.get('blog_content', ''),
            status="Draft",  # or any other default status
            style_id=BlogStyles.read(db, style=payload.blog_style)[0].id if BlogStyles.read(db, style=payload.blog_style) else None,
            blog_category=result.get('tweet_type', []),  # Assuming blog_category is part of the result
            tags=result.get('tags', [])  # Using the tags from the blog object
        ))

        # return ResponseModel(
        #     agent_id=agent_id,
        #     blog=blog,
        #     status=result.get('status', '')
        # )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/blogs/generate", response_model=BlogAgentResponse, tags=["Agents"])
async def generate_blog(
    payload: RequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    db: Session = Depends(get_db)
):
    """Initiate the workflow with the provided tweet data."""
    try:
        result = workflow.run_workflow(payload.model_dump())

        # Store the blog in the database with all relevant fields
        return BlogAgentResponse.model_validate(Blogs.create_blog(
            db,
            tweet_id=payload.tweet_id,
            title=result.blog_title,
            content=result.final_blog,
            tags=result.tags,
            twitter_post=result.twitter_post,
            linkedin_post=result.linkedin_post,
            status=BlogStatus.DRAFT,  # or any other default status
            style_id=BlogStyles.filter_styles(db, style=BlogStyleTypes.Academic)[0].id,
        ))

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/blogs/generic/generate", response_model=BlogAgentResponse, tags=["Agents"])
async def generate_generic_blog(
    payload: GenericBlogGenerationRequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    db: Session = Depends(get_db)
):
    """Initiate the workflow with the provided tweet data."""
    try:
        result = workflow.run_generic_workflow(payload.model_dump())
        
        # Store the blog in the database with all relevant fields
        return BlogAgentResponse.model_validate(Blogs.create_blog(
            db,
            tweet_id=payload.url,
            title=result.blog_title,
            content=result.final_blog,
            tags=result.tags,
            twitter_post=result.twitter_post,
            linkedin_post=result.linkedin_post,
            status=BlogStatus.DRAFT,  # or any other default status
            style_id=BlogStyles.filter_styles(db, style=BlogStyleTypes.Academic)[0].id,
        ))

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/agents/{agent_id}/status",tags=["Agents"])
def get_workflow_status(
    agent_id: str,db: Session = Depends(get_db)
):
    """Get current status of a workflow."""
    if not db.query(Agent).filter(Agent.id == agent_id).first():
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return db.query(Agent).filter(Agent.id == agent_id).first()

@app.get("/tweets", tags=["Tweets"])
def get_tweets(
    search_text: Any | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieve all tweets from the database with optional search and pagination."""
    tweets = Tweets.get_all(db, search_text=search_text, skip=skip, limit=limit)  # Use the class method to get all tweets with search and pagination
    return tweets

@app.post("/generate_blogs_for_tweets", tags=["Agents"])
async def generate_blogs_for_tweets(db: Session = Depends(get_db)):
    """Generate blog posts for all tweets based on their URLs."""
    tweets = Tweets.get_all(db)  # Retrieve all tweets
    results = []
    blog_entries = []  # List to hold blog entries for bulk creation
    workflow = get_workflow()
    for tweet in tweets:
        # Check if a blog has already been generated for this tweet
        existing_blog = Blogs.read(db, tweet_id=tweet.tweet_id)  # Assuming a method to check existing blogs
        if existing_blog:
            continue  # Skip to the next tweet if a blog already exists
        print(f"Generating blog for tweet id {tweet.tweet_id}")
        # Access the associated URLs from the tweet
        urls = tweet.urls  # Get the URLs directly from the relationship

        # Only proceed if there are URLs available
        if urls:
            # Determine the blog style based on the type of URLs
            # blog_style = "Academic"  # Default style
            # for url in urls:
            #     if url.type == "github":
            #         blog_style = "Developer"
            #         break  # No need to check further if we found a GitHub URL
            #     elif url.type == "arxiv":
            #         blog_style = "Research"
            #         break  # No need to check further if we found an Arxiv URL

            # # Create a new agent for the blog generation
            # agent_response = create_agent(AgentCreate(name=f"Agent for {tweet.tweet_id}"), db)
            # agent_id = agent_response.id

            # Prepare the payload for the workflow
            payload = RequestModel(tweet_id=tweet.tweet_id)

            # Call the run_workflow endpoint
            blog_response = await generate_blog( payload=payload, db=db,workflow=workflow)
            results.append(blog_response)
            time.sleep(30)

    return results

@app.post("/schedule_post", response_model=SchedulePostResponse, tags=["Scheduling"])
def schedule_post(request: SchedulePostRequest):
    """Schedule a post on a social media platform."""
    try:
        response = requests.post(
            BUFFER_API_URL,
            headers={
                "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"
            },
            data={
                "text": request.content,
                "profile_ids": [request.platform],
                "scheduled_at": request.scheduled_at.isoformat()
            }
        )
        response_data = response.json()
        if response.status_code == 200:
            return SchedulePostResponse(success=True, message="Post scheduled successfully")
        else:
            return SchedulePostResponse(success=False, message=response_data.get("message", "Failed to schedule post"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=False)
