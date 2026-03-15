"""
template.py — HTML template for the Poultry Intelligence Dashboard.

5-page app: Landing, Eggs, Broilers, Macro, Data Quality.
Chart.js for charts, vanilla JS for interactivity.
"""

# Chart colors
COLORS = {
    "Caged": "#F6851F",
    "Cage-Free": "#1F9EBC",
    "Free-Range": "#013046",
    "Pasture-Raised": "#FDB714",
    "USDA Organic": "#8FCAE6",
    "USDA Organic Free-Range": "#939598",
}

REGION_COLORS = {
    "National": "#013046",
    "Northeast": "#F6851F",
    "Midwest": "#1F9EBC",
    "South Central": "#FDB714",
    "Southeast": "#8FCAE6",
    "Southwest": "#939598",
    "Northwest": "#E5700A",
}

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>Poultry Intelligence Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --navy:#013046;
  --navy-2:#0a4561;
  --orange:#F6851F;
  --orange-soft:#fab87b;
  --teal:#1F9EBC;
  --gold:#FDB714;
  --sky:#8FCAE6;
  --slate:#939598;
  --mist:#f3f7fb;
  --panel:#ffffffd9;
  --border:#d7e3ed;
  --shadow:0 24px 60px rgba(1,48,70,.12);
}
body{
  font-family:'Lexend',sans-serif;
  background:
    radial-gradient(circle at top left, rgba(246,133,31,.16), transparent 26%),
    radial-gradient(circle at top right, rgba(31,158,188,.18), transparent 25%),
    linear-gradient(180deg, #f7fafc 0%, #eef4f8 46%, #f6f9fb 100%);
  color:var(--navy);
  line-height:1.55;
  min-height:100vh;
}
body::before{
  content:'';
  position:fixed;
  inset:0;
  background:
    linear-gradient(135deg, rgba(1,48,70,.05) 0%, transparent 28%),
    repeating-linear-gradient(135deg, rgba(1,48,70,.025) 0, rgba(1,48,70,.025) 1px, transparent 1px, transparent 22px);
  pointer-events:none;
  z-index:-1;
}
.wrap{max-width:1360px;margin:0 auto;padding:28px 18px 56px}
header.hero{
  display:grid;
  grid-template-columns:minmax(0,1.55fr) minmax(280px,.95fr);
  gap:18px;
  align-items:stretch;
  background:linear-gradient(145deg, rgba(1,48,70,.98), rgba(10,69,97,.94));
  border-radius:30px;
  padding:26px 28px;
  margin-bottom:20px;
  box-shadow:var(--shadow);
  color:#fff;
  overflow:hidden;
  position:relative;
}
header.hero::after{
  content:'';
  position:absolute;
  inset:auto -8% -35% auto;
  width:280px;
  height:280px;
  background:radial-gradient(circle, rgba(253,183,20,.22) 0%, rgba(253,183,20,0) 70%);
  pointer-events:none;
}
.hero-copy{position:relative;z-index:1}
.eyebrow{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:7px 12px;
  border-radius:999px;
  background:rgba(255,255,255,.11);
  border:1px solid rgba(255,255,255,.14);
  color:#dcedf6;
  font-size:.72rem;
  letter-spacing:.08em;
  text-transform:uppercase;
  font-weight:600;
  margin-bottom:14px;
}
header.hero h1{font-size:clamp(2rem,3vw,3rem);font-weight:700;line-height:1.05;max-width:12ch}
header.hero .sub{color:#d7e5ee;font-size:.96rem;max-width:60ch;margin-top:12px}
.hero-note{margin-top:16px;color:#b8cddd;font-size:.84rem}
.hero-meta{
  display:grid;
  gap:12px;
  align-content:stretch;
  position:relative;
  z-index:1;
}
.hero-pill{
  display:flex;
  flex-direction:column;
  justify-content:center;
  gap:4px;
  min-height:88px;
  padding:16px 18px;
  border-radius:22px;
  background:linear-gradient(135deg, rgba(255,255,255,.12), rgba(255,255,255,.06));
  border:1px solid rgba(255,255,255,.12);
  backdrop-filter:blur(8px);
}
.hero-pill span{font-size:.73rem;text-transform:uppercase;letter-spacing:.08em;color:#c2d6e2;font-weight:600}
.hero-pill strong{font-size:1.05rem;font-weight:600;color:#fff}
.tab-row{
  position:sticky;
  top:12px;
  z-index:8;
  display:flex;
  gap:8px;
  margin-bottom:18px;
  padding:10px;
  flex-wrap:wrap;
  border:1px solid rgba(255,255,255,.66);
  border-radius:22px;
  background:rgba(255,255,255,.74);
  box-shadow:0 14px 32px rgba(1,48,70,.08);
  backdrop-filter:blur(18px);
}
.tab-btn{
  padding:10px 16px;
  font-size:.82rem;
  font-weight:600;
  cursor:pointer;
  border:none;
  border-radius:999px;
  background:transparent;
  color:#5f7180;
  transition:all .18s ease;
}
.tab-btn:hover{background:#eef4f8;color:var(--navy)}
.tab-btn.active{
  background:linear-gradient(135deg, var(--navy), var(--navy-2));
  color:#fff;
  box-shadow:0 8px 20px rgba(1,48,70,.22);
}
.tab-content{display:none}
.tab-content.active{display:block}
.kpi-row{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:14px;
  margin-bottom:18px;
}
.kpi{
  position:relative;
  overflow:hidden;
  background:linear-gradient(180deg, rgba(255,255,255,.98), rgba(244,248,251,.94));
  border:1px solid rgba(1,48,70,.08);
  border-radius:24px;
  padding:18px 18px 16px;
  box-shadow:0 12px 28px rgba(1,48,70,.07);
}
.kpi::before{
  content:'';
  position:absolute;
  inset:0 0 auto 0;
  height:4px;
  background:linear-gradient(90deg, var(--orange), var(--gold));
}
.kpi:nth-child(2)::before{background:linear-gradient(90deg, var(--teal), var(--sky))}
.kpi:nth-child(3)::before{background:linear-gradient(90deg, var(--navy), var(--sky))}
.kpi:nth-child(4)::before{background:linear-gradient(90deg, var(--teal), #5fb8d0)}
.kpi:nth-child(5)::before{background:linear-gradient(90deg, var(--gold), var(--orange-soft))}
.kpi:nth-child(6)::before{background:linear-gradient(90deg, #c2410c, #991b1b)}
.kpi .lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#6a7b88;font-weight:700}
.kpi .val{font-size:1.7rem;font-weight:700;margin-top:8px;line-height:1.05}
.kpi .note{font-size:.77rem;color:#7f8f9a;margin-top:8px}
.dashboard-grid{
  display:grid;
  grid-template-columns:repeat(12,minmax(0,1fr));
  gap:16px;
}
.card{
  position:relative;
  grid-column:span 12;
  background:linear-gradient(180deg, rgba(255,255,255,.98), rgba(246,249,252,.92));
  border:1px solid rgba(1,48,70,.08);
  border-radius:26px;
  padding:22px 22px 18px;
  box-shadow:0 18px 36px rgba(1,48,70,.08);
  overflow:hidden;
}
.card::before{
  content:'';
  position:absolute;
  inset:0 0 auto 0;
  height:1px;
  background:linear-gradient(90deg, rgba(246,133,31,.75), rgba(31,158,188,.35), rgba(1,48,70,0));
}
.card-half{grid-column:span 6}
.card-wide{grid-column:span 8}
.card-narrow{grid-column:span 4}
.card h2{font-size:1.08rem;font-weight:650;margin-bottom:4px;color:var(--navy)}
.card .sub{font-size:.81rem;color:#667887;margin-bottom:14px;max-width:72ch}
.card-source{font-size:.7rem;color:#6f8190;margin-top:12px}
.card-source a{color:#55748a;text-decoration:underline}
.controls{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;margin-bottom:12px}
.range-row{display:flex;gap:6px;flex-wrap:wrap}
.rbtn{
  padding:6px 12px;
  border:1px solid var(--border);
  border-radius:999px;
  background:#f7fafc;
  font-size:.72rem;
  font-weight:600;
  cursor:pointer;
  color:#6a7b88;
  transition:all .15s ease;
}
.rbtn:hover{background:#eef4f8;border-color:#c6d5df;color:var(--navy)}
.rbtn.active{
  background:linear-gradient(135deg, var(--navy), var(--navy-2));
  color:#fff;
  border-color:transparent;
  box-shadow:0 10px 22px rgba(1,48,70,.18);
}
.ms-wrap{position:relative;display:inline-block}
.ms-btn{
  padding:7px 12px;
  border:1px solid var(--border);
  border-radius:12px;
  background:#f8fbfd;
  font-size:.78rem;
  cursor:pointer;
  color:var(--navy);
  min-width:154px;
  text-align:left;
  font-weight:600;
}
.ms-btn::after{content:'▾';float:right;margin-left:8px;color:#8a9ba6}
.ms-panel{
  display:none;
  position:absolute;
  right:0;
  z-index:20;
  background:#fff;
  border:1px solid var(--border);
  border-radius:16px;
  padding:10px 12px;
  max-height:320px;
  overflow-y:auto;
  min-width:250px;
  box-shadow:0 18px 42px rgba(1,48,70,.18);
  margin-top:6px;
}
.ms-panel.open{display:block}
.ms-actions{padding:2px 0 8px;border-bottom:1px solid #edf3f7;margin-bottom:8px;font-size:.75rem}
.ms-actions a{color:var(--teal);text-decoration:none;cursor:pointer;font-weight:600}
.ms-item{display:flex;align-items:center;gap:7px;padding:4px 0;font-size:.78rem;cursor:pointer;color:#27485a}
.ms-item input{accent-color:var(--navy)}
.ms-dot{width:10px;height:10px;border-radius:3px;flex-shrink:0}
.tbl-wrap{max-height:440px;overflow-y:auto;border:1px solid var(--border);border-radius:16px;margin-top:10px;background:#fff}
.tbl-wrap table{width:100%;border-collapse:collapse;font-size:.79rem}
.tbl-wrap thead{position:sticky;top:0;z-index:2}
.tbl-wrap th{
  background:linear-gradient(180deg, #f5f9fc, #eef4f8);
  padding:10px 12px;
  text-align:left;
  font-weight:700;
  border-bottom:1px solid var(--border);
  white-space:nowrap;
}
.tbl-wrap td{padding:8px 12px;border-bottom:1px solid #edf3f7}
.tbl-wrap tr:nth-child(even){background:#f9fbfd}
.num{text-align:right;font-variant-numeric:tabular-nums}
.export-btn{
  position:absolute;
  top:14px;
  right:14px;
  padding:6px 11px;
  border:1px solid var(--border);
  border-radius:999px;
  background:rgba(255,255,255,.92);
  font-size:.7rem;
  font-weight:700;
  cursor:pointer;
  color:#627684;
  transition:all .15s ease;
  z-index:5;
}
.export-btn:hover{background:var(--navy);color:#fff;border-color:var(--navy)}
.narrative{
  padding:14px 16px;
  border:1px solid rgba(246,133,31,.18);
  border-left:4px solid var(--orange);
  border-radius:16px;
  margin-bottom:12px;
  font-size:.82rem;
  line-height:1.65;
  background:linear-gradient(180deg, #fffdfa, #fff7ef);
}
.narrative .ndate{font-weight:700;font-size:.74rem;color:#7a8e9a;margin-bottom:6px;text-transform:uppercase;letter-spacing:.06em}
#loading{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:12px;
  padding:76px 24px;
  color:#6f8190;
}
.spinner{display:inline-block;width:38px;height:38px;border:3px solid #d6e2ea;border-top-color:var(--navy);border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.68rem;font-weight:600}
.badge-ok{background:#dcfce7;color:#166534}
.badge-warn{background:#fef3c7;color:#92400e}
.badge-err{background:#fee2e2;color:#991b1b}
.badge-na{background:#f1f5f9;color:#64748b}
footer{text-align:center;padding:26px 14px 0;color:#7b8c97;font-size:.72rem}
.up{color:var(--orange)}.dn{color:var(--teal)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
canvas{position:relative;z-index:1}
@media(max-width:1080px){
  header.hero{grid-template-columns:1fr}
  .card-half,.card-wide,.card-narrow{grid-column:span 12}
}
@media(max-width:768px){
  .wrap{padding:18px 14px 40px}
  header.hero{padding:22px 20px;border-radius:24px}
  header.hero h1{max-width:none}
  .tab-row{top:8px}
  .kpi-row{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
  .grid-2{grid-template-columns:1fr}
  .card{padding:18px 16px 16px;border-radius:22px}
}
</style>
</head>
<body>
<div class="wrap">
<header class="hero">
<div class="hero-copy">
<div class="eyebrow">Eggs • Broilers • Feed • HPAI</div>
<h1>Poultry Intelligence Dashboard</h1>
<div class="sub">A cleaner read on egg, broiler, macro, and disease signals using USDA MARS, NASS, APHIS, FRED, and BLS source data.</div>
<div class="hero-note">Last updated __UPDATED__. Chart exports, source downloads, and a built-in data quality view stay available below.</div>
</div>
<div class="hero-meta">
<div class="hero-pill"><span>Updated</span><strong>__UPDATED__</strong></div>
<div class="hero-pill"><span>Coverage</span><strong id="heroCoverage">Loading source coverage...</strong></div>
<div class="hero-pill"><span>Data Health</span><strong id="heroHealth">Checking freshness...</strong></div>
</div>
</header>

<!-- Loading -->
<div id="loading"><div class="spinner"></div><div style="margin-top:12px">Loading data...</div></div>

<!-- Tabs -->
<div class="tab-row">
<button class="tab-btn active" data-tab="landing">Overview</button>
<button class="tab-btn" data-tab="eggs">Eggs</button>
<button class="tab-btn" data-tab="broilers">Broilers</button>
<button class="tab-btn" data-tab="macro">Macro</button>
<button class="tab-btn" data-tab="quality">Data Quality</button>
</div>

<!-- ═══ TAB: Landing Overview ═══ -->
<div id="tab-landing" class="tab-content active">

<!-- KPI Row -->
<div class="kpi-row">
<div class="kpi"><div class="lbl">Shell Egg Index</div><div class="val" id="kpiEggPrice" style="color:#F6851F">—</div><div class="note" id="kpiEggDate"></div></div>
<div class="kpi"><div class="lbl">Week-over-Week</div><div class="val" id="kpiWoW">—</div><div class="note">vs prior week</div></div>
<div class="kpi"><div class="lbl">Breast B/S</div><div class="val" id="kpiBreast" style="color:#013046">—</div><div class="note" id="kpiBreastDate"></div></div>
<div class="kpi"><div class="lbl">Layer Inventory</div><div class="val" id="kpiLayers" style="color:#1F9EBC">—</div><div class="note" id="kpiLayerPeriod"></div></div>
<div class="kpi"><div class="lbl">Corn ($/mt)</div><div class="val" id="kpiCorn" style="color:#FDB714">—</div><div class="note" id="kpiCornDate"></div></div>
<div class="kpi"><div class="lbl">HPAI (30d)</div><div class="val" id="kpiHpai" style="color:#991b1b">—</div><div class="note" id="kpiHpaiBirds"></div></div>
</div>

<div class="dashboard-grid">
<div class="card card-wide">
<h2>Wholesale Egg Prices</h2>
<div class="sub">Daily Shell Egg Index (¢/dozen)</div>
<canvas id="landingEggChart" height="100"></canvas>
</div>
<div class="card card-narrow">
<h2>HPAI Detections</h2>
<div class="sub">Monthly commercial flock detections</div>
<canvas id="landingHpaiChart" height="100"></canvas>
</div>

<div class="card">
<h2>Market Commentary</h2>
<div class="sub">Latest Shell Egg Index report narratives</div>
<div id="narrativeBox"></div>
</div>
</div>

</div><!-- /tab-landing -->

<!-- ═══ TAB: Eggs ═══ -->
<div id="tab-eggs" class="tab-content">

<div class="dashboard-grid">
<div class="card">
<h2>Wholesale Egg Prices</h2>
<div class="sub">Daily national wholesale prices — Shell Egg Index, NY Shell Egg, Breaking Stock (¢/dozen)</div>
<div class="controls">
<div class="range-row" data-chart="eggIdx">
<button class="rbtn" data-r="30d">30D</button><button class="rbtn" data-r="3m">3M</button><button class="rbtn" data-r="6m">6M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
<div class="ms-wrap">
<button class="ms-btn" id="eggMSBtn">Series</button>
<div class="ms-panel" id="eggMSPanel"></div>
</div>
</div>
<canvas id="eggIdxChart" height="120"></canvas>
<div class="card-source">Source: USDA AMS MARS — <a href="data/shell_egg_index.csv">Shell Egg Index CSV</a> · <a href="data/ny_shell_egg.csv">NY Egg CSV</a> · <a href="data/breaking_stock.csv">Breaking Stock CSV</a></div>
</div>

<div class="card">
<h2>Cage-Free vs Conventional Spread</h2>
<div class="sub">Cage-Free minus Caged Shell Egg Index (¢/dozen)</div>
<div class="controls">
<div class="range-row" data-chart="cfSpread">
<button class="rbtn" data-r="30d">30D</button><button class="rbtn" data-r="3m">3M</button><button class="rbtn" data-r="6m">6M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
</div>
<canvas id="cfSpreadChart" height="80"></canvas>
<div class="card-source">Source: USDA AMS MARS Shell Egg Index (slug 2843)</div>
</div>

<div class="card card-half">
<h2>Shell Egg Trading Volume</h2>
<div class="sub">Daily national trading volume (cases)</div>
<div class="controls">
<div class="range-row" data-chart="eggVol">
<button class="rbtn" data-r="30d">30D</button><button class="rbtn" data-r="3m">3M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
</div>
<canvas id="eggVolChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Regional Egg Prices</h2>
<div class="sub">Weekly combined regional shell egg (Large class, ¢/dozen)</div>
<div class="controls">
<div class="range-row" data-chart="regional">
<button class="rbtn" data-r="3m">3M</button><button class="rbtn" data-r="6m">6M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
</div>
<canvas id="regionalChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Layer Inventory</h2>
<div class="sub">Monthly U.S. layers on hand (million head)</div>
<div class="controls">
<div class="range-row" data-chart="nassLayers">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassLayersChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Egg Production</h2>
<div class="sub">Monthly U.S. egg production (billion eggs)</div>
<div class="controls">
<div class="range-row" data-chart="nassEggProd">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassEggProdChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Rate of Lay — Table Layers</h2>
<div class="sub">Monthly eggs per 100 table layers per day (NASS)</div>
<div class="controls">
<div class="range-row" data-chart="nassRol">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassRolChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Replacement Pullet Inventory</h2>
<div class="sub">Monthly U.S. replacement pullets (million head)</div>
<div class="controls">
<div class="range-row" data-chart="nassPullets">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassPulletsChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Shell Egg Inventory</h2>
<div class="sub">Weekly national shell egg inventory by region (cases)</div>
<div class="controls">
<div class="range-row" data-chart="eggInv">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="eggInvChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Eggs Processed</h2>
<div class="sub">Weekly eggs processed by class (cases)</div>
<div class="controls">
<div class="range-row" data-chart="eggsProc">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="eggsProcChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Retail Egg Prices by Environment</h2>
<div class="sub">Weekly national retail egg prices (Large White, $/dozen)</div>
<div class="controls">
<div class="range-row" data-chart="retailEgg">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="retailEggChart" height="100"></canvas>
<div class="card-source">Source: USDA AMS MARS — <a href="data/retail_egg_prices.csv">Download CSV</a></div>
</div>

<div class="card card-half">
<h2>Egg Feature Activity</h2>
<div class="sub">Weekly national retail egg feature rate (%)</div>
<div class="controls">
<div class="range-row" data-chart="eggFeat">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="eggFeatChart" height="80"></canvas>
</div>

</div>

</div><!-- /tab-eggs -->

<!-- ═══ TAB: Broilers ═══ -->
<div id="tab-broilers" class="tab-content">

<div class="dashboard-grid">
<div class="card">
<h2>Wholesale Chicken Cut Prices</h2>
<div class="sub">Weekly national wholesale chicken prices by cut (¢/lb)</div>
<div class="controls">
<div class="range-row" data-chart="chxWhole">
<button class="rbtn" data-r="3m">3M</button><button class="rbtn" data-r="6m">6M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
<div class="ms-wrap">
<button class="ms-btn" id="chxMSBtn">Top cuts</button>
<div class="ms-panel" id="chxMSPanel"></div>
</div>
</div>
<canvas id="chxWholeChart" height="100"></canvas>
<div class="card-source">Source: USDA AMS MARS — <a href="data/chicken_wholesale_weekly.csv">Download CSV</a></div>
</div>

<div class="card card-half">
<h2>Wholesale Chicken Volume</h2>
<div class="sub">Weekly national wholesale chicken trading volume by cut (loads)</div>
<div class="controls">
<div class="range-row" data-chart="chxVol">
<button class="rbtn" data-r="3m">3M</button><button class="rbtn" data-r="6m">6M</button><button class="rbtn active" data-r="1y">1Y</button><button class="rbtn" data-r="all">All</button>
</div>
</div>
<canvas id="chxVolChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Broiler Placements</h2>
<div class="sub">Weekly U.S. broiler placements (million head)</div>
<div class="controls">
<div class="range-row" data-chart="nassPlace">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassPlaceChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Hatchery</h2>
<div class="sub">Monthly chicks hatched and eggs set (million head)</div>
<div class="controls">
<div class="range-row" data-chart="nassHatch">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassHatchChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>NASS Prices Received</h2>
<div class="sub">Monthly: eggs ($/dozen) and broilers ($/lb)</div>
<div class="controls">
<div class="range-row" data-chart="nassPrices">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="nassPricesChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Cold Storage — Weekly</h2>
<div class="sub">Weekly MARS cold storage holdings (million lbs)</div>
<div class="controls">
<div class="range-row" data-chart="coldMars">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="coldMarsChart" height="100"></canvas>
</div>
<div class="card card-half">
<h2>Cold Storage — Monthly (NASS)</h2>
<div class="sub">Monthly NASS cold storage stocks (million lbs)</div>
<div class="controls">
<div class="range-row" data-chart="coldNass">
<button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="coldNassChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Retail Chicken Prices</h2>
<div class="sub">Weekly national retail chicken prices by cut (conventional, $/lb)</div>
<div class="controls">
<div class="range-row" data-chart="retailChx">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="retailChxChart" height="100"></canvas>
</div>

<div class="card card-half">
<h2>Chicken Feature Activity</h2>
<div class="sub">Weekly national retail chicken feature rate (%)</div>
<div class="controls">
<div class="range-row" data-chart="chxFeat">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="chxFeatChart" height="80"></canvas>
</div>

</div>

</div><!-- /tab-broilers -->

<!-- ═══ TAB: Macro ═══ -->
<div id="tab-macro" class="tab-content">

<div class="dashboard-grid">
<div class="card card-half">
<h2>Feed Ingredient Costs</h2>
<div class="sub">Global corn and soybean meal prices ($/metric ton, FRED)</div>
<div class="controls">
<div class="range-row" data-chart="feedCosts">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn" data-r="3y">3Y</button><button class="rbtn" data-r="5y">5Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="feedCostsChart" height="100"></canvas>
<div class="card-source">Source: FRED (World Bank Commodity Prices)</div>
</div>

<div class="card card-half">
<h2>Layer Feed Cost Index</h2>
<div class="sub">Composite feed cost index (67% corn + 22% SBM, base=100)</div>
<canvas id="feedIndexChart" height="100"></canvas>
<div class="card-source">Derived from FRED corn + SBM prices</div>
</div>
<div class="card card-half">
<h2>Feed Ratios</h2>
<div class="sub">Egg/feed and broiler/feed price ratios</div>
<canvas id="feedRatioChart" height="100"></canvas>
<div class="card-source">NASS prices received / FRED feed cost composite</div>
</div>

<div class="card card-half">
<h2>HPAI Detection Timeline</h2>
<div class="sub">Monthly HPAI commercial flock detections and birds affected</div>
<div class="controls">
<div class="range-row" data-chart="hpaiTimeline">
<button class="rbtn" data-r="1y">1Y</button><button class="rbtn active" data-r="all">All</button>
</div>
</div>
<canvas id="hpaiTimelineChart" height="100"></canvas>
<div class="card-source">Source: USDA APHIS — <a href="data/hpai_detections.csv">Download CSV</a></div>
</div>

<div class="card card-half">
<h2>HPAI Detections by State</h2>
<div class="sub">Top 15 states by birds affected (all time)</div>
<canvas id="hpaiStateChart" height="120"></canvas>
</div>

<div class="card card-half">
<h2>Cross-Protein CPI Comparison</h2>
<div class="sub">BLS average retail prices: eggs, chicken ($/dozen, $/lb)</div>
<canvas id="crossProteinChart" height="100"></canvas>
<div class="card-source">Source: BLS Consumer Price Index</div>
</div>

<div class="card">
<h2>PPI: Poultry Products</h2>
<div class="sub">Producer Price Index for eggs and chicken (FRED)</div>
<canvas id="ppiChart" height="100"></canvas>
<div class="card-source">Source: FRED (BLS PPI via FRED)</div>
</div>

</div>

</div><!-- /tab-macro -->

<!-- ═══ TAB: Data Quality ═══ -->
<div id="tab-quality" class="tab-content">

<div class="dashboard-grid">
<div class="card">
<h2>Data Source Freshness</h2>
<div class="sub">Last fetch status for each data source and series</div>
<div class="tbl-wrap">
<table>
<thead><tr><th>Source</th><th>Series/Slug</th><th>Last Fetch</th><th>Latest Data</th><th class="num">Rows</th><th>Status</th></tr></thead>
<tbody id="freshnessBody"></tbody>
</table>
</div>
</div>

<div class="card">
<h2>Data Coverage Summary</h2>
<div class="sub">Active tables and their date ranges</div>
<div class="grid-2">
<div>
<h3 style="font-size:.85rem;margin-bottom:8px">USDA Sources</h3>
<div id="coverageUsda"></div>
</div>
<div>
<h3 style="font-size:.85rem;margin-bottom:8px">Non-USDA Sources</h3>
<div id="coverageOther"></div>
</div>
</div>
</div>

<div class="card">
<h2>API Key Status</h2>
<div class="sub">Required API keys and their availability</div>
<div id="apiKeyStatus"></div>
</div>

</div>

</div><!-- /tab-quality -->

<footer>Data sourced from USDA AMS MARS, USDA NASS QuickStats, USDA APHIS, FRED, and BLS. Dashboard updated __UPDATED__.</footer>
</div><!-- /wrap -->

<script>
/* ═══ Globals ═══ */
let D=null;
const charts={};
const ranges={};
const PAGE_SIZE=100;

const COLORS_ENV={'Caged':'#F6851F','Cage-Free':'#1F9EBC','Free-Range':'#013046','Pasture-Raised':'#FDB714','USDA Organic':'#8FCAE6','USDA Organic Free-Range':'#939598','Conventional':'#F6851F'};
const COLORS_EGG={'Caged':'#F6851F','Cage-Free':'#1F9EBC','NY Large':'#013046','NY Medium':'#8FCAE6','NY Extra Large':'#939598','Breaking Stock':'#FDB714','Undergrades':'#E5700A'};
const DEFAULT_EGG_SERIES=['Caged','Cage-Free','NY Large','Breaking Stock'];
const COLORS_REG={'National':'#013046','Northeast':'#F6851F','Northeast (NE)':'#F6851F','Midwest':'#1F9EBC','Midwest (MW)':'#1F9EBC','South Central':'#FDB714','South Central (SC)':'#FDB714','Southeast':'#8FCAE6','Southeast (SE)':'#8FCAE6','Southwest':'#939598','Northwest':'#E5700A','Northwest (NW)':'#E5700A'};
const COLORS_SEQ=['#F6851F','#1F9EBC','#013046','#FDB714','#8FCAE6','#939598','#E5700A','#D4920E','#3DB3CF','#0A4A6B','#FAB87B','#165E7A','#78C4DC','#5DB8D4','#B0D9ED'];
const TOP_CUTS=['Breast - B/S','Wings - Whole','Leg quarters - Bulk','Thighs - B/S','WOG'];

/* ═══ Helpers ═══ */
Chart.defaults.font.family='Lexend';
Chart.defaults.color='#013046';
Chart.defaults.plugins.legend.labels.usePointStyle=true;
Chart.defaults.plugins.legend.labels.pointStyle='line';
Chart.defaults.plugins.tooltip.backgroundColor='rgba(1, 48, 70, 0.92)';
Chart.defaults.plugins.tooltip.titleColor='#ffffff';
Chart.defaults.plugins.tooltip.bodyColor='#e8f1f6';
Chart.defaults.plugins.tooltip.padding=12;
Chart.defaults.plugins.tooltip.cornerRadius=12;

function fmtNum(v,d=0){if(v==null)return '—';return v.toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d})}
function fmtM(v){if(v==null)return '—';if(Math.abs(v)>=1e9)return (v/1e9).toFixed(1)+'B';if(Math.abs(v)>=1e6)return (v/1e6).toFixed(1)+'M';if(Math.abs(v)>=1e3)return (v/1e3).toFixed(0)+'K';return v.toFixed(0)}
function fmtDate(d){if(!d)return '';const p=d.split('-');if(p.length===3)return p[1]+'/'+p[2]+'/'+p[0];if(p.length===2)return d;return d}
const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function fmtYM(d){if(!d)return d;const p=d.split('-');if(p.length>=2&&p[0].length===4){const mi=parseInt(p[1],10)-1;if(mi>=0&&mi<12)return MON[mi]+'-'+p[0].slice(2)}return d}
function fmtPrice(v){if(v==null)return '—';return '$'+v.toFixed(2)}

function cutoffISO(range){
  const n=new Date();
  let d;
  switch(range){
    case '30d':d=new Date(n.getFullYear(),n.getMonth(),n.getDate()-30);break;
    case '3m':d=new Date(n.getFullYear(),n.getMonth()-3,n.getDate());break;
    case '6m':d=new Date(n.getFullYear(),n.getMonth()-6,n.getDate());break;
    case '1y':d=new Date(n.getFullYear()-1,n.getMonth(),n.getDate());break;
    case '3y':d=new Date(n.getFullYear()-3,n.getMonth(),n.getDate());break;
    case '5y':d=new Date(n.getFullYear()-5,n.getMonth(),n.getDate());break;
    case 'ytd':d=new Date(n.getFullYear(),0,1);break;
    default:d=new Date(2000,0,1);
  }
  return d.toISOString().slice(0,10);
}

function filterByRange(dates,range){
  const c=cutoffISO(range);
  const start=dates.findIndex(d=>d>=c);
  return start<0?[dates.length,dates.length]:[start,dates.length];
}

function ds(label,data,color,opts={}){
  return Object.assign({
    label,
    data,
    borderColor:color,
    backgroundColor:color+'26',
    fill:false,
    pointRadius:0,
    pointHoverRadius:4,
    pointHoverBackgroundColor:color,
    pointHoverBorderColor:'#fff',
    pointHoverBorderWidth:2,
    borderWidth:2.5,
    tension:.32,
    spanGaps:true
  },opts);
}

/* ═══ Logo + PNG export ═══ */
const logoImg=new Image();
logoImg.crossOrigin='anonymous';
logoImg.src='iaa-logo-with-navy-font-full-color.png';

function exportChart(btn){
  const card=btn.closest('.card');
  if(!card)return;
  const canvas=card.querySelector('canvas');
  if(!canvas)return;
  const chart=charts[canvas.id];
  if(!chart)return;
  // Text content
  const h2=card.querySelector('h2');
  const sub=card.querySelector('.sub');
  const title=h2?h2.textContent:'Chart';
  const subtitle=sub?sub.textContent:'';
  const fname=title.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/_+$/,'')+'.png';
  // Re-render chart at fixed high DPR for crisp export
  const origDpr=chart.options.devicePixelRatio;
  const exportDpr=3;
  chart.options.devicePixelRatio=exportDpr;
  chart.resize();
  // Now canvas is rendered at exportDpr — grab dimensions
  const cw=canvas.width,ch=canvas.height;
  // Layout
  const padL=80,padR=80,padTop=70,padBot=50;
  const titleSize=56,subSize=32,titleGap=14;
  const headerH=titleSize+(subtitle?subSize+titleGap:0)+30;
  const logoH=100;
  // Ensure logo top is at least 20px below chart bottom
  const minBot=logoH+20+20; // logo height + 20px edge margin + 20px gap
  const finalPadBot=Math.max(padBot,minBot);
  const W=cw+padL+padR;
  const H=padTop+headerH+ch+finalPadBot;
  const exp=document.createElement('canvas');
  exp.width=W;exp.height=H;
  const ctx=exp.getContext('2d');
  // White background
  ctx.fillStyle='#fff';
  ctx.fillRect(0,0,W,H);
  // Title
  let ty=padTop+titleSize;
  ctx.fillStyle='#013046';
  ctx.font='600 '+titleSize+'px Lexend,sans-serif';
  ctx.fillText(title,padL,ty);
  // Subtitle
  if(subtitle){
    ty+=subSize+titleGap;
    ctx.fillStyle='#939598';
    ctx.font='400 '+subSize+'px Lexend,sans-serif';
    ctx.fillText(subtitle,padL,ty);
  }
  // Chart at native size
  const chartY=padTop+headerH;
  ctx.drawImage(canvas,padL,chartY);
  // Logo — bottom-right corner, 20px from edges
  if(logoImg.complete&&logoImg.naturalWidth>0){
    const lw=logoH*(logoImg.naturalWidth/logoImg.naturalHeight);
    ctx.globalAlpha=0.8;
    ctx.drawImage(logoImg,W-lw-20,H-logoH-20,lw,logoH);
    ctx.globalAlpha=1.0;
  }
  // Download
  const a=document.createElement('a');
  a.download=fname;
  a.href=exp.toDataURL('image/png');
  a.click();
  // Restore original DPR and re-render
  chart.options.devicePixelRatio=origDpr||undefined;
  chart.resize();
}

/* ═══ Chart factory ═══ */
function makeLineChart(canvasId,datasets,labels,yLabel,opts={}){
  const ctx=document.getElementById(canvasId);
  if(!ctx)return null;
  if(charts[canvasId]){charts[canvasId].destroy()}
  const cfg={
    type:'line',
    data:{labels,datasets},
    options:{
      responsive:true,
      aspectRatio:opts.aspect||1.7,
      maintainAspectRatio:true,
      normalized:true,
      layout:{padding:{top:4,right:8,bottom:8,left:2}},
      interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{display:datasets.length>1,position:'bottom',align:'start',labels:{boxWidth:30,padding:16,font:{size:12,weight:'600'}}},
        annotation:opts.annotations?{annotations:opts.annotations}:undefined
      },
      scales:{
        x:{
          ticks:{maxTicksToDisplay:5,autoSkip:true,autoSkipPadding:72,maxRotation:0,padding:8,font:{size:12},color:'#627684',callback:function(v){const l=this.getLabelForValue(v);return fmtYM(l)}},
          border:{display:false},
          grid:{color:'rgba(1,48,70,0.05)',drawTicks:false}
        },
        y:{
          title:{display:!!yLabel,text:yLabel,font:{size:12,weight:'600'},color:'#5f7180'},
          ticks:{padding:8,font:{size:12},color:'#627684'},
          border:{display:false},
          grid:{color:'rgba(1,48,70,0.07)'}
        }
      },
      elements:{point:{radius:0,hitRadius:10},line:{tension:.32,borderWidth:2.5,capBezierPoints:true}}
    }
  };
  if(opts.y2){
    cfg.options.scales.y2={
      position:'right',
      title:{display:true,text:opts.y2,font:{size:12,weight:'600'},color:'#5f7180'},
      ticks:{font:{size:12},color:'#627684'},
      border:{display:false},
      grid:{drawOnChartArea:false}
    };
  }
  charts[canvasId]=new Chart(ctx,cfg);
  return charts[canvasId];
}

function makeBarChart(canvasId,datasets,labels,yLabel,opts={}){
  const ctx=document.getElementById(canvasId);
  if(!ctx)return null;
  if(charts[canvasId]){charts[canvasId].destroy()}
  charts[canvasId]=new Chart(ctx,{
    type:'bar',
    data:{labels,datasets},
    options:{
      responsive:true,indexAxis:opts.horizontal?'y':'x',
      aspectRatio:opts.aspect||1.7,
      maintainAspectRatio:true,
      normalized:true,
      layout:{padding:{top:4,right:8,bottom:8,left:2}},
      interaction:{mode:'index',intersect:false},
      plugins:{legend:{display:datasets.length>1,position:'bottom',align:'start',labels:{boxWidth:30,padding:16,font:{size:12,weight:'600'}}}},
      scales:{
        x:{
          ticks:{maxTicksToDisplay:5,autoSkip:true,autoSkipPadding:72,maxRotation:0,padding:8,font:{size:12},color:'#627684',callback:function(v){const l=this.getLabelForValue(v);return fmtYM(l)}},
          border:{display:false},
          grid:{drawOnChartArea:false,drawTicks:false},
          stacked:!!opts.stacked
        },
        y:{
          title:{display:!!yLabel,text:yLabel,font:{size:12,weight:'600'},color:'#5f7180'},
          ticks:{padding:8,font:{size:12},color:'#627684'},
          border:{display:false},
          grid:{color:'rgba(1,48,70,0.07)'},
          stacked:!!opts.stacked
        }
      }
    }
  });
  return charts[canvasId];
}

/* ═══ Landing page ═══ */
function initLanding(){
  // Mini egg index chart (last 90 days)
  const d=D.egg_index;
  if(d&&d.dates.length){
    const[s,e]=filterByRange(d.dates,'3m');
    const labels=d.dates.slice(s,e).map(fmtDate);
    const datasets=[];
    if(d.series['Caged'])datasets.push(ds('Caged',d.series['Caged'].slice(s,e),'#F6851F'));
    if(d.series['Cage-Free'])datasets.push(ds('Cage-Free',d.series['Cage-Free'].slice(s,e),'#1F9EBC'));
    makeLineChart('landingEggChart',datasets,labels,'¢ / dozen',{aspect:2,xLabel:'Date'});
  }
  // Mini HPAI chart
  const h=D.hpai_summary;
  if(h&&h.dates.length){
    makeBarChart('landingHpaiChart',
      [ds('Detections',h.detections,'#991b1b',{backgroundColor:'#991b1b80'})],
      h.dates,'Detections',{aspect:2,xLabel:'Month'});
  }
  renderNarratives();
}

/* ═══ Egg tab updates ═══ */
let eggSelected=new Set(DEFAULT_EGG_SERIES);

function initEggMS(){
  const items=Object.keys(D.egg_index.series).sort();
  const panel=document.getElementById('eggMSPanel');
  panel.innerHTML=`<div class="ms-actions"><a onclick="eggSelectAll()">All</a> · <a onclick="eggClear()">Clear</a></div>`+
    items.map(item=>{
      const chk=eggSelected.has(item)?'checked':'';
      const c=COLORS_EGG[item]||COLORS_SEQ[0];
      return `<label class="ms-item"><input type="checkbox" value="${item}" ${chk} onchange="onEggCheck()"><span class="ms-dot" style="background:${c}"></span><span>${item}</span></label>`;
    }).join('');
  updateEggBtn();
}

function getEggSelected(){return Array.from(document.querySelectorAll('#eggMSPanel input:checked')).map(b=>b.value)}
function onEggCheck(){eggSelected=new Set(getEggSelected());updateEggIdx(ranges.eggIdx||'1y');updateEggBtn()}
function eggSelectAll(){document.querySelectorAll('#eggMSPanel input').forEach(b=>b.checked=true);onEggCheck()}
function eggClear(){document.querySelectorAll('#eggMSPanel input').forEach(b=>b.checked=false);onEggCheck()}
function updateEggBtn(){
  const n=getEggSelected().length,t=Object.keys(D.egg_index.series).length;
  document.getElementById('eggMSBtn').textContent=n===t?'All series':n===0?'None':n+' series';
}

function updateEggIdx(range){
  const d=D.egg_index;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const sel=getEggSelected();
  const datasets=sel.map(k=>ds(k,(d.series[k]||[]).slice(s,e),COLORS_EGG[k]||COLORS_SEQ[0]));
  makeLineChart('eggIdxChart',datasets,labels,'¢ / dozen',{xLabel:'Date'});
}

function updateCfSpread(range){
  const d=D.cage_free_spread;
  if(!d||!d.dates.length)return;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  makeLineChart('cfSpreadChart',
    [ds('Cage-Free',d.cage_free.slice(s,e),'#1F9EBC'),
     ds('Caged',d.caged.slice(s,e),'#F6851F'),
     ds('Spread',d.spread.slice(s,e),'#013046',{borderDash:[5,3]})],
    labels,'¢ / dozen',{aspect:2,xLabel:'Date'});
}

function updateEggVol(range){
  const d=D.egg_volumes;
  const[s,e]=filterByRange(d.dates,range);
  makeBarChart('eggVolChart',
    [ds('Volume',d.volume.slice(s,e),'#1F9EBC',{backgroundColor:'#1F9EBC80'})],
    d.dates.slice(s,e).map(fmtDate),'Cases',{xLabel:'Date'});
}

function updateRegional(range){
  const d=D.regional_egg;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const datasets=Object.keys(d.series).map(r=>ds(r,d.series[r].slice(s,e),COLORS_REG[r]||COLORS_SEQ[0]));
  makeLineChart('regionalChart',datasets,labels,'¢ / dozen',{xLabel:'Date'});
}

function renderNarratives(){
  const box=document.getElementById('narrativeBox');
  if(!D.narratives||!D.narratives.length){box.innerHTML='<div style="color:#939598;font-size:.8rem">No narratives available</div>';return}
  box.innerHTML=D.narratives.map(n=>`<div class="narrative"><div class="ndate">${fmtDate(n.date)}</div>${n.text}</div>`).join('');
}

function updateNassLayers(range){
  const d=D.nass_layers;
  const[s,e]=filterByRange(d.dates,range);
  const datasets=[ds('All Layers',d.total.slice(s,e).map(v=>v/1e6),'#013046')];
  if(d.table&&d.table.length){const[s2,e2]=filterByRange(d.dates_table,range);datasets.push(ds('Table Layers',d.table.slice(s2,e2).map(v=>v/1e6),'#F6851F'))}
  makeLineChart('nassLayersChart',datasets,d.dates.slice(s,e),'Million head',{xLabel:'Month'});
}

function updateNassEggProd(range){
  const d=D.nass_egg_production;
  const[s,e]=filterByRange(d.dates,range);
  const datasets=[ds('All Eggs',d.total.slice(s,e).map(v=>v/1e9),'#013046')];
  if(d.table&&d.table.length){const[s2,e2]=filterByRange(d.dates_table,range);datasets.push(ds('Table Eggs',d.table.slice(s2,e2).map(v=>v/1e9),'#F6851F'))}
  makeLineChart('nassEggProdChart',datasets,d.dates.slice(s,e),'Billion eggs',{xLabel:'Month'});
}

function rollingAvg(arr,w){
  return arr.map((_,i)=>{if(i<w-1)return null;let s=0;for(let j=i-w+1;j<=i;j++)s+=arr[j];return+(s/w).toFixed(2);});
}
function updateNassRol(range){
  const d=D.nass_rate_of_lay;
  if(d.table&&d.dates_table.length){
    const avg12=rollingAvg(d.table,12);
    const[s,e]=filterByRange(d.dates_table,range);
    const avgDs=ds('1-Year Avg',avg12.slice(s,e),'#013046');
    avgDs.borderDash=[6,3];avgDs.borderWidth=2;avgDs.pointRadius=0;
    makeLineChart('nassRolChart',[ds('Table Layers',d.table.slice(s,e),'#F6851F'),avgDs],d.dates_table.slice(s,e),'Eggs / 100 layers / day',{xLabel:'Month'});
  } else {
    const avg12=rollingAvg(d.all,12);
    const[s,e]=filterByRange(d.dates,range);
    const avgDs=ds('1-Year Avg',avg12.slice(s,e),'#013046');
    avgDs.borderDash=[6,3];avgDs.borderWidth=2;avgDs.pointRadius=0;
    makeLineChart('nassRolChart',[ds('All Layers',d.all.slice(s,e),'#013046'),avgDs],d.dates.slice(s,e),'Eggs / 100 layers / day',{xLabel:'Month'});
  }
}

function updateNassPullets(range){
  const d=D.nass_pullets;
  const[s,e]=filterByRange(d.dates,range);
  makeLineChart('nassPulletsChart',[ds('Replacement Pullets',d.values.slice(s,e).map(v=>v/1e6),'#1F9EBC')],d.dates.slice(s,e),'Million head',{xLabel:'Month'});
}

function updateEggInv(range){
  const d=D.egg_inventory;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const keys=Object.keys(d.series);
  const datasets=keys.map((r,i)=>ds(r,(d.series[r]||[]).slice(s,e),COLORS_REG[r]||COLORS_SEQ[i%COLORS_SEQ.length]));
  makeLineChart('eggInvChart',datasets,labels,'Cases',{xLabel:'Date'});
}

function updateEggsProc(range){
  const d=D.eggs_processed;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const keys=Object.keys(d.series);
  const datasets=keys.map((c,i)=>ds(c,(d.series[c]||[]).slice(s,e),COLORS_SEQ[i%COLORS_SEQ.length]));
  makeLineChart('eggsProcChart',datasets,labels,'Cases',{xLabel:'Date'});
}

function updateRetailEgg(range){
  const d=D.retail_egg_prices;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const datasets=Object.keys(d.series).map(env=>ds(env,d.series[env].slice(s,e),COLORS_ENV[env]||COLORS_SEQ[0]));
  makeLineChart('retailEggChart',datasets,labels,'$ / dozen',{xLabel:'Date'});
}

function updateEggFeat(range){
  const d=D.retail_egg_feature;
  const[s,e]=filterByRange(d.dates,range);
  makeLineChart('eggFeatChart',[ds('Feature Rate',d.rate.slice(s,e),'#FDB714')],d.dates.slice(s,e).map(fmtDate),'%',{aspect:2,xLabel:'Date'});
}

/* ═══ Broilers tab ═══ */
let chxSelected=new Set(TOP_CUTS);

function initChxMS(){
  const items=Object.keys(D.chicken_wholesale.series).sort();
  const panel=document.getElementById('chxMSPanel');
  panel.innerHTML=`<div class="ms-actions"><a onclick="chxSelectAll()">All</a> · <a onclick="chxClear()">Clear</a></div>`+
    items.map(item=>{const chk=chxSelected.has(item)?'checked':'';
      return `<label class="ms-item"><input type="checkbox" value="${item}" ${chk} onchange="onChxCheck()"><span>${item}</span></label>`;
    }).join('');
}

function getChxSelected(){return Array.from(document.querySelectorAll('#chxMSPanel input:checked')).map(b=>b.value)}
function onChxCheck(){chxSelected=new Set(getChxSelected());updateChxWhole(ranges.chxWhole||'1y');updateChxBtn()}
function chxSelectAll(){document.querySelectorAll('#chxMSPanel input').forEach(b=>b.checked=true);onChxCheck()}
function chxClear(){document.querySelectorAll('#chxMSPanel input').forEach(b=>b.checked=false);onChxCheck()}
function updateChxBtn(){
  const n=getChxSelected().length,t=Object.keys(D.chicken_wholesale.series).length;
  document.getElementById('chxMSBtn').textContent=n===t?'All cuts':n===1?getChxSelected()[0]:n+' cuts';
}

function updateChxWhole(range){
  const d=D.chicken_wholesale;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const sel=getChxSelected();
  const datasets=sel.map((item,i)=>ds(item,(d.series[item]||[]).slice(s,e),COLORS_SEQ[i%COLORS_SEQ.length]));
  makeLineChart('chxWholeChart',datasets,labels,'¢ / lb',{xLabel:'Date'});
}

function updateChxVol(range){
  const d=D.chicken_volume;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const keys=Object.keys(d.series).slice(0,5);
  const datasets=keys.map((k,i)=>ds(k,(d.series[k]||[]).slice(s,e),COLORS_SEQ[i%COLORS_SEQ.length],{backgroundColor:COLORS_SEQ[i%COLORS_SEQ.length]+'80'}));
  makeBarChart('chxVolChart',datasets,labels,'Loads',{stacked:true,xLabel:'Date'});
}

function updateNassPlace(range){
  const d=D.nass_placements;
  const[s,e]=filterByRange(d.dates,range);
  makeLineChart('nassPlaceChart',[ds('Broiler Placements',d.values.slice(s,e).map(v=>v/1e6),'#013046')],d.dates.slice(s,e),'Million head',{xLabel:'Week'});
}

function updateNassHatch(range){
  const d=D.nass_hatchery;
  const[s,e]=filterByRange(d.dates_broiler,range);
  const datasets=[ds('Broiler Chicks',d.broiler_chicks.slice(s,e).map(v=>v/1e6),'#F6851F')];
  if(d.egg_chicks&&d.egg_chicks.length){const[s2,e2]=filterByRange(d.dates_egg,range);datasets.push(ds('Egg-Type Chicks',d.egg_chicks.slice(s2,e2).map(v=>v/1e6),'#1F9EBC'))}
  makeLineChart('nassHatchChart',datasets,d.dates_broiler.slice(s,e),'Million head',{xLabel:'Month'});
}

function updateNassPrices(range){
  const d=D.nass_prices;
  const[s,e]=filterByRange(d.dates_egg,range);
  const[s2,e2]=filterByRange(d.dates_broiler,range);
  const ds1=ds('Eggs ($/doz)',d.egg_doz.slice(s,e),'#F6851F');
  const ds2=Object.assign(ds('Broilers ($/lb)',d.broiler_lb.slice(s2,e2),'#1F9EBC'),{yAxisID:'y2'});
  makeLineChart('nassPricesChart',[ds1,ds2],d.dates_egg.slice(s,e),'$ / dozen',{y2:'$ / lb',xLabel:'Month'});
}

function updateColdMars(range){
  const d=D.cold_storage_mars;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const keys=Object.keys(d.series);
  const datasets=keys.map((c,i)=>ds(c,(d.series[c]||[]).slice(s,e).map(v=>v?v/1e6:null),COLORS_SEQ[i%COLORS_SEQ.length]));
  makeLineChart('coldMarsChart',datasets,labels,'Million lbs',{xLabel:'Date'});
}

function updateColdNass(range){
  const d=D.cold_storage_nass;
  const[s,e]=filterByRange(d.dates_chicken,range);
  const[s2,e2]=filterByRange(d.dates_egg,range);
  makeLineChart('coldNassChart',
    [ds('Chicken',d.chicken_lbs.slice(s,e).map(v=>v?v/1e6:null),'#013046'),
     ds('Eggs',d.egg_lbs.slice(s2,e2).map(v=>v?v/1e6:null),'#F6851F')],
    d.dates_chicken.slice(s,e),'Million lbs',{xLabel:'Month'});
}

function updateRetailChx(range){
  const d=D.retail_chicken_prices;
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e).map(fmtDate);
  const keys=Object.keys(d.series).slice(0,8);
  const datasets=keys.map((k,i)=>ds(k,d.series[k].slice(s,e),COLORS_SEQ[i%COLORS_SEQ.length]));
  makeLineChart('retailChxChart',datasets,labels,'$ / lb',{xLabel:'Date'});
}

function updateChxFeat(range){
  const d=D.retail_chicken_feature;
  const[s,e]=filterByRange(d.dates,range);
  makeLineChart('chxFeatChart',[ds('Feature Rate',d.rate.slice(s,e),'#013046')],d.dates.slice(s,e).map(fmtDate),'%',{aspect:2,xLabel:'Date'});
}

/* ═══ Macro tab ═══ */
function updateFeedCosts(range){
  const d=D.fred_feed_costs;
  if(!d||!d.dates.length){makeLineChart('feedCostsChart',[],[],'');return}
  const[s,e]=filterByRange(d.dates,range);
  makeLineChart('feedCostsChart',
    [ds('Corn',d.corn.slice(s,e),'#FDB714'),ds('Soybean Meal',d.sbm.slice(s,e),'#013046')],
    d.dates.slice(s,e),'$ / metric ton',{xLabel:'Month'});
}

function initFeedIndex(){
  const d=D.feed_index;
  if(!d||!d.dates.length)return;
  makeLineChart('feedIndexChart',
    [ds('Feed Cost Index',d.index,'#F6851F')],
    d.dates,'Index (base=100)',{xLabel:'Month'});
}

function initFeedRatios(){
  const d=D.feed_ratios;
  if(!d||!d.egg_dates.length)return;
  const datasets=[ds('Egg/Feed',d.egg_ratio,'#F6851F')];
  if(d.broiler_ratio&&d.broiler_ratio.length){
    datasets.push(ds('Broiler/Feed',d.broiler_ratio,'#1F9EBC'));
  }
  makeLineChart('feedRatioChart',datasets,d.egg_dates,'Ratio',{xLabel:'Month'});
}

function updateHpaiTimeline(range){
  const d=D.hpai_summary;
  if(!d||!d.dates.length){makeBarChart('hpaiTimelineChart',[],[],'');return}
  const[s,e]=filterByRange(d.dates,range);
  const labels=d.dates.slice(s,e);
  const ds1=ds('Detections',d.detections.slice(s,e),'#991b1b',{backgroundColor:'#991b1b80'});
  const ds2=Object.assign(ds('Birds (M)',d.commercial_birds.slice(s,e).map(v=>v?v/1e6:0),'#F6851F',{type:'line',fill:false}),{yAxisID:'y2'});
  makeBarChart('hpaiTimelineChart',[ds1],labels,'Detections',{aspect:1.7,xLabel:'Month'});
  // Overlay line for birds
  if(charts.hpaiTimelineChart){
    charts.hpaiTimelineChart.data.datasets.push(ds2);
    charts.hpaiTimelineChart.options.scales.y2={position:'right',title:{display:true,text:'Million birds',font:{size:11}},ticks:{font:{size:10}},grid:{drawOnChartArea:false}};
    charts.hpaiTimelineChart.update();
  }
}

function initHpaiState(){
  const d=D.hpai_by_state;
  if(!d||!d.states.length)return;
  makeBarChart('hpaiStateChart',
    [ds('Birds Affected',d.birds.map(v=>v/1e6),'#991b1b',{backgroundColor:'#991b1b80'})],
    d.states,'Million birds',{horizontal:true,aspect:1.8,xLabel:'State'});
}

function initCrossProtein(){
  const d=D.bls_retail;
  if(!d||!d.dates.length){makeLineChart('crossProteinChart',[],[],'');return}
  const datasets=[];
  if(d.egg.some(v=>v!=null))datasets.push(ds('Eggs ($/doz)',d.egg,'#F6851F'));
  if(d.chicken_whole.some(v=>v!=null))datasets.push(ds('Chicken Whole ($/lb)',d.chicken_whole,'#013046'));
  if(d.chicken_breast.some(v=>v!=null))datasets.push(ds('Breast B/S ($/lb)',d.chicken_breast,'#1F9EBC'));
  makeLineChart('crossProteinChart',datasets,d.dates,'$ / unit',{xLabel:'Month'});
}

function initPpi(){
  const d=D.fred_ppi;
  if(!d||!d.dates.length){makeLineChart('ppiChart',[],[],'');return}
  const datasets=Object.keys(d.series).map((k,i)=>
    ds(d.labels&&d.labels[k]||k,d.series[k],COLORS_SEQ[i%COLORS_SEQ.length])
  );
  makeLineChart('ppiChart',datasets,d.dates,'Index',{xLabel:'Month'});
}

/* ═══ Data Quality tab ═══ */
function initFreshness(){
  const rows=D.data_freshness||[];
  const body=document.getElementById('freshnessBody');
  body.innerHTML=rows.map(r=>{
    const badge=r.status==='ok'?'badge-ok':'badge-err';
    return `<tr><td>${r.source}</td><td>${r.item||'—'}</td><td>${r.last_fetch||'—'}</td><td>${r.latest_data||'—'}</td><td class="num">${(r.total_rows||0).toLocaleString()}</td><td><span class="badge ${badge}">${r.status}</span></td></tr>`;
  }).join('');

  // Coverage summary
  const usda=['mars','nass'];
  const other=['fred','bls','hpai'];
  const usdaHtml=usda.map(s=>{
    const items=rows.filter(r=>r.source===s);
    const total=items.reduce((a,r)=>a+(r.total_rows||0),0);
    return `<div style="font-size:.78rem;margin-bottom:4px"><strong>${s.toUpperCase()}</strong>: ${items.length} series, ${total.toLocaleString()} rows</div>`;
  }).join('');
  const otherHtml=other.map(s=>{
    const items=rows.filter(r=>r.source===s);
    const total=items.reduce((a,r)=>a+(r.total_rows||0),0);
    const badge=total>0?'badge-ok':'badge-na';
    return `<div style="font-size:.78rem;margin-bottom:4px"><strong>${s.toUpperCase()}</strong>: ${items.length} series, ${total.toLocaleString()} rows <span class="badge ${badge}">${total>0?'active':'no data'}</span></div>`;
  }).join('');
  document.getElementById('coverageUsda').innerHTML=usdaHtml;
  document.getElementById('coverageOther').innerHTML=otherHtml;

  // API key status
  const fredOk=(D.fred_feed_costs&&D.fred_feed_costs.dates.length>0);
  const blsOk=(D.bls_retail&&D.bls_retail.dates.length>0);
  const hpaiOk=(D.hpai_summary&&D.hpai_summary.dates.length>0);
  document.getElementById('apiKeyStatus').innerHTML=`
    <div style="font-size:.78rem;display:flex;gap:16px;flex-wrap:wrap">
      <div>MARS_API_KEY: <span class="badge badge-ok">OK</span></div>
      <div>NASS_API_KEY: <span class="badge badge-ok">OK</span></div>
      <div>FRED_API_KEY: <span class="badge ${fredOk?'badge-ok':'badge-warn'}">${fredOk?'OK':'Not set'}</span></div>
      <div>BLS_API_KEY: <span class="badge ${blsOk?'badge-ok':'badge-warn'}">${blsOk?'OK':'Not set'}</span></div>
      <div>HPAI (no key): <span class="badge ${hpaiOk?'badge-ok':'badge-na'}">${hpaiOk?'OK':'No data'}</span></div>
    </div>`;
}

/* ═══ Tab switching ═══ */
const tabInited={};
function switchTab(tab){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.toggle('active',t.id==='tab-'+tab));
  if(!tabInited[tab]){tabInited[tab]=true;initTab(tab)}
  Object.values(charts).forEach(c=>{try{c.resize()}catch(e){}});
}

function initTab(tab){
  switch(tab){
    case 'landing':
      initLanding();
      break;
    case 'eggs':
      initEggMS();
      updateEggIdx(ranges.eggIdx||'1y');
      updateCfSpread(ranges.cfSpread||'1y');
      updateEggVol(ranges.eggVol||'1y');
      updateRegional(ranges.regional||'1y');
      updateNassLayers(ranges.nassLayers||'all');
      updateNassEggProd(ranges.nassEggProd||'all');
      updateNassRol(ranges.nassRol||'all');
      updateNassPullets(ranges.nassPullets||'all');
      updateEggInv(ranges.eggInv||'all');
      updateEggsProc(ranges.eggsProc||'all');
      updateRetailEgg(ranges.retailEgg||'all');
      updateEggFeat(ranges.eggFeat||'all');
      break;
    case 'broilers':
      initChxMS();
      updateChxWhole(ranges.chxWhole||'1y');
      updateChxVol(ranges.chxVol||'1y');
      updateNassPlace(ranges.nassPlace||'all');
      updateNassHatch(ranges.nassHatch||'all');
      updateNassPrices(ranges.nassPrices||'all');
      updateColdMars(ranges.coldMars||'all');
      updateColdNass(ranges.coldNass||'all');
      updateRetailChx(ranges.retailChx||'all');
      updateChxFeat(ranges.chxFeat||'all');
      break;
    case 'macro':
      updateFeedCosts(ranges.feedCosts||'all');
      initFeedIndex();
      initFeedRatios();
      updateHpaiTimeline(ranges.hpaiTimeline||'all');
      initHpaiState();
      initCrossProtein();
      initPpi();
      break;
    case 'quality':
      initFreshness();
      break;
  }
}

/* ═══ Chart↔Range mapping ═══ */
const chartUpdateMap={
  eggIdx:updateEggIdx,cfSpread:updateCfSpread,eggVol:updateEggVol,regional:updateRegional,
  nassLayers:updateNassLayers,nassEggProd:updateNassEggProd,nassRol:updateNassRol,nassPullets:updateNassPullets,
  eggInv:updateEggInv,eggsProc:updateEggsProc,retailEgg:updateRetailEgg,eggFeat:updateEggFeat,
  chxWhole:updateChxWhole,chxVol:updateChxVol,nassPlace:updateNassPlace,nassHatch:updateNassHatch,
  nassPrices:updateNassPrices,coldMars:updateColdMars,coldNass:updateColdNass,
  retailChx:updateRetailChx,chxFeat:updateChxFeat,
  feedCosts:updateFeedCosts,hpaiTimeline:updateHpaiTimeline,
};

/* ═══ Event delegation ═══ */
document.addEventListener('click',function(ev){
  if(ev.target.classList.contains('rbtn')){
    const row=ev.target.closest('.range-row');
    if(!row)return;
    row.querySelectorAll('.rbtn').forEach(b=>b.classList.remove('active'));
    ev.target.classList.add('active');
    const chartId=row.dataset.chart;
    const range=ev.target.dataset.r;
    ranges[chartId]=range;
    if(chartUpdateMap[chartId])chartUpdateMap[chartId](range);
  }
  if(ev.target.classList.contains('tab-btn')){switchTab(ev.target.dataset.tab)}
  if(ev.target.classList.contains('ms-btn')){const panel=ev.target.nextElementSibling;if(panel)panel.classList.toggle('open')}
  if(!ev.target.closest('.ms-wrap')){document.querySelectorAll('.ms-panel.open').forEach(p=>p.classList.remove('open'))}
});

/* ═══ KPI rendering ═══ */
function renderKPIs(){
  const k=D.kpi;
  if(k.egg_index_price!=null){
    document.getElementById('kpiEggPrice').textContent=fmtNum(k.egg_index_price,2)+'¢';
    document.getElementById('kpiEggDate').textContent=fmtDate(k.egg_index_date);
  }
  if(k.egg_index_change_pct!=null){
    const el=document.getElementById('kpiWoW');
    const pct=k.egg_index_change_pct;
    el.textContent=(pct>=0?'+':'')+pct.toFixed(1)+'%';
    el.className='val '+(pct>=0?'up':'dn');
  }
  if(k.breast_bs_price!=null){
    document.getElementById('kpiBreast').textContent=fmtNum(k.breast_bs_price,2)+'¢';
    document.getElementById('kpiBreastDate').textContent=fmtDate(k.breast_bs_date);
  }
  if(k.layer_count!=null){
    document.getElementById('kpiLayers').textContent=fmtM(k.layer_count);
    document.getElementById('kpiLayerPeriod').textContent=k.layer_period||'';
  }
  if(k.corn_price!=null){
    document.getElementById('kpiCorn').textContent='$'+fmtNum(k.corn_price,0);
    document.getElementById('kpiCornDate').textContent=fmtDate(k.corn_date);
  }
  if(k.hpai_30d_detections!=null){
    document.getElementById('kpiHpai').textContent=k.hpai_30d_detections;
    document.getElementById('kpiHpaiBirds').textContent=k.hpai_30d_birds?fmtM(k.hpai_30d_birds)+' birds':'0 birds';
  }
}

function populateHero(){
  const rows=D.data_freshness||[];
  const coverage=document.getElementById('heroCoverage');
  const health=document.getElementById('heroHealth');
  if(coverage){
    const sources=new Set(rows.map(r=>r.source).filter(Boolean));
    coverage.textContent=rows.length?`${sources.size} sources • ${rows.length} tracked series`:'Coverage pending';
  }
  if(health){
    const bad=rows.filter(r=>r.status&&r.status!=='ok').length;
    health.textContent=bad?`${bad} source issues flagged`:'All tracked sources reporting OK';
  }
}

/* ═══ Inject export buttons ═══ */
function addExportButtons(){
  document.querySelectorAll('.card canvas').forEach(c=>{
    const card=c.closest('.card');
    if(!card||card.querySelector('.export-btn'))return;
    const btn=document.createElement('button');
    btn.className='export-btn';
    btn.textContent='\u2B73 PNG';
    btn.onclick=function(){exportChart(this)};
    card.appendChild(btn);
  });
}

/* ═══ Boot ═══ */
async function boot(){
  try{
    const resp=await fetch('data.json?v='+Date.now());
    D=await resp.json();
    document.getElementById('loading').style.display='none';
    addExportButtons();
    renderKPIs();
    populateHero();
    tabInited.landing=true;
    initTab('landing');
  }catch(e){
    document.getElementById('loading').innerHTML='<div style="color:#F6851F">Error loading data: '+e.message+'</div>';
  }
}
boot();
</script>
</body>
</html>"""
