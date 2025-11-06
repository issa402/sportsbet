"""
================================================================================
CONSENSUS ANALYSIS ENGINE
================================================================================

This module analyzes betting picks from multiple sources to identify consensus
recommendations. It:

1. GROUPS picks by team/player and pick type
2. CALCULATES consensus metrics (frequency, confidence, diversity)
3. RANKS picks by consensus strength
4. FILTERS picks by score thresholds
5. GENERATES statistics about consensus picks

CONSENSUS ALGORITHM:
    consensus_score = (frequency / num_sources) × average_confidence × diversity_bonus

    Where:
    - frequency = how many sources recommended this pick (1, 2, 3, 4, 5+)
    - num_sources = total number of sources
    - average_confidence = mean confidence level (0.0-1.0)
    - diversity_bonus = bonus for picks from multiple different sources (0.7-1.0)

EXAMPLE:
    If 4 out of 5 sources say "Lakers -5.5" with high confidence:
    - frequency = 4
    - num_sources = 4
    - average_confidence = 0.9
    - diversity_bonus = 1.0 (4 different sources)
    - consensus_score = (4/4) × 0.9 × 1.0 = 0.90 (EXCELLENT)

WHEN TO USE:
- Use ConsensusAnalyzer.analyze() to find consensus picks from raw picks
- Use get_top_picks() to get the best consensus recommendations
- Use get_statistics() to understand consensus distribution
================================================================================
"""

# Import required modules
from typing import List, Dict, Tuple  # Type hints for function signatures
from collections import Counter  # For counting occurrences
from core.models import BettingPick, ConsensusPick, PickType, ConfidenceLevel  # Data models
from core.logger import logger  # Logging for debugging and monitoring

