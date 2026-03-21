"""
cage_free_report_client.py — Fetch and parse the USDA AMS monthly cage-free report PDF.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen


CURRENT_REPORT_URL = "https://www.ams.usda.gov/mnreports/pymcagefree.pdf"

MONTH_NUMBERS = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12,
}

CATEGORY_TITLES = {
    "organic": "Certified Organic Cage-Free Layers",
    "non_organic_cage_free": "Non-Organic Cage-Free Layers",
    "all_cage_free": "All Cage-Free Layers",
}


def fetch_current_report_pdf():
    """Download the latest AMS monthly cage-free report PDF."""
    request = Request(
        CURRENT_REPORT_URL,
        headers={
            "User-Agent": "chartbook/1.0",
            "Accept": "application/pdf",
        },
    )
    with urlopen(request, timeout=90) as response:
        return response.read()


def pdf_bytes_to_text(pdf_bytes):
    """Convert PDF bytes to text via pdftotext."""
    pdftotext_bin = shutil.which("pdftotext")
    if not pdftotext_bin:
        raise RuntimeError("pdftotext is required to parse the AMS cage-free PDF")

    with tempfile.TemporaryDirectory(prefix="chartbook-cagefree-") as tmpdir:
        pdf_path = Path(tmpdir) / "pymcagefree.pdf"
        pdf_path.write_bytes(pdf_bytes)
        result = subprocess.run(
            [pdftotext_bin, "-layout", "-nopgbrk", str(pdf_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    return result.stdout


def _parse_report_date(text):
    match = re.search(
        r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+"
        r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\b",
        text,
    )
    if not match:
        raise ValueError("Could not locate AMS cage-free report date in PDF text")
    return datetime.strptime(match.group(0), "%A, %B %d, %Y").date()


def _parse_report_month(text, report_date):
    match = re.search(r"For the Month of\s+([A-Za-z]+)\b", text)
    if not match:
        raise ValueError("Could not locate AMS cage-free report month in PDF text")

    month_name = match.group(1).upper()
    month = MONTH_NUMBERS.get(month_name)
    if month is None:
        raise ValueError(f"Unsupported report month label: {match.group(1)}")

    year = report_date.year
    if month > report_date.month:
        year -= 1
    return f"{year}-{month:02d}"


def _parse_category_block(text, title):
    pattern = re.compile(
        rf"{re.escape(title)}\s+"
        r"Est\.\s+Layer\s+Flock\s+Size:\s*([\d,]+)\s+"
        r"Est\.\s+Lay\s+Rate:\s*([\d.]+)%\s+"
        r"Weekly\s+Egg\s+Production:\s*([\d,]+)",
        re.S,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Could not parse AMS cage-free section: {title}")
    return {
        "layer_flock_size": int(match.group(1).replace(",", "")),
        "lay_rate_pct": float(match.group(2)),
        "weekly_production_cases": int(match.group(3).replace(",", "")),
    }


def _parse_side_by_side_blocks(text):
    pattern = re.compile(
        r"Certified\s+Organic\s+Cage-Free\s+Layers\s+"
        r"Non-Organic\s+Cage-Free\s+Layers\s+"
        r"Est\.\s+Layer\s+Flock\s+Size:\s*([\d,]+)\s+"
        r"Est\.\s+Layer\s+Flock\s+Size:\s*([\d,]+)\s+"
        r"Est\.\s+Lay\s+Rate:\s*([\d.]+)%\s+"
        r"Est\.\s+Lay\s+Rate:\s*([\d.]+)%\s+"
        r"Weekly\s+Egg\s+Production:\s*([\d,]+)\s+30-dozen\s+cases\s+"
        r"Weekly\s+Egg\s+Production:\s*([\d,]+)\s+30-dozen\s+cases",
        re.S,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError("Could not parse AMS cage-free side-by-side production block")

    return {
        "organic": {
            "layer_flock_size": int(match.group(1).replace(",", "")),
            "lay_rate_pct": float(match.group(3)),
            "weekly_production_cases": int(match.group(5).replace(",", "")),
        },
        "non_organic_cage_free": {
            "layer_flock_size": int(match.group(2).replace(",", "")),
            "lay_rate_pct": float(match.group(4)),
            "weekly_production_cases": int(match.group(6).replace(",", "")),
        },
    }


def parse_report_text(text, source_url=CURRENT_REPORT_URL):
    """Parse the AMS cage-free PDF text into normalized monthly rows."""
    report_date = _parse_report_date(text)
    report_month = _parse_report_month(text, report_date)
    side_by_side = _parse_side_by_side_blocks(text)

    rows = []
    for category, title in CATEGORY_TITLES.items():
        parsed = side_by_side.get(category) if category in side_by_side else _parse_category_block(text, title)
        rows.append({
            "report_month": report_month,
            "report_date": report_date.isoformat(),
            "category": category,
            "layer_flock_size": parsed["layer_flock_size"],
            "lay_rate_pct": parsed["lay_rate_pct"],
            "weekly_production_cases": parsed["weekly_production_cases"],
            "source_url": source_url,
            "source_type": "ams_pdf_current",
        })
    return rows


def fetch_current_report_rows():
    """Fetch, convert, and parse the latest AMS cage-free report."""
    pdf_bytes = fetch_current_report_pdf()
    text = pdf_bytes_to_text(pdf_bytes)
    return parse_report_text(text)
