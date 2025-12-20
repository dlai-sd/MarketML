"""
Ensemble scorer using multiple ML models.
"""

from typing import Dict
import pandas as pd
import logging
import os
import pickle

logger = logging.getLogger(__name__)


class EnsembleScorer:
    """Ensemble of ML models for persona scoring."""
    
    def __init__(self):
        """Initialize models."""
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Try to load models, create placeholders if not found
        self.models = self._load_models()
        self.weights = [0.6, 0.3, 0.1]  # XGBoost, RF, Linear
    
    def predict(self, features: pd.DataFrame) -> Dict[str, float]:
        """
        Predict persona scores using ensemble of models.
        
        Args:
            features: Feature DataFrame
        
        Returns:
            Dictionary of scores
        """
        logger.info("Scoring persona with ML models")
        
        # TODO: Use actual trained models
        # For now, use rule-based scoring as placeholder
        
        scores = self._rule_based_scoring(features)
        
        logger.info(f"Scores: maturity={scores['maturity']:.1f}, " +
                   f"readiness={scores['marketing_readiness']:.1f}, " +
                   f"budget={scores['budget_capacity']:.1f}")
        
        return scores
    
    def score(self, features: Dict, enrichment: Dict) -> Dict[str, float]:
        """
        Score a persona based on features and enrichment data.
        Adapter method that converts dict inputs to DataFrame for predict().
        
        Args:
            features: Feature dictionary
            enrichment: Enrichment data dictionary
        
        Returns:
            Dictionary of scores
        """
        # Convert to DataFrame
        df = pd.DataFrame([features])
        return self.predict(df)
    
    def _rule_based_scoring(self, features: pd.DataFrame) -> Dict[str, float]:
        """
        Rule-based scoring as placeholder until models are trained.
        
        This provides reasonable scores based on feature values.
        """
        row = features.iloc[0]
        
        # Business Maturity Score (0-100)
        maturity = min(100, (
            row.get("years_experience", 0) * 8 +
            row.get("company_count", 0) * 10 +
            row.get("organization_count", 0) * 5 +
            row.get("education_count", 0) * 10 +
            row.get("profile_completeness", 0) * 0.3
        ))
        
        # Marketing Readiness Score (0-100)
        marketing_readiness = min(100, (
            row.get("digital_footprint_score", 0) * 0.4 +
            row.get("social_profile_count", 0) * 15 +
            row.get("has_linkedin", 0) * 20 +
            row.get("has_website", 0) * 15 +
            row.get("content_readiness", 0) * 0.3
        ))
        
        # Budget Capacity Score (0-100)
        budget_capacity = min(100, (
            row.get("location_affluence", 0) * 8 +
            row.get("city_tier", 0) * 10 +
            row.get("budget_indicator", 0) * 0.5 +
            maturity * 0.3
        ))
        
        # Recommended Tier (1-4)
        if budget_capacity >= 75 and marketing_readiness >= 70:
            tier = 3  # Scale pack
        elif budget_capacity >= 50 and marketing_readiness >= 50:
            tier = 2  # Growth pack
        elif budget_capacity >= 30:
            tier = 1  # Launch pack
        else:
            tier = 0  # Not ready
        
        return {
            "maturity": float(maturity),
            "marketing_readiness": float(marketing_readiness),
            "budget_capacity": float(budget_capacity),
            "recommended_tier": int(tier)
        }
    
    def _load_models(self) -> Dict:
        """Load trained models from disk."""
        models = {}
        
        model_files = {
            "xgboost": "xgboost_v1.pkl",
            "random_forest": "rf_v1.pkl",
            "linear": "linear_v1.pkl"
        }
        
        for model_name, filename in model_files.items():
            filepath = os.path.join(self.models_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        models[model_name] = pickle.load(f)
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.warning(f"Error loading {model_name}: {e}")
            else:
                logger.warning(f"Model file not found: {filepath}")
        
        return models
