"""
parsers.py — Transform raw API JSON into normalized row dicts for SQLite.

MARS: 8 parser functions for 12 reports (similar reports share parsers).
NASS: 1 universal parser for all QuickStats records.
"""

from datetime import datetime


# ── Helpers ──────────────────────────────────────────────────────────────

def normalize_date(date_str):
    """Convert MM/DD/YYYY → YYYY-MM-DD. Returns original string on failure."""
    if not date_str:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def _safe_float(val):
    """Parse a string to float, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",", ""))
    except (ValueError, TypeError):
        return None


def _safe_int(val):
    """Parse a string to int, returning None on failure."""
    if val is None or val == "":
        return None
    try:
        return int(float(str(val).replace(",", "")))
    except (ValueError, TypeError):
        return None


def _get(record, key, default=None):
    """Get a value from a dict, treating 'N/A' and '' as missing."""
    v = record.get(key, default)
    if v in (None, "", "N/A"):
        return default
    return v


# ── MARS Parsers ─────────────────────────────────────────────────────────

def parse_egg_prices(slug_id, sections):
    """Parse slugs 2843, 2734, 2848, 3888 → rows for egg_prices table.

    Handles both Detail Weighted (2843) and Detail Simple (2734, 2848, 3888)
    sections.
    """
    rows = []
    target_sections = ("Report Detail Weighted", "Report Detail Simple")

    for sec in sections:
        sec_name = sec.get("reportSection", "")
        if sec_name not in target_sections:
            continue
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            rows.append({
                "report_date": date,
                "slug_id": slug_id,
                "section": sec_name,
                "environment": _get(r, "environment", ""),
                "class": _get(r, "class", ""),
                "color": _get(r, "color", ""),
                "egg_type": _get(r, "egg_type", ""),
                "origin": _get(r, "origin", ""),
                "region": _get(r, "region", ""),
                "destination": _get(r, "destination", ""),
                "freight": _get(r, "freight", ""),
                "grade": _get(r, "grade", ""),
                "purchase_type": _get(r, "purchase_type", ""),
                "delivery": _get(r, "delivery", ""),
                "price_low": _safe_float(r.get("price_low")),
                "price_high": _safe_float(r.get("price_high")),
                "avg_price": _safe_float(r.get("avg_price")),
                "wtd_avg_price": _safe_float(r.get("wtd_avg_price")),
                "volume": _safe_int(r.get("volume")),
                "avg_price_prev": _safe_float(r.get("avg_price_previous")),
                "wtd_avg_price_prev": _safe_float(r.get("wtd_avg_price_previous")),
                "wtd_avg_price_ly": _safe_float(r.get("wtd_avg_price_last_year")),
                "price_unit": _get(r, "price_unit"),
                "volume_unit": _get(r, "volume_unit"),
            })
    return rows


def parse_egg_volumes(sections):
    """Parse slug 2843 Volume Weighted section → egg_volumes table."""
    rows = []
    for sec in sections:
        if sec.get("reportSection") != "Report Volume Weighted":
            continue
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            vol = _safe_int(r.get("volume_Shell") or r.get("volume_shell"))
            if vol is None:
                continue
            rows.append({
                "report_date": date,
                "origin": _get(r, "origin", ""),
                "destination": _get(r, "destination", ""),
                "purchase_type": _get(r, "purchase_type"),
                "volume_shell": vol,
                "volume_unit": _get(r, "shell_Volume_Unit")
                              or _get(r, "shell_volume_unit"),
            })
    return rows


def parse_egg_inventory(sections):
    """Parse slug 1427 → egg_inventory table."""
    rows = []
    for sec in (sections if isinstance(sections, list) else [sections]):
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            rows.append({
                "report_date": date,
                "region": _get(r, "region", ""),
                "class": _get(r, "class", ""),
                "type": _get(r, "type", ""),
                "volume": _safe_float(r.get("volume")),
                "pct_chg": _get(r, "pct_chg_last_week"),
            })
    return rows


def parse_eggs_processed(sections):
    """Parse slug 1665 → eggs_processed table."""
    rows = []
    for sec in (sections if isinstance(sections, list) else [sections]):
        for r in sec.get("results", []):
            date = normalize_date(
                r.get("report_begin_date") or r.get("report_Date") or r.get("report_date")
            )
            if not date:
                continue
            rows.append({
                "report_date": date,
                "class": _get(r, "class", ""),
                "period": _get(r, "period", ""),
                "volume": _safe_float(r.get("volume")),
            })
    return rows


def parse_cold_storage(sections):
    """Parse slug 1624 → cold_storage table."""
    rows = []
    for sec in (sections if isinstance(sections, list) else [sections]):
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            rows.append({
                "report_date": date,
                "category": _get(r, "category", ""),
                "commodity": _get(r, "commodity", ""),
                "holdings_lbs": _safe_float(r.get("holdings_current_lbs")),
                "holdings_1st_lbs": _safe_float(r.get("holdings_1stDayMTH_lbs")),
                "change_lbs": _safe_float(r.get("holdings_change_lbs")),
                "change_pct": _safe_float(r.get("holdings_change_percent")),
                "month_1st_day": _get(r, "currentMTH_1stDay"),
            })
    return rows


def parse_chicken_wholesale(slug_id, sections):
    """Parse slugs 3646/3649 → chicken_wholesale table."""
    rows = []
    for sec in sections:
        if sec.get("reportSection") != "Report Detail":
            continue
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            item = _get(r, "item")
            if not item:
                continue
            rows.append({
                "report_date": date,
                "slug_id": slug_id,
                "item": item,
                "low_price": _safe_float(r.get("low_price")),
                "high_price": _safe_float(r.get("high_price")),
                "wtd_avg_price": _safe_float(r.get("wtd_avg_price")),
                "volume": _safe_int(r.get("volume")),
                "wtd_avg_price_prev": _safe_float(r.get("wtd_avg_price_previous")),
                "volume_prev": _safe_int(r.get("volume_previous")),
                "price_change": _safe_float(r.get("price_change")),
                "price_unit": _get(r, "price_unit"),
                "volume_unit": _get(r, "volume_traded_unit"),
            })
    return rows


def parse_retail_metrics(slug_id, sections):
    """Parse slugs 2756/2757 Report Metrics → retail_metrics table."""
    rows = []
    for sec in sections:
        if sec.get("reportSection") != "Report Metrics":
            continue
        for r in sec.get("results", []):
            date = normalize_date(
                r.get("report_Date") or r.get("report_date") or r.get("report_begin_date")
            )
            if not date:
                continue
            rows.append({
                "report_date": date,
                "slug_id": slug_id,
                "region": _get(r, "region", ""),
                "stores": _safe_int(r.get("stores")),
                "last_week_stores": _safe_int(r.get("last_Week_Stores")),
                "last_year_stores": _safe_int(r.get("last_Year_Stores")),
                "feature_rate": _safe_float(r.get("feature")),
                "last_week_feature": _safe_float(r.get("last_Week_Feature")),
                "last_year_feature": _safe_float(r.get("last_Year_Feature")),
                "activity_index": _safe_float(r.get("activity_Index")),
                "last_week_activity": _safe_float(r.get("last_Week_Activity_Index")),
                "last_year_activity": _safe_float(r.get("last_Year_Activity_Index")),
            })
    return rows


def parse_retail_prices(slug_id, sections):
    """Parse slugs 2756/2757 Report Details → retail_prices table."""
    rows = []
    for sec in sections:
        if sec.get("reportSection") != "Report Details":
            continue
        for r in sec.get("results", []):
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            typ = _get(r, "type")
            if not typ:
                continue
            rows.append({
                "report_date": date,
                "slug_id": slug_id,
                "region": _get(r, "region", ""),
                "commodity": _get(r, "commodity"),
                "section": _get(r, "section"),
                "type": typ,
                "condition": _get(r, "condition"),
                "environment": _get(r, "environment", ""),
                "package_size": _get(r, "package_size", ""),
                "quality_grade": _get(r, "quality_grade"),
                "price_avg": _safe_float(r.get("price_avg")),
                "price_min": _safe_float(r.get("price_min")),
                "price_max": _safe_float(r.get("price_max")),
                "store_count": _safe_int(r.get("store_count")),
                "price_unit": _get(r, "price_unit"),
            })
    return rows


def parse_narratives(slug_id, sections):
    """Extract report_narrative from Header sections → report_narratives table."""
    rows = []
    for sec in sections:
        if sec.get("reportSection") != "Report Header":
            continue
        for r in sec.get("results", []):
            narrative = _get(r, "report_narrative")
            if not narrative:
                continue
            date = normalize_date(r.get("report_date") or r.get("report_begin_date"))
            if not date:
                continue
            rows.append({
                "report_date": date,
                "slug_id": slug_id,
                "narrative": narrative,
            })
    return rows


# ── NASS Parser ──────────────────────────────────────────────────────────

def parse_nass_record(record):
    """Normalize a single NASS QuickStats record → dict for nass_data table.

    Handles withheld values: (D)=withheld, (Z)=less than half unit, etc.
    """
    value_raw = record.get("Value", "")
    value = None
    if value_raw and value_raw not in ("(D)", "(Z)", "(NA)", "(S)", "(H)", "(L)"):
        try:
            value = float(str(value_raw).replace(",", ""))
        except (ValueError, TypeError):
            pass

    cv_raw = record.get("CV (%)", "")
    cv_pct = None
    if cv_raw and cv_raw not in ("(D)", "(H)", "(L)", ""):
        try:
            cv_pct = float(str(cv_raw).replace(",", ""))
        except (ValueError, TypeError):
            pass

    return {
        "year": int(record.get("year", 0)),
        "reference_period": record.get("reference_period_desc", ""),
        "freq": record.get("freq_desc", ""),
        "commodity": record.get("commodity_desc", ""),
        "class": record.get("class_desc"),
        "data_item": record.get("short_desc", ""),
        "stat_category": record.get("statisticcat_desc"),
        "unit": record.get("unit_desc"),
        "value": value,
        "value_raw": value_raw,
        "agg_level": record.get("agg_level_desc", ""),
        "state_alpha": record.get("state_alpha", "") if record.get("agg_level_desc") == "STATE" else "",
        "state_name": record.get("state_name") if record.get("agg_level_desc") == "STATE" else None,
        "cv_pct": cv_pct,
        "load_time": record.get("load_time"),
    }


# ── FRED Parser ──────────────────────────────────────────────────────────

def parse_fred_record(series_id, observation, label=None):
    """Normalize a single FRED observation → dict for fred_series table.

    FRED returns {date, value} where value may be '.' for missing.
    """
    val_raw = observation.get("value", "")
    value = None
    if val_raw and val_raw != ".":
        try:
            value = float(val_raw)
        except (ValueError, TypeError):
            pass

    return {
        "observation_date": observation.get("date", ""),
        "series_id": series_id,
        "value": value,
        "series_label": label,
    }


# ── BLS Parser ───────────────────────────────────────────────────────────

def parse_bls_record(series_id, data_point, label=None):
    """Normalize a single BLS data point → dict for bls_prices table.

    BLS returns {year, period, periodName, value, footnotes}.
    Period is 'M01'..'M12' for monthly, 'M13' for annual average.
    """
    period = data_point.get("period", "")
    # Skip annual averages (M13)
    if period == "M13":
        return None

    month = None
    if period.startswith("M"):
        try:
            month = int(period[1:])
        except ValueError:
            return None

    val_raw = data_point.get("value", "")
    value = None
    if val_raw:
        try:
            value = float(str(val_raw).replace(",", ""))
        except (ValueError, TypeError):
            pass

    footnotes = data_point.get("footnotes", [])
    footnote_str = "; ".join(
        fn.get("text", "") for fn in footnotes if fn.get("text")
    ) if footnotes else None

    return {
        "year": int(data_point.get("year", 0)),
        "month": month,
        "series_id": series_id,
        "value": value,
        "series_label": label,
        "footnotes": footnote_str,
    }


# ── HPAI Parser ──────────────────────────────────────────────────────────

def parse_hpai_record(row):
    """Normalize a single HPAI CSV row → dict for hpai_detections table.

    Tableau CSV column names vary; this handles known variants.
    Actual columns from Tableau (as of Apr 2026):
      Confirmed Diagnosis, County Name, Production, Special ID, State, Birds Affected
    """
    # Try multiple possible column name patterns
    def _find(row, *candidates):
        for c in candidates:
            for key in row:
                if c.lower() in key.lower():
                    return row[key]
        return None

    detection_date = _find(row, "Confirmed Diagnosis", "Confirmed",
                           "Confirmation Date", "confirmation_date",
                           "Detection Date")
    state = _find(row, "State", "state")
    county = _find(row, "County Name", "County", "county")
    flock_type = _find(row, "Production", "Flock Type", "flock_type")
    species = _find(row, "Species", "species", "WOAH Classification")
    flock_size_raw = _find(row, "Birds Affected", "Flock Size", "flock_size")

    flock_size = _safe_int(flock_size_raw)

    # Normalize date: try common formats including Tableau datetime
    conf_date = None
    if detection_date:
        ds = detection_date.strip()
        for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%Y-%m-%d",
                    "%m/%d/%y", "%Y/%m/%d", "%d-%b-%y"):
            try:
                conf_date = datetime.strptime(ds, fmt).strftime("%Y-%m-%d")
                break
            except (ValueError, AttributeError):
                continue
        if not conf_date:
            conf_date = ds

    return {
        "detection_date": conf_date,
        "state": state.strip() if state else None,
        "county": county.strip() if county else None,
        "flock_type": flock_type.strip() if flock_type else None,
        "species": species.strip() if species else None,
        "flock_size": flock_size,
        "confirmation_date": conf_date,
    }
