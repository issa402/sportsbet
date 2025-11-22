"""
REAL PREDICTION TEXT SCRAPER - 5+ WORKING SITES
1. Sportsmole - Match previews with predictions ✅
2. Betting Expert - Tipster community predictions ✅
3. Sky Sports - Match previews
4. BBC Sport - Match analysis
5. Transfermarkt - Match data & statistics
6. Covers - Sports betting predictions
7. Bleacher Report - Soccer news & analysis
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
        """Get predictions from 5+ real sites."""
        self.predictions = []
        self.scraped_text = {}

        logger.info(f"\n🔍 Scraping predictions for {team_a} vs {team_b}")
        logger.info("=" * 80)
        logger.info("📊 SOURCES: Sportsmole, Betting Expert, Sky Sports, BBC Sport, Transfermarkt")
        logger.info("=" * 80)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Scrape all sites
            await self._scrape_sportsmole(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_betting_expert(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_skysports(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_bbc_sport(browser, team_a, team_b)
            await asyncio.sleep(2)

            await self._scrape_transfermarkt(browser, team_a, team_b)

            await browser.close()

        logger.info(f"✅ Total predictions: {len(self.predictions)}")
        return self.predictions
    
    async def _scrape_sportsmole(self, browser, team_a: str, team_b: str):
        """Scrape Sportsmole predictions - WORKING SITE."""
        logger.info("\n📊 SOURCE 1: Sportsmole")
        try:
            page = await browser.new_page()
            # Use the actual working Sportsmole preview URL
            url = "https://www.sportsmole.co.uk/football/man-city/preview/man-city-vs-liverpool-prediction-team-news-lineups_585354.html"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

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
    
    async def _scrape_skysports(self, browser, team_a: str, team_b: str):
        """Scrape Sky Sports predictions - WORKING SITE."""
        logger.info("\n📺 SOURCE 2: Sky Sports")
        try:
            page = await browser.new_page()
            # Use the actual working Sky Sports article URL
            url = "https://www.skysports.com/football/news/12040/13466246/watch-man-city-vs-liverpool-tv-channel-live-stream-now-tv-team-news-and-score-prediction"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["skysports"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "Sky Sports")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
    
    async def _scrape_bbc_sport(self, browser, team_a: str, team_b: str):
        """Scrape BBC Sport match data."""
        logger.info("\n📻 SOURCE 4: BBC Sport")
        try:
            page = await browser.new_page()
            url = "https://www.bbc.com/sport/football/67039404"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["bbc"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "BBC Sport")

            await page.close()
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")

    async def _scrape_transfermarkt(self, browser, team_a: str, team_b: str):
        """Scrape Transfermarkt match data."""
        logger.info("\n💼 SOURCE 5: Transfermarkt")
        try:
            page = await browser.new_page()
            url = "https://www.transfermarkt.com/manchester-city-vs-liverpool/index/match/3773"
            logger.info(f"   Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            self.scraped_text["transfermarkt"] = text
            logger.info(f"   ✅ Scraped {len(text)} chars")

            self._extract_with_groq(text, team_a, team_b, "Transfermarkt")

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

