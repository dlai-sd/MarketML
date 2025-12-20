"""
LinkedIn scraper (public profiles only).
"""

from typing import Dict, Any, Optional
import logging
import os

from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """
    Scraper for LinkedIn public profiles.
    
    Supports multiple modes:
    1. skip - Skip LinkedIn scraping entirely
    2. basic - Use Playwright for basic public profile data
    3. proxycurl - Use Proxycurl API (requires API key and credits)
    """
    
    async def scrape(
        self,
        name: str,
        location: str,
        profile_url: Optional[str] = None,
        data_source: str = "mock",
        linkedin_mode: str = "skip",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape LinkedIn profile data.
        
        Args:
            name: Person name
            location: Location
            profile_url: Direct LinkedIn profile URL if available
            data_source: "mock", "google", or "playwright"
            linkedin_mode: "skip", "basic", or "proxycurl"
        
        Returns:
            Dictionary with profile data
        """
        logger.info(f"LinkedIn scraping for {name} (mode: {linkedin_mode})")
        
        if linkedin_mode == "skip":
            return self._get_mock_data(name, location, profile_url)
        elif linkedin_mode == "basic":
            return await self._scrape_with_playwright(name, location, profile_url)
        elif linkedin_mode == "proxycurl":
            return await self._scrape_with_proxycurl(profile_url)
        else:
            logger.warning(f"Unknown LinkedIn mode: {linkedin_mode}, using mock")
            return self._get_mock_data(name, location, profile_url)
    
    def _get_mock_data(self, name: str, location: str, profile_url: Optional[str]) -> Dict[str, Any]:
        """Return mock LinkedIn data."""
        return {
            "source": "linkedin",
            "name": name,
            "url": profile_url,
            "data": {
                "headline": None,
                "company": None,
                "title": None,
                "location": location,
                "connections": None,
                "about": None,
                "experience": [],
                "education": [],
                "skills": []
            },
            "metadata": {
                "scraped_at": None,
                "scraper_version": "0.1.0",
                "mode": "mock",
                "note": "Mock data - enable basic or proxycurl mode for real scraping"
            }
        }
    
    async def _scrape_with_playwright(
        self,
        name: str,
        location: str,
        profile_url: Optional[str]
    ) -> Dict[str, Any]:
        """Scrape using Playwright browser automation."""
        if not profile_url:
            logger.warning(f"No LinkedIn URL provided for {name}, returning mock data")
            return self._get_mock_data(name, location, None)
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                # Navigate to LinkedIn profile
                await page.goto(profile_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)  # Wait for dynamic content
                
                # Extract basic info (public profiles only)
                data = {
                    "headline": await page.locator(".text-body-medium").first.inner_text() if await page.locator(".text-body-medium").count() > 0 else None,
                    "company": None,  # Extract from headline or experience
                    "title": None,
                    "location": location,
                    "connections": None,
                    "about": None,
                    "experience": [],
                    "education": [],
                    "skills": []
                }
                
                await browser.close()
                
                return {
                    "source": "linkedin",
                    "name": name,
                    "url": profile_url,
                    "data": data,
                    "metadata": {
                        "scraper_version": "0.1.0",
                        "mode": "playwright",
                        "note": "Basic public profile scraping - limited data available"
                    }
                }
                
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
            return self._get_mock_data(name, location, profile_url)
        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            return self._get_mock_data(name, location, profile_url)
    
    async def _scrape_with_proxycurl(self, profile_url: Optional[str]) -> Dict[str, Any]:
        """Scrape using Proxycurl API."""
        if not profile_url:
            logger.warning("No LinkedIn URL provided for Proxycurl")
            return self._get_mock_data("", "", None)
        
        api_key = os.getenv("PROXYCURL_API_KEY")
        if not api_key or api_key == "your-proxycurl-key-here":
            logger.warning("Proxycurl API key not configured, using mock data")
            return self._get_mock_data("", "", profile_url)
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nubela.co/proxycurl/api/v2/linkedin",
                    params={"url": profile_url},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "source": "linkedin",
                    "name": data.get("full_name"),
                    "url": profile_url,
                    "data": {
                        "headline": data.get("headline"),
                        "company": data.get("experiences", [{}])[0].get("company") if data.get("experiences") else None,
                        "title": data.get("experiences", [{}])[0].get("title") if data.get("experiences") else None,
                        "location": data.get("city"),
                        "connections": data.get("connections"),
                        "about": data.get("summary"),
                        "experience": data.get("experiences", []),
                        "education": data.get("education", []),
                        "skills": data.get("skills", [])
                    },
                    "metadata": {
                        "scraper_version": "0.1.0",
                        "mode": "proxycurl",
                        "note": "Full profile data from Proxycurl API"
                    }
                }
                
        except Exception as e:
            logger.error(f"Proxycurl API failed: {e}")
            return self._get_mock_data("", "", profile_url)
