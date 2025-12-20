"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app
import logging
import os

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

# Serve frontend static files (eliminates CORS issues - same origin)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    logger.info(f"Frontend static files mounted from: {frontend_path}")

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
    """Root endpoint - redirects to frontend."""
    # Detect environment and construct URLs
    codespace_name = os.getenv("CODESPACE_NAME")
    domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    
    if codespace_name:
        # CodeSpace environment
        base_url = f"https://{codespace_name}-8000.{domain}"
    else:
        # Local development
        base_url = f"http://localhost:{settings.api_port}"
    
    return {
        "message": "MarketML Persona Builder API",
        "version": "0.1.0",
        "environment": settings.app_env,
        "urls": {
            "frontend": f"{base_url}/static/index.html",
            "api_docs": f"{base_url}{settings.api_v1_prefix}/docs",
            "health": f"{base_url}/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_debug
    )
