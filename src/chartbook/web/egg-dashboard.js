function setText(id, text) {
  const node = document.getElementById(id);
  if (node) node.textContent = text;
}

function fmtBirdCount(value) {
  if (value == null || Number.isNaN(value)) return '0 birds';
  return `${Math.round(value).toLocaleString()} birds`;
}

function fmtLongDateLabel(dateStr) {
  if (!dateStr) return '';
  const date = new Date(`${dateStr}T00:00:00`);
  if (Number.isNaN(date.getTime())) return dateStr;
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function fmtCompactMillions(value) {
  if (value == null || Number.isNaN(value)) return '';
  return `${fmtNum(value, Number.isInteger(value) ? 0 : 1)}M`;
}

function slugifyText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function setChartSources() {
  const sourceMap = {
    retailFeatureChart: 'Chart: Innovate Animal Ag • Source: <a href="https://mymarketnews.ams.usda.gov/viewReport/2757" target="_blank" rel="noreferrer">USDA AMS Weekly Retail Egg Feature Activity</a>',
    pulletClimbChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    hpaiDetectionsChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/poultry" target="_blank" rel="noreferrer">USDA APHIS Poultry HPAI Detections</a>',
    hpaiLayersChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/poultry" target="_blank" rel="noreferrer">USDA APHIS Poultry HPAI Detections</a>',
    monthlyProdChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    trailingProdChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    rolChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    breakersChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    eggInventoryChart: 'Chart: Innovate Animal Ag • Source: <a href="https://mymarketnews.ams.usda.gov/viewReport/1427" target="_blank" rel="noreferrer">USDA AMS National Weekly Shell Egg Inventory</a>',
    eggsProcessedMixChart: 'Chart: Innovate Animal Ag • Source: <a href="https://mymarketnews.ams.usda.gov/viewReport/1665" target="_blank" rel="noreferrer">USDA AMS Weekly Shell Eggs Processed Under Federal Inspection</a>',
    tableLayersChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    tableLayersTrendChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    turnoverChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    turnoverRateChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    moltChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    compositionChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.ams.usda.gov/market-news/egg-markets" target="_blank" rel="noreferrer">USDA AMS Egg Markets</a> and <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    breederFlockChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    chicksChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    chicksTrendChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    pipelineChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Chickens_and_Eggs/index.php" target="_blank" rel="noreferrer">USDA NASS Chickens and Eggs</a>',
    wholesaleChart: 'Chart: Innovate Animal Ag • Source: <a href="https://mymarketnews.ams.usda.gov/viewReport/2843" target="_blank" rel="noreferrer">USDA AMS Daily National Shell Egg Index</a> and <a href="https://mymarketnews.ams.usda.gov/viewReport/3888" target="_blank" rel="noreferrer">USDA AMS Daily National Breaking Stock</a>',
    eggPriceCompareChart: 'Chart: Innovate Animal Ag • Source: <a href="https://fred.stlouisfed.org/series/APU0000708111" target="_blank" rel="noreferrer">FRED APU0000708111</a>',
    eggPriceSpreadChart: 'Chart: Innovate Animal Ag • Source: <a href="https://fred.stlouisfed.org/series/APU0000708111" target="_blank" rel="noreferrer">FRED APU0000708111</a> and <a href="https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Prices_Received_and_Prices_Received_Indexes/" target="_blank" rel="noreferrer">USDA NASS Agricultural Prices</a>',
    feedIndexChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html" target="_blank" rel="noreferrer">CME Group delayed quotes</a>',
    dieselChart: 'Chart: Innovate Animal Ag • Sources: <a href="https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html" target="_blank" rel="noreferrer">CME Group delayed quotes</a> · <a href="https://fred.stlouisfed.org/series/GASDESW" target="_blank" rel="noreferrer">FRED GASDESW</a> · <a href="https://fred.stlouisfed.org/series/PCU322219322219" target="_blank" rel="noreferrer">FRED PCU322219322219</a>',
    regionalEggChart: 'Chart: Innovate Animal Ag • Source: <a href="https://mymarketnews.ams.usda.gov/viewReport/2848" target="_blank" rel="noreferrer">USDA AMS Weekly Combined Regional Shell Egg Report</a>',
    eggImportsTradeChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.ers.usda.gov/data-products/livestock-and-meat-international-trade-data" target="_blank" rel="noreferrer">USDA ERS Livestock and Meat International Trade Data</a>',
    eggExportsTradeChart: 'Chart: Innovate Animal Ag • Source: <a href="https://www.ers.usda.gov/data-products/livestock-and-meat-international-trade-data" target="_blank" rel="noreferrer">USDA ERS Livestock and Meat International Trade Data</a>'
  };

  Object.entries(sourceMap).forEach(([chartId, html]) => {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;
    const card = canvas.closest('.card');
    if (!card) return;
    let sourceNode = card.querySelector('.card-source');
    if (!sourceNode) {
      sourceNode = document.createElement('div');
      sourceNode.className = 'card-source';
      card.appendChild(sourceNode);
    }
    sourceNode.innerHTML = html;
  });
}

function initEggSidebarNav() {
  const nav = document.getElementById('eggSidebarNav');
  if (!nav) return;
  const sections = Array.from(document.querySelectorAll('.section[id]'));
  if (!sections.length) return;
  const chartEntries = [];

  const usedIds = new Set(Array.from(document.querySelectorAll('[id]')).map(node => node.id));
  const makeUniqueId = base => {
    let candidate = base || 'chart';
    let suffix = 2;
    while (usedIds.has(candidate)) {
      candidate = `${base}-${suffix}`;
      suffix += 1;
    }
    usedIds.add(candidate);
    return candidate;
  };

  sections.forEach(section => {
    Array.from(section.querySelectorAll('.card')).forEach(card => {
      if (card.id) return;
      const title = card.querySelector('h3')?.textContent?.trim() || 'chart';
      card.id = makeUniqueId(slugifyText(title));
    });
  });

  nav.innerHTML = '';
  const sectionGroups = sections.map(section => {
    const group = document.createElement('div');
    group.className = 'sidebar-group';
    group.dataset.section = section.id;

    const sectionLink = document.createElement('a');
    sectionLink.className = 'sidebar-section-link';
    sectionLink.href = `#${section.id}`;
    sectionLink.textContent = section.querySelector('.section-head h2')?.textContent?.trim() || section.id;
    group.appendChild(sectionLink);

    const chartLinks = document.createElement('div');
    chartLinks.className = 'sidebar-chart-links';
    Array.from(section.querySelectorAll('.card')).forEach(card => {
      const title = card.querySelector('h3')?.textContent?.trim();
      if (!title) return;
      const link = document.createElement('a');
      link.className = 'sidebar-chart-link';
      link.href = `#${card.id}`;
      link.textContent = title;
      link.dataset.chart = card.id;
      chartLinks.appendChild(link);
      chartEntries.push({
        card,
        link,
        sectionId: section.id
      });
    });
    group.appendChild(chartLinks);
    nav.appendChild(group);
    return group;
  });

  const setActiveState = (sectionId, chartId) => {
    sectionGroups.forEach(group => {
      const isActive = group.dataset.section === sectionId;
      group.classList.toggle('is-active', isActive);
      const link = group.querySelector('.sidebar-section-link');
      if (link) {
        if (isActive) {
          link.setAttribute('aria-current', 'true');
        } else {
          link.removeAttribute('aria-current');
        }
      }
    });

    chartEntries.forEach(entry => {
      const isActiveChart = entry.card.id === chartId;
      entry.link.classList.toggle('is-active', isActiveChart);
      if (isActiveChart) {
        entry.link.setAttribute('aria-current', 'true');
      } else {
        entry.link.removeAttribute('aria-current');
      }
    });
  };

  const updateActiveSidebarState = () => {
    const offset = window.innerHeight * 0.22;
    let activeSectionId = sections[0].id;
    sections.forEach(section => {
      if (section.getBoundingClientRect().top - offset <= 0) {
        activeSectionId = section.id;
      }
    });

    const sectionCharts = chartEntries.filter(entry => entry.sectionId === activeSectionId);
    let activeChartId = sectionCharts[0]?.card.id || null;
    sectionCharts.forEach(entry => {
      if (entry.card.getBoundingClientRect().top - offset <= 0) {
        activeChartId = entry.card.id;
      }
    });

    setActiveState(activeSectionId, activeChartId);
  };

  updateActiveSidebarState();
  window.addEventListener('scroll', updateActiveSidebarState, { passive: true });
  window.addEventListener('resize', updateActiveSidebarState);
}

function alignValues(primaryDates, secondaryDates, secondaryValues) {
  const map = Object.fromEntries(secondaryDates.map((date, idx) => [date, secondaryValues[idx]]));
  return primaryDates.map(date => map[date] ?? null);
}

function seasonalPayload(dates, values, range, minYear) {
  const map = buildYearMonthMap(dates, values);
  const years = Object.keys(map).map(Number).sort((a, b) => a - b);
  const current = years[years.length - 1];
  const previous = years.includes(current - 1) ? current - 1 : years[years.length - 2];
  const historyPool = years.filter(year => year < previous && (!minYear || year >= minYear));
  const avgYears = historyYearsForRange(historyPool, range, minYear);
  return {
    current,
    previous,
    currentValues: monthsForYear(map, current),
    previousValues: previous ? monthsForYear(map, previous) : Array(12).fill(null),
    averageValues: avgYears.length ? averageMonths(map, avgYears) : Array(12).fill(null),
    averageLabel: avgYears.length ? `${avgYears[0]}-${avgYears[avgYears.length - 1]} Avg` : 'History Avg'
  };
}

function boostEggLineDataset(entry) {
  const effectiveType = entry.type || 'line';
  if (effectiveType !== 'line') return entry;
  return Object.assign({}, entry, {
    borderWidth: (entry.borderWidth ?? 3.4) + 1
  });
}

function renderEggLineChart(id, labels, datasets, yLabel, extra = {}) {
  renderLineChart(id, labels, datasets.map(boostEggLineDataset), yLabel, extra);
}

function renderEggStackedAreaChart(id, labels, datasets, yLabel, y2Label, extra = {}) {
  renderStackedAreaChart(id, labels, datasets.map(boostEggLineDataset), yLabel, y2Label, extra);
}

function renderMixedChart(id, labels, datasets, yLabel, y2Label, extra = {}) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  const normalizedDatasets = datasets.map(entry => {
    const boosted = boostEggLineDataset(entry);
    return Object.assign(
      { order: boosted.type === 'line' ? 0 : 10 },
      boosted
    );
  });
  charts[id] = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: normalizedDatasets },
    options: baseOptions(yLabel, Object.assign({ chartId: id, y2: y2Label, maxTicks: 12 }, extra))
  });
}

