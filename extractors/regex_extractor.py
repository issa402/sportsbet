"""
Regex-based betting pick extractor.
Uses pattern matching to identify and extract betting picks from article text.
"""

import re
from typing import List, Optional, Tuple
from core.models import Article, BettingPick, PickType, ConfidenceLevel
from extractors.base_extractor import BaseExtractor
from core.logger import logger


class RegexExtractor(BaseExtractor):
    """Extract betting picks using regex patterns."""
    
    def __init__(self):
        """Initialize regex extractor."""
        super().__init__("regex")
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for pick extraction."""
        
        # Patterns for different pick types
        self.spread_pattern = re.compile(
            r'(?:pick|take|like|favor|lean|go with|backing)\s+(?:the\s+)?'
            r'([A-Za-z\s]+?)\s+(?:at|by|-)\s*(-?\d+\.?\d*)\s*(?:points?|pts?)',
            re.IGNORECASE
        )
        
        self.moneyline_pattern = re.compile(
            r'(?:pick|take|like|favor|lean|go with|backing)\s+(?:the\s+)?'
            r'([A-Za-z\s]+?)\s+(?:to win|moneyline|straight up|ML)',
            re.IGNORECASE
        )
        
        self.over_under_pattern = re.compile(
            r'(?:take|like|go with|backing)\s+(?:the\s+)?'
            r'(over|under)\s+(?:the\s+)?(\d+\.?\d*)\s*(?:points?|pts?|total)',
            re.IGNORECASE
        )
        
        self.prop_pattern = re.compile(
            r'(?:pick|take|like|favor|lean|go with|backing)\s+'
            r'([A-Za-z\s]+?)\s+(?:to|over|under)\s+(\d+\.?\d*)\s*'
            r'(?:points?|pts?|rebounds?|assists?|yards?|touchdowns?)',
            re.IGNORECASE
        )
        
        # Confidence indicators
        self.high_confidence_pattern = re.compile(
            r'(?:lock|strong|confident|love|best|top pick|must|definitely)',
            re.IGNORECASE
        )
        
        self.low_confidence_pattern = re.compile(
            r'(?:slight|lean|small|slight edge|toss-up|could go either way)',
            re.IGNORECASE
        )
        
        # Odds patterns
        self.odds_pattern = re.compile(
            r'(?:at|odds?|@)\s*([+-]?\d+)'
        )
    
    def extract(self, article: Article) -> List[BettingPick]:
        """
        Extract picks from article using regex patterns.
        
        Args:
            article: Article to extract picks from
            
        Returns:
            List of extracted BettingPick objects
        """
        picks = []
        content = article.content
        
        # Extract spread picks
        for match in self.spread_pattern.finditer(content):
            team = match.group(1).strip()
            spread = match.group(2)
            pick = self._create_pick(
                team_or_player=team,
                pick_type=PickType.SPREAD,
                odds=spread,
                context=content[max(0, match.start()-100):match.end()+100],
                article=article
            )
            if pick:
                picks.append(pick)
        
        # Extract moneyline picks
        for match in self.moneyline_pattern.finditer(content):
            team = match.group(1).strip()
            pick = self._create_pick(
                team_or_player=team,
                pick_type=PickType.MONEYLINE,
                context=content[max(0, match.start()-100):match.end()+100],
                article=article
            )
            if pick:
                picks.append(pick)
        
        # Extract over/under picks
        for match in self.over_under_pattern.finditer(content):
            ou_type = match.group(1).upper()
            total = match.group(2)
            team_or_player = f"{ou_type} {total}"
            pick = self._create_pick(
                team_or_player=team_or_player,
                pick_type=PickType.OVER_UNDER,
                odds=total,
                context=content[max(0, match.start()-100):match.end()+100],
                article=article
            )
            if pick:
                picks.append(pick)
        
        # Extract prop picks
        for match in self.prop_pattern.finditer(content):
            player = match.group(1).strip()
            line = match.group(2)
            pick = self._create_pick(
                team_or_player=player,
                pick_type=PickType.PROP,
                odds=line,
                context=content[max(0, match.start()-100):match.end()+100],
                article=article
            )
            if pick:
                picks.append(pick)
        
        logger.debug(f"Regex extractor found {len(picks)} picks in article: {article.title}")
        return picks
    
    def _create_pick(
        self,
        team_or_player: str,
        pick_type: PickType,
        context: str,
        article: Article,
        odds: Optional[str] = None
    ) -> Optional[BettingPick]:
        """
        Create a BettingPick object with confidence scoring.
        
        Args:
            team_or_player: Team or player name
            pick_type: Type of pick
            context: Context around the pick
            article: Source article
            odds: Optional odds information
            
        Returns:
            BettingPick object or None if invalid
        """
        if not team_or_player or len(team_or_player) < 2:
            return None
        
        # Determine confidence level from context
        confidence = self._determine_confidence(context)
        
        # Extract odds if not provided
        if not odds:
            odds_match = self.odds_pattern.search(context)
            if odds_match:
                odds = odds_match.group(1)
        
        pick = BettingPick(
            team_or_player=team_or_player,
            pick_type=pick_type,
            confidence=confidence,
            odds=odds,
            reasoning=context.strip()[:200],  # First 200 chars of context
            source=article.source,
            article_id=article.article_id,
        )
        
        return pick
    
    def _determine_confidence(self, context: str) -> ConfidenceLevel:
        """
        Determine confidence level from context text.
        
        Args:
            context: Context around the pick
            
        Returns:
            ConfidenceLevel enum value
        """
        if self.high_confidence_pattern.search(context):
            return ConfidenceLevel.HIGH
        elif self.low_confidence_pattern.search(context):
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.MEDIUM

