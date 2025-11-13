# CS439 Project Proposal: Sports Betting Consensus System

## Define Project

### Problem Statement

The main problem that our project aims to solve is to determine whether ensemble consensus methods combined with machine learning models can improve sports betting prediction accuracy beyond individual prediction sources. Currently, sports bettors rely on single prediction sources (Sportsmole, Sky Sports, Pro Soccer Wire, etc.), each with varying accuracy and reliability. These individual sources often provide conflicting predictions for the same match, leaving bettors uncertain about which prediction to trust. Our project will aggregate predictions from multiple sources, apply Bayesian weighting based on historical accuracy, and train machine learning models to identify which sources are most reliable for different match scenarios. This approach will enable bettors to make more informed decisions by leveraging ensemble methods rather than trusting a single source.

### Strategic Aspects

**Data-Driven Prediction Aggregation:** This project utilizes data science techniques to combine multiple prediction sources into a single, more reliable consensus prediction. By analyzing historical prediction accuracy across sources, we can weight predictions based on past performance, directly improving prediction reliability for future matches.

**Understanding Source Reliability:** Sports prediction sources vary significantly in accuracy due to different methodologies, data sources, and expertise. Our project strategically incorporates Bayesian weighting to identify which sources are most reliable, allowing us to dynamically adjust confidence levels based on historical performance patterns.

**Real-Time Data Integration:** The project combines real-time prediction scraping with live match result tracking, enabling continuous model training and evaluation. This creates a feedback loop where the system learns from each match outcome and improves future predictions.

**Machine Learning Model Ensemble:** We will implement multiple ML models (Logistic Regression, Naive Bayes, Linear Regression) to learn which prediction sources are most reliable for different match types, team combinations, and leagues. Each model will be trained on historical data and validated using cross-validation techniques.

### Course Relation to Lectures and Discussions

This project demonstrates key CS439 concepts:

- **Bayes Theorem & Probability:** Bayesian weighting of prediction sources based on historical accuracy
- **Naive Bayes Classification:** Classify match outcomes (win/loss/draw) using source predictions as features
- **Logistic Regression:** Binary classification for match outcomes (team wins vs. doesn't win)
- **Linear Regression:** Predict exact match scores using ensemble predictions
- **Gradient Descent:** Train models to minimize prediction error
- **Feature Engineering:** Create features from team statistics, form, head-to-head records, and prediction consensus
- **Model Evaluation:** Calculate accuracy, precision, recall, and R² scores
- **Training/Test Data:** Split historical data for proper model validation

## Novelty and Importance

**Gap in Current Research:** Most sports betting analysis focuses on single prediction sources or simple averaging. Our project addresses the gap by implementing Bayesian weighting and machine learning to identify which sources are most reliable for specific match scenarios.

**Real-World Applicability:** Sports betting is a multi-billion dollar industry. Improving prediction accuracy by even 5-10% has significant financial implications for bettors. Our ensemble approach provides a practical, data-driven method for improving betting decisions.

**Accessibility:** While professional betting syndicates use proprietary models, our project demonstrates that ensemble methods can be implemented using freely available prediction sources and open-source tools, making this approach accessible to individual bettors.

**Continuous Learning:** Unlike static models, our system continuously learns from match outcomes, adapting to changing source reliability over time.

## Plan

### Data Collection Strategy

**A. Prediction Data Collection:**
- Scrape predictions from 3+ sources (Sportsmole, Sky Sports, Pro Soccer Wire) using Playwright
- Implement data quality checks at collection points
- Validate prediction format and consistency
- Create error handling for failed scrapes

**B. Real-Time Results Collection:**
- Scrape actual match results from BBC Sport and Flashscore
- Implement real-time data validation
- Create duplicate detection procedures
- Set up error logging system

**C. Historical Team Data Collection:**
- Extract team form data (last 5 matches for each team)
- Collect head-to-head match history between teams
- Gather team statistics (wins, draws, losses, win percentage)
- Implement data quality checks for historical data

### Data Storage and Organization

**A. Data Structure:**
- Organize data into Pandas DataFrames for analysis
- Create structured format: [team_a, team_b, pred1, pred2, pred3, form_a, form_b, h2h, actual_result]
- Implement data validation rules and constraints
- Create data archival procedures for historical matches

**B. Feature Engineering:**
- Extract team form percentage (wins/total matches)
- Calculate head-to-head advantage metrics
- Compute prediction consensus scores (votes/total sources)
- Calculate source reliability weights from historical data
- Normalize and scale features for ML models

### Machine Learning Models and Techniques

**A. Model Selection:**
- **Logistic Regression:** Binary classification (team wins or doesn't win)
- **Naive Bayes:** Multi-class classification (win/loss/draw outcomes)
- **Linear Regression:** Predict exact match scores

**B. Model Training:**
- Split data into 80% training and 20% testing sets
- Implement cross-validation procedures
- Create model validation pipelines
- Set up model versioning for tracking improvements

**C. Bayesian Weighting:**
- Calculate source accuracy from historical predictions
- Weight each source by reliability (accurate sources get higher weight)
- Dynamically adjust weights as new data arrives
- Create weighted consensus predictions

### Implementation Steps

**Phase 1: Data Collection (Nov 14-20)**
- Collect predictions from 3 sources for 20-30 matches
- Scrape actual match results
- Extract team historical data
- Validate data quality

**Phase 2: Feature Engineering (Nov 21-25)**
- Extract features from raw data
- Calculate source accuracy weights
- Create feature vectors for ML models
- Normalize and scale features

**Phase 3: Model Training (Nov 26-Dec 1)**
- Train Logistic Regression model
- Train Naive Bayes model
- Train Linear Regression model
- Implement cross-validation

**Phase 4: Evaluation (Dec 2-5)**
- Test models on held-out test data
- Calculate accuracy, precision, recall, R² scores
- Compare individual sources vs. ensemble vs. ML models
- Analyze which sources are most reliable

**Phase 5: Reporting (Dec 6-9)**
- Visualize prediction accuracy trends
- Create comparison charts (individual vs. ensemble vs. ML)
- Generate final report with findings
- Document limitations and future improvements

### Evaluation Metrics

- **Accuracy:** Percentage of correct predictions
- **Precision:** When we predict X, how often are we right?
- **Recall:** Out of all actual X outcomes, how many did we predict?
- **R² Score:** For score prediction, how close are we to actual scores?
- **Baseline Comparison:** Individual sources (50-65%) vs. Ensemble (70-75%) vs. ML models (75-80%)

### Success Criteria

- Achieve 75-80% accuracy with ML models
- Demonstrate 10-15% improvement over individual sources
- Identify which sources are most reliable
- Show that ensemble + ML outperforms single sources