async function bootEggDashboard() {
  initEggSidebarNav();
  setChartSources();
  const response = await fetch(`data.json?v=${Date.now()}`);
  const D = await response.json();

  document.title = `Egg Industry Dashboard — ${D.updated}`;
  setText('updatedStamp', D.updated);
  setText('coverageStamp', 'Monthly chartbook-inspired egg market view');
  setText('statusStamp', 'Fresh USDA + APHIS series powering egg supply, disease, and price monitoring');

  const pulletLatest = latestNonNull(D.nass_pullets.dates, D.nass_pullets.values);
  const feedLatest = latestNonNull(D.feed_index.dates || [], D.feed_index.index || []);
  if (D.feed_index.base_date) {
    const feedSub = document.getElementById('feedIndexSub');
    if (feedSub) {
      const comp = D.feed_index.composition || {};
      const cornPct = comp.corn != null ? Math.round(comp.corn * 100) : 67;
      const soyPct = comp.soymeal != null ? Math.round(comp.soymeal * 100) : 22;
      const calciumPct = comp.calcium != null ? Math.round(comp.calcium * 100) : 8;
      const otherPct = comp.other != null ? Math.round(comp.other * 100) : 3;
      feedSub.textContent = `${cornPct}% corn, ${soyPct}% soybean meal, ${calciumPct}% calcium, ${otherPct}% other`;
    }
  }
  setText('kpiEggPrice', D.kpi.egg_index_price != null ? `${fmtNum(D.kpi.egg_index_price, 2)}¢` : '—');
  setText('kpiEggPriceSub', D.kpi.egg_index_date ? `Wholesale large caged · ${fmtDate(D.kpi.egg_index_date)}` : 'Latest shell egg index');
  setText('kpiRetailEgg', D.kpi.retail_egg_price != null ? `$${fmtNum(D.kpi.retail_egg_price, 2)}` : '—');
  setText('kpiRetailEggSub', D.kpi.retail_egg_date ? `National retail · ${fmtDate(D.kpi.retail_egg_date)}` : 'Retail feature price');
  setText('kpiLayers', D.kpi.layer_count != null ? fmtM(D.kpi.layer_count) : '—');
  setText('kpiLayersSub', D.kpi.layer_period || 'Layer inventory');
  setText('kpiPullets', pulletLatest.value != null ? fmtM(pulletLatest.value) : '—');
  setText('kpiPulletsSub', pulletLatest.date ? `Replacement pullets · ${fmtYM(pulletLatest.date)}` : 'Replacement pullets');
  setText('kpiHpai', D.kpi.hpai_30d_detections != null ? fmtNum(D.kpi.hpai_30d_detections) : '—');
  setText('kpiHpaiSub', D.kpi.hpai_30d_birds ? `${fmtM(D.kpi.hpai_30d_birds)} birds in last 30 days` : '30-day HPAI activity');
  setText('kpiFeed', feedLatest.value != null ? fmtNum(feedLatest.value, 1) : 'N/A');
  setText('kpiFeedSub', feedLatest.date ? `Index 100 = ${fmtDate(D.feed_index.base_date)} · latest ${fmtDate(feedLatest.date)}` : 'Feed index not ingested');

  registerRangeControl({
    chartId: 'retailFeatureChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.retail_egg_feature.dates;
      const raw = D.retail_egg_feature.rate;
      const rolled = rollingAverage(D.retail_egg_feature.rate, 4);
      const { start, end } = getRangeSlice(dates, range);
      renderEggLineChart(
        'retailFeatureChart',
        dates.slice(start, end),
        [
          dataset('Weekly feature rate', raw.slice(start, end), 'rgba(1, 48, 70, 0.10)', {
            borderColor: 'rgba(1, 48, 70, 0.10)',
            backgroundColor: 'transparent',
            borderDash: [7, 5],
            borderWidth: 2.4,
            order: 10
          }),
          dataset('4-week average', rolled.slice(start, end), DASH_COLORS.orange, { order: 0 })
        ],
        'Feature rate (%)',
        { yMax: 60 }
      );
    }
  });

  registerRangeControl({
    chartId: 'pulletClimbChart',
    options: ['1y', '2y', '5y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const { start, end } = getRangeSlice(D.nass_pullets.dates, range);
      const minStart = D.nass_pullets.dates.findIndex(date => date >= '2016-01');
      const clampedStart = range === 'all' && minStart !== -1 ? Math.max(start, minStart) : start;
      renderBarChart(
        'pulletClimbChart',
        D.nass_pullets.dates.slice(clampedStart, end),
        [dataset('Pullets', D.nass_pullets.values.slice(clampedStart, end).map(v => v / 1e6), DASH_COLORS.navy, { backgroundColor: DASH_COLORS.navy, borderWidth: 1 })],
        'Pullets',
        { yMin: 112, yMax: 148, yTickCallback: value => fmtCompactMillions(value) }
      );
    }
  });

  registerRangeControl({
    chartId: 'hpaiDetectionsChart',
    options: ['1y', '3y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(D.hpai_summary.dates, range);
      renderBarChart(
        'hpaiDetectionsChart',
        D.hpai_summary.dates.slice(start, end),
        [dataset('Detections', D.hpai_summary.detections.slice(start, end), DASH_COLORS.navy, { backgroundColor: DASH_COLORS.navy, borderWidth: 1 })],
        'Detections'
      );
    }
  });

  registerRangeControl({
    chartId: 'hpaiLayersChart',
    options: ['1y', '3y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const { start, end } = getRangeSlice(D.hpai_layers.dates, range);
      const categoryBreakdown = (D.hpai_layers.categories || []).map(category => ({
        label: category,
        birds: (D.hpai_layers.birds_by_category?.[category] || []).slice(start, end)
      }));
      renderBarChart(
        'hpaiLayersChart',
        D.hpai_layers.dates.slice(start, end),
        [dataset('Commercial layers impacted', D.hpai_layers.birds.slice(start, end), DASH_COLORS.orange, {
          backgroundColor: DASH_COLORS.orange,
          borderWidth: 1,
          categoryBreakdown
        })],
        'Birds',
        {
          yTickCallback: value => fmtMillionsAxis(value),
          tooltip: {
            callbacks: {
              title(items) {
                if (!items.length) return '';
                const item = items[0];
                const totalBirds = item.parsed?.y || 0;
                return [item.label, `Total: ${fmtBirdCount(totalBirds)}`];
              },
              label(context) {
                const breakdown = context.dataset.categoryBreakdown || [];
                const lines = [];
                breakdown.forEach(entry => {
                  const birds = entry.birds?.[context.dataIndex] || 0;
                  if (birds) {
                    lines.push(`${entry.label}: ${fmtBirdCount(birds)}`);
                  }
                });
                return lines.length ? lines : [context.dataset.label];
              }
            }
          }
        }
      );
    }
  });

  registerRangeControl({
    chartId: 'trailingProdChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const dates = D.nass_egg_production.dates_table;
      const values = rollingSum(D.nass_egg_production.table.map(v => v / 1e9), 3);
      const { start, end } = getRangeSlice(dates, range);
      renderEggLineChart(
        'trailingProdChart',
        dates.slice(start, end),
        [dataset('3-month trailing table egg production', values.slice(start, end), '#a23508')],
        'Billion eggs',
        { yTickCallback: value => fmtNum(value, 1) }
      );
    }
  });

  registerRangeControl({
    chartId: 'monthlyProdChart',
    options: ['2y', '5y', '10y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const payload = seasonalPayload(D.nass_egg_production.dates_table, D.nass_egg_production.table.map(v => v / 1e9), range, 2010);
      renderMixedChart(
        'monthlyProdChart',
        MON_SHORT,
        [
          dataset(String(payload.previous), payload.previousValues, DASH_COLORS.navy, { type: 'bar', backgroundColor: DASH_COLORS.navy, borderWidth: 1 }),
          dataset(String(payload.current), payload.currentValues, DASH_COLORS.orange, { type: 'bar', backgroundColor: '#F6851F', borderWidth: 1 }),
          dataset(payload.averageLabel, payload.averageValues, DASH_COLORS.gold, {
            type: 'line',
            showLine: false,
            borderWidth: 0,
            pointStyle: 'rectRot',
            pointRadius: 7,
            pointHoverRadius: 8,
            pointBackgroundColor: DASH_COLORS.gold,
            pointBorderColor: DASH_COLORS.gold
          })
        ],
        'Billion eggs',
        undefined,
        { yMin: 6.5, yMax: 8.5 }
      );
    }
  });

  registerRangeControl({
    chartId: 'rolChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_rate_of_lay.dates_table;
      const values = D.nass_rate_of_lay.table;
      const avg = rollingAverage(values, 12);
      const { start, end } = getRangeSlice(dates, range);
      const axisBounds = range === 'all'
        ? { yMin: 75, yMax: 85 }
        : { yMin: 80, yMax: 84 };
      renderMixedChart(
        'rolChart',
        dates.slice(start, end),
        [
          dataset('Table layer rate of lay', values.slice(start, end), DASH_COLORS.navy, { type: 'bar', backgroundColor: DASH_COLORS.navy, borderWidth: 1 }),
          dataset('12-month average', avg.slice(start, end), DASH_COLORS.gold, { type: 'line', borderDash: [6, 4], backgroundColor: 'transparent' })
        ],
        'Eggs / 100 layers / day',
        undefined,
        axisBounds
      );
    }
  });

  registerRangeControl({
    chartId: 'breakersChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.nass_shell_broken.dates;
      const brokenEggs = D.nass_shell_broken.dozen.map(v => (v * 12) / 1e9);
      const tableProdBillions = alignValues(dates, D.nass_egg_production.dates_table, D.nass_egg_production.table).map(v => v != null ? v / 1e9 : null);
      const brokenShare = brokenEggs.map((value, idx) => value != null && tableProdBillions[idx] ? (value / tableProdBillions[idx]) * 100 : null);
      const { start, end } = getRangeSlice(dates, range);
      renderMixedChart(
        'breakersChart',
        dates.slice(start, end),
        [
          dataset('Eggs delivered to breakers', brokenEggs.slice(start, end), DASH_COLORS.orange, {
            backgroundColor: DASH_COLORS.orange,
            borderColor: DASH_COLORS.orange,
            type: 'bar'
          }),
          dataset('% of total production', brokenShare.slice(start, end), DASH_COLORS.navy, {
            yAxisID: 'y2',
            type: 'line',
            borderDash: [8, 6],
            totalProduction: tableProdBillions.slice(start, end)
          })
        ],
        'Billion eggs',
        '% of production',
        {
          yMin: 1.5,
          yMax: 2.75,
          y2Min: 27,
          y2Max: 35,
          tooltip: {
            callbacks: {
              footer(items) {
                if (!items.length) return '';
                const item = items.find(entry => entry.dataset?.totalProduction) || items[0];
                const totalProduction = item.dataset?.totalProduction?.[item.dataIndex];
                if (totalProduction == null) return '';
                return `Monthly table egg production: ${fmtNum(totalProduction, 1)}B`;
              }
            }
          }
        }
      );
    }
  });

  if ((D.egg_inventory.dates || []).length) {
    registerRangeControl({
      chartId: 'eggInventoryChart',
      options: ['6m', '1y', '3y', 'all'],
      defaultRange: '1y',
      renderer(range) {
        const dates = D.egg_inventory.dates;
        const { start, end } = getRangeSlice(dates, range);
        const regionOrder = ['6-Area', 'Midwest (MW)', 'Northeast (NE)', 'Northwest (NW)', 'South Central (SC)', 'Southeast (SE)', 'Southwest (SW)'];
        const regionColors = {
          '6-Area': DASH_COLORS.gold,
          'Midwest (MW)': DASH_COLORS.navy,
          'Northeast (NE)': DASH_COLORS.sky,
          'Northwest (NW)': DASH_COLORS.slate,
          'South Central (SC)': DASH_COLORS.orange,
          'Southeast (SE)': DASH_COLORS.teal,
          'Southwest (SW)': DASH_COLORS.redSoft
        };
        const seriesKeys = regionOrder.filter(key => D.egg_inventory.series[key]).concat(
          Object.keys(D.egg_inventory.series).filter(key => !regionOrder.includes(key))
        );
        const datasets = seriesKeys.map((key, idx) => dataset(
          key,
          D.egg_inventory.series[key].slice(start, end),
          regionColors[key] || DASH_COLORS.seq[idx % DASH_COLORS.seq.length],
          key === '6-Area'
            ? { borderDash: [7, 4] }
            : {}
        ));
        renderEggLineChart(
          'eggInventoryChart',
          dates.slice(start, end),
          datasets,
          'Cases'
        );
      }
    });
  } else {
    showPlaceholder('eggInventoryWrap', 'Weekly shell egg inventory is not loaded in this environment yet.');
  }

  if ((D.eggs_processed.dates || []).length) {
    registerRangeControl({
      chartId: 'eggsProcessedMixChart',
      options: ['6m', '1y', '3y', 'all'],
      defaultRange: '1y',
      renderer(range) {
        const dates = D.eggs_processed.dates;
        const classes = [
          ['Liquid Whole', DASH_COLORS.orange],
          ['Liquid White', DASH_COLORS.sky],
          ['Liquid Yolk', DASH_COLORS.navy],
          ['Dried', DASH_COLORS.gold]
        ];
        const totals = dates.map((_, idx) => classes.reduce((sum, [name]) => sum + (D.eggs_processed.series[name]?.[idx] || 0), 0));
        const { start, end } = getRangeSlice(dates, range);
        const datasets = classes.map(([name, color], idx) => dataset(
          name,
          dates.map((_, rowIdx) => {
            const total = totals[rowIdx];
            const value = D.eggs_processed.series[name]?.[rowIdx] || 0;
            return total ? (value / total) * 100 : null;
          }).slice(start, end),
          color,
          {
            stack: 'processed_mix',
            fill: idx === 0 ? 'origin' : '-1',
            order: 20,
            borderWidth: 2,
            pointRadius: 0,
            backgroundColor: color
          }
        ));
        renderEggStackedAreaChart(
          'eggsProcessedMixChart',
          dates.slice(start, end),
          datasets,
          '% of selected output',
          undefined,
          { yMin: 0, yMax: 100 }
        );
      }
    });
  } else {
    showPlaceholder('eggsProcessedMixWrap', 'Weekly processed-egg data is not loaded in this environment yet.');
  }

  insertRangeControls('tableLayersChart', []);
  {
    const map = buildYearMonthMap(D.nass_layers.dates_table, D.nass_layers.table);
    const historyYears = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024].filter(year => map[year]);
    const highlightedYears = [2025, 2026].filter(year => map[year]);
    const layerSets = [
      ...historyYears.map(year =>
        dataset(String(year), monthsForYear(map, year), 'rgba(154, 163, 171, 0.52)', {
          borderWidth: 1.8,
          backgroundColor: 'rgba(154, 163, 171, 0.52)',
          pointRadius: 0,
          pointHoverRadius: 0,
          order: 10,
          legendKey: 'history-table-layers',
          legendLabel: '2016-2024'
        })
      ),
      ...(map[2025] ? [dataset('2025', monthsForYear(map, 2025), DASH_COLORS.orange, {
        borderWidth: 4.4,
        order: 0
      })] : []),
      ...(map[2026] ? [dataset('2026', monthsForYear(map, 2026), DASH_COLORS.gold, {
        borderWidth: 4.4,
        order: 0
      })] : [])
    ];
    const fallbackYears = highlightedYears.length ? highlightedYears : historyYears.slice(-2);
    renderEggLineChart(
      'tableLayersChart',
      MON_SHORT,
      layerSets.length ? layerSets : fallbackYears.map(year => dataset(String(year), monthsForYear(map, year), DASH_COLORS.slate)),
      'Hens',
      { maxTicks: 12, yTickCallback: value => fmtMillionsAxis(value) }
    );
  }

  registerRangeControl({
    chartId: 'tableLayersTrendChart',
    options: ['1y', '3y', '5y', '10y', 'all'],
    defaultRange: '10y',
    renderer(range) {
      const dates = D.nass_layers.dates_table;
      const values = D.nass_layers.table.map(v => v != null ? v : null);
      const { start, end } = getRangeSlice(dates, range);
      renderEggLineChart(
        'tableLayersTrendChart',
        dates.slice(start, end),
        [dataset('Table-egg layers', values.slice(start, end), '#a23508')],
        'Hens',
        { yTickCallback: value => fmtMillionsAxis(value) }
      );
    }
  });

  registerRangeControl({
    chartId: 'turnoverChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_layer_disposition.dates_sales;
      const slaughter = D.nass_layer_disposition.sales.map(v => v / 1e6);
      const loss = alignValues(dates, D.nass_layer_disposition.dates_loss, D.nass_layer_disposition.loss).map(v => v != null ? v / 1e6 : null);
      const { start, end } = getRangeSlice(dates, range);
      renderBarChart(
        'turnoverChart',
        dates.slice(start, end),
        [
          dataset('Sold for slaughter', slaughter.slice(start, end), DASH_COLORS.navy, { backgroundColor: DASH_COLORS.navy, borderWidth: 1 }),
          dataset('Rendered, Died, Destroyed, Composted, or Disappeared', loss.slice(start, end), DASH_COLORS.sky, { backgroundColor: DASH_COLORS.sky, borderWidth: 1 })
        ],
        'Hens',
        {
          stacked: true,
          yTickCallback: value => fmtMillionsAxis(value * 1e6),
          tooltip: {
            callbacks: {
              title(items) {
                if (!items.length) return '';
                const total = items.reduce((sum, item) => sum + (item.parsed?.y || 0), 0);
                return [fmtTooltipDate(items[0].label), `Total: ${fmtNum(total, 1)}M`];
              },
              label(context) {
                const value = Number(context.parsed?.y || 0);
                return `${context.dataset.label}: ${fmtNum(value, 1)}M`;
              }
            }
          }
        }
      );
    }
  });

  registerRangeControl({
    chartId: 'turnoverRateChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_layer_disposition.dates_sales;
      const slaughter = D.nass_layer_disposition.sales;
      const loss = alignValues(dates, D.nass_layer_disposition.dates_loss, D.nass_layer_disposition.loss).map(v => v != null ? v : 0);
      const tableLayers = alignValues(dates, D.nass_layers.dates_table, D.nass_layers.table);
      const turnoverRate = dates.map((_, idx) => {
        const flock = tableLayers[idx];
        if (flock == null || flock <= 0) return null;
        return (((slaughter[idx] || 0) + (loss[idx] || 0)) / flock) * 100;
      });
      const { start, end } = getRangeSlice(dates, range);
      const chartLabels = dates.slice(start, end);
      const chartTurnover = dates.map((_, idx) => (slaughter[idx] || 0) + (loss[idx] || 0)).slice(start, end);
      const chartFlock = tableLayers.slice(start, end);
      const chartRates = turnoverRate.slice(start, end);
      const chartDataset = dataset('Flock turnover rate', chartRates, DASH_COLORS.orange, {
        backgroundColor: DASH_COLORS.orange,
        borderWidth: 1,
        totalTurnover: chartTurnover,
        flockSize: chartFlock
      });
      const chartExtra = {
        yMin: range === 'all' ? undefined : 5,
        yMax: range === 'all' ? undefined : 14,
        tooltip: {
          callbacks: {
            title(items) {
              if (!items.length) return '';
              return fmtTooltipDate(items[0].label);
            },
            label(context) {
              const value = Number(context.parsed?.y || 0);
              const totalTurnover = context.dataset.totalTurnover?.[context.dataIndex] || 0;
              const flockSize = context.dataset.flockSize?.[context.dataIndex] || 0;
              return [
                `${context.dataset.label}: ${fmtNum(value, 1)}%`,
                `Total Turnover: ${fmtNum(totalTurnover / 1e6, 1)}M`,
                `Total Flock Size: ${fmtNum(flockSize / 1e6, 1)}M`
              ];
            }
          }
        }
      };
      renderBarChart(
        'turnoverRateChart',
        chartLabels,
        [chartDataset],
        '% of flock',
        chartExtra
      );
    }
  });

  registerRangeControl({
    chartId: 'moltChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const dates = D.nass_layer_disposition.dates_molted;
      const beingMolted = D.nass_layer_disposition.being_molted_pct;
      const moltCompleted = alignValues(
        dates,
        D.nass_layer_disposition.dates_molt_completed || [],
        D.nass_layer_disposition.molt_completed_pct || []
      );
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'moltChart',
        dates.slice(start, end),
        [
          dataset('Being molted', beingMolted.slice(start, end), DASH_COLORS.gold),
          dataset('Molt completed', moltCompleted.slice(start, end), DASH_COLORS.navy)
        ],
        '% of commercial egg-type layer flock'
      );
    }
  });

  if ((D.cage_free_composition.dates || []).length) {
    registerRangeControl({
      chartId: 'compositionChart',
      options: ['1y', '3y', 'all'],
      defaultRange: 'all',
      renderer(range) {
        const dates = D.cage_free_composition.dates;
        const { start, end } = getRangeSlice(dates, range);
        renderEggStackedAreaChart(
          'compositionChart',
          dates.slice(start, end),
          [
            dataset('Organic', D.cage_free_composition.organic.slice(start, end).map(v => v != null ? v * 1e6 : null), '#D9F0C2', {
              stack: 'flock',
              fill: 'origin',
              order: 20,
              borderWidth: 1.6,
              pointRadius: 0,
              backgroundColor: '#D9F0C2'
            }),
            dataset('Non-Organic Cage-Free', D.cage_free_composition.non_organic_cage_free.slice(start, end).map(v => v != null ? v * 1e6 : null), DASH_COLORS.sky, {
              stack: 'flock',
              fill: '-1',
              order: 20,
              borderWidth: 1.6,
              pointRadius: 0,
              backgroundColor: '#8FCAE6'
            }),
            dataset('Conventional', D.cage_free_composition.conventional.slice(start, end).map(v => v != null ? v * 1e6 : null), DASH_COLORS.navy, {
              stack: 'flock',
              fill: '-1',
              order: 20,
              borderWidth: 1.6,
              pointRadius: 0,
              backgroundColor: '#013046'
            }),
            dataset('Cage-Free %', D.cage_free_composition.cage_free_pct.slice(start, end), DASH_COLORS.orange, {
              yAxisID: 'y2',
              order: 0,
              borderDash: [8, 6],
              borderWidth: 3.2,
              fill: false
            })
          ],
          'Hens',
          '% cage-free',
          { y2Min: 15, y2Max: 50, yTickCallback: value => fmtMillionsAxis(value) }
        );
      }
    });
  } else {
    showPlaceholder('compositionWrap', 'The AMS monthly cage-free PDF source is now wired into the pipeline, but this environment does not have any captured composition history yet. Once current or seeded monthly rows are loaded, this chart will render here.');
  }

  registerRangeControl({
    chartId: 'breederFlockChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_breeder_flock.dates;
      const breederLevels = D.nass_breeder_flock.egg_type.map(v => v != null ? v : null);
      const breederChange = breederLevels.map((value, idx) => idx === 0 || breederLevels[idx - 1] == null ? null : (value - breederLevels[idx - 1]));
      const { start, end } = getRangeSlice(dates, range);
      if (range === '5y' || range === 'all') {
        renderEggLineChart(
          'breederFlockChart',
          dates.slice(start, end),
          [dataset('Table-egg breeding flock', breederLevels.slice(start, end), DASH_COLORS.orange)],
          'Hens'
        );
        return;
      }
      renderMixedChart(
        'breederFlockChart',
        dates.slice(start, end),
        [
          dataset('Monthly change', breederChange.slice(start, end), DASH_COLORS.navy, { backgroundColor: DASH_COLORS.navy, type: 'bar', borderWidth: 1 }),
          dataset('Table-egg breeding flock', breederLevels.slice(start, end), DASH_COLORS.orange, { yAxisID: 'y2', type: 'line' })
        ],
        'Change (hens)',
        'Hens',
        { y2Min: 3250000, y2Max: 5000000 }
      );
    }
  });

  insertRangeControls('chicksChart', []);
  {
    const map = buildYearMonthMap(D.nass_hatchery.dates_egg, D.nass_hatchery.egg_chicks.map(v => v / 1e6));
    const historyYears = [2021, 2022, 2023, 2024].filter(year => map[year]);
    const comparisonSets = [
      ...historyYears.map(year =>
        dataset(String(year), monthsForYear(map, year), 'rgba(154, 163, 171, 0.54)', {
          borderWidth: 1.8,
          backgroundColor: 'rgba(154, 163, 171, 0.54)',
          pointRadius: 0,
          pointHoverRadius: 0,
          order: 10,
          legendKey: 'history-egg-type-chicks',
          legendLabel: '2021-2024'
        })
      ),
      ...(map[2025] ? [dataset('2025', monthsForYear(map, 2025), DASH_COLORS.orange, {
        borderWidth: 4.2,
        order: 0
      })] : []),
      ...(map[2026] ? [dataset('2026', monthsForYear(map, 2026), DASH_COLORS.gold, {
        borderWidth: 4.2,
        pointRadius: 4,
        pointHoverRadius: 5,
        order: 0
      })] : [])
    ];
    const fallbackYears = [...historyYears, 2025, 2026].filter(year => map[year]).slice(-3);
    renderEggLineChart(
      'chicksChart',
      MON_SHORT,
      comparisonSets.length ? comparisonSets : fallbackYears.map(year => dataset(String(year), monthsForYear(map, year), DASH_COLORS.slate)),
      'Chicks',
      { maxTicks: 12, yMin: 45, yMax: 65, yTickCallback: value => fmtCompactMillions(value) }
    );
  }

  registerRangeControl({
    chartId: 'chicksTrendChart',
    options: ['1y', '3y', '5y', '10y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_hatchery.dates_egg;
      const values = D.nass_hatchery.egg_chicks.map(v => v / 1e6);
      const { start, end } = getRangeSlice(dates, range);
      renderBarChart(
        'chicksTrendChart',
        dates.slice(start, end),
        [dataset('Egg-type chicks hatched', values.slice(start, end), '#a23508', {
          backgroundColor: '#a23508',
          borderWidth: 1
        })],
        'Chicks',
        { yMin: 20, yMax: 65, yTickCallback: value => fmtCompactMillions(value) }
      );
    }
  });

  registerRangeControl({
    chartId: 'pipelineChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_pullets.dates;
      const alignedTableLayers = alignValues(dates, D.nass_layers.dates_table, D.nass_layers.table);
      const pipeline = D.nass_pullets.values.map((value, idx) => value != null && alignedTableLayers[idx] ? (value / alignedTableLayers[idx]) * 100 : null);
      const { start, end } = getRangeSlice(dates, range);
      renderEggLineChart(
        'pipelineChart',
        dates.slice(start, end),
        [dataset('Pullets per 100 layers', pipeline.slice(start, end), DASH_COLORS.teal)],
        'Pullets / 100 layers'
      );
    }
  });

  registerRangeControl({
    chartId: 'wholesaleChart',
    options: ['30d', '90d', '6m', '1y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const dates = D.egg_index.dates;
      const cagedRolling = rollingAverage(D.egg_index.series.Caged || [], 5);
      const breakingStock = D.egg_index.series['Breaking Stock'] || [];
      const undergrades = D.egg_index.series.Undergrades || [];
      const { start, end } = getRangeSlice(dates, range);
      renderEggLineChart(
        'wholesaleChart',
        dates.slice(start, end),
        [
          dataset('Wholesale Price', cagedRolling.slice(start, end), DASH_COLORS.orange),
          dataset('Breaking Stock', breakingStock.slice(start, end), DASH_COLORS.lightBlue),
          dataset('Undergrades', undergrades.slice(start, end), DASH_COLORS.teal)
        ],
        '¢ / dozen'
      );
    }
  });

  registerRangeControl({
    chartId: 'eggPriceCompareChart',
    options: ['3y', '5y', '10y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const fredDates = D.fred_retail_egg?.dates || [];
      const fredValues = D.fred_retail_egg?.values || [];
      const { start, end } = getRangeSlice(fredDates, range);
      renderEggLineChart(
        'eggPriceCompareChart',
        fredDates.slice(start, end),
        [dataset('FRED Grade A Large', fredValues.slice(start, end), '#a23508')],
        '$ / dozen',
        { yTickCallback: value => `$${fmtNum(value, 2)}` }
      );
    }
  });

  registerRangeControl({
    chartId: 'eggPriceSpreadChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: 'all',
    renderer(range) {
      const fredDates = D.fred_retail_egg?.dates || [];
      const fredValues = D.fred_retail_egg?.values || [];
      const nassByMonth = Object.fromEntries(D.nass_prices.dates_egg.map((date, idx) => [date, D.nass_prices.egg_doz[idx]]));
      const previousMonth = month => {
        if (!month || !/^\d{4}-\d{2}$/.test(month)) return null;
        const [yearStr, monthStr] = month.split('-');
        let year = Number(yearStr);
        let mon = Number(monthStr) - 1;
        if (mon === 0) {
          year -= 1;
          mon = 12;
        }
        return `${String(year).padStart(4, '0')}-${String(mon).padStart(2, '0')}`;
      };
      const spreadPairs = fredDates.map((date, idx) => {
        const retail = fredValues[idx];
        const prevNass = nassByMonth[previousMonth(date)];
        if (retail == null || prevNass == null) return null;
        return [date, retail - prevNass];
      }).filter(Boolean);
      const spreadDates = spreadPairs.map(([date]) => date);
      const spreadValues = spreadPairs.map(([, value]) => value);
      const spreadAvg = rollingAverage(spreadValues, 12);
      const { start, end } = getRangeSlice(spreadDates, range);
      renderEggLineChart(
        'eggPriceSpreadChart',
        spreadDates.slice(start, end),
        [dataset('12-month average', spreadAvg.slice(start, end), DASH_COLORS.navy)],
        '$ / dozen',
        { yTickCallback: value => `$${fmtNum(value, 2)}` }
      );
    }
  });

  if ((D.feed_index.dates || []).length) {
    registerRangeControl({
      chartId: 'feedIndexChart',
      options: ['30d', '60d', '3m', '6m', '1y', '3y', '5y', 'all'],
      defaultRange: '1y',
      renderer(range) {
        const dates = D.feed_index.dates;
        const { start, end } = getRangeSlice(dates, range);
        const baseMarkerValues = dates.map((date, idx) => (
          date === D.feed_index.base_date ? D.feed_index.index[idx] : null
        ));
        renderEggLineChart(
          'feedIndexChart',
          dates.slice(start, end),
          [
            dataset('Layer feed index', D.feed_index.index.slice(start, end), '#a23508', {
              order: 10
            }),
            dataset(`${fmtLongDateLabel(D.feed_index.base_date)} = 100`, baseMarkerValues.slice(start, end), DASH_COLORS.gold, {
              showLine: false,
              borderWidth: 0,
              pointStyle: 'rectRot',
              pointRadius: 6,
              pointHoverRadius: 7,
              pointBackgroundColor: DASH_COLORS.gold,
              pointBorderColor: DASH_COLORS.gold,
              order: 0
            })
          ],
          'Index'
        );
      }
    });
  } else {
    showPlaceholder('feedIndexWrap', 'Feed cost inputs are not currently ingested in this environment, so this chart will populate once FRED data is loaded.');
  }

  if ((D.input_indices?.dates || []).length) {
    registerRangeControl({
      chartId: 'dieselChart',
      options: ['1y', '3y', '5y', 'all'],
      defaultRange: '3y',
      renderer(range) {
        const dates = D.input_indices.dates;
        const { start, end } = getRangeSlice(dates, range);
        const colorByLabel = {
          'Layer feed': DASH_COLORS.orange,
          Diesel: DASH_COLORS.navy,
          'Paperboard packaging': DASH_COLORS.teal
        };
        renderEggLineChart(
          'dieselChart',
          dates.slice(start, end),
          Object.keys(D.input_indices.series).map(label =>
            dataset(label, D.input_indices.series[label].slice(start, end), colorByLabel[label] || DASH_COLORS.slate)
          ),
          'Index'
        );
      }
    });
  } else {
    showPlaceholder('dieselWrap', 'Input index comparison data is not fully ingested in this environment yet. Once feed and FRED input series are loaded, this chart will populate.');
  }

  registerRangeControl({
    chartId: 'regionalEggChart',
    options: ['6m', '1y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.regional_egg.dates;
      const { start, end } = getRangeSlice(dates, range);
      const regionalSets = Object.keys(D.regional_egg.series).map((key, idx) =>
        dataset(key, D.regional_egg.series[key].slice(start, end), DASH_COLORS.seq[idx % DASH_COLORS.seq.length])
      );
      renderEggLineChart(
        'regionalEggChart',
        dates.slice(start, end),
        regionalSets,
        '¢ / dozen'
      );
    }
  });

  if ((D.ers_trade_egg.dates || []).length) {
    registerRangeControl({
      chartId: 'eggImportsTradeChart',
      options: ['3y', '5y', '10y', 'all'],
      defaultRange: '3y',
      renderer(range) {
        const dates = D.ers_trade_egg.dates;
        const { start, end } = getRangeSlice(dates, range);
        renderBarChart(
          'eggImportsTradeChart',
          dates.slice(start, end),
          [
            dataset('Shell-egg imports', D.ers_trade_egg.import_shell_egg.slice(start, end), DASH_COLORS.navy, {
              backgroundColor: '#013046',
              borderWidth: 1
            }),
            dataset('Egg product imports', D.ers_trade_egg.import_egg_product.slice(start, end), DASH_COLORS.sky, {
              backgroundColor: DASH_COLORS.sky,
              borderWidth: 1
            })
          ],
          '1,000 dozen',
          { stacked: true }
        );
      }
    });

    registerRangeControl({
      chartId: 'eggExportsTradeChart',
      options: ['3y', '5y', '10y', 'all'],
      defaultRange: '3y',
      renderer(range) {
        const dates = D.ers_trade_egg.dates;
        const { start, end } = getRangeSlice(dates, range);
        renderBarChart(
          'eggExportsTradeChart',
          dates.slice(start, end),
          [
            dataset('Shell-egg exports', D.ers_trade_egg.export_shell_egg.slice(start, end), DASH_COLORS.navy, {
              backgroundColor: '#013046',
              borderWidth: 1
            }),
            dataset('Egg product exports', D.ers_trade_egg.export_egg_product.slice(start, end), DASH_COLORS.sky, {
              backgroundColor: DASH_COLORS.sky,
              borderWidth: 1
            })
          ],
          '1,000 dozen',
          { stacked: true }
        );
      }
    });
  } else {
    showPlaceholder('importsWrap', 'ERS egg trade totals are not loaded in this environment yet. Run the ERS trade ingest and this chart will populate.');
    showPlaceholder('exportsWrap', 'ERS egg trade totals are not loaded in this environment yet. Run the ERS trade ingest and this chart will populate.');
  }
}

bootEggDashboard().catch(error => {
  console.error(error);
  showPlaceholder('retailFeatureWrap', `Error loading egg dashboard: ${error.message}`);
});
