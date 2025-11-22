"""
Real Prediction Service - Scrapes actual sports prediction websites.

Scrapes from:
- sportsgambler.com
- sportsmole.co.uk
- sportskeeda.com
- mightytips.com
- footballpredictions.com

Uses Claude AI to interpret website content (not simple regex).
"""

from typing import List, Dict, Optional
from core.models import BettingPick, PickType, ConfidenceLevel
from core.logger import logger
import requests
from bs4 import BeautifulSoup
import re
import time
from anthropic import Anthropic


class RealPredictionService:
    """Scrapes REAL prediction websites for soccer match predictions."""

    def __init__(self):
        logger.info("Initialized RealPredictionService - scraping REAL websites with AI interpretation")
        self.predictions = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = []
        # Initialize Claude client - will use API key from environment
        try:
            self.client = Anthropic()
            self.has_claude = True
        except Exception as e:
            logger.warning(f"Claude not available: {e}. Will use basic extraction.")
            self.has_claude = False

    def scrape_predictions(self, team_a: str, team_b: str) -> List[BettingPick]:
        """Scrape REAL predictions from multiple websites."""
        self.predictions = []
        self.scraped_data = []
        logger.info(f"Scraping REAL predictions for {team_a} vs {team_b}")

        # Scrape 5 sites
        self._scrape_sportsgambler(team_a, team_b)
        time.sleep(1)
        self._scrape_sportsmole(team_a, team_b)
        time.sleep(1)
        self._scrape_sportskeeda(team_a, team_b)
        time.sleep(1)
        self._scrape_mightytips(team_a, team_b)
        time.sleep(1)
        self._scrape_footballpredictions_com(team_a, team_b)

        logger.info(f"Scraped {len(self.predictions)} predictions from {len(set(p.source for p in self.predictions))} sources")
        return self.predictions

    def get_scraped_data(self) -> List[Dict]:
        """Return actual scraped data for display."""
        return self.scraped_data

    def _extract_prediction(self, text: str, team_a: str, team_b: str, source: str) -> Optional[BettingPick]:
        """Extract prediction using Claude AI or fallback to keyword matching."""
        if not text or len(text.strip()) < 10:
            return None

        # Try Claude first if available
        if self.has_claude:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Analyze this sports prediction website content for {team_a} vs {team_b}.

Website content:
{text[:2000]}

Extract the prediction. Return ONLY a JSON object:
{{"prediction": "PREDICTION_HERE", "confidence": "high/medium/low", "reasoning": "BRIEF_EXPLANATION"}}

Prediction can be: "{team_a}", "{team_b}", "Draw", "Both Teams to Score", "Under", "Over", or "No Prediction"

