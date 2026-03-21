#!/usr/bin/env python3
"""
build_dashboard.py — Build the Egg & Chicken Chartbook dashboard.

Queries SQLite and publishes static dashboard files into docs/ for GitHub Pages.

Usage:
    python build_dashboard.py              # Build docs/data.json + docs/*.html
    python build_dashboard.py --json-only  # Just docs/data.json
    python build_dashboard.py --db path    # Custom DB path
"""

import argparse
import json
import shutil
from datetime import date, datetime, timedelta

from . import db
from .hpai_categories import ALL_POULTRY_PRODUCTION_TYPES
from .hpai_categories import COMMERCIAL_LAYER_TYPES
from .paths import ASSETS_ROOT
from .paths import DOCS_ROOT
from .paths import PACKAGE_ROOT
from .paths import REPO_ROOT

DATA_JSON_PATH = DOCS_ROOT / "data.json"

# ── NASS month mapping ───────────────────────────────────────────────────

MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    "FIRST OF JAN": "01", "FIRST OF FEB": "02", "FIRST OF MAR": "03",
    "FIRST OF APR": "04", "FIRST OF MAY": "05", "FIRST OF JUN": "06",
    "FIRST OF JUL": "07", "FIRST OF AUG": "08", "FIRST OF SEP": "09",
    "FIRST OF OCT": "10", "FIRST OF NOV": "11", "FIRST OF DEC": "12",
    "END OF JAN": "01", "END OF FEB": "02", "END OF MAR": "03",
    "END OF APR": "04", "END OF MAY": "05", "END OF JUN": "06",
    "END OF JUL": "07", "END OF AUG": "08", "END OF SEP": "09",
    "END OF OCT": "10", "END OF NOV": "11", "END OF DEC": "12",
}


def nass_sort_key(year, ref_period):
    """Return a stable chronological sort key for NASS reference periods."""
    ref = (ref_period or "").strip().upper()

    if ref == "YEAR":
        return year, 13, 0
    if ref == "MARKETING YEAR":
        return year, 14, 0

    mm = MONTH_MAP.get(ref)
    if mm:
        day_rank = 1
        if ref.startswith("FIRST OF"):
            day_rank = 0
        elif ref.startswith("END OF"):
            day_rank = 2
        return year, int(mm), day_rank

    if ref.startswith("WEEK #"):
        try:
            return year, 0, int(ref.replace("WEEK #", ""))
        except ValueError:
            pass

    return year, 99, ref


def nass_date(year, ref_period):
    """Convert NASS year + reference_period → 'YYYY-MM' string."""
    mm = MONTH_MAP.get(ref_period)
    if mm:
        return f"{year}-{mm}"
    return None


def latest_nass_observation(conn, data_item, agg_level="NATIONAL", excluded_periods=None):
    """Return the latest observation for a NASS series using chronological ordering."""
    rows = conn.execute("""
        SELECT year, reference_period, value
        FROM nass_data
        WHERE data_item = ? AND agg_level = ?
          AND value IS NOT NULL
    """, (data_item, agg_level)).fetchall()

    excluded = set(excluded_periods or [])
    filtered = [row for row in rows if row[1] not in excluded]
    if not filtered:
        return None
    return max(filtered, key=lambda row: nass_sort_key(row[0], row[1]))


def nass_monthly_series(conn, data_item, agg_level="NATIONAL", period_prefix=None):
    """Query a NASS monthly series → (dates[], values[]) sorted chronologically.

    period_prefix: if set, only include reference_periods starting with this
    string (e.g. 'FIRST OF' to get daily rates instead of monthly totals).
    """
    rows = conn.execute("""
        SELECT year, reference_period, value FROM nass_data
        WHERE data_item = ? AND agg_level = ?
          AND value IS NOT NULL
        ORDER BY year, reference_period
    """, (data_item, agg_level)).fetchall()

    points = []
    for year, ref, val in rows:
        if period_prefix and not ref.startswith(period_prefix):
            continue
        d = nass_date(year, ref)
        if d:
            points.append((d, val, nass_sort_key(year, ref)))

    points.sort(key=lambda row: row[2])
    dates = [row[0] for row in points]
    values = [row[1] for row in points]
    return dates, values


# ── Data aggregation functions ───────────────────────────────────────────

def _safe_div(a, b):
    """Safe division returning None on zero/None."""
    if a is None or b is None or b == 0:
        return None
    return a / b


def build_kpi(conn):
    """Build KPI summary dict."""
    kpi = {}

    # Latest Shell Egg Index price (slug 2843, Caged, White, Graded Loose, Large, National)
    row = conn.execute("""
        SELECT report_date, wtd_avg_price FROM egg_prices
        WHERE slug_id = 2843 AND section = 'Report Detail Weighted'
          AND environment = 'Caged' AND class = 'Large' AND origin = 'National'
          AND color = 'White' AND egg_type = 'Graded Loose'
        ORDER BY report_date DESC LIMIT 1
    """).fetchone()
    if row:
        kpi["egg_index_price"] = row[1]
        kpi["egg_index_date"] = row[0]

    # Previous week price for WoW change
    row2 = conn.execute("""
        SELECT wtd_avg_price FROM egg_prices
        WHERE slug_id = 2843 AND section = 'Report Detail Weighted'
          AND environment = 'Caged' AND class = 'Large' AND origin = 'National'
          AND color = 'White' AND egg_type = 'Graded Loose'
        ORDER BY report_date DESC LIMIT 1 OFFSET 5
    """).fetchone()
    if row2 and row2[0] and kpi.get("egg_index_price"):
        prev = row2[0]
        kpi["egg_index_prev"] = prev
        if prev > 0:
            kpi["egg_index_change_pct"] = round(
                (kpi["egg_index_price"] - prev) / prev * 100, 2
            )

    # Latest NASS layer count
    row = latest_nass_observation(conn, "CHICKENS, LAYERS - INVENTORY")
    if row:
        kpi["layer_count"] = row[2]
        kpi["layer_period"] = f"{row[1]} {row[0]}"

    # Latest NASS egg production
    row = latest_nass_observation(
        conn,
        "EGGS - PRODUCTION, MEASURED IN EGGS",
        excluded_periods={"MARKETING YEAR", "YEAR"},
    )
    if row:
        kpi["egg_production"] = row[2]
        kpi["egg_prod_period"] = f"{row[1]} {row[0]}"

    # Latest retail egg price
    row = conn.execute("""
        SELECT report_date, price_avg FROM retail_prices
        WHERE slug_id = 2757 AND region IN ('National', 'NATIONAL')
          AND type IN ('Large White', 'WHITE LARGE') AND environment = 'Conventional'
          AND price_avg IS NOT NULL
        ORDER BY report_date DESC LIMIT 1
    """).fetchone()
    if row:
        kpi["retail_egg_price"] = row[1]
        kpi["retail_egg_date"] = row[0]

    # Latest chicken breast B/S price (from chicken_wholesale slug 3646)
    row = conn.execute("""
        SELECT report_date, wtd_avg_price FROM chicken_wholesale
        WHERE slug_id = 3646 AND item LIKE '%Breast%Boneless%'
          AND wtd_avg_price IS NOT NULL
        ORDER BY report_date DESC LIMIT 1
    """).fetchone()
    if row:
        kpi["breast_bs_price"] = row[1]
        kpi["breast_bs_date"] = row[0]

    # Latest corn price (FRED)
    try:
        row = conn.execute("""
            SELECT observation_date, value FROM fred_series
            WHERE series_id = 'PMAIZMTUSDM' AND value IS NOT NULL
            ORDER BY observation_date DESC LIMIT 1
        """).fetchone()
        if row:
            kpi["corn_price"] = row[1]
            kpi["corn_date"] = row[0]
    except Exception:
        pass

    # HPAI detections in last 30 days
    try:
        row = conn.execute("""
            SELECT COUNT(*), SUM(CASE WHEN flock_size IS NOT NULL THEN flock_size ELSE 0 END)
            FROM hpai_detections
            WHERE confirmation_date >= date('now', '-30 days')
        """).fetchone()
        if row:
            kpi["hpai_30d_detections"] = row[0]
            kpi["hpai_30d_birds"] = row[1]
    except Exception:
        pass

    return kpi


