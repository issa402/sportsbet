# Technical Flow & Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPORTS BETTING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

INPUT: "Man City vs Liverpool"
   ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA COLLECTION                                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Prediction Scraper (prediction_scraper_real.py)             │
│    └─ Sportsmole, Sky Sports, Pro Soccer Wire                  │
│    └─ Output: ["2-1", "1-1", "2-1"]                            │
│                                                                  │
│ 2. Historical Data (historical_data_service.py)                │
│    └─ Man City last 5: [W, W, W, W, W] → 100%                 │
│    └─ Liverpool last 5: [L, W, D, W, L] → 40%                 │
│    └─ H2H last 5: [MC-W, MC-W, MC-W, Draw, MC-W]              │
│                                                                  │
│ 3. Real-Time Results (realtime_data_service.py)               │
│    └─ Wait for match to finish                                 │
│    └─ Scrape actual result: "3-0 Man City"                     │
└─────────────────────────────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: FEATURE ENGINEERING                                    │
├─────────────────────────────────────────────────────────────────┤
│ Raw Data → Features:                                            │
│                                                                  │
│ Predictions:                                                    │
│   - consensus_score = 2/3 agree on Man City                    │
│   - prediction_variance = low (2 same, 1 different)            │
│                                                                  │
│ Team Form:                                                      │
│   - team_a_win_pct = 100                                       │
│   - team_b_win_pct = 40                                        │
│   - form_difference = 60                                       │
│                                                                  │
│ Head-to-Head:                                                   │
│   - h2h_team_a_wins = 4                                        │
│   - h2h_team_b_wins = 0                                        │
│   - h2h_advantage = "Team A"                                   │
│                                                                  │
│ Source Reliability (from historical data):                      │
│   - sportsmole_accuracy = 0.80                                 │
│   - skysports_accuracy = 0.40                                  │
│   - prosoccer_accuracy = 0.75                                  │
│                                                                  │
│ Final Feature Vector:                                           │
│   [100, 40, 60, 4, 0, 1, 2/3, 0.80, 0.40, 0.75]              │
└─────────────────────────────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: ML MODEL TRAINING                                      │
├─────────────────────────────────────────────────────────────────┤
│ Model 1: Logistic Regression (Binary Classification)           │
│   Input: Feature vector                                        │
│   Output: P(Team A wins) = 0.92                                │
│   Learns: "When form_diff > 50% → Team A wins"                │
│                                                                  │
│ Model 2: Naive Bayes (Multi-class Classification)             │
│   Input: Feature vector                                        │
│   Output: P(Win)=0.85, P(Draw)=0.10, P(Loss)=0.05            │
│   Learns: "When h2h favors A → A wins 85%"                    │
│                                                                  │
│ Model 3: Linear Regression (Score Prediction)                 │
│   Input: Feature vector                                        │
│   Output: Predicted score = 2.5-1.2                           │
│   Learns: "When form_diff=60% → expect 2.5 goals"             │
└─────────────────────────────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: PREDICTION                                             │
├─────────────────────────────────────────────────────────────────┤
│ Ensemble Prediction:                                            │
│   - Sportsmole: "2-1 Man City" (weight: 0.80)                 │
│   - Sky Sports: "1-1 Draw" (weight: 0.40)                     │
│   - ProSoccer: "2-1 Man City" (weight: 0.75)                  │
│   → Weighted consensus: "2-1 Man City" (confidence: 78%)       │
│                                                                  │
│ ML Predictions:                                                 │
│   - Logistic Regression: "Man City wins" (92%)                │
│   - Naive Bayes: "Man City wins" (85%)                        │
│   - Linear Regression: "2.5-1.2 Man City"                     │
│                                                                  │
│ Final Prediction: "Man City 2-1 Liverpool" (confidence: 85%)   │
└─────────────────────────────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: EVALUATION                                             │
├─────────────────────────────────────────────────────────────────┤
│ Actual Result: "Man City 3-0 Liverpool"                        │
│                                                                  │
│ Accuracy Check:                                                 │
│   - Sportsmole: ✅ Correct (predicted Man City wins)           │
│   - Sky Sports: ❌ Wrong (predicted draw)                      │
│   - ProSoccer: ✅ Correct (predicted Man City wins)            │
│   - Ensemble: ✅ Correct (2/3 voted Man City)                 │
│   - ML Models: ✅ Correct (all predicted Man City)             │
│                                                                  │
│ Update Accuracy Metrics:                                        │
│   - Sportsmole: 80% → 80.5%                                   │
│   - Sky Sports: 40% → 39.5%                                   │
│   - ProSoccer: 75% → 75.5%                                    │
│   - Ensemble: 70% → 71%                                       │
│   - ML Models: 75% → 76%                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
MATCH DATA COLLECTION:
┌──────────────────┐
│ User Input       │ "Man City vs Liverpool"
└────────┬─────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Prediction Scraper                                           │
│ ├─ Sportsmole: "2-1"                                        │
│ ├─ Sky Sports: "1-1"                                        │
│ └─ ProSoccer: "2-1"                                         │
└────────┬─────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Historical Data Service                                      │
│ ├─ Man City last 5: [W, W, W, W, W]                        │
│ ├─ Liverpool last 5: [L, W, D, W, L]                       │
│ └─ H2H last 5: [MC-W, MC-W, MC-W, Draw, MC-W]              │
└────────┬─────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Pandas DataFrame (Training Data)                             │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ team_a | team_b | pred1 | pred2 | pred3 | form_a |... │  │
│ │ Man C  | Liv    | 2-1   | 1-1   | 2-1   | 100%  |... │  │
│ │ Ars    | Che    | 2-1   | 1-1   | 1-0   | 100%  |... │  │
│ │ ...    | ...    | ...   | ...   | ...   | ...   |... │  │
│ └────────────────────────────────────────────────────────┘  │
└────────┬─────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Train/Test Split (80/20)                                     │
│ ├─ Training: 16-24 matches                                  │
│ └─ Testing: 4-6 matches                                     │
└────────┬─────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ ML Models                                                    │
│ ├─ Logistic Regression                                      │
│ ├─ Naive Bayes                                              │
│ └─ Linear Regression                                        │
└────────┬─────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Evaluation Metrics                                           │
│ ├─ Accuracy: 76%                                            │
│ ├─ Precision: 78%                                           │
│ ├─ Recall: 74%                                              │
│ └─ R² Score: 0.72                                           │
└──────────────────────────────────────────────────────────────┘
```

## File Structure

```
/home/iscjmz/auto/
├── services/
│   ├── prediction_scraper_real.py      ✅ DONE
│   ├── realtime_data_service.py        ✅ DONE
│   ├── historical_data_service.py      ✅ DONE
│   ├── consensus_service.py            ⏳ TODO
│   ├── feature_engineering.py          ⏳ TODO
│   └── ml_models.py                    ⏳ TODO
├── core/
│   ├── logger.py                       ✅ DONE
│   └── models.py                       ✅ DONE
├── CS439_PROJECT_PROPOSAL.md           ✅ UPDATED
├── IMPLEMENTATION_STATUS.md            ✅ NEW
└── TECHNICAL_FLOW.md                   ✅ NEW
```

## Next Steps

1. **Collect 20-30 matches** with all data
2. **Create feature_engineering.py** to extract features
3. **Create ml_models.py** to train models
4. **Create consensus_service.py** to combine predictions
5. **Evaluate and compare** accuracy
6. **Generate final report** with visualizations

