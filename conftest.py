"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
from typing import Generator

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_person_data():
    """Sample person data for testing."""
    return {
        "name": "Yogesh Khandge",
        "location": "Pune, India",
        "description": "Digital marketing professional with 5 years experience in SEO and social media marketing"
    }


@pytest.fixture
def sample_entities():
    """Sample extracted entities."""
    return {
        "persons": ["Yogesh Khandge"],
        "organizations": ["TechCorp Solutions", "Digital Agency"],
        "locations": ["Pune", "Maharashtra"],
        "titles": ["Digital Marketing Manager"],
        "keywords": ["digital marketing", "SEO", "social media", "content strategy"]
    }


@pytest.fixture
def sample_enriched_data():
    """Sample enriched data."""
    return {
        "entities": {
            "persons": ["Yogesh Khandge"],
            "organizations": ["TechCorp"],
            "locations": ["Pune"]
        },
        "location_context": {
            "city": "Pune",
            "state": "Maharashtra",
            "country": "India",
            "affluence_score": 8.3,
            "tier": "Tier-1",
            "market_context": "High purchasing power metro"
        },
        "industry_context": {
            "industry": "Technology",
            "market_size_inr": 50000,
            "growth_rate": 15.0,
            "digital_maturity": 85,
            "avg_budget_lakhs": 20
        },
        "competitive_context": {
            "estimated_competitors": 50,
            "market_position": "Challenger"
        },
        "temporal_attributes": {
            "day_of_week": 5,
            "is_weekend": False,
            "is_business_hours": True
        }
    }


@pytest.fixture
def sample_features():
    """Sample feature dict."""
    return {
        "years_experience": 5,
        "company_count": 2,
        "organization_count": 1,
        "education_count": 1,
        "profile_completeness": 85,
        "digital_footprint_score": 75,
        "social_profile_count": 3,
        "has_linkedin": 1,
        "has_website": 1,
        "content_readiness": 70,
        "location_affluence": 8.3,
        "city_tier": 1,
        "budget_indicator": 75
    }


@pytest.fixture
def sample_scores():
    """Sample scoring results."""
    return {
        "maturity": 75.0,
        "marketing_readiness": 65.0,
        "budget_capacity": 80.0,
        "recommended_tier": 2
    }


@pytest.fixture
def sample_persona_data():
    """Sample complete persona data."""
    return {
        "name": "Yogesh Khandge",
        "title": "Digital Marketing Manager",
        "company": "TechCorp Solutions",
        "industry": None,
        "location": {
            "city": "Pune",
            "state": "Maharashtra",
            "country": "India",
            "affluence_score": 8.3,
            "market_context": "High purchasing power metro"
        },
        "business_metrics": {
            "estimated_revenue": None,
            "team_size": None,
            "years_in_business": 5,
            "growth_stage": "growth"
        },
        "digital_presence": {
            "linkedin_followers": None,
            "website_quality": "medium",
            "social_activity": "medium"
        },
        "scores": {
            "maturity": 75.0,
            "marketing_readiness": 65.0,
            "budget_capacity": 80.0,
            "recommended_tier": 2
        }
    }
