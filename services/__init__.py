"""
Services layer - Business logic orchestration for the soccer betting system.

This package contains service classes that orchestrate the core business logic:
- MatchService: Handles match validation and information retrieval
- PredictionService: Handles scraping and prediction extraction
- ConsensusService: Handles consensus calculation and recommendations
"""

from .match_service import MatchService
from .prediction_service import PredictionService
from .consensus_service import ConsensusService

__all__ = [
    'MatchService',
    'PredictionService',
    'ConsensusService',
]

