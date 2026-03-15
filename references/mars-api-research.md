# USDA Chicken & Egg Data Available via MARS API

## Context

Research into what data from the USDA "Chickens and Eggs" monthly report (and related poultry/egg reports) can be pulled from the MARS API, including historical data depth for each data series. All findings verified by live API queries using the `MARS_API_KEY` environment variable.

**Important distinction**: The NASS "Chickens and Eggs" monthly report (layers on hand, egg production, rate of lay, hatchery data, disposition) is a **statistical survey** published by NASS -- it is **NOT** available via the MARS API. That data lives in the NASS QuickStats API. The MARS API provides **market/price data** from AMS.

---

## MARS API Reports with Structured Data (Chicken & Egg)

### API Details
- **Base URL**: `https://marsapi.ams.usda.gov/services/v1.2/reports/{slug_id}`
- **Auth**: HTTP Basic Auth with `MARS_API_KEY` as username, no password
- **Date filter**: `?q=report_begin_date=MM/DD/YYYY:MM/DD/YYYY&allSections=true`
- **Max date range per request**: 180 days (chunk longer ranges)
- **Existing integration**: `hpai-dashboard/parsers.py` already fetches slug 2843

---

### Reports Confirmed to Return Structured JSON Data

| # | Slug | Report Name | Freq | Earliest Data | ~Years |
|---|------|-------------|------|---------------|--------|
| 1 | **2843** | Daily National Shell Egg Index (5-day rolling avg) | Daily | Feb 2025 | ~1 yr |
| 2 | **2734** | Daily New York Shell Egg | Daily | Feb 2025 | ~1 yr |
| 3 | **3888** | Daily National Breaking Stock | Daily | Feb 2025 | ~1 yr |
| 4 | **2848** | Weekly Combined Regional Shell Egg Report | Weekly | Jan 2025 | ~1 yr |
| 5 | **2842** | Weekly National Egg Products (liquid/frozen/dried) | Weekly | Feb 2025 | ~1 yr |
| 6 | **1427** | National Weekly Shell Egg Inventory | Weekly | Nov 2017 | ~8 yrs |
| 7 | **1665** | Weekly Shell Eggs Processed Under Federal Inspection | Weekly | Apr 2019 | ~7 yrs |
| 8 | **1624** | Weekly Poultry & Egg Cold Storage Holdings | Weekly | Mar 2019 | ~7 yrs |
| 9 | **3646** | Weekly National Chicken Report | Weekly | Jan 2023 | ~3 yrs |
| 10 | **3649** | Monthly National Chicken Report | Monthly | Jan 2023 | ~3 yrs |
| 11 | **2756** | Weekly Retail Chicken Feature Activity | Weekly | 2010+ | 16+ yrs |
| 12 | **2757** | Weekly Retail Egg Feature Activity | Weekly | 2010+ | 16+ yrs |

---

### Detailed Data Points Per Report

#### 1. Slug 2843 -- Daily National Shell Egg Index
**Sections**: Report Header, Volume Weighted, Detail Weighted
**Data points**:
- Weighted avg price (cents/dozen), volume, previous price, last year price
- **Environments**: Caged, Cage-Free, Free-Range, USDA Organic, USDA Organic Free-Range
- **Classes**: Large, Extra Large, Medium, Small, Jumbo, 1, 2, 3
- **Colors**: White, Brown
- **Egg types**: Gradeable Nest Run, Graded Loose
- **Origins**: National, California, regional (MW, NE, NW, SC, SE, SW)
- **Destinations**: National, California, Export, regional
- **Freight**: FOB, Delivered
- Narrative text (market commentary)
- **History**: Feb 2025 -- present (~1 year)

#### 2. Slug 2734 -- Daily New York Shell Egg
**Data points**:
- Price low/high/avg (cents/dozen), previous avg
- **Classes**: Extra Large, Large, Medium
- **Environment**: Caged
- Cartoned, Grade A, Delivered Store Door
- **History**: Feb 2025 -- present (~1 year)

