/* Broiler Industry Executive Chartbook.
   Every chart reads the single `D.broiler` block built by broiler_data.py. */

const SRC = {
  hatch: '<a href="https://esmis.nal.usda.gov/publication/broiler-hatchery" target="_blank" rel="noreferrer">USDA NASS Broiler Hatchery (ESMIS)</a>',
  chickens: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
  hatchery: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Hatchery_Production/index.php" target="_blank" rel="noreferrer">USDA NASS Hatchery Production</a>',
  wholesale: '<a href="https://mymarketnews.ams.usda.gov/viewReport/3646" target="_blank" rel="noreferrer">USDA AMS Weekly National Chicken Report</a>',
  retail: '<a href="https://mymarketnews.ams.usda.gov/viewReport/2756" target="_blank" rel="noreferrer">USDA AMS National Retail Chicken Report</a>',
  slaughter: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Poultry_Slaughter/index.php" target="_blank" rel="noreferrer">USDA NASS Poultry Slaughter</a>',
  ppv: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Poultry_Production_and_Value/index.php" target="_blank" rel="noreferrer">USDA NASS Poultry Production and Value</a>',
  prices: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Prices_Received_and_Prices_Received_Indexes/" target="_blank" rel="noreferrer">USDA NASS Agricultural Prices</a>',
  cme: '<a href="https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html" target="_blank" rel="noreferrer">CME Group delayed quotes</a>',
  cold: '<a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Cold_Storage/index.php" target="_blank" rel="noreferrer">USDA NASS Cold Storage</a>',
  ers: '<a href="https://www.ers.usda.gov/data-products/livestock-and-meat-international-trade-data" target="_blank" rel="noreferrer">USDA ERS Livestock and Meat International Trade Data</a>',
  aphis: '<a href="https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/poultry" target="_blank" rel="noreferrer">USDA APHIS Poultry HPAI Detections</a>'
};

const UP = '#15803d';
const DOWN = '#dc2626';

function broilerText(id, text) {
  const node = document.getElementById(id);
  if (node) node.textContent = text;
}

function signed(value, digits = 1, suffix = '%') {
  if (value == null || !Number.isFinite(value)) return '—';
  return `${value > 0 ? '+' : ''}${fmtNum(value, digits)}${suffix}`;
}

function setChartSources() {
  const chartBy = 'Chart: Innovate Animal Ag • Source: ';
  const map = {
    hatchabilityChart: `${SRC.hatch} • Gaps are weeks with no report (e.g. Oct 1–Nov 12, 2025 federal shutdown)`,
    hatchAnnualChart: `${SRC.hatch} • Average of the weekly reports available in each year`,
    hatchSeasonalChart: `${SRC.hatch} • Oct 2025 missing: no reports during the federal shutdown`,
    breederHensChart: SRC.chickens,
    breederProductivityChart: `${SRC.chickens} and ${SRC.hatchery}`,
    pulletPipelineChart: `${SRC.chickens} • Potential flock = U.S. pullet chicks placed 7–15 months earlier, as USDA defines it`,
    placementsYoYChart: `${SRC.hatch} • 4 weeks to date vs the 4 weeks ending 364 days earlier`,
    placementsWeeklyChart: SRC.hatch,
    chicksHatchedChart: SRC.hatchery,
    productionChart: `${SRC.slaughter} • USDA reports broilers as "young chickens"; federally inspected plants handle nearly all U.S. production`,
    productionMonthlyChart: SRC.slaughter,
    productionYoYChart: `${SRC.slaughter} • IAA calculation`,
    productionYtdChart: `${SRC.slaughter} • IAA calculation`,
    productionDriversChart: `${SRC.slaughter} • IAA calculation`,
    liveWeightChart: SRC.slaughter,
    condemnChart: `${SRC.slaughter} • Rates also reflect inspection and plant practices, not only flock health`,
    stateProductionChart: `${SRC.ppv} • Production year runs December to November; states USDA does not publish separately are not shown`,
    wholesaleCutsChart: `${SRC.wholesale} • National, domestic, fresh; parts FOB plant, WOG delivered, all sizes`,
    retailChickenChart: `${SRC.retail} • Fresh, conventional, regular pack. Party wings start Sept 2024 (AMS renamed its retail items then)`,
    pricesReceivedChart: SRC.prices,
    feedCostChart: `${SRC.cme} • Nearby futures; ration weights are an IAA assumption; excludes other ingredients, basis and freight`,
    feedRatioChart: `${SRC.prices} and ${SRC.cme} • IAA calculation; a price relationship, not a measured margin`,
    coldStorageChart: SRC.cold,
    exportsChart: SRC.ers,
    hpaiBroilerChart: SRC.aphis
  };
  Object.entries(map).forEach(([chartId, html]) => {
    const card = document.getElementById(chartId)?.closest('.card');
    if (!card) return;
    let node = card.querySelector('.card-source');
    if (!node) {
      node = document.createElement('div');
      node.className = 'card-source';
      card.appendChild(node);
    }
    node.innerHTML = chartBy + html;
  });
}

/* Append "Latest data: <date>" to a chart's source line. */
function setLatest(chartId, text) {
  const node = document.getElementById(chartId)?.closest('.card')?.querySelector('.card-source');
  if (!node || !text) return;
  let span = node.querySelector('.latest-obs');
  if (!span) {
    span = document.createElement('span');
    span.className = 'latest-obs';
    node.appendChild(span);
  }
  span.textContent = ` • Latest data: ${text}`;
}

function lastDateOf(dates, values) {
  for (let i = dates.length - 1; i >= 0; i -= 1) if (values[i] != null) return dates[i];
  return null;
}

const latestDay = d => (d ? fmtDate(d) : null);
const latestMonth = d => (d ? fmtYM(d) : null);

