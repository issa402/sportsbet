"""
================================================================================
DATA MODELS FOR SPORTS BETTING CONSENSUS SYSTEM
================================================================================

This module defines the core data structures used throughout the system:
1. PickType - Enum for different types of betting picks
2. ConfidenceLevel - Enum for confidence levels of picks
3. BettingPick - Individual pick extracted from an article
4. Article - Sports betting article containing picks
5. ConsensusPick - Aggregated pick across multiple sources

These models use Python's @dataclass decorator for clean, efficient data
structures with automatic __init__, __repr__, and other methods.

WHEN TO USE:
- Use BettingPick when extracting individual picks from articles
- Use Article when storing fetched articles with their picks
- Use ConsensusPick when analyzing and ranking picks across sources
- Use PickType and ConfidenceLevel enums to ensure type safety
================================================================================
"""

# Import required modules for data structures and type hints
from dataclasses import dataclass, field  # @dataclass decorator for clean classes
from datetime import datetime  # For timestamp tracking
from typing import Optional, List  # Type hints for better code clarity
from enum import Enum  # For creating enumeration types


# ============================================================================
# ENUMERATIONS - Define fixed sets of valid values
# ============================================================================

class PickType(str, Enum):
    """
    ENUM: Defines all valid types of betting picks.

    WHY USE THIS:
    - Prevents typos and invalid pick types
    - Provides autocomplete in IDEs
    - Makes code self-documenting
    - Enables type checking

    VALID VALUES:
    - SPREAD: Point spread bet (e.g., "Lakers -5.5")
    - MONEYLINE: Win/loss bet (e.g., "Lakers to win")
    - OVER_UNDER: Total points bet (e.g., "Over 220.5")
    - PROP: Player/game prop bet (e.g., "LeBron over 25 points")
    - PARLAY: Multiple bets combined (e.g., "Lakers -5.5 AND Over 220")
    - UNKNOWN: Pick type couldn't be determined

    USAGE EXAMPLE:
        pick_type = PickType.SPREAD  # Type-safe, won't accept invalid values
        if pick_type == PickType.MONEYLINE:
            print("This is a moneyline pick")
    """
    SPREAD = "spread"
    MONEYLINE = "moneyline"
    OVER_UNDER = "over_under"
    PROP = "prop"
    PARLAY = "parlay"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """
    ENUM: Defines confidence levels for betting picks.

    WHY USE THIS:
    - Standardizes how we represent confidence
    - Prevents invalid confidence values
    - Makes confidence levels comparable

    VALID VALUES:
    - HIGH: Expert is very confident (e.g., "lock of the day")
    - MEDIUM: Expert is moderately confident (default)
    - LOW: Expert has low confidence (e.g., "slight lean")
    - UNKNOWN: Confidence couldn't be determined

    USAGE EXAMPLE:
        confidence = ConfidenceLevel.HIGH
        if confidence == ConfidenceLevel.HIGH:
            weight_in_consensus = 0.9  # High confidence picks weighted more
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


# ============================================================================
# DATA CLASSES - Define data structures with automatic methods
# ============================================================================

@dataclass
class BettingPick:
    """
    DATACLASS: Represents a single betting pick extracted from an article.

    WHY USE THIS:
    - Automatically generates __init__, __repr__, __eq__ methods
    - Type-safe: enforces correct data types
    - Clean, readable code
    - Easy to convert to/from JSON

    ATTRIBUTES:
    - team_or_player (str): The team or player being picked (e.g., "Lakers", "LeBron")
    - pick_type (PickType): Type of pick (spread, moneyline, etc.)
    - confidence (ConfidenceLevel): How confident the expert is
    - odds (Optional[str]): The betting odds (e.g., "-110", "+150")
    - reasoning (Optional[str]): Why the expert made this pick
    - source (Optional[str]): Which source recommended this pick (e.g., "ESPN")
    - article_id (Optional[str]): ID of the article this pick came from
    - extracted_at (datetime): When this pick was extracted

    USAGE EXAMPLE:
        pick = BettingPick(
            team_or_player="Lakers",
            pick_type=PickType.SPREAD,
            confidence=ConfidenceLevel.HIGH,
            odds="-5.5",
            reasoning="Lakers dominant at home",
            source="ESPN"
        )
    """

    # REQUIRED FIELDS - Must be provided when creating a BettingPick
    team_or_player: str  # The team or player being picked
    pick_type: PickType  # Type of bet (spread, moneyline, etc.)
    confidence: ConfidenceLevel  # How confident the expert is

    # OPTIONAL FIELDS - Can be None if not available
    odds: Optional[str] = None  # Betting odds (e.g., "-110")
    reasoning: Optional[str] = None  # Expert's reasoning for the pick
    source: Optional[str] = None  # Which source made this pick
    article_id: Optional[str] = None  # ID of source article

    # AUTOMATIC FIELDS - Set automatically when created
    extracted_at: datetime = field(default_factory=datetime.now)  # Timestamp

    def to_dict(self):
        """
        METHOD: Convert BettingPick to dictionary for JSON serialization.

        WHY USE THIS:
        - Converts dataclass to JSON-serializable format
        - Handles datetime conversion to ISO format
        - Extracts enum values as strings

        RETURNS:
        - Dictionary with all pick data

        USAGE EXAMPLE:
            pick = BettingPick(...)
            pick_dict = pick.to_dict()
            json_string = json.dumps(pick_dict)  # Now JSON-serializable
        """
        return {
            'team_or_player': self.team_or_player,
            'pick_type': self.pick_type.value,  # Convert enum to string
            'confidence': self.confidence.value,  # Convert enum to string
            'odds': self.odds,
            'reasoning': self.reasoning,
            'source': self.source,
            'article_id': self.article_id,
            'extracted_at': self.extracted_at.isoformat(),  # Convert datetime to ISO string
        }


@dataclass
class Article:
    """
    DATACLASS: Represents a sports betting article.

    WHY USE THIS:
    - Stores article metadata and associated picks
    - Tracks when article was fetched
    - Maintains relationship between articles and picks

    ATTRIBUTES:
    - title (str): Article headline
    - url (str): URL to the article
    - source (str): Which website published it (e.g., "ESPN")
    - content (str): Full article text
    - published_at (Optional[datetime]): When article was published
    - fetched_at (datetime): When we downloaded it
    - picks (List[BettingPick]): Picks extracted from this article
    - article_id (Optional[str]): Unique identifier for this article

    USAGE EXAMPLE:
        article = Article(
            title="Expert Picks for Today",
            url="https://espn.com/picks",
            source="ESPN",
            content="Full article text here...",
            picks=[pick1, pick2, pick3]
        )
    """

    # REQUIRED FIELDS
    title: str  # Article headline
    url: str  # URL to the article
    source: str  # Source website (ESPN, Bleacher Report, etc.)
    content: str  # Full article text for extraction

    # OPTIONAL FIELDS
    published_at: Optional[datetime] = None  # When article was published

    # AUTOMATIC FIELDS
    fetched_at: datetime = field(default_factory=datetime.now)  # When we fetched it
    picks: List[BettingPick] = field(default_factory=list)  # Picks from this article
    article_id: Optional[str] = None  # Unique ID for this article

    def to_dict(self):
        """
        METHOD: Convert Article to dictionary for JSON serialization.

        WHY USE THIS:
        - Converts article and all its picks to JSON-serializable format
        - Handles nested BettingPick objects
        - Converts all datetimes to ISO format

        RETURNS:
        - Dictionary with article data and all picks

        USAGE EXAMPLE:
            article = Article(...)
            article_dict = article.to_dict()
            json_string = json.dumps(article_dict)
        """
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'content': self.content,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'fetched_at': self.fetched_at.isoformat(),
            'picks': [p.to_dict() for p in self.picks],  # Convert each pick to dict
            'article_id': self.article_id,
        }


@dataclass
class ConsensusPick:
    """
    DATACLASS: Represents a consensus pick across multiple sources.

    WHY USE THIS:
    - Aggregates picks from multiple sources
    - Calculates consensus strength
    - Ranks picks by agreement level
    - Provides reasoning from multiple sources

    ATTRIBUTES:
    - team_or_player (str): The team or player being picked
    - pick_type (PickType): Type of pick
    - frequency (int): How many sources recommended this pick (1-5+)
    - average_confidence (float): Average confidence across sources (0.0-1.0)
    - consensus_score (float): Overall consensus strength (0.0-1.0)
    - sources (List[str]): Which sources recommended this pick
    - reasoning_samples (List[str]): Sample reasoning from each source
    - calculated_at (datetime): When consensus was calculated

    USAGE EXAMPLE:
        consensus_pick = ConsensusPick(
            team_or_player="Lakers",
            pick_type=PickType.SPREAD,
            frequency=4,  # 4 out of 5 sources
            average_confidence=0.85,
            consensus_score=0.92,
            sources=["ESPN", "Bleacher Report", "The Athletic", "Vegas Insider"],
            reasoning_samples=[
                "Lakers dominant at home",
                "Easy cover for Lakers",
                "Lakers are the better team"
            ]
        )
    """

    # REQUIRED FIELDS
    team_or_player: str  # The team or player being picked
    pick_type: PickType  # Type of pick (spread, moneyline, etc.)
    frequency: int  # Number of sources recommending this pick (1, 2, 3, 4, 5+)
    average_confidence: float  # Average confidence (0.0 = low, 1.0 = high)
    consensus_score: float  # Overall consensus strength (0.0 = weak, 1.0 = strong)

    # OPTIONAL FIELDS WITH DEFAULTS
    sources: List[str] = field(default_factory=list)  # List of source names
    reasoning_samples: List[str] = field(default_factory=list)  # Sample reasoning

    # AUTOMATIC FIELDS
    calculated_at: datetime = field(default_factory=datetime.now)  # When calculated

    def to_dict(self):
        """
        METHOD: Convert ConsensusPick to dictionary for JSON serialization.

        WHY USE THIS:
        - Converts consensus pick to JSON-serializable format
        - Rounds scores to 3 decimal places for readability
        - Limits reasoning samples to top 3
        - Converts datetime to ISO format

        RETURNS:
        - Dictionary with consensus pick data

        USAGE EXAMPLE:
            consensus = ConsensusPick(...)
            consensus_dict = consensus.to_dict()
            json_string = json.dumps(consensus_dict)
        """
        return {
            'team_or_player': self.team_or_player,
            'pick_type': self.pick_type.value,  # Convert enum to string
            'frequency': self.frequency,  # Number of sources
            'average_confidence': round(self.average_confidence, 3),  # Round to 3 decimals
            'consensus_score': round(self.consensus_score, 3),  # Round to 3 decimals
            'sources': self.sources,  # List of source names
            'reasoning_samples': self.reasoning_samples[:3],  # Top 3 reasoning samples
            'calculated_at': self.calculated_at.isoformat(),  # Convert to ISO string
        }

