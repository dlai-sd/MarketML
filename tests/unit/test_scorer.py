"""Unit tests for ensemble scorer."""

import pytest
import pandas as pd
from app.scoring.ensemble_scorer import EnsembleScorer


@pytest.fixture
def scorer():
    return EnsembleScorer()


@pytest.fixture
def sample_features():
    return pd.DataFrame({
        "business_maturity": [65],
        "digital_footprint": [45],
        "budget_indicator": [55],
        "location_score": [75],
        "competitive_intensity": [60],
        "keyword_diversity": [8],
        "org_count": [3],
        "digital_keywords": [5],
        "has_website_mention": [1],
        "city_tier": [1],
        "affluence": [75]
    })


@pytest.fixture
def sample_enrichment():
    return {
        "temporal_attributes": {
            "revenue_estimate": "10-50 Lakhs",
            "digital_maturity": "Intermediate",
            "growth_stage": "Growth",
            "opportunity_score": 70
        }
    }


def test_score_computation(scorer, sample_features, sample_enrichment):
    """Test score computation."""
    result = scorer.score(sample_features, sample_enrichment)
    
    assert "maturity" in result
    assert "marketing_readiness" in result
    assert "budget_capacity" in result
    assert "recommended_tier" in result
    
    # Scores should be 0-100
    assert 0 <= result["maturity"] <= 100
    assert 0 <= result["marketing_readiness"] <= 100
    assert 0 <= result["budget_capacity"] <= 100
    
    # Tier should be 0-4
    assert 0 <= result["recommended_tier"] <= 4


def test_rule_based_scoring(scorer, sample_features, sample_enrichment):
    """Test rule-based scoring fallback."""
    result = scorer._rule_based_scoring(sample_features, sample_enrichment)
    
    assert isinstance(result, dict)
    assert all(key in result for key in ["maturity", "marketing_readiness", "budget_capacity"])


def test_tier_recommendation(scorer):
    """Test tier recommendation logic."""
    # High scores should recommend higher tiers
    high_scores = {"maturity": 85, "marketing_readiness": 80, "budget_capacity": 90}
    tier = scorer._recommend_tier(high_scores)
    assert tier >= 2
    
    # Low scores should recommend lower tiers
    low_scores = {"maturity": 30, "marketing_readiness": 25, "budget_capacity": 20}
    tier = scorer._recommend_tier(low_scores)
    assert tier <= 1


def test_score_consistency(scorer, sample_features, sample_enrichment):
    """Test that scoring is consistent."""
    result1 = scorer.score(sample_features, sample_enrichment)
    result2 = scorer.score(sample_features, sample_enrichment)
    
    assert result1 == result2


def test_edge_cases(scorer):
    """Test edge cases."""
    # Empty features
    empty_features = pd.DataFrame({
        "business_maturity": [0],
        "digital_footprint": [0],
        "budget_indicator": [0],
        "location_score": [0],
        "competitive_intensity": [0]
    })
    
    result = scorer.score(empty_features, {})
    
    # Should still return valid structure
    assert all(key in result for key in ["maturity", "marketing_readiness", "budget_capacity", "recommended_tier"])
    assert result["recommended_tier"] == 0  # Not ready


def test_revenue_parsing(scorer):
    """Test revenue estimate parsing."""
    estimates = [
        "0-10 Lakhs",
        "10-50 Lakhs",
        "50 Lakhs - 1 Cr",
        "Unknown"
    ]
    
    for estimate in estimates:
        enrichment = {"temporal_attributes": {"revenue_estimate": estimate}}
        features = pd.DataFrame({"business_maturity": [50]})
        
        result = scorer._rule_based_scoring(features, enrichment)
        assert isinstance(result["budget_capacity"], (int, float))
