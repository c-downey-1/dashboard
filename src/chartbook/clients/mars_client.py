"""
mars_client.py — MARS API client with Basic Auth and 180-day chunking.
"""

import base64
import json
import os
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MARS_BASE = "https://marsapi.ams.usda.gov/services/v1.2/reports"
MARS_KEY = os.environ.get("MARS_API_KEY", "")


def mars_get(url):
    """HTTP GET with Basic Auth. Returns parsed JSON."""
    req = Request(url)
    req.add_header(
        "Authorization",
        "Basic " + base64.b64encode(f"{MARS_KEY}:".encode()).decode(),
    )
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def fetch_report(slug_id, start, end):
    """Fetch all sections for a MARS report, chunked in 180-day windows.

    Returns a list of section dicts: [{reportSection, stats, results}, ...]
    accumulated across all chunks.
    """
    if not MARS_KEY:
        print("  WARNING: MARS_API_KEY not set, skipping MARS fetch")
        return []

    all_sections = []
    cur = start

    while cur <= end:
        # MARS date filters are inclusive, so cap windows at 180 calendar days.
        chunk_end = min(cur + timedelta(days=179), end)
        sd = cur.strftime("%m/%d/%Y")
        ed = chunk_end.strftime("%m/%d/%Y")
        url = f"{MARS_BASE}/{slug_id}?q=report_begin_date={sd}:{ed}&allSections=true"

        print(f"  [{slug_id}] {cur} → {chunk_end} ...", end=" ", flush=True)
        try:
            data = mars_get(url)
        except (HTTPError, URLError, Exception) as e:
            print(f"WARN: {e}")
            cur = chunk_end + timedelta(days=1)
            continue

        # Response is a list of section dicts when allSections=true
        sections = data if isinstance(data, list) else [data]
        rows = sum(s.get("stats", {}).get("totalRows", 0) for s in sections)
        print(f"{rows} rows")

        all_sections.extend(sections)
        cur = chunk_end + timedelta(days=1)

    return all_sections
