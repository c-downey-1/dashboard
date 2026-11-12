"""Data assembly for the Broiler Industry Dashboard.

Everything the broiler page draws comes from the single ``broiler`` block built
here, so the page never has to guess which keys of a shared block are broiler
series (the cause of several mislabelled charts in the original page).
"""

from __future__ import annotations

from datetime import date, timedelta

from .hpai_categories import HPAI_CATEGORY_GROUPS

# Broiler ration used for the feed-cost index: corn and soybean meal are ~93% of
# a typical US broiler grower diet by weight and nearly all of its price swing.
BROILER_RATION = {"corn": 0.65, "soymeal": 0.28}

# Hatchability baseline: the pre-decline years. Weekly coverage in these years
# is 47–53 reports a year, so this is an average of the reports available.
HATCH_BASELINE_YEARS = (2012, 2019)

WHOLESALE_CUTS = [
    "Breast - B/S",
    "Tenderloins",
    "Wings - Whole",
    "Thighs - B/S",
    "Drumsticks",
    "Leg quarters - Bulk",
    "WOG",
]

RETAIL_TYPES = [
    "Breast, Boneless/Skinless",
    "Thighs, Boneless/Skinless",
    "Drumsticks",
    "Leg Quarters",
    "Party Wings, Flats and Drums",
    "Whole Bagged Fryer",
]

# Only operation types APHIS labels as broiler. The generic "Commercial Breeder
# Operation" carries no species and APHIS epi reports place some under turkey.
HPAI_BROILER_GROUPS = {
    "Broiler production": ("Commercial Broiler Production",),
    "Broiler breeders": (
        "Commercial Broiler Breeder",
        "Primary Broiler Breeder Pedigree Farm",
    ),
    "Breeder pullets": ("Commercial Broiler Breeder Pullets",),
}
# Shown separately in grey: APHIS does not state the species for these.
HPAI_UNCLASSIFIED_GROUP = {"Breeders, species not stated": ("Commercial Breeder Operation",)}

MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def _r(value, digits=4):
    return round(value, digits) if value is not None else None


def _nass_monthly(conn, item, prefix=""):
    """National monthly NASS series → ({'YYYY-MM': value}). ``prefix`` selects
    'FIRST OF '/'END OF ' inventory periods; '' selects plain month totals."""
    rows = conn.execute(
        """SELECT year, reference_period, value FROM nass_data
           WHERE data_item = ? AND agg_level = 'NATIONAL' AND value IS NOT NULL""",
        (item,),
    ).fetchall()
    out = {}
    for year, ref, val in rows:
        mon = ref[len(prefix):] if ref.startswith(prefix) else None
        if prefix == "" and ref not in MONTHS:
            continue
        if mon in MONTHS:
            out[f"{year}-{MONTHS[mon]:02d}"] = val
    return dict(sorted(out.items()))


def _week_date(year, week):
    """Fallback week-ending Saturday for a NASS Broiler Hatchery week number.

    Week 1 ends on the first Saturday on or after Jan 4 (it holds at least four
    days of the new year). This reproduces USDA's own week_ending field for all
    722 weekly placement records, 2013–2026; the stored field is preferred."""
    jan4 = date(year, 1, 4)
    first_sat = jan4 + timedelta(days=(5 - jan4.weekday()) % 7)
    return (first_sat + timedelta(weeks=week - 1)).isoformat()


def _nass_weekly(conn, item):
    """National weekly NASS series (WEEK #nn) → sorted list of
    (week_ending, reporting_year, reporting_week, value)."""
    rows = conn.execute(
        """SELECT year, reference_period, value, week_ending FROM nass_data
           WHERE data_item = ? AND agg_level = 'NATIONAL' AND value IS NOT NULL
             AND reference_period LIKE 'WEEK #%'""",
        (item,),
    ).fetchall()
    out = []
    for y, ref, v, we in rows:
        w = int(ref.replace("WEEK #", ""))
        out.append((we or _week_date(y, w), y, w, v))
    out.sort()
    dates = [p[0] for p in out]
    assert len(dates) == len(set(dates)), f"duplicate week-ending dates in {item}"
    assert all((p[1], p[2]) < (q[1], q[2]) for p, q in zip(out, out[1:])), \
        f"week-ending dates out of reporting order in {item}"
    return out