def build_egg_index(conn):
    """Combined egg prices: Shell Egg Index + NY Shell Egg + Breaking Stock."""
    by_date = {}

    # 1) Shell Egg Index (slug 2843, White/Graded Loose) — wtd_avg_price by environment
    rows = conn.execute("""
        SELECT report_date, environment, wtd_avg_price
        FROM egg_prices
        WHERE slug_id = 2843 AND section = 'Report Detail Weighted'
          AND class = 'Large' AND origin = 'National'
          AND color = 'White' AND egg_type = 'Graded Loose'
          AND wtd_avg_price IS NOT NULL
        ORDER BY report_date, environment
    """).fetchall()
    for dt, env, price in rows:
        by_date.setdefault(dt, {})[env] = price

    # 2) NY Shell Egg (slug 2734) — avg_price by class, prefixed "NY "
    rows = conn.execute("""
        SELECT report_date, class, avg_price
        FROM egg_prices
        WHERE slug_id = 2734 AND avg_price IS NOT NULL
        ORDER BY report_date, class
    """).fetchall()
    for dt, cls, price in rows:
        by_date.setdefault(dt, {})["NY " + cls] = price

    # 3) Breaking Stock (slug 3888) — avg_price by egg_type
    rows = conn.execute("""
        SELECT report_date, egg_type, avg_price
        FROM egg_prices
        WHERE slug_id = 3888 AND avg_price IS NOT NULL
        ORDER BY report_date, egg_type
    """).fetchall()
    for dt, typ, price in rows:
        by_date.setdefault(dt, {})[typ] = price

    dates = sorted(by_date.keys())
    all_keys = sorted({k for d in by_date.values() for k in d})
    series = {k: [by_date[dt].get(k) for dt in dates] for k in all_keys}
    return {"dates": dates, "series": series}


def build_egg_volumes(conn):
    """Daily shell egg trading volumes."""
    rows = conn.execute("""
        SELECT report_date, SUM(volume_shell)
        FROM egg_volumes
        GROUP BY report_date
        ORDER BY report_date
    """).fetchall()
    return {
        "dates": [r[0] for r in rows],
        "volume": [r[1] for r in rows],
    }



def build_regional_egg(conn):
    """Regional egg prices (slug 2848) by region, class=Large."""
    rows = conn.execute("""
        SELECT report_date, region, avg_price
        FROM egg_prices
        WHERE slug_id = 2848 AND class = 'Large' AND avg_price IS NOT NULL
        ORDER BY report_date, region
    """).fetchall()

    by_date = {}
    regions = set()
    for dt, reg, price in rows:
        by_date.setdefault(dt, {})[reg] = price
        regions.add(reg)

    dates = sorted(by_date.keys())
    regions = sorted(regions)
    series = {r: [by_date[d].get(r) for d in dates] for r in regions}
    return {"dates": dates, "series": series}


def build_narratives(conn):
    """Latest market narratives from slug 2843."""
    rows = conn.execute("""
        SELECT report_date, narrative FROM report_narratives
        WHERE slug_id = 2843
        ORDER BY report_date DESC LIMIT 5
    """).fetchall()
    return [{"date": r[0], "text": r[1]} for r in rows]


def build_nass_layers(conn):
    """NASS layer inventory: total + table layers, national."""
    d1, v1 = nass_monthly_series(conn, "CHICKENS, LAYERS - INVENTORY")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, LAYERS, TABLE - INVENTORY")
    return {"dates": d1, "total": v1, "dates_table": d2, "table": v2}


def build_cage_free_composition(conn):
    """AMS cage-free flock composition combined with NASS table-layer totals."""
    empty = {
        "dates": [],
        "organic": [],
        "non_organic_cage_free": [],
        "all_cage_free": [],
        "conventional": [],
        "cage_free_pct": [],
        "table_layers": [],
    }

    try:
        rows = conn.execute("""
            SELECT report_month, category, layer_flock_size
            FROM cage_free_flock_composition
            WHERE layer_flock_size IS NOT NULL
            ORDER BY report_month, category
        """).fetchall()
    except Exception:
        return empty

    if not rows:
        return empty

    by_month = {}
    for report_month, category, flock_size in rows:
        by_month.setdefault(report_month, {})[category] = flock_size

    table_layer_dates, table_layer_values = nass_monthly_series(
        conn,
        "CHICKENS, LAYERS, TABLE - INVENTORY",
    )
    table_layers_by_month = {
        report_month: value
        for report_month, value in zip(table_layer_dates, table_layer_values)
    }

    dates = []
    organic = []
    non_organic_cage_free = []
    all_cage_free = []
    conventional = []
    cage_free_pct = []
    table_layers = []

    for report_month in sorted(by_month):
        organic_value = by_month[report_month].get("organic")
        non_org_value = by_month[report_month].get("non_organic_cage_free")
        all_cf_value = by_month[report_month].get("all_cage_free")
        table_layers_value = table_layers_by_month.get(report_month)
        if table_layers_value is None or all_cf_value is None:
            continue

        conventional_value = max(table_layers_value - all_cf_value, 0)
        cage_free_share = (all_cf_value / table_layers_value * 100) if table_layers_value else None

        dates.append(report_month)
        organic.append((organic_value / 1e6) if organic_value is not None else None)
        non_organic_cage_free.append((non_org_value / 1e6) if non_org_value is not None else None)
        all_cage_free.append((all_cf_value / 1e6) if all_cf_value is not None else None)
        conventional.append(conventional_value / 1e6)
        cage_free_pct.append(cage_free_share)
        table_layers.append(table_layers_value / 1e6)

    return {
        "dates": dates,
        "organic": organic,
        "non_organic_cage_free": non_organic_cage_free,
        "all_cage_free": all_cage_free,
        "conventional": conventional,
        "cage_free_pct": cage_free_pct,
        "table_layers": table_layers,
    }


def _ers_trade_series(conn, commodity, product_order):
    """Normalized ERS trade totals by month for a commodity group."""
    empty = {"dates": []}

    try:
        rows = conn.execute("""
            SELECT report_month, flow, product, value
            FROM ers_trade_totals
            WHERE commodity = ?
            ORDER BY report_month, flow, product
        """, (commodity,)).fetchall()
    except Exception:
        return empty

    if not rows:
        return empty

    by_month = {}
    for report_month, flow, product, value in rows:
        by_month.setdefault(report_month, {})[f"{flow}_{product}"] = value

    dates = sorted(by_month)
    payload = {"dates": dates}
    for flow in ("import", "export"):
        for product in product_order:
            key = f"{flow}_{product}"
            payload[key] = [by_month[report_month].get(key) for report_month in dates]
    return payload


