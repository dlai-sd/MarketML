"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app
import logging
import os
from pathlib import Path

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

# Include API router FIRST (before static files)
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


@app.get("/api")
async def root():
    """Root endpoint - API info."""
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
            "api_docs": f"{base_url}{settings.api_v1_prefix}/docs",
            "health": f"{base_url}/health"
        }
    }

# Mobile subdomain detection and routing
@app.middleware("http")
async def mobile_subdomain_handler(request: Request, call_next):
    """Detect m.subdomain and mobile User-Agent, serve appropriate version."""
    host = request.headers.get("host", "")
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Check if mobile subdomain or mobile User-Agent
    is_mobile_subdomain = host.startswith("m.")
    is_mobile_ua = any(x in user_agent for x in ["mobile", "android", "iphone", "ipad"])
    
    # Store in request state for use in route handlers
    request.state.is_mobile = is_mobile_subdomain or is_mobile_ua
    
    response = await call_next(request)
    return response

# Serve frontend static files LAST (catch-all for root path)
# This eliminates CORS issues - frontend and API on same origin!
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Frontend mounted at root from: {frontend_path}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_debug
    )
