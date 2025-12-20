"""
Base scraper class with rate limiting, retries, and caching.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers with common functionality."""
    
    def __init__(self):
        self.timeout = settings.scraper_timeout
        self.max_retries = settings.scraper_max_retries
        self.rate_limit = settings.scraper_rate_limit  # requests per second
        self.last_request_time = 0
        
        # HTTP client configuration
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    async def _rate_limit_wait(self):
        """Implement rate limiting."""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _fetch_url(self, url: str, **kwargs) -> Optional[str]:
        """
        Fetch URL with retries and error handling.
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments for httpx.get()
        
        Returns:
            HTML content or None if failed
        """
        await self._rate_limit_wait()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.text
                
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """Parse HTML content."""
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return None
    
    @abstractmethod
    async def scrape(self, **kwargs) -> Dict[str, Any]:
        """
        Scrape data from source.
        Must be implemented by subclasses.
        
        Returns:
            Dictionary with scraped data
        """
        pass
    
    def _clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters (optional - keep for now)
        # text = re.sub(r'[^\w\s\-.,]', '', text)
        
        return text.strip()
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract common metadata from HTML."""
        metadata = {}
        
        # OpenGraph tags
        for tag in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            key = tag.get("property", "").replace("og:", "")
            value = tag.get("content")
            if key and value:
                metadata[f"og_{key}"] = value
        
        # Twitter Card tags
        for tag in soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")}):
            key = tag.get("name", "").replace("twitter:", "")
            value = tag.get("content")
            if key and value:
                metadata[f"twitter_{key}"] = value
        
        # Title and description
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = self._clean_text(title_tag.text)
        
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            metadata["description"] = self._clean_text(desc_tag.get("content", ""))
        
        return metadata
