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
from dependencies import get_current_user_profile

from routers import content, profiles, content_types, sources, templates, parameters, reddit
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
        "User-Agent"
    ],
    max_age=600  # Move max_age here as middleware parameter
)

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
auth_repository = AuthRepository()

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

if __name__ == "__main__":
    uvicorn.run("src.backend.api.api:app", host="0.0.0.0", port=8000, reload=False)

