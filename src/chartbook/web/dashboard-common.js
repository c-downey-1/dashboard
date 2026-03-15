const charts = {};
const chartRanges = {};
const chartRenderers = {};

const RANGE_LABELS = {
  '30d': '30D',
  '90d': '90D',
  '6m': '6M',
  '1y': '1Y',
  '2y': '2Y',
  '3y': '3Y',
  '5y': '5Y',
  '10y': '10Y',
  all: 'All'
};

const DASH_COLORS = {
  navy: '#013046',
  navy2: '#0a4561',
  orange: '#F6851F',
  teal: '#1F9EBC',
  gold: '#FDB714',
  sky: '#8FCAE6',
  slate: '#939598',
  red: '#991b1b',
  redSoft: '#dc2626',
  seq: ['#F6851F', '#1F9EBC', '#013046', '#FDB714', '#8FCAE6', '#939598', '#E5700A']
};

if (window.Chart) {
  Chart.defaults.font.family = 'Lexend';
  Chart.defaults.color = DASH_COLORS.navy;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.pointStyle = 'line';
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(1,48,70,0.92)';
  Chart.defaults.plugins.tooltip.titleColor = '#fff';
  Chart.defaults.plugins.tooltip.bodyColor = '#eaf2f7';
  Chart.defaults.plugins.tooltip.cornerRadius = 12;
  Chart.defaults.plugins.tooltip.padding = 12;
}

const MON_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function fmtNum(value, digits = 0) {
  if (value == null || Number.isNaN(value)) return '—';
  return value.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

function fmtM(value) {
  if (value == null || Number.isNaN(value)) return '—';
  if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(1) + 'B';
  if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(1) + 'M';
  if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(0) + 'K';
  return value.toFixed(0);
}

function fmtDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) return `${parts[1]}/${parts[2]}/${parts[0]}`;
  return dateStr;
}

function fmtYM(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length < 2) return dateStr;
  const month = parseInt(parts[1], 10) - 1;
  if (month < 0 || month > 11) return dateStr;
  return `${MON_SHORT[month]}-${parts[0].slice(2)}`;
}

function latestNonNull(dates, values) {
  for (let i = values.length - 1; i >= 0; i -= 1) {
    if (values[i] != null && !Number.isNaN(values[i])) {
      return { date: dates[i], value: values[i] };
    }
  }
  return { date: null, value: null };
}

function rollingAverage(values, windowSize) {
  return values.map((_, index) => {
    if (index < windowSize - 1) return null;
    const slice = values.slice(index - windowSize + 1, index + 1).filter(v => v != null);
    if (!slice.length) return null;
    return slice.reduce((sum, value) => sum + value, 0) / slice.length;
  });
}

function rollingSum(values, windowSize) {
  return values.map((_, index) => {
    if (index < windowSize - 1) return null;
    const slice = values.slice(index - windowSize + 1, index + 1).filter(v => v != null);
    if (!slice.length) return null;
    return slice.reduce((sum, value) => sum + value, 0);
  });
}

function buildYearMonthMap(dates, values) {
  const out = {};
  dates.forEach((dateStr, index) => {
    const value = values[index];
    if (value == null || !dateStr || dateStr.length < 7) return;
    const year = parseInt(dateStr.slice(0, 4), 10);
    const month = parseInt(dateStr.slice(5, 7), 10);
    if (!out[year]) out[year] = {};
    out[year][month] = value;
  });
  return out;
}

function rangeCutoff(range) {
  const now = new Date();
  switch (range) {
    case '30d':
      return new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30);
    case '90d':
      return new Date(now.getFullYear(), now.getMonth(), now.getDate() - 90);
    case '6m':
      return new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
    case '1y':
      return new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    case '2y':
      return new Date(now.getFullYear() - 2, now.getMonth(), now.getDate());
    case '3y':
      return new Date(now.getFullYear() - 3, now.getMonth(), now.getDate());
    case '5y':
      return new Date(now.getFullYear() - 5, now.getMonth(), now.getDate());
    case '10y':
      return new Date(now.getFullYear() - 10, now.getMonth(), now.getDate());
    default:
      return null;
  }
}

function getRangeSlice(dates, range) {
  if (range === 'all' || !dates.length) {
    return { start: 0, end: dates.length };
  }
  const cutoff = rangeCutoff(range);
  if (!cutoff) return { start: 0, end: dates.length };
  const iso = cutoff.toISOString().slice(0, 10);
  const start = Math.max(0, dates.findIndex(date => date >= iso));
  return { start: start === -1 ? 0 : start, end: dates.length };
}

function historyYearsForRange(years, range, minYear) {
  const sorted = years.filter(year => !minYear || year >= minYear).sort((a, b) => a - b);
  if (!sorted.length) return [];
  const lookbackMap = { '2y': 2, '3y': 3, '5y': 5, '10y': 10 };
  if (range === 'all') return sorted;
  const count = lookbackMap[range] || 3;
  return sorted.slice(-count);
}

