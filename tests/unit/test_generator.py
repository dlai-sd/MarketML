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


def test_generate_persona(generator, sample_data):
    """Test full persona generation."""
    persona = generator.generate(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    assert "structured" in persona
    assert "narrative" in persona
    assert "short_narrative" in persona
    assert "marketing_insights" in persona
    assert "recommended_actions" in persona


def test_structured_data(generator, sample_data):
    """Test structured data generation."""
    persona = generator.generate(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    structured = persona["structured"]
    assert "name" in structured
    assert "location" in structured
    assert "industry" in structured
    assert "scores" in structured
    assert structured["scores"]["maturity"] == 65


def test_narrative_generation(generator, sample_data):
    """Test narrative generation."""
    narrative = generator._generate_narrative(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    assert isinstance(narrative, str)
    assert len(narrative) >= 200  # Should be substantial
    assert "Pune" in narrative  # Should include location


def test_short_narrative(generator, sample_data):
    """Test short narrative generation."""
    short = generator._generate_short_narrative(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    assert isinstance(short, str)
    words = short.split()
    assert 10 <= len(words) <= 20  # Around 15 words as specified


def test_insights_generation(generator, sample_data):
    """Test marketing insights generation."""
    insights = generator._generate_insights(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    assert isinstance(insights, list)
    assert 3 <= len(insights) <= 5  # 3-5 insights
    assert all(isinstance(i, str) for i in insights)


def test_actions_generation(generator, sample_data):
    """Test recommended actions generation."""
    actions = generator._generate_actions(sample_data["scores"])
    
    assert isinstance(actions, list)
    assert len(actions) >= 3
    assert all(isinstance(a, str) for a in actions)


def test_tier_specific_actions(generator):
    """Test that actions vary by tier."""
    tier0_actions = generator._generate_actions({"recommended_tier": 0})
    tier3_actions = generator._generate_actions({"recommended_tier": 3})
    
    # Should have different recommendations
    assert tier0_actions != tier3_actions


def test_empty_data_handling(generator):
    """Test handling of minimal data."""
    persona = generator.generate(
        {"persons": [], "organizations": [], "locations": [], "keywords": []},
        {"temporal_attributes": {}},
        {"maturity": 0, "marketing_readiness": 0, "budget_capacity": 0, "recommended_tier": 0}
    )
    
    # Should still generate valid structure
    assert "structured" in persona
    assert "narrative" in persona


def test_narrative_length(generator, sample_data):
    """Test narrative stays within word count."""
    narrative = generator._generate_narrative(
        sample_data["entities"],
        sample_data["enrichment"],
        sample_data["scores"]
    )
    
    words = narrative.split()
    assert 200 <= len(words) <= 350  # Within specified range
