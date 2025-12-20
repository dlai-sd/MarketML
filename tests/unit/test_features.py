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
    features = feature_engineer.compute_features(sample_entities, sample_enrichment)
    
    assert isinstance(features, pd.DataFrame)
    assert len(features) == 1  # Single row
    
    # Check key features exist
    assert "business_maturity" in features.columns
    assert "digital_footprint" in features.columns
    assert "budget_indicator" in features.columns
    assert "location_score" in features.columns
    assert "competitive_intensity" in features.columns


def test_business_maturity_features(feature_engineer, sample_entities):
    """Test business maturity feature extraction."""
    features = feature_engineer._compute_maturity_features(sample_entities)
    
    assert "org_count" in features
    assert "keyword_diversity" in features
    assert features["org_count"] == 3
    assert features["keyword_diversity"] > 0


def test_digital_presence_features(feature_engineer, sample_entities):
    """Test digital presence features."""
    features = feature_engineer._compute_digital_features(sample_entities)
    
    assert "digital_keywords" in features
    assert "has_website_mention" in features
    assert features["digital_keywords"] > 0


def test_location_features(feature_engineer, sample_enrichment):
    """Test location-based features."""
    features = feature_engineer._compute_location_features(sample_enrichment["location"])
    
    assert "city_tier" in features
    assert "affluence" in features
    assert features["city_tier"] == 1
    assert features["affluence"] == 75


def test_network_features(feature_engineer, sample_entities):
    """Test network features."""
    features = feature_engineer._compute_network_features(sample_entities)
    
    assert "person_count" in features
    assert "org_network" in features


def test_empty_data(feature_engineer):
    """Test handling of empty data."""
    features = feature_engineer.compute_features(
        {"persons": [], "organizations": [], "locations": [], "keywords": []},
        {"location": {}, "industry": {}, "competitors": {}, "temporal_attributes": {}}
    )
    
    assert isinstance(features, pd.DataFrame)
    assert len(features) == 1


def test_feature_normalization(feature_engineer, sample_entities, sample_enrichment):
    """Test that features are properly normalized."""
    features = feature_engineer.compute_features(sample_entities, sample_enrichment)
    
    # Most features should be between 0-100 or boolean
    numeric_cols = features.select_dtypes(include=['float64', 'int64']).columns
    
    for col in numeric_cols:
        val = features[col].iloc[0]
        # Check reasonable ranges
        assert val >= 0, f"{col} has negative value"
