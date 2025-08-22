"""Main FastAPI application entry point."""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .config import settings


def setup_logging() -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger = structlog.get_logger()
    
    logger.info(
        "Starting Linear Claude Agent",
        version=settings.app_version,
        environment=settings.environment,
    )
    
    # Initialize database connection
    # TODO: Initialize database connection pool
    
    # Initialize Redis connection
    # TODO: Initialize Redis connection
    
    # Initialize services
    # TODO: Initialize Linear API client
    # TODO: Initialize Claude Code runner
    # TODO: Initialize Git worktree manager
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down Linear Claude Agent")
    
    # Cleanup resources
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cleanup active sessions
    
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    setup_logging()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Modern Python Linear Agent with FastAPI and Claude Code integration",
        debug=settings.debug,
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json" if settings.debug else None,
        docs_url=f"{settings.api_prefix}/docs" if settings.debug else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.debug else None,
    )
    
    # Add security middleware
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure properly in production
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routes
    # TODO: Include API routers
    # app.include_router(webhooks.router, prefix=f"{settings.api_prefix}/webhooks")
    # app.include_router(agents.router, prefix=f"{settings.api_prefix}/agents")
    # app.include_router(health.router, prefix=f"{settings.api_prefix}/health")
    
    # Add basic health check
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }
    
    return app


# Create the application instance
app = create_app()


def main() -> None:
    """Main entry point for running the application."""
    uvicorn.run(
        "linear_agent.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_config=None,  # We handle logging ourselves
        access_log=False,  # Disable uvicorn access logs
    )


if __name__ == "__main__":
    main()