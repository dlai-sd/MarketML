"""
Quality validator for generated personas.
"""

from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)


class QualityValidator:
    """Validate quality of generated personas."""
    
    def validate(self, persona_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate persona quality.
        
        Args:
            persona_data: Generated persona data
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        logger.info("Validating persona quality")
        
        issues = []
        
        # Check completeness
        issues.extend(self._check_completeness(persona_data))
        
        # Check consistency
        issues.extend(self._check_consistency(persona_data))
        
        # Check narrative quality
        issues.extend(self._check_narrative_quality(persona_data))
        
        # Check confidence threshold
        if persona_data.get("confidence_score", 0) < 0.4:
            issues.append("Low confidence score (< 0.4)")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.info("Persona passed all quality checks")
        else:
            logger.warning(f"Persona has {len(issues)} quality issues")
        
        return is_valid, issues
    
    def _check_completeness(self, persona_data: Dict) -> List[str]:
        """Check if required fields are present."""
        issues = []
        
        # Required fields
        required = [
            ("structured", dict),
            ("narrative", str),
            ("short_narrative", str),
            ("confidence_score", (int, float))
        ]
        
        for field, expected_type in required:
            if field not in persona_data:
                issues.append(f"Missing required field: {field}")
            elif not isinstance(persona_data[field], expected_type):
                issues.append(f"Invalid type for {field}")
        
        # Check structured data completeness
        if "structured" in persona_data:
            structured = persona_data["structured"]
            if not structured.get("name"):
                issues.append("Missing name in structured data")
            if not structured.get("location"):
                issues.append("Missing location in structured data")
            if not structured.get("scores"):
                issues.append("Missing scores in structured data")
        
        return issues
    
    def _check_consistency(self, persona_data: Dict) -> List[str]:
        """Check internal consistency of data."""
        issues = []
        
        structured = persona_data.get("structured", {})
        narrative = persona_data.get("narrative", "")
        
        # Check if name appears in narrative
        name = structured.get("name", "")
        if name and name not in narrative:
            issues.append("Name not found in narrative")
        
        # Check if location appears in narrative
        location = structured.get("location", {})
        city = location.get("city", "")
        if city and city not in narrative:
            issues.append("City not found in narrative")
        
        # Check score ranges
        scores = structured.get("scores", {})
        for score_name, score_value in scores.items():
            if score_name == "recommended_tier":
                if not (0 <= score_value <= 4):
                    issues.append(f"Invalid tier value: {score_value}")
            else:
                if not (0 <= score_value <= 100):
                    issues.append(f"Score {score_name} out of range: {score_value}")
        
        return issues
    
    def _check_narrative_quality(self, persona_data: Dict) -> List[str]:
        """Check quality of generated narrative."""
        issues = []
        
        narrative = persona_data.get("narrative", "")
        short_narrative = persona_data.get("short_narrative", "")
        
        # Check narrative length
        narrative_words = len(narrative.split())
        if narrative_words < 50:
            issues.append(f"Narrative too short ({narrative_words} words, minimum 50)")
        elif narrative_words > 500:
            issues.append(f"Narrative too long ({narrative_words} words, maximum 500)")
        
        # Check short narrative length
        short_words = len(short_narrative.split())
        if short_words < 10:
            issues.append(f"Short narrative too short ({short_words} words)")
        elif short_words > 25:
            issues.append(f"Short narrative too long ({short_words} words)")
        
        # Check for placeholder text
        placeholders = ["TODO", "None", "null", "undefined", "N/A"]
        for placeholder in placeholders:
            if placeholder in narrative:
                issues.append(f"Placeholder text found in narrative: {placeholder}")
        
        # Check for basic grammar (very simple check)
        if narrative and not narrative[0].isupper():
            issues.append("Narrative doesn't start with capital letter")
        
        if narrative and narrative[-1] not in ".!?":
            issues.append("Narrative doesn't end with punctuation")
        
        return issues
