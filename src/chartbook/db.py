"""
db.py — SQLite helpers: init, upsert, ETL logging, and CSV export.
"""

import csv
import sqlite3
from pathlib import Path

from .paths import DEFAULT_DB_PATH
from .schema import create_all

DEFAULT_DB = DEFAULT_DB_PATH


def init_db(db_path=None):
    """Open (or create) the SQLite database and ensure all tables exist."""
    path = db_path or DEFAULT_DB
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    create_all(conn)
    return conn


def upsert_rows(conn, table, rows):
    """INSERT OR REPLACE a batch of row dicts into the given table.

    Column names are taken from the first row's keys.
    """
    if not rows:
        return 0
    cols = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in cols)
    col_names = ", ".join(cols)
    sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"
    cur = conn.cursor()
    cur.executemany(sql, [tuple(r.get(c) for c in cols) for r in rows])
    conn.commit()
    return len(rows)


def insert_or_ignore_rows(conn, table, rows):
    """INSERT OR IGNORE a batch of row dicts and return inserted row count."""
    if not rows:
        return 0
    cols = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in cols)
    col_names = ", ".join(cols)
    sql = f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})"
    before = conn.total_changes
    cur = conn.cursor()
    cur.executemany(sql, [tuple(r.get(c) for c in cols) for r in rows])
    conn.commit()
    return conn.total_changes - before


def log_fetch(conn, source, fetch_start, fetch_end, rows_fetched,
              slug_id=None, data_item=None, status="ok"):
    """Write a row to etl_log."""
    conn.execute(
        """INSERT INTO etl_log (source, slug_id, data_item,
           fetch_start, fetch_end, rows_fetched, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (source, slug_id, data_item,
         str(fetch_start), str(fetch_end), rows_fetched, status),
    )
    conn.commit()


def get_last_fetched(conn, source, slug_id=None, data_item=None):
    """Return the latest fetch_end for a source/slug/data_item, or None."""
    if slug_id is not None:
        row = conn.execute(
            "SELECT MAX(fetch_end) FROM etl_log WHERE source=? AND slug_id=? AND status='ok'",
            (source, slug_id),
        ).fetchone()
    elif data_item is not None:
        row = conn.execute(
            "SELECT MAX(fetch_end) FROM etl_log WHERE source=? AND data_item=? AND status='ok'",
            (source, data_item),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT MAX(fetch_end) FROM etl_log WHERE source=? AND status='ok'",
            (source,),
        ).fetchone()
    return row[0] if row and row[0] else None


def export_csv(conn, query, output_path):
    """Execute a SQL query and write results to a CSV file."""
    cur = conn.execute(query)
    cols = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)

    return len(rows)


def get_status(conn):
    """Return a summary of ingested data: source, slug/item, row counts, date ranges."""
    results = []

    # MARS tables
    mars_tables = [
        ("egg_prices", "slug_id", "report_date"),
        ("egg_volumes", None, "report_date"),
        ("egg_inventory", None, "report_date"),
        ("eggs_processed", None, "report_date"),
        ("cold_storage", None, "report_date"),
        ("chicken_wholesale", "slug_id", "report_date"),
        ("retail_metrics", "slug_id", "report_date"),
        ("retail_prices", "slug_id", "report_date"),
        ("report_narratives", "slug_id", "report_date"),
    ]
    for table, group_col, date_col in mars_tables:
        try:
            if group_col:
                rows = conn.execute(
                    f"SELECT {group_col}, COUNT(*), MIN({date_col}), MAX({date_col}) "
                    f"FROM {table} GROUP BY {group_col}"
                ).fetchall()
                for r in rows:
                    results.append({
                        "table": table, "group": r[0],
                        "rows": r[1], "min_date": r[2], "max_date": r[3],
                    })
            else:
                row = conn.execute(
                    f"SELECT COUNT(*), MIN({date_col}), MAX({date_col}) FROM {table}"
                ).fetchone()
                if row[0] > 0:
                    results.append({
                        "table": table, "group": None,
                        "rows": row[0], "min_date": row[1], "max_date": row[2],
                    })
        except sqlite3.OperationalError:
            pass

    # NASS
    try:
        rows = conn.execute(
            "SELECT data_item, COUNT(*), MIN(year), MAX(year) "
            "FROM nass_data GROUP BY data_item ORDER BY data_item"
        ).fetchall()
        for r in rows:
            results.append({
                "table": "nass_data", "group": r[0],
                "rows": r[1], "min_date": str(r[2]), "max_date": str(r[3]),
            })
    except sqlite3.OperationalError:
        pass

    # FRED
    try:
        rows = conn.execute(
            "SELECT series_id, COUNT(*), MIN(observation_date), MAX(observation_date) "
            "FROM fred_series GROUP BY series_id ORDER BY series_id"
        ).fetchall()
        for r in rows:
            results.append({
                "table": "fred_series", "group": r[0],
                "rows": r[1], "min_date": r[2], "max_date": r[3],
            })
    except sqlite3.OperationalError:
        pass

    # BLS
    try:
        rows = conn.execute(
            "SELECT series_id, COUNT(*), "
            "MIN(year || '-' || printf('%02d', month)), "
            "MAX(year || '-' || printf('%02d', month)) "
            "FROM bls_prices GROUP BY series_id ORDER BY series_id"
        ).fetchall()
        for r in rows:
            results.append({
                "table": "bls_prices", "group": r[0],
                "rows": r[1], "min_date": r[2], "max_date": r[3],
            })
    except sqlite3.OperationalError:
        pass

    # HPAI
    try:
        rows = conn.execute(
            "SELECT flock_type, COUNT(*), MIN(confirmation_date), MAX(confirmation_date) "
            "FROM hpai_detections GROUP BY flock_type ORDER BY flock_type"
        ).fetchall()
        for r in rows:
            results.append({
                "table": "hpai_detections", "group": r[0],
                "rows": r[1], "min_date": r[2], "max_date": r[3],
            })
    except sqlite3.OperationalError:
        pass

    # Broiler hatchability
    try:
        row = conn.execute(
            "SELECT COUNT(*), MIN(release_date), MAX(release_date) FROM broiler_hatchability"
        ).fetchone()
        if row[0] > 0:
            results.append({
                "table": "broiler_hatchability", "group": None,
                "rows": row[0], "min_date": row[1], "max_date": row[2],
            })
    except sqlite3.OperationalError:
        pass

    return results