def _weekly_block(points):
    """Weekly level + trailing 4-week total vs the 4 weeks ending 364 days earlier.

    Windows run across reporting-year boundaries and use a fixed 364-day offset,
    so a 53-week year does not turn the comparison into a 371-day one."""
    by_date = {p[0]: p[3] for p in points}
    dates, values, yoy = [], [], []
    for d, _, _, v in points:
        dates.append(d)
        values.append(v)
        d0 = date.fromisoformat(d)
        cur = [by_date.get((d0 - timedelta(weeks=k)).isoformat()) for k in range(4)]
        prev = [by_date.get((d0 - timedelta(days=364, weeks=k)).isoformat()) for k in range(4)]
        if None not in cur and None not in prev and sum(prev):
            yoy.append(_r((sum(cur) / sum(prev) - 1) * 100, 2))
        else:
            yoy.append(None)
    by_year, by_year_dates = {}, {}
    for d, y, w, v in points:
        by_year.setdefault(str(y), [None] * 53)[w - 1] = v
        by_year_dates.setdefault(str(y), [None] * 53)[w - 1] = d
    return {"dates": dates, "values": values, "yoy_4wk": yoy,
            "by_year": by_year, "by_year_dates": by_year_dates}


def _monthly_block(series):
    """Monthly level + % change vs the same month a year earlier."""
    dates = list(series)
    values = [series[d] for d in dates]
    yoy = []
    for d, v in zip(dates, values):
        prev = series.get(f"{int(d[:4]) - 1}{d[4:]}")
        yoy.append(_r((v / prev - 1) * 100, 2) if prev else None)
    return {"dates": dates, "values": values, "yoy": yoy}


def _nearest_saturday(d):
    """Snap a date to the nearest Saturday (Saturday = weekday 5)."""
    shift = (5 - d.weekday()) % 7
    return d + timedelta(days=shift if shift <= 3 else shift - 7)


def _hatchability(conn):
    rows = conn.execute(
        """SELECT release_date, week_ending_date, hatchability_pct
           FROM broiler_hatchability WHERE hatchability_pct IS NOT NULL
           ORDER BY release_date"""
    ).fetchall()
    observed = {}
    for release, week_end, pct in rows:
        # Seeded history has no week-ending date. Releases normally come out the
        # Wednesday after the Saturday week-ending; holiday weeks shift by a day
        # or two, so snap (release - 4 days) to the nearest Saturday.
        if week_end:
            d = _nearest_saturday(date.fromisoformat(week_end))
        else:
            d = _nearest_saturday(date.fromisoformat(release) - timedelta(days=4))
        observed[d] = pct

    # Explicit weekly calendar: weeks with no report are null, so lines break
    # across gaps instead of bridging them.
    first, last = min(observed), max(observed)
    dates, values = [], []
    d = first
    while d <= last:
        dates.append(d.isoformat())
        values.append(observed.get(d))
        d += timedelta(weeks=1)

    # Trailing 52-week average over elapsed time (the 52 calendar weeks ending
    # at each date), using the reports available; null if fewer than 40.
    avg52 = []
    for i in range(len(values)):
        win = [v for v in values[max(0, i - 51):i + 1] if v is not None]
        avg52.append(_r(sum(win) / len(win), 3) if len(win) >= 40 and values[i] is not None else None)
    obs = [(d, v) for d, v in zip(dates, values) if v is not None]

    by_month = {}
    for d, v in obs:
        by_month.setdefault(d[:7], []).append(v)
    monthly = {m: sum(v) / len(v) for m, v in sorted(by_month.items())}

    by_year = {}
    for d, v in obs:
        by_year.setdefault(d[:4], []).append(v)
    annual = {y: _r(sum(v) / len(v), 2) for y, v in by_year.items()}
    weeks = {y: len(v) for y, v in by_year.items()}
    # Latest year is partial: also give the prior year over the same weeks.
    last_year = max(by_year)
    cutoff = obs[-1][0][5:]
    prev_same = [v for d, v in obs if d[:4] == str(int(last_year) - 1) and d[5:] <= cutoff]
    ytd_compare = {
        "year": last_year,
        "through": obs[-1][0],
        "weeks": weeks[last_year],
        "value": annual[last_year],
        "prior_value": _r(sum(prev_same) / len(prev_same), 2) if prev_same else None,
        "prior_weeks": len(prev_same),
    }

    lo, hi = HATCH_BASELINE_YEARS
    base_vals = [v for d, v in obs if lo <= int(d[:4]) <= hi]
    baseline = _r(sum(base_vals) / len(base_vals), 2) if base_vals else None
    base_month = []
    for m in range(1, 13):
        vals = [monthly[k] for k in monthly if lo <= int(k[:4]) <= hi and int(k[5:]) == m]
        base_month.append(_r(sum(vals) / len(vals), 2) if vals else None)

    return {
        "dates": dates,
        "values": values,
        "avg52": avg52,
        "monthly_dates": list(monthly),
        "monthly_values": [_r(v, 2) for v in monthly.values()],
        "annual": annual,
        "annual_weeks": weeks,
        "ytd_compare": ytd_compare,
        "baseline": baseline,
        "baseline_reports": len(base_vals),
        "baseline_label": f"{lo}–{hi} avg",
        "baseline_by_month": base_month,
    }