def build_ers_trade_egg(conn):
    """ERS monthly egg trade totals and component sections."""
    data = _ers_trade_series(conn, "egg", ["total", "shell_egg", "egg_product"])
    data["unit_total"] = "1,000 dozen (shell-egg equivalent)"
    data["unit_shell_egg"] = "1,000 dozen"
    return data


def build_ers_trade_chicken(conn):
    """ERS monthly chicken trade totals for broilers and other chicken."""
    data = _ers_trade_series(conn, "chicken", ["broiler", "other_chicken"])
    data["unit"] = "1,000 pounds"
    return data


def build_nass_egg_production(conn):
    """NASS egg production: all + table eggs, national."""
    d1, v1 = nass_monthly_series(conn, "EGGS - PRODUCTION, MEASURED IN EGGS")
    d2, v2 = nass_monthly_series(conn, "EGGS, TABLE - PRODUCTION, MEASURED IN EGGS")
    return {"dates": d1, "total": v1, "dates_table": d2, "table": v2}


def build_nass_rate_of_lay(conn):
    """NASS rate of lay: all + table layers, national.

    Uses 'FIRST OF' period prefix to get daily rates (eggs/100 layers/day,
    ~70-80 range) instead of monthly totals (~2000+ range).
    """
    d1, v1 = nass_monthly_series(conn, "CHICKENS, LAYERS - RATE OF LAY, MEASURED IN EGGS / 100 LAYER",
                                  period_prefix="FIRST OF")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, LAYERS, TABLE - RATE OF LAY, MEASURED IN EGGS / 100 LAYER",
                                  period_prefix="FIRST OF")
    return {"dates": d1, "all": v1, "dates_table": d2, "table": v2}


def build_nass_pullets(conn):
    """NASS replacement pullet inventory, national."""
    d, v = nass_monthly_series(conn, "CHICKENS, PULLETS, REPLACEMENT - INVENTORY")
    return {"dates": d, "values": v}


def build_nass_prices(conn):
    """NASS prices received: eggs and broilers."""
    d1, v1 = nass_monthly_series(conn, "EGGS - PRICE RECEIVED, MEASURED IN $ / DOZEN")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, BROILERS - PRICE RECEIVED, MEASURED IN $ / LB")
    return {"dates_egg": d1, "egg_doz": v1, "dates_broiler": d2, "broiler_lb": v2}


def build_nass_hatchery(conn):
    """NASS hatchery data: chicks hatched + eggs set."""
    d1, v1 = nass_monthly_series(conn, "CHICKENS, CHICKS, BROILER TYPE - HATCHED, MEASURED IN HEAD")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, CHICKS, EGG TYPE - HATCHED, MEASURED IN HEAD")
    d3, v3 = nass_monthly_series(conn, "CHICKENS, BROILERS - EGGS SET, MEASURED IN EGGS")
    return {
        "dates_broiler": d1, "broiler_chicks": v1,
        "dates_egg": d2, "egg_chicks": v2,
        "dates_set": d3, "eggs_set": v3,
    }


def build_nass_breeder_flock(conn):
    """NASS hatching layer inventory, national."""
    d1, v1 = nass_monthly_series(conn, "CHICKENS, LAYERS, HATCHING - INVENTORY")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, LAYERS, HATCHING, BROILER TYPE - INVENTORY")
    broiler_map = {date: value for date, value in zip(d2, v2)}
    egg_type = [
        (value - broiler_map[date]) if value is not None and broiler_map.get(date) is not None else None
        for date, value in zip(d1, v1)
    ]
    return {
        "dates": d1,
        "layers": v1,
        "dates_broiler": d2,
        "broiler_type": v2,
        "egg_type": egg_type,
    }


def build_nass_layer_disposition(conn):
    """NASS monthly layer turnover proxies: slaughter sales + loss/rendered."""
    d1, v1 = nass_monthly_series(conn, "CHICKENS, LAYERS - SALES FOR SLAUGHTER, MEASURED IN HEAD")
    d2, v2 = nass_monthly_series(conn, "CHICKENS, LAYERS - LOSS, DEATH & RENDERED, MEASURED IN HEAD")
    d3, v3 = nass_monthly_series(conn, "CHICKENS, LAYERS - BEING MOLTED, MEASURED IN PCT OF INVENTORY")
    d4, v4 = nass_monthly_series(conn, "CHICKENS, LAYERS - MOLT COMPLETED, MEASURED IN PCT OF INVENTORY")
    return {
        "dates_sales": d1, "sales": v1,
        "dates_loss": d2, "loss": v2,
        "dates_molted": d3, "being_molted_pct": v3,
        "dates_molt_completed": d4, "molt_completed_pct": v4,
    }


def build_nass_shell_broken(conn):
    """Monthly shell eggs broken (dozen) from NASS."""
    d, v = nass_monthly_series(conn, "EGGS, SHELL - BROKEN, MEASURED IN DOZEN")
    return {"dates": d, "dozen": v}


def build_retail_egg_prices(conn):
    """Retail egg prices by environment (weekly, national, Large White)."""
    rows = conn.execute("""
        SELECT report_date, environment, price_avg
        FROM retail_prices
        WHERE slug_id = 2757 AND region IN ('National', 'NATIONAL')
          AND type IN ('Large White', 'WHITE LARGE') AND price_avg IS NOT NULL
        ORDER BY report_date, environment
    """).fetchall()

    by_date = {}
    envs = set()
    for dt, env, price in rows:
        by_date.setdefault(dt, {})[env] = price
        envs.add(env)

    dates = sorted(by_date.keys())
    envs = sorted(envs)
    series = {e: [by_date[d].get(e) for d in dates] for e in envs}
    return {"dates": dates, "series": series}


def build_retail_chicken_prices(conn):
    """Retail chicken prices by type (weekly, national, top types)."""
    rows = conn.execute("""
        SELECT report_date, type, price_avg
        FROM retail_prices
        WHERE slug_id = 2756 AND region IN ('National', 'NATIONAL')
          AND environment = 'Conventional' AND price_avg IS NOT NULL
        ORDER BY report_date, type
    """).fetchall()

    by_date = {}
    types = set()
    for dt, typ, price in rows:
        by_date.setdefault(dt, {})[typ] = price
        types.add(typ)

    dates = sorted(by_date.keys())
    types = sorted(types)
    series = {t: [by_date[d].get(t) for d in dates] for t in types}
    return {"dates": dates, "series": series}


def build_retail_feature(conn, slug_id):
    """Retail feature rate for national region.

    MARS changed format around 2024-09-02: values switched from whole-number
    percentages (e.g. 17.1 = 17.1%) to decimals (e.g. 0.109 = 10.9%).
    Normalize everything to percentage (0-100 scale).
    """
    rows = conn.execute("""
        SELECT report_date, feature_rate
        FROM retail_metrics
        WHERE slug_id = ? AND region IN ('National', 'NATIONAL')
          AND feature_rate IS NOT NULL
        ORDER BY report_date
    """, (slug_id,)).fetchall()

    dates, rates = [], []
    for dt, rate in rows:
        # Values <= 1.0 are decimal format → multiply by 100
        # Values > 1.0 are already percentage format
        if rate <= 1.0:
            rate = round(rate * 100, 2)
        dates.append(dt)
        rates.append(rate)

    return {"dates": dates, "rate": rates}


