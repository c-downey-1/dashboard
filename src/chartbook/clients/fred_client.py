"""
fred_client.py — FRED (Federal Reserve Economic Data) API client.

Uses stdlib only (urllib.request) to match existing client pattern.
"""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
FRED_KEY = os.environ.get("FRED_API_KEY", "")

# Courtesy delay between requests (seconds)
_REQUEST_DELAY = 0.5


def fred_get(params, retries=3):
    """HTTP GET against FRED API. Returns parsed JSON.

    Retries on transient errors with exponential backoff.
    """
    params["api_key"] = FRED_KEY
    params["file_type"] = "json"
    url = f"{FRED_BASE}?{urlencode(params)}"
    req = Request(url)
    req.add_header("Accept", "application/json")

    for attempt in range(retries):
        try:
            time.sleep(_REQUEST_DELAY)
            with urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            if e.code in (429, 500, 503) and attempt < retries - 1:
                wait = (attempt + 1) * 5
                print(f"  (FRED error {e.code}, waiting {wait}s) ", end="", flush=True)
                time.sleep(wait)
                continue
            raise
    return {}


def fetch_series(series_id, start_date=None, end_date=None):
    """Fetch all observations for a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'PMAIZMTUSDM')
        start_date: Optional start date as 'YYYY-MM-DD'
        end_date: Optional end date as 'YYYY-MM-DD'

    Returns list of observation dicts: [{date, value}, ...]
    """
    if not FRED_KEY:
        print("  WARNING: FRED_API_KEY not set, skipping FRED fetch")
        return []

    params = {"series_id": series_id}
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date

    print(f"  [FRED] {series_id} ...", end=" ", flush=True)
    try:
        result = fred_get(params)
        observations = result.get("observations", [])
        print(f"{len(observations)} observations")
        return observations
    except (HTTPError, URLError, Exception) as e:
        print(f"WARN: {e}")
        return []
