"""
Consensus Service - Handles consensus calculation and recommendations.

SENIOR ENGINEER THOUGHT PROCESS:
This service takes all predictions from different sources and calculates
a weighted consensus score. The algorithm:

1. Groups predictions by team
2. Calculates frequency (how many sources agree)
3. Calculates average confidence
4. Applies diversity bonus (more sources = higher score)
5. Generates recommendation level based on score
6. Provides detailed reasoning

This service is responsible for:
1. Calculating consensus from predictions
2. Generating betting recommendations
3. Providing confidence levels
4. Formatting results for output
5. Providing justification for each recommendation
"""

from typing import List, Dict, Optional
from core.models import BettingPick, ConsensusPick
from consensus.analyzer import ConsensusAnalyzer
from core.logger import logger


class ConsensusService:
    """
    SERVICE: Handles consensus calculation and recommendations.

    SENIOR ENGINEER NOTES:
    - Uses weighted consensus algorithm
    - Considers source diversity
    - Provides confidence levels
    - Generates detailed reasoning

    RESPONSIBILITIES:
    - Calculate consensus from predictions
    - Generate recommendations
    - Provide confidence levels
    - Format results
    - Provide justification
    """

    # Recommendation thresholds (based on consensus score)
    # These thresholds determine the recommendation level
    STRONG_BUY_THRESHOLD = 0.85  # 85%+ agreement = STRONG BUY 🔥
    BUY_THRESHOLD = 0.70         # 70-84% agreement = BUY ⚡
    CONSIDER_THRESHOLD = 0.55    # 55-69% agreement = CONSIDER ⚠️
    # Below 55% = WEAK ❄️

    def __init__(self):
        """
        Initialize the consensus service.

        SENIOR ENGINEER THOUGHT PROCESS:
        - Initialize the consensus analyzer
        - Set minimum frequency to 1 (accept even single predictions)
        - Set up logging
        """
        logger.info("Initialized ConsensusService")
        # ConsensusAnalyzer uses weighted algorithm
        self.analyzer = ConsensusAnalyzer(min_frequency=1)
    
    def calculate_consensus(self, predictions: List[BettingPick]) -> List[ConsensusPick]:
        """
        Calculate consensus from predictions.
        
        PARAMETERS:
        - predictions (List[BettingPick]): All predictions from sources
        
        RETURNS:
        - List[ConsensusPick]: Consensus picks sorted by score
        """
        logger.info(f"Calculating consensus from {len(predictions)} predictions")
        consensus_picks = self.analyzer.analyze(predictions)
        return consensus_picks
    
    def get_best_pick(self, consensus_picks: List[ConsensusPick]) -> Optional[ConsensusPick]:
        """
        Get the best consensus pick.
        
        PARAMETERS:
        - consensus_picks (List[ConsensusPick]): All consensus picks
        
        RETURNS:
        - Optional[ConsensusPick]: Best pick or None
        """
        if not consensus_picks:
            return None
        return consensus_picks[0]  # Already sorted by score
    
    def get_recommendation(self, consensus_score: float) -> Dict:
        """
        Get recommendation level based on consensus score.
        
        PARAMETERS:
        - consensus_score (float): Consensus score (0.0-1.0)
        
        RETURNS:
        - Dict: Recommendation with level and action
        
        THRESHOLDS:
        - 0.85-1.00: STRONG BUY (🔥)
        - 0.70-0.84: BUY (⚡)
        - 0.55-0.69: CONSIDER (⚠️)
        - 0.00-0.54: WEAK (❄️)
        """
        if consensus_score >= self.STRONG_BUY_THRESHOLD:
            return {
                'level': 'STRONG BUY',
                'emoji': '🔥',
                'action': 'Place bet immediately',
                'confidence': 'Very High',
            }
        elif consensus_score >= self.BUY_THRESHOLD:
            return {
                'level': 'BUY',
                'emoji': '⚡',
                'action': 'Consider placing bet',
                'confidence': 'High',
            }
        elif consensus_score >= self.CONSIDER_THRESHOLD:
            return {
                'level': 'CONSIDER',
                'emoji': '⚠️',
                'action': 'Research further',
                'confidence': 'Moderate',
            }
        else:
            return {
                'level': 'WEAK',
                'emoji': '❄️',
                'action': 'Avoid this bet',
                'confidence': 'Low',
            }
    
    def format_results(
        self,
        team_a: str,
        team_b: str,
        best_pick: ConsensusPick,
        all_predictions: List[BettingPick],
        match_info: Dict
    ) -> Dict:
        """
        Format results for output.
        
        PARAMETERS:
        - team_a (str): First team
        - team_b (str): Second team
        - best_pick (ConsensusPick): Best consensus pick
        - all_predictions (List[BettingPick]): All predictions
        - match_info (Dict): Match information
        
        RETURNS:
        - Dict: Formatted results
        """
        recommendation = self.get_recommendation(best_pick.consensus_score)
        
        return {
            'match': {
                'team_a': team_a,
                'team_b': team_b,
                'odds': match_info.get('odds', {}),
            },
            'prediction': {
                'team': best_pick.team_or_player,
                'consensus_score': round(best_pick.consensus_score, 3),
                'votes': best_pick.frequency,
                'sources': best_pick.sources,
                'confidence': round(best_pick.average_confidence, 3),
            },
            'recommendation': recommendation,
            'all_predictions': [p.to_dict() for p in all_predictions],
            'reasoning': best_pick.reasoning_samples,
        }