def build_chicken_wholesale(conn):
    """Weekly chicken wholesale prices by item (slug 3646)."""
    rows = conn.execute("""
        SELECT report_date, item, wtd_avg_price
        FROM chicken_wholesale
        WHERE slug_id = 3646 AND wtd_avg_price IS NOT NULL
        ORDER BY report_date, item
    """).fetchall()

    by_date = {}
    items = set()
    for dt, item, price in rows:
        by_date.setdefault(dt, {})[item] = price
        items.add(item)

    dates = sorted(by_date.keys())
    items = sorted(items)
    series = {i: [by_date[d].get(i) for d in dates] for i in items}
    return {"dates": dates, "series": series}


def build_chicken_volume(conn):
    """Weekly chicken wholesale volume by item (slug 3646)."""
    rows = conn.execute("""
        SELECT report_date, item, volume
        FROM chicken_wholesale
        WHERE slug_id = 3646 AND volume IS NOT NULL
        ORDER BY report_date, item
    """).fetchall()

    by_date = {}
    items = set()
    for dt, item, vol in rows:
        by_date.setdefault(dt, {})[item] = vol
        items.add(item)

    dates = sorted(by_date.keys())
    items = sorted(items)
    series = {i: [by_date[d].get(i) for d in dates] for i in items}
    return {"dates": dates, "series": series}


def build_nass_placements(conn):
    """NASS broiler placements, national (weekly data → aggregate by year)."""
    rows = conn.execute("""
        SELECT year, reference_period, value FROM nass_data
        WHERE data_item = 'CHICKENS, BROILERS - PLACEMENTS, MEASURED IN HEAD'
          AND agg_level = 'NATIONAL' AND value IS NOT NULL
        ORDER BY year, reference_period
    """).fetchall()

    # Weekly data (WEEK #01..#52): return raw with week-based dates
    dates, values = [], []
    for year, ref, val in rows:
        if ref.startswith("WEEK #"):
            week_num = int(ref.replace("WEEK #", ""))
            # Approximate date: year + week number
            from datetime import timedelta
            jan1 = date(year, 1, 1)
            d = jan1 + timedelta(weeks=week_num - 1)
            dates.append(d.isoformat())
            values.append(val)
        elif ref == "YEAR":
            dates.append(f"{year}")
            values.append(val)
    return {"dates": dates, "values": values}


def build_egg_inventory(conn):
    """Weekly shell egg inventory by region."""
    rows = conn.execute("""
        SELECT report_date, region, SUM(volume)
        FROM egg_inventory
        WHERE class = 'Shell Eggs' OR class LIKE '%Total%' OR class = ''
        GROUP BY report_date, region
        ORDER BY report_date, region
    """).fetchall()

    # If that returns nothing, try without class filter
    if not rows:
        rows = conn.execute("""
            SELECT report_date, region, SUM(volume)
            FROM egg_inventory
            GROUP BY report_date, region
            ORDER BY report_date, region
        """).fetchall()

    by_date = {}
    regions = set()
    for dt, reg, vol in rows:
        if vol:
            by_date.setdefault(dt, {})[reg] = vol
            regions.add(reg)

    dates = sorted(by_date.keys())
    regions = sorted(regions)
    series = {r: [by_date[d].get(r) for d in dates] for r in regions}
    return {"dates": dates, "series": series}


def build_eggs_processed(conn):
    """Weekly eggs processed by class (current week period)."""
    rows = conn.execute("""
        SELECT report_date, class, volume
        FROM eggs_processed
        WHERE period = 'Current Week' AND volume IS NOT NULL
        ORDER BY report_date, class
    """).fetchall()

    # If no "Current Week" rows, try without period filter
    if not rows:
        rows = conn.execute("""
            SELECT report_date, class, volume
            FROM eggs_processed
            WHERE volume IS NOT NULL
            ORDER BY report_date, class
        """).fetchall()

    by_date = {}
    classes = set()
    for dt, cls, vol in rows:
        by_date.setdefault(dt, {})[cls] = vol
        classes.add(cls)

    dates = sorted(by_date.keys())
    classes = sorted(classes)
    series = {c: [by_date[d].get(c) for d in dates] for c in classes}
    return {"dates": dates, "series": series}


def build_cold_storage_mars(conn):
    """Weekly cold storage from MARS (slug 1624)."""
    rows = conn.execute("""
        SELECT report_date, commodity, holdings_lbs
        FROM cold_storage
        WHERE holdings_lbs IS NOT NULL
        ORDER BY report_date, commodity
    """).fetchall()

    by_date = {}
    commodities = set()
    for dt, comm, lbs in rows:
        by_date.setdefault(dt, {})[comm] = lbs
        commodities.add(comm)

    dates = sorted(by_date.keys())
    commodities = sorted(commodities)
    series = {c: [by_date[d].get(c) for d in dates] for c in commodities}
    return {"dates": dates, "series": series}


def build_cold_storage_nass(conn):
    """Monthly cold storage from NASS (longer history)."""
    d1, v1 = nass_monthly_series(conn, "CHICKENS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB")
    d2, v2 = nass_monthly_series(conn, "EGGS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB")
    return {"dates_chicken": d1, "chicken_lbs": v1, "dates_egg": d2, "egg_lbs": v2}


def build_retail_events(conn):
    """Latest retail price detail rows for the table."""
    rows = conn.execute("""
        SELECT report_date, region, type, environment, price_avg, price_min,
               price_max, store_count
        FROM retail_prices
        WHERE slug_id = 2757 AND price_avg IS NOT NULL
        ORDER BY report_date DESC
        LIMIT 2000
    """).fetchall()
    return [
        {"d": r[0], "r": r[1], "t": r[2], "e": r[3],
         "p": r[4], "mn": r[5], "mx": r[6], "s": r[7]}
        for r in rows
    ]


# ── New data builders (Phase 2) ────────────────────────────────────────

def build_fred_feed_costs(conn):
    """FRED corn + soybean meal prices from v_feed_costs view."""
    try:
        rows = conn.execute("""
            SELECT observation_date, corn_price, sbm_price
            FROM v_feed_costs
            WHERE corn_price IS NOT NULL OR sbm_price IS NOT NULL
            ORDER BY observation_date
        """).fetchall()
    except Exception:
        return {"dates": [], "corn": [], "sbm": []}

    return {
        "dates": [r[0] for r in rows],
        "corn": [r[1] for r in rows],
        "sbm": [r[2] for r in rows],
    }


def build_fred_ppi(conn):
    """FRED PPI series for poultry products."""
    try:
        rows = conn.execute("""
            SELECT observation_date, series_id, value
            FROM fred_series
            WHERE series_id IN ('WPU0171', 'WPU0141', 'WPU014102')
              AND value IS NOT NULL
            ORDER BY observation_date, series_id
        """).fetchall()
    except Exception:
        return {"dates": [], "series": {}}

    by_date = {}
    series_keys = set()
    for dt, sid, val in rows:
        by_date.setdefault(dt, {})[sid] = val
        series_keys.add(sid)

    dates = sorted(by_date.keys())
    series = {k: [by_date[d].get(k) for d in dates] for k in sorted(series_keys)}
    labels = {
        "WPU0171": "PPI: Chicken Eggs",
        "WPU0141": "PPI: Slaughter Chickens",
        "WPU014102": "PPI: Broilers",
    }
    return {"dates": dates, "series": series, "labels": labels}


