"""
Health check endpoints for monitoring and Kubernetes probes.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import psycopg
from src.backend.settings import get_settings
from src.backend.auth import get_auth_provider

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    
    Use for: Kubernetes liveness probe
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "postbot-backend"
    }


@router.get("/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Comprehensive readiness check.
    Verifies all dependencies are available:
    - Database connectivity
    - Auth provider configuration
    
    Use for: Kubernetes readiness probe
    Returns 503 if any dependency fails.
    """
    settings = get_settings()
    checks = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "postbot-backend",
        "checks": {}
    }
    
    all_healthy = True
    
    # Check 1: Database connectivity
    try:
        conn = psycopg.connect(settings.database_url, connect_timeout=3)
        conn.execute("SELECT 1")
        conn.close()
        checks["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        all_healthy = False
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # Check 2: Auth provider configuration
    try:
        auth_provider = get_auth_provider()
        provider_name = auth_provider.get_provider_name()
        checks["checks"]["auth_provider"] = {
            "status": "healthy",
            "message": f"Auth provider configured: {provider_name}",
            "provider": provider_name
        }
    except Exception as e:
        all_healthy = False
        checks["checks"]["auth_provider"] = {
            "status": "unhealthy",
            "message": f"Auth provider configuration failed: {str(e)}"
        }
    
    # Check 3: Environment configuration
    try:
        # Verify critical settings are present
        critical_vars = ["DATABASE_URL", "AUTH_PROVIDER"]
        missing_vars = [var for var in critical_vars if not getattr(settings, var.lower(), None)]
        
        if missing_vars:
            raise ValueError(f"Missing critical environment variables: {', '.join(missing_vars)}")
        
        checks["checks"]["configuration"] = {
            "status": "healthy",
            "message": "All critical environment variables configured",
            "environment": settings.environment,
            "auth_provider": settings.auth_provider
        }
    except Exception as e:
        all_healthy = False
        checks["checks"]["configuration"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Set overall status
    checks["status"] = "ready" if all_healthy else "not_ready"
    
    # Return 503 if not ready (tells Kubernetes to not route traffic)
    if not all_healthy:
        raise HTTPException(status_code=503, detail=checks)
    
    return checks


@router.get("/startup")
async def startup_check() -> Dict[str, Any]:
    """
    Startup probe to ensure application has fully initialized.
    More lenient than readiness - just checks if service is responsive.
    
    Use for: Kubernetes startup probe (for slow-starting containers)
    """
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "postbot-backend"
    }
