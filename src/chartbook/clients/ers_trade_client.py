"""
ers_trade_client.py — Fetch and parse USDA ERS monthly chicken and egg trade totals.
"""

from __future__ import annotations

import io
import re
import zipfile
from datetime import datetime
from html import unescape
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ERS_TRADE_PAGE_URL = "https://www.ers.usda.gov/data-products/livestock-and-meat-international-trade-data"
FALLBACK_WORKBOOK_URL = "https://www.ers.usda.gov/media/5614/chickens-turkeys-and-eggs-monthly-us-trade.xlsx?v=20265"

XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
PKG_REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}

SECTION_CONFIG = {
    "broiler imports (1,000 pounds)": {
        "commodity": "chicken",
        "flow": "import",
        "product": "broiler",
        "unit": "1,000 pounds",
        "section_label": "Broiler imports",
    },
    "broiler exports (1,000 pounds)": {
        "commodity": "chicken",
        "flow": "export",
        "product": "broiler",
        "unit": "1,000 pounds",
        "section_label": "Broiler exports",
    },
    "other chicken imports (1,000 pounds)": {
        "commodity": "chicken",
        "flow": "import",
        "product": "other_chicken",
        "unit": "1,000 pounds",
        "section_label": "Other chicken imports",
    },
    "other chicken exports (1,000 pounds)": {
        "commodity": "chicken",
        "flow": "export",
        "product": "other_chicken",
        "unit": "1,000 pounds",
        "section_label": "Other chicken exports",
    },
    "egg imports, including products (shell-egg equivalent, 1,000 dozen)": {
        "commodity": "egg",
        "flow": "import",
        "product": "total",
        "unit": "1,000 dozen (shell-egg equivalent)",
        "section_label": "Egg imports, including products",
    },
    "shell-egg imports (1,000 dozen)": {
        "commodity": "egg",
        "flow": "import",
        "product": "shell_egg",
        "unit": "1,000 dozen",
        "section_label": "Shell-egg imports",
    },
    "egg product imports (shell-egg equivalent, 1,000 dozen)": {
        "commodity": "egg",
        "flow": "import",
        "product": "egg_product",
        "unit": "1,000 dozen (shell-egg equivalent)",
        "section_label": "Egg product imports",
    },
    "egg exports, including products (shell-egg equivalent, 1,000 dozen)": {
        "commodity": "egg",
        "flow": "export",
        "product": "total",
        "unit": "1,000 dozen (shell-egg equivalent)",
        "section_label": "Egg exports, including products",
    },
    "shell-egg exports (1,000 dozen)": {
        "commodity": "egg",
        "flow": "export",
        "product": "shell_egg",
        "unit": "1,000 dozen",
        "section_label": "Shell-egg exports",
    },
    "egg product exports (shell-egg equivalent, 1,000 dozen)": {
        "commodity": "egg",
        "flow": "export",
        "product": "egg_product",
        "unit": "1,000 dozen (shell-egg equivalent)",
        "section_label": "Egg product exports",
    },
}

XLSX_LINK_RE = re.compile(
    r'href="([^"]*chickens-turkeys-and-eggs-monthly[^"]*\.xlsx[^"]*)"',
    re.I,
)
CELL_REF_RE = re.compile(r"([A-Z]+)")


def _request_bytes(url, accept=None):
    request = Request(
        url,
        headers={
            "User-Agent": "chartbook/1.0",
            "Accept": accept or "*/*",
        },
    )
    with urlopen(request, timeout=90) as response:
        return response.read()


def discover_workbook_url():
    """Find the current ERS workbook download URL from the official landing page."""
    html = _request_bytes(ERS_TRADE_PAGE_URL, accept="text/html").decode("utf-8", "ignore")
    match = XLSX_LINK_RE.search(html)
    if not match:
        return FALLBACK_WORKBOOK_URL
    return urljoin(ERS_TRADE_PAGE_URL, unescape(match.group(1)))


def fetch_workbook_bytes(workbook_url=None):
    """Download the current ERS chicken/turkey/egg trade workbook."""
    resolved_url = workbook_url or discover_workbook_url()
    return resolved_url, _request_bytes(resolved_url, accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def _normalize_label(value):
    return " ".join((value or "").replace("\n", " ").split()).strip().lower()


def _parse_month_label(value):
    return datetime.strptime(value.strip(), "%b-%y").strftime("%Y-%m")


def _shared_strings(workbook):
    try:
        root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    except KeyError:
        return []

    values = []
    for item in root.findall("a:si", XML_NS):
        text = "".join(node.text or "" for node in item.iterfind(".//a:t", XML_NS))
        values.append(text)
    return values


def _workbook_sheet_targets(workbook):
    rels_root = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall("p:Relationship", PKG_REL_NS)
    }

    workbook_root = ET.fromstring(workbook.read("xl/workbook.xml"))
    targets = []
    for sheet in workbook_root.findall("a:sheets/a:sheet", XML_NS):
        rid = sheet.attrib.get(f"{{{REL_NS['r']}}}id")
        if not rid:
            continue
        target = rel_targets.get(rid)
        if not target:
            continue
        targets.append(f"xl/{target.lstrip('/')}")
    return targets


def _cell_text(cell, shared_strings):
    cell_type = cell.attrib.get("t")

    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iterfind(".//a:t", XML_NS))

    value_node = cell.find("a:v", XML_NS)
    if value_node is None or value_node.text is None:
        return ""

    if cell_type == "s":
        return shared_strings[int(value_node.text)]
    return value_node.text


def _sheet_rows(workbook, sheet_path, shared_strings):
    root = ET.fromstring(workbook.read(sheet_path))
    for row in root.findall(".//a:sheetData/a:row", XML_NS):
        values = {}
        for cell in row.findall("a:c", XML_NS):
            match = CELL_REF_RE.match(cell.attrib.get("r", ""))
            if not match:
                continue
            values[match.group(1)] = _cell_text(cell, shared_strings)
        yield values


def parse_workbook_bytes(workbook_bytes, source_url):
    """Parse ERS workbook bytes into normalized monthly section totals."""
    rows = []
    with zipfile.ZipFile(io.BytesIO(workbook_bytes)) as workbook:
        shared_strings = _shared_strings(workbook)

        for sheet_path in _workbook_sheet_targets(workbook):
            header_months = {}
            current_section = None

            for row in _sheet_rows(workbook, sheet_path, shared_strings):
                row_header = _normalize_label(row.get("A"))
                if row_header.startswith("import/export, geography code and name"):
                    header_months = {
                        column: _parse_month_label(value)
                        for column, value in row.items()
                        if column not in {"A", "B", "C"} and value
                    }
                    continue

                if row_header in SECTION_CONFIG:
                    current_section = SECTION_CONFIG[row_header]
                    continue

                if not current_section:
                    continue

                if _normalize_label(row.get("C")) != "total":
                    continue

                for column, report_month in header_months.items():
                    value = row.get(column)
                    if value in (None, ""):
                        continue
                    rows.append({
                        "report_month": report_month,
                        "commodity": current_section["commodity"],
                        "flow": current_section["flow"],
                        "product": current_section["product"],
                        "section_label": current_section["section_label"],
                        "value": float(value),
                        "unit": current_section["unit"],
                        "source_url": source_url,
                    })
                current_section = None
    return rows


def fetch_trade_rows():
    """Fetch and parse the current ERS workbook."""
    workbook_url, workbook_bytes = fetch_workbook_bytes()
    return parse_workbook_bytes(workbook_bytes, workbook_url)
