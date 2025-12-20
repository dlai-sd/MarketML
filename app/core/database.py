"""
Database models and session management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text, create_engine, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
import uuid
import logging

from app.config import settings
from app.constants import DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()


class Persona(Base):
    """Persona model storing generated personas."""
    
    __tablename__ = "personas"
    __table_args__ = (
        Index('idx_persona_person_created', 'person_id', 'created_at'),
        Index('idx_persona_confidence', 'confidence_score'),
    )
    
    persona_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String, nullable=False, index=True)
    version = Column(Integer, default=1)
    
    # Structured data
    structured_data = Column(JSON, nullable=False)
    narrative = Column(Text, nullable=False)
    short_narrative = Column(String(500))  # 15-word summary
    
    # Metadata
    confidence_score = Column(Float, index=True)
    quality_issues = Column(JSON)
    generation_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Persona {self.persona_id}>"


class ScrapedData(Base):
    """Raw scraped data from various sources."""
    
    __tablename__ = "scraped_data"
    
    scrape_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)
    url = Column(Text)
    
    # Content
    html_content = Column(Text)
    extracted_json = Column(JSON)
    
    # Metadata
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    scrape_duration_ms = Column(Integer)
    
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ScrapedData {self.source}:{self.scrape_id}>"


class UserFeedback(Base):
    """User feedback on generated personas."""
    
    __tablename__ = "user_feedback"
    
    feedback_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String, nullable=False, index=True)
    user_id = Column(String, index=True)
    
    # Feedback
    rating = Column(Integer)  # 1-5 stars
    corrections = Column(JSON)  # User-provided corrections
    comments = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<UserFeedback {self.feedback_id}>"


class ModelVersion(Base):
    """Track ML model versions and performance."""
    
    __tablename__ = "model_versions"
    
    version_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_type = Column(String(50), nullable=False)  # xgboost, random_forest, etc.
    model_path = Column(Text, nullable=False)
    
    # Metrics
    metrics = Column(JSON)  # MAE, RMSE, R², etc.
    trained_on = Column(Integer)  # Number of training examples
    
    # Status
    is_active = Column(Boolean, default=False, index=True)
    deployed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ModelVersion {self.model_type}:{self.version_id}>"


class JobStatus(Base):
    """Track async job status for persona generation."""
    
    __tablename__ = "job_status"
    
    job_id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False, index=True)
    
    # Status
    status = Column(String(20), default="pending", index=True)  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(String(100))
    
    # Result
    persona_id = Column(String, index=True)
    error_message = Column(Text)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<JobStatus {self.job_id}:{self.status}>"


# Database initialization
def get_database_url():
    """Get database URL (convert sqlite to sqlite+aiosqlite for async)."""
    if settings.database_url.startswith("sqlite"):
        return settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
    return settings.database_url


# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.app_debug,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database (create tables)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
