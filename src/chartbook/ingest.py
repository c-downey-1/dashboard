#!/usr/bin/env python3
"""
ingest.py — CLI for fetching MARS, NASS, FRED, BLS, HPAI, and ERS data into SQLite.

Usage:
    python ingest.py --backfill-mars              # All 12 MARS reports
    python ingest.py --backfill-mars --report 1427 # Single report
    python ingest.py --backfill-nass              # All NASS data series
    python ingest.py --backfill-fred              # All FRED series
    python ingest.py --backfill-bls               # All BLS series
    python ingest.py --backfill-hpai              # HPAI flock detections
    python ingest.py --backfill-cage-free-composition  # AMS monthly cage-free PDF
    python ingest.py --backfill-ers-trade         # ERS monthly chicken/egg trade totals
    python ingest.py --backfill-cme-feed          # CME-derived daily layer feed seed
    python ingest.py --update                     # Incremental (all APIs)
    python ingest.py --update --mars-only         # Incremental MARS
    python ingest.py --update --nass-only         # Incremental NASS
    python ingest.py --update --frequent-only     # MARS + HPAI only
    python ingest.py --status                     # Show ingestion summary
"""

import argparse
import csv
import os
from datetime import date, timedelta

from . import db
from . import parsers
from .clients import bls_client
from .clients import broiler_hatchery_client
from .clients import cage_free_report_client
from .clients import ers_trade_client
from .clients import fred_client
from .clients import google_sheets_client
from .clients import hpai_client
from .clients import mars_client
from .clients import nass_client
from .paths import SEEDS_ROOT

# ── MARS Report Configuration ───────────────────────────────────────────

MARS_REPORTS = {
    2843: {
        "title": "Daily National Shell Egg Index",
        "table": "egg_prices",
        "parser": parsers.parse_egg_prices,
        "extra": [
            (parsers.parse_egg_volumes, "egg_volumes"),
            (parsers.parse_narratives, "report_narratives"),
        ],
        "earliest": "2025-02-03",
        "freq": "daily",
    },
    2734: {
        "title": "Daily New York Shell Egg",
        "table": "egg_prices",
        "parser": parsers.parse_egg_prices,
        "earliest": "2025-02-01",
        "freq": "daily",
    },
    3888: {
        "title": "Daily National Breaking Stock",
        "table": "egg_prices",
        "parser": parsers.parse_egg_prices,
        "earliest": "2025-02-01",
        "freq": "daily",
    },
    2848: {
        "title": "Weekly Combined Regional Shell Egg",
        "table": "egg_prices",
        "parser": parsers.parse_egg_prices,
        "earliest": "2025-01-01",
        "freq": "weekly",
    },
    2842: {
        "title": "Weekly National Egg Products",
        "table": "egg_prices",
        "parser": parsers.parse_egg_prices,
        "extra": [
            (parsers.parse_narratives, "report_narratives"),
        ],
        "earliest": "2025-02-01",
        "freq": "weekly",
    },
    1427: {
        "title": "National Weekly Shell Egg Inventory",
        "table": "egg_inventory",
        "parser": parsers.parse_egg_inventory,
        "earliest": "2017-11-13",
        "freq": "weekly",
    },
    1665: {
        "title": "Weekly Shell Eggs Processed",
        "table": "eggs_processed",
        "parser": parsers.parse_eggs_processed,
        "earliest": "2019-04-29",
        "freq": "weekly",
    },
    1624: {
        "title": "Weekly Poultry & Egg Cold Storage",
        "table": "cold_storage",
        "parser": parsers.parse_cold_storage,
        "earliest": "2019-03-25",
        "freq": "weekly",
    },
    3646: {
        "title": "Weekly National Chicken Report",
        "table": "chicken_wholesale",
        "parser": parsers.parse_chicken_wholesale,
        "earliest": "2023-01-02",
        "freq": "weekly",
    },
    3649: {
        "title": "Monthly National Chicken Report",
        "table": "chicken_wholesale",
        "parser": parsers.parse_chicken_wholesale,
        "earliest": "2023-01-02",
        "freq": "monthly",
    },
    2756: {
        "title": "Weekly Retail Chicken Feature Activity",
        "table": "retail_prices",
        "parser": parsers.parse_retail_prices,
        "extra": [
            (parsers.parse_retail_metrics, "retail_metrics"),
            (parsers.parse_narratives, "report_narratives"),
        ],
        "earliest": "2010-01-01",
        "freq": "weekly",
    },
    2757: {
        "title": "Weekly Retail Egg Feature Activity",
        "table": "retail_prices",
        "parser": parsers.parse_retail_prices,
        "extra": [
            (parsers.parse_retail_metrics, "retail_metrics"),
            (parsers.parse_narratives, "report_narratives"),
        ],
        "earliest": "2010-01-01",
        "freq": "weekly",
    },
}

