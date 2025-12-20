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
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape company website if available.
        
        Args:
            name: Company/person name
            location: Location
            profile_url: Direct website URL if available
        
        Returns:
            Dictionary with website data
        """
        logger.info(f"Scraping company website for {name}")
        
        # Try to find company website
        website_url = profile_url or await self._find_company_website(name, location)
        
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
    
    async def _find_company_website(self, name: str, location: str) -> Optional[str]:
        """Try to find company website using Google search."""
        # TODO: Implement Google search to find website
        # For now, return None
        logger.warning(f"Website discovery not implemented for {name}")
        return None
    
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
