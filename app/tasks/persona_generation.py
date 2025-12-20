"""
Celery task for persona generation.
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, List
import logging
import time

from app.tasks import celery_app
from app.core.database import AsyncSessionLocal, Persona, JobStatus, ScrapedData
from app.scrapers.orchestrator import ScraperOrchestrator
from app.extractors.entity_extractor import EntityExtractor
from app.enrichment.enrichment_engine import EnrichmentEngine
from app.features.feature_engineer import FeatureEngineer
from app.scoring.ensemble_scorer import EnsembleScorer
from app.generation.persona_generator import PersonaGenerator
from app.validation.quality_validator import QualityValidator
from app.utils.performance import timer, monitor

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="generate_persona")
def generate_persona_task(
    self,
    job_id: str,
    person_id: str,
    name: str,
    location: str,
    description: Optional[str] = None,
    confirmed_profiles: Optional[List[Dict]] = None
):
    """
    Celery task to generate persona asynchronously.
    This runs the entire pipeline: scrape → extract → enrich → score → generate → validate
    """
    start_time = time.time()
    
    try:
        # Run async code in event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            _generate_persona_async(
                self, job_id, person_id, name, location, description, confirmed_profiles
            )
        )
        
        generation_time = int((time.time() - start_time) * 1000)
        logger.info(f"Persona generated successfully for {name} in {generation_time}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating persona: {str(e)}", exc_info=True)
        
        # Update job status to failed
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            _update_job_status(job_id, "failed", 100, f"Error: {str(e)}")
        )
        
        raise


async def _generate_persona_async(
    task,
    job_id: str,
    person_id: str,
    name: str,
    location: str,
    description: Optional[str],
    confirmed_profiles: Optional[List[Dict]]
):
    """Async persona generation pipeline."""
    
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Update job status - Starting
            await _update_job_status(job_id, "processing", 5, "Initializing scrapers...")
            
            # Step 2: Scrape data from multiple sources
            await _update_job_status(job_id, "processing", 10, "Scraping LinkedIn...")
            orchestrator = ScraperOrchestrator()
            scraped_data = await orchestrator.scrape_all_sources(
                name=name,
                location=location,
                confirmed_profiles=confirmed_profiles,
                person_id=person_id,
                db=db
            )
            
            # Step 3: Extract entities
            await _update_job_status(job_id, "processing", 40, "Extracting entities...")
            extractor = EntityExtractor()
            entities = await extractor.extract_from_scraped_data(scraped_data)
            
            # Step 4: Enrich with context
            await _update_job_status(job_id, "processing", 55, "Building context...")
            enrichment_engine = EnrichmentEngine()
            enriched_data = await enrichment_engine.enrich(entities, location)
            
            # Step 5: Feature engineering
            await _update_job_status(job_id, "processing", 65, "Computing features...")
            feature_engineer = FeatureEngineer()
            features = feature_engineer.compute_features(enriched_data)
            
            # Step 6: Score with ML models
            await _update_job_status(job_id, "processing", 75, "Scoring persona...")
            scorer = EnsembleScorer()
            scores = scorer.predict(features)
            
            # Step 7: Generate persona narrative
            await _update_job_status(job_id, "processing", 85, "Generating persona...")
            generator = PersonaGenerator()
            persona_data = await generator.generate(
                enriched_data=enriched_data,
                scores=scores,
                name=name
            )
            
            # Step 8: Validate quality
            await _update_job_status(job_id, "processing", 92, "Validating quality...")
            validator = QualityValidator()
            is_valid, quality_issues = validator.validate(persona_data)
            
            # Step 9: Save persona to database
            await _update_job_status(job_id, "processing", 95, "Saving persona...")
            persona = Persona(
                person_id=person_id,
                structured_data=persona_data,
                narrative=persona_data["narrative"],
                short_narrative=persona_data["short_narrative"],
                confidence_score=persona_data["confidence_score"],
                quality_issues=quality_issues,
                generation_time_ms=int(time.time() * 1000)
            )
            db.add(persona)
            await db.commit()
            await db.refresh(persona)
            
            # Step 10: Complete job
            await _update_job_status(
                job_id, "completed", 100, "Persona generated successfully",
                persona_id=persona.persona_id
            )
            
            logger.info(f"Persona {persona.persona_id} saved for {name}")
            
            return {
                "persona_id": persona.persona_id,
                "confidence_score": persona.confidence_score,
                "quality_issues": quality_issues
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            raise


async def _update_job_status(
    job_id: str,
    status: str,
    progress: int,
    current_step: str,
    persona_id: Optional[str] = None
):
    """Update job status in database."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        result = await db.execute(
            select(JobStatus).where(JobStatus.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            job.status = status
            job.progress = progress
            job.current_step = current_step
            
            if status == "processing" and not job.started_at:
                job.started_at = datetime.utcnow()
            
            if status in ["completed", "failed"]:
                job.completed_at = datetime.utcnow()
            
            if persona_id:
                job.persona_id = persona_id
            
            await db.commit()
