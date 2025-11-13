# Sports Betting Consensus System - Implementation Status

## 🎯 Project Overview

**Goal:** Prove that ensemble consensus methods + ML models improve sports betting prediction accuracy

**Research Question:** Can we beat 65% accuracy (individual sources) by combining predictions + ML?

**Expected Outcome:** 75-80% accuracy using ensemble + ML models

---

## ✅ WHAT WE HAVE (COMPLETED)

### 1. Data Collection Infrastructure

#### Prediction Scraper (`prediction_scraper_real.py`)
- ✅ Scrapes predictions from **3 working sources**:
  - Sportsmole: "Man City 2-1 Liverpool"
  - Sky Sports: "1-1 Draw"
  - Pro Soccer Wire: "Man City 2-1 Liverpool"
- ✅ Uses Playwright for JavaScript rendering
- ✅ Tested on multiple matches (Celta Vigo vs Barcelona, Man City vs Liverpool)

#### Real-Time Results (`realtime_data_service.py`)
- ✅ Scrapes actual match results from BBC Sport & Flashscore
- ✅ Successfully extracted: "Manchester City 3-0 Liverpool" (Nov 9, 2025)
- ✅ Real-time data (not future dates like football.json)

#### Historical Data (`historical_data_service.py`)
- ✅ Gets **Team A's last 5 matches** (any opponent)
- ✅ Gets **Team B's last 5 matches** (any opponent)
- ✅ Gets **Head-to-head last 5 matches** between teams
- ✅ Calculates form stats: wins, draws, losses, win %
- ✅ **NEW:** Gets **Home/Away performance stats** for each team
- ✅ Example output:
  - Man City: 5W-0D-0L (100% win rate)
  - Liverpool: 2W-1D-2L (40% win rate)
  - H2H: Man City 4-0-1 vs Liverpool
  - Man City Home: 60% win rate | Away: 40% win rate
  - Liverpool Home: 80% win rate | Away: 20% win rate

### 2. Data Structure Ready

For each match, we collect:
```
{
  "team_a": "Manchester City",
  "team_b": "Liverpool",
  "predictions": {
    "sportsmole": "2-1",
    "skysports": "1-1",
    "prosoccer": "2-1"
  },
  "team_a_form": {"wins": 5, "draws": 0, "losses": 0, "win_pct": 100},
  "team_b_form": {"wins": 2, "draws": 1, "losses": 2, "win_pct": 40},
  "h2h": [5 matches with dates, scores, winners],
  "actual_result": "3-0 Manchester City"
}
```

### 3. Version Control
- ✅ Created `document-sport` branch
- ✅ All code pushed and working
- ✅ Ready for `proposal-stages` branch

---

## 🔄 THE WORKFLOW (HOW IT WORKS)

### Step 1: User Input
```
User: "Predict Man City vs Liverpool"
```

### Step 2: Data Collection
```
System collects:
1. Predictions from 3 sources
2. Man City's last 5 matches + stats
3. Liverpool's last 5 matches + stats
4. Man City vs Liverpool H2H last 5 matches
```

### Step 3: Feature Engineering
```
6 Features created:
1. team_a_form_pct = 100 (Man City)
2. team_b_form_pct = 40 (Liverpool)
3. h2h_advantage = Man City (4-0-1)
4. prediction_consensus = 2/3 agree on Man City
5. source_accuracy = [Sportsmole: 0.8, Sky Sports: 1.0, ProSoccer: 0.6]
6. home_away_stats = Man City HOME (60%), Liverpool AWAY (20%)
```

### Step 4: ML Model Prediction
```
Logistic Regression learns:
"When form_diff > 50% AND h2h favors team_a AND 2/3 sources agree
→ team_a wins 90% of the time"

Naive Bayes learns:
"When form_diff ≈ 0% AND sources disagree
→ draw 60% of the time"

Linear Regression learns:
"When form_diff = 60%, expected score = 2.5-1.2"
```

### Step 5: Match Happens
```
Actual result: Man City 3-0 Liverpool
```

### Step 6: Evaluation
```
Sportsmole: ✅ Correct (predicted 2-1, team won)
Sky Sports: ❌ Wrong (predicted 1-1, Man City won)
ProSoccer: ✅ Correct (predicted 2-1, team won)
Ensemble: ✅ Correct (2/3 voted Man City)
ML Model: ✅ Correct (predicted Man City win)
```

### Step 7: Learning
```
System updates:
- Sportsmole accuracy: 80% → 81%
- Sky Sports accuracy: 40% → 39%
- ProSoccer accuracy: 80% → 81%
- ML model improves for next prediction
```

---

## ❌ WHAT'S MISSING (TODO)

### Phase 1: Data Collection (IN PROGRESS)
- [ ] Collect 20-30 matches with all data
- [ ] Store in Pandas DataFrame
- [ ] Validate data quality

### Phase 2: Feature Engineering (NOT STARTED)
- [ ] Create feature extraction pipeline
- [ ] Calculate source accuracy weights
- [ ] Normalize features for ML

### Phase 3: Model Training (NOT STARTED)
- [ ] Implement Logistic Regression
- [ ] Implement Naive Bayes
- [ ] Implement Linear Regression
- [ ] Train on 80% of data

### Phase 4: Evaluation (NOT STARTED)
- [ ] Test on 20% of data
- [ ] Calculate accuracy, precision, recall
- [ ] Compare: Individual vs Ensemble vs ML
- [ ] Cross-validation

### Phase 5: Reporting (NOT STARTED)
- [ ] Visualize results
- [ ] Create comparison charts
- [ ] Write final report

---

## 📊 DATASET EXAMPLE (WHAT WE'LL HAVE)

After collecting 20-30 matches:

| Match | Team A | Team B | Pred1 | Pred2 | Pred3 | FormA | FormB | H2H | Actual |
|-------|--------|--------|-------|-------|-------|-------|-------|-----|--------|
| 1 | Man C | Liv | 2-1 | 1-1 | 2-1 | 100% | 40% | 4-0 | 3-0 MC |
| 2 | Ars | Che | 2-1 | 1-1 | 1-0 | 100% | 50% | 2-0 | 2-1 Ars |
| 3 | Liv | Bri | 2-0 | 1-1 | 1-0 | 40% | 30% | 3-0 | 2-0 Liv |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 🛠️ TECH STACK

- **Scraping:** Playwright, BeautifulSoup4
- **Data:** Pandas, NumPy
- **ML:** Scikit-learn (Logistic Regression, Naive Bayes, Linear Regression)
- **Viz:** Matplotlib, Seaborn
- **Version Control:** Git, GitHub

---

## 📅 TIMELINE

- ✅ Nov 13: Proposal submitted
- ⏳ Nov 14-20: Collect 20-30 matches
- ⏳ Nov 21-25: Feature engineering
- ⏳ Nov 26-Dec 1: Model training
- ⏳ Dec 2-5: Evaluation
- ⏳ Dec 6-9: Final report

