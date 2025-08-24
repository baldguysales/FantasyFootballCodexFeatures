import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as StarletteHTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.append(main_project_path)

from app.core.config import settings
from app.core.database import init_db, close_db_connection, lifespan
from app.routers import auth, users

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize FastAPI app with metadata
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Authentication and User Management API for FF Codex",
        version="1.0.0",
        docs_url=settings.API_DOCS_URL if settings.DEBUG else None,
        redoc_url=settings.API_REDOC_URL if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    add_middleware(app)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Include routers
    include_routers(app)
    
    # Add health check endpoint
    add_health_check(app)
    
    return app

def add_middleware(app: FastAPI) -> None:
    """Add middleware to the FastAPI application."""
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Total-Count"],
    )
    
    # GZip Middleware for compressing responses
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Trusted Host Middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
        
        # Redirect HTTP to HTTPS in production
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Session Middleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie=settings.SESSION_COOKIE_NAME,
        https_only=settings.SESSION_COOKIE_SECURE,
        same_site=settings.SESSION_COOKIE_SAMESITE,
    )

def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"],
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

def include_routers(app: FastAPI) -> None:
    """Include all API routers."""
    # Authentication routes
    app.include_router(
        auth.router,
        prefix="/api/v1/auth",
        tags=["authentication"],
        dependencies=[],
    )
    
    # User management routes
    app.include_router(
        users.router,
        prefix="/api/v1/users",
        tags=["users"],
        dependencies=[],
    )

def add_health_check(app: FastAPI) -> None:
    """Add health check endpoints."""
    
    @app.get("/", include_in_schema=False)
    async def root() -> Dict[str, str]:
        """Root endpoint with welcome message."""
        return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
    
    @app.get("/health", include_in_schema=False)
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}
    
    @app.get("/version", include_in_schema=False)
    async def version() -> Dict[str, str]:
        """API version endpoint."""
        return {"version": "1.0.0"}

# Create the FastAPI application
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