# ── NASS Data Series Configuration ───────────────────────────────────────

NASS_SERIES = [
    # Layer Inventory & Disposition
    {"short_desc": "CHICKENS, LAYERS - INVENTORY", "label": "Layer Inventory"},
    {"short_desc": "CHICKENS, LAYERS, TABLE - INVENTORY", "label": "Table Layer Inventory"},
    {"short_desc": "CHICKENS, LAYERS, HATCHING - INVENTORY", "label": "Hatching Layer Inventory"},
    {"short_desc": "CHICKENS, LAYERS, HATCHING, BROILER TYPE - INVENTORY", "label": "Broiler-Type Hatching Layer Inv"},
    {"short_desc": "CHICKENS, LAYERS - LOSS, DEATH & RENDERED, MEASURED IN HEAD", "label": "Layer Death/Rendered"},
    {"short_desc": "CHICKENS, LAYERS - SALES FOR SLAUGHTER, MEASURED IN HEAD", "label": "Layer Slaughter Sales"},
    {"short_desc": "CHICKENS, LAYERS - BEING MOLTED, MEASURED IN PCT OF INVENTORY", "label": "Layers Molted %"},
    {"short_desc": "CHICKENS, LAYERS - MOLT COMPLETED, MEASURED IN PCT OF INVENTORY", "label": "Layers Molt Completed %"},
    {"short_desc": "CHICKENS, PULLETS, REPLACEMENT - INVENTORY", "label": "Replacement Pullet Inventory"},

    # Egg Production & Rate of Lay
    {"short_desc": "EGGS - PRODUCTION, MEASURED IN EGGS", "label": "Egg Production"},
    {"short_desc": "EGGS, TABLE - PRODUCTION, MEASURED IN EGGS", "label": "Table Egg Production"},
    {"short_desc": "EGGS, HATCHING, BROILER TYPE - PRODUCTION, MEASURED IN EGGS", "label": "Broiler Hatching Egg Prod"},
    {"short_desc": "CHICKENS, LAYERS - RATE OF LAY, MEASURED IN EGGS / 100 LAYER", "label": "Rate of Lay (All)"},
    {"short_desc": "CHICKENS, LAYERS, TABLE - RATE OF LAY, MEASURED IN EGGS / 100 LAYER", "label": "Rate of Lay (Table)"},

    # Hatchery
    {"short_desc": "CHICKENS, CHICKS, BROILER TYPE - HATCHED, MEASURED IN HEAD", "label": "Broiler Chicks Hatched"},
    {"short_desc": "CHICKENS, CHICKS, EGG TYPE - HATCHED, MEASURED IN HEAD", "label": "Egg-Type Chicks Hatched"},
    {"short_desc": "CHICKENS, BROILERS - EGGS SET, MEASURED IN EGGS", "label": "Broiler Eggs Set"},

    # Placements
    {"short_desc": "CHICKENS, BROILERS - PLACEMENTS, MEASURED IN HEAD", "label": "Broiler Placements"},
    {"short_desc": "CHICKENS, CHICKS, BROILER TYPE, PULLET - PLACEMENTS, INTENDED, MEASURED IN HEAD",
     "label": "Broiler Pullet Intended Placements"},
    {"short_desc": "CHICKENS, CHICKS, EGG TYPE, PULLET - PLACEMENTS, INTENDED, MEASURED IN HEAD",
     "label": "Egg-Type Pullet Intended Placements"},

    # Prices
    {"short_desc": "EGGS - PRICE RECEIVED, MEASURED IN $ / DOZEN", "label": "Egg Price Received"},
    {"short_desc": "CHICKENS, BROILERS - PRICE RECEIVED, MEASURED IN $ / LB", "label": "Broiler Price Received"},

    # Cold Storage
    {"short_desc": "CHICKENS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB", "label": "Chicken Cold Storage"},
    {"short_desc": "EGGS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB", "label": "Egg Cold Storage"},

    # Processed Eggs
    {"short_desc": "EGGS, SHELL - BROKEN, MEASURED IN DOZEN", "label": "Shell Eggs Broken"},
    {"short_desc": "EGGS, EDIBLE PRODUCT - PRODUCTION, MEASURED IN LB", "label": "Edible Egg Product Production"},

    # Additional series (Phase 2 — verify with get_counts before running)
    # Broiler production
    {"short_desc": "CHICKENS, BROILERS - PRODUCTION, MEASURED IN HEAD", "label": "Broiler Production"},
    # Edible egg product detail
    {"short_desc": "EGGS, EDIBLE PRODUCT, WHOLE - PRODUCTION, MEASURED IN LB", "label": "Edible Egg Product (Whole)"},
    {"short_desc": "EGGS, EDIBLE PRODUCT, WHITE - PRODUCTION, MEASURED IN LB", "label": "Edible Egg Product (White)"},
    {"short_desc": "EGGS, EDIBLE PRODUCT, YOLK - PRODUCTION, MEASURED IN LB", "label": "Edible Egg Product (Yolk)"},
]

