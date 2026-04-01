# Chartbook Data Sources

Quick reference for all data feeds, their update frequencies, and which dashboard charts they power.

---

## MARS Reports (USDA AMS Market News)

| Slug | Report Name | Table | Frequency | Dashboard Chart(s) |
|------|------------|-------|-----------|-------------------|
| **2843** | Daily National Shell Egg Index | `egg_prices` | Daily (M-F) | **Wholesale Prices** (Caged series), Egg Volumes, Sentiment Index |
| **2734** | Daily New York Shell Egg | `egg_prices` | Daily (M-F) | **Wholesale Prices** (NY Large/Extra Large/Medium) |
| **3888** | Daily National Breaking Stock | `egg_prices` | Daily (M-F) | **Wholesale Prices** (Breaking Stock, Undergrades) |
| **2848** | Weekly Combined Regional Shell Egg | `egg_prices` | Weekly | Regional Egg Prices |
| **2842** | Weekly National Egg Products | `egg_prices` | Weekly | (narratives only) |
| **1427** | National Weekly Shell Egg Inventory | `egg_inventory` | Weekly | Egg Inventory |
| **1665** | Weekly Shell Eggs Processed | `eggs_processed` | Weekly | Eggs Processed |
| **1624** | Weekly Poultry & Egg Cold Storage | `cold_storage` | Weekly | Cold Storage (MARS) |
| **3646** | Weekly National Chicken Report | `chicken_wholesale` | Weekly | Chicken Wholesale Prices |
| **3649** | Monthly National Chicken Report | `chicken_wholesale` | Monthly | Chicken Wholesale Prices |
| **2756** | Weekly Retail Chicken Feature Activity | `retail_prices` | Weekly | Retail Chicken Prices/Features |
| **2757** | Weekly Retail Egg Feature Activity | `retail_prices` | Weekly | Retail Egg Prices/Features |

### Wholesale Prices Chart (egg-dashboard)
The "Wholesale Prices" chart on the egg dashboard combines three MARS reports:
- **Slug 2843**: Caged Large (National, White, Graded Loose) → "Wholesale Price" line (5-day rolling avg of `wtd_avg_price`)
- **Slug 3888**: Breaking Stock and Undergrades → "Breaking Stock" and "Undergrades" lines (`avg_price`)
- **Slug 2734**: NY Shell Egg by class → "NY Large", "NY Extra Large", "NY Medium" lines (`avg_price`)

Built by `build_egg_index()` in `build_dashboard.py`.

---

## NASS (USDA National Agricultural Statistics Service)

| Series | Table | Frequency | Dashboard Chart(s) |
|--------|-------|-----------|-------------------|
| Layer Inventory (Table + Hatching) | `nass_data` | Monthly | NASS Layers |
| Egg Production (Total + Table) | `nass_data` | Monthly | Egg Production |
| Rate of Lay (All + Table) | `nass_data` | Monthly | Rate of Lay |
| Replacement Pullet Inventory | `nass_data` | Monthly | NASS Pullets |
| Broiler/Egg-Type Chicks Hatched | `nass_data` | Monthly | Hatchery |
| Placements (Broiler + Pullet) | `nass_data` | Weekly | Placements |
| Egg/Broiler Price Received | `nass_data` | Monthly | NASS Prices |
| Cold Storage (Chicken + Egg) | `nass_data` | Monthly | Cold Storage (NASS) |
| Shell Eggs Broken | `nass_data` | Monthly | Shell Broken |

---

## FRED (Federal Reserve Economic Data)

| Series ID | Description | Dashboard Chart(s) |
|-----------|-------------|-------------------|
| PMAIZMTUSDM | Global Corn Price | Feed Index (input) |
| PSMEAUSDM | Global Soybean Meal Price | Feed Index (input) |
| WPU0171 | PPI: Chicken Eggs | PPI chart |
| WPU0141 | PPI: Slaughter Chickens | PPI chart |
| APU0000708111 | Retail Egg Price (Grade A, Large) | FRED Retail Egg |
| GASDESW | US Diesel Price | FRED Diesel |

---

## CME Feed Index

| Source | Table | Frequency | Dashboard Chart(s) |
|--------|-------|-----------|-------------------|
| Google Sheets (manual + CME delayed quotes) | `cme_feed_daily` | Daily | **Layer Feed Index** |

The Layer Feed Index chart reads from `cme_feed_daily` which contains a reconstructed daily ration cost:
- 67% corn, 22% soybean meal, 8% calcium, 3% other
- Indexed to 100 on 2026-01-01
- Built by `build_feed_index()` in `build_dashboard.py`

---

## HPAI (USDA APHIS)

| Source | Table | Frequency | Dashboard Chart(s) |
|--------|-------|-----------|-------------------|
| "A Table by Confirmation Date.csv" (manual preferred) | `hpai_detections` | As updated | HPAI Summary, HPAI by State, HPAI Layers |
| Tableau direct endpoint (fallback) | `hpai_detections` | As updated | Same |

The manual CSV (UTF-16 crosstab from Tableau "Download Data" dialog) has exact flock counts. The Tableau direct endpoint returns rounded values (e.g., "0.1M"). Manual is always preferred.

---

## Sentiment Scoring

| Source | Table | Frequency | Dashboard Chart(s) |
|--------|-------|-----------|-------------------|
| Claude API scoring of slug 2843 narratives | `narrative_sentiment` | Manual | **Sentiment Index** |

Scoring uses `rubric.md` to score USDA Daily National Shell Egg Index commentary on 9 dimensions. Computed indices: NationalCoreIndex, FundamentalsCoreIndex.

**Important**: Sentiment scoring is NOT part of `--update`. It must be run separately.

---

## Other Sources

| Source | Table | Frequency | Dashboard Chart(s) |
|--------|-------|-----------|-------------------|
| AMS Cage-Free Report (PDF) | `cage_free_composition` | Monthly | Cage-Free Composition |
| ERS Trade Data | `ers_trade` | Monthly | ERS Egg/Chicken Trade |
| Broiler Hatchability (seed CSV) | `broiler_hatchability` | Seed only | Broiler Hatchability |

---

## Common Operations

```bash
# Full incremental update (MARS + NASS + FRED + HPAI)
PYTHONPATH=src python3 -m chartbook.ingest --update

# MARS daily reports only (2843, 2734, 3888)
PYTHONPATH=src python3 -m chartbook.ingest --update --frequent-only

# Rebuild dashboard (after any data changes)
PYTHONPATH=src python3 -m chartbook.build_dashboard

# Check data freshness
PYTHONPATH=src python3 -m chartbook.ingest --status
```

## Troubleshooting

**Chart not showing updated data?**
1. Check if `--update` or `--backfill-*` was run to fetch new data into SQLite
2. Check if `build_dashboard` was run to regenerate `data.json` from SQLite
3. Both steps are required — ingestion fills the DB, build generates the JSON

**Sentiment index stale?**
Sentiment scoring is manual. Check for unscored narratives:
```sql
SELECT rn.report_date FROM report_narratives rn
LEFT JOIN narrative_sentiment ns ON rn.report_date = ns.report_date AND rn.slug_id = ns.slug_id
WHERE rn.slug_id = 2843 AND ns.report_date IS NULL ORDER BY rn.report_date;
```
