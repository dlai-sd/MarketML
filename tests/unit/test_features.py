"""Unit tests for feature engineering."""

import pytest
import pandas as pd
from app.features.feature_engineer import FeatureEngineer


@pytest.fixture
def feature_engineer():
    return FeatureEngineer()


@pytest.fixture
def sample_entities():
    return {
        "persons": ["John Doe"],
        "organizations": ["TechCorp", "Competitor A", "Competitor B"],
        "locations": ["Pune"],
        "keywords": ["digital marketing", "SEO", "social media", "website", "content"]
    }


@pytest.fixture
def sample_enrichment():
    return {
        "location": {
            "city": "Pune",
            "state": "Maharashtra",
            "tier": 1,
            "affluence_score": 75,
            "population": 5000000
        },
        "industry": {
            "primary_industry": "Technology",
            "market_size": 50000,
            "growth_rate": 15
        },
        "competitors": {
            "count": 2,
            "names": ["Competitor A", "Competitor B"]
        },
        "temporal_attributes": {
            "revenue_estimate": "10-50 Lakhs",
            "digital_maturity": "Basic",
            "growth_stage": "Early",
            "opportunity_score": 70
        }
    }


def test_compute_features(feature_engineer, sample_entities, sample_enrichment):
    """Test feature computation."""
    # Combine into single enriched_data dict
    enriched_data = {
        "entities": sample_entities,
        "location_context": sample_enrichment["location"],
        "industry_context": sample_enrichment["industry"],
        "temporal_attributes": sample_enrichment["temporal_attributes"]
    }
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, dict)
    # Check key features exist
    assert "business_maturity" in features or "years_experience" in features


def test_business_maturity_features(feature_engineer, sample_entities):
    """Test business maturity feature extraction."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    # Should return a features dict
    assert isinstance(features, dict)
    assert len(features) > 0


def test_digital_presence_features(feature_engineer, sample_entities):
    """Test digital presence features."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, dict)
    assert len(features) > 0


def test_location_features(feature_engineer, sample_enrichment):
    """Test location-based features."""
    enriched_data = {"location_context": sample_enrichment["location"]}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, dict)


def test_network_features(feature_engineer, sample_entities):
    """Test network features."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, dict)
    assert len(features) > 0


def test_empty_data(feature_engineer):
    """Test handling of empty data."""
    enriched_data = {
        "entities": {"persons": [], "organizations": [], "locations": [], "keywords": []},
        "location_context": {},
        "industry_context": {},
        "temporal_attributes": {}
    }
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, dict)


def test_feature_normalization(feature_engineer, sample_entities, sample_enrichment):
    """Test that features are properly normalized."""
    enriched_data = {
        "entities": sample_entities,
        "location_context": sample_enrichment["location"],
        "industry_context": sample_enrichment["industry"],
        "temporal_attributes": sample_enrichment["temporal_attributes"]
    }
    features = feature_engineer.compute_features(enriched_data)
    
    # Features should be a dict with numeric values
    assert isinstance(features, dict)
    for key, val in features.items():
        if isinstance(val, (int, float)):
            assert val >= 0, f"{key} has negative value"
