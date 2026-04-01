"""
hpai_client.py — APHIS HPAI CSV downloader.

Downloads commercial/backyard flock detection data from APHIS.
Prefers a local manual CSV ("A Table by Confirmation Date.csv") for exact
flock counts; falls back to the Tableau direct endpoint if not found.
Adapted from hpai-dashboard/download_data.py but uses stdlib only.
"""

import csv
import io
import os
from pathlib import Path
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


LOCAL_CSV_NAME = "A Table by Confirmation Date.csv"


def load_local_csv(repo_root):
    """Load the manual Tableau crosstab CSV if it exists at repo root.

    Returns list of row dicts, or empty list if not found/parseable.
    The manual file is UTF-16 tab-delimited (crosstab format) with exact flock counts.
    """
    path = Path(repo_root) / LOCAL_CSV_NAME
    if not path.exists():
        return []

    print(f"  [HPAI] Loading local manual CSV: {path.name} ...", end=" ", flush=True)
    try:
        raw = path.read_bytes()
    except Exception as e:
        print(f"WARN: {e}")
        return []

    # Detect encoding: UTF-16 BOM → crosstab, else flat
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
        lines = text.strip().replace("\r\n", "\n").replace("\r", "\n").split("\n")
        # Find header row
        hdr_idx = None
        for i, line in enumerate(lines):
            low = line.lower()
            if "confirmed" in low and "production" in low:
                hdr_idx = i
                break
        if hdr_idx is None:
            print("WARN: no header row found")
            return []
        hdrs = [h.strip() for h in lines[hdr_idx].split("\t")]
        hdr_low = [h.lower() for h in hdrs]
        # Find metadata column indices
        def _fc(*candidates):
            for c in candidates:
                for i, h in enumerate(hdr_low):
                    if c in h:
                        return i
            return None
        ci = _fc("confirmed diagnosis", "confirmed")
        si = _fc("state")
        cni = _fc("county name")
        pi = _fc("production")
        if ci is None or pi is None:
            print("WARN: missing required columns")
            return []
        data_start = pi + 1
        # Flatten crosstab: extract flock count from first non-empty data column
        rows = []
        prev_conf = prev_st = prev_cn = None
        for line in lines[hdr_idx + 1:]:
            cols = line.split("\t")
            if len(cols) <= data_start:
                continue
            confirmed = cols[ci].strip()
            state = cols[si].strip() if si is not None else ""
            county = cols[cni].strip() if cni is not None else ""
            production = cols[pi].strip()
            if confirmed:
                prev_conf = confirmed
            else:
                confirmed = prev_conf or ""
            if state:
                prev_st = state
            else:
                state = prev_st or ""
            if county:
                prev_cn = county
            else:
                county = prev_cn or ""
            if not confirmed or not production:
                continue
            flock = None
            for cell in cols[data_start:]:
                v = cell.strip().replace(",", "")
                if v:
                    try:
                        flock = str(int(float(v)))
                        break
                    except ValueError:
                        continue
            rows.append({
                "Confirmed Diagnosis": confirmed,
                "State": state,
                "County Name": county,
                "Production": production,
                "Birds Affected": flock or "0",
            })
        print(f"{len(rows)} rows (crosstab, exact counts)")
        return rows
    else:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        print(f"{len(rows)} rows (flat)")
        return rows


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
