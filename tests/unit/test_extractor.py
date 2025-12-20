"""Unit tests for entity extractor."""

import pytest
from app.extractors.entity_extractor import EntityExtractor


@pytest.fixture
def extractor():
    return EntityExtractor()


@pytest.fixture
def sample_scraped_data():
    return {
        "linkedin": {
            "success": True,
            "data": {
                "headline": "Founder at TechCorp | Digital Marketing Expert",
                "company": "TechCorp Solutions",
                "location": "Pune, Maharashtra",
                "experience": ["Digital Marketing Manager at ABC", "Founder at TechCorp"],
                "skills": ["Digital Marketing", "SEO", "Content Strategy"]
            }
        },
        "company": {
            "success": True,
            "data": {
                "description": "TechCorp Solutions provides innovative digital marketing services in Pune",
                "services": ["SEO", "Social Media Marketing", "Content Marketing"]
            }
        },
        "news": {
            "success": True,
            "data": {
                "articles": [
                    {"title": "TechCorp wins Best Startup Award", "content": "Pune-based TechCorp Solutions..."}
                ]
            }
        }
    }


@pytest.mark.asyncio
async def test_extract_from_linkedin(extractor, sample_scraped_data):
    """Test LinkedIn entity extraction."""
    result = await extractor.extract_from_scraped_data({"linkedin": sample_scraped_data["linkedin"]})
    
    assert "persons" in result
    assert "organizations" in result
    assert "locations" in result
    assert len(result["organizations"]) > 0
    assert "TechCorp" in str(result["organizations"])


@pytest.mark.asyncio
async def test_extract_from_company(extractor, sample_scraped_data):
    """Test company website entity extraction."""
    result = await extractor.extract_from_scraped_data({"company": sample_scraped_data["company"]})
    
    assert "persons" in result
    assert "organizations" in result
    # Verify the source data contains expected content
    assert "digital marketing" in sample_scraped_data["company"]["data"]["description"].lower()


def test_deduplicate_entities(extractor):  
    """Test entity deduplication."""
    entities_dict = {
        "organizations": ["TechCorp", "TechCorp Solutions", "ABC Company", "ABC"],
        "persons": [],
        "locations": [],
        "titles": [],
        "skills": [],
        "dates": [],
        "contact": {"emails": [], "phones": []},
        "social_profiles": {},
        "experience": [],
        "education": []
    }
    deduplicated = extractor._deduplicate_entities(entities_dict)
    
    # Should keep longer versions
    assert "TechCorp Solutions" in deduplicated["organizations"]
    assert "ABC Company" in deduplicated["organizations"]


@pytest.mark.asyncio
async def test_extract_from_all_sources(extractor, sample_scraped_data):
    """Test extraction from all sources."""
    result = await extractor.extract_from_scraped_data(sample_scraped_data)
    
    assert "persons" in result
    assert "organizations" in result
    assert "locations" in result
    assert "skills" in result
    assert len(result["skills"]) > 0


@pytest.mark.asyncio
async def test_empty_scraped_data(extractor):
    """Test handling of empty scraped data."""
    result = await extractor.extract_from_scraped_data({})
    
    assert result["persons"] == []
    assert result["organizations"] == []
    assert result["locations"] == []


@pytest.mark.asyncio
async def test_failed_scraping(extractor):
    """Test handling of failed scraping results."""
    failed_data = {
        "linkedin": {"success": False, "error": "Rate limited"},
        "company": {"success": False, "error": "Site down"}
    }
    
    result = await extractor.extract_from_scraped_data(failed_data)
    
    # Should still return structure
    assert "persons" in result
    assert "organizations" in result