# Optional pandas import for statistics (graceful degradation if not available)
try:
    import pandas as pd  # Data analysis library
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class ConsensusAnalyzer:
    """
    CLASS: Analyzes betting picks to find consensus recommendations.

    WHY USE THIS:
    - Aggregates picks from multiple sources
    - Identifies picks with strong agreement
    - Ranks picks by consensus strength
    - Filters out low-confidence picks

    ATTRIBUTES:
    - min_frequency: Minimum sources required for a pick to be included

    USAGE EXAMPLE:
        analyzer = ConsensusAnalyzer(min_frequency=2)  # Need at least 2 sources
        consensus_picks = analyzer.analyze(all_picks)
        top_picks = analyzer.get_top_picks(consensus_picks, limit=10)
    """

    def __init__(self, min_frequency: int = 1):
        """
        CONSTRUCTOR: Initialize the consensus analyzer.

        WHY USE THIS:
        - Sets up the analyzer with configuration
        - Logs initialization for debugging

        PARAMETERS:
        - min_frequency (int): Minimum number of sources required for a pick
          to be included in consensus analysis. Default is 1 (all picks).
          Set to 2 or higher to filter out single-source picks.

        USAGE EXAMPLE:
            # Only include picks from 2+ sources
            analyzer = ConsensusAnalyzer(min_frequency=2)

            # Include all picks (even single-source)
            analyzer = ConsensusAnalyzer(min_frequency=1)
        """
        # Store the minimum frequency threshold
        self.min_frequency = min_frequency

        # Log initialization for debugging
        logger.info(f"Initialized ConsensusAnalyzer (min_frequency={min_frequency})")
    
    def analyze(self, picks: List[BettingPick]) -> List[ConsensusPick]:
        """
        METHOD: Analyze picks and generate consensus recommendations.

        WHAT IT DOES:
        1. Groups picks by team/player and pick type
        2. Calculates consensus metrics for each group
        3. Filters by minimum frequency threshold
        4. Sorts by consensus score (highest first)
        5. Returns ranked consensus picks

        PARAMETERS:
        - picks (List[BettingPick]): All picks extracted from articles

        RETURNS:
        - List[ConsensusPick]: Consensus picks sorted by score (descending)

        USAGE EXAMPLE:
            all_picks = [pick1, pick2, pick3, ...]  # From multiple sources
            analyzer = ConsensusAnalyzer(min_frequency=2)
            consensus_picks = analyzer.analyze(all_picks)

            # consensus_picks now contains aggregated picks with scores
            for pick in consensus_picks:
                print(f"{pick.team_or_player}: {pick.consensus_score}")
        """
        # STEP 1: Validate input - check if we have any picks to analyze
        if not picks:
            # Log warning if no picks provided
            logger.warning("No picks provided for analysis")
            # Return empty list if nothing to analyze
            return []

        # STEP 2: Log analysis start with summary info
        # Count unique sources to understand data diversity
        unique_sources = len(set(p.source for p in picks))
        logger.info(f"Analyzing {len(picks)} picks from {unique_sources} sources")

        # STEP 3: Group picks by team/player and pick type
        # This combines picks for the same bet from different sources
        grouped_picks = self._group_picks(picks)

        # STEP 4: Calculate consensus for each group
        consensus_picks = []
        for (team_or_player, pick_type), group_picks in grouped_picks.items():
            # Only include picks that meet minimum frequency threshold
            if len(group_picks) >= self.min_frequency:
                # Calculate consensus metrics for this group
                consensus = self._calculate_consensus(team_or_player, pick_type, group_picks)
                # Add to results
                consensus_picks.append(consensus)

        # STEP 5: Sort by consensus score (highest first)
        # This puts the most agreed-upon picks at the top
        consensus_picks.sort(key=lambda x: x.consensus_score, reverse=True)

        # STEP 6: Log completion
        logger.info(f"Generated {len(consensus_picks)} consensus picks")

        # Return sorted consensus picks
        return consensus_picks
    
    def _group_picks(self, picks: List[BettingPick]) -> Dict[Tuple[str, PickType], List[BettingPick]]:
        """
        PRIVATE METHOD: Group picks by team/player and pick type.

        WHY THIS IS NEEDED:
        - Different sources may use different capitalization ("Lakers" vs "lakers")
        - We need to combine picks for the same bet from different sources
        - Grouping allows us to calculate consensus for each unique pick

        WHAT IT DOES:
        1. Normalizes team/player names (lowercase, strip whitespace)
        2. Creates a key combining normalized name and pick type
        3. Groups all picks with the same key together

        PARAMETERS:
        - picks (List[BettingPick]): All picks to group

        RETURNS:
        - Dict: Maps (team_or_player, pick_type) to list of picks

        EXAMPLE:
            Input picks:
            - Pick 1: "Lakers" (spread) from ESPN
            - Pick 2: "lakers" (spread) from Bleacher Report
            - Pick 3: "Lakers" (moneyline) from The Athletic

            Output:
            {
                ("lakers", PickType.SPREAD): [Pick1, Pick2],
                ("lakers", PickType.MONEYLINE): [Pick3]
            }
        """
        # Initialize empty dictionary to store grouped picks
        grouped = {}

        # STEP 1: Iterate through each pick
        for pick in picks:
            # STEP 2: Normalize the team/player name
            # - strip() removes leading/trailing whitespace
            # - lower() converts to lowercase for case-insensitive matching
            # This ensures "Lakers", "LAKERS", and "lakers" are treated as the same
            normalized_name = pick.team_or_player.strip().lower()

            # STEP 3: Create a unique key for this pick
            # Key = (normalized_name, pick_type)
            # Example: ("lakers", PickType.SPREAD)
            key = (normalized_name, pick.pick_type)

            # STEP 4: Initialize list for this key if it doesn't exist
            if key not in grouped:
                grouped[key] = []

            # STEP 5: Add this pick to the group
            grouped[key].append(pick)

        # STEP 6: Log grouping results for debugging
        logger.debug(f"Grouped {len(picks)} picks into {len(grouped)} groups")

        # Return the grouped picks
        return grouped
    
    def _calculate_consensus(
        self,
        team_or_player: str,
        pick_type: PickType,
        picks: List[BettingPick]
    ) -> ConsensusPick:
        """
        PRIVATE METHOD: Calculate consensus metrics for a group of picks.

        THIS IS THE CORE ALGORITHM - It calculates how strong the consensus is
        for a particular pick based on:
        1. How many sources recommend it (frequency)
        2. How confident those sources are (average confidence)
        3. How diverse the sources are (source diversity bonus)

        CONSENSUS SCORE FORMULA:
            consensus_score = (frequency / num_sources) × average_confidence × diversity_bonus

        WHERE:
        - frequency = number of sources recommending this pick
        - num_sources = total number of unique sources
        - average_confidence = mean confidence level (0.0-1.0)
        - diversity_bonus = bonus for picks from multiple sources (0.7-1.0)

        EXAMPLE CALCULATION:
            If 4 out of 5 sources say "Lakers -5.5" with high confidence:
            - frequency = 4
            - num_sources = 4
            - average_confidence = 0.9
            - diversity_bonus = min(4/3, 1.0) = 1.0
            - consensus_score = (4/4) × 0.9 × (0.7 + 0.3×1.0) = 0.90

        PARAMETERS:
        - team_or_player (str): Team or player name
        - pick_type (PickType): Type of pick (spread, moneyline, etc.)
        - picks (List[BettingPick]): All picks for this team/player/type

        RETURNS:
        - ConsensusPick: Object with calculated consensus metrics
        """

        # ====================================================================
        # STEP 1: CALCULATE FREQUENCY
        # ====================================================================
        # Frequency = how many sources recommended this pick
        # Higher frequency = more sources agree = stronger consensus
        frequency = len(picks)
        # Example: If 4 sources say "Lakers -5.5", frequency = 4

        # ====================================================================
        # STEP 2: GET UNIQUE SOURCES
        # ====================================================================
        # Extract unique source names from the picks
        # set() removes duplicates (in case same source appears multiple times)
        # list() converts back to list for storage
        sources = list(set(p.source for p in picks if p.source))
        # Example: ["ESPN", "Bleacher Report", "The Athletic", "Vegas Insider"]

        # ====================================================================
        # STEP 3: CALCULATE AVERAGE CONFIDENCE
        # ====================================================================
        # Convert confidence levels (HIGH, MEDIUM, LOW) to numeric scores
        confidence_scores = self._confidence_to_score(picks)
        # Calculate the mean confidence across all sources
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        # Example: If 3 sources are HIGH (0.9) and 1 is MEDIUM (0.6):
        #          average = (0.9 + 0.9 + 0.9 + 0.6) / 4 = 0.825

        # ====================================================================
        # STEP 4: CALCULATE SOURCE DIVERSITY BONUS
        # ====================================================================
        # Bonus for picks from multiple different sources
        # Formula: min(num_sources / 3.0, 1.0)
        # - If 1 source: bonus = min(1/3, 1.0) = 0.33
        # - If 2 sources: bonus = min(2/3, 1.0) = 0.67
        # - If 3+ sources: bonus = min(3+/3, 1.0) = 1.0
        source_diversity_bonus = min(len(sources) / 3.0, 1.0)
        # This rewards picks that appear across multiple sources

        # ====================================================================
        # STEP 5: CALCULATE CONSENSUS SCORE
        # ====================================================================
        # Main formula: (frequency / num_sources) × average_confidence × diversity_bonus
        #
        # Breaking it down:
        # - (frequency / num_sources): How many sources agree (0.0-1.0)
        # - average_confidence: How confident those sources are (0.0-1.0)
        # - (0.7 + 0.3 × diversity_bonus): Baseline 0.7 + bonus up to 0.3
        #
        # Example: 4 out of 4 sources, high confidence, 4 different sources:
        #   = (4/4) × 0.9 × (0.7 + 0.3×1.0)
        #   = 1.0 × 0.9 × 1.0
        #   = 0.90 (EXCELLENT)
        consensus_score = (frequency / max(len(sources), 1)) * average_confidence * (0.7 + 0.3 * source_diversity_bonus)
        # max(len(sources), 1) prevents division by zero

        # ====================================================================
        # STEP 6: COLLECT REASONING SAMPLES
        # ====================================================================
        # Gather the reasoning from each source (up to 5 samples)
        # This shows WHY each source made this pick
        reasoning_samples = [
            p.reasoning for p in picks  # Extract reasoning from each pick
            if p.reasoning  # Only include picks that have reasoning
        ][:5]  # Limit to top 5 samples
        # Example: [
        #   "Lakers dominant at home",
        #   "Easy cover for Lakers",
        #   "Lakers are the better team"
        # ]

        # ====================================================================
        # STEP 7: CREATE AND RETURN CONSENSUS PICK
        # ====================================================================
        # Create a ConsensusPick object with all calculated metrics
        consensus = ConsensusPick(
            team_or_player=team_or_player,  # e.g., "Lakers"
            pick_type=pick_type,  # e.g., PickType.SPREAD
            frequency=frequency,  # e.g., 4 (4 sources)
            average_confidence=average_confidence,  # e.g., 0.825
            consensus_score=consensus_score,  # e.g., 0.90
            sources=sources,  # e.g., ["ESPN", "Bleacher Report", ...]
            reasoning_samples=reasoning_samples,  # e.g., ["Lakers dominant...", ...]
        )

        # Return the consensus pick
        return consensus
    
    def _confidence_to_score(self, picks: List[BettingPick]) -> List[float]:
        """
        PRIVATE METHOD: Convert confidence levels to numeric scores.

        WHY THIS IS NEEDED:
        - Confidence levels are text (HIGH, MEDIUM, LOW)
        - We need numeric scores to calculate averages
        - Different confidence levels should have different weights

        CONFIDENCE MAPPING:
        - HIGH (e.g., "lock", "strong", "love"): 0.9 (90% weight)
        - MEDIUM (default): 0.6 (60% weight)
        - LOW (e.g., "slight", "lean", "toss-up"): 0.3 (30% weight)
        - UNKNOWN (couldn't determine): 0.5 (50% weight)

        PARAMETERS:
        - picks (List[BettingPick]): Picks to convert

        RETURNS:
        - List[float]: Numeric confidence scores (0.0-1.0)

        USAGE EXAMPLE:
            picks = [
                BettingPick(..., confidence=ConfidenceLevel.HIGH),
                BettingPick(..., confidence=ConfidenceLevel.MEDIUM),
                BettingPick(..., confidence=ConfidenceLevel.LOW),
            ]
            scores = analyzer._confidence_to_score(picks)
            # Returns: [0.9, 0.6, 0.3]
            # Average: 0.6
        """
        # Initialize empty list to store scores
        scores = []

        # STEP 1: Iterate through each pick
        for pick in picks:
            # STEP 2: Convert confidence level to numeric score
            if pick.confidence == ConfidenceLevel.HIGH:
                # HIGH confidence: 0.9 (90%)
                # Used when expert is very confident (e.g., "lock of the day")
                scores.append(0.9)
            elif pick.confidence == ConfidenceLevel.MEDIUM:
                # MEDIUM confidence: 0.6 (60%)
                # Default confidence level
                scores.append(0.6)
            elif pick.confidence == ConfidenceLevel.LOW:
                # LOW confidence: 0.3 (30%)
                # Used when expert has low confidence (e.g., "slight lean")
                scores.append(0.3)
            else:  # UNKNOWN
                # UNKNOWN confidence: 0.5 (50%)
                # Used when confidence couldn't be determined
                scores.append(0.5)

        # Return list of numeric scores
        return scores
    
    def get_top_picks(
        self,
        consensus_picks: List[ConsensusPick],
        limit: int = 10,
        min_consensus_score: float = 0.0
    ) -> List[ConsensusPick]:
        """
        PUBLIC METHOD: Get top consensus picks filtered by score threshold.

        WHY USE THIS:
        - Filters out low-confidence picks
        - Limits results to top N picks
        - Helps focus on the best recommendations

        PARAMETERS:
        - consensus_picks (List[ConsensusPick]): All consensus picks
        - limit (int): Maximum number of picks to return (default: 10)
        - min_consensus_score (float): Minimum score threshold (default: 0.0)

        RETURNS:
        - List[ConsensusPick]: Top picks sorted by score, filtered and limited

        USAGE EXAMPLE:
            # Get top 10 picks with score >= 0.7
            top_picks = analyzer.get_top_picks(
                consensus_picks,
                limit=10,
                min_consensus_score=0.7
            )

            # Get top 5 picks (any score)
            top_5 = analyzer.get_top_picks(consensus_picks, limit=5)
        """
        # STEP 1: Filter picks by minimum score threshold
        # Only include picks with consensus_score >= min_consensus_score
        filtered = [
            p for p in consensus_picks
            if p.consensus_score >= min_consensus_score
        ]

        # STEP 2: Limit to top N picks
        # Return only the first 'limit' picks (already sorted by score)
        return filtered[:limit]

    def get_picks_by_type(
        self,
        consensus_picks: List[ConsensusPick],
        pick_type: PickType
    ) -> List[ConsensusPick]:
        """
        PUBLIC METHOD: Filter consensus picks by type.

        WHY USE THIS:
        - Get only specific types of picks (e.g., only spreads)
        - Useful for different betting strategies
        - Helps organize picks by category

        PARAMETERS:
        - consensus_picks (List[ConsensusPick]): All consensus picks
        - pick_type (PickType): Type to filter by (SPREAD, MONEYLINE, etc.)

        RETURNS:
        - List[ConsensusPick]: Picks matching the specified type

        USAGE EXAMPLE:
            # Get only spread picks
            spread_picks = analyzer.get_picks_by_type(
                consensus_picks,
                PickType.SPREAD
            )

            # Get only moneyline picks
            ml_picks = analyzer.get_picks_by_type(
                consensus_picks,
                PickType.MONEYLINE
            )
        """
        # Filter picks where pick_type matches the requested type
        return [p for p in consensus_picks if p.pick_type == pick_type]
    
    def get_statistics(self, consensus_picks: List[ConsensusPick]) -> Dict:
        """
        PUBLIC METHOD: Calculate statistics about consensus picks.

        WHY USE THIS:
        - Understand the overall quality of consensus picks
        - See distribution of scores and frequencies
        - Identify trends in the data
        - Monitor system health

        WHAT IT CALCULATES:
        - total_picks: How many consensus picks were generated
        - average_consensus_score: Mean consensus score (0.0-1.0)
        - average_frequency: Mean number of sources per pick
        - max_frequency: Highest number of sources for any pick
        - picks_by_type: Count of picks by type (spread, moneyline, etc.)
        - average_sources_per_pick: Mean number of sources per pick

        PARAMETERS:
        - consensus_picks (List[ConsensusPick]): All consensus picks

        RETURNS:
        - Dict: Dictionary with statistics

        USAGE EXAMPLE:
            stats = analyzer.get_statistics(consensus_picks)
            print(f"Total picks: {stats['total_picks']}")
            print(f"Average score: {stats['average_consensus_score']:.3f}")
            print(f"Picks by type: {stats['picks_by_type']}")
        """

        # STEP 1: Handle empty input
        if not consensus_picks:
            # Return default stats if no picks
            return {
                'total_picks': 0,
                'average_consensus_score': 0.0,
                'average_frequency': 0.0,
                'picks_by_type': {},
            }

        # STEP 2: Extract numeric values for calculations
        # Extract consensus scores from all picks
        scores = [p.consensus_score for p in consensus_picks]
        # Extract frequencies (how many sources per pick)
        frequencies = [p.frequency for p in consensus_picks]
        # Extract source counts (how many unique sources per pick)
        source_counts = [len(p.sources) for p in consensus_picks]

        # STEP 3: Count picks by type
        # Create a dictionary to count picks by type
        picks_by_type = {}
        for pick in consensus_picks:
            # Get the pick type as a string (e.g., "spread", "moneyline")
            pick_type = pick.pick_type.value
            # Increment count for this type (or initialize to 1)
            picks_by_type[pick_type] = picks_by_type.get(pick_type, 0) + 1

        # STEP 4: Calculate statistics
        stats = {
            # Total number of consensus picks
            'total_picks': len(consensus_picks),

            # Average consensus score (0.0-1.0)
            # Shows overall quality of consensus
            'average_consensus_score': sum(scores) / len(scores) if scores else 0.0,

            # Average frequency (how many sources per pick on average)
            # Higher = more agreement across sources
            'average_frequency': sum(frequencies) / len(frequencies) if frequencies else 0.0,

            # Maximum frequency (most sources for any single pick)
            # Shows the strongest consensus
            'max_frequency': max(frequencies) if frequencies else 0,

            # Count of picks by type
            # Shows distribution across pick types
            'picks_by_type': picks_by_type,

            # Average number of sources per pick
            # Shows source diversity
            'average_sources_per_pick': sum(source_counts) / len(source_counts) if source_counts else 0.0,
        }

        # Return statistics dictionary
        return stats

