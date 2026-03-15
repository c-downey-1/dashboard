function setText(id, text) {
  const node = document.getElementById(id);
  if (node) node.textContent = text;
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

function renderMixedChart(id, labels, datasets, yLabel, y2Label) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  charts[id] = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: baseOptions(yLabel, { y2: y2Label, maxTicks: 12 })
  });
}

async function bootEggDashboard() {
  const response = await fetch(`data.json?v=${Date.now()}`);
  const D = await response.json();

  document.title = `Egg Industry Dashboard — ${D.updated}`;
  setText('updatedStamp', D.updated);
  setText('coverageStamp', 'Monthly chartbook-inspired egg market view');
  setText('statusStamp', 'Fresh USDA + APHIS series powering egg supply, disease, and price monitoring');

  const pulletLatest = latestNonNull(D.nass_pullets.dates, D.nass_pullets.values);
  const feedLatest = latestNonNull(D.feed_index.dates || [], D.feed_index.index || []);
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
  setText('kpiFeedSub', feedLatest.date ? `Feed index · ${fmtYM(feedLatest.date)}` : 'Feed index not ingested');

  registerRangeControl({
    chartId: 'retailFeatureChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.retail_egg_feature.dates;
      const rolled = rollingAverage(D.retail_egg_feature.rate, 4);
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'retailFeatureChart',
        dates.slice(start, end),
        [dataset('4-week average', rolled.slice(start, end), DASH_COLORS.orange)],
        'Feature rate (%)'
      );
    }
  });

  registerRangeControl({
    chartId: 'pulletClimbChart',
    options: ['1y', '2y', '5y', 'all'],
    defaultRange: '2y',
    renderer(range) {
      const { start, end } = getRangeSlice(D.nass_pullets.dates, range);
      renderLineChart(
        'pulletClimbChart',
        D.nass_pullets.dates.slice(start, end),
        [dataset('Pullets', D.nass_pullets.values.slice(start, end).map(v => v / 1e6), DASH_COLORS.teal)],
        'Million head'
      );
    }
  });

  registerRangeControl({
    chartId: 'hpaiDetectionsChart',
    options: ['1y', '3y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const { start, end } = getRangeSlice(D.hpai_summary.dates, range);
      renderBarChart(
        'hpaiDetectionsChart',
        D.hpai_summary.dates.slice(start, end),
        [dataset('Detections', D.hpai_summary.detections.slice(start, end), DASH_COLORS.red, { backgroundColor: '#991b1b88', borderWidth: 1 })],
        'Detections'
      );
    }
  });

  registerRangeControl({
    chartId: 'hpaiLayersChart',
    options: ['1y', '3y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const { start, end } = getRangeSlice(D.hpai_layers.dates, range);
      renderBarChart(
        'hpaiLayersChart',
        D.hpai_layers.dates.slice(start, end),
        [dataset('Layer birds affected', D.hpai_layers.birds.slice(start, end).map(v => v / 1e3), DASH_COLORS.redSoft, { backgroundColor: '#dc262688', borderWidth: 1 })],
        'Thousand birds'
      );
    }
  });

  registerRangeControl({
    chartId: 'trailingProdChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_egg_production.dates_table;
      const values = rollingSum(D.nass_egg_production.table.map(v => v / 1e9), 3);
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'trailingProdChart',
        dates.slice(start, end),
        [dataset('3-month trailing table egg production', values.slice(start, end), DASH_COLORS.navy)],
        'Billion eggs'
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
          dataset(String(payload.previous), payload.previousValues, DASH_COLORS.sky, { type: 'bar', backgroundColor: '#8FCAE688', borderWidth: 1 }),
          dataset(String(payload.current), payload.currentValues, DASH_COLORS.orange, { type: 'bar', backgroundColor: '#F6851F88', borderWidth: 1 }),
          dataset(payload.averageLabel, payload.averageValues, DASH_COLORS.navy, { type: 'line', borderDash: [6, 4] })
        ],
        'Billion eggs'
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
      renderLineChart(
        'rolChart',
        dates.slice(start, end),
        [
          dataset('Table layer rate of lay', values.slice(start, end), DASH_COLORS.orange),
          dataset('12-month average', avg.slice(start, end), DASH_COLORS.navy, { borderDash: [6, 4] })
        ],
        'Eggs / 100 layers / day'
      );
    }
  });

  registerRangeControl({
    chartId: 'breakersChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_shell_broken.dates;
      const brokenEggs = D.nass_shell_broken.dozen.map(v => (v * 12) / 1e9);
      const totalProdBillions = alignValues(dates, D.nass_egg_production.dates, D.nass_egg_production.total).map(v => v != null ? v / 1e9 : null);
      const brokenShare = brokenEggs.map((value, idx) => value != null && totalProdBillions[idx] ? (value / totalProdBillions[idx]) * 100 : null);
      const { start, end } = getRangeSlice(dates, range);
      renderMixedChart(
        'breakersChart',
        dates.slice(start, end),
        [
          dataset('Eggs delivered to breakers', brokenEggs.slice(start, end), DASH_COLORS.gold, { backgroundColor: '#FDB71488', borderColor: DASH_COLORS.gold, type: 'bar' }),
          dataset('% of total production', brokenShare.slice(start, end), DASH_COLORS.navy, { yAxisID: 'y2', type: 'line' })
        ],
        'Billion eggs',
        '% of production'
      );
    }
  });

  registerRangeControl({
    chartId: 'tableLayersChart',
    options: ['2y', '5y', '10y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const payload = seasonalPayload(D.nass_layers.dates_table, D.nass_layers.table.map(v => v / 1e6), range, 2010);
      renderLineChart(
        'tableLayersChart',
        MON_SHORT,
        [
          dataset(payload.averageLabel, payload.averageValues, DASH_COLORS.slate, { borderDash: [6, 4] }),
          dataset(String(payload.previous), payload.previousValues, DASH_COLORS.sky),
          dataset(String(payload.current), payload.currentValues, DASH_COLORS.teal)
        ],
        'Million hens',
        { maxTicks: 12 }
      );
    }
  });

  registerRangeControl({
    chartId: 'turnoverChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_layer_disposition.dates_sales;
      const slaughter = D.nass_layer_disposition.sales.map(v => v / 1e3);
      const loss = alignValues(dates, D.nass_layer_disposition.dates_loss, D.nass_layer_disposition.loss).map(v => v != null ? v / 1e3 : null);
      const { start, end } = getRangeSlice(dates, range);
      renderBarChart(
        'turnoverChart',
        dates.slice(start, end),
        [
          dataset('Sold for slaughter', slaughter.slice(start, end), DASH_COLORS.orange, { backgroundColor: '#F6851F88', borderWidth: 1 }),
          dataset('Loss / rendered', loss.slice(start, end), DASH_COLORS.red, { backgroundColor: '#991b1b88', borderWidth: 1 })
        ],
        'Thousand head'
      );
    }
  });

  registerRangeControl({
    chartId: 'moltChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_layer_disposition.dates_molted;
      const values = D.nass_layer_disposition.being_molted_pct;
      const avg = rollingAverage(values, 12);
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'moltChart',
        dates.slice(start, end),
        [
          dataset('Being molted', values.slice(start, end), DASH_COLORS.gold),
          dataset('12-month average', avg.slice(start, end), DASH_COLORS.navy, { borderDash: [6, 4] })
        ],
        '% of inventory'
      );
    }
  });

  registerRangeControl({
    chartId: 'breederFlockChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_breeder_flock.dates;
      const breederLevels = D.nass_breeder_flock.layers.map(v => v / 1e6);
      const breederChange = breederLevels.map((value, idx) => idx === 0 || breederLevels[idx - 1] == null ? null : (value - breederLevels[idx - 1]) * 1e3);
      const { start, end } = getRangeSlice(dates, range);
      renderMixedChart(
        'breederFlockChart',
        dates.slice(start, end),
        [
          dataset('Monthly change', breederChange.slice(start, end), DASH_COLORS.orange, { backgroundColor: '#F6851F88', type: 'bar', borderWidth: 1 }),
          dataset('Breeder flock size', breederLevels.slice(start, end), DASH_COLORS.navy, { yAxisID: 'y2', type: 'line' })
        ],
        'Change (thousand hens)',
        'Million hens'
      );
    }
  });

  registerRangeControl({
    chartId: 'chicksChart',
    options: ['2y', '5y', 'all'],
    defaultRange: '5y',
    renderer(range) {
      const payload = seasonalPayload(D.nass_hatchery.dates_egg, D.nass_hatchery.egg_chicks.map(v => v / 1e6), range, 2012);
      renderMixedChart(
        'chicksChart',
        MON_SHORT,
        [
          dataset(String(payload.previous), payload.previousValues, DASH_COLORS.sky, { type: 'bar', backgroundColor: '#8FCAE688', borderWidth: 1 }),
          dataset(String(payload.current), payload.currentValues, DASH_COLORS.orange, { type: 'bar', backgroundColor: '#F6851F88', borderWidth: 1 }),
          dataset(payload.averageLabel, payload.averageValues, DASH_COLORS.navy, { type: 'line', borderDash: [6, 4] })
        ],
        'Million chicks'
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
      renderLineChart(
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
    defaultRange: '6m',
    renderer(range) {
      const dates = D.egg_index.dates;
      const cagedRolling = rollingAverage(D.egg_index.series.Caged || [], 5);
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'wholesaleChart',
        dates.slice(start, end),
        [dataset('5-day rolling wholesale price', cagedRolling.slice(start, end), DASH_COLORS.orange)],
        '¢ / dozen'
      );
    }
  });

  registerRangeControl({
    chartId: 'retailPriceChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.retail_egg_prices.dates;
      const { start, end } = getRangeSlice(dates, range);
      const retailDatasets = Object.keys(D.retail_egg_prices.series).map((key, idx) =>
        dataset(key, D.retail_egg_prices.series[key].slice(start, end), DASH_COLORS.seq[idx % DASH_COLORS.seq.length])
      );
      renderLineChart(
        'retailPriceChart',
        dates.slice(start, end),
        retailDatasets,
        '$ / dozen'
      );
    }
  });

  if ((D.feed_index.dates || []).length) {
    registerRangeControl({
      chartId: 'feedIndexChart',
      options: ['1y', '3y', '5y', 'all'],
      defaultRange: '3y',
      renderer(range) {
        const dates = D.feed_index.dates;
        const { start, end } = getRangeSlice(dates, range);
        renderLineChart(
          'feedIndexChart',
          dates.slice(start, end),
          [dataset('Layer feed index', D.feed_index.index.slice(start, end), DASH_COLORS.gold)],
          'Index'
        );
      }
    });
  } else {
    showPlaceholder('feedIndexWrap', 'Feed cost inputs are not currently ingested in this environment, so this chart will populate once FRED data is loaded.');
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
      renderLineChart(
        'regionalEggChart',
        dates.slice(start, end),
        regionalSets,
        '¢ / dozen'
      );
    }
  });

  showPlaceholder('compositionPlaceholder', 'The monthly chartbook uses the USDA AMS Monthly Cage-Free Shell Egg Report for flock composition. That source is not yet wired into this dashboard, so I left this slot as the main remaining egg-only data gap.');
  showPlaceholder('importsPlaceholder', 'Egg import data from the monthly chartbook is not currently ingested into this project. This card is reserved for that trade series once we add the source.');
  showPlaceholder('exportsPlaceholder', 'Egg export data from the monthly chartbook is not currently ingested into this project. This card is reserved for that trade series once we add the source.');
}

bootEggDashboard().catch(error => {
  console.error(error);
  showPlaceholder('retailFeatureWrap', `Error loading egg dashboard: ${error.message}`);
});