def build_fred_retail_egg(conn):
    """FRED retail egg series (BLS via FRED), monthly."""
    try:
        rows = conn.execute("""
            SELECT substr(observation_date, 1, 7) AS month, value
            FROM fred_series
            WHERE series_id = 'APU0000708111'
              AND value IS NOT NULL
            ORDER BY observation_date
        """).fetchall()
    except Exception:
        return {"dates": [], "values": []}

    return {
        "dates": [row[0] for row in rows],
        "values": [row[1] for row in rows],
    }


def build_fred_diesel(conn):
    """FRED diesel series (EIA via FRED), weekly."""
    try:
        rows = conn.execute("""
            SELECT observation_date, value
            FROM fred_series
            WHERE series_id = 'GASDESW'
              AND value IS NOT NULL
            ORDER BY observation_date
        """).fetchall()
    except Exception:
        return {"dates": [], "values": []}

    return {
        "dates": [row[0] for row in rows],
        "values": [row[1] for row in rows],
    }


def build_input_indices(conn):
    """Feed, diesel, and packaging indices rebased to Jan 2025 = 100."""
    base_month = "2025-01"
    base_start = "2025-01-01"

    def rebase(date_rows, *, base_prefix=None, base_floor=None):
        values_by_date = {label: value for label, value in date_rows if value is not None}
        if base_floor:
            base_candidates = [
                (label, value) for label, value in sorted(values_by_date.items())
                if str(label) >= base_floor
            ]
            base_value = base_candidates[0][1] if base_candidates else None
        else:
            prefix = base_prefix or base_month
            base_candidates = [
                value for label, value in values_by_date.items()
                if str(label).startswith(prefix)
            ]
            base_value = base_candidates[0] if base_candidates else None

        if not base_value:
            return {}
        return {
            label: round((value / base_value) * 100.0, 4)
            for label, value in values_by_date.items()
            if value is not None
        }

    def weekly_average(date_rows):
        grouped = {}
        for trade_date, value in date_rows:
            if value is None:
                continue
            dt = date.fromisoformat(trade_date)
            week_label = (dt + timedelta(days=(7 - dt.weekday()) % 7)).isoformat()
            grouped.setdefault(week_label, []).append(value)
        return [
            (week_label, sum(values) / len(values))
            for week_label, values in sorted(grouped.items())
        ]

    try:
        feed_rows = conn.execute("""
            SELECT trade_date, ration_cost
            FROM cme_feed_daily
            WHERE ration_cost IS NOT NULL
            ORDER BY trade_date
        """).fetchall()
    except Exception:
        feed_rows = []

    feed_rows = weekly_average(feed_rows) if feed_rows else []

    if not feed_rows:
        try:
            feed_rows = conn.execute("""
                SELECT substr(observation_date, 1, 7) AS month,
                       AVG(0.67 * corn_price + 0.22 * sbm_price) AS avg_feed_cost
                FROM v_feed_costs
                WHERE corn_price IS NOT NULL AND sbm_price IS NOT NULL
                GROUP BY substr(observation_date, 1, 7)
                ORDER BY month
            """).fetchall()
        except Exception:
            feed_rows = []

    try:
        diesel_rows = conn.execute("""
            SELECT observation_date, value
            FROM fred_series
            WHERE series_id = 'GASDESW'
              AND value IS NOT NULL
            ORDER BY observation_date
        """).fetchall()
    except Exception:
        diesel_rows = []

    try:
        packaging_rows = conn.execute("""
            SELECT substr(observation_date, 1, 7) AS month, AVG(value) AS avg_packaging
            FROM fred_series
            WHERE series_id = 'PCU322219322219'
              AND value IS NOT NULL
            GROUP BY substr(observation_date, 1, 7)
            ORDER BY month
        """).fetchall()
    except Exception:
        packaging_rows = []

    try:
        electricity_rows = conn.execute("""
            SELECT substr(observation_date, 1, 7) AS month, AVG(value) AS avg_electricity
            FROM fred_series
            WHERE series_id = 'APU000072610'
              AND value IS NOT NULL
            GROUP BY substr(observation_date, 1, 7)
            ORDER BY month
        """).fetchall()
    except Exception:
        electricity_rows = []

    series_maps = {
        "Layer feed": rebase(feed_rows, base_floor=base_start),
        "Diesel": rebase(diesel_rows, base_floor=base_start),
        "Paperboard packaging": rebase(packaging_rows, base_prefix=base_month),
        "Electricity": rebase(electricity_rows, base_prefix=base_month),
    }
    active_series = {label: values for label, values in series_maps.items() if values}
    if not active_series:
        return {"dates": [], "series": {}, "base_month": base_month}

    dates = sorted({month for values in active_series.values() for month in values})
    return {
        "dates": dates,
        "series": {
            label: [values.get(month) for month in dates]
            for label, values in active_series.items()
        },
        "base_month": base_month,
    }


def build_bls_retail(conn):
    """BLS CPI retail prices for eggs and chicken."""
    try:
        rows = conn.execute("""
            SELECT year, month, egg_price, chicken_whole_price,
                   chicken_breast_price, chicken_breast_bonein_price
            FROM v_cross_protein_cpi
            ORDER BY year, month
        """).fetchall()
    except Exception:
        return {"dates": [], "egg": [], "chicken_whole": [],
                "chicken_breast": [], "chicken_breast_bonein": []}

    dates = [f"{r[0]}-{r[1]:02d}" for r in rows]
    return {
        "dates": dates,
        "egg": [r[2] for r in rows],
        "chicken_whole": [r[3] for r in rows],
        "chicken_breast": [r[4] for r in rows],
        "chicken_breast_bonein": [r[5] for r in rows],
    }


def build_hpai_summary(conn):
    """Monthly HPAI detection counts + bird totals across all APHIS categories."""
    all_types_placeholders = ", ".join("?" for _ in ALL_POULTRY_PRODUCTION_TYPES)
    try:
        rows = conn.execute("""
            WITH dedup AS (
                SELECT confirmation_date, state, county, flock_type, flock_size
                FROM hpai_detections
                WHERE confirmation_date IS NOT NULL
                  AND flock_type IN (""" + all_types_placeholders + """)
                GROUP BY confirmation_date, state, county, flock_type, flock_size
            )
            SELECT strftime('%Y-%m', confirmation_date) AS month,
                   COUNT(*) AS detections,
                   SUM(CASE WHEN flock_size IS NOT NULL THEN flock_size ELSE 0 END) AS birds
            FROM dedup
            GROUP BY month
            ORDER BY month
        """, ALL_POULTRY_PRODUCTION_TYPES).fetchall()
    except Exception:
        return {"dates": [], "detections": [], "commercial_birds": []}

    return {
        "dates": [r[0] for r in rows],
        "detections": [r[1] for r in rows],
        "commercial_birds": [r[2] for r in rows],
    }


def build_hpai_by_state(conn):
    """HPAI detections by state (top 15)."""
    try:
        rows = conn.execute("""
            SELECT state, COUNT(*) as cnt,
                   SUM(CASE WHEN flock_size IS NOT NULL THEN flock_size ELSE 0 END) as birds
            FROM hpai_detections
            WHERE state IS NOT NULL
            GROUP BY state
            ORDER BY birds DESC
            LIMIT 15
        """).fetchall()
    except Exception:
        return {"states": [], "detections": [], "birds": []}

    return {
        "states": [r[0] for r in rows],
        "detections": [r[1] for r in rows],
        "birds": [r[2] for r in rows],
    }


