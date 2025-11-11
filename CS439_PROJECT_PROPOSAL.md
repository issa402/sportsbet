# CS439 Project Proposal: Sports Betting Consensus System

## Define Project

### Problem Statement

The main problem that our project aims to solve is to determine whether ensemble consensus methods combined with machine learning models can improve sports betting prediction accuracy beyond individual prediction sources. Currently, sports bettors rely on single prediction sources (Sportsmole, Sky Sports, Pro Soccer Wire, etc.), each with varying accuracy and reliability. These individual sources often provide conflicting predictions for the same match, leaving bettors uncertain about which prediction to trust. Our project will aggregate predictions from multiple sources, apply Bayesian weighting based on historical accuracy, and train machine learning models to identify which sources are most reliable for different match scenarios. This approach will enable bettors to make more informed decisions by leveraging ensemble methods rather than trusting a single source.

### Strategic Aspects

**Data-Driven Prediction Aggregation:** This project utilizes data science techniques to combine multiple prediction sources into a single, more reliable consensus prediction. By analyzing historical prediction accuracy across sources, we can weight predictions based on past performance, directly improving prediction reliability for future matches.

**Understanding Source Reliability:** Sports prediction sources vary significantly in accuracy due to different methodologies, data sources, and expertise. Our project strategically incorporates Bayesian weighting to identify which sources are most reliable, allowing us to dynamically adjust confidence levels based on historical performance patterns.

**Real-Time Data Integration:** The project combines real-time prediction scraping with live match result tracking, enabling continuous model training and evaluation. This creates a feedback loop where the system learns from each match outcome and improves future predictions.

**Machine Learning Model Ensemble:** We will implement multiple ML models (Logistic Regression, Naive Bayes, Linear Regression) to learn which prediction sources are most reliable for different match types, team combinations, and leagues. Each model will be trained on historical data and validated using cross-validation techniques.

## Course Relation to Lectures and Discussions

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

## Project Plan

### Phase 1: Data Collection (Week 1-2)
- Scrape predictions from 3+ sources (Sportsmole, Sky Sports, Pro Soccer Wire) using Playwright
- Scrape real-time match results from BBC Sport and Flashscore
- Collect historical team data (last 5 matches, head-to-head records)
- Store all data in structured format for analysis

### Phase 2: Feature Engineering (Week 2-3)
- Extract features: team form (wins/losses/draws), head-to-head records, prediction consensus
- Calculate source accuracy metrics from historical data
- Create Bayesian weights based on source reliability
- Normalize and scale features for ML models

### Phase 3: Model Development (Week 3-4)
- Implement Logistic Regression for binary classification (win/loss)
- Implement Naive Bayes for multi-class classification (win/loss/draw)
- Implement Linear Regression for score prediction
- Train models using 80% of historical data

### Phase 4: Evaluation & Validation (Week 4-5)
- Validate models using 20% test data
- Calculate accuracy, precision, recall, F1-score
- Compare ensemble accuracy vs. individual source accuracy
- Perform cross-validation to ensure model robustness

### Phase 5: Analysis & Reporting (Week 5-6)
- Visualize prediction accuracy trends over time
- Analyze which sources are most reliable by league/team
- Create performance comparison charts
- Generate final report with findings and recommendations

## Expected Outcomes

- **Baseline Accuracy:** Individual sources achieve 50-65% accuracy
- **Ensemble Accuracy:** Consensus method achieves 70-75% accuracy
- **Model Improvement:** ML models improve accuracy to 75-80%
- **Source Reliability:** Identify which sources are most reliable for different scenarios
- **Practical Tool:** Functional system that can predict match outcomes for new matches

## Technical Stack

- **Web Scraping:** Playwright, BeautifulSoup4
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (Logistic Regression, Naive Bayes, Linear Regression)
- **Visualization:** Matplotlib, Seaborn
- **APIs:** The Odds API (betting odds), football.json (historical data)
- **Version Control:** Git, GitHub

