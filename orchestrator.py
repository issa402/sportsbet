"""
================================================================================
MAIN ORCHESTRATOR - SPORTS BETTING CONSENSUS SYSTEM
================================================================================

This module coordinates the entire workflow of the betting consensus system:

1. FETCH ARTICLES - Scrape articles from multiple sources
2. EXTRACT PICKS - Parse picks from article content
3. ANALYZE CONSENSUS - Calculate consensus scores
4. STORE RESULTS - Save to database
5. DELIVER OUTPUT - Return results to user

WORKFLOW:
    Fetch Articles → Extract Picks → Analyze Consensus → Store → Output

WHEN TO USE:
- Run orchestrator.run_full_pipeline() to execute the complete workflow
- Run orchestrator.close() when done to clean up resources

EXAMPLE:
    orchestrator = BettingConsensusOrchestrator()
    result = orchestrator.run_full_pipeline()
    print(result['top_picks'])
    orchestrator.close()
================================================================================
"""

# Import required modules
from typing import List  # Type hints for lists
from datetime import datetime  # For timestamps
from core.models import Article, BettingPick, ConsensusPick  # Data models
from scrapers.espn_scraper import ESPNScraper  # ESPN scraper
from scrapers.bleacher_report_scraper import BleacherReportScraper  # Bleacher Report scraper
from extractors.regex_extractor import RegexExtractor  # Regex-based extraction
from extractors.llm_extractor import LLMExtractor  # LLM-based extraction
from consensus.analyzer import ConsensusAnalyzer  # Consensus calculation
from storage.database import Database  # Database operations
from core.logger import logger  # Logging
from config.settings import settings  # Configuration


