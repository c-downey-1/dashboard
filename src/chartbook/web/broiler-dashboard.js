function broilerText(id, text) {
  const node = document.getElementById(id);
  if (node) node.textContent = text;
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

async function bootBroilerDashboard() {
  const response = await fetch(`data.json?v=${Date.now()}`);
  const D = await response.json();

  document.title = `Broiler Industry Dashboard — ${D.updated}`;
  broilerText('updatedStamp', D.updated);
  broilerText('coverageStamp', 'Wholesale, hatchability, supply, storage, and retail broiler monitoring');
  broilerText('statusStamp', 'Built from weekly MARS + ESMIS and monthly NASS data');

  const placementLatest = latestNonNull(D.nass_placements.dates, D.nass_placements.values);
  const hatchLatest = latestNonNull(D.nass_hatchery.dates_broiler, D.nass_hatchery.broiler_chicks);
  const featureLatest = latestNonNull(D.retail_chicken_feature.dates, D.retail_chicken_feature.rate);
  broilerText('kpiBreast', D.kpi.breast_bs_price != null ? `${fmtNum(D.kpi.breast_bs_price, 2)}¢` : '—');
  broilerText('kpiBreastSub', D.kpi.breast_bs_date ? `Breast B/S · ${fmtDate(D.kpi.breast_bs_date)}` : 'Wholesale breast price');
  broilerText('kpiPlacement', placementLatest.value != null ? fmtM(placementLatest.value) : '—');
  broilerText('kpiPlacementSub', placementLatest.date ? `Placements · ${fmtDate(placementLatest.date)}` : 'Broiler placements');
  broilerText('kpiHatch', hatchLatest.value != null ? fmtM(hatchLatest.value) : '—');
  broilerText('kpiHatchSub', hatchLatest.date ? `Chicks hatched · ${fmtYM(hatchLatest.date)}` : 'Broiler hatchery output');
  broilerText('kpiFeature', featureLatest.value != null ? `${fmtNum(featureLatest.value, 1)}%` : '—');
  broilerText('kpiFeatureSub', featureLatest.date ? `Retail feature rate · ${fmtDate(featureLatest.date)}` : 'Retail feature activity');

  registerRangeControl({
    chartId: 'wholesaleCutsChart',
    options: ['90d', '6m', '1y', 'all'],
    defaultRange: '6m',
    renderer(range) {
      const dates = D.chicken_wholesale.dates;
      const { start, end } = getRangeSlice(dates, range);
      const cuts = ['Breast - B/S', 'Wings - Whole', 'Leg quarters - Bulk', 'Thighs - B/S', 'WOG']
        .filter(key => D.chicken_wholesale.series[key]);
      renderLineChart(
        'wholesaleCutsChart',
        dates.slice(start, end),
        cuts.map((key, idx) => dataset(key, D.chicken_wholesale.series[key].slice(start, end), DASH_COLORS.seq[idx % DASH_COLORS.seq.length])),
        '¢ / lb'
      );
    }
  });

  registerRangeControl({
    chartId: 'wholesaleVolumeChart',
    options: ['90d', '6m', '1y', 'all'],
    defaultRange: '6m',
    renderer(range) {
      const dates = D.chicken_volume.dates;
      const { start, end } = getRangeSlice(dates, range);
      const volKeys = Object.keys(D.chicken_volume.series).slice(0, 5);
      renderBarChart(
        'wholesaleVolumeChart',
        dates.slice(start, end),
        volKeys.map((key, idx) => dataset(key, D.chicken_volume.series[key].slice(start, end), DASH_COLORS.seq[idx % DASH_COLORS.seq.length], {
          backgroundColor: `${DASH_COLORS.seq[idx % DASH_COLORS.seq.length]}88`,
          borderWidth: 1
        })),
        'Loads',
        { stacked: true }
      );
    }
  });

  registerRangeControl({
    chartId: 'placementsChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const { start, end } = getRangeSlice(D.nass_placements.dates, range);
      renderLineChart(
        'placementsChart',
        D.nass_placements.dates.slice(start, end),
        [dataset('Broiler placements', D.nass_placements.values.slice(start, end).map(v => v / 1e6), DASH_COLORS.navy)],
        'Million head'
      );
    }
  });

  registerRangeControl({
    chartId: 'hatcheryChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_hatchery.dates_broiler;
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'hatcheryChart',
        dates.slice(start, end),
        [
          dataset('Broiler chicks hatched', D.nass_hatchery.broiler_chicks.slice(start, end).map(v => v / 1e6), DASH_COLORS.orange),
          dataset('Broiler eggs set', D.nass_hatchery.eggs_set.slice(start, end).map(v => v / 1e6), DASH_COLORS.teal)
        ],
        'Million'
      );
    }
  });

  registerRangeControl({
    chartId: 'pricesReceivedChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.nass_prices.dates_broiler;
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'pricesReceivedChart',
        dates.slice(start, end),
        [dataset('Broiler price received', D.nass_prices.broiler_lb.slice(start, end), DASH_COLORS.teal)],
        '$ / lb'
      );
    }
  });

  registerRangeControl({
    chartId: 'coldStorageWeeklyChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.cold_storage_mars.dates;
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'coldStorageWeeklyChart',
        dates.slice(start, end),
        Object.keys(D.cold_storage_mars.series).map((key, idx) =>
          dataset(key, D.cold_storage_mars.series[key].slice(start, end).map(v => v != null ? v / 1e6 : null), DASH_COLORS.seq[idx % DASH_COLORS.seq.length])
        ),
        'Million lbs'
      );
    }
  });

  registerRangeControl({
    chartId: 'coldStorageMonthlyChart',
    options: ['1y', '3y', '5y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.cold_storage_nass.dates_chicken;
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'coldStorageMonthlyChart',
        dates.slice(start, end),
        [dataset('Chicken cold storage', D.cold_storage_nass.chicken_lbs.slice(start, end).map(v => v != null ? v / 1e6 : null), DASH_COLORS.navy)],
        'Million lbs'
      );
    }
  });

  if ((D.broiler_hatchability?.dates || []).length) {
    registerRangeControl({
      chartId: 'hatchabilityChart',
      options: ['1y', '3y', '5y', 'all'],
      defaultRange: '3y',
      renderer(range) {
        const dates = D.broiler_hatchability.dates;
        const values = D.broiler_hatchability.values;
        const rolling4 = rollingAverage(values, 4);
        const rolling52 = rollingAverage(values, 52);
        const { start, end } = getRangeSlice(dates, range);
        renderLineChart(
          'hatchabilityChart',
          dates.slice(start, end),
          [
            dataset('Reported hatchability', values.slice(start, end), DASH_COLORS.orange),
            dataset('Rolling 1-month average', rolling4.slice(start, end), DASH_COLORS.navy, {
              borderDash: [8, 6],
              borderWidth: 2.2,
              pointRadius: 0,
              backgroundColor: 'transparent'
            }),
            dataset('Rolling 1-year average', rolling52.slice(start, end), DASH_COLORS.teal, {
              borderDash: [2, 6],
              borderWidth: 2.2,
              pointRadius: 0,
              backgroundColor: 'transparent'
            })
          ],
          '%'
        );
      }
    });
  } else {
    showPlaceholder('hatchabilityWrap', 'Broiler hatchability data is not available in this build yet.');
  }

  registerRangeControl({
    chartId: 'retailChickenChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.retail_chicken_prices.dates;
      const { start, end } = getRangeSlice(dates, range);
      const retailCuts = Object.keys(D.retail_chicken_prices.series).slice(0, 8);
      renderLineChart(
        'retailChickenChart',
        dates.slice(start, end),
        retailCuts.map((key, idx) => dataset(key, D.retail_chicken_prices.series[key].slice(start, end), DASH_COLORS.seq[idx % DASH_COLORS.seq.length])),
        '$ / lb'
      );
    }
  });

  registerRangeControl({
    chartId: 'featureActivityChart',
    options: ['6m', '1y', '3y', 'all'],
    defaultRange: '1y',
    renderer(range) {
      const dates = D.retail_chicken_feature.dates;
      const { start, end } = getRangeSlice(dates, range);
      renderLineChart(
        'featureActivityChart',
        dates.slice(start, end),
        [dataset('Retail feature rate', D.retail_chicken_feature.rate.slice(start, end), DASH_COLORS.orange)],
        '%'
      );
    }
  });

  registerRangeControl({
    chartId: 'hpaiChart',
    options: ['1y', '3y', 'all'],
    defaultRange: '3y',
    renderer(range) {
      const dates = D.hpai_summary.dates;
      const { start, end } = getRangeSlice(dates, range);
      renderBarChart(
        'hpaiChart',
        dates.slice(start, end),
        [dataset('Commercial birds affected', D.hpai_summary.commercial_birds.slice(start, end).map(v => v ? v / 1e6 : 0), DASH_COLORS.red, { backgroundColor: '#991b1b88', borderWidth: 1 })],
        'Million birds'
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
          [dataset('Feed cost index', D.feed_index.index.slice(start, end), DASH_COLORS.gold)],
          'Index'
        );
      }
    });
  } else {
    showPlaceholder('feedIndexWrap', 'Feed cost inputs are not currently ingested in this environment, so this card will populate once FRED data is loaded.');
  }
}

bootBroilerDashboard().catch(error => {
  console.error(error);
  showPlaceholder('wholesaleCutsWrap', `Error loading broiler dashboard: ${error.message}`);
});
