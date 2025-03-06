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

# Get settings from environment variables with better default handling
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PRODUCTION_FRONTEND = "https://postbot-frontend.onrender.com"
PRODUCTION_BACKEND = "https://postbot-4977.onrender.com"

ALLOWED_ORIGINS = [
    FRONTEND_URL,
    PRODUCTION_FRONTEND,
    "http://localhost:5173",
    "http://localhost:3000",
]

db_manager = DatabaseConnectionManager()
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware first, before including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept", 
        "Origin",
        "Referer",
        "User-Agent",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Set-Cookie",
        "Cookie"
    ],
    expose_headers=[
        "Set-Cookie",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials"
    ],
    max_age=3600
)

# Include routers after CORS middleware
app.include_router(content.router)
app.include_router(profiles.router)
app.include_router(content_types.router)
app.include_router(sources.router)
app.include_router(templates.router)
app.include_router(parameters.router)
app.include_router(reddit.router)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database session and CORS per request"""
    session = None
    try:
        session = db_manager.get_session()
        request.state.auth_cache = {}
        
        # Get origin from request headers
        origin = request.headers.get("origin")
        
        # Enhanced logging for debugging
        auth_header = request.headers.get('Authorization')
        refresh_token = request.cookies.get('refresh_token')
        
        logger.debug(f"Request path: {request.url.path}")
        logger.debug(f"Origin: {origin}")
        logger.debug(f"Has Authorization header: {bool(auth_header)}")
        logger.debug(f"Has refresh token cookie: {bool(refresh_token)}")
        logger.debug(f"Request cookies: {request.cookies}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        if auth_header and refresh_token and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            try:
                refresh_result = await auth_repository.refresh_session(refresh_token)
                logger.debug(f"Session refresh attempt result: {bool(refresh_result)}")
            except Exception as e:
                logger.error(f"Session refresh failed: {str(e)}")
        
        response = await call_next(request)
        
        # Ensure CORS headers are set for the specific origin if it's allowed
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Set cookie parameters based on environment
        is_production = origin and (origin.startswith("https://") or "render.com" in origin)
        
        if refresh_token:
            domain = None
            if is_production:
                # Extract domain from origin for production
                from urllib.parse import urlparse
                domain = urlparse(origin).hostname
            
            # Update cookie settings if needed
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=is_production,
                samesite='none' if is_production else 'lax',
                domain=domain,
                path='/',
                max_age=3600 * 24 * 30
            )
        
        # Log response cookies for debugging
        logger.debug(f"Response cookies: {response.headers.get('set-cookie', 'None')}")
        
        if session:
            try:
                session.commit()
            except Exception as e:
                logger.error(f"Session commit error: {str(e)}")
                session.rollback()
                raise
        return response
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}")
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
        
        # Enhanced logging for signin process
        logger.debug(f"Sign in attempt for email: {email}")
        logger.debug(f"Sign in result contains refresh token: {bool(result.get('refresh_token'))}")
        
        # Set refresh token in HTTP-only cookie
        if result.get('refresh_token'):
            domain = None
            is_secure = True
            
            if FRONTEND_URL:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(FRONTEND_URL)
                    domain = parsed_url.hostname if parsed_url.hostname not in ('localhost', '127.0.0.1') else None
                    is_secure = parsed_url.scheme == 'https'
                    
                    logger.debug(f"Cookie settings - Domain: {domain}, Secure: {is_secure}")
                except Exception as e:
                    logger.error(f"URL parsing error: {str(e)}")
            
            # Set SameSite attribute based on environment
            samesite_setting = 'none' if is_secure else 'lax'
            
            response.set_cookie(
                key="refresh_token",
                value=result['refresh_token'],
                httponly=True,
                secure=is_secure,
                samesite=samesite_setting,
                domain=domain,
                path='/',
                max_age=3600 * 24 * 30
            )
            
            logger.debug(f"Set refresh token cookie with settings: domain={domain}, secure={is_secure}, samesite={samesite_setting}")
        
        return result
    except Exception as e:
        logger.error(f"Sign in error: {str(e)}")
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

