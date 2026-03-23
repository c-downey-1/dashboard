"""
schema.py — SQLite schema definitions for the chartbook data warehouse.
"""

TABLES = {
    "etl_log": """
        CREATE TABLE IF NOT EXISTS etl_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            source        TEXT NOT NULL,
            slug_id       INTEGER,
            data_item     TEXT,
            fetch_start   TEXT NOT NULL,
            fetch_end     TEXT NOT NULL,
            rows_fetched  INTEGER DEFAULT 0,
            fetched_at    TEXT DEFAULT (datetime('now')),
            status        TEXT DEFAULT 'ok'
        )
    """,

    "egg_prices": """
        CREATE TABLE IF NOT EXISTS egg_prices (
            report_date    TEXT NOT NULL,
            slug_id        INTEGER NOT NULL,
            section        TEXT NOT NULL DEFAULT '',
            environment    TEXT NOT NULL DEFAULT '',
            class          TEXT NOT NULL DEFAULT '',
            color          TEXT NOT NULL DEFAULT '',
            egg_type       TEXT NOT NULL DEFAULT '',
            origin         TEXT NOT NULL DEFAULT '',
            region         TEXT NOT NULL DEFAULT '',
            destination    TEXT NOT NULL DEFAULT '',
            freight        TEXT NOT NULL DEFAULT '',
            grade          TEXT NOT NULL DEFAULT '',
            purchase_type  TEXT NOT NULL DEFAULT '',
            delivery       TEXT NOT NULL DEFAULT '',
            price_low      REAL,
            price_high     REAL,
            avg_price      REAL,
            wtd_avg_price  REAL,
            volume         INTEGER,
            avg_price_prev     REAL,
            wtd_avg_price_prev REAL,
            wtd_avg_price_ly   REAL,
            price_unit     TEXT,
            volume_unit    TEXT,
            PRIMARY KEY (report_date, slug_id, section,
                         environment, class, color, egg_type,
                         origin, region, destination, freight,
                         grade, delivery)
        )
    """,

    "egg_volumes": """
        CREATE TABLE IF NOT EXISTS egg_volumes (
            report_date    TEXT NOT NULL,
            origin         TEXT NOT NULL DEFAULT '',
            destination    TEXT NOT NULL DEFAULT '',
            purchase_type  TEXT,
            volume_shell   INTEGER,
            volume_unit    TEXT,
            PRIMARY KEY (report_date, origin, destination)
        )
    """,

    "egg_inventory": """
        CREATE TABLE IF NOT EXISTS egg_inventory (
            report_date    TEXT NOT NULL,
            region         TEXT NOT NULL,
            class          TEXT NOT NULL,
            type           TEXT NOT NULL DEFAULT '',
            volume         REAL,
            pct_chg        TEXT,
            PRIMARY KEY (report_date, region, class, type)
        )
    """,

    "eggs_processed": """
        CREATE TABLE IF NOT EXISTS eggs_processed (
            report_date    TEXT NOT NULL,
            class          TEXT NOT NULL,
            period         TEXT NOT NULL,
            volume         REAL,
            PRIMARY KEY (report_date, class, period)
        )
    """,

    "cold_storage": """
        CREATE TABLE IF NOT EXISTS cold_storage (
            report_date       TEXT NOT NULL,
            category          TEXT NOT NULL,
            commodity         TEXT NOT NULL,
            holdings_lbs      REAL,
            holdings_1st_lbs  REAL,
            change_lbs        REAL,
            change_pct        REAL,
            month_1st_day     TEXT,
            PRIMARY KEY (report_date, category, commodity)
        )
    """,

    "chicken_wholesale": """
        CREATE TABLE IF NOT EXISTS chicken_wholesale (
            report_date     TEXT NOT NULL,
            slug_id         INTEGER NOT NULL,
            item            TEXT NOT NULL,
            low_price       REAL,
            high_price      REAL,
            wtd_avg_price   REAL,
            volume          INTEGER,
            wtd_avg_price_prev REAL,
            volume_prev     INTEGER,
            price_change    REAL,
            price_unit      TEXT,
            volume_unit     TEXT,
            PRIMARY KEY (report_date, slug_id, item)
        )
    """,

    "retail_metrics": """
        CREATE TABLE IF NOT EXISTS retail_metrics (
            report_date        TEXT NOT NULL,
            slug_id            INTEGER NOT NULL,
            region             TEXT NOT NULL,
            stores             INTEGER,
            last_week_stores   INTEGER,
            last_year_stores   INTEGER,
            feature_rate       REAL,
            last_week_feature  REAL,
            last_year_feature  REAL,
            activity_index     REAL,
            last_week_activity REAL,
            last_year_activity REAL,
            PRIMARY KEY (report_date, slug_id, region)
        )
    """,

    "retail_prices": """
        CREATE TABLE IF NOT EXISTS retail_prices (
            report_date    TEXT NOT NULL,
            slug_id        INTEGER NOT NULL,
            region         TEXT NOT NULL,
            commodity      TEXT,
            section        TEXT,
            type           TEXT NOT NULL,
            condition      TEXT,
            environment    TEXT NOT NULL DEFAULT '',
            package_size   TEXT NOT NULL DEFAULT '',
            quality_grade  TEXT,
            price_avg      REAL,
            price_min      REAL,
            price_max      REAL,
            store_count    INTEGER,
            price_unit     TEXT,
            PRIMARY KEY (report_date, slug_id, region, type,
                         environment, package_size)
        )
    """,

    "report_narratives": """
        CREATE TABLE IF NOT EXISTS report_narratives (
            report_date    TEXT NOT NULL,
            slug_id        INTEGER NOT NULL,
            narrative      TEXT,
            PRIMARY KEY (report_date, slug_id)
        )
    """,

    "nass_data": """
        CREATE TABLE IF NOT EXISTS nass_data (
            year               INTEGER NOT NULL,
            reference_period   TEXT NOT NULL,
            freq               TEXT NOT NULL,
            commodity          TEXT NOT NULL,
            class              TEXT,
            data_item          TEXT NOT NULL,
            stat_category      TEXT,
            unit               TEXT,
            value              REAL,
            value_raw          TEXT,
            agg_level          TEXT NOT NULL,
            state_alpha        TEXT NOT NULL DEFAULT '',
            state_name         TEXT,
            cv_pct             REAL,
            load_time          TEXT,
            PRIMARY KEY (year, reference_period, data_item,
                         agg_level, state_alpha)
        )
    """,

    "fred_series": """
        CREATE TABLE IF NOT EXISTS fred_series (
            observation_date   TEXT NOT NULL,
            series_id          TEXT NOT NULL,
            value              REAL,
            series_label       TEXT,
            source             TEXT DEFAULT 'FRED',
            fetched_at         TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (observation_date, series_id)
        )
    """,

    "bls_prices": """
        CREATE TABLE IF NOT EXISTS bls_prices (
            year               INTEGER NOT NULL,
            month              INTEGER NOT NULL,
            series_id          TEXT NOT NULL,
            value              REAL,
            series_label       TEXT,
            footnotes          TEXT,
            source             TEXT DEFAULT 'BLS',
            fetched_at         TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (year, month, series_id)
        )
    """,

    "hpai_detections": """
        CREATE TABLE IF NOT EXISTS hpai_detections (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_date     TEXT,
            state              TEXT,
            county             TEXT,
            flock_type         TEXT,
            species            TEXT,
            flock_size         INTEGER,
            confirmation_date  TEXT,
            source_file        TEXT,
            fetched_at         TEXT DEFAULT (datetime('now'))
        )
    """,

    "broiler_hatchability": """
        CREATE TABLE IF NOT EXISTS broiler_hatchability (
            release_date       TEXT PRIMARY KEY,
            week_ending_date   TEXT,
            hatchability_pct   REAL NOT NULL,
            source             TEXT NOT NULL DEFAULT 'esmis',
            txt_url            TEXT,
            pdf_url            TEXT,
            fetched_at         TEXT DEFAULT (datetime('now'))
        )
    """,

    "cage_free_flock_composition": """
        CREATE TABLE IF NOT EXISTS cage_free_flock_composition (
            report_month            TEXT NOT NULL,
            report_date             TEXT NOT NULL,
            category                TEXT NOT NULL,
            layer_flock_size        INTEGER,
            lay_rate_pct            REAL,
            weekly_production_cases INTEGER,
            source_url              TEXT,
            source_type             TEXT NOT NULL DEFAULT 'ams_pdf_current',
            fetched_at              TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (report_month, category)
        )
    """,

    "ers_trade_totals": """
        CREATE TABLE IF NOT EXISTS ers_trade_totals (
            report_month        TEXT NOT NULL,
            commodity           TEXT NOT NULL,
            flow                TEXT NOT NULL,
            product             TEXT NOT NULL,
            section_label       TEXT NOT NULL,
            value               REAL,
            unit                TEXT NOT NULL,
            source_url          TEXT,
            fetched_at          TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (report_month, commodity, flow, product)
        )
    """,

    "cme_feed_daily": """
        CREATE TABLE IF NOT EXISTS cme_feed_daily (
            trade_date          TEXT PRIMARY KEY,
            corn_per_ton        REAL,
            soymeal_per_ton     REAL,
            calcium_per_ton     REAL,
            other_per_ton       REAL,
            ration_cost         REAL,
            layer_feed_index    REAL,
            source_type         TEXT NOT NULL DEFAULT 'seed',
            source_note         TEXT,
            fetched_at          TEXT DEFAULT (datetime('now'))
        )
    """,

    "source_freshness": """
        CREATE TABLE IF NOT EXISTS source_freshness (
            source_name        TEXT PRIMARY KEY,
            expected_cadence   TEXT,
            last_success       TEXT,
            last_attempt       TEXT,
            last_status        TEXT,
            rows_last_fetch    INTEGER,
            alert_threshold_hours INTEGER
        )
    """,

    "narrative_sentiment": """
        CREATE TABLE IF NOT EXISTS narrative_sentiment (
            report_date              TEXT NOT NULL,
            slug_id                  INTEGER NOT NULL,
            price_direction          REAL,
            undertone                REAL,
            retail_demand            REAL,
            loose_demand             REAL,
            food_service_demand      REAL,
            offerings                REAL,
            supplies                 REAL,
            market_activity          REAL,
            price_confidence         REAL,
            secondary_demand_score   REAL,
            secondary_coverage       REAL,
            national_core_index      REAL,
            national_extended_index  REAL,
            fundamentals_core_index     REAL,
            fundamentals_extended_index REAL,
            scored_at                TEXT DEFAULT (datetime('now')),
            model_version            TEXT,
            PRIMARY KEY (report_date, slug_id)
        )
    """,
}

