# Sports Betting Consensus System - Project Overview

## What This Project Does (In Plain English)

**The Problem:**
- Sports bettors use prediction websites (Sportsmole, Sky Sports, Pro Soccer Wire)
- These sites often disagree on who will win a match
- Bettors don't know which site to trust
- Individual sites are only 50-65% accurate

**Our Solution:**
1. Scrape predictions from 3 prediction websites
2. Scrape actual match results
3. Track how accurate each website was for each team
4. Use Bayesian weighting to combine predictions intelligently
5. Train ML models to learn which sources are most reliable
6. Achieve 75-80% accuracy (vs 50-65% for individual sources)

**The Result:**
- Better predictions by combining multiple sources
- Understand which sources are most reliable
- Prove that ensemble + ML beats individual sources

---

## How It Works (Step by Step)

### Step 1: Data Collection
```
Real Betis (HOME) vs Celta Vigo (AWAY)

Sportsmole predicts: "Real Betis Win"
Sky Sports predicts: "Real Betis Win"
Pro Soccer Wire predicts: "Draw"

Actual result: Real Betis 2-1 Celta Vigo (Real Betis Win)
```

### Step 2: Track Source Accuracy
```
Real Betis (Last 5 Matches):
  - Sportsmole: 80% accurate (4/5 correct)
  - Sky Sports: 100% accurate (5/5 correct)
  - Pro Soccer Wire: 60% accurate (3/5 correct)

Celta Vigo (Last 5 Matches):
  - Sportsmole: 70% accurate
  - Sky Sports: 90% accurate
  - Pro Soccer Wire: 50% accurate
```

### Step 2.5: Track Home/Away Performance
```
Real Betis:
  - At HOME: 60% win rate (3/5)
  - AWAY: 40% win rate (2/5)

Celta Vigo:
  - At HOME: 40% win rate (2/5)
  - AWAY: 20% win rate (1/5)

Real Betis is playing at HOME → Better chance to win!
```

### Step 3: Apply Bayesian Weighting
```
Without weighting (equal):
  (1 + 1 + 0) / 3 = 67% confidence for Real Betis Win

With team-specific weighting (smart):
  Real Betis weights: 80% + 100% + 60% = 240%
  Weighted consensus: 240% / 3 = 80% confidence
  
Result: Better confidence estimate!
```

### Step 4: Train ML Models
```
Features for each match:
  - Team A form (last 5 matches)
  - Team B form (last 5 matches)
  - Head-to-head history
  - Source predictions
  - Source accuracy for each team
  
Models trained:
  - Logistic Regression (binary: win or not)
  - Naive Bayes (multi-class: win/loss/draw)
  - Linear Regression (exact score prediction)
```

### Step 5: Evaluate & Compare
```
Individual sources: 50-65% accuracy
Ensemble (equal weighting): 70-75% accuracy
Ensemble + ML models: 75-80% accuracy ← BEST!
```

---

## 6 Features We Use

| Feature | What It Is | Example |
|---------|-----------|---------|
| **Team A Form** | Win % from last 5 matches | Real Betis: 60% (3/5) |
| **Team B Form** | Win % from last 5 matches | Celta Vigo: 40% (2/5) |
| **Head-to-Head** | Team A win % vs Team B | Real Betis: 80% (4/5) |
| **Source Predictions** | Consensus from 3 websites | 2/3 say Real Betis Win |
| **Source Accuracy** | How accurate each source is for that team | Sky Sports: 100% for Real Betis |
| **Home/Away Stats** | How teams play at home vs away | Real Betis: 60% home, 40% away |

## CS439 Concepts Used

| Concept | How We Use It |
|---------|---------------|
| **Bayes Theorem** | Weight sources by historical accuracy |
| **Naive Bayes** | Classify match outcomes (W/L/D) |
| **Logistic Regression** | Binary classification (team wins or not) |
| **Linear Regression** | Predict exact match scores |
| **Gradient Descent** | Train models to minimize error |
| **Feature Engineering** | Extract team form, H2H, consensus scores, home/away |
| **Model Evaluation** | Accuracy, precision, recall, R² |
| **Train/Test Split** | 80% training, 20% testing |

---

## Current Status

✅ **COMPLETED:**
- Web scraping system (Playwright + BeautifulSoup)
- Prediction data collection (3 sources working)
- Real-time results collection (BBC Sport, Flashscore)
- Historical team data (last 5 matches + H2H)
- Source reliability tracking (accuracy per team)

⏳ **TODO:**
- Collect 20-30 matches with all data
- Feature engineering pipeline
- Train ML models
- Evaluate and compare accuracy
- Generate final report

---

## Timeline

- **Nov 14-20:** Data Collection (20-30 matches)
- **Nov 21-25:** Feature Engineering
- **Nov 26-Dec 1:** Model Training
- **Dec 2-5:** Evaluation
- **Dec 6-9:** Final Report