# ── FRED Series Configuration ─────────────────────────────────────────────

FRED_SERIES = {
    "PMAIZMTUSDM": "Global Price of Corn ($/metric ton)",
    "PSMEAUSDM":   "Global Price of Soybean Meal ($/metric ton)",
    "WPU0171":     "PPI: Chicken Eggs",
    "WPU0141":     "PPI: Slaughter Chickens",
    "WPU014102":   "PPI: Broilers & Meat-Type Chickens",
    "PCU322219322219": "Other Paperboard Container Manufacturing",
    "PPOULTUSDM":  "Global Price of Poultry ($/kg)",
    "APU0000708111": "Eggs, Grade A, Large (per dozen)",
    "GASDESW":     "US Diesel Sales Price ($/gallon)",
    "APU000072610": "Avg Price: Electricity per kWh",
}

# ── BLS Series Configuration ──────────────────────────────────────────────

BLS_SERIES = {
    "APU0000708111": "Eggs, Grade A, Large (per dozen)",
    "APU0000706111": "Chicken, Fresh, Whole (per lb)",
    "APU0000FF1101": "Chicken Breast, Boneless (per lb)",
    "APU0000706211": "Chicken Breast, Bone-in (per lb)",
}

BROILER_HATCHABILITY_SEED = SEEDS_ROOT / "broiler_hatchability_seed.csv"
CAGE_FREE_COMPOSITION_SEED = SEEDS_ROOT / "cage_free_flock_composition_seed.csv"
LAYER_FEED_SEED = SEEDS_ROOT / "layer_feed_seed.csv"


def _cme_feed_sheet_ref():
    """Return the configured public Google Sheet URL or id for feed ingestion."""
    return (
        os.environ.get("CME_FEED_GOOGLE_SHEET_URL", "").strip()
        or os.environ.get("CME_FEED_GOOGLE_SHEET_ID", "").strip()
        or None
    )


# ── Pipeline Functions ───────────────────────────────────────────────────

def _log_date_span(conn, source, rows, data_item=None):
    """Log fetch coverage using the actual returned observation dates when possible."""
    if not rows:
        return

    sample = rows[0]
    if "observation_date" in sample:
        dates = [r["observation_date"] for r in rows if r.get("observation_date")]
    elif "year" in sample:
        dates = [str(r["year"]) for r in rows if r.get("year")]
    elif "confirmation_date" in sample:
        dates = [r["confirmation_date"] for r in rows if r.get("confirmation_date")]
    else:
        dates = []

    start = min(dates) if dates else str(date.today())
    end = max(dates) if dates else str(date.today())
    db.log_fetch(conn, source, start, end, len(rows), data_item=data_item)

def ingest_mars_report(conn, slug_id, start_date, end_date):
    """Fetch and ingest a single MARS report."""
    config = MARS_REPORTS[slug_id]
    print(f"\n{'='*60}")
    print(f"  {config['title']} (slug {slug_id})")
    print(f"  {start_date} → {end_date}")
    print(f"{'='*60}")

    sections = mars_client.fetch_report(slug_id, start_date, end_date)
    if not sections:
        print(f"  No data returned for slug {slug_id}")
        db.log_fetch(conn, "mars", str(start_date), str(end_date), 0,
                      slug_id=slug_id, status="empty")
        return 0

    # Primary parser
    parser = config["parser"]
    if parser in (parsers.parse_egg_prices, parsers.parse_chicken_wholesale,
                  parsers.parse_retail_prices, parsers.parse_retail_metrics):
        rows = parser(slug_id, sections)
    else:
        rows = parser(sections)

    total = 0
    if rows:
        count = db.upsert_rows(conn, config["table"], rows)
        total += count
        print(f"  → {count} rows → {config['table']}")

    # Extra parsers (volumes, narratives, metrics)
    for extra_parser, extra_table in config.get("extra", []):
        if extra_parser in (parsers.parse_retail_metrics,):
            extra_rows = extra_parser(slug_id, sections)
        elif extra_parser == parsers.parse_narratives:
            extra_rows = extra_parser(slug_id, sections)
        else:
            extra_rows = extra_parser(sections)
        if extra_rows:
            count = db.upsert_rows(conn, extra_table, extra_rows)
            total += count
            print(f"  → {count} rows → {extra_table}")

    db.log_fetch(conn, "mars", str(start_date), str(end_date), total,
                  slug_id=slug_id)
    return total


