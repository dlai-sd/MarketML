"""Enrichment engine for adding context to extracted entities."""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
import logging
from contextlib import contextmanager
from functools import lru_cache

from app.constants import (
    ENRICHMENT_DB_LOCATIONS,
    ENRICHMENT_DB_INDUSTRIES,
    ENRICHMENT_DB_COMPETITORS,
    ENRICHMENT_DB_KEYWORDS,
    TIER_1_CITIES,
    TIER_2_CITIES
)
from app.utils.performance import timer, log_slow_queries

logger = logging.getLogger(__name__)


class EnrichmentEngine:
    """Enrich extracted data with geographic, industry, and competitive context."""
    
    def __init__(self):
        """Initialize enrichment databases."""
        # Database paths from centralized constants
        self.locations_db = ENRICHMENT_DB_LOCATIONS
        self.industries_db = ENRICHMENT_DB_INDUSTRIES
        self.competitors_db = ENRICHMENT_DB_COMPETITORS
        self.keywords_db = ENRICHMENT_DB_KEYWORDS
        
        # Ensure parent directory exists
        self.locations_db.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for frequently accessed data
        self._location_cache = {}
        self._industry_cache = {}
    
    @contextmanager
    def _get_connection(self, db_path: Path):
        """Context manager for database connections with optimizations."""
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            # Enable performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
            conn.execute("PRAGMA cache_size=10000")  # 10MB cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp
            yield conn
        finally:
            if conn:
                conn.close()
    
    def _query_db(self, db_path: Path, query: str, params: tuple = ()) -> List[tuple]:
        """Execute database query safely with connection pooling."""
        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}")
            return []
        
        try:
            with self._get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results
        except sqlite3.Error as e:
            logger.error(f"Database query error on {db_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying {db_path}: {e}")
            return []
    
    async def enrich(self, entities: Dict[str, Any], location: str) -> Dict[str, Any]:
        """
        Enrich extracted entities with context.
        
        Args:
            entities: Extracted entities
            location: Primary location
        
        Returns:
            Enriched data dictionary
        """
        logger.info(f"Enriching data for location: {location}")
        
        enriched = {
            "entities": entities,
            "location_context": self._enrich_location(location),
            "industry_context": self._enrich_industry(entities),
            "competitive_context": self._enrich_competitive(entities, location),
            "temporal_attributes": self._compute_temporal_attributes(entities)
        }
        
        return enriched
    
    def _enrich_location(self, location: str) -> Dict[str, Any]:
        """Enrich location with demographic and economic data."""
        # Parse location (city, state)
        parts = [p.strip() for p in location.split(',')]
        city = parts[0] if parts else location
        state = parts[1] if len(parts) > 1 else None
        
        # Query database
        results = self._query_db(
            self.locations_db,
            "SELECT state, tier, population, affluence_score, digital_penetration, business_density, avg_income FROM cities WHERE name = ?",
            (city,)
        )
        
        if results:
            row = results[0]
            tier_map = {1: "Tier-1", 2: "Tier-2", 3: "Tier-3"}
            tier = tier_map.get(row[1], "Tier-3")
            affluence_score = row[3] / 10.0  # Convert to 0-10 scale
            
            return {
                "city": city,
                "state": row[0],
                "country": "India",
                "affluence_score": affluence_score,
                "tier": tier,
                "market_context": self._generate_market_context(city, affluence_score),
                "population_estimate": row[2],
                "business_density": row[5],
                "digital_penetration": row[4],
                "avg_income": row[6]
            }
        else:
            # Fallback for unknown cities
            affluence_score = self._estimate_affluence_score(city)
            return {
                "city": city,
                "state": state,
                "country": "India",
                "affluence_score": affluence_score,
                "tier": self._classify_city_tier(city),
                "market_context": self._generate_market_context(city, affluence_score),
                "population_estimate": None,
                "business_density": None,
                "digital_penetration": None,
                "avg_income": None
            }
    
    def _enrich_industry(self, entities: Dict) -> Dict[str, Any]:
        """Enrich with industry-specific context."""
        # Get keywords for matching
        keywords = entities.get("keywords", [])
        keywords_lower = " ".join(keywords).lower()
        
        # Get all industries with their keywords
        industries_results = self._query_db(
            self.industries_db,
            "SELECT name, market_size_cr, growth_rate, digital_maturity, avg_budget_lakhs, common_keywords FROM industries"
        )
        
        # Find best matching industry
        best_match = None
        best_score = 0
        
        for row in industries_results:
            industry_keywords = row[5].split(",")
            match_score = sum(1 for kw in industry_keywords if kw in keywords_lower)
            if match_score > best_score:
                best_score = match_score
                best_match = row
        
        if best_match:
            return {
                "industry": best_match[0],
                "market_size_inr": best_match[1],
                "growth_rate": best_match[2],
                "digital_maturity": best_match[3],
                "avg_budget_lakhs": best_match[4],
                "competitive_intensity": self._calculate_competitive_intensity(best_match[0])
            }
        else:
            return {
                "industry": "General",
                "market_size_inr": 50000,
                "growth_rate": 10.0,
                "digital_maturity": 70,
                "avg_budget_lakhs": 15,
                "competitive_intensity": "Medium"
            }
    
    def _enrich_competitive(self, entities: Dict, location: str) -> Dict[str, Any]:
        """Enrich with competitive intelligence."""
        industry_context = self._enrich_industry(entities)
        industry = industry_context.get("industry", "General")
        
        # Query competitor database
        competitors = self._query_db(
            self.competitors_db,
            "SELECT company_name, tier, market_share FROM competitors WHERE industry = ?",
            (industry,)
        )
        
        # Calculate competitive metrics
        competitor_count = len(competitors) * 10 if competitors else 5
        competitor_names = [row[0] for row in competitors[:3]] if competitors else []
        
        return {
            "estimated_competitors": competitor_count,
            "market_position": "Challenger" if competitor_count > 10 else "Niche",
            "major_competitors": competitor_names,
            "differentiation_opportunities": self._generate_differentiation_opportunities(industry)
        }
    
    def _calculate_competitive_intensity(self, industry: str) -> str:
        """Calculate competitive intensity for an industry."""
        competitors = self._query_db(
            self.competitors_db,
            "SELECT COUNT(*) FROM competitors WHERE industry = ?",
            (industry,)
        )
        
        count = competitors[0][0] if competitors else 0
        
        if count > 8:
            return "High"
        elif count > 4:
            return "Medium"
        else:
            return "Low"
    
    def _generate_differentiation_opportunities(self, industry: str) -> List[str]:
        """Generate differentiation opportunities based on industry."""
        opportunities = {
            "Technology": [
                "Niche specialization",
                "Superior customer service",
                "Local market expertise"
            ],
            "Retail": [
                "Omnichannel presence",
                "Personalized service",
                "Sustainable practices"
            ],
            "default": [
                "Digital transformation",
                "Customer experience focus",
                "Value-added services"
            ]
        }
        
        return opportunities.get(industry, opportunities["default"])
    
    def _compute_temporal_attributes(self, entities: Dict) -> List[Dict[str, Any]]:
        """Compute 10 temporal attributes as requested."""
        experience = entities.get("experience", [])
        education = entities.get("education", [])
        
        attributes = [
            {
                "attribute": "years_of_experience",
                "value": len(experience),
                "confidence": 0.7 if experience else 0.3
            },
            {
                "attribute": "education_level",
                "value": len(education),
                "confidence": 0.8 if education else 0.3
            },
            {
                "attribute": "skill_count",
                "value": len(entities.get("skills", [])),
                "confidence": 0.6
            },
            {
                "attribute": "digital_footprint",
                "value": len(entities.get("social_profiles", {})),
                "confidence": 0.7
            },
            {
                "attribute": "professional_connections",
                "value": 0,
                "confidence": 0.3
            },
            {
                "attribute": "content_activity",
                "value": 0,
                "confidence": 0.3
            },
            {
                "attribute": "company_count",
                "value": len(set(entities.get("organizations", []))),
                "confidence": 0.6
            },
            {
                "attribute": "location_changes",
                "value": len(set(entities.get("locations", []))),
                "confidence": 0.5
            },
            {
                "attribute": "recent_activity_score",
                "value": 50,
                "confidence": 0.4
            },
            {
                "attribute": "profile_completeness",
                "value": self._calculate_completeness(entities),
                "confidence": 0.9
            }
        ]
        
        return attributes
    
    def _estimate_affluence_score(self, city: str) -> float:
        """Estimate affluence score (0-10) based on city."""
        tier1_cities = ["mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "pune", "kolkata"]
        tier2_cities = ["ahmedabad", "surat", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "bhopal"]
        
        city_lower = city.lower()
        
        if any(t1 in city_lower for t1 in tier1_cities):
            return 7.5
        elif any(t2 in city_lower for t2 in tier2_cities):
            return 6.0
        else:
            return 5.0
    
    def _classify_city_tier(self, city: str) -> str:
        """Classify city as Tier 1, 2, or 3."""
        affluence = self._estimate_affluence_score(city)
        if affluence >= 7:
            return "Tier-1"
        elif affluence >= 5.5:
            return "Tier-2"
        else:
            return "Tier-3"
    
    def _generate_market_context(self, city: str, affluence_score: float) -> str:
        """Generate natural language market context."""
        tier = self._classify_city_tier(city)
        
        if affluence_score >= 7:
            return f"{tier} metropolitan area with high purchasing power and strong digital adoption"
        elif affluence_score >= 6:
            return f"{tier} city with growing middle class and increasing business opportunities"
        else:
            return f"{tier} market with emerging digital presence and development potential"
    
    def _calculate_completeness(self, entities: Dict) -> float:
        """Calculate profile completeness score (0-100)."""
        score = 0
        
        if entities.get("organizations"):
            score += 20
        if entities.get("titles"):
            score += 20
        if entities.get("locations"):
            score += 10
        if entities.get("skills"):
            score += 15
        if entities.get("contact", {}).get("emails"):
            score += 15
        if entities.get("social_profiles"):
            score += 10
        if entities.get("experience"):
            score += 10
        
        return min(score, 100.0)