def build_hpai_layers(conn):
    """Monthly HPAI birds affected for the HPAI dashboard's Commercial Layers set."""
    all_types_placeholders = ", ".join("?" for _ in ALL_POULTRY_PRODUCTION_TYPES)
    layer_type_placeholders = ", ".join("?" for _ in COMMERCIAL_LAYER_TYPES)
    try:
        month_rows = conn.execute("""
            WITH dedup AS (
                SELECT confirmation_date, state, county, flock_type, flock_size
                FROM hpai_detections
                WHERE confirmation_date IS NOT NULL
                  AND flock_type IN (""" + all_types_placeholders + """)
                GROUP BY confirmation_date, state, county, flock_type, flock_size
            )
            SELECT DISTINCT strftime('%Y-%m', confirmation_date) AS month
            FROM dedup
            ORDER BY month
        """, ALL_POULTRY_PRODUCTION_TYPES).fetchall()

        rows = conn.execute("""
            WITH dedup AS (
                SELECT confirmation_date, state, county, flock_type, flock_size
                FROM hpai_detections
                WHERE confirmation_date IS NOT NULL
                  AND flock_type IN (""" + all_types_placeholders + """)
                GROUP BY confirmation_date, state, county, flock_type, flock_size
            )
            SELECT strftime('%Y-%m', confirmation_date) AS month,
                   COUNT(*) AS detections,
                   SUM(CASE WHEN flock_size IS NOT NULL THEN flock_size ELSE 0 END) AS birds
            FROM dedup
            WHERE flock_type IN (?, ?, ?)
            GROUP BY month
            ORDER BY month
        """, ALL_POULTRY_PRODUCTION_TYPES + COMMERCIAL_LAYER_TYPES).fetchall()

        category_rows = conn.execute("""
            WITH dedup AS (
                SELECT confirmation_date, state, county, flock_type, flock_size
                FROM hpai_detections
                WHERE confirmation_date IS NOT NULL
                  AND flock_type IN (""" + all_types_placeholders + """)
                GROUP BY confirmation_date, state, county, flock_type, flock_size
            )
            SELECT strftime('%Y-%m', confirmation_date) AS month,
                   flock_type,
                   COUNT(*) AS detections,
                   SUM(CASE WHEN flock_size IS NOT NULL THEN flock_size ELSE 0 END) AS birds
            FROM dedup
            WHERE flock_type IN (""" + layer_type_placeholders + """)
            GROUP BY month, flock_type
            ORDER BY month, flock_type
        """, ALL_POULTRY_PRODUCTION_TYPES + COMMERCIAL_LAYER_TYPES).fetchall()
    except Exception:
        return {"dates": [], "detections": [], "birds": []}

    all_months = [row[0] for row in month_rows]
    layer_by_month = {
        row[0]: {
            "detections": row[1],
            "birds": row[2],
        }
        for row in rows
    }
    category_map = {
        flock_type: {"birds": {}, "detections": {}}
        for flock_type in COMMERCIAL_LAYER_TYPES
    }
    for month, flock_type, detections, birds in category_rows:
        category_map.setdefault(flock_type, {"birds": {}, "detections": {}})
        category_map[flock_type]["birds"][month] = birds or 0
        category_map[flock_type]["detections"][month] = detections or 0

    return {
        "dates": all_months,
        "detections": [layer_by_month.get(month, {}).get("detections", 0) for month in all_months],
        "birds": [layer_by_month.get(month, {}).get("birds", 0) for month in all_months],
        "categories": list(COMMERCIAL_LAYER_TYPES),
        "birds_by_category": {
            flock_type: [category_map[flock_type]["birds"].get(month, 0) for month in all_months]
            for flock_type in COMMERCIAL_LAYER_TYPES
        },
        "detections_by_category": {
            flock_type: [category_map[flock_type]["detections"].get(month, 0) for month in all_months]
            for flock_type in COMMERCIAL_LAYER_TYPES
        },
    }


def build_cage_free_spread(conn):
    """Cage-free vs conventional spread from Shell Egg Index (slug 2843)."""
    rows = conn.execute("""
        SELECT report_date, environment, wtd_avg_price
        FROM egg_prices
        WHERE slug_id = 2843 AND section = 'Report Detail Weighted'
          AND class = 'Large' AND origin = 'National'
          AND color = 'White' AND egg_type = 'Graded Loose'
          AND wtd_avg_price IS NOT NULL
        ORDER BY report_date, environment
    """).fetchall()

    by_date = {}
    for dt, env, price in rows:
        by_date.setdefault(dt, {})[env] = price

    dates = sorted(by_date.keys())
    caged = []
    cage_free = []
    spread = []
    for d in dates:
        c = by_date[d].get("Caged")
        cf = by_date[d].get("Cage-Free")
        caged.append(c)
        cage_free.append(cf)
        spread.append(round(cf - c, 4) if c and cf else None)

    return {"dates": dates, "caged": caged, "cage_free": cage_free, "spread": spread}


def build_feed_index(conn):
    """Layer feed cost index.

    Prefer the reconstructed daily CME-derived series when present.
    Fall back to the older monthly FRED proxy otherwise.
    """
    try:
        rows = conn.execute("""
            SELECT trade_date, ration_cost
            FROM cme_feed_daily
            WHERE ration_cost IS NOT NULL
            ORDER BY trade_date
        """).fetchall()
    except Exception:
        rows = []

    if rows:
        target_reset_date = "2026-01-01"
        source_row = conn.execute("""
            SELECT source_type
            FROM cme_feed_daily
            WHERE source_type IS NOT NULL
            ORDER BY trade_date DESC
            LIMIT 1
        """).fetchone()
        base_row = conn.execute("""
            SELECT trade_date, ration_cost
            FROM cme_feed_daily
            WHERE ration_cost IS NOT NULL
              AND trade_date >= ?
            ORDER BY trade_date
            LIMIT 1
        """, (target_reset_date,)).fetchone()
        if not base_row:
            base_row = rows[0]
        base_date = base_row[0]
        base_ration = base_row[1]
        return {
            "dates": [r[0] for r in rows],
            "index": [((r[1] / base_ration) * 100.0) if base_ration else None for r in rows],
            "base_date": base_date,
            "source": source_row[0] if source_row else "cme_feed_daily",
            "composition": {
                "corn": 0.67,
                "soymeal": 0.22,
                "calcium": 0.08,
                "other": 0.03,
            },
        }

    try:
        rows = conn.execute("""
            SELECT observation_date, corn_price, sbm_price
            FROM v_feed_costs
            WHERE corn_price IS NOT NULL AND sbm_price IS NOT NULL
            ORDER BY observation_date
        """).fetchall()
    except Exception:
        return {"dates": [], "index": []}

    if not rows:
        return {"dates": [], "index": []}

    base_corn = rows[0][1]
    base_sbm = rows[0][2]
    base_composite = 0.67 * base_corn + 0.22 * base_sbm

    dates = []
    index_vals = []
    for dt, corn, sbm in rows:
        composite = 0.67 * corn + 0.22 * sbm
        idx = round(composite / base_composite * 100, 2) if base_composite else None
        dates.append(dt)
        index_vals.append(idx)

    return {"dates": dates, "index": index_vals, "base_date": rows[0][0], "source": "FRED proxy"}


