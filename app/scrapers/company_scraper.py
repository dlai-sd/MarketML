"""
Company website scraper.
"""

from typing import Dict, Any, Optional
import logging
import re

from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CompanyScraper(BaseScraper):
    """Scraper for company websites."""
    
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
        Scrape company website if available.
        
        Args:
            name: Company/person name
            location: Location
            profile_url: Direct website URL if available
            data_source: "mock", "google", or "playwright"
        
        Returns:
            Dictionary with website data
        """
        logger.info(f"Scraping company website for {name} (source: {data_source})")
        
        # Try to find company website
        if data_source == "google":
            website_url = profile_url or await self._find_company_website_google(name, location)
        elif data_source == "playwright":
            website_url = profile_url or await self._find_company_website_playwright(name, location)
        else:
            # Mock mode - no website discovery
            website_url = profile_url
        
        if not website_url:
            return {
                "source": "company",
                "name": name,
                "url": None,
                "data": {},
                "success": False,
                "error": "No website found"
            }
        
        # Fetch website content
        html = await self._fetch_url(website_url)
        if not html:
            return {
                "source": "company",
                "name": name,
                "url": website_url,
                "data": {},
                "success": False,
                "error": "Failed to fetch website"
            }
        
        # Parse website
        soup = self._parse_html(html)
        if not soup:
            return {
                "source": "company",
                "name": name,
                "url": website_url,
                "data": {},
                "success": False,
                "error": "Failed to parse HTML"
            }
        
        # Extract data
        metadata = self._extract_metadata(soup)
        
        # Extract contact information
        emails = self._extract_emails(soup)
        phones = self._extract_phones(soup)
        
        # Extract business information
        about_text = self._extract_about_section(soup)
        
        return {
            "source": "company",
            "name": name,
            "url": website_url,
            "data": {
                "title": metadata.get("title"),
                "description": metadata.get("description"),
                "about": about_text,
                "emails": emails,
                "phones": phones,
                "social_links": self._extract_social_links(soup)
            },
            "success": True
        }
    
    async def _find_company_website_google(self, name: str, location: str) -> Optional[str]:
        """Find company website using Google search."""
        try:
            from googlesearch import search
            
            # Search query
            query = f"{name} {location} website"
            logger.info(f"Searching Google for: {query}")
            
            # Get first result
            results = search(query, num_results=5, lang="en")
            for url in results:
                # Filter out social media and directory sites
                if not any(x in url.lower() for x in ['linkedin', 'facebook', 'twitter', 'instagram', 'justdial']):
                    logger.info(f"Found company website: {url}")
                    return url
            
            logger.warning(f"No suitable website found for {name}")
            return None
            
        except ImportError:
            logger.error("googlesearch-python not installed")
            return None
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return None
    
    async def _find_company_website_playwright(self, name: str, location: str) -> Optional[str]:
        """Find company website using Playwright (Google search with JS rendering)."""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Search on Google
                query = f"{name} {location} website"
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                
                await page.goto(search_url)
                await page.wait_for_timeout(2000)
                
                # Extract first few search results
                links = await page.query_selector_all("a")
                for link in links[:10]:
                    href = await link.get_attribute("href")
                    if href and href.startswith("http") and not any(x in href for x in ['google.com', 'linkedin', 'facebook']):
                        await browser.close()
                        logger.info(f"Found company website via Playwright: {href}")
                        return href
                
                await browser.close()
                return None
                
        except Exception as e:
            logger.error(f"Playwright website discovery failed: {e}")
            return None
    
    async def _find_company_website(self, name: str, location: str) -> Optional[str]:
        """Try to find company website using Google search (deprecated - use _find_company_website_google)."""
        return await self._find_company_website_google(name, location)
    
    def _extract_emails(self, soup) -> list:
        """Extract email addresses from page."""
        emails = set()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Search in text
        text = soup.get_text()
        found_emails = re.findall(email_pattern, text)
        emails.update(found_emails)
        
        # Search in mailto links
        for link in soup.find_all('a', href=re.compile(r'^mailto:')):
            email = link.get('href').replace('mailto:', '').split('?')[0]
            emails.add(email)
        
        return list(emails)
    
    def _extract_phones(self, soup) -> list:
        """Extract phone numbers from page."""
        phones = set()
        # Indian phone number patterns
        phone_patterns = [
            r'\+91[-\s]?\d{10}',
            r'0\d{2,4}[-\s]?\d{6,8}',
            r'\d{10}',
        ]
        
        text = soup.get_text()
        for pattern in phone_patterns:
            found_phones = re.findall(pattern, text)
            phones.update(found_phones)
        
        return list(phones)[:5]  # Limit to 5
    
    def _extract_about_section(self, soup) -> Optional[str]:
        """Extract about/description section from website."""
        # Look for common about section identifiers
        about_keywords = ['about', 'who-we-are', 'our-story', 'company']
        
        for keyword in about_keywords:
            # Try to find section by ID or class
            section = soup.find(['section', 'div'], id=re.compile(keyword, re.I))
            if not section:
                section = soup.find(['section', 'div'], class_=re.compile(keyword, re.I))
            
            if section:
                return self._clean_text(section.get_text())
        
        return None
    
    def _extract_social_links(self, soup) -> Dict[str, str]:
        """Extract social media links."""
        social_links = {}
        social_patterns = {
            'linkedin': r'linkedin\.com',
            'facebook': r'facebook\.com',
            'twitter': r'twitter\.com|x\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com'
        }
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    social_links[platform] = href
                    break
        
        return social_links