def ingest_nass_series(conn, series_config, year_ge=2010):
    """Fetch and ingest a single NASS data series."""
    short_desc = series_config["short_desc"]
    label = series_config["label"]
    print(f"\n  {label}")

    records = nass_client.fetch_data_item(short_desc, year__GE=str(year_ge))
    if not records:
        return 0

    rows = [parsers.parse_nass_record(r) for r in records]
    rows = [r for r in rows if r["year"] > 0]

    if rows:
        count = db.upsert_rows(conn, "nass_data", rows)
        db.log_fetch(conn, "nass", str(year_ge), str(date.today()), count,
                      data_item=short_desc)
        return count
    return 0


def load_broiler_hatchability_seed(conn):
    """Load the fixed historical hatchability seed series."""
    if not BROILER_HATCHABILITY_SEED.exists():
        print("  WARNING: seed file missing, skipping broiler hatchability seed load")
        return 0

    rows = []
    with BROILER_HATCHABILITY_SEED.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            rows.append({
                "release_date": record["release_date"],
                "week_ending_date": None,
                "hatchability_pct": float(record["hatchability_pct"]),
                "source": "seed",
                "txt_url": None,
                "pdf_url": None,
            })

    inserted = db.insert_or_ignore_rows(conn, "broiler_hatchability", rows)
    if inserted:
        db.log_fetch(
            conn,
            "broiler_hatchery",
            rows[0]["release_date"],
            rows[-1]["release_date"],
            inserted,
            data_item="seed",
        )
    return inserted


def ingest_broiler_hatchability(conn, start_after=None):
    """Fetch and ingest Broiler Hatchery releases after the latest stored date."""
    seed_inserted = load_broiler_hatchability_seed(conn)
    if seed_inserted:
        print(f"  Seeded {seed_inserted} historical hatchability rows")

    row = conn.execute("SELECT MAX(release_date) FROM broiler_hatchability").fetchone()
    last_release_date = start_after or (row[0] if row and row[0] else None)
    if not last_release_date:
        print("  No baseline hatchability date available")
        return 0

    releases = broiler_hatchery_client.fetch_releases_after(last_release_date)
    if not releases:
        print("  No new broiler hatchability releases found")
        return 0

    rows = []
    for release in releases:
        print(f"  {release['release_date']}")
        text = broiler_hatchery_client.fetch_report_text(release["txt_url"])
        parsed = broiler_hatchery_client.parse_report_text(text)
        rows.append({
            "release_date": release["release_date"],
            "week_ending_date": parsed["week_ending_date"],
            "hatchability_pct": parsed["hatchability_pct"],
            "source": "esmis",
            "txt_url": release["txt_url"],
            "pdf_url": release["pdf_url"],
        })

    count = db.upsert_rows(conn, "broiler_hatchability", rows)
    db.log_fetch(
        conn,
        "broiler_hatchery",
        rows[0]["release_date"],
        rows[-1]["release_date"],
        count,
        data_item="scraped",
    )
    return count


def load_cage_free_composition_seed(conn):
    """Load optional historical AMS cage-free composition seed data."""
    if not CAGE_FREE_COMPOSITION_SEED.exists():
        return 0

    rows = []
    with CAGE_FREE_COMPOSITION_SEED.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            rows.append({
                "report_month": record["report_month"],
                "report_date": record["report_date"],
                "category": record["category"],
                "layer_flock_size": int(record["layer_flock_size"]) if record.get("layer_flock_size") else None,
                "lay_rate_pct": float(record["lay_rate_pct"]) if record.get("lay_rate_pct") else None,
                "weekly_production_cases": int(record["weekly_production_cases"]) if record.get("weekly_production_cases") else None,
                "source_url": record.get("source_url") or None,
                "source_type": record.get("source_type") or "seed",
            })

    inserted = db.insert_or_ignore_rows(conn, "cage_free_flock_composition", rows)
    if inserted and rows:
        db.log_fetch(
            conn,
            "ams_cage_free",
            rows[0]["report_month"],
            rows[-1]["report_month"],
            inserted,
            data_item="seed",
        )
    return inserted


