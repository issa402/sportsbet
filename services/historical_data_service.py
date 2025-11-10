"""
Historical Match Data Service
Fetches historical match data from football.json API (FREE, NO AUTH NEEDED)
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HistoricalDataService:
    """Fetch historical match data from football.json API"""
    
    BASE_URL = "https://raw.githubusercontent.com/openfootball/football.json/master"
    
    # League mappings
    LEAGUES = {
        "premier_league": "2024-25/en.1.json",
        "championship": "2024-25/en.2.json",
        "bundesliga": "2024-25/de.1.json",
        "la_liga": "2024-25/es.1.json",
        "serie_a": "2024-25/it.1.json",
        "ligue_1": "2024-25/fr.1.json",
    }
    
    def __init__(self):
        self.cache = {}
    
    def get_league_data(self, league: str = "premier_league") -> Optional[Dict]:
        """Fetch league data from football.json"""
        if league in self.cache:
            return self.cache[league]
        
        league_file = self.LEAGUES.get(league)
        if not league_file:
            logger.error(f"League {league} not found")
            return None
        
        try:
            url = f"{self.BASE_URL}/{league_file}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.cache[league] = data
                logger.info(f"✅ Fetched {league}: {len(data.get('matches', []))} matches")
                return data
            else:
                logger.error(f"Failed to fetch {league}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {league}: {str(e)}")
            return None
    
    def get_head_to_head(self, team_a: str, team_b: str, league: str = "premier_league", limit: int = 5) -> List[Dict]:
        """Get last N head-to-head matches between two teams"""
        data = self.get_league_data(league)
        if not data:
            return []
        
        h2h_matches = []
        for match in data.get('matches', []):
            team1 = match.get('team1', '').lower()
            team2 = match.get('team2', '').lower()
            
            team_a_lower = team_a.lower()
            team_b_lower = team_b.lower()
            
            # Check if this is a match between the two teams
            if (team_a_lower in team1 or team_a_lower in team2) and \
               (team_b_lower in team1 or team_b_lower in team2):
                h2h_matches.append(match)
        
        # Return last N matches
        return h2h_matches[-limit:]
    
    def get_team_form(self, team: str, league: str = "premier_league", limit: int = 5) -> List[Dict]:
        """Get last N matches for a team"""
        data = self.get_league_data(league)
        if not data:
            return []
        
        team_matches = []
        team_lower = team.lower()
        
        for match in data.get('matches', []):
            team1 = match.get('team1', '').lower()
            team2 = match.get('team2', '').lower()
            
            if team_lower in team1 or team_lower in team2:
                team_matches.append(match)
        
        # Return last N matches
        return team_matches[-limit:]
    
    def extract_features(self, team_a: str, team_b: str, league: str = "premier_league") -> Dict:
        """Extract features for ML model"""
        h2h = self.get_head_to_head(team_a, team_b, league, limit=5)
        form_a = self.get_team_form(team_a, league, limit=5)
        form_b = self.get_team_form(team_b, league, limit=5)
        
        features = {
            "team_a": team_a,
            "team_b": team_b,
            "head_to_head": h2h,
            "form_a": form_a,
            "form_b": form_b,
            "h2h_count": len(h2h),
            "form_a_count": len(form_a),
            "form_b_count": len(form_b),
        }
        
        # Calculate win/loss/draw stats
        if h2h:
            team_a_wins = sum(1 for m in h2h if m.get('score', {}).get('ft', [None, None])[0] > m.get('score', {}).get('ft', [None, None])[1])
            team_b_wins = sum(1 for m in h2h if m.get('score', {}).get('ft', [None, None])[0] < m.get('score', {}).get('ft', [None, None])[1])
            draws = len(h2h) - team_a_wins - team_b_wins
            
            features["h2h_stats"] = {
                f"{team_a}_wins": team_a_wins,
                f"{team_b}_wins": team_b_wins,
                "draws": draws,
            }
        
        return features


if __name__ == "__main__":
    # Test the service
    service = HistoricalDataService()
    
    print("=" * 80)
    print("TESTING HISTORICAL DATA SERVICE")
    print("=" * 80)
    
    # Get head-to-head
    print("\n1️⃣  MAN CITY VS LIVERPOOL HEAD-TO-HEAD (LAST 5)")
    h2h = service.get_head_to_head("Manchester City", "Liverpool", limit=5)
    for match in h2h:
        print(f"  {match['date']}: {match['team1']} {match['score']['ft'][0]}-{match['score']['ft'][1]} {match['team2']}")
    
    # Get team form
    print("\n2️⃣  MAN CITY FORM (LAST 5)")
    form = service.get_team_form("Manchester City", limit=5)
    for match in form:
        print(f"  {match['date']}: {match['team1']} {match['score']['ft'][0]}-{match['score']['ft'][1]} {match['team2']}")
    
    # Extract features
    print("\n3️⃣  EXTRACTED FEATURES")
    features = service.extract_features("Manchester City", "Liverpool")
    print(json.dumps(features, indent=2, default=str))