def build_feed_ratios(conn):
    """Egg/feed and broiler/feed ratios using NASS prices + available feed costs."""
    # Get NASS egg prices (monthly)
    egg_d, egg_v = nass_monthly_series(conn, "EGGS - PRICE RECEIVED, MEASURED IN $ / DOZEN")
    broiler_d, broiler_v = nass_monthly_series(conn, "CHICKENS, BROILERS - PRICE RECEIVED, MEASURED IN $ / LB")

    try:
        feed_rows = conn.execute("""
            SELECT substr(trade_date, 1, 7) AS month, AVG(ration_cost)
            FROM cme_feed_daily
            WHERE ration_cost IS NOT NULL
            GROUP BY month
        """).fetchall()
    except Exception:
        feed_rows = []

    if feed_rows:
        feed_by_month = {month: ration_cost for month, ration_cost in feed_rows}
    else:
        try:
            feed_rows = conn.execute("""
                SELECT substr(observation_date, 1, 7) as month, corn_price, sbm_price
                FROM v_feed_costs
                WHERE corn_price IS NOT NULL AND sbm_price IS NOT NULL
            """).fetchall()
        except Exception:
            return {"egg_dates": [], "egg_ratio": [], "broiler_dates": [], "broiler_ratio": []}

        feed_by_month = {}
        for month, corn, sbm in feed_rows:
            feed_by_month[month] = 0.67 * corn + 0.22 * sbm

    # Compute ratios
    egg_ratio_dates, egg_ratios = [], []
    for d, price in zip(egg_d, egg_v):
        feed = feed_by_month.get(d)
        if feed and price:
            egg_ratio_dates.append(d)
            egg_ratios.append(round(price / (feed / 100), 4))

    broiler_ratio_dates, broiler_ratios = [], []
    for d, price in zip(broiler_d, broiler_v):
        feed = feed_by_month.get(d)
        if feed and price:
            broiler_ratio_dates.append(d)
            broiler_ratios.append(round(price / (feed / 100), 4))

    return {
        "egg_dates": egg_ratio_dates, "egg_ratio": egg_ratios,
        "broiler_dates": broiler_ratio_dates, "broiler_ratio": broiler_ratios,
    }


def build_broiler_hatchability(conn):
    """Weekly broiler hatchability series sourced from ESMIS reports."""
    rows = conn.execute("""
        SELECT release_date, hatchability_pct
        FROM broiler_hatchability
        WHERE hatchability_pct IS NOT NULL
        ORDER BY release_date
    """).fetchall()
    return {
        "dates": [row[0] for row in rows],
        "values": [row[1] for row in rows],
    }


def build_data_freshness(conn):
    """Data freshness summary from etl_log."""
    rows = conn.execute("""
        SELECT id, source, COALESCE(data_item, CAST(slug_id AS TEXT)) as item,
               fetched_at, fetch_end, rows_fetched, status
        FROM etl_log
        ORDER BY source, item, fetched_at, id
    """).fetchall()

    grouped = {}
    for row_id, source, item, fetched_at, fetch_end, rows_fetched, status in rows:
        key = (source, item)
        entry = grouped.setdefault(key, {
            "source": source,
            "item": item,
            "last_fetch": fetched_at,
            "latest_data": fetch_end,
            "total_rows": 0,
            "status": status,
            "_last_id": row_id,
        })
        entry["total_rows"] += rows_fetched or 0
        if fetch_end and (entry["latest_data"] is None or fetch_end > entry["latest_data"]):
            entry["latest_data"] = fetch_end
        if (fetched_at, row_id) >= (entry["last_fetch"], entry["_last_id"]):
            entry["last_fetch"] = fetched_at
            entry["status"] = status
            entry["_last_id"] = row_id

    results = []
    for entry in grouped.values():
        entry.pop("_last_id", None)
        results.append(entry)

    return sorted(results, key=lambda row: (row["source"], row["item"] or ""))


# ── Main build ───────────────────────────────────────────────────────────