#### 3. Slug 3888 -- Daily National Breaking Stock
**Data points**:
- Price low/high/avg (cents/dozen), previous avg
- **Egg types**: Undergrades, Checks, Breaking Stock
- Caged, National, Delivered, Ungraded
- **History**: Feb 2025 -- present (~1 year)

#### 4. Slug 2848 -- Weekly Combined Regional Shell Egg
**Data points**:
- Price low/high/avg (cents/dozen), previous avg
- **Classes**: Extra Large, Large, Medium, Small
- **Regions**: Northeast, Midwest, South Central, Southeast, National
- Caged, Cartoned, White, Grade A, Delivered Warehouse
- **History**: Jan 2025 -- present (~1 year)

#### 5. Slug 2842 -- Weekly National Egg Products
**Data points**:
- Weighted avg price, volume (liquid); simple prices (frozen/dried)
- **Commodities**: Liquid Eggs, Frozen Eggs, Dried Eggs
- **Egg types**: Liquid Whole, Liquid White, Liquid Yolk, Dried Whole, Frozen Whole, etc.
- Caged, National, FOB
- Narrative text (liquid/frozen/dried market commentary)
- **History**: Feb 2025 -- present (~1 year)

#### 6. Slug 1427 -- National Weekly Shell Egg Inventory
**Data points**:
- Volume (30-dozen cases, thousands), % change vs last week
- **Classes**: Large, Extra Large, Medium, Small, Jumbo, Breaking Stock, Misc, Ungraded, Total
- **Types**: Cage-Free, Organic, Specialty, N/A (conventional)
- **Regions**: 6-Area total, Midwest, Northeast, Northwest, South Central, Southeast, Southwest
- **History**: Nov 2017 -- present (~8 years) -- DEEPEST EGG HISTORY

#### 7. Slug 1665 -- Weekly Shell Eggs Processed
**Data points**:
- Volume by period (current week, prior week, YTD, previous year, % changes)
- **Classes**: Cases Broken, Liquid Whole/White/Yolk, Dried, Inedible, Inline %, Yield
- Current week, prior week, year-to-date, last year comparisons, % change
- **History**: Apr 2019 -- present (~7 years)

#### 8. Slug 1624 -- Weekly Poultry & Egg Cold Storage Holdings
**Data points**:
- Holdings (lbs): current, 1st day of month, change lbs, change %
- **Categories**: Eggs, Chicken, Turkey
- **Commodities**: Frozen Eggs, Processed Other Poultry, Processed Turkeys
- **History**: Mar 2019 -- present (~7 years)

#### 9. Slug 3646 -- Weekly National Chicken Report
**Data points**:
- Prices: low, high, weighted avg (cents/lb), previous week avg/volume, price change
- **Items**: 19 cuts including Breast B/S, Breast Line Run, Tenderloins, Thighs B/S, Thighs Bone-in, Drumsticks, Legs Bone-in, Leg Quarters (Bulk), Wings Whole, Backs/Necks, MSC, Frames, WOG, RTC Broiler, Breast with Ribs, Livers, Gizzards/Hearts, V-Cut Wings
- National, Domestic, Fresh, Conventional, FOB
- **History**: Jan 2023 -- present (~3 years)

#### 10. Slug 3649 -- Monthly National Chicken Report
**Data points**: Same structure as 3646 but monthly aggregation
- **History**: Jan 2023 -- present (~3 years)

#### 11. Slug 2756 -- Weekly Retail Chicken Feature Activity
**Data points**:
- **Metrics section**: Feature rate, activity index, store count (current/last week/last year) by region
- **Details section**: Avg/min/max price (per lb or per unit), store count
- **Types**: 42 chicken product types including whole birds, parts, IQF, ground, prepared, deli
- **Environments**: Conventional, Antibiotic Free, ABF Free Range, ABF Pasture Raised, USDA Organic, USDA Organic Free Range
- **Regions**: National, Midwest, Northeast, Northwest, Southcentral, Southeast, Southwest, Alaska, Hawaii
- **History**: 2010 -- present (16+ years) -- DEEPEST CHICKEN HISTORY

