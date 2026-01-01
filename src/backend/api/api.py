import os
from fastapi import FastAPI, HTTPException, Depends, Query, Security, Body, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.backend.db.connection import DatabaseConnectionManager, session_context
from src.backend.api.datamodel import *
from src.backend.settings import get_settings
from src.backend.exceptions import ConfigurationException
import uvicorn
from src.backend.agents.blogs import AgentWorkflow
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from src.backend.utils.logger import setup_logger
from src.backend.db.repositories import AuthRepository
from cachetools import TTLCache

from src.backend.api.routers import content, profiles, content_types, sources, templates, parameters, reddit, health
from src.backend.api.middleware import register_exception_handlers, request_logging_middleware

# Setup logger
logger = setup_logger(__name__)

# Validate environment and load settings
try:
    settings = get_settings()
    logger.info(f"Application starting in {settings.environment} mode")
except ConfigurationException as e:
    logger.error(f"Configuration error: {e}")
    raise

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Auth cache to store token-to-user mappings with a TTL (Time To Live)
auth_cache = TTLCache(maxsize=settings.auth_cache_size, ttl=settings.auth_cache_ttl)

db_manager = DatabaseConnectionManager()
security = HTTPBearer()

app = FastAPI(
    title="PostBot API",
    version="1.0.0",
    description="AI-powered content generation and management platform"
)

# Register exception handlers for consistent error responses
register_exception_handlers(app)

# Add request logging middleware
app.middleware("http")(request_logging_middleware)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health.router)  # Health checks (no prefix for standard endpoints)
app.include_router(content.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(content_types.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(parameters.router, prefix="/api")
app.include_router(reddit.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
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

# Legacy health endpoint kept for backwards compatibility
# Use /readiness for proper dependency checks
@app.get("/")
async def root():
    """Root endpoint - redirects to /health"""
    return {"message": "PostBot API", "version": "1.0.0", "health_endpoint": "/health"}

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database session per request"""
    session = None
    try:
        session = db_manager.get_session()
        # Set up a place to cache auth results
        
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

# Initialize repositories
auth_repository = AuthRepository()

@app.post("/auth/signup", tags=["auth"])
@limiter.limit("5/minute")
async def sign_up(request: Request, email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_up(email, password)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", tags=["auth"])
@limiter.limit("10/minute")
async def sign_in(request: Request, response: Response, email: str = Body(...), password: str = Body(...)):
    try:
        result = await auth_repository.sign_in(email, password)
        
        # Set refresh token in HTTP-only cookie
        if result.get('refresh_token'):
            domain = None  # Let the browser set the appropriate domain
            if settings.frontend_url:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(settings.frontend_url)
                    if parsed_url.hostname not in ('localhost', '127.0.0.1'):
                        domain = '.' + parsed_url.hostname  # Include subdomain support
                except:
                    pass
                    
            response.set_cookie(
                key="refresh_token",
                value=result['refresh_token'],
                httponly=True,
                secure=True,
                samesite='lax',
                domain=domain,
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
        if settings.frontend_url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(settings.frontend_url)
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

