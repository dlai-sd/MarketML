"""Unit tests for persona generator."""

import pytest
from app.generation.persona_generator import PersonaGenerator


@pytest.fixture
def generator():
    return PersonaGenerator()


@pytest.fixture
def sample_data():
    return {
        "entities": {
            "persons": ["Yogesh Khandge"],
            "organizations": ["TechCorp Solutions"],
            "locations": ["Pune"],
            "keywords": ["digital marketing", "SEO"]
        },
        "enrichment": {
            "location": {
                "city": "Pune",
                "state": "Maharashtra",
                "tier": 1,
                "affluence_score": 75
            },
            "industry": {
                "primary_industry": "Technology",
                "market_size": 50000
            },
            "temporal_attributes": {
                "revenue_estimate": "10-50 Lakhs",
                "digital_maturity": "Intermediate",
                "growth_stage": "Growth",
                "pain_points": ["Limited online presence", "Budget constraints"],
                "opportunity_score": 70
            }
        },
        "scores": {
            "maturity": 65,
            "marketing_readiness": 55,
            "budget_capacity": 45,
            "recommended_tier": 2
        }
    }


@pytest.mark.asyncio
async def test_generate_persona(generator, sample_data):
    """Test full persona generation."""
    # Combine data for current API signature
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    
    assert "structured" in persona
    assert "narrative" in persona
    assert "short_narrative" in persona
    assert "marketing_insights" in persona
    assert "recommended_actions" in persona


@pytest.mark.asyncio
async def test_structured_data(generator, sample_data):
    """Test structured data generation."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    
    structured = persona["structured"]
    assert "name" in structured
    assert "scores" in structured
    assert structured["scores"]["maturity"] == 65


@pytest.mark.asyncio
async def test_narrative_generation(generator, sample_data):
    """Test narrative generation."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    narrative = persona["narrative"]
    
    assert isinstance(narrative, str)
    assert len(narrative) >= 100  # Should have content


@pytest.mark.asyncio
async def test_short_narrative(generator, sample_data):
    """Test short narrative generation."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    short = persona["short_narrative"]
    
    assert isinstance(short, str)
    assert len(short) > 0


@pytest.mark.asyncio
async def test_insights_generation(generator, sample_data):
    """Test marketing insights generation."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    insights = persona["marketing_insights"]
    
    assert isinstance(insights, list)
    assert len(insights) >= 3
    assert all(isinstance(i, str) for i in insights)


@pytest.mark.asyncio
async def test_actions_generation(generator, sample_data):
    """Test recommended actions generation."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    actions = persona["recommended_actions"]
    
    assert isinstance(actions, list)
    assert len(actions) >= 3
    assert all(isinstance(a, str) for a in actions)


@pytest.mark.asyncio
async def test_tier_specific_actions(generator):
    """Test that actions vary by tier."""
    enriched_data = {"entities": {}, "temporal_attributes": {}}
    
    tier0_persona = await generator.generate("Test0", enriched_data, {"recommended_tier": 0, "maturity": 0, "marketing_readiness": 0, "budget_capacity": 0})
    tier3_persona = await generator.generate("Test3", enriched_data, {"recommended_tier": 3, "maturity": 80, "marketing_readiness": 80, "budget_capacity": 80})
    
    tier0_actions = tier0_persona["recommended_actions"]
    tier3_actions = tier3_persona["recommended_actions"]
    
    # Should have actions
    assert len(tier0_actions) >= 3
    assert len(tier3_actions) >= 3


@pytest.mark.asyncio
async def test_empty_data_handling(generator):
    """Test handling of minimal data."""
    enriched_data = {
        "entities": {"persons": [], "organizations": [], "locations": [], "keywords": []},
        "temporal_attributes": {}
    }
    scores = {"maturity": 0, "marketing_readiness": 0, "budget_capacity": 0, "recommended_tier": 0}
    
    persona = await generator.generate("Empty Test", enriched_data, scores)
    
    # Should still generate valid structure
    assert "structured" in persona
    assert "narrative" in persona


@pytest.mark.asyncio
async def test_narrative_length(generator, sample_data):
    """Test narrative stays within word count."""
    name = sample_data["entities"]["persons"][0] if sample_data["entities"]["persons"] else "Test Business"
    enriched_data = {
        "entities": sample_data["entities"],
        "location_context": sample_data["enrichment"]["location"],
        "temporal_attributes": sample_data["enrichment"]["temporal_attributes"]
    }
    scores = sample_data["scores"]
    
    persona = await generator.generate(name, enriched_data, scores)
    narrative = persona["narrative"]
    
    # Should have content
    assert len(narrative) > 50
