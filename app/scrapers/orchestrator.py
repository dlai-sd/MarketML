"""
Orchestrates scraping from multiple sources in parallel.
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.scrapers.base_scraper import BaseScraper
from app.core.database import ScrapedData

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """Coordinates scraping from multiple sources."""
    
    def __init__(self):
        # Import scrapers here to avoid circular imports
        from app.scrapers.linkedin_scraper import LinkedInScraper
        from app.scrapers.company_scraper import CompanyScraper
        from app.scrapers.news_scraper import NewsScraper
        
        self.scrapers = {
            "linkedin": LinkedInScraper(),
            "company": CompanyScraper(),
            "news": NewsScraper(),
            # Add more scrapers as needed
        }
    
    async def scrape_all_sources(
        self,
        name: str,
        location: str,
        confirmed_profiles: Optional[List[Dict]] = None,
        person_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Scrape all available sources in parallel.
        
        Args:
            name: Person/business name
            location: Location
            confirmed_profiles: List of confirmed profile URLs
            person_id: Person ID for tracking
            db: Database session for storing results
        
        Returns:
            Dictionary of scraped data by source
        """
        logger.info(f"Starting parallel scraping for {name}")
        
        # Create scraping tasks
        tasks = []
        source_names = []
        
        for source_name, scraper in self.scrapers.items():
            # Check if we have a confirmed profile for this source
            profile_url = None
            if confirmed_profiles:
                for profile in confirmed_profiles:
                    if profile.get("source") == source_name:
                        profile_url = profile.get("url")
                        break
            
            task = self._scrape_with_error_handling(
                scraper=scraper,
                source_name=source_name,
                name=name,
                location=location,
                profile_url=profile_url,
                person_id=person_id,
                db=db
            )
            tasks.append(task)
            source_names.append(source_name)
        
        # Run all scrapers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        scraped_data = {}
        for source_name, result in zip(source_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {source_name}: {str(result)}")
                scraped_data[source_name] = {"error": str(result), "success": False}
            else:
                scraped_data[source_name] = result
        
        success_count = sum(1 for data in scraped_data.values() if data.get("success"))
        logger.info(f"Scraping complete: {success_count}/{len(scraped_data)} sources succeeded")
        
        return scraped_data
    
    async def _scrape_with_error_handling(
        self,
        scraper: BaseScraper,
        source_name: str,
        name: str,
        location: str,
        profile_url: Optional[str],
        person_id: Optional[str],
        db: Optional[AsyncSession]
    ) -> Dict[str, Any]:
        """Scrape a single source with error handling."""
        start_time = datetime.utcnow()
        
        try:
            # Scrape data
            data = await scraper.scrape(
                name=name,
                location=location,
                profile_url=profile_url
            )
            
            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Store in database if session provided
            if db and person_id:
                scraped_record = ScrapedData(
                    person_id=person_id,
                    source=source_name,
                    url=profile_url or data.get("url"),
                    html_content=None,  # Don't store HTML to save space
                    extracted_json=data,
                    success=True,
                    scrape_duration_ms=duration_ms
                )
                db.add(scraped_record)
                await db.commit()
            
            data["success"] = True
            data["duration_ms"] = duration_ms
            return data
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {str(e)}", exc_info=True)
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Store error in database
            if db and person_id:
                scraped_record = ScrapedData(
                    person_id=person_id,
                    source=source_name,
                    url=profile_url,
                    success=False,
                    error_message=str(e),
                    scrape_duration_ms=duration_ms
                )
                db.add(scraped_record)
                await db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms
            }