Return ONLY JSON, no other text."""
                        }
                    ]
                )

                response_text = message.content[0].text
                prediction_data = json.loads(response_text)

                prediction = prediction_data.get("prediction", "No Prediction")
                confidence_str = prediction_data.get("confidence", "medium").lower()
                reasoning = prediction_data.get("reasoning", "")

                if prediction == "No Prediction":
                    return None

                # Map confidence
                confidence_map = {
                    "high": ConfidenceLevel.HIGH,
                    "medium": ConfidenceLevel.MEDIUM,
                    "low": ConfidenceLevel.LOW
                }
                confidence = confidence_map.get(confidence_str, ConfidenceLevel.MEDIUM)

                return BettingPick(
                    team_or_player=prediction,
                    pick_type=PickType.MONEYLINE,
                    confidence=confidence,
                    reasoning=reasoning or f"{source}: {prediction}",
                    source=source
                )
            except Exception as e:
                logger.warning(f"Claude error for {source}: {e}. Using fallback.")
                self.has_claude = False

        # Fallback: keyword-based extraction
        return self._extract_prediction_fallback(text, team_a, team_b, source)

    def _extract_prediction_fallback(self, text: str, team_a: str, team_b: str, source: str) -> Optional[BettingPick]:
        """Fallback extraction using keyword matching."""
        text_lower = text.lower()
        team_a_lower = team_a.lower()
        team_b_lower = team_b.lower()

        # Check for "both teams to score"
        if "both teams" in text_lower and "score" in text_lower:
            return BettingPick(
                team_or_player="Both Teams to Score",
                pick_type=PickType.MONEYLINE,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=f"{source} suggests both teams will score",
                source=source
            )

        # Check for draw
        if "draw" in text_lower or "tie" in text_lower or "1-1" in text_lower:
            return BettingPick(
                team_or_player="Draw",
                pick_type=PickType.MONEYLINE,
                confidence=ConfidenceLevel.MEDIUM,
                reasoning=f"{source} suggests draw is likely",
                source=source
            )

        # Check for team_a
        if team_a_lower in text_lower:
            return BettingPick(
                team_or_player=team_a,
                pick_type=PickType.MONEYLINE,
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"{source} prediction favors {team_a}",
                source=source
            )

        # Check for team_b
        if team_b_lower in text_lower:
            return BettingPick(
                team_or_player=team_b,
                pick_type=PickType.MONEYLINE,
                confidence=ConfidenceLevel.HIGH,
                reasoning=f"{source} prediction favors {team_b}",
                source=source
            )

        return None

    def _scrape_sportsgambler(self, team_a: str, team_b: str) -> None:
        """Scrape sportsgambler.com"""
        try:
            url = f"https://www.sportsgambler.com/predictions/soccer/{team_a.lower()}-vs-{team_b.lower()}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                self.scraped_data.append({"source": "sportsgambler.com", "status": "✅", "url": url})
                pred = self._extract_prediction(text, team_a, team_b, "sportsgambler.com")
                if pred:
                    self.predictions.append(pred)
                    logger.info(f"✅ sportsgambler.com: {pred.team_or_player}")
        except Exception as e:
            logger.warning(f"❌ sportsgambler.com: {e}")
            self.scraped_data.append({"source": "sportsgambler.com", "status": "❌", "error": str(e)})

    def _scrape_sportsmole(self, team_a: str, team_b: str) -> None:
        """Scrape sportsmole.co.uk"""
        try:
            url = f"https://www.sportsmole.co.uk/football/search/?q={team_a}+{team_b}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                self.scraped_data.append({"source": "sportsmole.co.uk", "status": "✅", "url": url})
                pred = self._extract_prediction(text, team_a, team_b, "sportsmole.co.uk")
                if pred:
                    self.predictions.append(pred)
                    logger.info(f"✅ sportsmole.co.uk: {pred.team_or_player}")
        except Exception as e:
            logger.warning(f"❌ sportsmole.co.uk: {e}")
            self.scraped_data.append({"source": "sportsmole.co.uk", "status": "❌", "error": str(e)})

    def _scrape_sportskeeda(self, team_a: str, team_b: str) -> None:
        """Scrape sportskeeda.com"""
        try:
            # Try multiple URL formats
            urls = [
                f"https://www.sportskeeda.com/football/{team_a.lower()}-vs-{team_b.lower()}",
                f"https://www.sportskeeda.com/football/predictions/{team_a.lower()}-vs-{team_b.lower()}",
                f"https://www.sportskeeda.com/search?q={team_a}+{team_b}+prediction"
            ]

            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        self.scraped_data.append({"source": "sportskeeda.com", "status": "✅", "url": url})
                        pred = self._extract_prediction(text, team_a, team_b, "sportskeeda.com")
                        if pred:
                            self.predictions.append(pred)
                            logger.info(f"✅ sportskeeda.com: {pred.team_or_player}")
                        return
                except:
                    continue

            logger.warning(f"❌ sportskeeda.com: No valid URL found")
            self.scraped_data.append({"source": "sportskeeda.com", "status": "❌", "error": "No valid URL"})
        except Exception as e:
            logger.warning(f"❌ sportskeeda.com: {e}")
            self.scraped_data.append({"source": "sportskeeda.com", "status": "❌", "error": str(e)})

    def _scrape_mightytips(self, team_a: str, team_b: str) -> None:
        """Scrape mightytips.com"""
        try:
            url = f"https://www.mightytips.com/search?q={team_a}+{team_b}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                self.scraped_data.append({"source": "mightytips.com", "status": "✅", "url": url})
                pred = self._extract_prediction(text, team_a, team_b, "mightytips.com")
                if pred:
                    self.predictions.append(pred)
                    logger.info(f"✅ mightytips.com: {pred.team_or_player}")
        except Exception as e:
            logger.warning(f"❌ mightytips.com: {e}")
            self.scraped_data.append({"source": "mightytips.com", "status": "❌", "error": str(e)})

    def _scrape_footballpredictions_com(self, team_a: str, team_b: str) -> None:
        """Scrape footballpredictions.com"""
        try:
            # Try multiple URL formats
            urls = [
                f"https://www.footballpredictions.com/{team_a.lower()}-vs-{team_b.lower()}",
                f"https://www.footballpredictions.com/predictions/{team_a.lower()}-vs-{team_b.lower()}",
                f"https://www.footballpredictions.com/search?q={team_a}+{team_b}"
            ]

            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        self.scraped_data.append({"source": "footballpredictions.com", "status": "✅", "url": url})
                        pred = self._extract_prediction(text, team_a, team_b, "footballpredictions.com")
                        if pred:
                            self.predictions.append(pred)
                            logger.info(f"✅ footballpredictions.com: {pred.team_or_player}")
                        return
                except:
                    continue

            logger.warning(f"❌ footballpredictions.com: No valid URL found")
            self.scraped_data.append({"source": "footballpredictions.com", "status": "❌", "error": "No valid URL"})
        except Exception as e:
            logger.warning(f"❌ footballpredictions.com: {e}")
            self.scraped_data.append({"source": "footballpredictions.com", "status": "❌", "error": str(e)})