def ingest_cage_free_composition(conn):
    """Fetch the latest AMS cage-free composition PDF and store monthly rows."""
    seeded = load_cage_free_composition_seed(conn)
    if seeded:
        print(f"  Seeded {seeded} historical cage-free composition rows")

    rows = cage_free_report_client.fetch_current_report_rows()
    if not rows:
        print("  No AMS cage-free composition rows parsed")
        return 0

    count = db.upsert_rows(conn, "cage_free_flock_composition", rows)
    db.log_fetch(
        conn,
        "ams_cage_free",
        rows[0]["report_month"],
        rows[0]["report_month"],
        count,
        data_item="current_pdf",
    )
    return count


def ingest_ers_trade_totals(conn):
    """Fetch the ERS workbook and store monthly chicken and egg trade totals."""
    rows = ers_trade_client.fetch_trade_rows()
    if not rows:
        print("  No ERS trade rows parsed")
        return 0

    count = db.upsert_rows(conn, "ers_trade_totals", rows)
    db.log_fetch(
        conn,
        "ers_trade",
        rows[0]["report_month"],
        rows[-1]["report_month"],
        count,
        data_item="monthly_workbook",
    )
    return count


def load_cme_feed_seed(conn):
    """Load the reconstructed daily CME-derived layer feed history."""
    if not LAYER_FEED_SEED.exists():
        print("  WARNING: layer feed seed file missing, skipping CME feed seed load")
        return 0

    rows = []
    with LAYER_FEED_SEED.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            rows.append({
                "trade_date": record["trade_date"],
                "corn_per_ton": float(record["corn_per_ton"]) if record.get("corn_per_ton") else None,
                "soymeal_per_ton": float(record["soymeal_per_ton"]) if record.get("soymeal_per_ton") else None,
                "calcium_per_ton": float(record["calcium_per_ton"]) if record.get("calcium_per_ton") else None,
                "other_per_ton": float(record["other_per_ton"]) if record.get("other_per_ton") else None,
                "ration_cost": float(record["ration_cost"]) if record.get("ration_cost") else None,
                "layer_feed_index": float(record["layer_feed_index"]) if record.get("layer_feed_index") else None,
                "source_type": record.get("source_type") or "layerfeed_workbook_seed",
                "source_note": record.get("source_note") or None,
            })

    count = db.upsert_rows(conn, "cme_feed_daily", rows)
    if rows:
        db.log_fetch(
            conn,
            "cme_feed",
            rows[0]["trade_date"],
            rows[-1]["trade_date"],
            count,
            data_item="seed",
        )
    return count


def ingest_cme_feed(conn, gid=0):
    """Fetch public Google Sheets feed data and fall back to the local seed."""
    sheet_ref = _cme_feed_sheet_ref()
    if not sheet_ref:
        print("  CME_FEED_GOOGLE_SHEET_URL / CME_FEED_GOOGLE_SHEET_ID not set, falling back to seed")
        return load_cme_feed_seed(conn)

    try:
        _, csv_rows = google_sheets_client.fetch_public_csv_rows(sheet_ref, gid=gid)
        rows = google_sheets_client.parse_layer_feed_rows(csv_rows, "public_google_sheet")
    except Exception as exc:
        print(f"  Public Google Sheet fetch failed, falling back to seed: {exc}")
        return load_cme_feed_seed(conn)

    if not rows:
        print("  Public Google Sheet returned no usable feed rows, falling back to seed")
        return load_cme_feed_seed(conn)

    count = db.upsert_rows(conn, "cme_feed_daily", rows)
    db.log_fetch(
        conn,
        "cme_feed",
        rows[0]["trade_date"],
        rows[-1]["trade_date"],
        count,
        data_item="public_google_sheet",
    )
    return count


def backfill_mars(conn, report_filter=None):
    """Full backfill of MARS reports."""
    today = date.today()
    grand_total = 0

    slugs = [report_filter] if report_filter else list(MARS_REPORTS.keys())
    for slug_id in slugs:
        config = MARS_REPORTS[slug_id]
        start = date.fromisoformat(config["earliest"])
        total = ingest_mars_report(conn, slug_id, start, today)
        grand_total += total

    print(f"\n  MARS backfill complete: {grand_total:,} total rows")
    return grand_total


def backfill_nass(conn, year_ge=2010):
    """Full backfill of all NASS data series."""
    print(f"\n{'='*60}")
    print(f"  NASS QuickStats Backfill (year >= {year_ge})")
    print(f"{'='*60}")

    grand_total = 0
    for series in NASS_SERIES:
        total = ingest_nass_series(conn, series, year_ge=year_ge)
        grand_total += total

    print(f"\n  NASS backfill complete: {grand_total:,} total rows")
    return grand_total


def backfill_broiler_hatchability(conn):
    """Load seed history and scrape all newer Broiler Hatchery releases."""
    print(f"\n{'='*60}")
    print("  Broiler Hatchability Backfill")
    print(f"{'='*60}")

    total = ingest_broiler_hatchability(conn)
    print(f"\n  Broiler hatchability backfill complete: {total:,} scraped rows")
    return total


def backfill_cage_free_composition(conn):
    """Load any seeded history and fetch the current AMS cage-free report."""
    print(f"\n{'='*60}")
    print("  AMS Cage-Free Flock Composition Backfill")
    print(f"{'='*60}")

    total = ingest_cage_free_composition(conn)
    print(f"\n  AMS cage-free composition backfill complete: {total:,} rows")
    return total


def backfill_ers_trade(conn):
    """Fetch the ERS monthly trade workbook and load full chicken/egg history."""
    print(f"\n{'='*60}")
    print("  ERS Chicken and Egg Trade Backfill")
    print(f"{'='*60}")

    total = ingest_ers_trade_totals(conn)
    print(f"\n  ERS trade backfill complete: {total:,} rows")
    return total


def backfill_cme_feed(conn):
    """Load daily CME-derived feed history from the public Google Sheet."""
    print(f"\n{'='*60}")
    print("  CME-Derived Layer Feed History Backfill")
    print(f"{'='*60}")

    total = ingest_cme_feed(conn)
    print(f"\n  CME-derived layer feed backfill complete: {total:,} rows")
    return total


def update_mars(conn, report_filter=None):
    """Incremental update: fetch only new data since last fetch."""
    today = date.today()
    grand_total = 0

    slugs = [report_filter] if report_filter else list(MARS_REPORTS.keys())
    for slug_id in slugs:
        config = MARS_REPORTS[slug_id]
        last = db.get_last_fetched(conn, "mars", slug_id=slug_id)
        if last:
            # Overlap by 7 days to catch revisions
            start = max(
                date.fromisoformat(last) - timedelta(days=7),
                date.fromisoformat(config["earliest"]),
            )
        else:
            start = date.fromisoformat(config["earliest"])

        total = ingest_mars_report(conn, slug_id, start, today)
        grand_total += total

    print(f"\n  MARS update complete: {grand_total:,} total rows")
    return grand_total


def update_nass(conn):
    """Incremental NASS update: re-fetch current year + prior year."""
    current_year = date.today().year
    year_ge = current_year - 1
    print(f"\n{'='*60}")
    print(f"  NASS Incremental Update (year >= {year_ge})")
    print(f"{'='*60}")

    grand_total = 0
    for series in NASS_SERIES:
        total = ingest_nass_series(conn, series, year_ge=year_ge)
        grand_total += total

    print(f"\n  NASS update complete: {grand_total:,} total rows")
    return grand_total


def update_broiler_hatchability(conn):
    """Incremental Broiler Hatchery update from the latest stored release date."""
    print(f"\n{'='*60}")
    print("  Broiler Hatchability Incremental Update")
    print(f"{'='*60}")

    total = ingest_broiler_hatchability(conn)
    print(f"\n  Broiler hatchability update complete: {total:,} scraped rows")
    return total


def update_cage_free_composition(conn):
    """Refresh the current AMS monthly cage-free composition report."""
    print(f"\n{'='*60}")
    print("  AMS Cage-Free Flock Composition Incremental Update")
    print(f"{'='*60}")

    total = ingest_cage_free_composition(conn)
    print(f"\n  AMS cage-free composition update complete: {total:,} rows")
    return total


def update_ers_trade(conn):
    """Refresh ERS monthly chicken and egg trade totals."""
    print(f"\n{'='*60}")
    print("  ERS Chicken and Egg Trade Incremental Update")
    print(f"{'='*60}")

    total = ingest_ers_trade_totals(conn)
    print(f"\n  ERS trade update complete: {total:,} rows")
    return total


def update_cme_feed(conn):
    """Refresh daily CME-derived feed history."""
    print(f"\n{'='*60}")
    print("  CME-Derived Layer Feed Incremental Update")
    print(f"{'='*60}")

    total = ingest_cme_feed(conn)
    print(f"\n  CME-derived layer feed update complete: {total:,} rows")
    return total


def backfill_fred(conn):
    """Full backfill of all FRED series."""
    print(f"\n{'='*60}")
    print(f"  FRED Series Backfill")
    print(f"{'='*60}")

    grand_total = 0
    for series_id, label in FRED_SERIES.items():
        observations = fred_client.fetch_series(series_id)
        if not observations:
            continue
        rows = [parsers.parse_fred_record(series_id, obs, label) for obs in observations]
        rows = [r for r in rows if r["observation_date"] and r["value"] is not None]
        if rows:
            count = db.upsert_rows(conn, "fred_series", rows)
            db.log_fetch(conn, "fred", rows[0]["observation_date"],
                         rows[-1]["observation_date"], count,
                         data_item=series_id)
            grand_total += count

    print(f"\n  FRED backfill complete: {grand_total:,} total rows")
    return grand_total


