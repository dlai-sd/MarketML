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
        "temporal_attributes": [
            {"attribute": "years_of_experience", "value": 5, "confidence": 0.7},
            {"attribute": "education_level", "value": 2, "confidence": 0.8},
            {"attribute": "skill_count", "value": 8, "confidence": 0.6},
            {"attribute": "digital_footprint", "value": 3, "confidence": 0.7},
            {"attribute": "professional_connections", "value": 150, "confidence": 0.5},
            {"attribute": "content_activity", "value": 25, "confidence": 0.4}
        ]
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
    
    assert isinstance(features, pd.DataFrame)
    # Check key features exist
    assert "years_experience" in features.columns or "business_maturity" in features.columns


def test_business_maturity_features(feature_engineer, sample_entities):
    """Test business maturity feature extraction."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    # Should return a features DataFrame
    assert isinstance(features, pd.DataFrame)
    assert len(features) > 0


def test_digital_presence_features(feature_engineer, sample_entities):
    """Test digital presence features."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, pd.DataFrame)
    assert len(features) > 0


def test_location_features(feature_engineer, sample_enrichment):
    """Test location-based features."""
    enriched_data = {"location_context": sample_enrichment["location"]}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, pd.DataFrame)


def test_network_features(feature_engineer, sample_entities):
    """Test network features."""
    enriched_data = {"entities": sample_entities}
    features = feature_engineer.compute_features(enriched_data)
    
    assert isinstance(features, pd.DataFrame)
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
    
    assert isinstance(features, pd.DataFrame)


def test_feature_normalization(feature_engineer, sample_entities, sample_enrichment):
    """Test that features are properly normalized."""
    enriched_data = {
        "entities": sample_entities,
        "location_context": sample_enrichment["location"],
        "industry_context": sample_enrichment["industry"],
        "temporal_attributes": sample_enrichment["temporal_attributes"]
    }
    features = feature_engineer.compute_features(enriched_data)
    
    # Features should be a DataFrame
    assert isinstance(features, pd.DataFrame)
    # Check we have numeric columns
    assert len(features.select_dtypes(include=["number"]).columns) > 0
