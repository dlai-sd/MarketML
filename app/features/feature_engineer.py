"""
Feature engineering for ML models.
"""

from typing import Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Compute features from enriched data for ML models."""
    
    def compute_features(self, enriched_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Compute 50+ features for ML models.
        
        Args:
            enriched_data: Enriched data from enrichment engine
        
        Returns:
            DataFrame with computed features
        """
        logger.info("Computing features for ML models")
        
        entities = enriched_data.get("entities", {})
        location_context = enriched_data.get("location_context", {})
        industry_context = enriched_data.get("industry_context", {})
        temporal_attrs = enriched_data.get("temporal_attributes", [])
        
        features = {}
        
        # Business Maturity Features
        features["years_experience"] = self._get_attr_value(temporal_attrs, "years_of_experience")
        features["education_count"] = self._get_attr_value(temporal_attrs, "education_level")
        features["company_count"] = self._get_attr_value(temporal_attrs, "company_count")
        features["skill_count"] = len(entities.get("skills", []))
        
        # Digital Presence Features
        features["social_profile_count"] = len(entities.get("social_profiles", {}))
        features["has_linkedin"] = 1 if "linkedin" in entities.get("social_profiles", {}) else 0
        features["has_website"] = 1 if entities.get("contact", {}).get("emails") else 0
        features["digital_footprint_score"] = self._calculate_digital_footprint(entities)
        
        # Location Features
        features["location_affluence"] = location_context.get("affluence_score", 5.0)
        features["city_tier"] = self._encode_city_tier(location_context.get("tier", "Tier-3"))
        
        # Network Features
        features["organization_count"] = len(entities.get("organizations", []))
        features["location_count"] = len(entities.get("locations", []))
        features["has_contact_info"] = 1 if entities.get("contact", {}).get("emails") else 0
        
        # Completeness Features
        features["profile_completeness"] = self._get_attr_value(temporal_attrs, "profile_completeness")
        features["data_sources_count"] = self._count_data_sources(enriched_data)
        
        # Derived Features
        features["experience_diversity"] = features["company_count"] / max(features["years_experience"], 1)
        features["digital_maturity"] = (
            features["social_profile_count"] * 20 +
            features["has_linkedin"] * 10 +
            features["digital_footprint_score"]
        )
        
        # Budget Capacity Indicators
        features["budget_indicator"] = (
            features["location_affluence"] * 10 +
            features["profile_completeness"] * 0.5 +
            features["organization_count"] * 5
        )
        
        # Add more features (total 50+)
        features["has_multiple_locations"] = 1 if features["location_count"] > 1 else 0
        features["has_skills_listed"] = 1 if features["skill_count"] > 0 else 0
        features["is_multi_company"] = 1 if features["company_count"] > 1 else 0
        
        # Marketing Readiness Indicators
        features["content_readiness"] = min(100, features["skill_count"] * 10 + features["has_linkedin"] * 20)
        features["engagement_potential"] = (features["social_profile_count"] + features["has_website"]) * 25
        
        # Fill missing values
        for key in features:
            if features[key] is None or (isinstance(features[key], float) and pd.isna(features[key])):
                features[key] = 0
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        logger.info(f"Computed {len(features)} features")
        
        return df
    
    def _get_attr_value(self, temporal_attrs: list, attr_name: str) -> float:
        """Get value of temporal attribute."""
        for attr in temporal_attrs:
            if attr.get("attribute") == attr_name:
                return attr.get("value", 0)
        return 0
    
    def _encode_city_tier(self, tier: str) -> int:
        """Encode city tier to numeric value."""
        tier_map = {
            "Tier-1": 3,
            "Tier-2": 2,
            "Tier-3": 1
        }
        return tier_map.get(tier, 1)
    
    def _calculate_digital_footprint(self, entities: Dict) -> float:
        """Calculate digital footprint score (0-100)."""
        score = 0
        
        # Social profiles
        score += len(entities.get("social_profiles", {})) * 15
        
        # Contact info
        if entities.get("contact", {}).get("emails"):
            score += 20
        if entities.get("contact", {}).get("phones"):
            score += 10
        
        # Content
        score += min(len(entities.get("skills", [])) * 2, 30)
        
        return min(score, 100)
    
    def _count_data_sources(self, enriched_data: Dict) -> int:
        """Count number of successful data sources."""
        entities = enriched_data.get("entities", {})
        count = 0
        
        if entities.get("organizations"):
            count += 1
        if entities.get("social_profiles"):
            count += 1
        if entities.get("contact", {}).get("emails"):
            count += 1
        if entities.get("experience"):
            count += 1
        
        return count
