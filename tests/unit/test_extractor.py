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


def test_extract_from_linkedin(extractor, sample_scraped_data):
    """Test LinkedIn entity extraction."""
    entities = extractor._extract_from_linkedin(sample_scraped_data["linkedin"]["data"])
    
    assert "persons" in entities
    assert "organizations" in entities
    assert "locations" in entities
    assert len(entities["organizations"]) > 0
    assert "TechCorp" in str(entities["organizations"])


def test_extract_from_company(extractor, sample_scraped_data):
    """Test company website entity extraction."""
    entities = extractor._extract_from_company(sample_scraped_data["company"]["data"])
    
    assert "persons" in entities
    assert "organizations" in entities
    assert "Digital Marketing" in sample_scraped_data["company"]["data"]["description"]


def test_deduplicate_entities(extractor):
    """Test entity deduplication."""
    entities = ["TechCorp", "TechCorp Solutions", "ABC Company", "ABC"]
    deduplicated = extractor._deduplicate_entities(entities)
    
    # Should keep longer versions
    assert "TechCorp Solutions" in deduplicated
    assert "ABC Company" in deduplicated


def test_extract_from_all_sources(extractor, sample_scraped_data):
    """Test extraction from all sources."""
    result = extractor.extract_from_scraped_data(sample_scraped_data)
    
    assert "entities" in result
    assert "persons" in result["entities"]
    assert "organizations" in result["entities"]
    assert "locations" in result["entities"]
    assert "keywords" in result
    assert len(result["keywords"]) > 0


def test_empty_scraped_data(extractor):
    """Test handling of empty scraped data."""
    result = extractor.extract_from_scraped_data({})
    
    assert result["entities"]["persons"] == []
    assert result["entities"]["organizations"] == []
    assert result["entities"]["locations"] == []


def test_failed_scraping(extractor):
    """Test handling of failed scraping results."""
    failed_data = {
        "linkedin": {"success": False, "error": "Rate limited"},
        "company": {"success": False, "error": "Site down"}
    }
    
    result = extractor.extract_from_scraped_data(failed_data)
    
    # Should still return structure
    assert "entities" in result
    assert "keywords" in result
