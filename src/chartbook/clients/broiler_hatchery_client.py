"""
broiler_hatchery_client.py — ESMIS Broiler Hatchery scraper.
"""

import re
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

ESMIS_BASE = "https://esmis.nal.usda.gov"
PUBLICATION_PATH = "/publication/broiler-hatchery"
_REQUEST_DELAY = 0.2

_ROW_RE = re.compile(
    r'<tr>\s*<td[^>]*class="views-field views-field-release-date"[^>]*>'
    r'<time datetime="([^"]+)">.*?</time>\s*</td>\s*'
    r'<td[^>]*class="views-field views-field-release-files"[^>]*>(.*?)</td>',
    re.IGNORECASE | re.DOTALL,
)
_LINK_RE = re.compile(r'href="([^"]+?\.(pdf|txt|zip))"', re.IGNORECASE)
_HATCHABILITY_RE = re.compile(
    r"Average hatchability .*?\s+was\s+(\d+(?:\.\d+)?)\s+percent",
    re.IGNORECASE | re.DOTALL,
)
_WEEK_ENDING_RE = re.compile(
    r"during the week ending\s+([A-Za-z]+ \d{1,2}, \d{4})",
    re.IGNORECASE | re.DOTALL,
)


def _http_get(url, params=None, retries=3):
    """Return decoded response body for an ESMIS URL."""
    if params:
        query = urlencode(params)
        joiner = "&" if "?" in url else "?"
        url = f"{url}{joiner}{query}"

    req = Request(url)
    req.add_header("User-Agent", "chartbook-broiler-hatchability/1.0")
    req.add_header("Accept", "text/html,text/plain,*/*")

    for attempt in range(retries):
        try:
            time.sleep(_REQUEST_DELAY)
            with urlopen(req, timeout=120) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except HTTPError as exc:
            if exc.code in (403, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise
        except URLError:
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise


def _month_starts(start_date, end_date):
    """Yield YYYY-MM strings from start month through end month inclusive."""
    current = date(start_date.year, start_date.month, 1)
    limit = date(end_date.year, end_date.month, 1)
    while current <= limit:
        yield current.strftime("%Y-%m")
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def fetch_month_releases(month_str):
    """Fetch release rows for a specific YYYY-MM month filter."""
    html = _http_get(urljoin(ESMIS_BASE, PUBLICATION_PATH), params={"date": month_str})
    releases = []
    seen = set()

    for dt_raw, files_html in _ROW_RE.findall(html):
        release_date = datetime.fromisoformat(dt_raw.replace("Z", "+00:00")).date().isoformat()
        if not release_date.startswith(month_str):
            continue

        links = {}
        for href, ext in _LINK_RE.findall(files_html):
            links[ext.lower()] = urljoin(ESMIS_BASE, href)

        if "txt" not in links or release_date in seen:
            continue

        seen.add(release_date)
        releases.append({
            "release_date": release_date,
            "txt_url": links.get("txt"),
            "pdf_url": links.get("pdf"),
            "zip_url": links.get("zip"),
        })

    releases.sort(key=lambda row: row["release_date"])
    return releases


def fetch_releases_after(last_release_date, through_date=None):
    """Fetch all release metadata after the given YYYY-MM-DD release date."""
    start = date.fromisoformat(last_release_date)
    end = through_date or date.today()
    releases = []

    for month_str in _month_starts(start, end):
        for release in fetch_month_releases(month_str):
            if release["release_date"] > last_release_date:
                releases.append(release)

    releases.sort(key=lambda row: row["release_date"])
    return releases


def fetch_report_text(txt_url):
    """Fetch raw report text for a release."""
    return _http_get(txt_url)


def parse_report_text(text):
    """Extract hatchability percent and week-ending date from report text."""
    hatchability_match = _HATCHABILITY_RE.search(text)
    if not hatchability_match:
        raise ValueError("Could not find hatchability sentence in report text")

    week_match = _WEEK_ENDING_RE.search(text)
    week_ending_date = None
    if week_match:
        week_ending_date = datetime.strptime(week_match.group(1), "%B %d, %Y").date().isoformat()

    return {
        "hatchability_pct": float(hatchability_match.group(1)),
        "week_ending_date": week_ending_date,
    }
