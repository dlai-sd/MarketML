"""Enhanced news scraper using Google News RSS."""

import asyncio
from typing import Dict, Any, List
import feedparser
from datetime import datetime, timedelta
import re
from .base_scraper import BaseScraper


class NewsScraper(BaseScraper):
    """Scrape news articles about the company/person."""
    
    def __init__(self):
        super().__init__()
        self.google_news_rss = "https://news.google.com/rss/search"
    
    async def scrape(self, name: str, location: str = "", description: str = "") -> Dict[str, Any]:
        """Scrape news articles."""
        try:
            # Build search query
            query = self._build_search_query(name, location)
            
            # Fetch RSS feed
            feed_url = f"{self.google_news_rss}?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            # Parse feed (in separate thread to avoid blocking)
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
            
            if not feed.entries:
                return {
                    "success": False,
                    "error": "No news articles found"
                }
            
            # Process articles
            articles = []
            for entry in feed.entries[:10]:  # Limit to 10 articles
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "source": self._extract_source(entry),
                }
                articles.append(article)
            
            # Analyze articles for signals
            signals = self._analyze_articles(articles)
            
            return {
                "success": True,
                "data": {
                    "articles": articles,
                    "total_mentions": len(articles),
                    "signals": signals,
                    "date_range": self._get_date_range(articles)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_search_query(self, name: str, location: str) -> str:
        """Build Google News search query."""
        # URL encode the name
        query_parts = [name]
        
        if location:
            city = location.split(",")[0].strip()
            query_parts.append(city)
        
        # Add business-related terms
        query_parts.extend(["business", "company", "startup"])
        
        return "%20".join(query_parts)
    
    def _extract_source(self, entry: Dict) -> str:
        """Extract news source from entry."""
        if "source" in entry:
            return entry["source"].get("title", "Unknown")
        
        # Try to extract from title
        title = entry.get("title", "")
        match = re.search(r' - (.+)$', title)
        if match:
            return match.group(1)
        
        return "Unknown"
    
    def _analyze_articles(self, articles: List[Dict]) -> Dict[str, Any]:
        """Analyze articles for business signals."""
        signals = {
            "mentions_growth": 0,
            "mentions_funding": 0,
            "mentions_expansion": 0,
            "mentions_awards": 0,
            "mentions_innovation": 0,
            "sentiment_positive": 0,
            "sentiment_negative": 0,
        }
        
        # Keywords for different categories
        growth_keywords = ["growth", "expanding", "growing", "scale", "increase"]
        funding_keywords = ["funding", "investment", "raised", "capital", "investors"]
        expansion_keywords = ["expansion", "new office", "new location", "launch"]
        award_keywords = ["award", "recognition", "winner", "best", "top"]
        innovation_keywords = ["innovation", "technology", "AI", "digital", "new product"]
        
        positive_keywords = ["success", "achievement", "milestone", "breakthrough"]
        negative_keywords = ["loss", "decline", "challenge", "struggle", "shutdown"]
        
        for article in articles:
            text = (article.get("title", "") + " " + article.get("summary", "")).lower()
            
            if any(kw in text for kw in growth_keywords):
                signals["mentions_growth"] += 1
            if any(kw in text for kw in funding_keywords):
                signals["mentions_funding"] += 1
            if any(kw in text for kw in expansion_keywords):
                signals["mentions_expansion"] += 1
            if any(kw in text for kw in award_keywords):
                signals["mentions_awards"] += 1
            if any(kw in text for kw in innovation_keywords):
                signals["mentions_innovation"] += 1
            
            if any(kw in text for kw in positive_keywords):
                signals["sentiment_positive"] += 1
            if any(kw in text for kw in negative_keywords):
                signals["sentiment_negative"] += 1
        
        # Calculate overall visibility score
        signals["visibility_score"] = min(100, len(articles) * 10)
        signals["momentum_score"] = min(100, 
            (signals["mentions_growth"] * 20 +
             signals["mentions_funding"] * 25 +
             signals["mentions_expansion"] * 15 +
             signals["mentions_awards"] * 15 +
             signals["mentions_innovation"] * 20))
        
        return signals
    
    def _get_date_range(self, articles: List[Dict]) -> Dict[str, str]:
        """Get date range of articles."""
        if not articles:
            return {"earliest": None, "latest": None}
        
        dates = []
        for article in articles:
            pub_date = article.get("published", "")
            if pub_date:
                dates.append(pub_date)
        
        return {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
            "span_days": self._calculate_span(dates)
        }
    
    def _calculate_span(self, dates: List[str]) -> int:
        """Calculate span of dates in days."""
        if len(dates) < 2:
            return 0
        
        # Simple approximation
        return 30  # Placeholder
