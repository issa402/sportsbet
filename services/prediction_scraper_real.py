"""
REAL PREDICTION TEXT SCRAPER - SOCCER ONLY
PREDICTION SITES (4):
1. Sportsmole - Match previews with predictions ✅
2. Eagle Predict - Free soccer predictions ✅
3. Deepbetting - AI soccer predictions ✅
4. LeagueLane - Football predictions & betting tips ✅

PAST RESULTS SITE:
- Sportsmole - Past match results & scores ✅
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Optional
from core.models import BettingPick, PickType, ConfidenceLevel
from core.logger import logger
from groq import Groq
import os
import json
import requests
import re


class PredictionScraperReal:
    """Scrape REAL prediction text from 3 working sites."""
    def __init__(self):
        self.predictions: List[BettingPick] = []
        self.scraped_text = {}
        self.client = None
        
        # Initialize Groq
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                self.client = Groq(api_key=groq_key)
                logger.info("✅ Groq API initialized")
        except Exception as e:
            logger.warning(f"Groq not available: {e}")
    
    
    async def get_predictions(self, team_a: str, team_b: str) -> List[BettingPick]:
        """Get predictions from 4 SOCCER prediction sites."""
        self.predictions = []
        self.scraped_text = {}

        logger.info(f"\n🔍 Scraping predictions for {team_a} vs {team_b}")
        logger.info("=" * 80)
        logger.info("📊 SOURCES: Sportsmole, Eagle Predict, Deepbetting, LeagueLane")
        logger.info("=" * 80)


        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Scrape all 4 prediction sites
            await self._scrape_sportsmole(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_eagle_predict(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_deepbetting(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_leaguelane(browser, team_a, team_b)

            await browser.close()

        logger.info(f"✅ Total predictions: {len(self.predictions)}")
        return self.predictions

    
    async def get_past_results(self, team_name: str, num_games: int = 5) -> dict:
        """Get past results for a team from Sportsmole."""
        logger.info(f"\n📊 Scraping past {num_games} games for {team_name}")
        logger.info("=" * 80)
        logger.info("📊 SOURCE: Sportsmole (team page)")
        logger.info("=" * 80)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Go to Sportsmole team page
                team_slug = team_name.lower().replace(" ", "-")
                url = f"https://www.sportsmole.co.uk/football/{team_slug}/"
                logger.info(f"   Navigating to: {url}")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)

                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()

                logger.info(f"   ✅ Scraped {len(text)} chars from Sportsmole")

                # Use Groq to extract past results
                if self.client:
                    message = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{
                            "role": "user",
                            "content": f"""Extract the past {num_games} match results for {team_name} from this Sportsmole data.

Return JSON with array of matches:
[
  {{"date": "YYYY-MM-DD", "opponent": "team name", "score": "X-Y", "result": "W/D/L"}},
  ...
]

