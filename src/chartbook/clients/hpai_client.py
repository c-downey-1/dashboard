"""
hpai_client.py — APHIS HPAI CSV downloader.

Downloads commercial/backyard flock detection data from APHIS.
Adapted from hpai-dashboard/download_data.py but uses stdlib only.
"""

import csv
import io
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# APHIS data URLs
FLOCK_DETECTIONS_URL = (
    "https://publicdashboards.dl.usda.gov/t/MRP_PUB/views/"
    "VS_Avian_HPAIConfirmedDetections2022/HPAI2022ConfirmedDetections.csv"
)


def _download_csv(url, timeout=120):
    """Download a CSV from URL, return text content."""
    req = Request(url)
    req.add_header("User-Agent", "chartbook-pipeline/1.0")
    with urlopen(req, timeout=timeout) as r:
        raw = r.read()
    # Try UTF-8 first, fall back to UTF-16 (Tableau sometimes uses UTF-16)
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_flock_detections():
    """Download HPAI flock detections CSV from APHIS Tableau endpoint.

    Returns list of row dicts from the CSV, or empty list on failure.
    """
    print("  [HPAI] Downloading flock detections ...", end=" ", flush=True)
    try:
        text = _download_csv(FLOCK_DETECTIONS_URL)
    except (HTTPError, URLError, Exception) as e:
        print(f"WARN: {e}")
        return []

    # Validate the response looks like the expected data
    first_line = text.split("\n")[0] if text else ""
    if "Confirm" not in first_line and "State" not in first_line:
        print(f"WARN: unexpected CSV format — header: {first_line[:100]}")
        return []

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"{len(rows)} rows")
    return rows
