"""
Services layer - Business logic orchestration for the soccer betting system.

This package contains service classes that orchestrate the core business logic:
- MatchService: Handles match validation and information retrieval
- ConsensusService: Handles consensus calculation and recommendations
"""

from .match_service import MatchService
from .consensus_service import ConsensusService

__all__ = [
    'MatchService',
    'ConsensusService',
]