def _breeder(conn):
    hens = _nass_monthly(conn, "CHICKENS, LAYERS, HATCHING, BROILER TYPE - INVENTORY", "FIRST OF ")
    eggs = _nass_monthly(conn, "EGGS, HATCHING, BROILER TYPE - PRODUCTION, MEASURED IN EGGS")
    chicks = _nass_monthly(conn, "CHICKENS, CHICKS, BROILER TYPE - HATCHED, MEASURED IN HEAD")
    # U.S. placements only (the series without "FOR DOMESTIC USE" also counts
    # pullet chicks hatched here for export, ~24% more in 2025).
    pullets = _nass_monthly(
        conn,
        "CHICKENS, CHICKS, BROILER TYPE, PULLET, FOR DOMESTIC USE - PLACEMENTS, INTENDED, MEASURED IN HEAD",
    )
    dates = list(hens)
    pullet_dates = list(pullets)
    pullet_vals = [pullets[d] for d in pullet_dates]

    # USDA's "cumulative potential placements relative to current supply flocks":
    # pullet chicks placed 7–15 months earlier (Chickens and Eggs, Apr 2026, p.19).
    # Known up to 7 months past the latest placement month.
    def ym_shift(ym, k):
        t = int(ym[:4]) * 12 + int(ym[5:]) - 1 + k
        return f"{t // 12}-{t % 12 + 1:02d}"

    potential = {}
    if pullet_dates:
        m = ym_shift(pullet_dates[0], 15)
        end = ym_shift(pullet_dates[-1], 7)
        while m <= end:
            win = [pullets.get(ym_shift(m, -k)) for k in range(7, 16)]
            if None not in win:
                potential[m] = sum(win)
            m = ym_shift(m, 1)
    return {
        "dates": dates,
        "hens": [hens[d] for d in dates],
        "hens_yoy": _monthly_block(hens)["yoy"],
        "eggs_per_hen": [_r(eggs[d] / hens[d], 2) if eggs.get(d) and hens[d] else None for d in dates],
        "chicks_per_hen": [_r(chicks[d] / hens[d], 2) if chicks.get(d) and hens[d] else None for d in dates],
        "pullet_dates": pullet_dates,
        "pullets": pullet_vals,
        "potential_dates": list(potential),
        "potential": list(potential.values()),
    }


def _wholesale(conn):
    # One explicitly defined series per item: national, domestic, fresh,
    # conventional. Parts are FOB plant; WOG is the delivered all-sizes composite.
    rows = conn.execute(
        f"""SELECT report_date, item, wtd_avg_price FROM chicken_wholesale_detail
            WHERE slug_id = 3646 AND wtd_avg_price IS NOT NULL
              AND region = 'National' AND trade_status = 'Domestic'
              AND condition = 'Fresh' AND environment = 'Conventional'
              AND ((item != 'WOG' AND freight = 'FOB')
                   OR (item = 'WOG' AND freight = 'Delivered' AND size = 'All Sizes'))
              AND item IN ({",".join("?" * len(WHOLESALE_CUTS))})
            ORDER BY report_date""",
        WHOLESALE_CUTS,
    ).fetchall()
    by_date = {}
    for d, item, price in rows:
        assert item not in by_date.get(d, {}), f"two wholesale rows for {item} on {d}"
        by_date.setdefault(d, {})[item] = price
    dates = sorted(by_date)
    series, yoy = {}, {}
    for cut in WHOLESALE_CUTS:
        vals = [by_date[d].get(cut) for d in dates]
        if not any(v is not None for v in vals):
            continue
        series[cut] = vals
        out = []
        for d, v in zip(dates, vals):
            prev_d = (date.fromisoformat(d) - timedelta(days=364)).isoformat()
            prev = by_date.get(prev_d, {}).get(cut)
            out.append(_r((v / prev - 1) * 100, 2) if v is not None and prev else None)
        yoy[cut] = out
    return {"dates": dates, "series": series, "yoy": yoy, "unit": "¢/lb"}


