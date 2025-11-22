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
import os
import json
from anthropic import Anthropic
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


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
        # Initialize LLM client - supports Groq, OpenRouter, or Anthropic
        self.client = None
        self.client_type = None
        self.has_claude = False

        try:
            # Try Groq first (completely free, no limits)
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key and HAS_GROQ:
                self.client = Groq(api_key=groq_key)
                self.client_type = "groq"
                self.has_claude = True
                logger.info("Using Groq API (FREE, no limits)")
            else:
                # Try OpenRouter
                openrouter_key = os.getenv("OPENROUTER_API_KEY")
                if openrouter_key:
                    self.client = Anthropic(
                        api_key=openrouter_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                    self.client_type = "openrouter"
                    self.has_claude = True
                    logger.info("Using OpenRouter API")
                else:
                    # Try Anthropic direct
                    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
                    if anthropic_key:
                        self.client = Anthropic(api_key=anthropic_key)
                        self.client_type = "anthropic"
                        self.has_claude = True
                        logger.info("Using Anthropic API")
        except Exception as e:
            logger.warning(f"LLM not available: {e}. Will use keyword extraction only.")
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

        # Try LLM first if available
        if self.has_claude:
            try:
                prompt = f"""Analyze this sports prediction website content for {team_a} vs {team_b}.

Website content:
{text[:2000]}

Extract the prediction. Return ONLY a JSON object:
{{"prediction": "PREDICTION_HERE", "confidence": "high/medium/low", "reasoning": "BRIEF_EXPLANATION"}}

Prediction can be: "{team_a}", "{team_b}", "Draw", "Both Teams to Score", "Under", "Over", or "No Prediction"

Return ONLY JSON, no other text."""

                if self.client_type == "groq":
                    # Use llama-3.3-70b (current Groq model)
                    message = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500,
                        temperature=0.3
                    )
                    response_text = message.choices[0].message.content
                elif self.client_type == "openrouter":
                    # OpenRouter - use direct HTTP request
                    import requests
                    headers = {
                        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "anthropic/claude-3-5-sonnet",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500
                    }
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    response.raise_for_status()
                    response_text = response.json()["choices"][0]["message"]["content"]
                else:
                    # Anthropic direct
                    message = self.client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=500,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_text = message.content[0].text
                prediction_data = json.loads(response_text)

                prediction = prediction_data.get("prediction", "No Prediction")
                confidence_str = prediction_data.get("confidence", "medium").lower()
                reasoning = prediction_data.get("reasoning", "")

                if prediction != "No Prediction":
                    # Map confidence
                    confidence_map = {
                        "high": ConfidenceLevel.HIGH,
                        "medium": ConfidenceLevel.MEDIUM,
                        "low": ConfidenceLevel.LOW
                    }
                    confidence = confidence_map.get(confidence_str, ConfidenceLevel.MEDIUM)

                    logger.info(f"✅ {source} (Claude AI): {prediction} ({confidence_str})")

                    return BettingPick(
                        team_or_player=prediction,
                        pick_type=PickType.MONEYLINE,
                        confidence=confidence,
                        reasoning=reasoning or f"{source}: {prediction}",
                        source=source
                    )
                # If LLM says "No Prediction", fall through to keyword fallback
            except Exception as e:
                logger.warning(f"⚠️  Claude error for {source}: {e}. Using fallback keyword matching.")
                # Don't disable Claude entirely, just for this request
                pass

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

