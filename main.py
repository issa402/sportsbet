#!/usr/bin/env python3
"""
Soccer Betting Consensus System - Main Entry Point

This is the main entry point for the soccer betting consensus system.
It orchestrates the entire workflow:

1. Accept user input (two teams)
2. Validate teams
3. Scrape predictions from multiple websites
4. Calculate consensus
5. Generate recommendations
6. Return results

USAGE:
    python3 main.py
    
    Then use the API at http://localhost:8000
    
    POST /predict
    {
        "team_a": "Real Madrid",
        "team_b": "Getafe"
    }
"""

import sys
import json
import os
import asyncio
from dotenv import load_dotenv
from services import MatchService, ConsensusService
from services.prediction_scraper_real import PredictionScraperReal
from services.supabase_service import SupabaseService
from core.logger import logger

# Load environment variables from .env file
load_dotenv()


async def main():
    """
    Main entry point - orchestrates the entire prediction workflow.

    WORKFLOW:
    1. Initialize services
    2. Get user input
    3. Validate teams
    4. Get match info
    5. Scrape predictions (using Playwright with 4 REAL prediction sites)
    6. Calculate consensus
    7. Generate recommendations
    8. Return results
    """

    # STEP 1: Initialize services
    logger.info("Initializing services...")
    match_service = MatchService()
    prediction_scraper = PredictionScraperReal()
    consensus_service = ConsensusService()

    # STEP 2: Get user input
    print("\n" + "="*70)
    print("SOCCER BETTING CONSENSUS SYSTEM")
    print("="*70)

    team_a = input("\nEnter first team: ").strip()
    team_b = input("Enter second team: ").strip()

    # STEP 3: Validate teams
    logger.info(f"Validating teams: {team_a} vs {team_b}")
    is_valid, error = match_service.validate_teams(team_a, team_b)

    if not is_valid:
        print(f"\n❌ Error: {error}")
        return

    print(f"\n✅ Teams validated: {team_a} vs {team_b}")

    # STEP 4: Get match info
    logger.info("Retrieving match information...")
    match_info = match_service.get_match_info(team_a, team_b)
    print(f"✅ Match info retrieved")

    # STEP 5: Scrape predictions (using Playwright with 4 REAL prediction sites)
    logger.info("Scraping predictions from websites...")
    print("\n📡 Scraping predictions...")
    predictions = await prediction_scraper.get_predictions(team_a, team_b)
    print(f"✅ Scraped {len(predictions)} predictions")

    # Display scraped data
    print("\n" + "="*70)
    print("SCRAPED DATA FROM WEBSITES")
    print("="*70)
    for source, text in prediction_scraper.scraped_text.items():
        print(f"✅ {source.upper()}: {len(text)} chars scraped")
    
    # STEP 6: Calculate consensus
    logger.info("Calculating consensus...")
    print("\n🔍 Calculating consensus...")
    consensus_picks = consensus_service.calculate_consensus(predictions)
    
    if not consensus_picks:
        print("❌ No consensus picks found")
        return
    
    best_pick = consensus_service.get_best_pick(consensus_picks)
    print(f"✅ Consensus calculated")
    
    # STEP 7: Generate recommendations
    logger.info("Generating recommendations...")
    results = consensus_service.format_results(
        team_a, team_b, best_pick, predictions, match_info
    )
    
    # STEP 8: Display results
    print("\n" + "="*70)
    print("PREDICTION RESULTS")
    print("="*70)
    
    pred = results['prediction']
    rec = results['recommendation']
    
    print(f"\n🏆 BET ON: {pred['team']}")
    print(f"   Consensus Score: {pred['consensus_score']}")
    print(f"   Agreement: {pred['votes']}/{len(predictions)} sources")
    print(f"   Average Confidence: {int(pred['confidence']*100)}%")
    print(f"   Sources: {', '.join(pred['sources'])}")
    print(f"\n   {rec['emoji']} {rec['level']} - {rec['action']}")
    print(f"   Confidence: {rec['confidence']}")
    
    print("\n" + "="*70)
    print("REASONING")
    print("="*70)
    for i, reason in enumerate(results['reasoning'][:3], 1):
        print(f"{i}. {reason}")
    
    print("\n" + "="*70)
    
    # Save results to JSON
    with open('prediction_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save to Supabase (optional)
    supabase_service = SupabaseService()
    if supabase_service.enabled:
        supabase_service.save_prediction(match_info, results['prediction'])

    logger.info("Results saved to prediction_results.json")
    print("\n✅ Results saved to prediction_results.json")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

