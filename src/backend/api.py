import os
import uuid
from fastapi import FastAPI, HTTPException, Depends, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabaseclient import supabase_client
from db.supabasedatamodel import *
from typing import List, Optional
import uvicorn
from src.backend.agents.blogs import AgentWorkflow
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
from datetime import datetime
from uuid import UUID

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

# Token Generation Models
class TokenRequest(BaseModel):
    provider: str  # e.g., "google", "github"

class TokenResponse(BaseModel):
    oauth_url: str  # URL to redirect the user for OAuth authentication

class CallbackResponse(BaseModel):
    access_token: str  # The access token returned after the OAuth flow
    token_type: str    # The type of token (e.g., "bearer")

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

class SourceListResponse(BaseModel):
    items: List[Dict]
    total: int
    page: int
    size: int

class GenerationLimitResponse(BaseModel):
    tier: str
    max_generations: int
    generations_used: int

# Agent Workflow Endpoint
def get_workflow() -> AgentWorkflow:
    """Dependency to get a AgentWorkflow instance."""
    return AgentWorkflow()

# Authentication Dependency
async def get_current_user_profile(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get associated profile
    profile = supabase.table("profiles").select("*").eq("user_id", user.user.id).single().execute()
    if not profile.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.data

@app.post("/token", response_model=TokenResponse, tags=["auth"])
def generate_token(token_request: TokenRequest):
    provider = token_request.provider
    try:
        # Prepare the credentials dictionary
        redirect_url = os.getenv("VITE_API_URL", "http://localhost:8000")
        credentials = {
            "provider": provider,
            "options": {
            "redirect_to": f"{redirect_url}/callback",  # Use environment variable if available
            # Add other options if needed, e.g., "scopes" or "query_params"
            }
        }

        # For Google sign-in, request additional scopes
        if provider == 'google':
            credentials['options']['scopes'] = ['email', 'profile']

        # Sign in with the OAuth provider
        response = supabase.auth.sign_in_with_oauth(credentials)

         # Check if the response is valid
        if not response or not hasattr(response, "url"):
            raise HTTPException(status_code=401, detail="Failed to initiate OAuth flow")

        # Return the OAuth URL to the client
        return {"oauth_url": response.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update callback to use correct profile schema
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
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.error:
            raise HTTPException(status_code=400, detail=str(auth_response.error))

        if auth_response.user:
            # Create profile
            profile_response = supabase.table('profiles').insert({
                "user_id": auth_response.user.id,
                "email": email,
                "role": "free",
                "subscription_status": "none"
            }).execute()
            
            if profile_response.error:
                # Rollback user creation if profile creation fails
                await supabase.auth.admin.delete_user(auth_response.user.id)
                raise HTTPException(status_code=400, detail="Failed to create profile")

        return auth_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/callback", response_model=CallbackResponse, tags=["auth"])
async def oauth_callback(code: str):
    try:
        # Exchange code for session
        response = await supabase.auth.exchange_code_for_session({"auth_code": code})
        
        if response.error:
            raise HTTPException(status_code=401, detail=str(response.error))

        # Create/update profile for Google user
        if response.user and response.user.app_metadata.get('provider') == 'google':
            profile_data = {
                "user_id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get('full_name'),
                "avatar_url": response.user.user_metadata.get('avatar_url'),
                "role": "free",
                "subscription_status": "none"
            }
            
            await supabase.table('profiles').upsert(profile_data).execute()

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print("OAuth callback error:", str(e))  # Debug log
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", tags=["auth"]) 
async def signin(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signout", tags=["auth"])
async def signout(user: dict = Depends(get_current_user_profile)):
    try:
        response = supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Profile Endpoints
@app.post("/profiles/", response_model=Profile, tags=["profiles"])
def create_profile(profile: ProfileCreate, user: dict = Depends(get_current_user_profile)):
    profile.user_id = user.id  # Ensure the profile is linked to the authenticated user
    response = supabase.table("profiles").insert(profile.dict()).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create profile")
    return response.data[0]

@app.get("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
def read_profile(profile_id: UUID, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("profiles").select("*").eq("id", profile_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return response.data[0]

@app.put("/profiles/{profile_id}", response_model=Profile, tags=["profiles"])
def update_profile(profile_id: UUID, profile: ProfileUpdate, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("profiles").update(profile.dict()).eq("id", profile_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return response.data[0]

@app.delete("/profiles/{profile_id}", tags=["profiles"])
def delete_profile(profile_id: UUID, user: dict = Depends(get_current_user_profile)):
    # Perform soft delete by updating deleted_at and is_deleted fields 
    response = supabase.table("profiles").update({
        "deleted_at": datetime.now().isoformat(),
        "is_deleted": True
    }).eq("id", profile_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}

@app.get("/profiles/", response_model=List[Profile], tags=["profiles"])
def filter_profiles(user_id: Optional[UUID] = None, role: Optional[str] = None, subscription_status: Optional[str] = None, skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user_profile)):
    query = supabase.table("profiles").select("*").range(skip, skip + limit - 1)
    if user_id:
        query = query.eq("user_id", user_id)
    if role:
        query = query.eq("role", role)
    if subscription_status:
        query = query.eq("subscription_status", subscription_status)
    response = query.execute()
    return response.data

# ContentType Endpoints
@app.post("/content-types/", response_model=ContentType, tags=["content_types"])
def create_content_type(content_type: ContentTypeCreate, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("content_types").insert(content_type.dict()).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create content type")
    return response.data[0]

@app.get("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def read_content_type(content_type_id: UUID, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("content_types").select("*").eq("content_type_id", content_type_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return response.data[0]

@app.put("/content-types/{content_type_id}", response_model=ContentType, tags=["content_types"])
def update_content_type(content_type_id: UUID, content_type: ContentTypeUpdate, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("content_types").update(content_type.dict()).eq("content_type_id", content_type_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return response.data[0]

@app.delete("/content-types/{content_type_id}", tags=["content_types"])
def delete_content_type(content_type_id: UUID, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("content_types").delete().eq("content_type_id", content_type_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="ContentType not found")
    return {"message": "ContentType deleted"}

@app.get("/content-types/", response_model=List[ContentType], tags=["content_types"])
def filter_content_types(name: Optional[str] = None, skip: int = 0, limit: int = 10, user: dict = Depends(get_current_user_profile)):
    query = supabase.table("content_types").select("*").range(skip, skip + limit - 1)
    if name:
        query = query.ilike("name", f"%{name}%")
    response = query.execute()
    return response.data

# Update content endpoints to use profile_id
@app.post("/content/", response_model=Content, tags=["content"])
def create_content(content: ContentCreate, profile: dict = Depends(get_current_user_profile)):
    content_data = content.dict()
    content_data['profile_id'] = profile['id']  # Use profile_id instead of user_id
    response = supabase.table("content").insert(content_data).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create content")
    return response.data[0]

@app.get("/content/", tags=["content"])
def filter_content(content_type_id: Optional[UUID] = None, status: Optional[str] = None, search_text: Optional[str] = None, skip: int = 0, limit: int = 10, profile: dict = Depends(get_current_user_profile)):
    query = supabase.table("content").select("*").eq('profile_id', profile['id']).range(skip, skip + limit - 1)

    if content_type_id:
        query = query.eq("content_type_id", content_type_id) 
    if status:
        query = query.eq("status", status)
    if search_text:
        query = query.or_(f"title.ilike.%{search_text}%,body.ilike.%{search_text}%")
    response = query.execute()
    return response.data

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
    try:
        
        #generate thread_id
        thread_id = payload.thread_id or str(uuid.uuid4())
        # Check generation limit        
        limit_response = await check_generation_limit(user['id'])
        if limit_response['generations_used'] >= limit_response['max_generations']:
            raise HTTPException(status_code=403, detail="Generation limit reached for this thread")

        # Proceed with generation
        result = workflow.run_generic_workflow(payload.dict(),thread_id, user)

        # Increment generation count
        await increment_generation_count(user['id'])

        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def check_generation_limit(profile_id: UUID) -> Dict:
    """Check the generation limit for a specific thread."""
    # Get user tier
    profile = supabase.table("profiles").select("role").eq("id", profile_id).single().execute()
    if not profile.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    tier = profile.data['role']

    # Get generation limit for the tier
    limit_query = supabase.table("generation_limits").select("max_generations").eq("tier", tier).single().execute()
    if not limit_query.data:
        raise HTTPException(status_code=404, detail="Generation limit not found for this tier")

    max_generations = limit_query.data['max_generations']

    # Get current generations used
    generations_query = supabase.table("user_generations").select("generations_used").eq("profile_id", profile_id).execute()
    
    # If no entry exists, create one with generations_used = 0
    if not generations_query.data:
        supabase.table("user_generations").insert({
            "profile_id": profile_id,
            "generations_used": 0
        }).execute()
        generations_used = 0
    else:
        generations_used = generations_query.data[0]['generations_used']

    return {
        "tier": tier,
        "max_generations": max_generations,
        "generations_used": generations_used
    }

async def increment_generation_count(profile_id: UUID):
    """Increment the generation count for a user."""
    try:
        # Fetch the current generation count
        response = supabase.table("user_generations").select("generations_used").eq("profile_id", profile_id).execute()
        
        if response.data:
            # Increment the count
            current_count = response.data[0]["generations_used"]
            new_count = current_count + 1
        else:
            # If no record exists, start with 1
            new_count = 1

        # Update the generations_used field
        supabase.table("user_generations").update({
            "generations_used": new_count
        }).eq("profile_id", profile_id).execute()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to increment generation count: {str(e)}")
    
# Update content endpoints to use profile_id
@app.get("/content/list", response_model=ContentListResponse)
async def list_content(skip: int = 0, limit: int = 10, profile: dict = Depends(get_current_user_profile)):
    query = (
    supabase.table("content")
    .select(
        "*, content_types:content_type_id(content_type_id, name), content_tags(tag_id, tags:tag_id(name)), content_sources(content_source_id, sources:source_id(source_id, source_types(name), url_references(url_reference_id, url, type, domain), media(media_id, media_url, media_type)))"
    )
    .eq('profile_id', profile['id'])  # Filter by profile_id instead of user_id
    .order('created_at', desc=True)
    .range(skip, skip + limit)
)

    response = query.execute()

    # Parse the response
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
                "type": ref["type"],
                "domain": ref["domain"]
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
        for item in response.data
    ]

    return ContentListResponse(
        items=items,
        total=response.count if response.count else len(items),
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
    # Base query with updated select to properly get source_identifier
    query = supabase.table("content").select("*, content_types:content_type_id(content_type_id, name), content_tags(tag_id, tags:tag_id(name)), content_sources!inner(content_source_id, source:source_id(source_id, source_identifier, source_types(name), url_references(*), media(*)))"
                                             ).order('created_at', desc=True)
    query = query.eq('profile_id', user['id'])  # Filter by profile_id instead of user_id
    # Apply filters
    if title_contains:
        query = query.ilike("title", f"\"%{title_contains}%\"")  # Case-insensitive title search
    if post_type:
        query = query.eq("content_types.name", post_type)
    if status:
        query = query.eq("status", status)
    if domain:
        query = query.ilike("content_sources.source.url_references.domain", f"\"%{domain}%\"")
    if tag_name:
        query = query.contains("content_tags.tags.name", [tag_name])
    if source_type:
        query = query.eq("content_sources.source.source_types.name", source_type)
    if created_after:
        query = query.gte("created_at", created_after.isoformat())
    if created_before:
        query = query.lte("created_at", created_before.isoformat())
    if updated_after:
        query = query.gte("updated_at", updated_after.isoformat())
    if updated_before:
        query = query.lte("updated_at", updated_before.isoformat())
    if media_type:
        query = query.eq("content_sources.source.media.media_type", media_type)
    if url_type:
        query = query.eq("content_sources.source.url_references.type", url_type)

    query=query.range(skip, skip + limit)

    response = query.execute()

    # Add null checks when parsing response
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
        for item in response.data
    ]

    return ContentListResponse(
        items=items,
        total=response.count if response.count else len(items),
        page=skip // limit + 1,
        size=limit
    )

@app.get("/content/{content_id}", response_model=Content, tags=["content"])
def read_content(content_id: UUID, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("content").select("*").eq("content_id", content_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return response.data[0]

@app.put("/content/{content_id}", response_model=Content, tags=["content"]) 
def update_content(content_id: UUID, content: ContentUpdate, profile: dict = Depends(get_current_user_profile)):
    # Add profile_id filter to ensure user can only update their own content
    response = supabase.table("content").update(content.dict()).eq("content_id", content_id).eq("profile_id", profile["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return response.data[0]

@app.delete("/content/{content_id}", tags=["content"])
def delete_content(content_id: UUID, profile: dict = Depends(get_current_user_profile)):
    # Perform soft delete by updating deleted_at and is_deleted fields
    # Add profile_id filter to ensure user can only delete their own content
    response = supabase.table("content").update({
        "deleted_at": datetime.now().isoformat(),
        "is_deleted": True
    }).eq("content_id", content_id).eq("profile_id", profile["id"]).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted"}

@app.put("/content/thread/{thread_id}/save", tags=["content"])
async def save_thread_content(thread_id: UUID, payload: SaveContentRequest, user: dict = Depends(get_current_user_profile)):
    """Save all content types for a thread in a single transaction"""
    try:
        # Get all content records for this thread
        content_types = supabase.table("content_types").select("*").in_("name", ["blog", "twitter", "linkedin"]).execute()
        content_type_map = {ct["name"]: ct["content_type_id"] for ct in content_types.data}
        

        thread_content = supabase.table("content").select("*").eq("thread_id", thread_id).eq("profile_id", user["id"]).execute()
        content_by_type = {item["content_type_id"]: item for item in thread_content.data}
        
        # Update blog content
        if payload.content:
            blog_content = content_by_type.get(content_type_map["blog"])
            if blog_content:
                supabase.table("content").update({
                    "title": payload.title,
                    "body": payload.content,
                    "status": payload.status
                }).eq("content_id", blog_content["content_id"]).execute()

        # Update Twitter post
        if payload.twitter_post:
            twitter_content = content_by_type.get(content_type_map["twitter"])
            if twitter_content:
                supabase.table("content").update({
                    "body": payload.twitter_post,
                    "status": payload.status
                }).eq("content_id", twitter_content["content_id"]).execute()

        # Update LinkedIn post
        if payload.linkedin_post:
            linkedin_content = content_by_type.get(content_type_map["linkedin"])
            if linkedin_content:
                supabase.table("content").update({
                    "body": payload.linkedin_post,
                    "status": payload.status
                }).eq("content_id", linkedin_content["content_id"]).execute()

        
        return {"message": "Content saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/content/thread/{thread_id}/schedule", tags=["content"])
async def schedule_thread_content(thread_id: UUID, payload: ScheduleContentRequest):
    """Schedule content for publishing"""
    try:
        async with supabase.pool.acquire() as connection:
            async with connection.transaction():
                # Get content type for the platform
                content_type = await supabase.table("content_types").select("*").eq("name", f"{payload.platform}_post").execute()
                
                if not content_type.data:
                    raise HTTPException(status_code=400, detail=f"Invalid platform: {payload.platform}")

                # Update the specific content type for this thread
                response = await supabase.table("content").update({
                    "status": payload.status,
                    "scheduled_at": payload.schedule_date
                }).eq("thread_id", thread_id).eq("content_type_id", content_type.data[0]["content_type_id"]).execute()

                return {"message": "Content scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update sources endpoints to use profile_id
@app.post("/sources/", response_model=Source, tags=["sources"])
def create_source(source: SourceCreate, profile: dict = Depends(get_current_user_profile)):
    source_data = source.dict()
    source_data['profile_id'] = profile['id']  # Use profile_id
    response = supabase.table("sources").insert(source_data).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create source")
    return response.data[0]

@app.get("/sources/{source_id}", response_model=Source, tags=["sources"])
def read_source(source_id: UUID, user: dict = Depends(get_current_user_profile)):
    response = supabase.table("sources").select("*").eq("source_id", source_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Source not found")
    return response.data[0]

@app.put("/sources/{source_id}", response_model=Source, tags=["sources"])
def update_source(source_id: UUID, source: SourceUpdate, profile: dict = Depends(get_current_user_profile)):
    # Add profile_id filter to ensure user can only update their own sources
    response = supabase.table("sources").update(source.dict()).eq("source_id", source_id).eq("profile_id", profile["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Source not found")
    return response.data[0]

@app.delete("/sources/{source_id}", tags=["sources"])
def delete_source(source_id: UUID, profile: dict = Depends(get_current_user_profile)):
    # Perform soft delete by updating deleted_at and is_deleted fields
    # Add profile_id filter to ensure user can only delete their own sources
    response = supabase.table("sources").update({
        "deleted_at": datetime.now().isoformat(),
        "is_deleted": True
    }).eq("source_id", source_id).eq("profile_id", profile["id"]).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted"}


# Update sources endpoints to use profile_id
@app.get("/sources/", response_model=SourceListResponse, tags=["sources"])
def filter_sources(
    type: Optional[str] = None, 
    source_identifier: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10, 
    profile: dict = Depends(get_current_user_profile)
):
    # Build base query with blog content information and url references
    base_query = (
        supabase.table("sources")
        .select("*,source_types(source_type_id,name),content_sources(content:content_id(content_id,title,thread_id,content_types(name))),url_references(*)")
        .eq('profile_id', profile['id'])  # Filter by profile_id instead of user_id
        .order("created_at", desc=True)
    )
    
    # Apply filters
    if type:
        source_type_query = supabase.table("source_types").select("source_type_id").eq("name", type).execute()
        if source_type_query.data:
            source_type_id = source_type_query.data[0]["source_type_id"]
            base_query = base_query.eq("source_type_id", source_type_id)
        else:
            return SourceListResponse(
                items=[],
                total=0,
                page=1,
                size=limit
            )
        
    if source_identifier:
        base_query = base_query.ilike("source_identifier", f"%{source_identifier}%")
    
    # Get total count and paginated data
    count_response = base_query.execute()
    total_count = len(count_response.data)
    paginated_response = base_query.range(skip, skip + limit - 1).execute()
    
    # Transform the response to include blog information and has_url
    transformed_data = []
    for item in paginated_response.data:
        source_type_name = item["source_types"]["name"] if item.get("source_types") else None
        
        # Check if blog content exists and get thread_id
        has_blog = False
        thread_id = None
        for content in item.get("content_sources", []):
            if content.get("content") and content["content"].get("content_types", {}).get("name") == "blog":
                has_blog = True
                thread_id = content["content"].get("thread_id")
                break

        # Check if source has any URL references
        has_url = bool(item.get("url_references") and len(item["url_references"]) > 0)

        transformed_item = {
            **item,
            "source_type": source_type_name,
            "has_blog": has_blog,
            "has_url": has_url,
            "thread_id": thread_id
        }
        del transformed_item["source_types"]
        del transformed_item["content_sources"]
        del transformed_item["url_references"]
        
        transformed_data.append(transformed_item)
        
    return SourceListResponse(
        items=transformed_data,
        total=total_count,
        page=skip // limit + 1,
        size=limit
    )

@app.get("/content/thread/{thread_id}", response_model=ContentListItem, tags=["content"])
async def get_content_by_thread(
    thread_id: UUID, 
    post_type: Optional[str] = Query(None, description="Filter by post type (blog, twitter, linkedin)"),
    user: dict = Depends(get_current_user_profile)
):
    # Map incoming post types to database post types
    post_type_map = {
        'twitter': 'twitter',
        'linkedin': 'linkedin',
        'blog': 'blog'
    }
    
    mapped_post_type = post_type_map.get(post_type) if post_type else None
    
    # First, get the content type ID if post_type is provided
    content_type_id = None
    if mapped_post_type:
        content_type_query = supabase.table("content_types").select("content_type_id").eq("name", mapped_post_type).execute()
        if content_type_query.data:
            content_type_id = content_type_query.data[0]["content_type_id"]

    # Build the main query with proper joins and profile_id filter
    query = (
    supabase.table("content")
    .select(
        "*, content_type:content_type_id(*), content_sources!content_id(source:source_id(source_type:source_type_id(*), url_references(*), media(*))), content_tags!content_id(tag:tag_id(*))"
        )
        .eq("thread_id", thread_id)
        .eq("profile_id", user["id"])  # Add profile_id filter
    )

    if content_type_id:
        query = query.eq("content_type_id", content_type_id)

    response = query.execute()

    if not response.data:
        # Return empty response
        return ContentListItem(
            id="",
            thread_id=str(thread_id),
            title="",
            content="",
            tags=[],
            createdAt="",
            updatedAt="",
            status="",
            twitter_post="",
            linkedin_post="",
            urls=[],
            media=[],
            source_type=None
        )

    # Get the first matching item
    item = response.data[0]
    content_type = item["content_type"]["name"] if item.get("content_type") else None

    content_item = ContentListItem(
        id=item["content_id"],
        thread_id=str(thread_id),  # Convert UUID to string
        title=item.get("title", "") if content_type == "blog" else "",
        content=item.get("body", "") if content_type == post_type else "",
        tags=[tag["tag"]["name"] for tag in item.get("content_tags", []) if tag.get("tag")],
        createdAt=item["created_at"],
        updatedAt=item["updated_at"],
        status=item["status"],
        twitter_post=item.get("body", "") if content_type == "twitter_post" else "",
        linkedin_post=item.get("body", "") if content_type == "linkedin_post" else "",
        urls=[{
            "url": ref["url"],
            "type": ref.get("type"),
            "domain": ref.get("domain")
        } for source in item.get("content_sources", [])
            if source.get("source") and source["source"].get("url_references")
            for ref in source["source"]["url_references"]],
        media=[{
            "url": media["media_url"],
            "type": media["media_type"]
        } for source in item.get("content_sources", [])
            if source.get("source") and source["source"].get("media")
            for media in source["source"]["media"]],
        source_type=next((source["source"]["source_type"]["name"]
            for source in item.get("content_sources", [])
            if source.get("source") and source["source"].get("source_type")), None)
    )

    return content_item


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

