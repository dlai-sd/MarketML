"""Google search scraper for basic business information."""

import asyncio
from typing import Dict, Any, List
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper


class GoogleSearchScraper(BaseScraper):
    """Scrape Google search results for business information."""
    
    async def scrape(self, name: str, location: str = "", description: str = "") -> Dict[str, Any]:
        """Scrape Google search results."""
        try:
            # Build search query
            query = f"{name} {location} business".strip()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                content = await page.content()
                
                await browser.close()
            
            # Parse results
            soup = BeautifulSoup(content, 'html.parser')
            
            data = {
                "search_results": self._extract_search_results(soup),
                "knowledge_panel": self._extract_knowledge_panel(soup),
                "featured_snippet": self._extract_featured_snippet(soup),
                "related_searches": self._extract_related_searches(soup),
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
    
    def _extract_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract organic search results."""
        results = []
        
        # Find search result divs
        search_divs = soup.find_all("div", class_=re.compile("g"))
        
        for div in search_divs[:5]:  # Top 5 results
            title_elem = div.find("h3")
            link_elem = div.find("a")
            snippet_elem = div.find("div", class_=re.compile("VwiC3b"))
            
            if title_elem and link_elem:
                results.append({
                    "title": title_elem.get_text(),
                    "link": link_elem.get("href", ""),
                    "snippet": snippet_elem.get_text() if snippet_elem else ""
                })
        
        return results
    
    def _extract_knowledge_panel(self, soup: BeautifulSoup) -> Dict:
        """Extract knowledge panel information if available."""
        panel = soup.find("div", class_=re.compile("knowledge"))
        
        if not panel:
            return {}
        
        return {
            "found": True,
            "type": "business"
        }
    
    def _extract_featured_snippet(self, soup: BeautifulSoup) -> str:
        """Extract featured snippet if available."""
        snippet = soup.find("div", class_=re.compile("featured"))
        return snippet.get_text() if snippet else ""
    
    def _extract_related_searches(self, soup: BeautifulSoup) -> List[str]:
        """Extract related search terms."""
        related = []
        
        related_section = soup.find_all("div", class_=re.compile("related"))
        for section in related_section:
            links = section.find_all("a")
            for link in links[:5]:
                related.append(link.get_text())
        
        return related
