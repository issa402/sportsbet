"""
LLM-based betting pick extractor using Claude API.
Uses natural language understanding for accurate pick extraction.
"""

import json
from typing import List, Optional
from anthropic import Anthropic
from core.models import Article, BettingPick, PickType, ConfidenceLevel
from extractors.base_extractor import BaseExtractor
from core.logger import logger
from config.settings import settings


class LLMExtractor(BaseExtractor):
    """Extract betting picks using Claude LLM."""
    
    def __init__(self):
        """Initialize LLM extractor."""
        super().__init__("llm")
        
        if not settings.claude_api_key:
            logger.warning("Claude API key not configured. LLM extraction will be disabled.")
            self.client = None
        else:
            self.client = Anthropic(api_key=settings.claude_api_key)
    
    def extract(self, article: Article) -> List[BettingPick]:
        """
        Extract picks from article using Claude LLM.
        
        Args:
            article: Article to extract picks from
            
        Returns:
            List of extracted BettingPick objects
        """
        if not self.client:
            logger.warning("LLM extractor not available (no API key)")
            return []
        
        try:
            # Limit content to avoid token limits
            content = article.content[:5000]
            
            prompt = self._build_prompt(content)
            
            logger.debug(f"Sending extraction request to Claude for: {article.title}")
            
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            response_text = response.content[0].text
            picks = self._parse_response(response_text, article)
            
            logger.debug(f"LLM extractor found {len(picks)} picks in article: {article.title}")
            return picks
        
        except Exception as e:
            logger.error(f"Error in LLM extraction for {article.title}: {e}")
            return []
    
    def _build_prompt(self, content: str) -> str:
        """
        Build the extraction prompt for Claude.
        
        Args:
            content: Article content to analyze
            
        Returns:
            Prompt string
        """
        return f"""Analyze this sports betting article and extract all betting picks/predictions.

For each pick, identify:
1. Team or Player name
2. Pick type (spread, moneyline, over_under, prop, parlay, or unknown)
3. Confidence level (high, medium, low, or unknown)
4. Odds (if mentioned)
5. Brief reasoning

Return ONLY a valid JSON array with this structure:
[
  {{
    "team_or_player": "Team/Player Name",
    "pick_type": "spread|moneyline|over_under|prop|parlay|unknown",
    "confidence": "high|medium|low|unknown",
    "odds": "optional odds string or null",
    "reasoning": "brief explanation"
  }}
]

If no picks are found, return an empty array: []

Article content:
{content}

JSON Response:"""
    
    def _parse_response(self, response_text: str, article: Article) -> List[BettingPick]:
        """
        Parse Claude's JSON response into BettingPick objects.
        
        Args:
            response_text: Claude's response text
            article: Source article
            
        Returns:
            List of BettingPick objects
        """
        picks = []
        
        try:
            # Extract JSON from response
            json_str = response_text.strip()
            
            # Try to find JSON array in response
            if '[' not in json_str:
                logger.warning("No JSON array found in LLM response")
                return picks
            
            json_start = json_str.find('[')
            json_end = json_str.rfind(']') + 1
            json_str = json_str[json_start:json_end]
            
            # Parse JSON
            picks_data = json.loads(json_str)
            
            if not isinstance(picks_data, list):
                logger.warning("LLM response is not a JSON array")
                return picks
            
            # Convert to BettingPick objects
            for pick_data in picks_data:
                try:
                    pick = self._create_pick_from_data(pick_data, article)
                    if pick:
                        picks.append(pick)
                except Exception as e:
                    logger.debug(f"Error creating pick from LLM data: {e}")
                    continue
            
            return picks
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return picks
    
    def _create_pick_from_data(self, data: dict, article: Article) -> Optional[BettingPick]:
        """
        Create a BettingPick from LLM response data.
        
        Args:
            data: Dictionary with pick data
            article: Source article
            
        Returns:
            BettingPick object or None if invalid
        """
        try:
            team_or_player = data.get('team_or_player', '').strip()
            if not team_or_player:
                return None
            
            # Parse pick type
            pick_type_str = data.get('pick_type', 'unknown').lower()
            try:
                pick_type = PickType(pick_type_str)
            except ValueError:
                pick_type = PickType.UNKNOWN
            
            # Parse confidence
            confidence_str = data.get('confidence', 'unknown').lower()
            try:
                confidence = ConfidenceLevel(confidence_str)
            except ValueError:
                confidence = ConfidenceLevel.UNKNOWN
            
            pick = BettingPick(
                team_or_player=team_or_player,
                pick_type=pick_type,
                confidence=confidence,
                odds=data.get('odds'),
                reasoning=data.get('reasoning'),
                source=article.source,
                article_id=article.article_id,
            )
            
            return pick
        
        except Exception as e:
            logger.debug(f"Error creating pick from data: {e}")
            return None

