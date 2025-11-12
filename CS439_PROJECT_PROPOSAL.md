# CS439 Project Proposal: Sports Betting Consensus System

## Problem Statement

**Question:** Can ensemble consensus methods + ML models improve sports betting prediction accuracy?

**Current Problem:** Sports bettors use single prediction sources (Sportsmole, Sky Sports, Pro Soccer Wire) that often conflict and have unknown reliability.

**Our Solution:**
1. Aggregate predictions from 3+ sources
2. Weight sources by historical accuracy (Bayesian weighting)
3. Train ML models to identify which sources are most reliable
4. Achieve 75-80% accuracy vs. 50-65% from individual sources

**Why It Matters:** Sports betting is a multi-billion dollar industry. Even 5-10% accuracy improvement has significant financial impact.

## CS439 Concepts Used

| Concept | Application |
|---------|-------------|
| **Bayes Theorem** | Weight prediction sources by historical accuracy |
| **Naive Bayes** | Classify match outcomes (win/loss/draw) |
| **Logistic Regression** | Binary classification (team wins or not) |
| **Linear Regression** | Predict exact match scores |
| **Gradient Descent** | Train models to minimize error |
| **Feature Engineering** | Extract team form, H2H, consensus scores |
| **Model Evaluation** | Accuracy, precision, recall, R² scores |
| **Train/Test Split** | 80% training, 20% testing |

## Project Timeline

| Phase | Tasks | Timeline |
|-------|-------|----------|
| **1. Data Collection** | Scrape predictions (3 sources), match results, team history | Nov 14-20 |
| **2. Feature Engineering** | Extract team form, H2H, consensus, source weights | Nov 21-25 |
| **3. Model Training** | Train Logistic Regression, Naive Bayes, Linear Regression | Nov 26-Dec 1 |
| **4. Evaluation** | Test accuracy, compare models, cross-validate | Dec 2-5 |
| **5. Reporting** | Visualize results, write final report | Dec 6-9 |

## Expected Results

- Individual sources: 50-65% accuracy
- Ensemble consensus: 70-75% accuracy
- ML models: 75-80% accuracy

## Tech Stack

Playwright • BeautifulSoup4 • Pandas • NumPy • Scikit-learn • Matplotlib • Git

