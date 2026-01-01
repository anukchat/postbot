"""
Centralized error handling middleware for FastAPI.
Provides consistent error responses and logging.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.backend.exceptions import (
    ConfigurationException,
    AuthenticationException,
    DatabaseException
)
from src.backend.utils.logger import setup_logger
import traceback
from typing import Union

logger = setup_logger(__name__)


class ErrorResponse:
    """Standard error response format"""
    
    @staticmethod
    def format_error(
        error_type: str,
        message: str,
        status_code: int,
        details: Union[dict, list, None] = None
    ) -> dict:
        """Format error response in consistent structure"""
        response = {
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        return response


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions (4xx, 5xx errors)
    """
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.format_error(
            error_type="http_error",
            message=exc.detail,
            status_code=exc.status_code
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors (422 Unprocessable Entity)
    Provides detailed field-level error information
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.url.path}: {len(errors)} field(s) invalid",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.format_error(
            error_type="validation_error",
            message="Request validation failed",
            status_code=422,
            details=errors
        )
    )


async def authentication_exception_handler(request: Request, exc: AuthenticationException) -> JSONResponse:
    """
    Handle authentication errors
    """
    logger.warning(
        f"Authentication error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse.format_error(
            error_type="authentication_error",
            message=str(exc),
            status_code=401
        ),
        headers={"WWW-Authenticate": "Bearer"}
    )


async def configuration_exception_handler(request: Request, exc: ConfigurationException) -> JSONResponse:
    """
    Handle configuration errors
    """
    logger.error(
        f"Configuration error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.format_error(
            error_type="configuration_error",
            message="Service configuration error. Please contact support.",
            status_code=500
        )
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """
    Handle database errors
    """
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse.format_error(
            error_type="database_error",
            message="Database temporarily unavailable. Please try again.",
            status_code=503
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unexpected exceptions
    """
    # Log full traceback for debugging
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Don't expose internal error details to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.format_error(
            error_type="internal_error",
            message="An unexpected error occurred. Please try again or contact support.",
            status_code=500
        )
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app
    
    Usage:
        from src.backend.api.middleware.error_handler import register_exception_handlers
        register_exception_handlers(app)
    """
    from fastapi import FastAPI
    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(ConfigurationException, configuration_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")