function slugify(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

/* Sidebar outline + mobile section jumper (same behaviour as the egg chartbook). */
function initBroilerSidebarNav() {
  const nav = document.getElementById('broilerSidebarNav');
  const sections = Array.from(document.querySelectorAll('.section[id]'));
  if (!nav || !sections.length) return;
  const used = new Set(Array.from(document.querySelectorAll('[id]')).map(n => n.id));
  const entries = [];
  nav.innerHTML = '';
  const groups = sections.map(section => {
    const group = document.createElement('div');
    group.className = 'sidebar-group';
    group.dataset.section = section.id;
    const head = document.createElement('a');
    head.className = 'sidebar-section-link';
    head.href = `#${section.id}`;
    head.textContent = section.querySelector('.section-head h2')?.textContent?.trim() || section.id;
    group.appendChild(head);
    const links = document.createElement('div');
    links.className = 'sidebar-chart-links';
    section.querySelectorAll('.card').forEach(card => {
      const title = card.querySelector('h3')?.textContent?.trim();
      if (!title) return;
      if (!card.id) {
        let id = slugify(title);
        let n = 2;
        while (used.has(id)) id = `${slugify(title)}-${n++}`;
        used.add(id);
        card.id = id;
      }
      const link = document.createElement('a');
      link.className = 'sidebar-chart-link';
      link.href = `#${card.id}`;
      link.textContent = title;
      links.appendChild(link);
      entries.push({ card, link, sectionId: section.id });
    });
    group.appendChild(links);
    nav.appendChild(group);
    return group;
  });

  const update = () => {
    const offset = window.innerHeight * 0.22;
    const atBottom = (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 40);
    let active = sections[0].id;
    if (atBottom) active = sections[sections.length - 1].id;
    else sections.forEach(s => { if (s.getBoundingClientRect().top - offset <= 0) active = s.id; });
    const inSection = entries.filter(e => e.sectionId === active);
    let activeCard = inSection[0]?.card.id;
    inSection.forEach(e => { if (e.card.getBoundingClientRect().top - offset <= 0) activeCard = e.card.id; });
    groups.forEach(g => g.classList.toggle('is-active', g.dataset.section === active));
    entries.forEach(e => e.link.classList.toggle('is-active', e.card.id === activeCard));
  };
  update();
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);

  const select = document.getElementById('mobileSectionSelect');
  if (select) {
    sections.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = s.querySelector('.section-head h2')?.textContent?.trim() || s.id;
      select.appendChild(opt);
    });
    select.addEventListener('change', () => {
      document.getElementById(select.value)?.scrollIntoView({ behavior: 'smooth' });
      setTimeout(() => { select.value = ''; }, 600);
    });
  }
}

function renderBroilerMixed(id, labels, datasets, yLabel, y2Label, extra = {}) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  const normalized = datasets.map(entry => {
    const isBar = (entry.type || 'bar') === 'bar';
    const styled = isBar ? Object.assign({}, entry, { borderWidth: 0, borderColor: 'transparent' }) : entry;
    return Object.assign({ order: isBar ? 10 : 0 }, styled);
  });
  const options = baseOptions(yLabel, Object.assign({ chartId: id, y2: y2Label, maxTicks: 12 }, extra));
  if (extra.stacked) options.scales.y2 && (options.scales.y2.stacked = false);
  charts[id] = new Chart(ctx, { type: 'bar', data: { labels, datasets: normalized }, options, plugins: extra.plugins || [] });
}

/* Monthly seasonal comparison: prior year + current year bars, history-average diamonds. */
function seasonalDatasets(dates, values, range, minYear) {
  const map = buildYearMonthMap(dates, values);
  const years = Object.keys(map).map(Number).sort((a, b) => a - b);
  const current = years[years.length - 1];
  const previous = current - 1;
  const pool = years.filter(y => y < previous && (!minYear || y >= minYear));
  const avgYears = historyYearsForRange(pool, range, minYear);
  return [
    dataset(avgYears.length ? `${avgYears[0]}–${avgYears[avgYears.length - 1]} avg` : 'History avg',
      avgYears.length ? averageMonths(map, avgYears) : Array(12).fill(null), DASH_COLORS.slate,
      { type: 'line', borderDash: [6, 5], borderWidth: 2.2, pointRadius: 0 }),
    dataset(String(previous), monthsForYear(map, previous), DASH_COLORS.navy, { type: 'line', borderWidth: 2.6, pointRadius: 3 }),
    dataset(String(current), monthsForYear(map, current), DASH_COLORS.orange, { type: 'line', borderWidth: 3, pointRadius: 3.5 })
  ];
}

/* Axis bounds snapped to a "nice" tick step (1, 2, 2.5 or 5 × 10^k), so the
   top and bottom ticks sit on the same grid as the rest and labels never bunch. */
function niceStep(span, targetTicks = 6) {
  const raw = span / targetTicks;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  const nice = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10;
  return nice * mag;
}

function niceBounds(values, pad = 0.08) {
  const v = values.filter(x => x != null && Number.isFinite(x));
  if (!v.length) return {};
  const lo = Math.min(...v);
  const hi = Math.max(...v);
  const span = (hi - lo) || Math.abs(hi) * 0.1 || 1;
  const step = niceStep(span * (1 + 2 * pad));
  const round = x => Math.round(x / step * 1e6) / 1e6 * step;
  return {
    yMin: round(Math.floor((lo - span * pad) / step) * step),
    yMax: round(Math.ceil((hi + span * pad) / step) * step),
    yStep: step
  };
}

/* Tick label formatter that shows only as many decimals as the tick step needs. */
function tickFmt({ prefix = '', suffix = '', sign = false, scale = 1 } = {}) {
  return function (value, index, ticks) {
    const step = ticks && ticks.length > 1 ? Math.abs(ticks[1].value - ticks[0].value) / scale : 1;
    const digits = step >= 1 && Number.isInteger(Math.round(step * 1e6) / 1e6) ? 0 : step >= 0.1 ? (Number.isInteger(Math.round(step * 10 * 1e6) / 1e6) ? 1 : 2) : 2;
    const v = value / scale;
    const s = sign && v > 0 ? '+' : '';
    return `${s}${prefix}${fmtNum(v, digits)}${suffix}`;
  };
}

/* Let render calls pass `yStep` (from niceBounds) through to Chart.js. */
const baseOptionsShared = baseOptions;
baseOptions = function (yLabel, extra = {}) {
  const options = baseOptionsShared(yLabel, extra);
  if (extra.yStep) options.scales.y.ticks.stepSize = extra.yStep;
  // The shared date-tick planner keeps every year (up to 20) even on a phone;
  // thin the date ticks to what fits the axis width (keeping the latest one).
  const sharedAfterBuild = options.scales.x.afterBuildTicks;
  options.scales.x.afterBuildTicks = function (scale) {
    sharedAfterBuild.call(this, scale);
    const ticks = scale.ticks || [];
    if (ticks.length < 3 || !scale.width) return;
    const fmt = options.scales.x.ticks.callback;
    const widest = Math.max(...ticks.map(t => {
      const lab = fmt ? fmt.call(scale, t.value) : scale.getLabelForValue(t.value);
      return Math.max(...(Array.isArray(lab) ? lab : [lab]).map(l => String(l ?? '').length));
    }));
    const slot = widest * (isMobileWidth() ? 6.5 : 8) + 14;
    const fits = Math.max(2, Math.floor(scale.width / slot));
    if (ticks.length <= fits) return;
    const stride = Math.ceil(ticks.length / fits);
    const last = ticks.length - 1;
    scale.ticks = ticks.filter((_, i) => (last - i) % stride === 0);
  };
  return options;
};

