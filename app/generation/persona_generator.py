"""
Persona generator using templates and optional LLM fallback.
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Generate persona narratives from enriched data and scores."""
    
    async def generate(
        self,
        enriched_data: Dict[str, Any],
        scores: Dict[str, float],
        name: str
    ) -> Dict[str, Any]:
        """
        Generate complete persona with structured data and narrative.
        
        Args:
            enriched_data: Enriched data from pipeline
            scores: ML model scores
            name: Person/business name
        
        Returns:
            Complete persona dictionary
        """
        logger.info(f"Generating persona for {name}")
        
        entities = enriched_data.get("entities", {})
        location_context = enriched_data.get("location_context", {})
        
        # Build structured persona
        structured = self._build_structured_persona(
            name, entities, location_context, scores
        )
        
        # Generate narratives
        narrative = self._generate_narrative(structured, enriched_data)
        short_narrative = self._generate_short_narrative(structured)
        
        # Generate insights and recommendations
        insights = self._generate_insights(structured, enriched_data, scores)
        recommendations = self._generate_recommendations(scores)
        
        # Calculate confidence
        confidence = self._calculate_confidence(enriched_data, scores)
        
        return {
            "structured": structured,
            "narrative": narrative,
            "short_narrative": short_narrative,
            "marketing_insights": insights,
            "recommended_actions": recommendations,
            "confidence_score": confidence
        }
    
    def _build_structured_persona(
        self,
        name: str,
        entities: Dict,
        location_context: Dict,
        scores: Dict
    ) -> Dict:
        """Build structured persona data."""
        # Extract key information
        title = entities.get("titles", [None])[0]
        company = entities.get("organizations", [None])[0]
        
        return {
            "name": name,
            "title": title,
            "company": company,
            "industry": None,  # TODO: Extract from enrichment
            "location": {
                "city": location_context.get("city"),
                "state": location_context.get("state"),
                "country": location_context.get("country", "India"),
                "affluence_score": location_context.get("affluence_score"),
                "market_context": location_context.get("market_context")
            },
            "business_metrics": {
                "estimated_revenue": None,  # TODO: Estimate
                "team_size": None,  # TODO: Estimate
                "years_in_business": entities.get("experience", [{}])[0].get("years") if entities.get("experience") else None,
                "growth_stage": self._classify_growth_stage(scores)
            },
            "digital_presence": {
                "linkedin_followers": None,
                "website_quality": "medium" if entities.get("contact", {}).get("emails") else "low",
                "social_activity": self._classify_social_activity(entities)
            },
            "scores": {
                "maturity": scores["maturity"],
                "marketing_readiness": scores["marketing_readiness"],
                "budget_capacity": scores["budget_capacity"],
                "recommended_tier": scores["recommended_tier"]
            }
        }
    
    def _generate_narrative(self, structured: Dict, enriched_data: Dict) -> str:
        """Generate full persona narrative (200-300 words)."""
        name = structured["name"]
        title = structured.get("title") or "business professional"
        company = structured.get("company")
        location = structured["location"]
        scores = structured["scores"]
        
        # Build narrative sections
        intro = self._generate_intro(name, title, company, location)
        location_section = self._generate_location_section(location)
        digital_section = self._generate_digital_section(scores, structured["digital_presence"])
        readiness_section = self._generate_readiness_section(scores)
        
        narrative = f"{intro}\n\n{location_section}\n\n{digital_section}\n\n{readiness_section}"
        
        return narrative.strip()
    
    def _generate_intro(self, name: str, title: str, company: str, location: Dict) -> str:
        """Generate introduction section."""
        if company and title:
            return f"{name} is a {title} at {company}, based in {location['city']}, {location['state']}."
        elif title:
            return f"{name} works as a {title}, based in {location['city']}, {location['state']}."
        elif company:
            return f"{name} is associated with {company}, based in {location['city']}, {location['state']}."
        else:
            return f"{name} is a business professional based in {location['city']}, {location['state']}."
    
    def _generate_location_section(self, location: Dict) -> str:
        """Generate location context section."""
        city = location["city"]
        market_context = location.get("market_context", "")
        affluence = location.get("affluence_score", 5.0)
        
        if affluence >= 7:
            return f"{city} is a {market_context}, making it ideal for premium product positioning and digital-first marketing strategies."
        elif affluence >= 5.5:
            return f"{city} is a {market_context}, offering strong potential for mid-market digital marketing initiatives."
        else:
            return f"{city} is a {market_context}, with emerging opportunities for cost-effective digital marketing."
    
    def _generate_digital_section(self, scores: Dict, digital_presence: Dict) -> str:
        """Generate digital presence section."""
        readiness = scores["marketing_readiness"]
        
        if readiness >= 70:
            return "The business demonstrates strong digital presence with active social media engagement and professional online profiles. This indicates readiness for advanced marketing automation and multi-channel campaigns."
        elif readiness >= 40:
            return "The business has established basic digital presence with room for growth. A structured digital marketing strategy could significantly enhance visibility and customer acquisition."
        else:
            return "The business is in early stages of digital adoption. Foundational digital marketing setup, including website optimization and social media establishment, would be beneficial."
    
    def _generate_readiness_section(self, scores: Dict) -> str:
        """Generate marketing readiness section."""
        tier = scores["recommended_tier"]
        maturity = scores["maturity"]
        budget = scores["budget_capacity"]
        
        if tier >= 3:
            return f"With a business maturity score of {maturity:.0f} and strong budget capacity, this profile is ideal for comprehensive marketing packages including advanced analytics, A/B testing, and multi-platform campaigns."
        elif tier >= 2:
            return f"With moderate maturity ({maturity:.0f}) and budget capacity ({budget:.0f}), a growth-focused marketing package with core digital channels would be most suitable."
        elif tier >= 1:
            return f"A launch package focusing on essential digital marketing foundations would be appropriate, with gradual scaling as the business grows."
        else:
            return "Building fundamental digital assets and presence would be the recommended first step before investing in comprehensive marketing campaigns."
    
    def _generate_short_narrative(self, structured: Dict) -> str:
        """Generate 15-word narrative summary."""
        name = structured["name"]
        title = structured.get("title") or "professional"
        city = structured["location"]["city"]
        tier_map = {3: "scaling", 2: "growing", 1: "emerging", 0: "early-stage"}
        stage = tier_map.get(structured["scores"]["recommended_tier"], "emerging")
        
        return f"{title} in {city}, {stage} business with digital marketing focus and growth potential"
    
    def _generate_insights(
        self,
        structured: Dict,
        enriched_data: Dict,
        scores: Dict
    ) -> list:
        """Generate marketing insights."""
        insights = []
        
        # Digital readiness insight
        if scores["marketing_readiness"] >= 70:
            insights.append("Strong digital presence indicates readiness for advanced marketing campaigns")
        
        # Location insight
        affluence = structured["location"].get("affluence_score", 5.0)
        if affluence >= 7:
            insights.append(f"{structured['location']['city']} market offers high-value customer base")
        
        # Budget insight
        if scores["budget_capacity"] >= 60:
            insights.append("Budget capacity supports comprehensive multi-channel marketing strategy")
        
        # Maturity insight
        if scores["maturity"] >= 60:
            insights.append("Business maturity level supports sustained marketing investment")
        
        # Add at least 3 insights
        if len(insights) < 3:
            insights.append("Digital marketing investment recommended to enhance market visibility")
        
        return insights[:5]  # Max 5 insights
    
    def _generate_recommendations(self, scores: Dict) -> list:
        """Generate recommended actions."""
        tier = scores["recommended_tier"]
        readiness = scores["marketing_readiness"]
        
        recommendations = []
        
        if tier >= 3:
            recommendations.append("Start with Scale Pack (₹34,999/mo) for comprehensive marketing")
            recommendations.append("Focus on LinkedIn + Google Ads + Content Marketing")
            recommendations.append("Target: 100-200 qualified leads per month")
        elif tier >= 2:
            recommendations.append("Start with Growth Pack (₹14,999/mo) for core channels")
            recommendations.append("Focus on LinkedIn + Instagram + SEO")
            recommendations.append("Target: 50-100 qualified leads per month")
        elif tier >= 1:
            recommendations.append("Start with Launch Pack (₹4,999/mo) for foundational presence")
            recommendations.append("Focus on single platform mastery (LinkedIn or Instagram)")
            recommendations.append("Target: 20-40 qualified leads per month")
        else:
            recommendations.append("Build website and basic social presence first")
            recommendations.append("Consider consultation for strategy development")
        
        return recommendations[:5]
    
    def _calculate_confidence(self, enriched_data: Dict, scores: Dict) -> float:
        """Calculate overall confidence score (0-1)."""
        entities = enriched_data.get("entities", {})
        
        # Factors contributing to confidence
        data_completeness = len([v for v in entities.values() if v]) / 10
        data_sources = min(enriched_data.get("temporal_attributes", [{}])[0].get("value", 1), 4) / 4
        score_consistency = 1.0 if max(scores.values()) - min(list(scores.values())[:3]) < 40 else 0.7
        
        confidence = (
            0.4 * data_completeness +
            0.3 * data_sources +
            0.3 * score_consistency
        )
        
        return round(min(max(confidence, 0.3), 0.95), 2)
    
    def _classify_growth_stage(self, scores: Dict) -> str:
        """Classify business growth stage."""
        maturity = scores["maturity"]
        
        if maturity >= 75:
            return "scaling"
        elif maturity >= 50:
            return "growth"
        elif maturity >= 30:
            return "early"
        else:
            return "startup"
    
    def _classify_social_activity(self, entities: Dict) -> str:
        """Classify social media activity level."""
        profiles = entities.get("social_profiles", {})
        
        if len(profiles) >= 3:
            return "high"
        elif len(profiles) >= 1:
            return "moderate"
        else:
            return "low"