#### 12. Slug 2757 -- Weekly Retail Egg Feature Activity
**Data points**:
- **Metrics section**: Feature rate, activity index, store count (current/last week/last year) by region
- **Details section**: Avg/min/max price (per carton or per unit), store count
- **Types**: Large/Extra Large/Medium/Jumbo White/Brown, Liquid Egg, Liquid Egg White
- **Environments**: Conventional, Cage-Free, Free Range, Pasture Raised, USDA Organic, USDA Organic Free Range, USDA Organic Pasture Raised, Nutritionally Enhanced (Omega-3), Vegetarian-Fed
- **Regions**: National, Midwest, Northeast, Northwest, Southcentral, Southeast, Southwest, Alaska
- Package sizes: 12, 18, etc.
- **History**: 2010 -- present (16+ years) -- DEEPEST EGG RETAIL HISTORY

---

### Reports That Do NOT Return Structured API Data (PDF/TXT only)

These reports are published to MARS but return 0 rows via the JSON API -- they're PDF or text-only:

| Slug | Report | Notes |
|------|--------|-------|
| 2806 | Shell Egg Demand Indicator (SEDI) | PDF only |
| 2755 | Weekly National Retail Egg Purchases | TXT only |
| 2847 | Monthly Cage-Free Shell Egg Report | PDF only |
| 2740 | Daily National Broiler Market at a Glance | PDF only |
| 2818 | Weekly Fryer Slaughter/Availability | TXT only |
| 2819 | Weekly Young Chickens Slaughtered | TXT only |
| 2759 | Organic Poultry and Eggs | PDF only |
| 3725 | Egg Markets Overview | PDF only |

---

## NASS QuickStats API (Production/Inventory Data -- NOT MARS)

The NASS "Chickens and Eggs" monthly report data is available via a separate API. All findings below verified by live API queries on 2026-03-01 using the `NASS_API_KEY` environment variable.

### API Details
- **Base URL**: `https://quickstats.nass.usda.gov/api/api_GET/?key=$NASS_API_KEY&params`
- **Auth**: API key as `key=` query parameter (free, register at QuickStats portal)
- **Param discovery**: `/api/get_param_values/?key=$NASS_API_KEY&param=PARAM_NAME`
- **Record count check**: `/api/get_counts/?key=$NASS_API_KEY&filters`
- **Max records per request**: 50,000
- **Output formats**: JSON, CSV, XML
- **Query operators**: `__GE`, `__LE`, `__GT`, `__LT`, `__LIKE`, `__NOT_LIKE`, `__NE`
- **Important**: URL-encode `&` in values (e.g., "ANIMALS & PRODUCTS" breaks the URL)

### Record Structure
Each record contains these fields:
```
commodity_desc, class_desc, short_desc (data item name)
statisticcat_desc (e.g., INVENTORY, PRODUCTION, RATE OF LAY)
unit_desc (HEAD, EGGS, DOZEN, LB, $ / DOZEN, EGGS / 100 LAYER, etc.)
Value (the data value)
year, freq_desc (ANNUAL, MONTHLY, WEEKLY, POINT IN TIME)
reference_period_desc (e.g., FIRST OF JAN, JAN, YEAR)
agg_level_desc (NATIONAL, STATE)
state_alpha, state_name, location_desc
source_desc (SURVEY)
domain_desc, domaincat_desc
load_time
```

### Relevant Commodities
- `CHICKENS` -- layers, broilers, hatchery, pullets, chicks, cold storage, slaughter
- `EGGS` -- production, prices, hatching eggs, cold storage, edible products

---

### Data Series from the "Chickens and Eggs" Report