class BettingConsensusOrchestrator:
    """
    CLASS: Orchestrates the entire consensus system workflow.

    WHY USE THIS:
    - Coordinates all components (scrapers, extractors, analyzer, database)
    - Manages the complete pipeline from fetch to output
    - Handles errors and logging
    - Provides a single entry point for the system

    ATTRIBUTES:
    - database: Database connection for storing results
    - analyzer: ConsensusAnalyzer for calculating consensus
    - regex_extractor: RegexExtractor for pattern-based extraction
    - llm_extractor: LLMExtractor for AI-based extraction
    - scrapers: List of scrapers for fetching articles

    USAGE EXAMPLE:
        orchestrator = BettingConsensusOrchestrator()
        result = orchestrator.run_full_pipeline()
        print(result['top_picks'])
        orchestrator.close()
    """

    def __init__(self):
        """
        CONSTRUCTOR: Initialize the orchestrator with all components.

        WHY USE THIS:
        - Sets up database connection
        - Initializes consensus analyzer
        - Initializes extractors (regex and LLM)
        - Initializes scrapers based on configuration

        WHAT IT DOES:
        1. Creates database connection
        2. Creates consensus analyzer
        3. Creates regex extractor
        4. Creates LLM extractor
        5. Creates scrapers for enabled sources
        6. Logs initialization

        USAGE EXAMPLE:
            orchestrator = BettingConsensusOrchestrator()
            # Now ready to run pipeline
        """
        # STEP 1: Initialize database connection
        # This connects to SQLite database for storing articles, picks, and consensus
        self.database = Database()

        # STEP 2: Initialize consensus analyzer
        # min_frequency=1 means include picks from any number of sources
        # Set to 2+ to filter out single-source picks
        self.analyzer = ConsensusAnalyzer(min_frequency=1)

        # STEP 3: Initialize regex extractor
        # Uses pattern matching to extract picks from article text
        self.regex_extractor = RegexExtractor()

        # STEP 4: Initialize LLM extractor
        # Uses Claude AI to understand article content and extract picks
        self.llm_extractor = LLMExtractor()

        # STEP 5: Initialize scrapers based on configuration
        # Only create scrapers for enabled sources
        self.scrapers = []

        # Check if ESPN is enabled in settings
        if "espn" in settings.enabled_sources:
            # Create ESPN scraper
            self.scrapers.append(ESPNScraper())

        # Check if Bleacher Report is enabled in settings
        if "bleacher_report" in settings.enabled_sources:
            # Create Bleacher Report scraper
            self.scrapers.append(BleacherReportScraper())

        # STEP 6: Log initialization
        logger.info(f"Initialized orchestrator with {len(self.scrapers)} scrapers")
    
    def run_full_pipeline(self) -> dict:
        """
        PUBLIC METHOD: Run the complete pipeline: fetch -> extract -> analyze -> store.

        THIS IS THE MAIN ENTRY POINT - Executes the entire workflow in sequence:
        1. Fetch articles from all sources
        2. Save articles to database
        3. Extract picks using regex patterns
        4. Extract picks using LLM (AI)
        5. Save picks to database
        6. Analyze consensus across sources
        7. Save consensus picks to database
        8. Generate statistics
        9. Return results

        RETURNS:
        - dict: Pipeline results with status, metrics, and top picks

        USAGE EXAMPLE:
            orchestrator = BettingConsensusOrchestrator()
            result = orchestrator.run_full_pipeline()

            if result['status'] == 'success':
                print(f"Fetched {result['articles_fetched']} articles")
                print(f"Extracted {result['picks_extracted']} picks")
                print(f"Generated {result['consensus_picks_generated']} consensus picks")
                for pick in result['top_picks']:
                    print(f"  {pick['team_or_player']}: {pick['consensus_score']}")
        """
        # Log pipeline start
        logger.info("=" * 80)
        logger.info("Starting full pipeline execution")
        logger.info("=" * 80)

        # Record start time for performance measurement
        start_time = datetime.now()

        try:
            # ====================================================================
            # STEP 1: FETCH ARTICLES FROM ALL SOURCES
            # ====================================================================
            logger.info("Step 1: Fetching articles from sources...")
            # Call _fetch_articles() to scrape articles from all enabled sources
            articles = self._fetch_articles()

            # Check if any articles were fetched
            if not articles:
                # Log warning if no articles found
                logger.warning("No articles fetched")
                # Return failure result
                return {
                    "status": "failed",
                    "message": "No articles fetched",
                    "timestamp": datetime.now().isoformat()
                }

            # Log success
            logger.info(f"Fetched {len(articles)} articles")

            # ====================================================================
            # STEP 2: SAVE ARTICLES TO DATABASE
            # ====================================================================
            logger.info("Step 2: Saving articles to database...")
            # Save articles to database for future reference
            saved_articles = self._save_articles(articles)
            logger.info(f"Saved {saved_articles} articles")

            # ====================================================================
            # STEP 3: EXTRACT PICKS USING REGEX PATTERNS
            # ====================================================================
            logger.info("Step 3: Extracting picks using regex...")
            # Use regex extractor to find picks using pattern matching
            # This is fast but may miss complex picks
            regex_picks = self.regex_extractor.extract_batch(articles)
            logger.info(f"Extracted {len(regex_picks)} picks using regex")

            # ====================================================================
            # STEP 4: EXTRACT PICKS USING LLM (AI)
            # ====================================================================
            logger.info("Step 4: Extracting picks using LLM...")
            # Use LLM extractor to understand article content and extract picks
            # This is slower but more accurate for complex picks
            llm_picks = self.llm_extractor.extract_batch(articles)
            logger.info(f"Extracted {len(llm_picks)} picks using LLM")

            # ====================================================================
            # STEP 5: COMBINE PICKS FROM BOTH EXTRACTORS
            # ====================================================================
            # Combine picks from both regex and LLM extraction
            # This gives us the best of both approaches
            all_picks = regex_picks + llm_picks
            logger.info(f"Total picks extracted: {len(all_picks)}")

            # ====================================================================
            # STEP 6: SAVE PICKS TO DATABASE
            # ====================================================================
            logger.info("Step 5: Saving picks to database...")
            # Save all extracted picks to database
            saved_picks = self._save_picks(all_picks)
            logger.info(f"Saved {saved_picks} picks")

            # ====================================================================
            # STEP 7: ANALYZE CONSENSUS
            # ====================================================================
            logger.info("Step 6: Analyzing consensus...")
            # Run consensus analyzer to find picks with strong agreement
            # This groups picks by team/player/type and calculates consensus scores
            consensus_picks = self.analyzer.analyze(all_picks)
            logger.info(f"Generated {len(consensus_picks)} consensus picks")

            # ====================================================================
            # STEP 8: SAVE CONSENSUS PICKS TO DATABASE
            # ====================================================================
            logger.info("Step 7: Saving consensus picks...")
            # Save consensus picks to database
            saved_consensus = self._save_consensus_picks(consensus_picks)
            logger.info(f"Saved {saved_consensus} consensus picks")

            # ====================================================================
            # STEP 9: GENERATE STATISTICS
            # ====================================================================
            logger.info("Step 8: Generating statistics...")
            # Calculate statistics about the consensus picks
            stats = self.analyzer.get_statistics(consensus_picks)

            # Get top 10 consensus picks
            top_picks = self.analyzer.get_top_picks(consensus_picks, limit=10)

            # ====================================================================
            # STEP 10: CALCULATE EXECUTION TIME
            # ====================================================================
            # Calculate how long the pipeline took
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # Log completion
            logger.info("=" * 80)
            logger.info("Pipeline execution completed successfully")
            logger.info("=" * 80)

            # ====================================================================
            # STEP 11: RETURN RESULTS
            # ====================================================================
            # Return comprehensive results dictionary
            return {
                "status": "success",  # Pipeline succeeded
                "timestamp": datetime.now().isoformat(),  # When it completed
                "execution_time_seconds": elapsed_time,  # How long it took
                "articles_fetched": len(articles),  # Number of articles fetched
                "articles_saved": saved_articles,  # Number saved to database
                "picks_extracted": len(all_picks),  # Total picks extracted
                "picks_saved": saved_picks,  # Picks saved to database
                "consensus_picks_generated": len(consensus_picks),  # Consensus picks
                "consensus_picks_saved": saved_consensus,  # Saved to database
                "statistics": stats,  # Statistics about consensus picks
                "top_picks": [p.to_dict() for p in top_picks],  # Top 10 picks
            }

        except Exception as e:
            # Handle any errors that occur during pipeline execution
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            # Return error result
            return {
                "status": "failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _fetch_articles(self) -> List[Article]:
        """
        PRIVATE METHOD: Fetch articles from all configured scrapers.

        WHY THIS IS NEEDED:
        - Coordinates fetching from multiple sources
        - Handles errors gracefully
        - Ensures resources are cleaned up

        WHAT IT DOES:
        1. Iterates through all configured scrapers
        2. Calls fetch_articles() on each scraper
        3. Combines results from all sources
        4. Handles errors without stopping
        5. Closes each scraper after use

        RETURNS:
        - List[Article]: All articles from all sources

        USAGE EXAMPLE:
            articles = orchestrator._fetch_articles()
            # Returns articles from ESPN, Bleacher Report, etc.
        """
        # Initialize empty list to store all articles
        all_articles = []

        # STEP 1: Iterate through each configured scraper
        for scraper in self.scrapers:
            try:
                # STEP 2: Fetch articles from this scraper
                articles = scraper.fetch_articles()

                # STEP 3: Add articles to combined list
                all_articles.extend(articles)

                # STEP 4: Log success
                logger.debug(f"Fetched {len(articles)} articles from {scraper.source_name}")

            except Exception as e:
                # STEP 5: Handle errors without stopping
                # Log error but continue with next scraper
                logger.error(f"Error fetching from {scraper.source_name}: {e}")
                continue

            finally:
                # STEP 6: Always close the scraper (cleanup resources)
                # This ensures HTTP connections are closed
                scraper.close()

        # Return all articles from all sources
        return all_articles

    def _save_articles(self, articles: List[Article]) -> int:
        """
        PRIVATE METHOD: Save articles to database.

        WHY THIS IS NEEDED:
        - Persists articles for future reference
        - Allows tracking of which articles were processed
        - Enables deduplication

        PARAMETERS:
        - articles (List[Article]): Articles to save

        RETURNS:
        - int: Number of articles successfully saved

        USAGE EXAMPLE:
            saved_count = orchestrator._save_articles(articles)
            print(f"Saved {saved_count} articles")
        """
        # Initialize counter for saved articles
        saved_count = 0

        # STEP 1: Iterate through each article
        for article in articles:
            try:
                # STEP 2: Save article to database
                article_id = self.database.save_article(article)

                # STEP 3: Check if save was successful
                if article_id:
                    # Store the database ID in the article object
                    article.article_id = article_id
                    # Increment counter
                    saved_count += 1

            except Exception as e:
                # Handle errors without stopping
                logger.error(f"Error saving article: {e}")
                continue

        # Return count of successfully saved articles
        return saved_count

    def _save_picks(self, picks: List[BettingPick]) -> int:
        """
        PRIVATE METHOD: Save picks to database.

        WHY THIS IS NEEDED:
        - Persists extracted picks
        - Allows historical analysis
        - Enables pick accuracy tracking

        PARAMETERS:
        - picks (List[BettingPick]): Picks to save

        RETURNS:
        - int: Number of picks saved

        USAGE EXAMPLE:
            saved_count = orchestrator._save_picks(all_picks)
        """
        # Call database method to save all picks at once
        return self.database.save_picks(picks)

    def _save_consensus_picks(self, consensus_picks: List[ConsensusPick]) -> int:
        """
        PRIVATE METHOD: Save consensus picks to database.

        WHY THIS IS NEEDED:
        - Persists consensus analysis results
        - Allows tracking of consensus over time
        - Enables performance analysis

        PARAMETERS:
        - consensus_picks (List[ConsensusPick]): Consensus picks to save

        RETURNS:
        - int: Number of consensus picks saved

        USAGE EXAMPLE:
            saved_count = orchestrator._save_consensus_picks(consensus_picks)
        """
        # Call database method to save all consensus picks
        return self.database.save_consensus_picks(consensus_picks)

    def close(self):
        """
        PUBLIC METHOD: Clean up resources.

        WHY USE THIS:
        - Closes database connection
        - Releases resources
        - Ensures clean shutdown

        USAGE EXAMPLE:
            orchestrator = BettingConsensusOrchestrator()
            result = orchestrator.run_full_pipeline()
            orchestrator.close()  # Always call this when done
        """
        # Close database connection
        self.database.close()
        # Log closure
        logger.info("Orchestrator closed")


def main():
    """
    FUNCTION: Main entry point for running the orchestrator.

    WHY USE THIS:
    - Provides a clean entry point for command-line execution
    - Handles initialization and cleanup
    - Displays results in a user-friendly format
    - Ensures resources are cleaned up even if errors occur

    WHAT IT DOES:
    1. Creates orchestrator instance
    2. Runs full pipeline
    3. Displays results
    4. Cleans up resources

    USAGE EXAMPLE:
        python3 orchestrator.py
        # Runs the full pipeline and displays results
    """
    # STEP 1: Create orchestrator instance
    # This initializes all components (scrapers, extractors, analyzer, database)
    orchestrator = BettingConsensusOrchestrator()

    try:
        # STEP 2: Run the full pipeline
        # This executes: fetch → extract → analyze → store
        result = orchestrator.run_full_pipeline()

        # STEP 3: Display results
        # Print header
        print("\n" + "=" * 80)
        print("PIPELINE RESULTS")
        print("=" * 80)

        # Print status and timestamp
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")

        # STEP 4: Display detailed results if successful
        if result['status'] == 'success':
            # Display execution metrics
            print(f"Execution Time: {result['execution_time_seconds']:.2f}s")
            print(f"Articles Fetched: {result['articles_fetched']}")
            print(f"Picks Extracted: {result['picks_extracted']}")
            print(f"Consensus Picks: {result['consensus_picks_generated']}")

            # Display statistics
            print("\nStatistics:")
            stats = result['statistics']
            print(f"  Average Consensus Score: {stats['average_consensus_score']:.3f}")
            print(f"  Average Frequency: {stats['average_frequency']:.2f}")
            print(f"  Picks by Type: {stats['picks_by_type']}")

            # Display top 5 consensus picks
            print("\nTop 5 Consensus Picks:")
            for i, pick in enumerate(result['top_picks'][:5], 1):
                # Print pick number, team/player, and type
                print(f"  {i}. {pick['team_or_player']} ({pick['pick_type']})")
                # Print consensus score and frequency
                print(f"     Score: {pick['consensus_score']:.3f}, Frequency: {pick['frequency']}")
        else:
            # Display error message if pipeline failed
            print(f"Error: {result.get('message', 'Unknown error')}")

        # Print footer
        print("=" * 80 + "\n")

    finally:
        # STEP 5: Always clean up resources
        # This ensures database connection is closed even if errors occur
        orchestrator.close()


# ENTRY POINT: Run main() when script is executed directly
if __name__ == "__main__":
    main()

