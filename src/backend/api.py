import os
import uuid
from fastapi import FastAPI, HTTPException, Depends, Query, Security, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.backend.db.supabaseclient import supabase_client
from src.backend.db.supabasedatamodel import *
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
from src.backend.db.repository import RateLimitExceeded, QuotaExceeded
from fastapi.responses import JSONResponse

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

supabase = supabase_client()
security = HTTPBearer()

# Setup logger
logger = setup_logger(__name__)

# Initialize repositories
template_repository = TemplateRepository()
parameter_repository = ParameterRepository()
content_repository = ContentRepository()
profile_repository = ProfileRepository()
source_repository = SourceRepository()
content_type_repository = ContentTypeRepository()
auth_repository = AuthRepository(supabase)

# Token Generation Models
class TokenRequest(BaseModel):
    provider: str  # e.g., "google", "github"

class TokenResponse(BaseModel):
    oauth_url: str  # URL to redirect the user for OAuth authentication

class CallbackResponse(BaseModel):
    access_token: str  # The access token returned after the OAuth flow
    token_type: str    # The type of token (e.g., "bearer")


# Model for a single parameter value
class TemplateParameterValue(BaseModel):
    parameter_id: UUID
    value_id: UUID
    value: str  # The actual value (e.g., "Technical Expert")

# Model for a single parameter
class TemplateParameter(BaseModel):
    parameter_id: UUID
    name: str  # Parameter name (e.g., "persona")
    display_name: str  # Friendly name for UI
    value: TemplateParameterValue  # Selected value

# Model for creating a template
class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str = "default"
    template_image_url: Optional[str] = None
    parameters: List[TemplateParameter]  # List of selected parameters

# Model for updating a template
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    template_image_url: Optional[str] = None
    parameters: Optional[List[TemplateParameter]] = None  # Optional list of updated parameters

# Model for template response
class TemplateResponse(BaseModel):
    template_id: UUID
    name: str
    description: Optional[str] = None
    template_type: str
    template_image_url: Optional[str] = None
    parameters: List[TemplateParameter]  # List of parameters with selected values
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

# Model for filtering templates
class TemplateFilter(BaseModel):
    persona: Optional[str] = None
    age_group: Optional[str] = None
    content_type: Optional[str] = None
    template_type: Optional[str] = None  # Default or custom
    is_deleted: Optional[bool] = False  # Filter by soft-deleted templates

class ParameterResponse(BaseModel):
    parameter_id: str
    name: str
    display_name: str
    description: Optional[str]
    is_required: bool
    created_at: datetime

class ParameterFilter(BaseModel):
    parameter_id: UUID
    value_id: UUID

class AdvancedTemplateFilter(BaseModel):
    parameters: List[ParameterFilter]
    template_type: Optional[str] = None
    is_deleted: Optional[bool] = False

class ParameterValueResponse(BaseModel):
    value_id: str
    value: str
    display_order: int
    created_at: datetime

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
    source_type: Optional[str]  # Add source_type field

class ContentListResponse(BaseModel):
    items: List[ContentListItem]
    total: int
    page: int
    size: int

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

class SourceListResponse(BaseModel):
    items: List[Dict]
    total: int
    page: int
    size: int

class GenerationLimitResponse(BaseModel):
    tier: str
    max_generations: int
    generations_used: int

# Add new models for Reddit endpoints
class RedditRequest(BaseModel):
    subreddits: Optional[List[str]] = None
    category: Optional[str] = None
    timeframe: Optional[str] = 'day'
    limit: Optional[int] = 10

class RedditResponse(BaseModel):
    data: Dict[str, Any]
    status: str
    error: Optional[str] = None

class RedditSuggetsionsResponse(BaseModel):
    blog_topics: List[str]

# Agent Workflow Endpoint
def get_workflow() -> AgentWorkflow:
    """Dependency to get a AgentWorkflow instance."""
    return AgentWorkflow()

