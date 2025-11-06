"""
Bleacher Report scraper for fetching sports betting picks and analysis.
Handles Bleacher Report's article structure and content extraction.
"""

from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from core.models import Article
from scrapers.base_scraper import BaseScraper
from core.logger import logger


class BleacherReportScraper(BaseScraper):
    """Scraper for Bleacher Report sports betting content."""
    
    def __init__(self):
        """Initialize Bleacher Report scraper."""
        super().__init__("bleacher_report")
        self.base_url = "https://bleacherreport.com"
        # Bleacher Report has various sections with picks
        self.picks_sections = [
            "/nfl",
            "/nba",
            "/mlb",
            "/nhl",
        ]
    
    def get_urls(self) -> List[str]:
        """
        Get Bleacher Report picks URLs.
        
        Returns:
            List of Bleacher Report URLs
        """
        urls = []
        for section in self.picks_sections:
            url = f"{self.base_url}{section}"
            urls.append(url)
            logger.debug(f"Added Bleacher Report URL: {url}")
        return urls
    
    def parse_article(self, html: str, url: str) -> Optional[Article]:
        """
        Parse Bleacher Report article HTML and extract content.
        
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
                # Try alternative selectors
                title_elem = soup.find('h2', {'class': 'article-title'})
            
            if not title_elem:
                logger.warning(f"Could not find title in BR article: {url}")
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Extract article content
            # Bleacher Report uses various content containers
            content_elem = soup.find('article')
            if not content_elem:
                content_elem = soup.find('div', {'class': 'article-content'})
            if not content_elem:
                content_elem = soup.find('div', {'class': 'article-body'})
            if not content_elem:
                content_elem = soup.find('main')
            
            if not content_elem:
                logger.warning(f"Could not find content in BR article: {url}")
                return None
            
            # Extract all text from content
            content = content_elem.get_text(separator='\n', strip=True)
            
            # Limit content length
            if len(content) > 50000:
                content = content[:50000]
            
            # Try to extract publish date
            published_at = self._extract_publish_date(soup)
            
            # Create Article object
            article = Article(
                title=title,
                url=url,
                source="bleacher_report",
                content=content,
                published_at=published_at,
                fetched_at=datetime.now(),
            )
            
            logger.debug(f"Parsed BR article: {title}")
            return article
        
        except Exception as e:
            logger.error(f"Error parsing BR article from {url}: {e}")
            return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        Extract publish date from article metadata.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            datetime object or None
        """
        try:
            # Look for time element
            time_elem = soup.find('time')
            if time_elem and time_elem.get('datetime'):
                date_str = time_elem.get('datetime')
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Look for meta tags
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date and meta_date.get('content'):
                date_str = meta_date.get('content')
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            return None
        except Exception as e:
            logger.debug(f"Could not extract publish date: {e}")
            return None

