"""Unit tests for enrichment engine."""

import pytest
import asyncio
from app.enrichment.enrichment_engine import EnrichmentEngine


@pytest.fixture
def enrichment_engine():
    return EnrichmentEngine()


@pytest.mark.asyncio
async def test_enrich_basic(enrichment_engine, sample_entities):
    """Test basic enrichment."""
    result = await enrichment_engine.enrich(
        entities=sample_entities,
        location="Pune, Maharashtra"
    )
    
    assert "entities" in result
    assert "location_context" in result
    assert "industry_context" in result
    assert "competitive_context" in result
    assert "temporal_attributes" in result


def test_enrich_location(enrichment_engine):
    """Test location enrichment."""
    location_data = enrichment_engine._enrich_location("Pune")
    
    assert "city" in location_data
    assert "state" in location_data
    assert "tier" in location_data
    assert "affluence_score" in location_data
    assert location_data["tier"] in ["Tier-1", "Tier-2", "Tier-3"]


def test_enrich_industry(enrichment_engine, sample_entities):
    """Test industry enrichment."""
    industry_data = enrichment_engine._enrich_industry(sample_entities)
    
    assert "primary_industry" in industry_data
    assert "secondary_industries" in industry_data
    assert "market_size" in industry_data
    assert industry_data["primary_industry"] != ""


def test_temporal_attributes(enrichment_engine, sample_entities):
    """Test temporal attributes computation."""
    temporal = enrichment_engine._compute_temporal_attributes(
        sample_entities,
        {"city": "Pune", "tier": 1}
    )
    
    # All 10 required attributes
    assert "revenue_estimate" in temporal
    assert "market_context" in temporal
    assert "digital_maturity" in temporal
    assert "marketing_budget_range" in temporal
    assert "growth_stage" in temporal
    assert "pain_points" in temporal
    assert "opportunity_score" in temporal
    assert "competitive_pressure" in temporal
    assert "urgency_level" in temporal
    assert "decision_timeline" in temporal


def test_enrich_with_empty_entities(enrichment_engine):
    """Test enrichment with minimal data."""
    result = enrichment_engine.enrich(
        entities={"persons": [], "organizations": [], "locations": [], "keywords": []},
        location="Unknown"
    )
    
    # Should still return structure
    assert "location" in result
    assert "industry" in result


def test_tier_calculation(enrichment_engine):
    """Test city tier calculation."""
    tier1_cities = ["Mumbai", "Delhi", "Bangalore", "Pune"]
    tier2_cities = ["Jaipur", "Chandigarh", "Lucknow"]
    
    for city in tier1_cities:
        location = enrichment_engine._enrich_location(city)
        assert location["tier"] == 1
    
    for city in tier2_cities:
        location = enrichment_engine._enrich_location(city)
        assert location["tier"] == 2


def test_affluence_scoring(enrichment_engine):
    """Test affluence score calculation."""
    # Tier 1 cities should have higher affluence
    pune_data = enrichment_engine._enrich_location("Pune")
    small_city_data = enrichment_engine._enrich_location("Solapur")
    
    assert pune_data["affluence_score"] > small_city_data["affluence_score"]
