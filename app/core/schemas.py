"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, validator


# Request Schemas

class PersonaGenerationRequest(BaseModel):
    """Request to generate a persona."""
    
    person_id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=200)
    location: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    confirmed_profiles: Optional[List[Dict[str, str]]] = None
    
    # Generation options
    generation_mode: Optional[str] = Field(default="template", pattern="^(template|gpt-3.5|gpt-4)$")
    data_source: Optional[str] = Field(default="mock", pattern="^(mock|google|playwright)$")
    linkedin_mode: Optional[str] = Field(default="skip", pattern="^(skip|basic|proxycurl)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Yogesh Khandge",
                "location": "Pune, Maharashtra",
                "description": "Entrepreneur in furniture business",
                "generation_mode": "gpt-3.5",
                "data_source": "google",
                "linkedin_mode": "basic",
                "confirmed_profiles": [
                    {"source": "linkedin", "url": "https://linkedin.com/in/..."}
                ]
            }
        }


class FeedbackRequest(BaseModel):
    """User feedback on generated persona."""
    
    persona_id: str
    user_id: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    corrections: Optional[Dict[str, Any]] = None
    comments: Optional[str] = Field(None, max_length=2000)


# Response Schemas

class LocationContext(BaseModel):
    """Geographic context information."""
    
    city: str
    state: Optional[str] = None
    country: str = "India"
    affluence_score: Optional[float] = None
    market_context: Optional[str] = None


class BusinessMetrics(BaseModel):
    """Business-related metrics."""
    
    estimated_revenue: Optional[str] = None
    team_size: Optional[str] = None
    years_in_business: Optional[int] = None
    growth_stage: Optional[str] = None


class DigitalPresence(BaseModel):
    """Digital presence metrics."""
    
    linkedin_followers: Optional[int] = None
    website_quality: Optional[str] = None
    social_activity: Optional[str] = None


class PersonaScores(BaseModel):
    """Calculated persona scores."""
    
    maturity: float = Field(..., ge=0, le=100)
    marketing_readiness: float = Field(..., ge=0, le=100)
    budget_capacity: float = Field(..., ge=0, le=100)
    recommended_tier: int = Field(..., ge=1, le=4)


class StructuredPersona(BaseModel):
    """Structured persona data."""
    
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    location: LocationContext
    business_metrics: Optional[BusinessMetrics] = None
    digital_presence: Optional[DigitalPresence] = None
    scores: PersonaScores


class PersonaResponse(BaseModel):
    """Complete persona response."""
    
    persona_id: str
    version: int = 1
    generated_at: datetime
    confidence_score: float = Field(..., ge=0, le=1)
    
    structured: StructuredPersona
    narrative: str = Field(..., min_length=50)
    short_narrative: str = Field(..., max_length=500)
    
    marketing_insights: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    
    generation_time_ms: Optional[int] = None
    quality_issues: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "uuid-here",
                "version": 1,
                "generated_at": "2025-12-20T10:00:00Z",
                "confidence_score": 0.87,
                "structured": {
                    "name": "Yogesh Khandge",
                    "title": "Founder",
                    "company": "Noya Furniture",
                    "industry": "Furniture Manufacturing",
                    "location": {
                        "city": "Pune",
                        "state": "Maharashtra",
                        "affluence_score": 7.2
                    },
                    "scores": {
                        "maturity": 65,
                        "marketing_readiness": 72,
                        "budget_capacity": 58,
                        "recommended_tier": 2
                    }
                },
                "narrative": "Full narrative here...",
                "short_narrative": "Furniture entrepreneur in Pune, scaling business with digital marketing focus",
                "marketing_insights": [
                    "Strong local presence indicates opportunity for regional expansion"
                ]
            }
        }


class JobStatusResponse(BaseModel):
    """Async job status response."""
    
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int = Field(..., ge=0, le=100)
    current_step: Optional[str] = None
    persona_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    environment: str
    uptime_seconds: Optional[float] = None