VIEWS = {
    "v_layers": """
        CREATE VIEW IF NOT EXISTS v_layers AS
        SELECT year, reference_period, class, value, agg_level, state_alpha
        FROM nass_data
        WHERE commodity = 'CHICKENS' AND stat_category = 'INVENTORY'
          AND data_item LIKE '%LAYERS%'
    """,

    "v_egg_production": """
        CREATE VIEW IF NOT EXISTS v_egg_production AS
        SELECT year, reference_period, class, value, unit, agg_level, state_alpha
        FROM nass_data
        WHERE commodity = 'EGGS' AND stat_category = 'PRODUCTION'
    """,

    "v_rate_of_lay": """
        CREATE VIEW IF NOT EXISTS v_rate_of_lay AS
        SELECT year, reference_period, class, value, agg_level
        FROM nass_data
        WHERE stat_category = 'RATE OF LAY'
    """,

    "v_hatchery": """
        CREATE VIEW IF NOT EXISTS v_hatchery AS
        SELECT year, reference_period, data_item, value, unit
        FROM nass_data
        WHERE data_item LIKE '%HATCHED%' OR data_item LIKE '%EGGS SET%'
           OR data_item LIKE '%INCUBATOR%' OR data_item LIKE '%PLACEMENTS%'
    """,

    "v_nass_prices": """
        CREATE VIEW IF NOT EXISTS v_nass_prices AS
        SELECT year, reference_period, data_item, value, unit
        FROM nass_data
        WHERE stat_category = 'PRICE RECEIVED'
    """,

    "v_cold_storage_nass": """
        CREATE VIEW IF NOT EXISTS v_cold_storage_nass AS
        SELECT year, reference_period, data_item, value, unit
        FROM nass_data
        WHERE data_item LIKE '%COLD STORAGE%'
    """,

    "v_hpai_monthly": """
        CREATE VIEW IF NOT EXISTS v_hpai_monthly AS
        SELECT strftime('%Y-%m', confirmation_date) AS month,
               flock_type,
               COUNT(*) AS detections,
               SUM(CASE WHEN flock_type = 'Commercial' THEN flock_size ELSE 0 END) AS commercial_birds
        FROM hpai_detections
        WHERE confirmation_date IS NOT NULL
        GROUP BY month, flock_type
    """,

    "v_feed_costs": """
        CREATE VIEW IF NOT EXISTS v_feed_costs AS
        SELECT observation_date,
               MAX(CASE WHEN series_id = 'PMAIZMTUSDM' THEN value END) AS corn_price,
               MAX(CASE WHEN series_id = 'PSMEAUSDM' THEN value END) AS sbm_price
        FROM fred_series
        WHERE series_id IN ('PMAIZMTUSDM', 'PSMEAUSDM')
        GROUP BY observation_date
    """,

    "v_cross_protein_cpi": """
        CREATE VIEW IF NOT EXISTS v_cross_protein_cpi AS
        SELECT year, month,
               MAX(CASE WHEN series_id = 'APU0000708111' THEN value END) AS egg_price,
               MAX(CASE WHEN series_id = 'APU0000706111' THEN value END) AS chicken_whole_price,
               MAX(CASE WHEN series_id = 'APU0000FF1101' THEN value END) AS chicken_breast_price,
               MAX(CASE WHEN series_id = 'APU0000706211' THEN value END) AS chicken_breast_bonein_price
        FROM bls_prices
        GROUP BY year, month
    """,
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_egg_prices_date ON egg_prices(report_date)",
    "CREATE INDEX IF NOT EXISTS idx_egg_prices_slug ON egg_prices(slug_id)",
    "CREATE INDEX IF NOT EXISTS idx_egg_inventory_date ON egg_inventory(report_date)",
    "CREATE INDEX IF NOT EXISTS idx_chicken_wholesale_date ON chicken_wholesale(report_date)",
    "CREATE INDEX IF NOT EXISTS idx_retail_prices_date ON retail_prices(report_date)",
    "CREATE INDEX IF NOT EXISTS idx_retail_prices_type ON retail_prices(type)",
    "CREATE INDEX IF NOT EXISTS idx_nass_commodity ON nass_data(commodity)",
    "CREATE INDEX IF NOT EXISTS idx_nass_item ON nass_data(data_item)",
    "CREATE INDEX IF NOT EXISTS idx_nass_year ON nass_data(year)",
    "CREATE INDEX IF NOT EXISTS idx_etl_log_source ON etl_log(source, slug_id)",
    # New table indexes
    "CREATE INDEX IF NOT EXISTS idx_fred_series_id ON fred_series(series_id)",
    "CREATE INDEX IF NOT EXISTS idx_fred_date ON fred_series(observation_date)",
    "CREATE INDEX IF NOT EXISTS idx_bls_series_id ON bls_prices(series_id)",
    "CREATE INDEX IF NOT EXISTS idx_bls_year_month ON bls_prices(year, month)",
    "CREATE INDEX IF NOT EXISTS idx_hpai_date ON hpai_detections(confirmation_date)",
    "CREATE INDEX IF NOT EXISTS idx_hpai_state ON hpai_detections(state)",
    "CREATE INDEX IF NOT EXISTS idx_hpai_flock_type ON hpai_detections(flock_type)",
    "CREATE INDEX IF NOT EXISTS idx_broiler_hatchability_week_end ON broiler_hatchability(week_ending_date)",
    "CREATE INDEX IF NOT EXISTS idx_cage_free_month ON cage_free_flock_composition(report_month)",
    "CREATE INDEX IF NOT EXISTS idx_ers_trade_month ON ers_trade_totals(report_month)",
    "CREATE INDEX IF NOT EXISTS idx_ers_trade_lookup ON ers_trade_totals(commodity, flow, product)",
    "CREATE INDEX IF NOT EXISTS idx_cme_feed_daily_trade_date ON cme_feed_daily(trade_date)",
    "CREATE INDEX IF NOT EXISTS idx_source_freshness ON source_freshness(source_name)",
    "CREATE INDEX IF NOT EXISTS idx_narrative_sentiment_date ON narrative_sentiment(report_date)",
]


def create_all(conn):
    """Execute all CREATE TABLE, VIEW, and INDEX statements."""
    cur = conn.cursor()
    # One-time migration: drop hpai_detections if it has the old UNIQUE
    # constraint (which collapsed legitimately distinct detections).
    # Safe because data is full-refreshed on every ingestion run.
    row = cur.execute(
        "SELECT sql FROM sqlite_master "
        "WHERE type='table' AND name='hpai_detections'"
    ).fetchone()
    if row and "UNIQUE" in (row[0] or ""):
        cur.execute("DROP TABLE hpai_detections")
    for ddl in TABLES.values():
        cur.execute(ddl)
    for ddl in VIEWS.values():
        cur.execute(ddl)
    for ddl in INDEXES:
        cur.execute(ddl)
    # Drop stale HPAI dedup index if present (removed: data is now full-refreshed)
    cur.execute("DROP INDEX IF EXISTS idx_hpai_dedupe")
    conn.commit()