Text:
{text[:4000]}"""
                        }],
                        max_tokens=500,
                        temperature=0.3
                    )

                    response_text = message.choices[0].message.content
                    logger.info(f"   Groq response: {response_text[:200]}")
                    return {"team": team_name, "results": response_text}

    
            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
            finally:
                await browser.close()

        return {"team": team_name, "results": "No data"}
    
    async def _scrape_sportsmole(self, browser, team_a: str, team_b: str):
        """Scrape Sportsmole predictions - DYNAMIC."""
        logger.info("\n📊 SOURCE 1: Sportsmole")
        try:
            page = await browser.new_page()

            # Construct URL from team names
            team_a_slug = team_a.lower().replace(" ", "-")
            team_b_slug = team_b.lower().replace(" ", "-")

            # Step 1: Search for the article to get the article ID
            search_team_a = team_a.split()[-1] if " " in team_a else team_a
            search_team_b = team_b.split()[-1] if " " in team_b else team_b

            search_url = f"https://www.sportsmole.co.uk/football/search/?q={search_team_a}+{search_team_b}"
            logger.info(f"   Searching: {search_url}")

            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Get all preview links and find the matching one
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            article_id = None
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'preview' in href and 'prediction' in href.lower():
                    # Check if both teams are in the URL
                    if team_a_slug in href and team_b_slug in href:
                        if '_' in href and '.html' in href:
                            article_id = href.split('_')[-1].replace('.html', '')
                            logger.info(f"   Found article ID: {article_id}")
                            break

            # Step 2: Navigate to the article
            if article_id:
                url = f"https://www.sportsmole.co.uk/football/{team_a_slug}/preview/{team_a_slug}-vs-{team_b_slug}-prediction-team-news-lineups_{article_id}.html"
            else:
                url = f"https://www.sportsmole.co.uk/football/{team_a_slug}/preview/{team_a_slug}-vs-{team_b_slug}-prediction-team-news-lineups.html"

            logger.info(f"   Navigating to: {url}")
        
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["sportsmole"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            # Extract predictions using Groq
            self._extract_with_groq(text, team_a, team_b, "Sportsmole")

            await page.close()

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

    async def _scrape_eagle_predict(self, browser, team_a: str, team_b: str):
        """Scrape Eagle Predict predictions - search for specific match."""
        logger.info("\n🦅 SOURCE 2: Eagle Predict")
        try:
            page = await browser.new_page()

            # Search for the match on Eagle Predict
            search_url = f"https://eaglepredict.com/search?q={team_a}+{team_b}"
            logger.info(f"   Searching: {search_url}")
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["eaglepredict"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "Eagle Predict")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

    async def _scrape_deepbetting(self, browser, team_a: str, team_b: str):
        """Scrape Deepbetting predictions - search for specific match."""
        logger.info("\n🤖 SOURCE 3: Deepbetting")
        try:
            page = await browser.new_page()

            # Search for the match on Deepbetting
            search_url = f"https://deepbetting.io/search?q={team_a}+{team_b}"
            logger.info(f"   Searching: {search_url}")
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["deepbetting"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "Deepbetting")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

    async def _scrape_leaguelane(self, browser, team_a: str, team_b: str):
        """Scrape LeagueLane predictions - direct URL pattern."""
        logger.info("\n🏆 SOURCE 4: LeagueLane")
        try:
            page = await browser.new_page()

            # Construct URL from team names - use last name only for simpler URL
            team_a_slug = team_a.split()[-1].lower().replace(" ", "-")
            team_b_slug = team_b.split()[-1].lower().replace(" ", "-")

            url = f"https://www.leaguelane.com/predictions/{team_a_slug}-vs-{team_b_slug}/"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["leaguelane"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "LeagueLane")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
    


    async def _scrape_betting_expert(self, browser, team_a: str, team_b: str):
        """Scrape Betting Expert predictions - WORKING SITE."""
        logger.info("\n💡 SOURCE 3: Betting Expert")
    
        try:

            page = await browser.new_page()
            url = "https://www.bettingexpert.com/"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(2000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["betting_expert"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "Betting Expert")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
    

    def _extract_with_groq(self, text: str, team_a: str, team_b: str, source: str):
        """Use Groq to extract predictions from text."""
        if not self.client or len(text) < 100:
            logger.debug(f"   Skipping {source}: text too short ({len(text)} chars)")
            return

        try:
            # Extract all lines (don't filter too aggressively)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            relevant_text = '\n'.join(lines[:200])  # Top 200 lines

            prompt = f"""You are a soccer prediction analyzer. Extract ANY soccer prediction from this text.

Text:
{relevant_text}

Find ANY prediction about soccer matches. Return ONLY valid JSON:
{{"prediction": "TEAM_NAME or DRAW or BTTS or OVER or UNDER or NO_PREDICTION", "confidence": "high/medium/low", "reasoning": "BRIEF explanation"}}

