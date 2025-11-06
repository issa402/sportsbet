"""
ESPN scraper for fetching sports betting picks and analysis.
Handles ESPN's article structure and content extraction.
"""

from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from core.models import Article
from scrapers.base_scraper import BaseScraper
from core.logger import logger


class ESPNScraper(BaseScraper):
    """Scraper for ESPN sports betting content."""
    
    def __init__(self):
        """Initialize ESPN scraper."""
        super().__init__("espn")
        self.base_url = "https://www.espn.com"
        self.picks_endpoints = [
            "/nfl/picks",
            "/nba/picks",
            "/mlb/picks",
            "/nhl/picks",
        ]
    
    def get_urls(self) -> List[str]:
        """
        Get ESPN picks page URLs.
        
        Returns:
            List of ESPN picks URLs
        """
        urls = []
        for endpoint in self.picks_endpoints:
            url = f"{self.base_url}{endpoint}"
            urls.append(url)
            logger.debug(f"Added ESPN URL: {url}")
        return urls
    
    def parse_article(self, html: str, url: str) -> Optional[Article]:
        """
        Parse ESPN article HTML and extract content.
        
        Args:
            html: HTML content
            url: Article URL
            
        Returns:
            Article object or None
        """
        soup = self._parse_html(html)
        if soup is None:
            return None
        
        try:
            # Extract article title
            title_elem = soup.find('h1')
            if not title_elem:
                title_elem = soup.find('h2')
            
            if not title_elem:
                logger.warning(f"Could not find title in ESPN article: {url}")
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Extract article content
            # ESPN typically uses article or main content containers
            content_elem = soup.find('article')
            if not content_elem:
                content_elem = soup.find('div', {'class': 'article-body'})
            if not content_elem:
                content_elem = soup.find('main')
            
            if not content_elem:
                logger.warning(f"Could not find content in ESPN article: {url}")
                return None
            
            # Extract all text from content
            content = content_elem.get_text(separator='\n', strip=True)
            
            # Limit content length to avoid processing huge articles
            if len(content) > 50000:
                content = content[:50000]
            
            # Create Article object
            article = Article(
                title=title,
                url=url,
                source="espn",
                content=content,
                published_at=None,  # ESPN doesn't always have clear publish dates
                fetched_at=datetime.now(),
            )
            
            logger.debug(f"Parsed ESPN article: {title}")
            return article
        
        except Exception as e:
            logger.error(f"Error parsing ESPN article from {url}: {e}")
            return None
    
    def _extract_picks_section(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract the picks/predictions section from the page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Text content of picks section or None
        """
        # Look for common picks section identifiers
        picks_section = soup.find('div', {'class': 'picks'})
        if picks_section:
            return picks_section.get_text(separator='\n', strip=True)
        
        picks_section = soup.find('section', {'class': 'predictions'})
        if picks_section:
            return picks_section.get_text(separator='\n', strip=True)
        
        return None

