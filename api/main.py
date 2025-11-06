"""
FastAPI application for the sports betting consensus system.
Provides REST endpoints for accessing consensus picks and statistics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from core.models import PickType
from storage.database import Database
from core.logger import logger
from config.settings import settings
from services import MatchService, PredictionService, ConsensusService


# Request/Response models
class PredictRequest(BaseModel):
    """Request model for /predict endpoint."""
    team_a: str
    team_b: str


class PredictResponse(BaseModel):
    """Response model for /predict endpoint."""
    match: dict
    prediction: dict
    recommendation: dict
    reasoning: List[str]

app = FastAPI(
    title=settings.app_name,
    description="Sports Betting Consensus System API",
    version="1.0.0"
)

# Initialize database
db = Database()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("FastAPI application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    db.close()
    logger.info("FastAPI application shutdown")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app": settings.app_name
    }


@app.post("/predict")
async def predict(request: PredictRequest):
    """
    Main prediction endpoint - accepts two teams and returns consensus prediction.

    WORKFLOW:
    1. Validate teams
    2. Get match information
    3. Scrape predictions from websites
    4. Calculate consensus
    5. Generate recommendations
    6. Return results

    REQUEST:
    {
        "team_a": "Real Madrid",
        "team_b": "Getafe"
    }

    RESPONSE:
    {
        "match": {...},
        "prediction": {...},
        "recommendation": {...},
        "reasoning": [...]
    }
    """
    try:
        # Initialize services
        match_service = MatchService()
        prediction_service = PredictionService()
        consensus_service = ConsensusService()

        # Validate teams
        is_valid, error = match_service.validate_teams(request.team_a, request.team_b)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        # Get match info
        match_info = match_service.get_match_info(request.team_a, request.team_b)

        # Scrape predictions
        predictions = prediction_service.scrape_predictions(request.team_a, request.team_b)

        if not predictions:
            raise HTTPException(status_code=500, detail="Failed to scrape predictions")

        # Calculate consensus
        consensus_picks = consensus_service.calculate_consensus(predictions)

        if not consensus_picks:
            raise HTTPException(status_code=500, detail="Failed to calculate consensus")

        best_pick = consensus_service.get_best_pick(consensus_picks)

        # Format results
        results = consensus_service.format_results(
            request.team_a, request.team_b, best_pick, predictions, match_info
        )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predict endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/consensus/picks")
async def get_consensus_picks(
    limit: int = 50,
    min_score: float = 0.0,
    pick_type: Optional[str] = None
):
    """
    Get consensus picks.
    
    Args:
        limit: Maximum number of picks to return
        min_score: Minimum consensus score threshold
        pick_type: Filter by pick type (spread, moneyline, over_under, prop)
        
    Returns:
        List of consensus picks
    """
    try:
        picks = db.get_recent_consensus_picks(limit=limit * 2)  # Get extra to filter
        
        # Filter by score
        picks = [p for p in picks if p.consensus_score >= min_score]
        
        # Filter by type if specified
        if pick_type:
            try:
                pt = PickType(pick_type.lower())
                picks = [p for p in picks if p.pick_type == pt]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid pick type: {pick_type}")
        
        # Limit results
        picks = picks[:limit]
        
        return {
            "count": len(picks),
            "picks": [p.to_dict() for p in picks],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error retrieving consensus picks: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving picks")


@app.get("/api/consensus/picks/top")
async def get_top_picks(limit: int = 10):
    """
    Get top consensus picks by score.
    
    Args:
        limit: Number of top picks to return
        
    Returns:
        List of top consensus picks
    """
    try:
        picks = db.get_recent_consensus_picks(limit=limit)
        
        return {
            "count": len(picks),
            "picks": [p.to_dict() for p in picks],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error retrieving top picks: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving picks")


@app.get("/api/consensus/statistics")
async def get_statistics():
    """
    Get statistics about consensus picks.
    
    Returns:
        Statistics dictionary
    """
    try:
        picks = db.get_recent_consensus_picks(limit=1000)
        
        if not picks:
            return {
                "total_picks": 0,
                "average_consensus_score": 0.0,
                "average_frequency": 0.0,
                "picks_by_type": {},
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate statistics
        scores = [p.consensus_score for p in picks]
        frequencies = [p.frequency for p in picks]
        
        stats = {
            "total_picks": len(picks),
            "average_consensus_score": sum(scores) / len(scores),
            "max_consensus_score": max(scores),
            "min_consensus_score": min(scores),
            "average_frequency": sum(frequencies) / len(frequencies),
            "max_frequency": max(frequencies),
            "picks_by_type": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Count by type
        for pick in picks:
            pick_type = pick.pick_type.value
            if pick_type not in stats["picks_by_type"]:
                stats["picks_by_type"][pick_type] = 0
            stats["picks_by_type"][pick_type] += 1
        
        return stats
    
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(status_code=500, detail="Error calculating statistics")


@app.get("/api/consensus/picks/by-type/{pick_type}")
async def get_picks_by_type(pick_type: str, limit: int = 50):
    """
    Get consensus picks filtered by type.
    
    Args:
        pick_type: Type of picks (spread, moneyline, over_under, prop)
        limit: Maximum number of picks to return
        
    Returns:
        List of picks of specified type
    """
    try:
        # Validate pick type
        try:
            pt = PickType(pick_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid pick type: {pick_type}")
        
        picks = db.get_recent_consensus_picks(limit=limit * 2)
        picks = [p for p in picks if p.pick_type == pt][:limit]
        
        return {
            "pick_type": pick_type,
            "count": len(picks),
            "picks": [p.to_dict() for p in picks],
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving picks by type: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving picks")


@app.get("/api/config")
async def get_config():
    """
    Get application configuration.
    
    Returns:
        Configuration dictionary
    """
    return {
        "app_name": settings.app_name,
        "enabled_sources": settings.enabled_sources,
        "scheduler_enabled": settings.scheduler_enabled,
        "scheduler_interval_hours": settings.scheduler_interval_hours,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )

