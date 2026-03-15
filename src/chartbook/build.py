#!/usr/bin/env python3
"""
build.py — Export SQLite data to CSVs and build data.json for the dashboard.

Usage:
    python build.py                 # Export CSVs + build data.json
    python build.py --csv-only      # Just export CSVs
"""

import argparse
import json

from . import db
from . import build_dashboard
from .paths import DATA_ROOT

DATA_DIR = DATA_ROOT

# ── CSV Export Definitions ───────────────────────────────────────────────

EXPORTS = [
    # MARS exports
    {
        "file": "shell_egg_index.csv",
        "query": """
            SELECT report_date, environment, class, color, egg_type,
                   origin, destination, freight,
                   wtd_avg_price, volume, wtd_avg_price_prev, wtd_avg_price_ly,
                   price_unit, volume_unit
            FROM egg_prices
            WHERE slug_id = 2843 AND section = 'Report Detail Weighted'
            ORDER BY report_date, environment, class
        """,
    },
    {
        "file": "ny_shell_egg.csv",
        "query": """
            SELECT report_date, class, price_low, price_high, avg_price,
                   avg_price_prev, price_unit
            FROM egg_prices
            WHERE slug_id = 2734
            ORDER BY report_date, class
        """,
    },
    {
        "file": "breaking_stock.csv",
        "query": """
            SELECT report_date, egg_type, price_low, price_high, avg_price,
                   avg_price_prev, price_unit
            FROM egg_prices
            WHERE slug_id = 3888
            ORDER BY report_date, egg_type
        """,
    },
    {
        "file": "regional_egg_prices.csv",
        "query": """
            SELECT report_date, region, class, price_low, price_high,
                   avg_price, avg_price_prev, price_unit
            FROM egg_prices
            WHERE slug_id = 2848
            ORDER BY report_date, region, class
        """,
    },
    {
        "file": "egg_products.csv",
        "query": """
            SELECT report_date, section, egg_type, environment,
                   avg_price, wtd_avg_price, volume,
                   avg_price_prev, wtd_avg_price_prev, price_unit, volume_unit
            FROM egg_prices
            WHERE slug_id = 2842
            ORDER BY report_date, egg_type
        """,
    },
    {
        "file": "egg_inventory.csv",
        "query": """
            SELECT report_date, region, class, type, volume, pct_chg
            FROM egg_inventory
            ORDER BY report_date, region, class
        """,
    },
    {
        "file": "eggs_processed.csv",
        "query": """
            SELECT report_date, class, period, volume
            FROM eggs_processed
            ORDER BY report_date, class, period
        """,
    },
    {
        "file": "cold_storage.csv",
        "query": """
            SELECT report_date, category, commodity,
                   holdings_lbs, holdings_1st_lbs, change_lbs, change_pct
            FROM cold_storage
            ORDER BY report_date, category, commodity
        """,
    },
    {
        "file": "chicken_wholesale_weekly.csv",
        "query": """
            SELECT report_date, item, low_price, high_price, wtd_avg_price,
                   volume, wtd_avg_price_prev, volume_prev, price_change,
                   price_unit, volume_unit
            FROM chicken_wholesale
            WHERE slug_id = 3646
            ORDER BY report_date, item
        """,
    },
    {
        "file": "chicken_wholesale_monthly.csv",
        "query": """
            SELECT report_date, item, low_price, high_price, wtd_avg_price,
                   volume, wtd_avg_price_prev, volume_prev, price_change,
                   price_unit, volume_unit
            FROM chicken_wholesale
            WHERE slug_id = 3649
            ORDER BY report_date, item
        """,
    },
    {
        "file": "retail_chicken_metrics.csv",
        "query": """
            SELECT report_date, region, stores, feature_rate, activity_index,
                   last_week_feature, last_year_feature,
                   last_week_activity, last_year_activity
            FROM retail_metrics
            WHERE slug_id = 2756
            ORDER BY report_date, region
        """,
    },
    {
        "file": "retail_egg_metrics.csv",
        "query": """
            SELECT report_date, region, stores, feature_rate, activity_index,
                   last_week_feature, last_year_feature,
                   last_week_activity, last_year_activity
            FROM retail_metrics
            WHERE slug_id = 2757
            ORDER BY report_date, region
        """,
    },
    {
        "file": "retail_chicken_prices.csv",
        "query": """
            SELECT report_date, region, type, environment, condition,
                   price_avg, price_min, price_max, store_count, price_unit
            FROM retail_prices
            WHERE slug_id = 2756
            ORDER BY report_date, region, type, environment
        """,
    },
    {
        "file": "retail_egg_prices.csv",
        "query": """
            SELECT report_date, region, type, environment, package_size,
                   quality_grade, price_avg, price_min, price_max,
                   store_count, price_unit
            FROM retail_prices
            WHERE slug_id = 2757
            ORDER BY report_date, region, type, environment
        """,
    },
    # NASS exports
    {
        "file": "nass_layers.csv",
        "query": """
            SELECT year, reference_period, class, value, agg_level, state_alpha
            FROM v_layers
            ORDER BY year, reference_period, agg_level, state_alpha
        """,
    },
    {
        "file": "nass_egg_production.csv",
        "query": """
            SELECT year, reference_period, class, value, unit, agg_level, state_alpha
            FROM v_egg_production
            ORDER BY year, reference_period, agg_level, state_alpha
        """,
    },
    {
        "file": "nass_rate_of_lay.csv",
        "query": """
            SELECT year, reference_period, class, value, agg_level
            FROM v_rate_of_lay
            ORDER BY year, reference_period
        """,
    },
    {
        "file": "nass_hatchery.csv",
        "query": """
            SELECT year, reference_period, data_item, value, unit
            FROM v_hatchery
            ORDER BY year, reference_period, data_item
        """,
    },
    {
        "file": "nass_prices.csv",
        "query": """
            SELECT year, reference_period, data_item, value, unit
            FROM v_nass_prices
            ORDER BY year, reference_period, data_item
        """,
    },
    {
        "file": "nass_cold_storage.csv",
        "query": """
            SELECT year, reference_period, data_item, value, unit
            FROM v_cold_storage_nass
            ORDER BY year, reference_period, data_item
        """,
    },
    # FRED exports
    {
        "file": "fred_feed_costs.csv",
        "query": """
            SELECT observation_date, corn_price, sbm_price
            FROM v_feed_costs
            ORDER BY observation_date
        """,
    },
    {
        "file": "fred_ppi.csv",
        "query": """
            SELECT observation_date, series_id, series_label, value
            FROM fred_series
            WHERE series_id IN ('WPU0171', 'WPU0141', 'WPU014102', 'PPOULTUSDM')
            ORDER BY observation_date, series_id
        """,
    },
    # BLS exports
    {
        "file": "bls_retail_prices.csv",
        "query": """
            SELECT year, month, egg_price, chicken_whole_price,
                   chicken_breast_price, chicken_breast_bonein_price
            FROM v_cross_protein_cpi
            ORDER BY year, month
        """,
    },
    # HPAI exports
    {
        "file": "hpai_detections.csv",
        "query": """
            SELECT confirmation_date, state, county, flock_type, species, flock_size
            FROM hpai_detections
            ORDER BY confirmation_date, state
        """,
    },
    {
        "file": "hpai_monthly.csv",
        "query": """
            SELECT month, flock_type, detections, commercial_birds
            FROM v_hpai_monthly
            ORDER BY month, flock_type
        """,
    },
    {
        "file": "broiler_hatchability.csv",
        "query": """
            SELECT release_date, week_ending_date, hatchability_pct, source, txt_url, pdf_url
            FROM broiler_hatchability
            ORDER BY release_date
        """,
    },
]


