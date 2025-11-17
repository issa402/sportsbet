"""
ESPN API Service - Fetch REAL historical data for soccer teams
Gets ONLY last 5 matches for any team (NO MOCK DATA)

ESPN's public API: https://site.web.api.espn.com/apis/site/v2/sports/soccer/
No authentication needed - completely FREE
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ESPNAPIService:
    """Fetch REAL team data from ESPN's free public API"""

    BASE_URL = "https://site.web.api.espn.com/apis/site/v2/sports/soccer"

    # Top 4 European leagues supported by ESPN API
    LEAGUES = {
        'eng.1': 'English Premier League',
        'esp.1': 'La Liga (Spain)',
        'ita.1': 'Serie A (Italy)',
        'ger.1': 'Bundesliga (Germany)',
    }

    def __init__(self):
        self.cache = {}
        self.timeout = 10
        self.team_cache = {}  # Cache team IDs to avoid repeated searches

    def get_team_last_5_matches(self, team_name: str) -> List[Dict]:
        """
        Get ONLY the last 5 matches for ANY team from ESPN API
        Automatically searches across all major leagues

        Args:
            team_name: Team name (e.g., "Manchester City", "Real Madrid", "Celta Vigo")

        Returns:
            List of last 5 matches with: date, home_team, away_team, score
        """
        logger.info(f"\n🔍 Fetching last 5 matches for {team_name} from ESPN API...")

        try:
            # Check cache first
            if team_name.lower() in self.team_cache:
                team_id, league = self.team_cache[team_name.lower()]
                logger.info(f"   ✅ Found in cache: {team_name} (ID: {team_id}, League: {league})")
            else:
                # Search for team across all leagues
                result = self._search_team_across_leagues(team_name)
                if not result:
                    logger.warning(f"   ❌ Team not found: {team_name}")
                    return []

                team_id, league = result
                self.team_cache[team_name.lower()] = (team_id, league)
                logger.info(f"   ✅ Found team: {team_name} (ID: {team_id}, League: {self.LEAGUES.get(league, league)})")

            # Get team schedule
            matches = self._get_team_schedule(team_id, league)

            # Return only last 5
            last_5 = matches[:5]
            logger.info(f"   ✅ Got {len(last_5)} matches")

            return last_5

        except Exception as e:
            logger.error(f"   ❌ Error fetching matches: {e}")
            return []
    
    def _search_team_across_leagues(self, team_name: str) -> Optional[tuple]:
        """Search for team ID by name across ALL major leagues

        Returns:
            Tuple of (team_id, league_code) or None if not found
        """
        try:
            team_name_lower = team_name.lower()

            # Try each league
            for league_code in self.LEAGUES.keys():
                try:
                    url = f"{self.BASE_URL}/{league_code}/teams"
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()

                    data = response.json()
                    teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])

                    for team in teams:
                        team_obj = team.get('team', {})
                        display_name = team_obj.get('displayName', '').lower()

                        # Exact match or partial match
                        if team_name_lower == display_name or team_name_lower in display_name:
                            return (team_obj.get('id'), league_code)
                except Exception as e:
                    logger.debug(f"   Error searching {league_code}: {e}")
                    continue

            return None
        except Exception as e:
            logger.error(f"   Error searching team: {e}")
            return None

    def _get_team_schedule(self, team_id: str, league: str) -> List[Dict]:
        """Get team's schedule/matches from ESPN API

        Args:
            team_id: ESPN team ID
            league: League code (e.g., 'eng.1', 'esp.1')
        """
        try:
            url = f"{self.BASE_URL}/{league}/teams/{team_id}/schedule"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            events = data.get('events', [])

            matches = []
            for event in events:
                match_data = self._parse_match(event)
                if match_data:
                    matches.append(match_data)

            return matches

        except Exception as e:
            logger.error(f"   Error getting schedule: {e}")
            return []
    
    def _parse_match(self, event: Dict) -> Optional[Dict]:
        """Parse a match from ESPN event data"""
        try:
            # Get date
            date_str = event.get('date', '')

            # Get competitors from competitions
            competitions = event.get('competitions', [])
            if not competitions:
                return None

            comp = competitions[0]
            competitors = comp.get('competitors', [])
            if len(competitors) < 2:
                return None

            # Extract team info and scores
            home_team = competitors[0].get('team', {}).get('displayName', 'Unknown')
            away_team = competitors[1].get('team', {}).get('displayName', 'Unknown')

            # Get score - handle both simple int and complex dict
            home_score_obj = competitors[0].get('score', 0)
            away_score_obj = competitors[1].get('score', 0)

            # Extract numeric value
            if isinstance(home_score_obj, dict):
                home_score = home_score_obj.get('value', 0)
            else:
                home_score = home_score_obj

            if isinstance(away_score_obj, dict):
                away_score = away_score_obj.get('value', 0)
            else:
                away_score = away_score_obj

            return {
                'date': date_str,
                'home_team': home_team,
                'away_team': away_team,
                'score': f"{int(home_score)}-{int(away_score)}",
                'home_score': int(home_score),
                'away_score': int(away_score)
            }
        except Exception as e:
            logger.error(f"   Error parsing match: {e}")
            return None


if __name__ == "__main__":
    service = ESPNAPIService()
    
    print("=" * 80)
    print("ESPN API SERVICE - LAST 5 MATCHES")
    print("=" * 80)
    
    # Test with Manchester City
    matches = service.get_team_last_5_matches("Manchester City")
    print(f"\n✅ Manchester City - Last 5 Matches:")
    for m in matches:
        print(f"  {m['date']}: {m['home_team']} vs {m['away_team']} ({m['score']})")