# AMS renamed the retail types in Sept 2024 and moved pack size into its own
# field. Old regular-pack names → new names (levels match across the break:
# e.g. B/S breast $2.91 Jul–Aug 2024 vs $2.87 Sep–Oct 2024). Party wings have no
# pre-2024 equivalent ("WHOLE WINGS" is a different product).
RETAIL_CROSSWALK = {
    "BREAST, BONELESS/SKINLESS, REGULAR PACK": "Breast, Boneless/Skinless",
    "THIGHS, BONELESS/SKINLESS, REGULAR PACK": "Thighs, Boneless/Skinless",
    "DRUMSTICKS, REGULAR PACK": "Drumsticks",
    "LEG QUARTERS, TRAY PACK": "Leg Quarters",
}


def _retail(conn):
    # Defined basket: national, conventional, fresh, regular pack. Frozen and
    # value/bulk packs are separate rows in the source and are left out.
    names = RETAIL_TYPES + list(RETAIL_CROSSWALK)
    rows = conn.execute(
        f"""SELECT report_date, type, price_avg FROM retail_prices_detail
            WHERE slug_id = 2756 AND region IN ('National', 'NATIONAL')
              AND environment = 'Conventional' AND condition = 'Fresh'
              AND price_avg IS NOT NULL AND package_size IN ('Regular', '')
              AND type IN ({",".join("?" * len(names))})
            ORDER BY report_date""",
        names,
    ).fetchall()
    by_date = {}
    for d, typ, price in rows:
        typ = RETAIL_CROSSWALK.get(typ, typ)
        assert typ not in by_date.get(d, {}), f"two retail rows for {typ} on {d}"
        by_date.setdefault(d, {})[typ] = price
    dates = sorted(by_date)
    series = {t: [by_date[d].get(t) for d in dates] for t in RETAIL_TYPES}
    return {"dates": dates, "series": {k: v for k, v in series.items() if any(x is not None for x in v)}}


def _feed_and_margin(conn):
    rows = conn.execute(
        """SELECT trade_date, corn_per_ton, soymeal_per_ton FROM cme_feed_daily
           WHERE corn_per_ton IS NOT NULL AND soymeal_per_ton IS NOT NULL
           ORDER BY trade_date"""
    ).fetchall()
    dates, cost = [], []
    for d, corn, sbm in rows:
        dates.append(d)
        cost.append(_r(BROILER_RATION["corn"] * corn + BROILER_RATION["soymeal"] * sbm, 2))

    by_month = {}
    for d, c in zip(dates, cost):
        by_month.setdefault(d[:7], []).append(c)
    feed_month = {m: sum(v) / len(v) for m, v in by_month.items()}

    price = _nass_monthly(conn, "CHICKENS, BROILERS - PRICE RECEIVED, MEASURED IN $ / LB")
    ratio_dates, ratio, price_vals = [], [], []
    for m, p in price.items():
        f = feed_month.get(m)
        if f and p:
            ratio_dates.append(m)
            # Pounds of feed (corn + SBM component) one pound of liveweight buys.
            ratio.append(_r(p / (f / 2000), 2))
            price_vals.append(p)
    return {
        "feed": {"dates": dates, "cost_per_ton": cost, "ration": BROILER_RATION},
        "price_received": {"dates": list(price), "values": list(price.values())},
        "broiler_feed_ratio": {"dates": ratio_dates, "ratio": ratio, "price": price_vals},
    }