# ── Build Functions ──────────────────────────────────────────────────────

def export_csvs(conn):
    """Export all SQL queries to CSV files in data/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    total_files = 0

    for export in EXPORTS:
        path = DATA_DIR / export["file"]
        try:
            rows = db.export_csv(conn, export["query"], str(path))
            print(f"  {export['file']}: {rows:,} rows")
            total_files += 1
        except Exception as e:
            print(f"  {export['file']}: WARN: {e}")

    print(f"\n  Exported {total_files} CSV files to {DATA_DIR}/")


def build_dashboard_outputs(conn):
    """Build docs/data.json + split dashboard HTML via build_dashboard.py."""
    build_dashboard.build_data_json(conn)
    with open(build_dashboard.DATA_JSON_PATH) as f:
        data = json.load(f)
    build_dashboard.build_html(data)


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Build dashboard data from SQLite")
    ap.add_argument("--csv-only", action="store_true",
                    help="Only export CSVs (skip dashboard build)")
    ap.add_argument("--no-html", action="store_true",
                    help="Skip HTML dashboard generation")
    ap.add_argument("--db", default=None,
                    help="Path to SQLite database (default: chartbook.db)")
    args = ap.parse_args()

    conn = db.init_db(args.db)
    try:
        export_csvs(conn)
        if not args.csv_only:
            build_dashboard_outputs(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
