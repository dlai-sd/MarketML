"""
Persona generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging

from app.core.database import get_db, Persona, JobStatus
from app.core.schemas import PersonaGenerationRequest, PersonaResponse, JobStatusResponse
from app.tasks.persona_generation import generate_persona_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=JobStatusResponse, status_code=202)
async def generate_persona(
    request: PersonaGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a persona asynchronously.
    Returns job ID to track progress.
    """
    # Generate IDs
    person_id = request.person_id or str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    
    # Create job status record
    job = JobStatus(
        job_id=job_id,
        person_id=person_id,
        status="pending",
        progress=0,
        current_step="Queued for processing"
    )
    db.add(job)
    await db.commit()
    
    # Queue the persona generation task
    generate_persona_task.delay(
        job_id=job_id,
        person_id=person_id,
        name=request.name,
        location=request.location,
        description=request.description,
        confirmed_profiles=request.confirmed_profiles
    )
    
    logger.info(f"Queued persona generation for {request.name}, job_id={job_id}")
    
    return JobStatusResponse(
        job_id=job_id,
        status="pending",
        progress=0,
        current_step="Queued for processing",
        created_at=job.created_at
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a generated persona by ID."""
    result = await db.execute(
        select(Persona).where(Persona.persona_id == persona_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    return PersonaResponse(
        persona_id=persona.persona_id,
        version=persona.version,
        generated_at=persona.created_at,
        confidence_score=persona.confidence_score or 0.0,
        structured=persona.structured_data["structured"],
        narrative=persona.narrative,
        short_narrative=persona.short_narrative or "",
        marketing_insights=persona.structured_data.get("marketing_insights", []),
        recommended_actions=persona.structured_data.get("recommended_actions", []),
        generation_time_ms=persona.generation_time_ms,
        quality_issues=persona.quality_issues
    )


@router.get("/by-person/{person_id}", response_model=list[PersonaResponse])
async def get_personas_by_person(
    person_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all personas for a person."""
    result = await db.execute(
        select(Persona)
        .where(Persona.person_id == person_id)
        .order_by(Persona.created_at.desc())
    )
    personas = result.scalars().all()
    
    return [
        PersonaResponse(
            persona_id=p.persona_id,
            version=p.version,
            generated_at=p.created_at,
            confidence_score=p.confidence_score or 0.0,
            structured=p.structured_data["structured"],
            narrative=p.narrative,
            short_narrative=p.short_narrative or "",
            marketing_insights=p.structured_data.get("marketing_insights", []),
            recommended_actions=p.structured_data.get("recommended_actions", []),
            generation_time_ms=p.generation_time_ms,
            quality_issues=p.quality_issues
        )
        for p in personas
    ]