# Authentication Dependency
async def get_current_user_profile(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    user = await auth_repository.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    profile = profile_repository.find_by_id("user_id", user.user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@app.post("/token", response_model=TokenResponse, tags=["auth"])
async def generate_token(token_request: TokenRequest):
    try:
        redirect_url = os.getenv("VITE_API_URL", "http://localhost:8000")
        credentials = {
            "provider": token_request.provider,
            "options": {
                "redirect_to": f"{redirect_url}/callback",
            }
        }

        if token_request.provider == 'google':
            credentials['options']['scopes'] = ['email', 'profile']

        response = await auth_repository.sign_in_with_oauth(credentials)
        if not response or not hasattr(response, "url"):
            raise HTTPException(status_code=401, detail="Failed to initiate OAuth flow")

        return {"oauth_url": response.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/callback", response_model=CallbackResponse, tags=["auth"])
async def oauth_callback(code: str, state: Optional[str] = None):
    try:
        # Prepare the parameters for exchange_code_for_session
        params = {
            "auth_code": code,  # The authorization code from the OAuth provider
            # Optionally, include code_verifier if using PKCE
            # "code_verifier": "your_code_verifier",
            # Optionally, include redirect_to if needed
            # "redirect_to": "http://localhost:8000/callback",
        }

        # Exchange the authorization code for a session
        response = supabase.auth.exchange_code_for_session(params)

        # Check if the response contains a session with an access token
        if not response or not response.session or not response.session.access_token:
            raise HTTPException(status_code=401, detail="Failed to exchange code for token")

        if response and response.session:
            user = response.session.user
            
            # For Google Auth, create/update profile
            if user.app_metadata.get('provider') == 'google':
                # Get user info from Google
                user_info = response.session.user.user_metadata
                
                # Create/update profile
                profile_data = {
                    "user_id": user.id,
                    "full_name": user_info.get('full_name'),
                    "avatar_url": user_info.get('avatar_url'),
                    "role": "free",  # Set default role
                    "subscription_status": "none"  # Set default subscription
                }
                
                supabase.table('profiles').upsert(profile_data).execute()
            else:
                # For email registration, create basic profile
                profile_data = {
                    "user_id": user.id,
                    "role": "free",
                    "subscription_status": "none"
                }
                supabase.table('profiles').upsert(profile_data).execute()

        # Return the access token to the client
        return {"access_token": response.session.access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signup", tags=["auth"])
async def signup(email: str, password: str):
    try:
        auth_response = await auth_repository.sign_up(email, password)
        
        if auth_response.error:
            raise HTTPException(status_code=400, detail=str(auth_response.error))

        if auth_response.user:
            profile_data = {
                "user_id": auth_response.user.id,
                "email": email,
                "role": "free",
                "subscription_status": "none"
            }
            result = profile_repository.create(profile_data)
            
            if not result:
                # Rollback user creation if profile creation fails
                await auth_repository.delete_user(auth_response.user.id)
                raise HTTPException(status_code=400, detail="Failed to create profile")

        return auth_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/callback", response_model=CallbackResponse, tags=["auth"])
async def oauth_callback(code: str):
    try:
        response = await auth_repository.exchange_code_for_session({"auth_code": code})
        
        if response.error:
            raise HTTPException(status_code=401, detail=str(response.error))

        if response.user and response.user.app_metadata.get('provider') == 'google':
            profile_data = {
                "user_id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get('full_name'),
                "avatar_url": response.user.user_metadata.get('avatar_url'),
                "role": "free",
                "subscription_status": "none"
            }
            
            result = profile_repository.update(
                id_field="user_id",
                id_value=response.user.id,
                data=profile_data
            )
            if not result:
                result = profile_repository.create(profile_data)

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print("OAuth callback error:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", tags=["auth"]) 
async def signin(email: str, password: str):
    try:
        response = await auth_repository.sign_in(email, password)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signout", tags=["auth"])
async def signout(user: dict = Depends(get_current_user_profile)):
    try:
        response = await auth_repository.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Profile Endpoints
@app.post("/profiles/", response_model=Profile, tags=["profiles"])
def create_profile(profile: ProfileCreate, user: dict = Depends(get_current_user_profile)):
    """Create a new profile"""
    profile.user_id = user["id"]  # Ensure profile is linked to authenticated user
    result = profile_repository.create(profile.dict())
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create profile")
    return result

@app.get("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
def read_profile(profile_id: UUID, user: dict = Depends(get_current_user_profile)):
    """Get a profile by ID"""
    result = profile_repository.find_by_id("id", profile_id)
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result

@app.put("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
def update_profile(profile_id: UUID, profile: ProfileUpdate, user: dict = Depends(get_current_user_profile)):
    """Update a profile by ID"""
    # Check if profile belongs to user
    if str(profile_id) != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
    result = profile_repository.update(
        id_field="id",
        id_value=profile_id,
        data=profile.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result

@app.delete("/profiles/{profile_id}", tags=["profiles"])
def delete_profile(profile_id: UUID, user: dict = Depends(get_current_user_profile)):
    """Soft delete a profile"""
    # Check if profile belongs to user
    if str(profile_id) != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
        
    result = profile_repository.update(
        id_field="id",
        id_value=profile_id,
        data={
            "is_deleted": True
        }
    )
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}

@app.get("/profiles/", response_model=List[Profile], tags=["profiles"])
def filter_profiles(
    user_id: Optional[UUID] = None,
    role: Optional[str] = None,
    subscription_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    user: dict = Depends(get_current_user_profile)
):
    """Filter profiles based on criteria"""
    filters = {}
    if user_id:
        filters["user_id"] = str(user_id)
    if role:
        filters["role"] = role
    if subscription_status:
        filters["subscription_status"] = subscription_status
        
    results = profile_repository.filter(filters, skip, limit)
    return results

# ContentType Endpoints
@app.post("/content-types/", response_model=ContentType, tags=["content_types"])
def create_content_type(content_type: ContentTypeCreate, user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.create(content_type.dict())
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create content type")
    return result

@app.get("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def read_content_type(content_type_id: UUID, user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.find_by_id("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@app.put("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def update_content_type(content_type_id: UUID, content_type: ContentTypeUpdate, user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.update(
        id_field="content_type_id",
        id_value=content_type_id,
        data=content_type.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return result

@app.delete("/content-types/{content_type_id}", tags=["content_types"])
def delete_content_type(content_type_id: UUID, user: dict = Depends(get_current_user_profile)):
    result = content_type_repository.delete("content_type_id", content_type_id)
    if not result:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return {"message": "ContentType deleted"}

@app.get("/content-types/", response_model=List[ContentType], tags=["content_types"])
def filter_content_types(name: Optional[str] = None, skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user_profile)):
    query_filters = {}
    if name:
        query_filters["name"] = name
    result = content_type_repository.filter(query_filters, skip, limit)
    return result

# Update content endpoints to use profile_id
@app.post("/content/", response_model=Content, tags=["content"])
def create_content(content: ContentCreate, profile: dict = Depends(get_current_user_profile)):
    """Create new content"""
    try:
        with content_repository.rate_limited_operation(
            profile_id=profile["id"],
            action_type='content_creation',
            limit=20,  # 20 manual content creations per hour
            window_minutes=60
        ):
            content_data = content.dict()
            content_data['profile_id'] = profile['id']
            result = content_repository.create(content_data)
            if not result:
                raise HTTPException(status_code=400, detail="Failed to create content")
            return result
    except RateLimitExceeded as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/content/", tags=["content"])
def filter_content(
    content_type_id: Optional[UUID] = None, 
    status: Optional[str] = None, 
    search_text: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    profile: dict = Depends(get_current_user_profile)
):
    """List/filter content"""
    filters = {
        "profile_id": profile["id"],
        "is_deleted": False
    }
    if content_type_id:
        filters["content_type_id"] = str(content_type_id)
    if status:
        filters["status"] = status
        
    result = content_repository.filter_content(profile["id"], {
        "content_type_id": content_type_id,
        "status": status,
        "title_contains": search_text
    }, skip, limit)
    
    return result

@app.get("/content/all", response_model=List[Dict], tags=["content"])
def get_all_content(skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user_profile)):
    query = (
        supabase.table("content")
        .select(
            """
            content_id, title, body, status, created_at, updated_at, published_at,
            content_types (content_type_id, name),
            profiles (id, full_name, avatar_url, role),
            content_sources (source_id),
            url_references (url_reference_id, url, description),
            media (media_id, media_url, media_type),
            content_tags (tag_id),
            tags (tag_id, name),
            metadata (metadata_id, key, value)
            """
        )
        .eq('profile_id', user['id'])  # Add filter by profile_id
        .order("created_at", desc=True)
        .range(skip, skip + limit - 1)
    )
    response = query.execute()
    return response.data

@app.post("/content/generate", tags=["agents"])
async def generate_generic_blog(
    payload: GeneratePostRequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    user: dict = Depends(get_current_user_profile),
):
    """Initiate the workflow with the provided data."""
    logger.info(f"Starting content generation for user {user['id']} with payload type: {type(payload).__name__}")
    try:
        thread_id = payload.thread_id or str(uuid.uuid4())
        logger.debug(f"Using thread_id: {thread_id}")

        # Get template and parameters if template_id is provided
        if (payload.template_id):
            template_data = read_template(UUID(payload.template_id), user)
            payload_dict = payload.model_dump()
            payload_dict["template"] = template_data

        # Use repository's rate limiting and quota checking
        period_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        with content_repository.quota_limited_operation(
            profile_id=user['id'],
            quota_type='content_generation',
            period_start=period_start
        ):
            with content_repository.rate_limited_operation(
                profile_id=user['id'],
                action_type='content_generation',
                limit=5,  # 5 generations per hour
                window_minutes=60
            ):
                # Proceed with generation
                logger.debug("Starting workflow execution")
                result = workflow.run_generic_workflow(payload.model_dump(), thread_id, user)
                logger.debug("Workflow execution completed")
                return result

    except (RateLimitExceeded, QuotaExceeded) as e:
        logger.warning(f"Limit exceeded for user {user['id']}: {str(e)}")
        raise
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
    
# Update content endpoints to use profile_id
@app.get("/content/list", response_model=ContentListResponse)
async def list_content(skip: int = 0, limit: int = 10, profile: dict = Depends(get_current_user_profile)):
    results = content_repository.list_content(profile["id"], skip, limit)
    
    items = [
        ContentListItem(
            id=item["content_id"],
            title=item["title"] if item["content_types"]["name"] == "blog" else "",
            content=item["body"] if item["content_types"]["name"] == "blog" else "",
            tags=[tag["tags"]["name"] for tag in item.get("content_tags", []) if tag.get("tags")],
            createdAt=item["created_at"],
            updatedAt=item["updated_at"],
            status=item["status"],
            twitter_post=item["body"] if item["content_types"]["name"] == "twitter_post" else "",
            linkedin_post=item["body"] if item["content_types"]["name"] == "linkedin_post" else "",
            urls=[{
                "url": ref["url"],
                "type": ref.get("type"),
                "domain": ref.get("domain")
            } for source in item.get("content_sources", [])
                if source.get("sources") and source["sources"].get("url_references")
                for ref in source["sources"]["url_references"]
                if item["content_types"]["name"] == "blog"],
            media=[{
                "url": media["media_url"],
                "type": media["media_type"]
            } for source in item.get("content_sources", [])
                if source.get("sources") and source["sources"].get("media")
                for media in source["sources"]["media"]
                if item["content_types"]["name"] == "blog"],
            source_type=next((source["sources"]["source_types"]["name"]
                for source in item.get("content_sources", [])
                if source.get("sources") and source["sources"].get("source_types")), None)
        )
        for item in results
    ]

    return ContentListResponse(
        items=items,
        total=len(results),
        page=skip // limit + 1,
        size=limit
    )

@app.get("/content/filter", response_model=ContentListResponse)
async def filter_content(
    skip: int = 0,
    limit: int = 10,
    title_contains: Optional[str] = Query(None, description="Filter by title containing a string"),
    post_type: Optional[str] = Query(None, description="Filter by post type (e.g., blog, twitter_post)"),
    status: Optional[str] = Query(None, description="Filter by status (e.g., published, draft)"),
    domain: Optional[str] = Query(None, description="Filter by domain in URL references"),
    tag_name: Optional[str] = Query(None, description="Filter by tag name"),
    source_type: Optional[str] = Query(None, description="Filter by source type (e.g., news, social_media)"),
    created_after: Optional[datetime] = Query(None, description="Filter by content created after a date"),
    created_before: Optional[datetime] = Query(None, description="Filter by content created before a date"),
    updated_after: Optional[datetime] = Query(None, description="Filter by content updated after a date"),
    updated_before: Optional[datetime] = Query(None, description="Filter by content updated before a date"),
    media_type: Optional[str] = Query(None, description="Filter by media type (e.g., image, video)"),
    url_type: Optional[str] = Query(None, description="Filter by URL type (e.g., internal, external)"),
    user: dict = Depends(get_current_user_profile)
):
    filters = {
        "title_contains": title_contains,
        "post_type": post_type,
        "status": status,
        "domain": domain,
        "tag_name": tag_name,
        "source_type": source_type,
        "created_after": created_after,
        "created_before": created_before,
        "updated_after": updated_after,
        "updated_before": updated_before,
        "media_type": media_type,
        "url_type": url_type
    }
    
    results = content_repository.filter_content(user["id"], filters, skip, limit)
    
    items = [
        ContentListItem(
            id=item["content_id"],
            thread_id=item["thread_id"],
            source_identifier=next(
                (source["source"]["source_identifier"]
                for source in item.get("content_sources", [])
                if source.get("source") and source["source"].get("source_identifier")),
                ""
            ),
            title=item.get("title", "") if item.get("content_types", {}).get("name") == "blog" else "",
            content=item.get("body", "") if item.get("content_types", {}).get("name") == "blog" else "",
            tags=[tag["tags"]["name"] for tag in item.get("content_tags", []) if tag.get("tags")],
            createdAt=item["created_at"],
            updatedAt=item["updated_at"],
            status=item["status"],
            twitter_post=item.get("body", "") if item.get("content_types", {}).get("name") == "twitter_post" else "",
            linkedin_post=item.get("body", "") if item.get("content_types", {}).get("name") == "linkedin_post" else "",
            urls=[{
                "url": ref["url"],
                "type": ref.get("type"),
                "domain": ref.get("domain")
            } for source in item.get("content_sources", [])
                if source.get("source") and source["source"].get("url_references")
                for ref in source["source"]["url_references"]
                if item.get("content_types", {}).get("name") == "blog"],
            media=[{
                "url": media["media_url"],
                "type": media["media_type"]
            } for source in item.get("content_sources", [])
                if source.get("source") and source["source"].get("media")
                for media in source["source"]["media"]
                if item.get("content_types", {}).get("name") == "blog"],
            source_type=next((source["source"]["source_types"]["name"]
                for source in item.get("content_sources", [])
                if source.get("source") and source["source"].get("source_types")), None)
        )
        for item in results
    ]

    return ContentListResponse(
        items=items,
        total=len(results),
        page=skip // limit + 1,
        size=limit
    )

@app.get("/content/{content_id}", response_model=Content, tags=["content"])
def read_content(content_id: UUID, user: dict = Depends(get_current_user_profile)):
    """Get content by ID"""
    result = content_repository.find_by_id("content_id", content_id)
    if not result:
        raise HTTPException(status_code=404, detail="Content not found")
    if result["profile_id"] != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this content")
    return result

@app.put("/content/{content_id}", response_model=Content, tags=["content"]) 
def update_content(content_id: UUID, content: ContentUpdate, profile: dict = Depends(get_current_user_profile)):
    """Update content"""
    result = content_repository.update(
        id_field="content_id",
        id_value=content_id,
        data=content.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Content not found")
    if result["profile_id"] != str(profile["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this content")
    return result

@app.delete("/content/thread/{thread_id}", tags=["content"])
def delete_content(thread_id: UUID, profile: dict = Depends(get_current_user_profile)):
    """Soft delete content"""
    content = content_repository.find_by_id("thread_id", thread_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content["profile_id"] != str(profile["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this content")
        
    result = content_repository.soft_delete("thread_id", thread_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete content")
    return {"message": "Content deleted"}

@app.put("/content/thread/{thread_id}/save", tags=["content"])
async def save_thread_content(
    thread_id: UUID, 
    payload: SaveContentRequest, 
    user: dict = Depends(get_current_user_profile)
):
    """Save all content types for a thread in a single transaction"""
    try:
        with content_repository.rate_limited_operation(
            profile_id=user["id"],
            action_type='content_save',
            limit=60,  # 60 saves per hour
            window_minutes=60
        ):
            # Get content type mapping
            type_map = content_type_repository.get_content_type_map(["blog", "twitter", "linkedin"])
            if not type_map:
                raise HTTPException(status_code=400, detail="Failed to get content types")
                
            result = content_repository.save_thread_content(thread_id, user["id"], payload.dict(), type_map)
            return {"message": "Content saved successfully", "content": result}
    except RateLimitExceeded as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/content/thread/{thread_id}/schedule", tags=["content"])
async def schedule_thread_content(thread_id: UUID, payload: ScheduleContentRequest):
    """Schedule content for publishing"""
    try:
        async with supabase.pool.acquire() as connection:
            async with connection.transaction():
                # Get content type for the platform
                content_type = supabase.table("content_types").select("*").eq("name", f"{payload.platform}_post").execute()
                
                if not content_type.data:
                    raise HTTPException(status_code=400, detail=f"Invalid platform: {payload.platform}")

                # Update the specific content type for this thread
                response = supabase.table("content").update({
                    "status": payload.status,
                    "scheduled_at": payload.schedule_date
                }).eq("thread_id", thread_id).eq("content_type_id", content_type.data[0]["content_type_id"]).execute()

                return {"message": "Content scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update sources endpoints to use profile_id
@app.post("/sources/", response_model=Source, tags=["sources"])
def create_source(source: SourceCreate, profile: dict = Depends(get_current_user_profile)):
    """Create a new source"""
    try:
        with source_repository.rate_limited_operation(
            profile_id=profile["id"],
            action_type='source_creation',
            limit=30,  # 30 sources per hour
            window_minutes=60
        ):
            result = source_repository.create_source(source.dict(), profile['id'])
            if not result:
                raise HTTPException(status_code=400, detail="Failed to create source")
            return result
    except RateLimitExceeded as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sources/", response_model=SourceListResponse, tags=["sources"])
def filter_sources(
    type: Optional[str] = None, 
    source_identifier: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    profile: dict = Depends(get_current_user_profile)
):
    result = source_repository.list_sources_with_related(
        profile_id=profile['id'],
        type=type,
        source_identifier=source_identifier,
        skip=skip,
        limit=limit
    )
    return SourceListResponse(**result)

@app.get("/sources/{source_id}", response_model=Source, tags=["sources"])
def read_source(source_id: UUID, user: dict = Depends(get_current_user_profile)):
    result = source_repository.find_by_id("source_id", source_id)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@app.put("/sources/{source_id}", response_model=Source, tags=["sources"])
def update_source(source_id: UUID, source: SourceUpdate, profile: dict = Depends(get_current_user_profile)):
    result = source_repository.update(
        id_field="source_id",
        id_value=source_id,
        data=source.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result

@app.delete("/sources/{source_id}", tags=["sources"])
def delete_source(source_id: UUID, profile: dict = Depends(get_current_user_profile)):
    result = source_repository.soft_delete(source_id, profile["id"])
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted"}

@app.get("/content/thread/{thread_id}", response_model=ContentListItem, tags=["content"]) 
async def get_content_by_thread(
    thread_id: UUID,
    post_type: Optional[str] = Query(None, description="Filter by post type (blog, twitter, linkedin)"),
    user: dict = Depends(get_current_user_profile)
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

        result = content_repository.get_content_by_thread(thread_id, user["id"], content_type_id)

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

        content_type = result.get("content_type", {}).get("name")
        source_info = next(iter(result.get("content_sources", [])), {})
        source = source_info.get("source", {})

        return ContentListItem(
            id=result["content_id"],
            thread_id=str(thread_id),
            source_identifier=source.get("source_identifier"),
            title=result.get("title", "") if content_type == "blog" else "",
            content=result.get("body", ""),
            tags=[tag["tag"]["name"] for tag in result.get("content_tags", []) if tag.get("tag")],
            createdAt=result["created_at"],
            updatedAt=result["updated_at"],
            status=result["status"],
            twitter_post=result.get("body", "") if content_type == "twitter_post" else "",
            linkedin_post=result.get("body", "") if content_type == "linkedin_post" else "",
            urls=[{
                "url": ref["url"],
                "type": ref.get("type"),
                "domain": ref.get("domain")
            } for ref in source.get("url_references", [])],
            media=[{
                "url": media["media_url"],
                "type": media["media_type"]
            } for media in source.get("media", [])],
            source_type=source.get("source_type", {}).get("name")
        )
    except Exception as e:
        logger.error(f"Error getting content by thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving content")

@app.get("/reddit/trending", response_model=RedditResponse, tags=["reddit"])
async def get_trending_reddit_topics(
    limit: int = Query(10, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    user: dict = Depends(get_current_user_profile)
):
    """Fetch trending topics from specified subreddits or r/all"""
    try:
        reddit_extractor = RedditExtractor()
        subreddit_list = subreddits.split(',') if subreddits else None
        trending_data = reddit_extractor.get_trending_topics(
            limit=limit,
            subreddits=subreddit_list
        )

        # Use llm to identify the topics for blog posts

        
        return RedditResponse(
            data=trending_data,
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
        )

@app.get("/reddit/discussions", response_model=RedditResponse, tags=["reddit"])
async def get_trending_discussions(
    category: str = Query('all', description="Category/subreddit to fetch from"),
    timeframe: str = Query('day', description="Time period (hour, day, week, month, year, all)"),
    limit: int = Query(10, description="Number of posts to fetch"),
    user: dict = Depends(get_current_user_profile)
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

@app.get("/reddit/topic-suggestions", response_model=RedditSuggetsionsResponse, tags=["reddit"])
async def get_topic_suggetsions(
    limit: int = Query(15, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    user: dict = Depends(get_current_user_profile)
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
    user: dict = Depends(get_current_user_profile)
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
    user: dict = Depends(get_current_user_profile)
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
    user: dict = Depends(get_current_user_profile)
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
def create_template(template: TemplateCreate, profile: dict = Depends(get_current_user_profile)):
    """Create a new template."""
    try:
        with template_repository.rate_limited_operation(
            profile_id=profile["id"],
            action_type='template_creation',
            limit=10,  # 10 templates per hour
            window_minutes=60
        ):
            template_data = {
                "name": template.name,
                "description": template.description,
                "template_type": template.template_type,
                "template_image_url": template.template_image_url,
                "profile_id": profile["id"],
                "is_deleted": False
            }
            result = template_repository.create_template_with_parameters(template_data, template.parameters)
            if not result:
                raise HTTPException(status_code=400, detail="Failed to create template")
            return read_template(result["template_id"], profile)
    except RateLimitExceeded as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
def read_template(template_id: UUID, profile: dict = Depends(get_current_user_profile)):
    """Get a template by ID."""
    try:
        result = template_repository.get_template_with_parameters(template_id, profile["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
def update_template(template_id: UUID, template: TemplateUpdate, profile: dict = Depends(get_current_user_profile)):
    """Update a template by ID."""
    try:
        update_data = template.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        result = template_repository.update_template_with_parameters(
            template_id=template_id,
            profile_id=profile["id"],
            template_data=update_data,
            parameters=template.parameters
        )
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return read_template(template_id, profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/templates/{template_id}", tags=["templates"])
def delete_template(template_id: UUID, profile: dict = Depends(get_current_user_profile)):
    """Soft delete a template by ID."""
    try:
        result = template_repository.update_template_with_parameters(
            template_id=template_id,
            profile_id=profile["id"],
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
def list_templates(
    skip: int = 0, 
    limit: int = 10, 
    template_type: Optional[str] = None, 
    profile: dict = Depends(get_current_user_profile)
):
    """List all templates for the authenticated user."""
    try:
        results = template_repository.list_templates_for_profile(
            profile_id=profile["id"],
            skip=skip,
            limit=limit,
            template_type=template_type,
            include_deleted=False
        )
        return [read_template(UUID(t["template_id"]), profile) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/filter", response_model=List[TemplateResponse], tags=["templates"])
def filter_templates(
    filter: TemplateFilter, 
    skip: int = 0, 
    limit: int = 10, 
    profile: dict = Depends(get_current_user_profile)
):
    """Filter templates based on parameters."""
    try:
        results = template_repository.list_templates_for_profile(
            profile_id=profile["id"],
            skip=skip,
            limit=limit,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted or False
        )
        return [read_template(UUID(t["template_id"]), profile) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/templates/advanced-filter", response_model=List[TemplateResponse], tags=["templates"])
def advanced_filter_templates(
    filter: AdvancedTemplateFilter,
    skip: int = 0,
    limit: int = 10,
    profile: dict = Depends(get_current_user_profile)
):
    """Filter templates by multiple parameters."""
    try:
        results = template_repository.filter_templates(
            profile_id=profile["id"],
            parameters=filter.parameters,
            template_type=filter.template_type,
            include_deleted=filter.is_deleted,
            skip=skip,
            limit=limit
        )
        return [read_template(UUID(t["template_id"]), profile) for t in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/", response_model=List[ParameterResponse], tags=["parameters"])
def get_all_parameters(
    skip: int = 0, 
    limit: int = 100,
    profile: dict = Depends(get_current_user_profile)
):
    """Get all available parameters."""
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        return [param for param in parameters]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Response model for parameter values
class ParameterWithValues(BaseModel):
    parameter_id: UUID
    name: str
    display_name: str
    description: Optional[str]
    is_required: bool
    created_at: datetime
    values: List[ParameterValueResponse]

@app.get("/parameters/all", response_model=List[ParameterWithValues], tags=["parameters"])
def get_all_parameters_with_values(
    skip: int = 0,
    limit: int = 100,
    profile: dict = Depends(get_current_user_profile)
):
    """Get all parameters with their values."""
    try:
        parameters = parameter_repository.list_parameters_with_values(skip, limit)
        if not parameters:
            return []
        # Convert raw parameters into ParameterWithValues schema
        formatted_parameters = []
        for param in parameters:
            formatted_param = ParameterWithValues(
                parameter_id=param["parameter_id"],
                name=param["name"],
                display_name=param["display_name"],
                description=param.get("description"),
                is_required=param["is_required"],
                created_at=param["created_at"],
                values=[
                    ParameterValueResponse(
                        value_id=value["value_id"],
                        value=value["value"], 
                        display_order=value["display_order"],
                        created_at=value["created_at"]
                    )
                    for value in param.get("parameter_values", [])
                ]
            )
            formatted_parameters.append(formatted_param)
        return formatted_parameters
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/{parameter_id}", response_model=ParameterResponse, tags=["parameters"])
def get_parameter(
    parameter_id: UUID,
    profile: dict = Depends(get_current_user_profile)
):
    """Get a parameter by ID."""
    try:
        result = parameter_repository.get_parameter(parameter_id)
        if not result:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parameters/{parameter_id}/values", response_model=List[ParameterValueResponse], tags=["parameters"])
def get_parameter_values(
    parameter_id: UUID, 
    profile: dict = Depends(get_current_user_profile)
):
    """Get allowed values for a parameter."""
    try:
        parameter = parameter_repository.get_parameter_with_values(parameter_id)
        if not parameter:
            raise HTTPException(status_code=404, detail="Parameter not found")
        return parameter.get("parameter_values", [])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameter management endpoints
@app.post("/parameters/", response_model=ParameterResponse, tags=["parameters"])
def create_parameter(
    name: str = Body(...),
    display_name: str = Body(...),
    description: Optional[str] = Body(None),
    is_required: bool = Body(True),
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
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
    profile: dict = Depends(get_current_user_profile)
):
    """Create a copy of an existing template."""
    try:
        result = template_repository.duplicate_template(template_id, profile["id"], new_name)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        return read_template(result["template_id"], profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/templates/count", response_model=Dict[str, int], tags=["templates"])
def count_templates(
    template_type: Optional[str] = None,
    include_deleted: bool = False,
    profile: dict = Depends(get_current_user_profile)
):
    """Get count of templates for the current user."""
    try:
        count = template_repository.count_templates(
            profile_id=profile["id"],
            template_type=template_type,
            include_deleted=include_deleted
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": str(exc)}
    )

@app.exception_handler(QuotaExceeded)
async def quota_exceeded_handler(request: Request, exc: QuotaExceeded):
    return JSONResponse(
        status_code=402,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run("src.backend.api:app", host="0.0.0.0", port=8000, reload=False)