Examples of valid predictions:
- "Liverpool" (team to win)
- "Draw" (match will draw)
- "BTTS" (both teams to score)
- "OVER" (over 2.5 goals)
- "UNDER" (under 2.5 goals)
- "NO_PREDICTION" (if no prediction found)
"""

            message = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )

            response_text = message.choices[0].message.content
            logger.info(f"   Groq response: {response_text[:150]}")

            # Parse JSON
            try:
                data = json.loads(response_text)
            except Exception as parse_err:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                    except:
                        logger.info(f"   ⚠️  Failed to parse JSON from {source}: {parse_err}")
                        return
                else:
                    logger.info(f"   ⚠️  No JSON found in response from {source}")
                    return

            if data.get("prediction") and data.get("prediction") != "NO_PREDICTION":
                confidence_map = {"high": ConfidenceLevel.HIGH, "medium": ConfidenceLevel.MEDIUM, "low": ConfidenceLevel.LOW}
                pred = BettingPick(
                    team_or_player=data["prediction"],
                    pick_type=PickType.MONEYLINE,
                    confidence=confidence_map.get(data.get("confidence", "medium"), ConfidenceLevel.MEDIUM),
                    reasoning=data.get("reasoning", ""),
                    source=source
                )
                self.predictions.append(pred)
                logger.info(f"   ✅ {source}: {data['prediction']}")
            else:
                logger.info(f"   ⚠️  No prediction from {source}: {data.get('prediction')}")
        except Exception as e:
            logger.info(f"   ❌ Groq extraction error: {type(e).__name__}: {e}")
            # Fallback: Try regex-based extraction
            self._extract_with_regex(text, team_a, team_b, source)

    def _extract_with_regex(self, text: str, team_a: str, team_b: str, source: str):
        """Fallback regex-based extraction when Groq fails."""
        logger.info(f"   🔄 Trying regex fallback for {source}")
        try:
            text_lower = text.lower()
            team_a_lower = team_a.lower()
            team_b_lower = team_b.lower()

            # Extract last names for better matching
            team_a_last = team_a.split()[-1].lower()
            team_b_last = team_b.split()[-1].lower()

            # Look for team names in text
            team_a_count = text_lower.count(team_a_lower) + text_lower.count(team_a_last)
            team_b_count = text_lower.count(team_b_lower) + text_lower.count(team_b_last)

            # Look for prediction keywords near team names
            has_win = any(x in text_lower for x in ['win', 'winner', 'to win', 'victory', 'predicted to win', 'prediction:'])
            has_draw = any(x in text_lower for x in ['draw', 'tie', 'equal', '1-1', '0-0'])
            has_over = any(x in text_lower for x in ['over 2.5', 'over 3.5', 'over goals'])

            # Look for explicit prediction patterns
            import re
            prediction_patterns = [
                r'prediction[:\s]+([a-z\s]+)',
                r'tip[:\s]+([a-z\s]+)',
                r'forecast[:\s]+([a-z\s]+)',
                r'our pick[:\s]+([a-z\s]+)',
            ]

            for pattern in prediction_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    pred_text = match.group(1).strip()
                    if team_a_last in pred_text or team_a_lower in pred_text:
                        prediction = team_a
                        confidence = ConfidenceLevel.MEDIUM
                        pred = BettingPick(
                            team_or_player=prediction,
                            pick_type=PickType.MONEYLINE,
                            confidence=confidence,
                            reasoning="Extracted via regex pattern",
                            source=source
                        )
                        self.predictions.append(pred)
                        logger.info(f"   ✅ {source} (regex): {prediction}")
                        return
                    elif team_b_last in pred_text or team_b_lower in pred_text:
                        prediction = team_b
                        confidence = ConfidenceLevel.MEDIUM
                        pred = BettingPick(
                            team_or_player=prediction,
                            pick_type=PickType.MONEYLINE,
                            confidence=confidence,
                            reasoning="Extracted via regex pattern",
                            source=source
                        )
                        self.predictions.append(pred)
                        logger.info(f"   ✅ {source} (regex): {prediction}")
                        return

            # Fallback: count-based heuristic
            if team_a_count > team_b_count and has_win:
                prediction = team_a
                confidence = ConfidenceLevel.LOW
            elif team_b_count > team_a_count and has_win:
                prediction = team_b
                confidence = ConfidenceLevel.LOW
            elif has_draw:
                prediction = "Draw"
                confidence = ConfidenceLevel.LOW
            else:
                logger.info(f"   ⚠️  No prediction found via regex for {source}")
                return

            pred = BettingPick(
                team_or_player=prediction,
                pick_type=PickType.MONEYLINE,
                confidence=confidence,
                reasoning="Extracted via regex fallback",
                source=source
            )
            self.predictions.append(pred)
            logger.info(f"   ✅ {source} (regex): {prediction}")
        except Exception as e:
            logger.info(f"   ❌ Regex extraction error: {e}")

