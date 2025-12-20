"""
Entity extraction using spaCy NER and custom rules.
"""

from typing import Dict, Any, List
import logging
import spacy
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract structured entities from scraped data."""
    
    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("SpaCy model loaded successfully")
        except OSError:
            logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
            raise
    
    async def extract_from_scraped_data(self, scraped_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Extract entities from all scraped sources.
        
        Args:
            scraped_data: Dictionary of scraped data by source
        
        Returns:
            Dictionary of extracted entities
        """
        logger.info("Extracting entities from scraped data")
        
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "titles": [],
            "skills": [],
            "dates": [],
            "contact": {
                "emails": [],
                "phones": []
            },
            "social_profiles": {},
            "experience": [],
            "education": []
        }
        
        # Extract from each source
        for source_name, source_data in scraped_data.items():
            if not source_data.get("success"):
                continue
            
            data = source_data.get("data", {})
            
            if source_name == "linkedin":
                self._extract_from_linkedin(data, entities)
            elif source_name == "company":
                self._extract_from_company(data, entities)
            elif source_name == "news":
                self._extract_from_news(data, entities)
        
        # Deduplicate and normalize
        entities = self._deduplicate_entities(entities)
        
        logger.info(f"Extracted {len(entities['persons'])} persons, {len(entities['organizations'])} orgs")
        
        return entities
    
    def _extract_from_linkedin(self, data: Dict, entities: Dict):
        """Extract entities from LinkedIn data."""
        if data.get("headline"):
            entities["titles"].append(data["headline"])
        
        if data.get("company"):
            entities["organizations"].append(data["company"])
        
        if data.get("location"):
            entities["locations"].append(data["location"])
        
        if data.get("skills"):
            entities["skills"].extend(data["skills"])
        
        if data.get("experience"):
            entities["experience"].extend(data["experience"])
        
        if data.get("education"):
            entities["education"].extend(data["education"])
    
    def _extract_from_company(self, data: Dict, entities: Dict):
        """Extract entities from company website data."""
        if data.get("emails"):
            entities["contact"]["emails"].extend(data["emails"])
        
        if data.get("phones"):
            entities["contact"]["phones"].extend(data["phones"])
        
        if data.get("social_links"):
            entities["social_profiles"].update(data["social_links"])
        
        # Use spaCy for about text
        if data.get("about"):
            doc = self.nlp(data["about"][:5000])  # Limit text length
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
                elif ent.label_ == "ORG":
                    entities["organizations"].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities["locations"].append(ent.text)
                elif ent.label_ == "DATE":
                    entities["dates"].append(ent.text)
    
    def _extract_from_news(self, data: Dict, entities: Dict):
        """Extract entities from news articles."""
        articles = data.get("articles", [])
        
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            
            text = f"{title}. {description}"
            if text:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        entities["persons"].append(ent.text)
                    elif ent.label_ == "ORG":
                        entities["organizations"].append(ent.text)
    
    def _deduplicate_entities(self, entities: Dict) -> Dict:
        """Remove duplicates and normalize entities."""
        for key in ["persons", "organizations", "locations", "titles", "skills", "dates"]:
            if key in entities and isinstance(entities[key], list):
                # Remove duplicates while preserving order
                seen = set()
                unique = []
                for item in entities[key]:
                    item_lower = item.lower() if isinstance(item, str) else str(item)
                    if item_lower not in seen:
                        seen.add(item_lower)
                        unique.append(item)
                entities[key] = unique
        
        # Deduplicate contact info
        entities["contact"]["emails"] = list(set(entities["contact"]["emails"]))
        entities["contact"]["phones"] = list(set(entities["contact"]["phones"]))
        
        return entities
