HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Egg Industry Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/split-dashboard.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
</head>
<body>
<div class="shell">
  <header class="hero">
    <div>
      <div class="hero-tag">Egg Industry Dashboard</div>
      <h1>Executive egg market dashboard</h1>
      <p>A dedicated egg-industry view built to mirror the structure of the monthly executive chartbook while using the live chartbook database behind this project.</p>
    </div>
    <div class="hero-meta">
      <div class="meta-card"><span>Updated</span><strong id="updatedStamp">__UPDATED__</strong></div>
      <div class="meta-card"><span>Coverage</span><strong id="coverageStamp">Loading…</strong></div>
      <div class="meta-card"><span>Status</span><strong id="statusStamp">Loading…</strong></div>
    </div>
  </header>

  <nav class="topnav">
    <a class="nav-link" href="index.html">Dashboard Home</a>
    <a class="nav-link active" href="egg-dashboard.html">Egg Industry</a>
    <a class="nav-link" href="broiler-dashboard.html">Broiler Industry</a>
  </nav>

  <section class="kpi-row">
    <article class="kpi"><div class="label">Wholesale Eggs</div><div class="value" id="kpiEggPrice">—</div><div class="sub" id="kpiEggPriceSub"></div></article>
    <article class="kpi"><div class="label">Retail Eggs</div><div class="value" id="kpiRetailEgg">—</div><div class="sub" id="kpiRetailEggSub"></div></article>
    <article class="kpi"><div class="label">Layers</div><div class="value" id="kpiLayers">—</div><div class="sub" id="kpiLayersSub"></div></article>
    <article class="kpi"><div class="label">Pullets</div><div class="value" id="kpiPullets">—</div><div class="sub" id="kpiPulletsSub"></div></article>
    <article class="kpi"><div class="label">HPAI 30D</div><div class="value" id="kpiHpai">—</div><div class="sub" id="kpiHpaiSub"></div></article>
    <article class="kpi"><div class="label">Feed Index</div><div class="value" id="kpiFeed">—</div><div class="sub" id="kpiFeedSub"></div></article>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Charts of the Month</h2><p>Top-of-book retail activity and flock pipeline signals.</p></div></div>
    <div class="grid">
      <article class="card" id="retailFeatureWrap"><h3>Egg Retail Feature Rates</h3><div class="sub">4-week average retail feature participation</div><canvas id="retailFeatureChart" height="120"></canvas></article>
      <article class="card"><h3>Pullet Inventories Continue Climb</h3><div class="sub">Replacement pullets on hand</div><canvas id="pulletClimbChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Avian Influenza</h2><p>Disease pressure and layer-specific bird impacts.</p></div></div>
    <div class="grid">
      <article class="card"><h3>HPAI Detections Per Month</h3><div class="sub">All operations and flock types</div><canvas id="hpaiDetectionsChart" height="120"></canvas></article>
      <article class="card"><h3>Commercial Layer Depopulations</h3><div class="sub">Layer-related birds affected by month</div><canvas id="hpaiLayersChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Production Figures</h2><p>Production, lay rate, and breaker flow.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Production Recovering Sharply</h3><div class="sub">Trailing 3-month table egg production</div><canvas id="trailingProdChart" height="120"></canvas></article>
      <article class="card"><h3>Monthly Egg Production</h3><div class="sub">Current year versus prior year</div><canvas id="monthlyProdChart" height="120"></canvas></article>
      <article class="card"><h3>Rate of Lay</h3><div class="sub">Table eggs per 100 layers per day</div><canvas id="rolChart" height="120"></canvas></article>
      <article class="card"><h3>Eggs Delivered to Breakers</h3><div class="sub">Broken shell eggs and share of total production</div><canvas id="breakersChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Layer Flock</h2><p>Seasonality, turnover, and molting.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Table-Egg Layer Flock Size</h3><div class="sub">Seasonal comparison of table-egg layers on hand</div><canvas id="tableLayersChart" height="120"></canvas></article>
      <article class="card"><h3>Turnover Slows in Mid 2025</h3><div class="sub">Slaughter sales and loss / rendered birds</div><canvas id="turnoverChart" height="120"></canvas></article>
      <article class="card"><h3>Molting Watch</h3><div class="sub">Share of the flock being molted</div><canvas id="moltChart" height="120"></canvas></article>
      <article class="card note-card" id="compositionPlaceholder"><h3>Flock Size and Composition</h3></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Breeder Flock and Supply</h2><p>Breeder inventory, hatch, and pullet pipeline intensity.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Breeder Flock Size and Change</h3><div class="sub">Hatching layers and monthly change</div><canvas id="breederFlockChart" height="120"></canvas></article>
      <article class="card"><h3>Egg-Type Chicks Hatched</h3><div class="sub">Current year versus historical average</div><canvas id="chicksChart" height="120"></canvas></article>
      <article class="card wide"><h3>Flock Pipeline Intensity</h3><div class="sub">Pullets per 100 table layers</div><canvas id="pipelineChart" height="110"></canvas></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>Prices</h2><p>Wholesale, retail, regional, and feed-cost context.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Wholesale Rates Continue to Fall</h3><div class="sub">5-day average caged large white egg index</div><canvas id="wholesaleChart" height="120"></canvas></article>
      <article class="card"><h3>Retail Prices by Environment</h3><div class="sub">National large white featured prices</div><canvas id="retailPriceChart" height="120"></canvas></article>
      <article class="card" id="feedIndexWrap"><h3>Layer Feed Index</h3><div class="sub">Composite layer ration cost proxy</div><canvas id="feedIndexChart" height="120"></canvas></article>
      <article class="card"><h3>Regional Egg Prices</h3><div class="sub">Combined regional shell egg prices</div><canvas id="regionalEggChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><div><h2>International</h2><p>Reserved for the trade pages from the monthly chartbook.</p></div></div>
    <div class="grid">
      <article class="card note-card" id="importsPlaceholder"><h3>Egg Imports</h3></article>
      <article class="card note-card" id="exportsPlaceholder"><h3>Monthly Egg Exports</h3></article>
    </div>
  </section>

  <div class="footer">Egg dashboard updated __UPDATED__. Sources in this build include USDA MARS, USDA NASS, and USDA APHIS.</div>
</div>
<script src="assets/dashboard-common.js"></script>
<script src="assets/egg-dashboard.js"></script>
</body>
</html>
"""
