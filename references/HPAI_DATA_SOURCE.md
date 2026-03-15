# HPAI Data: Automated Download from APHIS

## Source

USDA APHIS publishes confirmed HPAI (Highly Pathogenic Avian Influenza) flock detections through a public Tableau dashboard. The underlying data is available as a CSV export at:

```
https://publicdashboards.dl.usda.gov/t/MRP_PUB/views/
  VS_Avian_HPAIConfirmedDetections2022/HPAI2022ConfirmedDetections.csv
```

This is the same dataset that powers the [APHIS HPAI Confirmed Detections dashboard](https://publicdashboards.dl.usda.gov/t/MRP_PUB/views/VS_Avian_HPAIConfirmedDetections2022/HPAI2022ConfirmedDetections). No API key is required.

## How It Works

The pipeline (`hpai_client.py`) downloads the CSV directly using Python's stdlib `urllib.request` -- no third-party packages needed.

1. **Download**: `GET` request to the Tableau CSV endpoint with a 120-second timeout
2. **Decode**: Tries UTF-8 first, then UTF-16 and Latin-1 (Tableau exports vary)
3. **Validate**: Checks that the CSV header contains expected columns (`Confirmed`, `State`)
4. **Parse**: `csv.DictReader` produces a list of row dicts

The parser (`parsers.py: parse_hpai_record`) then normalizes each row:

| CSV Column | DB Field | Notes |
|---|---|---|
| `Confirmed` | `detection_date` | Datetime like `4/12/2024 12:00:00 AM`, normalized to `YYYY-MM-DD` |
| `State` | `state` | |
| `County Name` | `county` | |
| `Production` | `flock_type` | e.g. "Commercial - Table Egg Layer", "Backyard" |
| `Birds Affected` | `flock_size` | Integer, can be comma-separated |

Column matching is fuzzy (case-insensitive substring) to handle Tableau's inconsistent naming.

## Running It

```bash
# Initial backfill (downloads full CSV, ~2,100+ rows from Feb 2022 onward)
python3 ingest.py --backfill-hpai

# Incremental update (same command -- upserts based on unique constraint)
python3 ingest.py --update
```

The `hpai_detections` table has a unique constraint on `(detection_date, state, county, species, flock_type, flock_size)`, so re-running is safe and idempotent.

## Caveats

- **No official API**: This relies on the Tableau public CSV export URL, which could change without notice.
- **Full download each time**: The CSV endpoint returns the complete dataset (~2K+ rows), not incremental updates. The upsert handles deduplication.
- **Date format changed**: Tableau exports dates as `M/D/YYYY H:MM:SS AM/PM`. The parser handles this along with several other date formats as a fallback.
