import json
import os
import uuid
from fastapi import FastAPI, HTTPException, Depends, Query, Security, Body, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.backend.db.connection import DatabaseConnectionManager, session_context
from src.backend.db.datamodel import *
from typing import List, Optional
import uvicorn
from src.backend.agents.blogs import AgentWorkflow
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
from datetime import datetime
from uuid import UUID
from src.backend.utils.logger import setup_logger
from src.backend.extraction.extractors.reddit import RedditExtractor
from src.backend.db.repositories import (
    TemplateRepository,
    ParameterRepository,
    ContentRepository,
    ProfileRepository,
    SourceRepository,
    ContentTypeRepository,
    AuthRepository
)
from fastapi.responses import JSONResponse
from src.backend.formatters import (
    format_content_list_item,
    format_content_list_response,
    format_parameter_response,
    format_source_list_response,
    format_template_response,
)
from cachetools import TTLCache

# Auth cache to store token-to-user mappings with a TTL (Time To Live)
# Cache size of 100 users, and tokens expire after 5 minutes
auth_cache = TTLCache(maxsize=100, ttl=6000)  # 6000 seconds = 100 minutes

# Get settings from environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin",
        "Referer",
        "User-Agent"
    ],
    max_age=600  # Move max_age here as middleware parameter
)

