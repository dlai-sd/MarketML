"""
API v1 routes.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import personas, feedback, jobs

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