#### A. Layer Inventory & Disposition

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| CHICKENS, LAYERS - INVENTORY | Monthly (1st of month) | 1997 | 2026 | National | 529 |
| CHICKENS, LAYERS - INVENTORY | Monthly (1st of month) | 1974 | 2025 | State (51) | 15,410 |
| CHICKENS, LAYERS, TABLE - INVENTORY | Monthly (1st of month) | 2008 | 2026 | National | 218 |
| CHICKENS, LAYERS, HATCHING - INVENTORY | Monthly (1st of month) | 2008 | 2026 | National | 218 |
| CHICKENS, LAYERS, HATCHING, BROILER TYPE - INVENTORY | Monthly (1st of month) | 2008 | 2026 | National | 218 |
| CHICKENS, LAYERS - LOSS, DEATH & RENDERED, MEASURED IN HEAD | Monthly | 2007 | 2026 | National | 218 |
| CHICKENS, LAYERS - SALES FOR SLAUGHTER, MEASURED IN HEAD | Monthly | 2007 | 2026 | National | 218 |
| CHICKENS, LAYERS - BEING MOLTED, MEASURED IN PCT OF INVENTORY | Monthly (1st of month) | 2008 | 2026 | National | 218 |
| CHICKENS, PULLETS, REPLACEMENT - INVENTORY | Monthly (1st of month) | 2002 | 2026 | National | 474 |

#### B. Egg Production & Rate of Lay

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| EGGS - PRODUCTION, MEASURED IN EGGS | Monthly + Annual | 2007 | 2026 | National | 236 |
| EGGS - PRODUCTION, MEASURED IN EGGS | Monthly + Annual | 1944 | 2026 | State (42) | 7,315 |
| EGGS, TABLE - PRODUCTION, MEASURED IN EGGS | Monthly + Annual | 2007 | 2026 | National | 236 |
| EGGS, HATCHING, BROILER TYPE - PRODUCTION, MEASURED IN EGGS | Monthly + Annual | 2007 | 2026 | National | 223 |
| CHICKENS, LAYERS - RATE OF LAY, MEASURED IN EGGS / 100 LAYER | Monthly | 2007 | 2026 | National | 436 |
| CHICKENS, LAYERS, TABLE - RATE OF LAY, MEASURED IN EGGS / 100 LAYER | Monthly | 2007 | 2026 | National | 436 |

#### C. Hatchery Data

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| CHICKENS, CHICKS, BROILER TYPE - HATCHED, MEASURED IN HEAD | Monthly + Annual | 2012 | 2026 | National | 182 |
| CHICKENS, CHICKS, EGG TYPE - HATCHED, MEASURED IN HEAD | Monthly | 2012 | 2026 | National | 169 |
| CHICKENS, BROILERS - EGGS SET, MEASURED IN EGGS | Weekly + Annual | 2013 | 2026 | National | 698 |
| CHICKENS, BROILER TYPE - EGGS IN INCUBATORS, MEASURED IN EGGS | -- | -- | -- | National | -- |
| CHICKENS, EGG TYPE - EGGS IN INCUBATORS, MEASURED IN EGGS | -- | -- | -- | National | -- |
| CHICKENS, HATCHERY - CAPACITY, MEASURED IN EGGS | Annual (1st of month) | 2008 | 2025 | National | 18 |

#### D. Placements & Intended Placements

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| CHICKENS, BROILERS - PLACEMENTS, MEASURED IN HEAD | Weekly + Annual | 2013 | 2026 | National | 698 |
| CHICKENS, CHICKS, BROILER TYPE, PULLET - PLACEMENTS, INTENDED, MEASURED IN HEAD | Monthly + Annual | 2013 | 2026 | National | 169 |
| CHICKENS, CHICKS, EGG TYPE, PULLET - PLACEMENTS, INTENDED, MEASURED IN HEAD | Monthly + Annual | 2013 | 2026 | National | 169 |
| CHICKENS, CHICKS, EGG TYPE, PULLET - PLACEMENTS, MEASURED IN HEAD | Monthly | 2023 | 2023 | National | 1 |

#### E. Prices

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| EGGS - PRICE RECEIVED, MEASURED IN $ / DOZEN | Monthly + Annual | 1996 | 2026 | National | 360 |
| CHICKENS, BROILERS - PRICE RECEIVED, MEASURED IN $ / LB | Monthly + Annual | 1991 | 2026 | National | 453 |

#### F. Broiler Production

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| CHICKENS, BROILERS - PRODUCTION, MEASURED IN HEAD | Annual | 2008 | 2024 | National | 17 |
| CHICKENS, BROILERS - PRODUCTION, MEASURED IN LB | -- | -- | -- | National | -- |

