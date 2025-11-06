"""
Base scraper class providing common functionality for all scrapers.
Handles article fetching, parsing, and error handling.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup
from core.models import Article
from core.http_client import RateLimitedHTTPClient
from core.logger import logger


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self, source_name: str):
        """
        Initialize the scraper.
        
        Args:
            source_name: Name of the source (e.g., 'espn', 'bleacher_report')
        """
        self.source_name = source_name
        self.http_client = RateLimitedHTTPClient()
        logger.info(f"Initialized scraper for source: {source_name}")
    
    @abstractmethod
    def get_urls(self) -> List[str]:
        """
        Get list of URLs to scrape.
        Must be implemented by subclasses.
        
        Returns:
            List of URLs to fetch
        """
        pass
    
    @abstractmethod
    def parse_article(self, html: str, url: str) -> Optional[Article]:
        """
        Parse HTML content and extract article information.
        Must be implemented by subclasses.
        
        Args:
            html: HTML content of the page
            url: URL of the article
            
        Returns:
            Article object or None if parsing failed
        """
        pass
    
    def fetch_articles(self) -> List[Article]:
        """
        Fetch and parse articles from the source.
        
        Returns:
            List of Article objects
        """
        articles = []
        urls = self.get_urls()
        
        logger.info(f"Fetching {len(urls)} URLs from {self.source_name}")
        
        for url in urls:
            try:
                response = self.http_client.get(url)
                if response is None:
                    logger.warning(f"Failed to fetch {url}")
                    continue
                
                article = self.parse_article(response.text, url)
                if article is not None:
                    articles.append(article)
                    logger.debug(f"Successfully parsed article: {article.title}")
                else:
                    logger.warning(f"Failed to parse article from {url}")
            
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(articles)} articles from {self.source_name}")
        return articles
    
    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html: HTML content
            
        Returns:
            BeautifulSoup object or None if parsing failed
        """
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return None
    
    def close(self):
        """Clean up resources."""
        self.http_client.close()
        logger.debug(f"Closed scraper for {self.source_name}")

