"""
bls_client.py — BLS (Bureau of Labor Statistics) Public Data API v2 client.

Uses stdlib only (urllib.request) to match existing client pattern.
BLS v2 requires POST with JSON body and registration key.
"""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BLS_BASE = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_KEY = os.environ.get("BLS_API_KEY", "")

# Delay between requests (seconds)
_REQUEST_DELAY = 1.0


def bls_post(series_ids, start_year, end_year, retries=3):
    """POST to BLS API v2. Returns parsed JSON.

    BLS v2 limits: 50 series/request, 20 years max span, 500 queries/day.
    """
    payload = {
        "seriesid": series_ids if isinstance(series_ids, list) else [series_ids],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": BLS_KEY,
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(BLS_BASE, data=data)
    req.add_header("Content-Type", "application/json")

    for attempt in range(retries):
        try:
            time.sleep(_REQUEST_DELAY)
            with urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            if e.code in (429, 500, 503) and attempt < retries - 1:
                wait = (attempt + 1) * 10
                print(f"  (BLS error {e.code}, waiting {wait}s) ", end="", flush=True)
                time.sleep(wait)
                continue
            raise
    return {}


def fetch_series(series_ids, start_year=None, end_year=None):
    """Fetch observations for one or more BLS series.

    BLS v2 allows up to 20-year spans. For longer ranges, this
    automatically chunks into 20-year windows.

    Args:
        series_ids: Single series ID string or list of up to 50 IDs
        start_year: Start year (default: 2006)
        end_year: End year (default: current year)

    Returns dict mapping series_id → list of data dicts.
    """
    if not BLS_KEY:
        print("  WARNING: BLS_API_KEY not set, skipping BLS fetch")
        return {}

    from datetime import date
    if start_year is None:
        start_year = 2006
    if end_year is None:
        end_year = date.today().year

    if isinstance(series_ids, str):
        series_ids = [series_ids]

    all_data = {sid: [] for sid in series_ids}

    # Chunk into 20-year windows (BLS limit)
    cur_start = start_year
    while cur_start <= end_year:
        cur_end = min(cur_start + 19, end_year)
        print(f"  [BLS] {len(series_ids)} series, {cur_start}-{cur_end} ...", end=" ", flush=True)

        try:
            result = bls_post(series_ids, cur_start, cur_end)
            status = result.get("status", "")
            if status != "REQUEST_SUCCEEDED":
                msg = result.get("message", ["Unknown error"])
                print(f"WARN: {status} — {msg}")
                cur_start = cur_end + 1
                continue

            for series in result.get("Results", {}).get("series", []):
                sid = series.get("seriesID", "")
                data_points = series.get("data", [])
                all_data.setdefault(sid, []).extend(data_points)
                print(f"{sid}:{len(data_points)}", end=" ")
            print()

        except (HTTPError, URLError, Exception) as e:
            print(f"WARN: {e}")

        cur_start = cur_end + 1

    return all_data