def _exports(conn):
    rows = conn.execute(
        """SELECT report_month, value FROM ers_trade_totals
           WHERE commodity = 'chicken' AND flow = 'export' AND product = 'broiler'
             AND value IS NOT NULL ORDER BY report_month"""
    ).fetchall()
    dates = [r[0] for r in rows]
    totals = {r[0]: r[1] for r in rows}
    country_rows = conn.execute(
        """SELECT report_month, geography_name, value FROM ers_trade_country
           WHERE commodity = 'chicken' AND flow = 'export' AND product = 'broiler'
             AND value IS NOT NULL"""
    ).fetchall()
    by_country = {}
    for m, name, v in country_rows:
        by_country.setdefault(name, {})[m] = v
    # Rank every destination within each selectable range (months), so the
    # "All" view shows the all-history leaders (e.g. Russia, Hong Kong).
    windows = {"3y": 36, "5y": 60, "10y": 120, "all": len(dates)}
    top_by_range = {}
    for key, n in windows.items():
        months = set(dates[-n:])
        ranked = sorted(
            by_country,
            key=lambda c: sum(v for m, v in by_country[c].items() if m in months),
            reverse=True,
        )
        top = ranked[:8]
        # China is always named (it matters to dark-meat and paw markets even
        # when it falls outside the top eight for a period).
        if "China" in by_country and "China" not in top:
            top.append("China")
        top_by_range[key] = top
    keep = []
    for key in ("all", "10y", "5y", "3y"):
        keep += [c for c in top_by_range[key] if c not in keep]
    countries = {n: [by_country[n].get(d) for d in dates] for n in keep}
    return {
        "dates": dates,
        "total": [totals[d] for d in dates],
        "yoy": _monthly_block(totals)["yoy"],
        "countries": countries,
        "top_by_range": top_by_range,
        "unit": "1,000 pounds",
    }


def _hpai(conn):
    broiler_types = [t for group in HPAI_BROILER_GROUPS.values() for t in group]
    assert set(broiler_types) <= set(HPAI_CATEGORY_GROUPS["Commercial Broiler"])
    groups = {**HPAI_BROILER_GROUPS, **HPAI_UNCLASSIFIED_GROUP}
    types = [t for group in groups.values() for t in group]
    rows = conn.execute(
        f"""SELECT strftime('%Y-%m', confirmation_date), flock_type, COUNT(*),
                   SUM(COALESCE(flock_size, 0))
            FROM hpai_detections
            WHERE confirmation_date IS NOT NULL
              AND flock_type IN ({",".join("?" * len(types))})
            GROUP BY 1, 2""",
        types,
    ).fetchall()
    months_all = conn.execute(
        """SELECT MIN(strftime('%Y-%m', confirmation_date)), MAX(strftime('%Y-%m', confirmation_date))
           FROM hpai_detections WHERE confirmation_date IS NOT NULL"""
    ).fetchone()
    dates = []
    if months_all[0]:
        y, m = map(int, months_all[0].split("-"))
        end = months_all[1]
        while f"{y}-{m:02d}" <= end:
            dates.append(f"{y}-{m:02d}")
            m += 1
            if m > 12:
                y, m = y + 1, 1
    group_of = {t: g for g, ts in groups.items() for t in ts}
    birds = {g: [0] * len(dates) for g in groups}
    detections = [0] * len(dates)
    idx = {d: i for i, d in enumerate(dates)}
    for month, ftype, n, b in rows:
        i = idx[month]
        birds[group_of[ftype]][i] += b or 0
        detections[i] += n
    last_detection = conn.execute(
        "SELECT MAX(confirmation_date) FROM hpai_detections"
    ).fetchone()[0]
    last_broiler = conn.execute(
        f"""SELECT confirmation_date, state, county FROM hpai_detections
            WHERE flock_type IN ({",".join("?" * len(broiler_types))})
            ORDER BY confirmation_date DESC LIMIT 1""",
        broiler_types,
    ).fetchone()
    return {"dates": dates, "birds": birds, "detections": detections,
            "data_through": last_detection,
            "last_broiler": {"date": last_broiler[0], "state": last_broiler[1],
                             "county": last_broiler[2]} if last_broiler else None}


YOUNG = "CHICKENS, YOUNG, SLAUGHTER, FI"


def _trailing(series, n=12):
    """{'YYYY-MM': v} → {'YYYY-MM': sum of the n months ending there}, only
    where all n months are present."""
    out = {}
    for m in series:
        t = int(m[:4]) * 12 + int(m[5:]) - 1
        win = [series.get(f"{(t - k) // 12}-{(t - k) % 12 + 1:02d}") for k in range(n)]
        if None not in win:
            out[m] = sum(win)
    return out


def _yoy(series):
    out = {}
    for m, v in series.items():
        prev = series.get(f"{int(m[:4]) - 1}{m[4:]}")
        out[m] = _r((v / prev - 1) * 100, 2) if prev else None
    return out