function monthsForYear(map, year) {
  return Array.from({ length: 12 }, (_, idx) => map[year]?.[idx + 1] ?? null);
}

function averageMonths(map, years) {
  return Array.from({ length: 12 }, (_, idx) => {
    const month = idx + 1;
    const values = years.map(year => map[year]?.[month]).filter(v => v != null);
    if (!values.length) return null;
    return values.reduce((sum, value) => sum + value, 0) / values.length;
  });
}

function dataset(label, data, color, extra = {}) {
  return Object.assign({
    label,
    data,
    borderColor: color,
    backgroundColor: `${color}22`,
    pointRadius: 0,
    pointHoverRadius: 4,
    pointHoverBorderWidth: 2,
    pointHoverBorderColor: '#fff',
    borderWidth: 2.4,
    tension: 0.28,
    spanGaps: true,
    fill: false
  }, extra);
}

function destroyChart(id) {
  if (charts[id]) {
    charts[id].destroy();
  }
}

function baseOptions(yLabel, extra = {}) {
  const hasY2 = !!extra.y2;
  const options = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: extra.aspect || 1.7,
    interaction: { mode: 'index', intersect: false },
    layout: { padding: { top: 4, right: 8, bottom: 8, left: 2 } },
    plugins: {
      legend: {
        display: extra.legend !== false,
        position: 'bottom',
        align: 'start',
        labels: { boxWidth: 28, padding: 14, font: { size: 12, weight: '600' } }
      }
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: extra.maxTicks || 6,
          color: '#627684',
          font: { size: 12 },
          callback(value) {
            const label = this.getLabelForValue(value);
            return typeof label === 'string' && label.includes('-') ? fmtYM(label) : label;
          }
        },
        border: { display: false },
        grid: { drawOnChartArea: false, drawTicks: false }
      },
      y: {
        title: { display: !!yLabel, text: yLabel, color: '#5f7180', font: { size: 12, weight: '600' } },
        ticks: { color: '#627684', font: { size: 12 } },
        border: { display: false },
        grid: { color: 'rgba(1,48,70,0.07)' }
      }
    }
  };
  if (hasY2) {
    options.scales.y2 = {
      position: 'right',
      title: { display: true, text: extra.y2, color: '#5f7180', font: { size: 12, weight: '600' } },
      ticks: { color: '#627684', font: { size: 12 } },
      border: { display: false },
      grid: { drawOnChartArea: false }
    };
  }
  return options;
}

function renderLineChart(id, labels, datasets, yLabel, extra = {}) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  charts[id] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: baseOptions(yLabel, extra)
  });
}

function renderBarChart(id, labels, datasets, yLabel, extra = {}) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  destroyChart(id);
  const options = baseOptions(yLabel, extra);
  if (extra.stacked) {
    options.scales.x.stacked = true;
    options.scales.y.stacked = true;
  }
  if (extra.horizontal) {
    options.indexAxis = 'y';
  }
  charts[id] = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options
  });
}

function showPlaceholder(id, message) {
  const node = document.getElementById(id);
  if (!node) return;
  node.innerHTML = `<div class="placeholder-note">${message}</div>`;
}

function insertRangeControls(chartId, options) {
  const canvas = document.getElementById(chartId);
  if (!canvas) return;
  const card = canvas.closest('.card');
  if (!card) return;
  let host = card.querySelector(`.range-controls[data-chart="${chartId}"]`);
  if (!host) {
    host = document.createElement('div');
    host.className = 'range-controls';
    host.dataset.chart = chartId;
    const sub = card.querySelector('.sub');
    if (sub) {
      sub.insertAdjacentElement('afterend', host);
    } else {
      card.insertBefore(host, canvas);
    }
  }
  host.innerHTML = options.map(option => {
    const active = chartRanges[chartId] === option ? ' active' : '';
    return `<button class="range-btn${active}" type="button" data-chart="${chartId}" data-range="${option}">${RANGE_LABELS[option] || option}</button>`;
  }).join('');
}

function registerRangeControl({ chartId, options, defaultRange, renderer }) {
  chartRanges[chartId] = defaultRange || options[0];
  chartRenderers[chartId] = renderer;
  insertRangeControls(chartId, options);
  renderer(chartRanges[chartId]);
}

document.addEventListener('click', event => {
  const button = event.target.closest('.range-btn');
  if (!button) return;
  const chartId = button.dataset.chart;
  const range = button.dataset.range;
  if (!chartRenderers[chartId]) return;
  chartRanges[chartId] = range;
  insertRangeControls(chartId, button.parentElement ? Array.from(button.parentElement.querySelectorAll('.range-btn')).map(node => node.dataset.range) : [range]);
  chartRenderers[chartId](range);
});
