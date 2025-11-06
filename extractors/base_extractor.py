"""
Base extractor class for betting pick extraction.
Provides common functionality for all extraction methods.
"""

from abc import ABC, abstractmethod
from typing import List
from core.models import Article, BettingPick
from core.logger import logger


class BaseExtractor(ABC):
    """Abstract base class for all extractors."""
    
    def __init__(self, name: str):
        """
        Initialize the extractor.
        
        Args:
            name: Name of the extractor (e.g., 'regex', 'llm')
        """
        self.name = name
        logger.info(f"Initialized extractor: {name}")
    
    @abstractmethod
    def extract(self, article: Article) -> List[BettingPick]:
        """
        Extract betting picks from an article.
        Must be implemented by subclasses.
        
        Args:
            article: Article object to extract picks from
            
        Returns:
            List of BettingPick objects
        """
        pass
    
    def extract_batch(self, articles: List[Article]) -> List[BettingPick]:
        """
        Extract picks from multiple articles.
        
        Args:
            articles: List of Article objects
            
        Returns:
            List of all extracted BettingPick objects
        """
        all_picks = []
        
        for article in articles:
            try:
                picks = self.extract(article)
                all_picks.extend(picks)
                logger.debug(f"Extracted {len(picks)} picks from article: {article.title}")
            except Exception as e:
                logger.error(f"Error extracting picks from article {article.title}: {e}")
                continue
        
        logger.info(f"Extracted {len(all_picks)} total picks from {len(articles)} articles")
        return all_picks