def _production(conn):
    """Federally inspected young-chicken (broiler) slaughter, from NASS Poultry
    Slaughter, plus annual production by state from Poultry Production and Value."""
    head = _nass_monthly(conn, f"{YOUNG} - SLAUGHTERED, MEASURED IN HEAD")
    live = _nass_monthly(conn, f"{YOUNG} - SLAUGHTERED, MEASURED IN LB, LIVE BASIS")
    weight = _nass_monthly(conn, f"{YOUNG} - SLAUGHTERED, MEASURED IN LB / HEAD, LIVE BASIS")
    rtc = _nass_monthly(conn, f"{YOUNG}, CERTIFIED, CHILLED & FROZEN - PRODUCTION, MEASURED IN LB")
    ante = _nass_monthly(conn, f"{YOUNG} - CONDEMNED, ANTE-MORTEM, MEASURED IN PCT OF SLAUGHTER")
    post = _nass_monthly(
        conn,
        f"{YOUNG}, CARCASS & PARTS - CONDEMNED, POST-MORTEM, "
        "MEASURED IN PCT OF LB CERTIFIED & POST-MORTEM CONDEMNED",
    )
    dates = list(rtc)
    rtc12, head12, live12 = _trailing(rtc), _trailing(head), _trailing(live)
    # 12-month average weight is pounds over birds, not a mean of monthly means.
    weight12 = {m: live12[m] / head12[m] for m in live12 if head12.get(m)}
    rtc12_yoy, head12_yoy = _yoy(rtc12), _yoy(head12)
    weight12_yoy, live12_yoy = _yoy(weight12), _yoy(live12)

    # Annual production by state (pounds live weight produced, Dec–Nov year).
    item = "CHICKENS, BROILERS - PRODUCTION, MEASURED IN LB"
    latest = conn.execute(
        "SELECT MAX(year) FROM nass_data WHERE data_item = ? AND agg_level = 'STATE' AND value IS NOT NULL",
        (item,),
    ).fetchone()[0]
    states = {}
    if latest:
        base_year = latest - 10
        rows = conn.execute(
            """SELECT year, state_alpha, state_name, value FROM nass_data
               WHERE data_item = ? AND agg_level = 'STATE' AND value IS NOT NULL
                 AND reference_period = 'YEAR' AND year IN (?, ?)""",
            (item, latest, base_year),
        ).fetchall()
        cur = {a: (n, v) for y, a, n, v in rows if y == latest and a != "OT"}
        base = {a: v for y, a, n, v in rows if y == base_year}
        national = conn.execute(
            """SELECT value FROM nass_data WHERE data_item = ? AND agg_level = 'NATIONAL'
               AND reference_period = 'YEAR' AND year = ?""",
            (item, latest),
        ).fetchone()
        top = sorted(cur, key=lambda a: cur[a][1], reverse=True)[:10]
        states = {
            "year": latest,
            "base_year": base_year,
            "national": national[0] if national else None,
            "abbr": top,
            "names": [cur[a][0].title() for a in top],
            "values": [cur[a][1] for a in top],
            "base_values": [base.get(a) for a in top],
        }

    def col(series):
        return [_r(series.get(d), 4) if series.get(d) is not None else None for d in dates]

    return {
        "dates": dates,
        "rtc": [rtc[d] for d in dates],
        "rtc_12m": col(rtc12),
        "rtc_12m_yoy": col(rtc12_yoy),
        "head": col(head),
        "head_12m": col(head12),
        "weight": col(weight),
        "weight_12m": col(weight12),
        "head_12m_yoy": col(head12_yoy),
        "weight_12m_yoy": col(weight12_yoy),
        "live_12m_yoy": col(live12_yoy),
        "ante_pct": col(ante),
        "post_pct": col(post),
        "states": states,
    }


def build_broiler(conn):
    """Everything the broiler page needs, in one block."""
    placements = _weekly_block(_nass_weekly(conn, "CHICKENS, BROILERS - PLACEMENTS, MEASURED IN HEAD"))
    eggs_set = _weekly_block(_nass_weekly(conn, "CHICKENS, BROILERS - EGGS SET, MEASURED IN EGGS"))
    chicks = _monthly_block(_nass_monthly(conn, "CHICKENS, CHICKS, BROILER TYPE - HATCHED, MEASURED IN HEAD"))
    cold = _monthly_block(
        _nass_monthly(conn, "CHICKENS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB", "END OF ")
    )
    out = {
        "hatchability": _hatchability(conn),
        "breeder": _breeder(conn),
        "placements": placements,
        "eggs_set": eggs_set,
        "chicks_hatched": chicks,
        "production": _production(conn),
        "cold_storage": cold,
        "wholesale": _wholesale(conn),
        "retail": _retail(conn),
        "exports": _exports(conn),
        "hpai": _hpai(conn),
    }
    out.update(_feed_and_margin(conn))
    return out