/* Week-of-year comparison chart with month-name ticks. */
function renderWeekOfYearChart(id, byYear, byYearDates, unitScale, yLabel, avgYears) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  const years = Object.keys(byYear).map(Number).sort((a, b) => a - b);
  const current = years[years.length - 1];
  const previous = current - 1;
  const pool = years.filter(y => y < previous).slice(-avgYears);
  // Reporting weeks 1–53 (week 53 occurs in 2014, 2020 and 2025). Month hints
  // use a typical year in which week 1 ends Jan 7; labels never repeat January.
  const weeks = 53;
  const ref = Date.UTC(2023, 0, 7);
  const labels = [];
  let lastMonth = -1;
  for (let w = 0; w < weeks; w += 1) {
    const m = new Date(ref + w * 7 * 86400000).getUTCMonth();
    labels.push(m > lastMonth ? MON_SHORT[m] : '');
    if (m > lastMonth) lastMonth = m;
  }
  const series = y => (byYear[String(y)] || []).slice(0, weeks).map(v => v != null ? v / unitScale : null);
  const yearOf = { 1: String(previous), 2: String(current) };
  const avg = Array.from({ length: weeks }, (_, w) => {
    const vals = pool.map(y => byYear[String(y)]?.[w]).filter(v => v != null);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length / unitScale : null;
  });
  const sets = [
    dataset(pool.length ? `${pool[0]}–${pool[pool.length - 1]} avg` : 'Avg', avg, DASH_COLORS.slate, { borderDash: [6, 5], borderWidth: 2.4 }),
    dataset(String(previous), series(previous), DASH_COLORS.navy, { borderWidth: 2.6 }),
    dataset(String(current), series(current), DASH_COLORS.orange)
  ];
  const all = sets.flatMap(s => s.data);
  const opts = baseOptions(yLabel, Object.assign({
    chartId: id,
    tooltip: { callbacks: {
      title: items => (items && items[0]) ? `Reporting week ${items[0].dataIndex + 1}` : '',
      label(c) {
        const v = c.parsed?.y;
        if (v == null) return '';
        const y = yearOf[c.datasetIndex];
        const d = y ? byYearDates[y]?.[c.dataIndex] : null;
        return `${c.dataset.label}${d ? ` (week ending ${fmtDate(d)})` : ''}: ${fmtNum(v, 1)}M`;
      }
    } }
  }, niceBounds(all)));
  opts.scales.x.afterBuildTicks = scale => {
    scale.ticks = scale.getLabels().reduce((out, label, index) => { if (label) out.push({ value: index }); return out; }, []);
  };
  opts.scales.x.ticks.callback = function (value) { return this.getLabelForValue(value); };
  charts[id] = new Chart(ctx, { type: 'line', data: { labels, datasets: sets }, options: opts });
}

function yoyBars(label, values) {
  return dataset(label, values, UP, {
    backgroundColor: c => (c.raw != null && c.raw < 0) ? DOWN : UP
  });
}

const pctTooltip = {
  callbacks: {
    label(c) {
      const v = c.parsed?.y;
      if (v == null || !Number.isFinite(v)) return '';
      return `${c.dataset.label}: ${signed(v)}`;
    }
  }
};

/* Rolling mean that is null until a full window of non-null values exists. */
function fullRollingAverage(values, windowSize) {
  return values.map((_, i) => {
    if (i < windowSize - 1) return null;
    const win = values.slice(i - windowSize + 1, i + 1);
    if (win.some(v => v == null)) return null;
    return win.reduce((a, b) => a + b, 0) / windowSize;
  });
}

function shiftMonths(ym, k) {
  const [y, m] = ym.split('-').map(Number);
  const t = y * 12 + (m - 1) + k;
  return `${Math.floor(t / 12)}-${String((t % 12) + 1).padStart(2, '0')}`;
}