#### G. Cold Storage & Processed Products

| Data Item (`short_desc`) | Freq | Earliest | Latest | Geo | Records |
|--------------------------|------|----------|--------|-----|---------|
| CHICKENS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB | Monthly (1st of month) | 1940 | 2026 | National | 1,027 |
| EGGS, COLD STORAGE, FROZEN - STOCKS, MEASURED IN LB | Monthly (1st of month) | 1990 | 2026 | National | 433 |
| EGGS, SHELL - BROKEN, MEASURED IN DOZEN | Monthly | 2013 | 2026 | National | 157 |
| EGGS, EDIBLE PRODUCT - PRODUCTION, MEASURED IN LB | Monthly | 2013 | 2026 | National | 157 |
| EGGS, EDIBLE PRODUCT, WHOLE - PRODUCTION, MEASURED IN LB | Monthly | 2013 | 2026 | National | -- |
| EGGS, EDIBLE PRODUCT, WHITE - PRODUCTION, MEASURED IN LB | Monthly | 2013 | 2026 | National | -- |
| EGGS, EDIBLE PRODUCT, YOLK - PRODUCTION, MEASURED IN LB | Monthly | 2013 | 2026 | National | -- |

#### H. Additional Chicken Cold Storage Detail

| Data Item (`short_desc`) | Freq | Notes |
|--------------------------|------|-------|
| CHICKENS, BREASTS & BREAST MEAT, COLD STORAGE, FROZEN - STOCKS | Monthly | Part-level breakdown |
| CHICKENS, DRUMSTICKS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, LEG QUARTERS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, LEGS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, THIGH & THIGH QUARTERS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, THIGH MEAT, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, WINGS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, PAWS & FEET, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, OTHER PARTS & FORMS, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, YOUNG, WHOLE, COLD STORAGE, FROZEN - STOCKS | Monthly | |
| CHICKENS, MATURE, WHOLE, HENS, COLD STORAGE, FROZEN - STOCKS | Monthly | |

---

### NASS QuickStats: Historical Data Depth at a Glance

```
  86 years: Chicken Cold Storage (1940-present)
  82 years: State Egg Production (1944-present, 42 states)
  35 years: Broiler Price Received (1991-present)
  36 years: Egg Cold Storage (1990-present)
  30 years: Egg Price Received (1996-present)
  29 years: National Layer Inventory (1997-present)
  52 years: State Layer Inventory (1974-present)
  24 years: Replacement Pullet Inventory (2002-present)
  19 years: Table/Hatching Layer Detail, Rate of Lay, Death Loss,
            Slaughter, Molting, Hatching Egg Prod (2007/2008-present)
  14 years: Chicks Hatched (2012-present)
  13 years: Eggs Set, Broiler Placements, Intended Placements,
            Shell Eggs Broken, Edible Egg Products (2013-present)
```

---

## Combined Summary: MARS + NASS Historical Data Depth

```
MARS API (AMS market/price data):
  16+ years: Retail Chicken (2756), Retail Egg (2757)
   ~8 years: Shell Egg Inventory (1427)
   ~7 years: Eggs Processed (1665), Cold Storage (1624)
   ~3 years: Weekly/Monthly Chicken (3646/3649)
   ~1 year:  Shell Egg Index (2843), NY Shell Egg (2734),
             Regional Shell Egg (2848), Egg Products (2842),
             Breaking Stock (3888)

NASS QuickStats API (NASS survey/statistical data):
  86 years: Chicken Cold Storage (1940)
  82 years: State Egg Production (1944)
  52 years: State Layer Inventory (1974)
  35 years: Broiler Prices (1991)
  30 years: Egg Prices (1996)
  29 years: National Layer Inventory (1997)
  24 years: Replacement Pullets (2002)
  19 years: Layer Detail / Rate of Lay / Disposition (2007-08)
  14 years: Chicks Hatched (2012)
  13 years: Eggs Set / Placements / Breaking / Edible Products (2013)
```