def build_data_json(conn):
    """Build the complete data.json for the dashboard."""
    print("  Building data.json ...")
    data = {
        "updated": date.today().strftime("%B %d, %Y"),
    }

    print("    KPIs ...", end=" ", flush=True)
    data["kpi"] = build_kpi(conn)
    print("ok")

    print("    Egg Prices (combined) ...", end=" ", flush=True)
    data["egg_index"] = build_egg_index(conn)
    print(f"{len(data['egg_index']['dates'])} dates, {len(data['egg_index']['series'])} series")

    print("    Egg Volumes ...", end=" ", flush=True)
    data["egg_volumes"] = build_egg_volumes(conn)
    print(f"{len(data['egg_volumes']['dates'])} dates")

    print("    Regional Egg ...", end=" ", flush=True)
    data["regional_egg"] = build_regional_egg(conn)
    print(f"{len(data['regional_egg']['dates'])} dates")

    print("    Narratives ...", end=" ", flush=True)
    data["narratives"] = build_narratives(conn)
    print(f"{len(data['narratives'])} entries")

    print("    NASS Layers ...", end=" ", flush=True)
    data["nass_layers"] = build_nass_layers(conn)
    print(f"{len(data['nass_layers']['dates'])} dates")

    print("    Cage-Free Composition ...", end=" ", flush=True)
    data["cage_free_composition"] = build_cage_free_composition(conn)
    print(f"{len(data['cage_free_composition']['dates'])} dates")

    print("    ERS Egg Trade ...", end=" ", flush=True)
    data["ers_trade_egg"] = build_ers_trade_egg(conn)
    print(f"{len(data['ers_trade_egg']['dates'])} dates")

    print("    ERS Chicken Trade ...", end=" ", flush=True)
    data["ers_trade_chicken"] = build_ers_trade_chicken(conn)
    print(f"{len(data['ers_trade_chicken']['dates'])} dates")

    print("    NASS Egg Production ...", end=" ", flush=True)
    data["nass_egg_production"] = build_nass_egg_production(conn)
    print(f"{len(data['nass_egg_production']['dates'])} dates")

    print("    NASS Rate of Lay ...", end=" ", flush=True)
    data["nass_rate_of_lay"] = build_nass_rate_of_lay(conn)
    print(f"{len(data['nass_rate_of_lay']['dates'])} dates")

    print("    NASS Pullets ...", end=" ", flush=True)
    data["nass_pullets"] = build_nass_pullets(conn)
    print(f"{len(data['nass_pullets']['dates'])} dates")

    print("    NASS Prices ...", end=" ", flush=True)
    data["nass_prices"] = build_nass_prices(conn)
    print(f"{len(data['nass_prices']['dates_egg'])} egg, {len(data['nass_prices']['dates_broiler'])} broiler")

    print("    NASS Hatchery ...", end=" ", flush=True)
    data["nass_hatchery"] = build_nass_hatchery(conn)
    print(f"{len(data['nass_hatchery']['dates_broiler'])} dates")

    print("    NASS Breeder Flock ...", end=" ", flush=True)
    data["nass_breeder_flock"] = build_nass_breeder_flock(conn)
    print(f"{len(data['nass_breeder_flock']['dates'])} dates")

    print("    NASS Layer Disposition ...", end=" ", flush=True)
    data["nass_layer_disposition"] = build_nass_layer_disposition(conn)
    print(f"{len(data['nass_layer_disposition']['dates_sales'])} sales dates")

    print("    NASS Shell Broken ...", end=" ", flush=True)
    data["nass_shell_broken"] = build_nass_shell_broken(conn)
    print(f"{len(data['nass_shell_broken']['dates'])} dates")

    print("    Retail Egg Prices ...", end=" ", flush=True)
    data["retail_egg_prices"] = build_retail_egg_prices(conn)
    print(f"{len(data['retail_egg_prices']['dates'])} dates")

    print("    Retail Chicken Prices ...", end=" ", flush=True)
    data["retail_chicken_prices"] = build_retail_chicken_prices(conn)
    print(f"{len(data['retail_chicken_prices']['dates'])} dates")

    print("    Retail Egg Feature ...", end=" ", flush=True)
    data["retail_egg_feature"] = build_retail_feature(conn, 2757)
    print(f"{len(data['retail_egg_feature']['dates'])} dates")

    print("    Retail Chicken Feature ...", end=" ", flush=True)
    data["retail_chicken_feature"] = build_retail_feature(conn, 2756)
    print(f"{len(data['retail_chicken_feature']['dates'])} dates")

    print("    Chicken Wholesale ...", end=" ", flush=True)
    data["chicken_wholesale"] = build_chicken_wholesale(conn)
    print(f"{len(data['chicken_wholesale']['dates'])} dates")

    print("    Chicken Volume ...", end=" ", flush=True)
    data["chicken_volume"] = build_chicken_volume(conn)
    print(f"{len(data['chicken_volume']['dates'])} dates")

    print("    NASS Placements ...", end=" ", flush=True)
    data["nass_placements"] = build_nass_placements(conn)
    print(f"{len(data['nass_placements']['dates'])} dates")

    print("    Egg Inventory ...", end=" ", flush=True)
    data["egg_inventory"] = build_egg_inventory(conn)
    print(f"{len(data['egg_inventory']['dates'])} dates")

    print("    Eggs Processed ...", end=" ", flush=True)
    data["eggs_processed"] = build_eggs_processed(conn)
    print(f"{len(data['eggs_processed']['dates'])} dates")

    print("    Cold Storage (MARS) ...", end=" ", flush=True)
    data["cold_storage_mars"] = build_cold_storage_mars(conn)
    print(f"{len(data['cold_storage_mars']['dates'])} dates")

    print("    Cold Storage (NASS) ...", end=" ", flush=True)
    data["cold_storage_nass"] = build_cold_storage_nass(conn)
    print(f"{len(data['cold_storage_nass']['dates_chicken'])} dates")

    print("    Retail Detail Events ...", end=" ", flush=True)
    data["retail_detail_events"] = build_retail_events(conn)
    print(f"{len(data['retail_detail_events'])} rows")

    # ── New Phase 2 data ──
    print("    Cage-Free Spread ...", end=" ", flush=True)
    data["cage_free_spread"] = build_cage_free_spread(conn)
    print(f"{len(data['cage_free_spread']['dates'])} dates")

    print("    FRED Feed Costs ...", end=" ", flush=True)
    data["fred_feed_costs"] = build_fred_feed_costs(conn)
    print(f"{len(data['fred_feed_costs']['dates'])} dates")

    print("    FRED PPI ...", end=" ", flush=True)
    data["fred_ppi"] = build_fred_ppi(conn)
    print(f"{len(data['fred_ppi']['dates'])} dates")

    print("    FRED Retail Egg ...", end=" ", flush=True)
    data["fred_retail_egg"] = build_fred_retail_egg(conn)
    print(f"{len(data['fred_retail_egg']['dates'])} dates")

    print("    FRED Diesel ...", end=" ", flush=True)
    data["fred_diesel"] = build_fred_diesel(conn)
    print(f"{len(data['fred_diesel']['dates'])} dates")

    print("    BLS Retail ...", end=" ", flush=True)
    data["bls_retail"] = build_bls_retail(conn)
    print(f"{len(data['bls_retail']['dates'])} dates")

    print("    HPAI Summary ...", end=" ", flush=True)
    data["hpai_summary"] = build_hpai_summary(conn)
    print(f"{len(data['hpai_summary']['dates'])} dates")

    print("    HPAI by State ...", end=" ", flush=True)
    data["hpai_by_state"] = build_hpai_by_state(conn)
    print(f"{len(data['hpai_by_state']['states'])} states")

    print("    HPAI Layers ...", end=" ", flush=True)
    data["hpai_layers"] = build_hpai_layers(conn)
    print(f"{len(data['hpai_layers']['dates'])} dates")

    print("    Feed Index ...", end=" ", flush=True)
    data["feed_index"] = build_feed_index(conn)
    print(f"{len(data['feed_index']['dates'])} dates")

    print("    Input Indices ...", end=" ", flush=True)
    data["input_indices"] = build_input_indices(conn)
    print(f"{len(data['input_indices']['dates'])} dates")

    print("    Feed Ratios ...", end=" ", flush=True)
    data["feed_ratios"] = build_feed_ratios(conn)
    print(f"{len(data['feed_ratios']['egg_dates'])} egg, {len(data['feed_ratios']['broiler_dates'])} broiler")

    print("    Broiler Hatchability ...", end=" ", flush=True)
    data["broiler_hatchability"] = build_broiler_hatchability(conn)
    print(f"{len(data['broiler_hatchability']['dates'])} dates")

    print("    Data Freshness ...", end=" ", flush=True)
    data["data_freshness"] = build_data_freshness(conn)
    print(f"{len(data['data_freshness'])} sources")

    DOCS_ROOT.mkdir(parents=True, exist_ok=True)

    # Write data.json
    out_path = DATA_JSON_PATH
    with open(out_path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    size_kb = out_path.stat().st_size / 1024
    print(f"\n  data.json written ({size_kb:.0f} KB)")

    return data


def build_html(data):
    """Generate split dashboard HTML files."""
    from .templates.home_page_template import HTML_TEMPLATE as HOME_TEMPLATE
    from .templates.egg_page_template import HTML_TEMPLATE as EGG_TEMPLATE
    from .templates.broiler_page_template import HTML_TEMPLATE as BROILER_TEMPLATE

    DOCS_ROOT.mkdir(parents=True, exist_ok=True)
    ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
    web_root = PACKAGE_ROOT / "web"
    for asset_name in (
        "split-dashboard.css",
        "dashboard-common.js",
        "egg-dashboard.js",
        "broiler-dashboard.js",
    ):
        shutil.copy2(web_root / asset_name, ASSETS_ROOT / asset_name)
    shutil.copy2(
        REPO_ROOT / "iaa-logo-with-navy-font-full-color.png",
        ASSETS_ROOT / "iaa-logo-with-navy-font-full-color.png",
    )

    outputs = {
        "index.html": HOME_TEMPLATE,
        "egg-dashboard.html": EGG_TEMPLATE,
        "broiler-dashboard.html": BROILER_TEMPLATE,
    }

    for filename, template in outputs.items():
        html = template.replace("__UPDATED__", data["updated"])
        out_path = DOCS_ROOT / filename
        with open(out_path, "w") as f:
            f.write(html)
        size_kb = out_path.stat().st_size / 1024
        print(f"  {filename} written ({size_kb:.0f} KB)")


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Build chartbook dashboard")
    ap.add_argument("--json-only", action="store_true",
                    help="Only build data.json (skip HTML)")
    ap.add_argument("--db", default=None,
                    help="Path to SQLite database")
    args = ap.parse_args()

    conn = db.init_db(args.db)
    try:
        data = build_data_json(conn)
        if not args.json_only:
            build_html(data)
    finally:
        conn.close()

    print("\n  Done! Test with: python3 -m http.server 8011 -d docs")


if __name__ == "__main__":
    main()