async function bootBroilerDashboard() {
  initBroilerSidebarNav();
  setChartSources();
  const response = await fetch(`data.json?v=${Date.now()}`);
  const D = await response.json();
  const B = D.broiler;
  document.title = `Broiler Industry Dashboard — ${D.updated}`;
  setAllLatest(B);

  const H = B.hatchability;
  const hatch52 = H.avg52;
  const P = B.placements;
  const W = B.wholesale;
  const PD = B.production;

  /* ── Hatchery performance ─────────────────────────────── */
  const baselineLine = H.dates.map(() => H.baseline);
  registerRangeControl({
    chartId: 'hatchabilityChart',
    options: ['6m', '1y', '3y', '5y', '10y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      // Weekly coverage before 2010 is patchy (7–38 weeks a year), so the long view starts in 2010.
      const slice = getRangeSlice(H.dates, range);
      const firstGood = H.dates.findIndex(d => d >= '2010-01-01');
      const start = Math.max(slice.start, firstGood);
      const end = slice.end;
      const weekly = H.values.slice(start, end);
      const avg = hatch52.slice(start, end);
      // Short views are about the week-to-week reading: make the weekly line the
      // subject and leave the far-off 2012–2019 baseline (which would flatten it)
      // to the long views; the subtitle states it instead.
      const short = range === '6m' || range === '1y';
      const sets = short ? [
        dataset('Weekly hatchability', weekly, DASH_COLORS.orange, { borderWidth: 2.4, pointRadius: range === '6m' ? 3 : 0, order: 0, spanGaps: false }),
        dataset('52-week average', avg, DASH_COLORS.navy, { borderWidth: 2.4, order: 1, spanGaps: false })
      ] : [
        dataset('Weekly hatchability', weekly, 'rgba(246,133,31,0.35)', { borderWidth: 1.6, order: 5, spanGaps: false }),
        dataset('52-week average', avg, DASH_COLORS.navy, { order: 0, spanGaps: false }),
        dataset(H.baseline_label, baselineLine.slice(start, end), DASH_COLORS.slate, { borderDash: [6, 5], borderWidth: 2.2, order: 1 })
      ];
      renderLineChart('hatchabilityChart', H.dates.slice(start, end), sets, '% of eggs set that hatched',
        Object.assign({
          yTickCallback: tickFmt({ suffix: '%' }),
          tooltip: { callbacks: { label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: ${fmtNum(c.parsed.y, 1)}%`) } }
        }, niceBounds(short ? weekly.concat(avg) : weekly.concat([H.baseline]), short ? 0.15 : 0.05)));
      broilerText('hatchabilitySub', short
        ? `Weekly share of broiler-type eggs set that hatched, and the average of reports in the trailing 52 weeks. The 2012–2019 average was ${fmtNum(H.baseline, 1)}%`
        : 'Weekly share of broiler-type eggs set that hatched, the average of reports in the trailing 52 weeks, and the 2012–2019 average of available reports');
    }
  });

  const annualYears = Object.keys(H.annual).filter(y => Number(y) >= 2010 && H.annual_weeks[y] >= 30);
  const lastYear = annualYears[annualYears.length - 1];
  registerRangeControl({
    chartId: 'hatchAnnualChart',
    options: [],
    defaultRange: 'all',
    renderer() {
      const vals = annualYears.map(y => H.annual[y]);
      const YC = H.ytd_compare;
      const priorSame = annualYears.map(y => (y === String(Number(lastYear) - 1) ? YC.prior_value : null));
      renderLineChart('hatchAnnualChart', annualYears.map(y => y === lastYear ? [y, 'YTD'] : y), [
        dataset('Annual average', vals, DASH_COLORS.navy, {
          borderWidth: 2.4, pointRadius: 4,
          pointBackgroundColor: annualYears.map(y => y === lastYear ? DASH_COLORS.orange : DASH_COLORS.navy),
          pointBorderColor: annualYears.map(y => y === lastYear ? DASH_COLORS.orange : DASH_COLORS.navy)
        }),
        dataset(`${Number(lastYear) - 1}, same weeks as ${lastYear} YTD`, priorSame, DASH_COLORS.orange, {
          showLine: false, pointStyle: 'rectRot', pointRadius: 6, pointBackgroundColor: '#fff', borderWidth: 2
        }),
        dataset(H.baseline_label, annualYears.map(() => H.baseline), DASH_COLORS.slate, { borderDash: [6, 5], borderWidth: 2.2, pointRadius: 0 })
      ], '% of eggs set that hatched', Object.assign({
        yTickCallback: tickFmt({ suffix: '%' }),
        tooltip: { callbacks: {
          label(c) {
            const v = c.parsed?.y;
            if (v == null) return '';
            const y = annualYears[c.dataIndex];
            if (c.datasetIndex === 0) return `${y}: ${fmtNum(v, 2)}% (${H.annual_weeks[y]} weekly reports)`;
            if (c.datasetIndex === 1) return `${c.dataset.label}: ${fmtNum(v, 2)}% (${YC.prior_weeks} reports)`;
            return `${c.dataset.label}: ${fmtNum(v, 2)}%`;
          }
        } }
      }, niceBounds(vals.concat([H.baseline]), 0.15)));
    }
  });

  registerRangeControl({
    chartId: 'hatchSeasonalChart',
    options: [],
    defaultRange: 'all',
    renderer() {
      const map = buildYearMonthMap(H.monthly_dates, H.monthly_values);
      const years = Object.keys(map).map(Number).sort((a, b) => a - b);
      const cur = years[years.length - 1];
      const sets = [
        dataset(H.baseline_label, H.baseline_by_month, DASH_COLORS.slate, { type: 'line', borderDash: [6, 5], borderWidth: 2.2, pointRadius: 0 }),
        dataset(String(cur - 1), monthsForYear(map, cur - 1), DASH_COLORS.navy, { type: 'line', borderWidth: 2.6, pointRadius: 3, spanGaps: false }),
        dataset(String(cur), monthsForYear(map, cur), DASH_COLORS.orange, { type: 'line', borderWidth: 3, pointRadius: 3.5, spanGaps: false })
      ];
      renderBroilerMixed('hatchSeasonalChart', MON_SHORT, sets, '%', undefined,
        Object.assign({ yTickCallback: tickFmt({ suffix: '%' }) }, niceBounds(sets.flatMap(s => s.data), 0.2)));
    }
  });

  /* ── Breeder flock ─────────────────────────────────────── */
  const BR = B.breeder;
  registerRangeControl({
    chartId: 'breederHensChart',
    options: ['3y', '5y', '10y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const { start, end } = getRangeSlice(BR.dates, range);
      const hens = BR.hens.slice(start, end).map(v => v != null ? v / 1e6 : null);
      const ctx = document.getElementById('breederHensChart');
      destroyChart('breederHensChart');
      const options = baseOptions('Million hens', Object.assign({
        chartId: 'breederHensChart',
        maxTicks: 12,
        aspect: 1.35,
        yTickCallback: tickFmt({ suffix: 'M' }),
        tooltip: { callbacks: { label(c) {
          const v = c.parsed?.y;
          if (v == null) return '';
          return c.dataset.yAxisID === 'yChange' ? `${c.dataset.label}: ${signed(v)}` : `${c.dataset.label}: ${fmtNum(v, 1)}M`;
        } } }
      }, niceBounds(hens, 0.15)));
      // Two panels on one time axis: the flock on top, its change underneath.
      options.scales.y.stack = 'panels';
      options.scales.y.stackWeight = 2;
      options.scales.yChange = {
        position: 'left',
        stack: 'panels',
        stackWeight: 1,
        offset: true,
        title: { display: true, text: '% vs year ago', color: '#5f7180', font: { size: isMobileWidth() ? 10 : 13, weight: '600' } },
        ticks: { color: '#627684', padding: isMobileWidth() ? 6 : 10, maxTicksLimit: 5, font: { size: isMobileWidth() ? 10 : 13 }, callback: tickFmt({ suffix: '%', sign: true }) },
        border: { display: false },
        grid: { color: c => (c.tick && c.tick.value === 0 ? 'rgba(1,48,70,0.35)' : 'rgba(1,48,70,0.045)') }
      };
      // Chart.js stacks axes bottom-up in definition order: change first, hens last (on top).
      options.scales = { x: options.scales.x, yChange: options.scales.yChange, y: options.scales.y };
      charts.breederHensChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: BR.dates.slice(start, end),
          datasets: [
            dataset('Hatching hens', hens, DASH_COLORS.navy, { type: 'line', borderWidth: 2.8, yAxisID: 'y', order: 0 }),
            Object.assign(yoyBars('Change vs year ago', BR.hens_yoy.slice(start, end)), { type: 'bar', yAxisID: 'yChange', borderWidth: 0, order: 10 })
          ]
        },
        options
      });
    }
  });

  const eggsPerHen12 = fullRollingAverage(BR.eggs_per_hen, 12);
  const chicksPerHen12 = fullRollingAverage(BR.chicks_per_hen, 12);
  registerRangeControl({
    chartId: 'breederProductivityChart',
    options: ['5y', '10y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(BR.dates, range);
      const a = eggsPerHen12.slice(start, end);
      const b = chicksPerHen12.slice(start, end);
      renderLineChart('breederProductivityChart', BR.dates.slice(start, end), [
        dataset('Hatching eggs per hen', a, DASH_COLORS.navy),
        dataset('Chicks hatched per hen', b, DASH_COLORS.orange)
      ], 'Per hen per month', Object.assign({ yTickCallback: tickFmt() }, niceBounds(a.concat(b), 0.15)));
    }
  });

  registerRangeControl({
    chartId: 'pulletPipelineChart',
    options: ['5y', '10y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const potMap = Object.fromEntries(BR.potential_dates.map((d, i) => [d, BR.potential[i]]));
      const henMap = Object.fromEntries(BR.dates.map((d, i) => [d, BR.hens[i]]));
      const all = Array.from(new Set(BR.potential_dates.concat(BR.dates))).sort();
      const { start, end } = getRangeSlice(all, range);
      const labels = all.slice(start, end);
      const lastHen = BR.dates[BR.dates.length - 1];
      const pot = labels.map(d => potMap[d] != null && d <= lastHen ? potMap[d] / 1e6 : null);
      const potAhead = labels.map((d, i) => potMap[d] != null && d >= lastHen ? potMap[d] / 1e6 : null);
      const hens = labels.map(d => henMap[d] != null ? henMap[d] / 1e6 : null);
      renderLineChart('pulletPipelineChart', labels, [
        dataset('Hatching hens on hand', hens, DASH_COLORS.navy),
        dataset('Potential flock from pullets placed 7–15 months earlier', pot, DASH_COLORS.orange),
        dataset('Potential flock, months ahead (pullets already placed)', potAhead, DASH_COLORS.orange, { borderDash: [7, 4] })
      ], 'Million birds', Object.assign({ yTickCallback: tickFmt({ suffix: 'M' }) }, niceBounds(hens.concat(pot, potAhead), 0.1)));
    }
  });

  /* ── Chick supply ──────────────────────────────────────── */
  const ES = B.eggs_set;
  const esMap = Object.fromEntries(ES.dates.map((d, i) => [d, ES.yoy_4wk[i]]));
  registerRangeControl({
    chartId: 'placementsYoYChart',
    options: ['3m', '6m', '1y', '2y', '3y', '5y', 'all'],
    defaultRange: '2y',
    renderer(range) {
      const { start, end } = getRangeSlice(P.dates, range);
      const labels = P.dates.slice(start, end);
      renderBroilerMixed('placementsYoYChart', labels, [
        yoyBars('Chicks placed', P.yoy_4wk.slice(start, end)),
        dataset('Eggs set', labels.map(d => esMap[d] ?? null), DASH_COLORS.navy, { type: 'line', borderWidth: 2.4 })
      ], '% vs year ago', undefined, { yTickCallback: tickFmt({ suffix: '%', sign: true }), tooltip: pctTooltip });
    }
  });

  let weeklyMode = 'placements';
  const renderWeekly = () => {
    const src = weeklyMode === 'placements' ? P : ES;
    renderWeekOfYearChart('placementsWeeklyChart', src.by_year, src.by_year_dates, 1e6, weeklyMode === 'placements' ? 'Million chicks' : 'Million eggs', 5);
    broilerText('placementsWeeklyTitle', weeklyMode === 'placements' ? 'Weekly Chick Placements by Year' : 'Weekly Eggs Set by Year');
    broilerText('placementsWeeklySub', weeklyMode === 'placements'
      ? 'Broiler chicks placed for meat production, by USDA reporting week'
      : 'Broiler-type eggs set in incubators, by USDA reporting week');
  };
  registerRangeControl({ chartId: 'placementsWeeklyChart', options: [], defaultRange: 'all', renderer: renderWeekly });
  insertModeToggle('placementsWeeklyChart', [
    { mode: 'placements', label: 'Chicks placed' },
    { mode: 'eggs', label: 'Eggs set' }
  ], 'placements', mode => { weeklyMode = mode; renderWeekly(); });

  const CH = B.chicks_hatched;
  registerRangeControl({
    chartId: 'chicksHatchedChart',
    options: ['3y', '5y', '10y'],
    defaultRange: '5y',
    renderer(range) {
      const sets = seasonalDatasets(CH.dates, CH.values.map(v => v / 1e6), range, 2012);
      renderBroilerMixed('chicksHatchedChart', MON_SHORT, sets, 'Million chicks', undefined,
        Object.assign({ yTickCallback: tickFmt({ suffix: 'M' }) }, niceBounds(sets.flatMap(s => s.data), 0.5)));
    }
  });

  /* ── Production ────────────────────────────────────────── */
  registerRangeControl({
    chartId: 'productionChart',
    options: ['5y', '10y', 'all'],
    defaultRange: '10y',
    renderer(range) {
      const { start, end } = getRangeSlice(PD.dates, range);
      const vals = PD.rtc_12m.slice(start, end).map(v => v != null ? v / 1e9 : null);
      renderLineChart('productionChart', PD.dates.slice(start, end), [
        dataset('12-month total', vals, DASH_COLORS.navy)
      ], 'Billion lb, trailing 12 months', Object.assign({
        legend: false,
        yTickCallback: tickFmt({ suffix: 'B' }),
        tooltip: { callbacks: { label: c => (c.parsed?.y == null ? '' : `12-month total: ${fmtNum(c.parsed.y, 2)}B lb`) } }
      }, niceBounds(vals, 0.1)));
    }
  });

  /* Month-by-month: this year and last year as bars, the five years before
     that as diamonds. */
  const rtcMap = buildYearMonthMap(PD.dates, PD.rtc.map(v => (v == null ? null : v / 1e9)));
  const rtcYears = Object.keys(rtcMap).map(Number).sort((x, y) => x - y);
  const rtcCur = rtcYears[rtcYears.length - 1];
  const rtcAvgYears = rtcYears.filter(y => y < rtcCur - 1).slice(-5);
  const rtcAvgLabel = `${rtcAvgYears[0]}–${rtcAvgYears[rtcAvgYears.length - 1]} avg`;
  const rtcPrev = monthsForYear(rtcMap, rtcCur - 1);
  const rtcNow = monthsForYear(rtcMap, rtcCur);
  const rtcAvg = averageMonths(rtcMap, rtcAvgYears);
  const rtcLastMonth = rtcNow.reduce((acc, v, i) => (v != null ? i : acc), -1);

  registerRangeControl({
    chartId: 'productionMonthlyChart',
    options: [],
    defaultRange: 'all',
    renderer() {
      const bounds = niceBounds(rtcPrev.concat(rtcNow, rtcAvg), 0.25);
      renderBroilerMixed('productionMonthlyChart', MON_SHORT, [
        dataset(String(rtcCur - 1), rtcPrev, DASH_COLORS.navy, { type: 'bar', backgroundColor: DASH_COLORS.navy }),
        dataset(String(rtcCur), rtcNow, DASH_COLORS.orange, { type: 'bar', backgroundColor: DASH_COLORS.orange }),
        dataset(rtcAvgLabel, rtcAvg, DASH_COLORS.gold, {
          type: 'line', showLine: false, borderWidth: 2, pointStyle: 'rectRot', pointRadius: 7, pointHoverRadius: 8,
          pointBackgroundColor: DASH_COLORS.gold, pointBorderColor: DASH_COLORS.navy
        })
      ], 'Billion lb', undefined, Object.assign({
        yTickCallback: tickFmt({ suffix: 'B' }),
        tooltip: { callbacks: { title: items => items[0].label, label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: ${fmtNum(c.parsed.y, 2)}B lb`) } }
      }, bounds));
      broilerText('productionMonthlySub', `Ready-to-cook broiler meat by month: ${rtcCur - 1} and ${rtcCur} as bars, the ${rtcAvgYears[0]}–${rtcAvgYears[rtcAvgYears.length - 1]} average as diamonds`);
    }
  });

  registerRangeControl({
    chartId: 'productionYoYChart',
    options: [],
    defaultRange: 'all',
    renderer() {
      const yoy = rtcNow.map((v, i) => (v != null && rtcPrev[i] ? (v / rtcPrev[i] - 1) * 100 : null));
      renderBroilerMixed('productionYoYChart', MON_SHORT, [yoyBars(`${rtcCur} vs ${rtcCur - 1}`, yoy)],
        '% vs same month last year', undefined, {
          legend: false,
          yTickCallback: tickFmt({ suffix: '%', sign: true }),
          tooltip: { callbacks: { title: items => items[0].label, label: c => (c.parsed?.y == null ? '' : signed(c.parsed.y)) } }
        });
      broilerText('productionYoYSub', `${rtcCur} ready-to-cook production, % change from the same month of ${rtcCur - 1}`);
    }
  });

  registerRangeControl({
    chartId: 'productionYtdChart',
    options: [],
    defaultRange: 'all',
    renderer() {
      const ytd = arr => arr.slice(0, rtcLastMonth + 1).reduce((sum, v) => sum + (v || 0), 0);
      const avgYtd = rtcAvgYears.reduce((sum, y) => sum + ytd(monthsForYear(rtcMap, y)), 0) / rtcAvgYears.length;
      const vals = [avgYtd, ytd(rtcPrev), ytd(rtcNow)];
      const span = rtcLastMonth === 0 ? 'January' : `January to ${MON_SHORT[rtcLastMonth]}`;
      const valueLabels = {
        id: 'valueLabels',
        afterDatasetsDraw(chart) {
          const c = chart.ctx;
          c.save();
          c.font = `600 ${isMobileWidth() ? 11 : 13}px Lexend`;
          c.fillStyle = DASH_COLORS.navy;
          c.textAlign = 'center';
          chart.getDatasetMeta(0).data.forEach((bar, i) => c.fillText(`${fmtNum(vals[i], 1)}B`, bar.x, bar.y - 8));
          c.restore();
        }
      };
      renderBroilerMixed('productionYtdChart', [rtcAvgLabel, String(rtcCur - 1), String(rtcCur)], [
        dataset(`${span} total`, vals, DASH_COLORS.navy, { type: 'bar', backgroundColor: ['#B9C2C8', DASH_COLORS.navy, DASH_COLORS.orange] })
      ], 'Billion lb', undefined, {
        legend: false, plugins: [valueLabels], yMin: 0, yMax: niceBounds([0, Math.max(...vals) * 1.12], 0).yMax,
        yTickCallback: tickFmt({ suffix: 'B' }),
        tooltip: { callbacks: { title: items => items[0].label, label: c => `${fmtNum(c.parsed.y, 2)}B lb` } }
      });
      broilerText('productionYtdSub', `Ready-to-cook production, ${span}: ${rtcCur} against ${rtcCur - 1} and the ${rtcAvgYears[0]}–${rtcAvgYears[rtcAvgYears.length - 1]} average`);
    }
  });

  registerRangeControl({
    chartId: 'productionDriversChart',
    options: ['5y', '10y', 'all'],
    defaultRange: '10y',
    renderer(range) {
      const { start, end } = getRangeSlice(PD.dates, range);
      const birds = PD.head_12m_yoy.slice(start, end);
      const weight = PD.weight_12m_yoy.slice(start, end);
      const live = PD.live_12m_yoy.slice(start, end);
      renderBroilerMixed('productionDriversChart', PD.dates.slice(start, end), [
        dataset('Birds slaughtered', birds, DASH_COLORS.navy, { type: 'bar', backgroundColor: DASH_COLORS.navy, stack: 'parts' }),
        dataset('Average live weight', weight, DASH_COLORS.gold, { type: 'bar', backgroundColor: DASH_COLORS.gold, stack: 'parts' }),
        dataset('Live pounds', live, '#1F9EBC', { type: 'line', stack: 'total', borderWidth: 2.8 })
      ], '% vs year ago, trailing 12 months', undefined, {
        stacked: true,
        yTickCallback: tickFmt({ suffix: '%', sign: true }),
        tooltip: pctTooltip
      });
    }
  });

  registerRangeControl({
    chartId: 'liveWeightChart',
    options: ['5y', '10y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(PD.dates, range);
      const monthly = PD.weight.slice(start, end);
      renderLineChart('liveWeightChart', PD.dates.slice(start, end), [
        dataset('Monthly', monthly, 'rgba(246,133,31,0.4)', { borderWidth: 1.6, order: 5 }),
        dataset('12-month average', PD.weight_12m.slice(start, end), DASH_COLORS.navy, { order: 0 })
      ], 'lb per bird, live', Object.assign({
        yTickCallback: tickFmt(),
        tooltip: { callbacks: { label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: ${fmtNum(c.parsed.y, 2)} lb`) } }
      }, niceBounds(monthly, 0.08)));
    }
  });

  const ante12 = fullRollingAverage(PD.ante_pct, 12);
  const post12 = fullRollingAverage(PD.post_pct, 12);
  registerRangeControl({
    chartId: 'condemnChart',
    options: ['5y', '10y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(PD.dates, range);
      renderLineChart('condemnChart', PD.dates.slice(start, end), [
        dataset('After slaughter, % of carcass weight', post12.slice(start, end), DASH_COLORS.navy),
        dataset('Before slaughter, % of birds', ante12.slice(start, end), DASH_COLORS.orange)
      ], '% condemned', {
        yMin: 0,
        yTickCallback: tickFmt({ suffix: '%' }),
        tooltip: { callbacks: { label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: ${fmtNum(c.parsed.y, 2)}%`) } }
      });
    }
  });

  const ST = PD.states;
  if (ST && (ST.abbr || []).length) {
    broilerText('stateProductionSub', `Annual broiler production by state, live weight: ${ST.year} vs ${ST.base_year}. The ten largest states produced ${fmtNum(ST.values.reduce((a, b) => a + b, 0) / ST.national * 100, 0)}% of the U.S. total in ${ST.year}`);
    registerRangeControl({
      chartId: 'stateProductionChart',
      options: [],
      defaultRange: 'all',
      renderer() {
        renderBarChart('stateProductionChart', ST.abbr, [
          dataset(String(ST.base_year), ST.base_values.map(v => v != null ? v / 1e9 : null), DASH_COLORS.slate, { backgroundColor: '#B9C2C8' }),
          dataset(String(ST.year), ST.values.map(v => v / 1e9), DASH_COLORS.navy, { backgroundColor: DASH_COLORS.navy })
        ], 'Billion lb, live weight', {
          yTickCallback: tickFmt({ suffix: 'B' }),
          tooltip: { callbacks: {
            title: items => (items && items[0]) ? ST.names[items[0].dataIndex] : '',
            label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: ${fmtNum(c.parsed.y, 2)}B lb`)
          } }
        });
      }
    });
  }

  /* ── Prices ────────────────────────────────────────────── */
  const CUT_LABELS = {
    'Breast - B/S': 'Breast, boneless/skinless',
    Tenderloins: 'Tenderloins',
    'Wings - Whole': 'Wings, whole',
    'Thighs - B/S': 'Thighs, boneless/skinless',
    Drumsticks: 'Drumsticks',
    'Leg quarters - Bulk': 'Leg quarters, bulk',
    WOG: 'Whole bird (WOG)'
  };
  const CUT_COLORS = ['#F6851F', '#FDB714', '#1F9EBC', '#013046', '#8FCAE6', '#939598', '#7c2d12'];
  let cutMode = 'price';
  let cutSet = 'main';
  const MAIN_CUTS = ['Breast - B/S', 'Wings - Whole', 'Leg quarters - Bulk', 'WOG'];
  const renderCuts = range => {
    const { start, end } = getRangeSlice(W.dates, range);
    const allCuts = Object.keys(W.series);
    const cuts = cutSet === 'main' ? allCuts.filter(c => MAIN_CUTS.includes(c)) : allCuts;
    const src = cutMode === 'price' ? W.series : W.yoy;
    renderLineChart('wholesaleCutsChart', W.dates.slice(start, end),
      cuts.map(cut => dataset(CUT_LABELS[cut] || cut, src[cut].slice(start, end), CUT_COLORS[allCuts.indexOf(cut) % CUT_COLORS.length], { borderWidth: 2.6 })),
      cutMode === 'price' ? '¢ / lb' : '% vs year ago',
      cutMode === 'price' ? {} : { yTickCallback: tickFmt({ suffix: '%', sign: true }), tooltip: pctTooltip });
  };
  registerRangeControl({ chartId: 'wholesaleCutsChart', options: ['3m', '6m', '1y', '2y', 'all'], defaultRange: '1y', renderer: renderCuts });
  insertModeToggle('wholesaleCutsChart', [
    { mode: 'price', label: 'Price' },
    { mode: 'yoy', label: '% vs year ago' }
  ], 'price', mode => { cutMode = mode; renderCuts(chartRanges.wholesaleCutsChart || '1y'); });
  {
    // Second toggle: the four headline cuts, or all seven.
    const toolbar = document.getElementById('wholesaleCutsChart').closest('.card').querySelector('.chart-toolbar');
    const host = document.createElement('div');
    host.className = 'mode-controls';
    host.innerHTML = '<button class="mode-btn active" type="button" data-chart="wholesaleCutSet" data-mode="main">Main cuts</button>' +
      '<button class="mode-btn" type="button" data-chart="wholesaleCutSet" data-mode="all">All 7</button>';
    toolbar.querySelector('.mode-controls').insertAdjacentElement('afterend', host);
    modeHandlers.wholesaleCutSet = { current: 'main', onChange: mode => { cutSet = mode; renderCuts(chartRanges.wholesaleCutsChart || '1y'); } };
  }

  const R = B.retail;
  const RETAIL_LABELS = {
    'Breast, Boneless/Skinless': 'Breast, B/S',
    'Thighs, Boneless/Skinless': 'Thighs, B/S',
    Drumsticks: 'Drumsticks',
    'Leg Quarters': 'Leg quarters',
    'Party Wings, Flats and Drums': 'Party wings',
    'Whole Bagged Fryer': 'Whole bagged fryer'
  };
  const retailSmooth = Object.fromEntries(Object.entries(R.series).map(([k, v]) => [k, rollingAverage(v, 8)]));
  registerRangeControl({
    chartId: 'retailChickenChart',
    options: ['6m', '1y', '2y', '3y', 'all'],
    defaultRange: '2y',
    renderer(range) {
      const { start, end } = getRangeSlice(R.dates, range);
      renderLineChart('retailChickenChart', R.dates.slice(start, end),
        Object.keys(retailSmooth).map((k, i) => dataset(RETAIL_LABELS[k] || k, retailSmooth[k].slice(start, end), CUT_COLORS[i % CUT_COLORS.length], { borderWidth: 2.6 })),
        '$ / lb', { yTickCallback: tickFmt({ prefix: '$' }) });
    }
  });

  const PR = B.price_received;
  const pr12 = rollingAverage(PR.values, 12);
  registerRangeControl({
    chartId: 'pricesReceivedChart',
    options: ['3y', '5y', '10y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const { start, end } = getRangeSlice(PR.dates, range);
      const monthly = PR.values.slice(start, end);
      renderLineChart('pricesReceivedChart', PR.dates.slice(start, end), [
        dataset('Monthly', monthly, 'rgba(246,133,31,0.55)', { borderWidth: 1.8, order: 5 }),
        dataset('12-month average', pr12.slice(start, end), DASH_COLORS.navy, { order: 0 })
      ], '$ / lb live weight', Object.assign({
        yTickCallback: tickFmt({ prefix: '$' }),
        tooltip: { callbacks: { label: c => (c.parsed?.y == null ? '' : `${c.dataset.label}: $${fmtNum(c.parsed.y, 3)}`) } }
      }, niceBounds(monthly, 0.1)));
    }
  });

  /* ── Feed and margin ──────────────────────────────────── */
  const F = B.feed;
  registerRangeControl({
    chartId: 'feedCostChart',
    options: ['3m', '6m', '1y', '2y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(F.dates, range);
      renderLineChart('feedCostChart', F.dates.slice(start, end), [
        dataset('Corn + soybean meal per ton of feed', F.cost_per_ton.slice(start, end), DASH_COLORS.gold)
      ], '$ / ton', { yTickCallback: tickFmt({ prefix: '$' }) });
    }
  });

  const RT = B.broiler_feed_ratio;
  const ratioAvg = RT.ratio.reduce((a, b) => a + b, 0) / (RT.ratio.length || 1);
  registerRangeControl({
    chartId: 'feedRatioChart',
    options: ['2y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(RT.dates, range);
      const labels = RT.dates.slice(start, end);
      renderLineChart('feedRatioChart', labels, [
        dataset('Broiler-to-feed ratio', RT.ratio.slice(start, end), DASH_COLORS.teal),
        dataset(`Average since ${fmtYM(RT.dates[0])}`, labels.map(() => ratioAvg), DASH_COLORS.slate, { borderDash: [6, 5], borderWidth: 2.2 })
      ], 'lb of feed per lb live broiler', { yTickCallback: tickFmt() });
    }
  });

  /* ── Storage and trade ────────────────────────────────── */
  const CS = B.cold_storage;
  let coldMode = 'seasonal';
  const renderCold = range => {
    if (coldMode === 'seasonal') {
      const sets = seasonalDatasets(CS.dates, CS.values.map(v => v / 1e6), range, 2012);
      renderBroilerMixed('coldStorageChart', MON_SHORT, sets, 'Million lb', undefined,
        Object.assign({ yTickCallback: tickFmt({ suffix: 'M' }) }, niceBounds(sets.flatMap(s => s.data), 0.4)));
      return;
    }
    const { start, end } = getRangeSlice(CS.dates, range);
    renderBarChart('coldStorageChart', CS.dates.slice(start, end), [yoyBars('Change vs year ago', CS.yoy.slice(start, end))],
      '% vs year ago', { yTickCallback: tickFmt({ suffix: '%', sign: true }), tooltip: pctTooltip });
  };
  registerRangeControl({ chartId: 'coldStorageChart', options: ['3y', '5y', '10y'], defaultRange: '5y', renderer: renderCold });
  insertModeToggle('coldStorageChart', [
    { mode: 'seasonal', label: 'Seasonal' },
    { mode: 'yoy', label: '% vs year ago' }
  ], 'seasonal', mode => { coldMode = mode; renderCold(chartRanges.coldStorageChart || '5y'); });

  const X = B.exports;
  if ((X.dates || []).length) {
    let exportMode = 'total';
    const total12 = rollingAverage(X.total, 12);
    const EXPORT_COLORS = ['#013046', '#1F9EBC', '#F6851F', '#FDB714', '#8FCAE6', '#7c2d12', '#0a4561', '#E5700A',
      '#5B8C2A', '#9B4F96', '#B8860B', '#2F6F73', '#C0504D', '#6B7A8F', '#D99694', '#4B3B2B'];
    const countryColor = Object.fromEntries(Object.keys(X.countries).map((n, i) => [n, EXPORT_COLORS[i % EXPORT_COLORS.length]]));
    countryColor.China = '#C0504D';
    const renderExports = range => {
      const { start, end } = getRangeSlice(X.dates, range);
      const labels = X.dates.slice(start, end);
      const toM = arr => arr.slice(start, end).map(v => v != null ? v / 1000 : null);
      if (exportMode === 'country') {
        // Top 8 destinations ranked over the selected range among all countries, plus China.
        const top = X.top_by_range[range] || X.top_by_range.all;
        const other = X.total.map((t, i) => (t == null ? null : Math.max(t - top.reduce((a, n) => a + (X.countries[n][i] || 0), 0), 0)));
        const sets = top.map(n => dataset(n, toM(X.countries[n]), countryColor[n], { backgroundColor: countryColor[n] }));
        sets.push(dataset('All other', toM(other), '#C7CDD1', { backgroundColor: '#C7CDD1' }));
        renderBarChart('exportsChart', labels, sets, 'Million lb', { stacked: true });
        return;
      }
      renderBroilerMixed('exportsChart', labels, [
        dataset('Broiler exports', toM(X.total), DASH_COLORS.navy, { type: 'bar', backgroundColor: DASH_COLORS.navy }),
        dataset('12-month average', toM(total12), DASH_COLORS.orange, { type: 'line' })
      ], 'Million lb', undefined, {});
    };
    registerRangeControl({ chartId: 'exportsChart', options: ['3y', '5y', '10y', 'all'], defaultRange: '5y', renderer: renderExports });
    insertModeToggle('exportsChart', [
      { mode: 'total', label: 'Total' },
      { mode: 'country', label: 'By destination' }
    ], 'total', mode => { exportMode = mode; renderExports(chartRanges.exportsChart || '5y'); });
  } else {
    showPlaceholder('exportsWrap', 'ERS broiler export data is not loaded in this build.');
  }

  /* ── Avian influenza ──────────────────────────────────── */
  const HP = B.hpai;
  {
    const lastMonth = HP.dates[HP.dates.length - 1];
    const node = document.getElementById('hpaiBroilerChart')?.closest('.card')?.querySelector('.card-source');
    if (node && HP.data_through && lastMonth && HP.data_through.slice(0, 7) === lastMonth) {
      node.insertAdjacentText('beforeend', ` • ${fmtYM(lastMonth)} is month to date (all poultry detections through ${fmtDate(HP.data_through)})`);
    }
    if (node && HP.last_broiler) {
      node.insertAdjacentText('beforeend', ` • Most recent broiler flock: ${fmtDate(HP.last_broiler.date)}, ${HP.last_broiler.county} County, ${HP.last_broiler.state} • Grey: "Commercial Breeder Operation" flocks, for which APHIS does not state the species`);
    }
  }
  const HPAI_COLORS = { 'Broiler production': DASH_COLORS.red, 'Broiler breeders': DASH_COLORS.orange, 'Breeder pullets': DASH_COLORS.gold, 'Breeders, species not stated': '#B9C2C8' };
  registerRangeControl({
    chartId: 'hpaiBroilerChart',
    options: ['1y', '3y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(HP.dates, range);
      const sets = Object.keys(HP.birds).map(g => dataset(g, HP.birds[g].slice(start, end).map(v => v / 1e6), HPAI_COLORS[g], { type: 'bar', backgroundColor: HPAI_COLORS[g], stack: 'birds' }));
      sets.push(dataset('Flocks detected', HP.detections.slice(start, end), DASH_COLORS.navy, {
        type: 'line', yAxisID: 'y2', showLine: false, pointRadius: c => (c.raw ? 4 : 0), pointBackgroundColor: DASH_COLORS.navy
      }));
      renderBroilerMixed('hpaiBroilerChart', HP.dates.slice(start, end), sets, 'Million birds', 'Flocks detected', {
        stacked: true,
        yTickCallback: tickFmt({ suffix: 'M' }),
        tooltip: { filter: item => item.raw != null && item.raw !== 0 }
      });
    }
  });
}

function setAllLatest(B) {
  const H = B.hatchability;
  const hatchLast = latestDay(lastDateOf(H.dates, H.values));
  setLatest('hatchabilityChart', `week ending ${hatchLast}`);
  setLatest('hatchAnnualChart', `week ending ${hatchLast}`);
  setLatest('hatchSeasonalChart', `week ending ${hatchLast}`);
  const BR = B.breeder;
  setLatest('breederHensChart', latestMonth(lastDateOf(BR.dates, BR.hens)));
  setLatest('breederProductivityChart', latestMonth(lastDateOf(BR.dates, BR.chicks_per_hen)));
  setLatest('pulletPipelineChart', `hens ${latestMonth(lastDateOf(BR.dates, BR.hens))}; pullets placed ${latestMonth(BR.pullet_dates[BR.pullet_dates.length - 1])}`);
  setLatest('placementsYoYChart', `week ending ${latestDay(lastDateOf(B.placements.dates, B.placements.values))}`);
  setLatest('placementsWeeklyChart', `week ending ${latestDay(lastDateOf(B.placements.dates, B.placements.values))}`);
  setLatest('chicksHatchedChart', latestMonth(lastDateOf(B.chicks_hatched.dates, B.chicks_hatched.values)));
  const PDL = latestMonth(B.production.dates[B.production.dates.length - 1]);
  ['productionChart', 'productionMonthlyChart', 'productionYoYChart', 'productionYtdChart', 'productionDriversChart', 'liveWeightChart', 'condemnChart'].forEach(id => setLatest(id, PDL));
  if (B.production.states && B.production.states.year) setLatest('stateProductionChart', String(B.production.states.year));
  const W = B.wholesale;
  setLatest('wholesaleCutsChart', `week of ${latestDay(W.dates[W.dates.length - 1])}`);
  setLatest('retailChickenChart', `week of ${latestDay(B.retail.dates[B.retail.dates.length - 1])}`);
  setLatest('pricesReceivedChart', latestMonth(lastDateOf(B.price_received.dates, B.price_received.values)));
  setLatest('feedCostChart', latestDay(B.feed.dates[B.feed.dates.length - 1]));
  setLatest('feedRatioChart', latestMonth(B.broiler_feed_ratio.dates[B.broiler_feed_ratio.dates.length - 1]));
  setLatest('coldStorageChart', latestMonth(lastDateOf(B.cold_storage.dates, B.cold_storage.values)));
  if ((B.exports.dates || []).length) setLatest('exportsChart', latestMonth(B.exports.dates[B.exports.dates.length - 1]));
}

bootBroilerDashboard().catch(error => {
  console.error(error);
  showPlaceholder('hatchabilityWrap', `Error loading broiler dashboard: ${error.message}`);
});
