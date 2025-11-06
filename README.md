# Soccer Betting Consensus System

Scrapes REAL sports prediction websites and generates betting recommendations.

## Websites Scraped

- sportsgambler.com
- sportsmole.co.uk
- footballpredictions.net
- sportytrader.com
- yahoo sports

## Quick Start

```bash
source venv/bin/activate
python3 main.py
```

Enter two teams when prompted:
```
Enter first team: Real Madrid
Enter second team: Barcelona
```

## Output

Returns:
- Which team to bet on
- Consensus score (0-1)
- Source agreement
- Reasoning from each source
- Recommendation level (STRONG BUY, BUY, CONSIDER, WEAK)

## Example Output

```
🏆 BET ON: barcelona
Consensus Score: 0.48
Agreement: 1/1 sources
Average Confidence: 60%
Sources: sportsmole.co.uk

❄️ WEAK - Avoid this bet
Confidence: Low

REASONING
1. sportsmole.co.uk prediction favors Barcelona
```

## Architecture

```
main.py                          # CLI entry point
├── MatchService                 # Team validation & match info
├── RealPredictionService        # Scrapes real websites
└── ConsensusService             # Calculates consensus
```

## Data Storage

Predictions are saved to `prediction_results.json` and can be stored in Supabase (AutoCam project).

## API

```bash
python3 -m uvicorn api.main:app --reload
```

POST `/predict`
```json
{
  "team_a": "Real Madrid",
  "team_b": "Barcelona"
}
```

## Notes

- Scrapes real websites (not mock data)
- Rate limiting between requests (1 second)
- Handles timeouts gracefully
- Returns real predictions from actual sources

