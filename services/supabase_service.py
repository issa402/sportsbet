"""
Supabase Service - Stores predictions in AutoCam project.

Uses AutoCam Supabase project (vumvytymksxbulrulumc) to store:
- Match predictions
- Consensus scores
- Source data
"""

from core.logger import logger
from typing import Dict, List, Optional
import os
from datetime import datetime

# Supabase credentials for AutoCam project
SUPABASE_URL = "https://vumvytymksxbulrulumc.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Set via environment variable

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase not installed. Install with: pip install supabase")


class SupabaseService:
    """Stores predictions in Supabase AutoCam project."""

    def __init__(self):
        self.enabled = SUPABASE_AVAILABLE and SUPABASE_KEY
        if self.enabled:
            try:
                self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("✅ Connected to Supabase (AutoCam project)")
            except Exception as e:
                logger.warning(f"❌ Failed to connect to Supabase: {e}")
                self.enabled = False
        else:
            logger.info("⚠️ Supabase not configured. Set SUPABASE_KEY environment variable.")

    def save_prediction(self, match_data: Dict, prediction_data: Dict) -> bool:
        """Save prediction to Supabase."""
        if not self.enabled:
            logger.warning("Supabase not enabled. Skipping save.")
            return False

        try:
            # Create record
            record = {
                "team_a": match_data.get("team_a"),
                "team_b": match_data.get("team_b"),
                "predicted_team": prediction_data.get("team"),
                "consensus_score": prediction_data.get("consensus_score"),
                "sources": ",".join(prediction_data.get("sources", [])),
                "recommendation": prediction_data.get("level"),
                "created_at": datetime.now().isoformat(),
            }

            # Insert into predictions table
            response = self.client.table("predictions").insert(record).execute()
            logger.info(f"✅ Saved prediction to Supabase: {match_data['team_a']} vs {match_data['team_b']}")
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to save to Supabase: {e}")
            return False

    def get_predictions(self, team_a: Optional[str] = None, team_b: Optional[str] = None) -> List[Dict]:
        """Retrieve predictions from Supabase."""
        if not self.enabled:
            return []

        try:
            query = self.client.table("predictions").select("*")
            
            if team_a:
                query = query.eq("team_a", team_a)
            if team_b:
                query = query.eq("team_b", team_b)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.warning(f"❌ Failed to retrieve from Supabase: {e}")
            return []

    def create_table_if_not_exists(self) -> bool:
        """Create predictions table if it doesn't exist."""
        if not self.enabled:
            return False

        try:
            # This would need to be done via Supabase dashboard or migrations
            logger.info("Note: Create 'predictions' table in Supabase dashboard with columns:")
            logger.info("  - id (uuid, primary key)")
            logger.info("  - team_a (text)")
            logger.info("  - team_b (text)")
            logger.info("  - predicted_team (text)")
            logger.info("  - consensus_score (float)")
            logger.info("  - sources (text)")
            logger.info("  - recommendation (text)")
            logger.info("  - created_at (timestamp)")
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to create table: {e}")
            return False