def backfill_bls(conn, start_year=2006):
    """Full backfill of all BLS series."""
    print(f"\n{'='*60}")
    print(f"  BLS Series Backfill (from {start_year})")
    print(f"{'='*60}")

    series_ids = list(BLS_SERIES.keys())
    all_data = bls_client.fetch_series(series_ids, start_year=start_year)

    grand_total = 0
    for series_id, data_points in all_data.items():
        label = BLS_SERIES.get(series_id, "")
        rows = [parsers.parse_bls_record(series_id, dp, label) for dp in data_points]
        rows = [r for r in rows if r is not None and r["month"] is not None]
        if rows:
            count = db.upsert_rows(conn, "bls_prices", rows)
            years = [r["year"] for r in rows]
            db.log_fetch(conn, "bls", str(min(years)), str(max(years)),
                         count, data_item=series_id)
            grand_total += count

    print(f"\n  BLS backfill complete: {grand_total:,} total rows")
    return grand_total


def backfill_hpai(conn):
    """Full backfill of HPAI flock detections."""
    print(f"\n{'='*60}")
    print(f"  HPAI Flock Detections Backfill")
    print(f"{'='*60}")

    csv_rows = hpai_client.fetch_flock_detections()
    if not csv_rows:
        print("  No HPAI data returned")
        return 0

    rows = [parsers.parse_hpai_record(r) for r in csv_rows]
    rows = [r for r in rows if r["state"] is not None]

    if rows:
        conn.execute("DELETE FROM hpai_detections")
        count = db.insert_or_ignore_rows(conn, "hpai_detections", rows)
        dates = [r["confirmation_date"] for r in rows if r["confirmation_date"]]
        db.log_fetch(conn, "hpai",
                     min(dates) if dates else str(date.today()),
                     max(dates) if dates else str(date.today()),
                     count)
        print(f"\n  HPAI backfill complete: {count:,} rows")
        return count
    return 0


def update_hpai(conn):
    """Incremental HPAI update using a full re-download plus deduped inserts."""
    print(f"\n{'='*60}")
    print(f"  HPAI Incremental Update")
    print(f"{'='*60}")
    return backfill_hpai(conn)


def update_fred(conn):
    """Incremental FRED update: fetch last 2 years."""
    print(f"\n{'='*60}")
    print(f"  FRED Incremental Update")
    print(f"{'='*60}")

    two_years_ago = (date.today() - timedelta(days=730)).isoformat()
    grand_total = 0
    for series_id, label in FRED_SERIES.items():
        observations = fred_client.fetch_series(series_id, start_date=two_years_ago)
        if not observations:
            continue
        rows = [parsers.parse_fred_record(series_id, obs, label) for obs in observations]
        rows = [r for r in rows if r["observation_date"] and r["value"] is not None]
        if rows:
            count = db.upsert_rows(conn, "fred_series", rows)
            _log_date_span(conn, "fred", rows, data_item=series_id)
            grand_total += count

    print(f"\n  FRED update complete: {grand_total:,} total rows")
    return grand_total


def update_bls(conn):
    """Incremental BLS update: fetch last 3 years."""
    current_year = date.today().year
    start_year = current_year - 2
    print(f"\n{'='*60}")
    print(f"  BLS Incremental Update ({start_year}-{current_year})")
    print(f"{'='*60}")

    series_ids = list(BLS_SERIES.keys())
    all_data = bls_client.fetch_series(series_ids, start_year=start_year,
                                       end_year=current_year)
    grand_total = 0
    for series_id, data_points in all_data.items():
        label = BLS_SERIES.get(series_id, "")
        rows = [parsers.parse_bls_record(series_id, dp, label) for dp in data_points]
        rows = [r for r in rows if r is not None and r["month"] is not None]
        if rows:
            count = db.upsert_rows(conn, "bls_prices", rows)
            _log_date_span(conn, "bls", rows, data_item=series_id)
            grand_total += count

    print(f"\n  BLS update complete: {grand_total:,} total rows")
    return grand_total


