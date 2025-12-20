"""Unit tests for quality validator."""

import pytest
from app.validation.quality_validator import QualityValidator


@pytest.fixture
def validator():
    return QualityValidator()


@pytest.fixture
def valid_persona():
    return {
        "structured": {
            "name": "Yogesh Khandge",
            "location": {
                "city": "Pune",
                "state": "Maharashtra",
                "country": "India"
            },
            "industry": "Technology",
            "scores": {
                "maturity": 65,
                "marketing_readiness": 55,
                "budget_capacity": 55,
                "recommended_tier": 2
            }
        },
        "confidence_score": 0.85,
        "narrative": "Yogesh Khandge is a technology professional based in Pune, Maharashtra, with extensive experience in digital marketing. " * 5 + "He demonstrates strong market potential.",
        "short_narrative": "Growing technology business in Pune with strong digital marketing potential and innovative approach.",
        "marketing_insights": [
            "Strong local market presence",
            "Growing digital footprint",
            "Budget-conscious decision maker"
        ],
        "recommended_actions": [
            "Start with social media presence",
            "Invest in SEO optimization",
            "Build professional website"
        ]
    }


def test_valid_persona(validator, valid_persona):
    """Test validation of valid persona."""
    is_valid, issues = validator.validate(valid_persona)
    
    assert is_valid
    assert len(issues) == 0


def test_missing_required_fields(validator, valid_persona):
    """Test detection of missing fields."""
    invalid = valid_persona.copy()
    del invalid["narrative"]
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("narrative" in issue.lower() for issue in issues)


def test_score_range_validation(validator, valid_persona):
    """Test score range validation."""
    invalid = valid_persona.copy()
    invalid["structured"]["scores"]["maturity"] = 150  # Out of range
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("score" in issue.lower() for issue in issues)


def test_narrative_length_validation(validator, valid_persona):
    """Test narrative length validation."""
    invalid = valid_persona.copy()
    invalid["narrative"] = "Too short."
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("narrative" in issue.lower() and "short" in issue.lower() for issue in issues)


def test_short_narrative_validation(validator, valid_persona):
    """Test short narrative validation."""
    invalid = valid_persona.copy()
    invalid["short_narrative"] = "This is way too long " * 10
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("short" in issue.lower() for issue in issues)


def test_insights_validation(validator, valid_persona):
    """Test insights count validation."""
    invalid = valid_persona.copy()
    invalid["marketing_insights"] = ["Only one insight"]
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("insights" in issue.lower() for issue in issues)


def test_actions_validation(validator, valid_persona):
    """Test actions count validation."""
    invalid = valid_persona.copy()
    invalid["recommended_actions"] = []
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("actions" in issue.lower() for issue in issues)


def test_tier_consistency(validator, valid_persona):
    """Test tier consistency with scores."""
    invalid = valid_persona.copy()
    invalid["structured"]["scores"]["maturity"] = 10
    invalid["structured"]["scores"]["marketing_readiness"] = 10
    invalid["structured"]["scores"]["budget_capacity"] = 10
    invalid["structured"]["scores"]["recommended_tier"] = 4  # Should be 0
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert any("tier" in issue.lower() or "inconsistent" in issue.lower() for issue in issues)


def test_empty_persona(validator):
    """Test validation of empty persona."""
    is_valid, issues = validator.validate({})
    
    assert not is_valid
    assert len(issues) > 0


def test_multiple_issues(validator):
    """Test detection of multiple issues."""
    invalid = {
        "structured": {
            "scores": {
                "maturity": 150,  # Out of range
                "marketing_readiness": -10,  # Out of range
                "budget_capacity": 50,
                "recommended_tier": 5  # Invalid tier
            }
        },
        "narrative": "Short",  # Too short
        "marketing_insights": []  # Too few
    }
    
    is_valid, issues = validator.validate(invalid)
    
    assert not is_valid
    assert len(issues) >= 3  # Multiple issues detected
