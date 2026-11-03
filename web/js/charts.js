// Minimal dependency-free canvas charts (bars with a fitted line, and multi-series lines).
// Colours come from CSS custom properties so the charts follow light/dark mode.

export const DQ_COLORS = ['#3a8074', '#97ae85', '#d3c46b', '#e0a361', '#c1593a'];
export const DQ_LABELS = ['DQ1', 'DQ2', 'DQ3', 'DQ4', 'DQ5'];

const css = (name, fallback) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;

function setup(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const { width, height } = canvas.getBoundingClientRect();
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  return { ctx, width, height };
}

/** "Nice" axis upper bound and ticks. */
function niceScale(min, max, count = 4) {
  if (min === max) { max = min + 1; }
  const span = max - min;
  const raw = span / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? 10 * mag;
  const lo = Math.floor(min / step) * step;
  const hi = Math.ceil(max / step) * step;
  const ticks = [];
  for (let v = lo; v <= hi + step / 2; v += step) ticks.push(Number(v.toPrecision(12)));
  return { lo, hi, ticks };
}

export function formatNumber(v) {
  const a = Math.abs(v);
  if (a === 0) return '0';
  if (a >= 10000) return (v / 1000).toFixed(0) + 'k';
  if (a >= 100) return v.toFixed(0);
  if (a >= 10) return v.toFixed(1);
  if (a >= 1) return v.toFixed(2);
  if (a >= 0.01) return v.toFixed(3);
  return v.toExponential(1);
}

function frame(ctx, width, height, { lo, hi, ticks }, m, fmt) {
  const text = css('--muted', '#666'), grid = css('--grid', 'rgba(0,0,0,.08)');
  ctx.font = '11px system-ui, sans-serif';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'right';
  const y = (v) => m.top + (1 - (v - lo) / (hi - lo)) * (height - m.top - m.bottom);
  for (const t of ticks) {
    ctx.strokeStyle = grid; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(m.left, y(t)); ctx.lineTo(width - m.right, y(t)); ctx.stroke();
    ctx.fillStyle = text; ctx.fillText(fmt(t), m.left - 6, y(t));
  }
  return y;
}

/**
 * Bar chart over DQ1..DQ5 with an optional least-squares line.
 * opts: { values, fit: {slope, intercept}|null, format, zeroBase }
 */
export function drawBars(canvas, { values, fit = null, format = formatNumber, zeroBase = true }) {
  const { ctx, width, height } = setup(canvas);
  const m = { top: 12, right: 12, bottom: 26, left: 46 };
  const all = fit ? [...values, fit.at(1), fit.at(5)] : values;
  let min = zeroBase ? Math.min(0, ...all) : Math.min(...all);
  let max = Math.max(...all, zeroBase ? 0 : -Infinity);
  if (!zeroBase) { const pad = (max - min) * 0.2 || 1; min -= pad; max += pad; }
  const scale = niceScale(min, max);
  const y = frame(ctx, width, height, scale, m, format);
  const plotW = width - m.left - m.right;
  const slot = plotW / values.length;
  const bw = Math.min(56, slot * 0.62);
  const base = y(Math.max(scale.lo, Math.min(scale.hi, zeroBase ? 0 : scale.lo)));

  values.forEach((v, i) => {
    const x = m.left + slot * i + (slot - bw) / 2;
    ctx.fillStyle = DQ_COLORS[i];
    const top = y(v);
    ctx.fillRect(x, Math.min(top, base), bw, Math.abs(base - top) || 1);
  });

  ctx.fillStyle = css('--muted', '#666');
  ctx.textAlign = 'center';
  DQ_LABELS.forEach((l, i) => ctx.fillText(l, m.left + slot * i + slot / 2, height - m.bottom + 14));

  if (fit) {
    ctx.strokeStyle = css('--ink', '#111');
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(m.left + slot * 0.5, y(fit.at(1)));
    ctx.lineTo(m.left + slot * (values.length - 0.5), y(fit.at(values.length)));
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

/** Line chart; `series` is an array of equal-length arrays, one per DQ. */
export function drawLines(canvas, { series, xMax, xLabel = 'week' }) {
  const { ctx, width, height } = setup(canvas);
  const m = { top: 12, right: 14, bottom: 28, left: 46 };
  const n = series[0]?.length ?? 0;
  const maxY = Math.max(1, ...series.map((s) => s[s.length - 1] ?? 0));
  const scale = niceScale(0, maxY);
  const y = frame(ctx, width, height, scale, m, formatNumber);
  const x = (i) => m.left + (i / Math.max(1, (xMax ?? n) - 1)) * (width - m.left - m.right);

  series.forEach((s, d) => {
    if (s.length === 0) return;
    ctx.strokeStyle = DQ_COLORS[d]; ctx.lineWidth = 2; ctx.lineJoin = 'round';
    ctx.beginPath();
    s.forEach((v, i) => (i === 0 ? ctx.moveTo(x(i), y(v)) : ctx.lineTo(x(i), y(v))));
    ctx.stroke();
  });

  ctx.fillStyle = css('--muted', '#666');
  ctx.textAlign = 'center';
  const total = xMax ?? n;
  [0, 0.25, 0.5, 0.75, 1].forEach((f) => {
    ctx.fillText(String(Math.round(f * total)), m.left + f * (width - m.left - m.right), height - m.bottom + 14);
  });
  ctx.textAlign = 'right';
  ctx.fillText(xLabel, width - m.right, height - 4);
}

/** Paint the 50x50 board: faint DQ areas behind, one dot per agent sized by its FCT resources. */
export function drawBoard(canvas, { areaRows, size, agents }) {
  const { ctx, width, height } = setup(canvas);
  const cell = Math.min(width, height) / size;
  areaRows.forEach((row, y) => {
    for (let x = 0; x < size; x++) {
      ctx.globalAlpha = 0.16;
      ctx.fillStyle = DQ_COLORS[Number(row[x]) - 1];
      ctx.fillRect(x * cell, y * cell, cell + 0.5, cell + 0.5);
    }
  });
  ctx.globalAlpha = 1;
  for (const a of agents) {
    const r = cell * (0.22 + 0.2 * Math.min(1, a.resources / 4));
    ctx.fillStyle = DQ_COLORS[a.dq];
    ctx.beginPath();
    ctx.arc((a.x + 0.5) * cell, (a.y + 0.5) * cell, r, 0, Math.PI * 2);
    ctx.fill();
  }
}
