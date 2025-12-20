"""Enhanced company website scraper with better parsing."""

import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper


class CompanyScraper(BaseScraper):
    """Scrape company website information."""
    
    async def scrape(self, name: str, location: str = "", description: str = "") -> Dict[str, Any]:
        """Scrape company website."""
        # Try to find company website
        website_url = await self._find_company_website(name)
        
        if not website_url:
            return {
                "success": False,
                "error": "Could not find company website"
            }
        
        # Scrape website content
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                await page.goto(website_url, wait_until="domcontentloaded", timeout=15000)
                content = await page.content()
                
                await browser.close()
            
            # Parse content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract structured data
            data = {
                "url": website_url,
                "title": soup.title.string if soup.title else "",
                "description": self._extract_description(soup),
                "services": self._extract_services(soup),
                "contact": self._extract_contact(soup),
                "social_media": self._extract_social_links(soup),
                "technologies": self._detect_technologies(soup),
                "business_signals": self._extract_business_signals(content)
            }
            
            return {
                "success": True,
                "data": data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _find_company_website(self, name: str) -> Optional[str]:
        """Try to find company website URL."""
        # Common patterns
        name_slug = name.lower().replace(" ", "").replace(".", "")
        possible_urls = [
            f"https://www.{name_slug}.com",
            f"https://www.{name_slug}.in",
            f"https://{name_slug}.com",
            f"https://{name_slug}.in",
        ]
        
        # Try each URL
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                for url in possible_urls:
                    try:
                        response = await page.goto(url, wait_until="domcontentloaded", timeout=5000)
                        if response and response.status == 200:
                            await browser.close()
                            return url
                    except:
                        continue
                
                await browser.close()
        except:
            pass
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract company description."""
        # Try meta description
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        
        # Try og:description
        og_desc = soup.find("meta", {"property": "og:description"})
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        # Try first paragraph
        first_p = soup.find("p")
        if first_p:
            return first_p.get_text()[:200]
        
        return ""
    
    def _extract_services(self, soup: BeautifulSoup) -> list:
        """Extract services/products."""
        services = []
        
        # Look for service sections
        keywords = ["service", "product", "solution", "offering"]
        for keyword in keywords:
            sections = soup.find_all(class_=re.compile(keyword, re.I))
            for section in sections[:5]:
                text = section.get_text().strip()
                if len(text) < 100:
                    services.append(text)
        
        return list(set(services))[:5]
    
    def _extract_contact(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact["email"] = emails[0]
        
        # Phone pattern (Indian)
        phone_pattern = r'(\+91[\s-]?)?[6-9]\d{9}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact["phone"] = phones[0]
        
        return contact
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links."""
        social = {}
        
        social_patterns = {
            "linkedin": r'linkedin\.com/company/[\w-]+',
            "facebook": r'facebook\.com/[\w-]+',
            "twitter": r'twitter\.com/[\w-]+',
            "instagram": r'instagram\.com/[\w-]+',
        }
        
        page_text = soup.get_text() + str(soup)
        
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, page_text)
            if match:
                social[platform] = match.group(0)
        
        return social
    
    def _detect_technologies(self, soup: BeautifulSoup) -> list:
        """Detect technologies used on website."""
        technologies = []
        
        # Check scripts and frameworks
        scripts = soup.find_all("script")
        for script in scripts:
            src = script.get("src", "")
            if "react" in src.lower():
                technologies.append("React")
            elif "angular" in src.lower():
                technologies.append("Angular")
            elif "vue" in src.lower():
                technologies.append("Vue.js")
            elif "jquery" in src.lower():
                technologies.append("jQuery")
        
        # Check meta tags
        generator = soup.find("meta", {"name": "generator"})
        if generator:
            technologies.append(generator.get("content", ""))
        
        return list(set(technologies))
    
    def _extract_business_signals(self, html: str) -> Dict[str, Any]:
        """Extract business maturity signals."""
        signals = {
            "has_about_page": bool(re.search(r'(about|company)', html, re.I)),
            "has_services_page": bool(re.search(r'(services|products|solutions)', html, re.I)),
            "has_contact_page": bool(re.search(r'contact', html, re.I)),
            "has_blog": bool(re.search(r'blog', html, re.I)),
            "has_testimonials": bool(re.search(r'(testimonial|review|client)', html, re.I)),
            "has_team_page": bool(re.search(r'(team|people)', html, re.I)),
            "ssl_enabled": html.startswith("https"),
            "responsive": bool(re.search(r'viewport', html)),
        }
        
        signals["maturity_score"] = sum(signals.values()) * 12.5  # 0-100 scale
        
        return signals