def show_status(conn):
    """Print a summary of all ingested data."""
    status = db.get_status(conn)
    if not status:
        print("  Database is empty. Run --backfill-mars and/or --backfill-nass first.")
        return

    print(f"\n{'Table':<22} {'Group/Item':<50} {'Rows':>8} {'From':>12} {'To':>12}")
    print("-" * 108)
    for s in status:
        group = str(s["group"] or "")
        if len(group) > 48:
            group = group[:45] + "..."
        min_d = str(s["min_date"] or "—")
        max_d = str(s["max_date"] or "—")
        print(f"{s['table']:<22} {group:<50} {s['rows']:>8,} {min_d:>12} {max_d:>12}")


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Chartbook data ingestion pipeline")
    ap.add_argument("--backfill-mars", action="store_true",
                    help="Full backfill of all MARS reports")
    ap.add_argument("--backfill-nass", action="store_true",
                    help="Full backfill of all NASS data series")
    ap.add_argument("--backfill-fred", action="store_true",
                    help="Full backfill of all FRED series")
    ap.add_argument("--backfill-bls", action="store_true",
                    help="Full backfill of all BLS series")
    ap.add_argument("--backfill-hpai", action="store_true",
                    help="Download HPAI flock detections from APHIS")
    ap.add_argument("--backfill-broiler-hatchability", action="store_true",
                    help="Load seeded broiler hatchability history and scrape newer ESMIS releases")
    ap.add_argument("--backfill-cage-free-composition", action="store_true",
                    help="Load seeded history and fetch the current AMS cage-free flock composition PDF")
    ap.add_argument("--backfill-ers-trade", action="store_true",
                    help="Fetch ERS monthly chicken and egg trade totals from the workbook")
    ap.add_argument("--backfill-cme-feed", action="store_true",
                    help="Load daily CME-derived layer feed history from the public Google Sheet")
    ap.add_argument("--update", action="store_true",
                    help="Incremental update (all APIs)")
    ap.add_argument("--mars-only", action="store_true",
                    help="With --update: MARS only")
    ap.add_argument("--nass-only", action="store_true",
                    help="With --update: NASS only")
    ap.add_argument("--frequent-only", action="store_true",
                    help="With --update: only refresh highest-frequency sources (MARS + HPAI)")
    ap.add_argument("--report", type=int, default=None,
                    help="MARS slug ID to target (with --backfill-mars or --update)")
    ap.add_argument("--nass-year-ge", type=int, default=2010,
                    help="Earliest year for NASS backfill (default: 2010)")
    ap.add_argument("--status", action="store_true",
                    help="Show ingestion summary")
    ap.add_argument("--db", default=None,
                    help="Path to SQLite database (default: chartbook.db)")
    args = ap.parse_args()

    conn = db.init_db(args.db)

    try:
        if args.status:
            show_status(conn)
            return

        if args.backfill_mars:
            backfill_mars(conn, report_filter=args.report)

        if args.backfill_nass:
            backfill_nass(conn, year_ge=args.nass_year_ge)

        if args.backfill_fred:
            backfill_fred(conn)

        if args.backfill_bls:
            backfill_bls(conn)

        if args.backfill_hpai:
            backfill_hpai(conn)

        if args.backfill_broiler_hatchability:
            backfill_broiler_hatchability(conn)

        if args.backfill_cage_free_composition:
            backfill_cage_free_composition(conn)

        if args.backfill_ers_trade:
            backfill_ers_trade(conn)

        if args.backfill_cme_feed:
            backfill_cme_feed(conn)

        if args.update:
            run_mars = not args.nass_only
            run_nass = not args.mars_only and not args.frequent_only
            run_fred = not (args.mars_only or args.nass_only or args.frequent_only)
            run_bls = not (args.mars_only or args.nass_only or args.frequent_only)
            run_hpai = not args.nass_only
            run_broiler_hatchability = not (args.mars_only or args.nass_only or args.frequent_only)
            run_cage_free_composition = not (args.mars_only or args.nass_only or args.frequent_only)
            run_ers_trade = not (args.mars_only or args.nass_only or args.frequent_only)
            run_cme_feed = not (args.mars_only or args.nass_only or args.frequent_only)

            if run_mars:
                update_mars(conn, report_filter=args.report)
            if run_nass:
                update_nass(conn)
            if run_fred:
                update_fred(conn)
            if run_bls:
                update_bls(conn)
            if run_hpai:
                update_hpai(conn)
            if run_broiler_hatchability:
                update_broiler_hatchability(conn)
            if run_cage_free_composition:
                update_cage_free_composition(conn)
            if run_ers_trade:
                update_ers_trade(conn)
            if run_cme_feed:
                update_cme_feed(conn)

        all_actions = [args.backfill_mars, args.backfill_nass,
                       args.backfill_fred, args.backfill_bls,
                       args.backfill_hpai, args.backfill_broiler_hatchability,
                       args.backfill_cage_free_composition,
                       args.backfill_ers_trade,
                       args.backfill_cme_feed,
                       args.update, args.status]
        if not any(all_actions):
            ap.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
