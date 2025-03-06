import os
from fastapi import FastAPI, HTTPException, Depends, Query, Security, Body, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.backend.db.connection import DatabaseConnectionManager, session_context
from src.backend.api.datamodel import *
import uvicorn
from src.backend.agents.blogs import AgentWorkflow
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from src.backend.utils.logger import setup_logger
from src.backend.db.repositories import AuthRepository
from cachetools import TTLCache

from src.backend.api.routers import content, profiles, content_types, sources, templates, parameters, reddit
# Auth cache to store token-to-user mappings with a TTL (Time To Live)
# Cache size of 100 users, and tokens expire after 5 minutes
auth_cache = TTLCache(maxsize=100, ttl=6000)  # 6000 seconds = 100 minutes

# Get settings from environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")
db_manager = DatabaseConnectionManager()
security = HTTPBearer()

app = FastAPI()
app.include_router(content.router)
app.include_router(profiles.router)
app.include_router(content_types.router)
app.include_router(sources.router)
app.include_router(templates.router)
app.include_router(parameters.router)
app.include_router(reddit.router)

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
        "User-Agent",
        "Set-Cookie",
        "Cookie"
    ],
    expose_headers=["Set-Cookie"],
    max_age=600
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database session per request"""
    session = None
    try:
        session = db_manager.get_session()
        # Set up a place to cache auth results
        request.state.auth_cache = {}
        
        # Handle token refresh if needed
        auth_header = request.headers.get('Authorization')
        refresh_token = request.cookies.get('refresh_token')
        
        if auth_header and refresh_token and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            try:
                await auth_repository.refresh_session(refresh_token)
            except Exception as e:
                logger.warning(f"Session refresh failed: {str(e)}")
        
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
auth_repository = AuthRepository()

@app.post("/auth/signup", tags=["auth"])
async def sign_up(email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_up(email, password)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", tags=["auth"])
async def sign_in(response: Response, email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_in(email, password)
        
        # Set refresh token in HTTP-only cookie
        if result.get('refresh_token'):
            domain = None
            is_secure = True  # Set to True for HTTPS
            
            if FRONTEND_URL:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(FRONTEND_URL)
                    if parsed_url.hostname not in ('localhost', '127.0.0.1'):
                        domain = parsed_url.hostname  # Remove the dot prefix
                        is_secure = parsed_url.scheme == 'https'
                except:
                    pass
                    
            response.set_cookie(
                key="refresh_token",
                value=result['refresh_token'],
                httponly=True,
                secure=is_secure,  # Based on protocol
                samesite='lax',
                domain=domain,
                path='/',  # Ensure cookie is available for all paths
                max_age=3600 * 24 * 30  # 30 days
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signout", tags=["auth"])
async def sign_out(response: Response):
    try:
        result = await auth_repository.sign_out()
        
        auth_cache.clear()
        
        # Calculate domain for cookie removal
        domain = None
        if FRONTEND_URL:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(FRONTEND_URL)
                if parsed_url.hostname not in ('localhost', '127.0.0.1'):
                    domain = '.' + parsed_url.hostname
            except:
                pass
        
        # Clear the refresh token cookie with matching domain
        response.delete_cookie(
            key="refresh_token",
            secure=True,
            httponly=True,
            samesite='lax',
            domain=domain
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.backend.api.api:app", host="0.0.0.0", port=8000, reload=False)