db_manager = DatabaseConnectionManager()
security = HTTPBearer()

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database session per request"""
    session = None
    try:
        session = db_manager.get_session()
        # Set up a place to cache auth results
        request.state.auth_cache = {}
        response = await call_next(request)
        if session:
            try:
                session.commit()
            except:
                session.rollback()
                raise
        return response
    except Exception as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()
            try:
                session_context.set(None)
            except:
                pass

# Setup logger
logger = setup_logger(__name__)

# Initialize repositories
template_repository = TemplateRepository()
parameter_repository = ParameterRepository()
content_repository = ContentRepository()
profile_repository = ProfileRepository()
source_repository = SourceRepository()
content_type_repository = ContentTypeRepository()
auth_repository = AuthRepository()

# Agent Workflow Endpoint
def get_workflow() -> AgentWorkflow:
    """Dependency to get a AgentWorkflow instance."""
    return AgentWorkflow()

# Authentication Dependency with caching
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Security(security),
    request: Request=None
):
    try:
        # Get access token from authorization header
        access_token = credentials.credentials
        # Get refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token is required")
        
        # Create a cache key based on both tokens
        cache_key = f"{access_token}:{refresh_token}"
        
        # Try to get user from cache first
        cached_user_data = auth_cache.get(cache_key)
        if cached_user_data:
            return cached_user_data
        
        # If not in cache, perform the API call
        user = await auth_repository.get_user(access_token, refresh_token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token or expired")

        # Get associated profile using user_id
        profile = profile_repository.get_profile_by_user_id(UUID(user.user.id))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        user_profile = UserProfileResponse(
            id=user.user.id,
            profile_id=str(profile.id),
            role=profile.role,
        )
        
        # Store in cache
        auth_cache[cache_key] = user_profile
        
        return user_profile
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/signup", tags=["auth"])
async def sign_up(email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_up(email, password)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", tags=["auth"])
async def sign_in(email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_in(email, password)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signout", tags=["auth"])
async def sign_out():
    try:
        result = await auth_repository.sign_out()
        
        # Clear the auth cache on signout
        auth_cache.clear()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Profile Endpoints
@app.post("/profiles/", response_model=Profile, tags=["profiles"])
async def create_profile(
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Create profile with both id and user_id
        return profile_repository.create({
            **profile_data,
            "id": uuid.uuid4(),  # Generate new profile ID
            "user_id": current_user.id  # Set user_id from auth
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
async def get_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
async def update_profile(
    profile_id: UUID,
    profile_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile_repository.update("id", profile_id, profile_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/profiles/{profile_id}", tags=["profiles"])
async def delete_profile(
    profile_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        profile = profile_repository.find_by_field("id", profile_id)
        if not profile or profile["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile_repository.soft_delete("id", profile_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profiles/", response_model=List[Profile], tags=["profiles"])
async def list_profiles(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_user_profile)
):
    try:
        return profile_repository.filter({"id": current_user.profile_id}, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ContentType Endpoints
@app.post("/content-types/", response_model=ContentType, tags=["content_types"])
def create_content_type(content_type: ContentTypeCreate, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.create(content_type.dict())
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create content type")
    return result

@app.get("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def read_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.find_by_field("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@app.put("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def update_content_type(content_type_id: UUID, content_type: ContentTypeUpdate, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.update(
        id_field="content_type_id",
        id_value=content_type_id,
        data=content_type.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@app.delete("/content-types/{content_type_id}", tags=["content_types"])
def delete_content_type(content_type_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.delete("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return {"message": "ContentType deleted"}

@app.get("/content-types/", response_model=List[ContentType], tags=["content_types"])
def filter_content_types(name: Optional[str] = None, skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user_profile)):
    query_filters = {}
    if name:
        query_filters["name"] = name
    result = content_type_repository.filter(query_filters, skip, limit)
    return result

# Update content endpoints to use profile_id
@app.post("/content/", response_model=Content, tags=["content"])
async def create_content(
    content_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        content_data["profile_id"] = current_user.profile_id
        return content_repository.create(content_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/content/generate", tags=["agents"])
async def generate_generic_blog(
    payload: GeneratePostRequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    current_user: dict = Depends(get_current_user_profile),
):
    """Initiate the workflow with the provided data."""
    try:
        thread_id = payload.thread_id or str(uuid.uuid4())
        # Get template and parameters if template_id is provided
        if payload.template_id:
            template_data=template_repository.get_template_with_parameters(UUID(payload.template_id), UUID(current_user.profile_id))
            payload_dict = payload.model_dump()
            payload_dict["template"] = template_data
            # payload = GeneratePostRequestModel(**payload_dict)
        # Check generation limit        
        limit_response = await check_generation_limit(current_user.profile_id)
        logger.info(f"Generation limit check: {limit_response}")
        
        if limit_response['generations_used'] >= limit_response['max_generations']:
            logger.warning(f"Generation limit reached for user {current_user['id']}")
            raise HTTPException(status_code=403, detail="Generation limit reached for this thread")

        # Proceed with generation
        logger.debug("Starting workflow execution")
        result = workflow.run_generic_workflow(payload_dict, thread_id, current_user)
        logger.debug("Workflow execution completed")

        # Increment generation count
        await increment_generation_count(current_user.profile_id)

        return result
    except HTTPException as e:
        logger.error(f"HTTP Exception in generate_generic_blog: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in generate_generic_blog: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

async def check_generation_limit(profile_id: UUID) -> Dict:
    """Check the generation limit for a specific profile."""
    profile_data = profile_repository.get_with_generation_limits(profile_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "tier": profile_data["role"],
        "max_generations": profile_data["generation_limit"],
        "generations_used": profile_data["generations_used"]
    }

async def increment_generation_count(profile_id: UUID):
    """Increment the generation count for a profile."""
    try:
        success = profile_repository.increment_generation_count(profile_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to increment generation count")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to increment generation count: {str(e)}")
    

@app.get("/content/filter", response_model=ContentListResponse)
async def filter_content(
    skip: int = 0,
    limit: int = 10,
    filters: str = Query(None, description="JSON string containing filters"),
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Parse the JSON string filters into a dictionary
        filter_dict = {}
        if filters:
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse filters JSON: {filters}")
                filter_dict = {}

        result = content_repository.filter_content(UUID(current_user.profile_id), filter_dict, skip, limit)
        return format_content_list_response(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as e:
        logger.error(f"Error in filter_content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/content/{content_id}", response_model=ContentListItem, tags=["content"])
async def get_content(
    content_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        content = content_repository.find_by_field("content_id", content_id)
        if not content or str(content.profile_id) != current_user.profile_id:
            raise HTTPException(status_code=404, detail="Content not found")
        return format_content_list_item(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/content/{content_id}", response_model=Content, tags=["content"]) 
def update_content(content_id: UUID, content: ContentUpdate, current_user: dict = Depends(get_current_user_profile)):
    """Update content"""
    result = content_repository.update(
        id_field="content_id",
        id_value=content_id,
        data=content.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Content not found")
    if result["profile_id"] != str(current_user.profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this content")
    return result

@app.delete("/content/thread/{thread_id}", tags=["content"])
async def delete_thread_content(
    thread_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Delete all content associated with thread
        content = content_repository.find_by_field("thread_id", thread_id)
        if not content or str(content["profile_id"]) != current_user.profile_id:
            raise HTTPException(status_code=404, detail="Content not found")
        return content_repository.soft_delete("thread_id", thread_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/content/thread/{thread_id}/save", response_model=ContentListItem, tags=["content"])
async def save_content(
    thread_id: UUID,
    content: SaveContentRequest,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        result = content_repository.update_by_thread(
            thread_id,
            UUID(current_user.profile_id),
            content.dict(exclude_unset=True)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        return ContentListItem(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/content/thread/{thread_id}/schedule", tags=["content"])
async def schedule_thread_content(
    thread_id: UUID, 
    payload: ScheduleContentRequest,
    current_user: Dict = Depends(get_current_user_profile)
):
    """Schedule content for publishing"""
    try:
        content_type_id = content_type_repository.get_content_type_id_by_name(f"{payload.platform}_post")
        if not content_type_id:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {payload.platform}")

        content_data = {
            "status": payload.status,
            "scheduled_at": payload.schedule_date
        }

        result = content_repository.update(
            id_field="thread_id",
            id_value=thread_id,
            data=content_data
        )

        if not result:
            raise HTTPException(status_code=404, detail="Content not found")

        return {"message": "Content scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update sources endpoints to use profile_id
@app.post("/sources/", response_model=Source, tags=["sources"])
def create_source(source: SourceCreate, current_user: dict = Depends(get_current_user_profile)):
    """Create a new source"""
    try:
        result = source_repository.create_source(source.dict(), current_user.profile_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create source")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sources/", response_model=SourceListResponse, tags=["sources"])
def filter_sources(
    type: Optional[str] = None, 
    source_identifier: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: dict = Depends(get_current_user_profile)
):
    result = source_repository.list_sources_with_related(
        profile_id=current_user.profile_id,
        type=type,
        source_identifier=source_identifier,
        skip=skip,
        limit=limit
    )
    return result

@app.get("/sources/{source_id}", response_model=Source, tags=["sources"])
def read_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.find_by_field("source_id", source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@app.put("/sources/{source_id}", response_model=Source, tags=["sources"])
def update_source(source_id: UUID, source: SourceUpdate, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.update(
        id_field="source_id",
        id_value=source_id,
        data=source.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@app.delete("/sources/{source_id}", tags=["sources"])
def delete_source(source_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    result = source_repository.soft_delete(source_id, current_user.profile_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted"}

@app.get("/content/thread/{thread_id}", response_model=ContentListItem, tags=["content"]) 
async def get_content_by_thread(
    thread_id: UUID,
    post_type: Optional[str] = Query(None, description="Filter by post type (blog, twitter, linkedin)"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get content by thread ID with optional post type filter"""
    try:
        # Get content type ID if post_type is provided
        content_type_id = None
        if post_type:
            type_id = content_type_repository.get_content_type_id_by_name(post_type)
            if not type_id:
                raise HTTPException(status_code=400, detail=f"Invalid post type: {post_type}")
            content_type_id = type_id

        result = content_repository.get_content_by_thread(thread_id, UUID(current_user.profile_id), content_type_id)

        if not result:
            return ContentListItem(
                id="",
                thread_id=str(thread_id),
                title="",
                content="",
                tags=[],
                createdAt=datetime.now().isoformat(),
                updatedAt=datetime.now().isoformat(),
                status="",
                twitter_post="",
                linkedin_post="",
                urls=[],
                media=[],
                source_type=None
            )

        return format_content_list_item(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reddit/trending", response_model=RedditResponse, tags=["reddit"])
async def get_trending_reddit_topics(
    limit: int = Query(10, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Fetch trending topics from specified subreddits or r/all"""
    try:
        reddit_extractor = RedditExtractor()
        subreddit_list = subreddits.split(',') if subreddits else None
        trending_data = reddit_extractor.get_trending_topics(
            limit=limit,
            subreddits=subreddit_list
        )
        return trending_data
    except Exception as e:
        return trending_data

@app.get("/reddit/discussions", response_model=RedditResponse, tags=["reddit"])
async def get_trending_discussions(
    category: str = Query('all', description="Category/subreddit to fetch from"),
    timeframe: str = Query('day', description="Time period (hour, day, week, month, year, all)"),
    limit: int = Query(10, description="Number of posts to fetch"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Fetch trending discussion posts based on category and timeframe"""
    try:
        reddit_extractor = RedditExtractor()
        discussions = reddit_extractor.get_trending_discussions(
            category=category,
            timeframe=timeframe,
            limit=limit
        )
        
        return RedditResponse(
            data=discussions,
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@app.get("/reddit/topic-suggestions", response_model=RedditSuggestionsResponse, tags=["reddit"])
async def get_topic_suggetsions(
    limit: int = Query(15, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get information about a specific subreddit"""
    try:
        reddit_extractor = RedditExtractor()
        subreddit_list = subreddits.split(',') if subreddits else None
        trending_data = reddit_extractor.get_trending_topics(
            limit=limit,
            subreddits=subreddit_list
        )
        
        topic_list=reddit_extractor.suggest_trending_titles(trending_data)

        return topic_list
    except Exception as e:
        return []

@app.get("/reddit/active-subreddits", response_model=RedditResponse, tags=["reddit"])
async def get_active_subreddits(
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(10, description="Number of subreddits to return"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get most active subreddits for a given category"""
    try:
        reddit_extractor = RedditExtractor()
        active_subs = reddit_extractor.get_active_subreddits(
            category=category,
            limit=limit
        )
        
        return RedditResponse(
            data={"subreddits": active_subs},
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@app.post("/reddit/extract", response_model=RedditResponse, tags=["reddit"])
async def extract_reddit_content(
    url: str = Body(..., description="Reddit post URL to extract"),
    skip_llm: bool = Body(False, description="Skip LLM processing"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Extract content from a Reddit post URL"""
    try:
        reddit_extractor = RedditExtractor()
        content = reddit_extractor.extract(
            source=url,
            skip_llm=skip_llm
        )
        
        return RedditResponse(
            data=content,
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@app.post("/reddit/batch-summary", response_model=RedditResponse, tags=["reddit"])
async def create_reddit_summary(
    posts: List[Dict] = Body(..., description="List of Reddit posts to summarize"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a summary from multiple Reddit posts"""
    try:
        reddit_extractor = RedditExtractor()
        summary = reddit_extractor.create_summary(posts)
        
        return RedditResponse(
            data={"summary": summary},
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

#Templates endpoints
@app.post("/templates/", response_model=TemplateResponse, tags=["templates"])
async def create_template(
    template: TemplateCreate,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template_data = template.dict()
        template_data["profile_id"] = current_user.profile_id
        parameters = template_data.pop("parameters", [])
        return template_repository.create_template_with_parameters(template_data, parameters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def get_template(
    template_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template = template_repository.get_template_with_parameters(template_id, UUID(current_user.profile_id))
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return format_template_response(template)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def update_template(
    template_id: UUID,
    template: TemplateUpdate,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        template_data = template.dict(exclude_unset=True)
        parameters = template_data.pop("parameters", None)
        updated = template_repository.update_template_with_parameters(
            template_id,
            UUID(current_user.profile_id),
            template_data,
            parameters
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/", response_model=List[TemplateResponse], tags=["templates"]) 
def list_templates(
    skip: int = 0, 
    limit: int = 10, 
    template_type: Optional[str] = None,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """List all templates for the authenticated user."""
    try:
        templates = template_repository.list_templates_for_profile(
            profile_id=UUID(current_user.profile_id),
            skip=skip,
            limit=limit,
            template_type=template_type,
            include_deleted=include_deleted
        )
        return templates
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/{template_id}/duplicate", response_model=TemplateResponse, tags=["templates"])
async def duplicate_template(
    template_id: UUID,
    new_name: str = Body(...),
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        duplicated = template_repository.duplicate_template(
            template_id,
            UUID(current_user.profile_id),
            new_name
        )
        if not duplicated:
            raise HTTPException(status_code=404, detail="Template not found")
        return duplicated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/filter", response_model=List[TemplateResponse], tags=["templates"])
def filter_templates(
    filters: TemplateFilter,
    skip: int = 0,
    limit: int = 10,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates based on parameters."""
    try:
        return template_repository.filter_templates(
            UUID(current_user.profile_id),
            filters.dict(exclude_unset=True),
            filters.template_type,
            include_deleted,
            skip,
            limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/templates/{template_id}", tags=["templates"])
def delete_template(template_id: UUID, current_user: dict = Depends(get_current_user_profile)):
    """Soft delete a template by ID."""
    try:
        result = template_repository.update_template_with_parameters(
            template_id=template_id,
            profile_id=current_user.profile_id,
            template_data={
                "updated_at": datetime.now().isoformat(),
                "is_deleted": True,
                "deleted_at": datetime.now().isoformat()
            }
        )
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/", response_model=List[TemplateResponse], tags=["templates"])
async def list_templates(
    skip: int = 0,
    limit: int = 10,
    template_type: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        templates = template_repository.list_templates_for_profile(
            UUID(current_user.profile_id),
            skip,
            limit,
            template_type
        )
        return [TemplateResponse(**template) for template in templates]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/filter", response_model=List[TemplateResponse], tags=["templates"])
def filter_templates(
    filter: TemplateFilter, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates based on parameters."""
    try:
        results = template_repository.list_templates_for_profile(
            profile_id=current_user.profile_id,
            skip=skip,
            limit=limit,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted or False
        )
        return [template_repository.get_template_with_parameters(UUID(t["template_id"]), UUID(current_user.profile_id)) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/advanced-filter", response_model=List[TemplateResponse], tags=["templates"])
def advanced_filter_templates(
    filter: AdvancedTemplateFilter,
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user_profile)
):
    """Filter templates by multiple parameters."""
    try:
        results = template_repository.filter_templates(
            profile_id=current_user.profile_id,
            parameters=filter.parameters,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted,
            skip=skip,
            limit=limit
        )
        return [template_repository.get_template_with_parameters(UUID(t["template_id"]), UUID(current_user.profile_id)) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/", response_model=List[ParameterResponse], tags=["parameters"])
def get_all_parameters(
    skip: int = 0, 
    limit: int = 100,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get all available parameters."""
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        return [param for param in parameters]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/parameters/all", response_model=List[ParameterResponse], tags=["parameters"])
def get_all_parameters_with_values(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get all parameters with their values."""
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        if not parameters:
            return []
        # Convert raw parameters into ParameterWithValues schema
        formatted_parameters = []
        for param in parameters:
            formatted_param = ParameterResponse(
                parameter_id=str(param.parameter_id),
                name=param.name,
                display_name=param.display_name,
                description=param.description,
                is_required=param.is_required,
                created_at=param.created_at,
                values=[
                    ParameterValueResponse(
                        value_id=str(value.value_id),
                        value=value.value, 
                        display_order=value.display_order,
                        created_at=value.created_at
                    )
                    for value in param.values
                ]
            )
            formatted_parameters.append(formatted_param)
        return formatted_parameters
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/{parameter_id}", response_model=ParameterResponse, tags=["parameters"])
def get_parameter(
    parameter_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get a parameter by ID."""
    try:
        result = parameter_repository.get_parameter_with_values(parameter_id)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/{parameter_id}/values", response_model=List[ParameterValueResponse], tags=["parameters"])
async def get_parameter_values(
    parameter_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        values = parameter_repository.get_parameter_values(parameter_id)
        return [ParameterValueResponse(value_id=str(value.value_id),value=value.value,display_order=value.display_order,created_at=value.created_at) for value in values]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameter management endpoints
@app.post("/parameters/", response_model=ParameterResponse, tags=["parameters"])
def create_parameter(
    name: str = Body(...),
    display_name: str = Body(...),
    description: Optional[str] = Body(None),
    is_required: bool = Body(True),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a new parameter."""
    try:
        result = parameter_repository.create_parameter({
            "name": name,
            "display_name": display_name,
            "description": description,
            "is_required": is_required
        })
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create parameter")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/parameters/{parameter_id}", response_model=ParameterResponse, tags=["parameters"])
def update_parameter(
    parameter_id: UUID,
    name: Optional[str] = Body(None),
    display_name: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    is_required: Optional[bool] = Body(None),
    current_user: dict = Depends(get_current_user_profile)
):
    """Update a parameter."""
    try:
        update_data = {k: v for k, v in {
            "name": name,
            "display_name": display_name,
            "description": description,
            "is_required": is_required
        }.items() if v is not None}

        result = parameter_repository.update_parameter(parameter_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/parameters/{parameter_id}", tags=["parameters"])
def delete_parameter(
    parameter_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Delete a parameter and its values."""
    try:
        success = parameter_repository.delete_parameter(parameter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return {"message": "Parameter and associated values deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameter values management endpoints
@app.post("/parameters/{parameter_id}/values", response_model=ParameterValueResponse, tags=["parameters"])
def create_parameter_value(
    parameter_id: UUID,
    value: str = Body(...),
    display_order: int = Body(0),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a new parameter value."""
    try:
        result = parameter_repository.create_parameter_value(parameter_id, value, display_order)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create parameter value")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/parameters/{parameter_id}/values/{value_id}", response_model=ParameterValueResponse, tags=["parameters"])
def update_parameter_value(
    parameter_id: UUID,
    value_id: UUID,
    value: Optional[str] = Body(None),
    display_order: Optional[int] = Body(None),
    current_user: dict = Depends(get_current_user_profile)
):
    """Update a parameter value."""
    try:
        update_data = {k: v for k, v in {
            "value": value,
            "display_order": display_order
        }.items() if v is not None}

        result = parameter_repository.update_parameter_value(value_id, parameter_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/parameters/{parameter_id}/values/{value_id}", tags=["parameters"])
def delete_parameter_value(
    parameter_id: UUID,
    value_id: UUID,
    current_user: dict = Depends(get_current_user_profile)
):
    """Delete a parameter value."""
    try:
        success = parameter_repository.delete_parameter_value(value_id, parameter_id)
        if not success:
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return {"message": "Parameter value deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/{template_id}/duplicate", response_model=TemplateResponse, tags=["templates"])
def duplicate_template(
    template_id: UUID, 
    new_name: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a copy of an existing template."""
    try:
        result = template_repository.duplicate_template(template_id, current_user.profile_id, new_name)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return template_repository.get_template_with_parameters(result["template_id"], UUID(current_user.profile_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/count", response_model=Dict[str, int], tags=["templates"])
def count_templates(
    template_type: Optional[str] = None,
    include_deleted: bool = False,
    current_user: dict = Depends(get_current_user_profile)
):
    """Get count of templates for the current user."""
    try:
        count = template_repository.count_templates(
            profile_id=current_user.profile_id,
            template_type=template_type,
            include_deleted=include_deleted
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sources/list", response_model=SourceListResponse, tags=["sources"])
async def list_sources(
    skip: int = 0,
    limit: int = 10,
    type: Optional[str] = None,
    source_identifier: Optional[str] = None,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        with db_manager.keep_session() as session:
            result = source_repository.list_sources_with_related(
                UUID(current_user.profile_id),
                type,
                source_identifier,
                skip,
                limit
            )
            return format_source_list_response(
                items=result,
                total=len(result),
                page=skip // limit + 1,
                size=limit
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sources/", response_model=Source, tags=["sources"])
async def create_source(
    source_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        return source_repository.create_source(source_data, UUID(current_user.profile_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/sources/{source_id}", tags=["sources"])
async def delete_source(
    source_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        result = source_repository.soft_delete(source_id, UUID(current_user.profile_id))
        if not result:
            raise HTTPException(status_code=404, detail="Source not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/{parameter_id}", response_model=ParameterResponse, tags=["parameters"])
async def get_parameter(parameter_id: UUID, current_user: Dict = Depends(get_current_user_profile)):
    try:
        parameter = parameter_repository.get_parameter_with_values(parameter_id)
        if not parameter:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return format_parameter_response(parameter)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/", response_model=List[ParameterResponse], tags=["parameters"])
async def list_parameters(skip: int = 0, limit: int = 100, current_user: Dict = Depends(get_current_user_profile)):
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        return [format_parameter_response(param) for param in parameters]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/parameters/{parameter_id}/values", tags=["parameters"])
async def create_parameter_value(
    parameter_id: UUID,
    value: str = Body(...),
    display_order: int = Body(0),
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        return parameter_repository.create_parameter_value(parameter_id, value, display_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/parameters/{parameter_id}/values/{value_id}", tags=["parameters"])
async def update_parameter_value(
    parameter_id: UUID,
    value_id: UUID,
    update_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        result = parameter_repository.update_parameter_value(value_id, parameter_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/parameters/{parameter_id}/values/{value_id}", tags=["parameters"])
async def delete_parameter_value(parameter_id: UUID, value_id: UUID, current_user: Dict = Depends(get_current_user_profile)):
    try:
        if not parameter_repository.delete_parameter_value(value_id, parameter_id):
            raise HTTPException(status_code=404, detail="Parameter value not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.backend.api:app", host="0.0.0.0", port=8000, reload=False)

