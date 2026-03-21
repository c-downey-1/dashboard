"""
google_sheets_client.py — Minimal public Google Sheets CSV helpers.
"""

from __future__ import annotations

import csv
import io
import re
import subprocess
from datetime import datetime


SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")
DATE_FORMATS = ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M")


def extract_sheet_id(sheet_url_or_id):
    """Return a Google Sheets spreadsheet id from either a URL or raw id."""
    if "/" not in sheet_url_or_id:
        return sheet_url_or_id
    match = SHEET_ID_RE.search(sheet_url_or_id)
    if not match:
        raise ValueError(f"Could not parse Google Sheets id from: {sheet_url_or_id}")
    return match.group(1)


def public_csv_url(sheet_url_or_id, gid=0):
    """Return the unauthenticated CSV export URL for a public sheet tab."""
    sheet_id = extract_sheet_id(sheet_url_or_id)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def fetch_public_csv_rows(sheet_url_or_id, gid=0):
    """Fetch a public Google Sheet tab as CSV rows."""
    url = public_csv_url(sheet_url_or_id, gid=gid)
    result = subprocess.run(
        ["curl", "-L", "--max-time", "30", url],
        check=True,
        capture_output=True,
        text=True,
    )
    reader = csv.reader(io.StringIO(result.stdout.lstrip("\ufeff")))
    return url, list(reader)


def _parse_sheet_datetime(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _parse_float(value):
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    return float(value)


def parse_layer_feed_rows(csv_rows, source_url):
    """Parse the public feed spreadsheet into normalized daily ration rows."""
    corn_by_date = {}
    soy_by_date = {}

    for row in csv_rows:
        if not row:
            continue
        padded = row + [""] * max(0, 7 - len(row))

        corn_date = _parse_sheet_datetime(padded[0]) if padded[0].strip() else None
        soy_date = _parse_sheet_datetime(padded[5]) if padded[5].strip() else None

        if corn_date:
            corn_cents_per_bushel = _parse_float(padded[1])
            corn_per_ton = _parse_float(padded[3])
            if corn_per_ton is None and corn_cents_per_bushel is not None:
                corn_per_ton = (corn_cents_per_bushel / 100.0) * (2000.0 / 56.0)
            if corn_per_ton is not None:
                corn_by_date[corn_date.date().isoformat()] = corn_per_ton

        if soy_date:
            soy_close = _parse_float(padded[6])
            if soy_close is not None:
                soy_by_date[soy_date.date().isoformat()] = soy_close

    common_dates = sorted(set(corn_by_date) & set(soy_by_date))
    if not common_dates:
        return []

    calcium_per_ton = 5.1
    other_per_ton = 16.35
    weights = {
        "corn": 0.67,
        "soymeal": 0.22,
        "calcium": 0.08,
        "other": 0.03,
    }

    ration_by_date = {}
    for trade_date in common_dates:
        ration_by_date[trade_date] = (
            corn_by_date[trade_date] * weights["corn"]
            + soy_by_date[trade_date] * weights["soymeal"]
            + calcium_per_ton * weights["calcium"]
            + other_per_ton * weights["other"]
        )

    base_date = "2024-01-02" if "2024-01-02" in ration_by_date else common_dates[0]
    base_ration = ration_by_date[base_date]

    rows = []
    for trade_date in common_dates:
        rows.append({
            "trade_date": trade_date,
            "corn_per_ton": corn_by_date[trade_date],
            "soymeal_per_ton": soy_by_date[trade_date],
            "calcium_per_ton": calcium_per_ton,
            "other_per_ton": other_per_ton,
            "ration_cost": ration_by_date[trade_date],
            "layer_feed_index": (ration_by_date[trade_date] / base_ration * 100.0) if base_ration else None,
            "source_type": "public_google_sheet",
            "source_note": source_url,
        })
    return rows
