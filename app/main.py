"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging

from app.config import settings
from app.api.v1 import api_router
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.app_log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting MarketML application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # TODO: Load ML models
    logger.info("ML models loaded")
    
    # TODO: Initialize vector database
    logger.info("Vector database initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down MarketML application...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version="0.1.0",
    description="AI-Powered Marketing Persona Builder",
    lifespan=lifespan,
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Prometheus metrics endpoint
if settings.enable_monitoring:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.app_env
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MarketML Persona Builder API",
        "version": "0.1.0",
        "docs": f"{settings.api_v1_prefix}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_debug
    )
