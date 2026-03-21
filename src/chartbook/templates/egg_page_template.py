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
<link rel="stylesheet" href="assets/split-dashboard.css?v=20260321d">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
</head>
<body>
<div class="shell">
  <header class="iaa-bar">
    <a class="iaa-brand" id="topHeaderBrand" href="https://innovateanimalag.org/" target="_blank" rel="noreferrer">
      <img class="iaa-brand-logo" src="assets/iaa-logo-with-navy-font-full-color.png" alt="Innovate Animal Ag">
      <div class="iaa-brand-copy">
        <span class="iaa-eyebrow">Innovate Animal Ag</span>
        <strong>Egg Industry Dashboard</strong>
      </div>
    </a>
    <nav class="iaa-nav" aria-label="Innovate Animal Ag">
      <a href="https://innovateanimalag.org/research" target="_blank" rel="noreferrer">Research</a>
      <a href="https://innovateanimalag.org/#what-we-do" target="_blank" rel="noreferrer">Projects</a>
      <a href="https://innovateanimalag.org/grants" target="_blank" rel="noreferrer">Grants</a>
      <a href="https://innovateanimalag.org/about" target="_blank" rel="noreferrer">About</a>
      <a href="https://innovateanimalag.org/blog" target="_blank" rel="noreferrer">Blog</a>
      <a class="iaa-home-link" href="https://innovateanimalag.org/" target="_blank" rel="noreferrer">InnovateAnimalAg.org</a>
    </nav>
  </header>

  <div class="dashboard-layout">
    <aside class="dashboard-sidebar" aria-label="Egg dashboard outline">
      <div class="dashboard-sidebar-inner">
        <nav class="dashboard-sidebar-nav" id="eggSidebarNav"></nav>
      </div>
    </aside>

    <main class="dashboard-content">
  <section class="section" id="layer-flock">
    <div class="section-head"><div><div class="section-number">I</div><h2>Layer Flock</h2><p>Seasonality, Flock Size, Turnover, Molting, Cage-Free Composition</p></div></div>
    <div class="grid">
      <article class="card"><h3>Table-Egg Layer Flock Size Comparison</h3><div class="sub">Seasonal comparison of table-egg layers on hand</div><canvas id="tableLayersChart" height="120"></canvas></article>
      <article class="card"><h3>Table-Egg Layer Flock Size</h3><div class="sub">Monthly table-egg layers on hand (first of month)</div><canvas id="tableLayersTrendChart" height="120"></canvas></article>
      <article class="card" id="compositionWrap"><h3>Flock Cage-Free Composition</h3><div class="sub">Table layer flock by system type and cage-free share</div><canvas id="compositionChart" height="120"></canvas></article>
      <article class="card"><h3>Flock Turnover</h3><div class="sub">Hens sold for slaughter, destroyed, composted, etc</div><canvas id="turnoverChart" height="120"></canvas></article>
      <article class="card wide"><h3>Flock Turnover Rate</h3><div class="sub">Monthly flock turnover as a share of the table-egg layer flock</div><canvas id="turnoverRateChart" height="110"></canvas></article>
      <article class="card"><h3>Molting Data</h3><div class="sub">Share of flock molted or being molted</div><canvas id="moltChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="production-figures">
    <div class="section-head"><div><div class="section-number">II</div><h2>Production Figures</h2><p>Production, lay rate, and breaker flow.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Monthly Egg Production</h3><div class="sub">Current year versus prior year</div><canvas id="monthlyProdChart" height="120"></canvas></article>
      <article class="card"><h3>Trailing Three Month Table Egg Production</h3><div class="sub">Trailing 3-month table egg production</div><canvas id="trailingProdChart" height="120"></canvas></article>
      <article class="card"><h3>Rate of Lay</h3><div class="sub">Table eggs per 100 layers per day</div><canvas id="rolChart" height="120"></canvas></article>
      <article class="card"><h3>Eggs Delivered to Breakers</h3><div class="sub">Broken shell eggs and share of total production</div><canvas id="breakersChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="prices">
    <div class="section-head"><div><div class="section-number">III</div><h2>Prices</h2><p>Wholesale, retail feature activity, and retail-farmgate price context.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Wholesale Prices</h3><div class="sub">Large Eggs, Conventional, 5-Day Rolling Average</div><canvas id="wholesaleChart" height="120"></canvas></article>
      <article class="card"><h3>Retail Egg Price</h3><div class="sub">FRED Grade A Large eggs, U.S. city average</div><canvas id="eggPriceCompareChart" height="120"></canvas></article>
      <article class="card"><h3>Retail to Farmgate Spread Estimate</h3><div class="sub">FRED Grade A Large eggs, U.S. city average - prior-month NASS all-eggs price received</div><canvas id="eggPriceSpreadChart" height="120"></canvas></article>
      <article class="card" id="retailFeatureWrap"><h3>Egg Retail Feature Rates</h3><div class="sub">4-week average retail feature participation</div><canvas id="retailFeatureChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="breeder-flock">
    <div class="section-head"><div><div class="section-number">IV</div><h2>Pullet Supply and Breeder Flock</h2><p>Breeder inventory, hatch, and pullet pipeline intensity.</p></div></div>
    <div class="grid">
      <article class="card"><h3>Egg-Type Chicks Hatched Comparison</h3><div class="sub">Monthly egg-type chicks hatched in 2025-2026 vs. 2021-2024</div><canvas id="chicksChart" height="120"></canvas></article>
      <article class="card wide"><h3>Egg-Type Chicks Hatched</h3><div class="sub">Historical monthly egg-type chicks hatched</div><canvas id="chicksTrendChart" height="110"></canvas></article>
      <article class="card"><h3>Pullet Inventory</h3><div class="sub">Replacement Egg-Type Pullets on Hand (1st of Month)</div><canvas id="pulletClimbChart" height="120"></canvas></article>
      <article class="card wide"><h3>Flock Pipeline Intensity</h3><div class="sub">Pullets per 100 table layers</div><canvas id="pipelineChart" height="110"></canvas></article>
      <article class="card"><h3>Breeder Flock Size and Change</h3><div class="sub">Hatching layers and monthly change</div><canvas id="breederFlockChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="inputs">
    <div class="section-head"><div><div class="section-number">V</div><h2>Inputs</h2><p>Feed-cost context and input pressure.</p></div></div>
    <div class="grid">
      <article class="card" id="feedIndexWrap"><h3>Layer Feed Index</h3><div class="sub" id="feedIndexSub">67% corn, 22% soybean meal, 8% calcium, 3% other</div><canvas id="feedIndexChart" height="120"></canvas></article>
      <article class="card" id="dieselWrap"><h3>Input Cost Indices</h3><div class="sub">Weekly feed and diesel plus monthly packaging; Jan 2025 baseline = 100</div><canvas id="dieselChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="avian-influenza">
    <div class="section-head"><div><div class="section-number">VI</div><h2>Avian Influenza</h2><p>Disease pressure and layer-specific bird impacts.</p></div></div>
    <div class="grid">
      <article class="card"><h3>HPAI Detections Per Month</h3><div class="sub">All operations and flock types</div><canvas id="hpaiDetectionsChart" height="120"></canvas></article>
      <article class="card"><h3>Commercial Layers Impacted by Month</h3><div class="sub">Includes Commercial Table Egg Layer, Commercial Table Egg Pullets, and Commercial Table Egg Breeder.</div><canvas id="hpaiLayersChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="international">
    <div class="section-head"><div><div class="section-number">VII</div><h2>International Trade</h2><p>USDA ERS monthly trade totals for eggs and egg products.</p></div></div>
    <div class="grid">
      <article class="card" id="importsWrap"><h3>Egg Imports</h3><div class="sub">Total, shell-egg, and egg product imports</div><canvas id="eggImportsTradeChart" height="120"></canvas></article>
      <article class="card" id="exportsWrap"><h3>Egg Exports</h3><div class="sub">Total, shell-egg, and egg product exports</div><canvas id="eggExportsTradeChart" height="120"></canvas></article>
    </div>
  </section>

  <section class="section" id="monthly-updates" data-sidebar-title="Subscribe for Free">
    <div class="section-head"><div><div class="section-number">VIII</div><h2>Monthly Updates</h2><p>Sign up for monthly updates of the Egg Executive Chartbook.</p></div></div>
    <div class="grid">
      <article class="card">
        <h3>Sign Up for Monthly Updates of the Egg Executive Chartbook</h3>
        <form class="dashboard-signup-form" id="eggDashboardSignupForm">
          <label class="dashboard-signup-field" for="dashboardSignupFirstName">
            <span>First Name</span>
            <input id="dashboardSignupFirstName" name="firstName" type="text" autocomplete="given-name" placeholder="First name" required>
          </label>
          <label class="dashboard-signup-field" for="dashboardSignupLastName">
            <span>Last Name</span>
            <input id="dashboardSignupLastName" name="lastName" type="text" autocomplete="family-name" placeholder="Last name" required>
          </label>
          <label class="dashboard-signup-field" for="dashboardSignupEmail">
            <span>Email</span>
            <input id="dashboardSignupEmail" name="email" type="email" autocomplete="email" placeholder="Email address" required>
          </label>
          <button class="dashboard-signup-button" type="submit">Submit Sign Up</button>
          <p class="dashboard-signup-status" id="eggDashboardSignupStatus" aria-live="polite"></p>
        </form>
      </article>
    </div>
  </section>

  <div class="footer">Egg dashboard updated __UPDATED__. Sources in this build include USDA MARS, USDA NASS, USDA ERS, and USDA APHIS.</div>
    </main>
  </div>
</div>
<script src="assets/dashboard-common.js?v=20260321d"></script>
<script src="assets/egg-dashboard.js?v=20260321d"></script>
</body>
</html>
"""
