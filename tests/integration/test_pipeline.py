"""Integration tests for full persona generation pipeline."""

import pytest
import asyncio
from app.scrapers.orchestrator import ScraperOrchestrator
from app.extractors.entity_extractor import EntityExtractor
from app.enrichment.enrichment_engine import EnrichmentEngine
from app.features.feature_engineer import FeatureEngineer
from app.scoring.ensemble_scorer import EnsembleScorer
from app.generation.persona_generator import PersonaGenerator
from app.validation.quality_validator import QualityValidator


@pytest.fixture
def pipeline_components():
    """Initialize all pipeline components."""
    return {
        "orchestrator": ScraperOrchestrator(),
        "extractor": EntityExtractor(),
        "enrichment": EnrichmentEngine(),
        "features": FeatureEngineer(),
        "scorer": EnsembleScorer(),
        "generator": PersonaGenerator(),
        "validator": QualityValidator()
    }


@pytest.mark.asyncio
async def test_full_pipeline(pipeline_components):
    """Test complete pipeline from scraping to validation."""
    
    # Input data
    name = "Yogesh Khandge"
    location = "Pune, Maharashtra"
    description = "Digital marketing expert"
    
    # Step 1: Scraping
    scraped = await pipeline_components["orchestrator"].scrape_all_sources(
        name=name,
        location=location,
        description=description
    )
    assert scraped is not None
    
    # Step 2: Extraction
    entities = pipeline_components["extractor"].extract_from_scraped_data(scraped)
    assert "entities" in entities
    assert len(entities["entities"]["keywords"]) > 0
    
    # Step 3: Enrichment
    enrichment = pipeline_components["enrichment"].enrich(
        entities=entities["entities"],
        location=location
    )
    assert "temporal_attributes" in enrichment
    
    # Step 4: Feature Engineering
    features = pipeline_components["features"].compute_features(
        entities["entities"],
        enrichment
    )
    assert len(features) > 0
    
    # Step 5: Scoring
    scores = pipeline_components["scorer"].score(features, enrichment)
    assert "maturity" in scores
    assert 0 <= scores["maturity"] <= 100
    
    # Step 6: Generation
    persona = pipeline_components["generator"].generate(
        entities["entities"],
        enrichment,
        scores
    )
    assert "narrative" in persona
    
    # Step 7: Validation
    is_valid, issues = pipeline_components["validator"].validate(persona)
    assert is_valid, f"Validation failed: {issues}"


@pytest.mark.asyncio
async def test_pipeline_with_minimal_data(pipeline_components):
    """Test pipeline with minimal input data."""
    
    name = "Unknown Business"
    location = "Unknown"
    description = ""
    
    # Run through pipeline
    scraped = await pipeline_components["orchestrator"].scrape_all_sources(
        name=name,
        location=location,
        description=description
    )
    
    entities = pipeline_components["extractor"].extract_from_scraped_data(scraped)
    enrichment = pipeline_components["enrichment"].enrich(
        entities=entities["entities"],
        location=location
    )
    features = pipeline_components["features"].compute_features(
        entities["entities"],
        enrichment
    )
    scores = pipeline_components["scorer"].score(features, enrichment)
    persona = pipeline_components["generator"].generate(
        entities["entities"],
        enrichment,
        scores
    )
    
    # Should still generate valid persona
    assert "structured" in persona
    assert "narrative" in persona


@pytest.mark.asyncio
async def test_pipeline_error_handling(pipeline_components):
    """Test pipeline error handling."""
    
    # Invalid input
    try:
        scraped = await pipeline_components["orchestrator"].scrape_all_sources(
            name="",
            location="",
            description=""
        )
        # Should handle gracefully
        assert scraped is not None
    except Exception as e:
        pytest.fail(f"Pipeline should handle empty input: {e}")


def test_data_flow_consistency(pipeline_components):
    """Test that data flows consistently through pipeline."""
    
    # Create test data
    entities = {
        "persons": ["Test Person"],
        "organizations": ["Test Org"],
        "locations": ["Pune"],
        "keywords": ["technology", "software"]
    }
    
    enrichment = pipeline_components["enrichment"].enrich(
        entities=entities,
        location="Pune"
    )
    
    features = pipeline_components["features"].compute_features(entities, enrichment)
    scores = pipeline_components["scorer"].score(features, enrichment)
    persona = pipeline_components["generator"].generate(entities, enrichment, scores)
    
    # Verify data consistency
    assert persona["structured"]["location"]["city"] == "Pune"
    assert persona["structured"]["scores"] == scores


def test_pipeline_performance(pipeline_components):
    """Test pipeline performance."""
    import time
    
    entities = {
        "persons": ["Test"],
        "organizations": ["Test Org"],
        "locations": ["Pune"],
        "keywords": ["tech"]
    }
    
    start = time.time()
    
    enrichment = pipeline_components["enrichment"].enrich(entities, "Pune")
    features = pipeline_components["features"].compute_features(entities, enrichment)
    scores = pipeline_components["scorer"].score(features, enrichment)
    persona = pipeline_components["generator"].generate(entities, enrichment, scores)
    
    elapsed = time.time() - start
    
    # Should complete in reasonable time (< 5 seconds without scraping)
    assert elapsed < 5.0, f"Pipeline too slow: {elapsed}s"
