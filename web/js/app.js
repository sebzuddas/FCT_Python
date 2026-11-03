import { FCTModel, PRESETS, paramsForPreset, gradient } from './model.js';
import { AREA_ROWS, BOARD_SIZE } from './areas.js';
import { drawBars, drawLines, drawBoard, formatNumber } from './charts.js';

const $ = (id) => document.getElementById(id);

/** Parameter controls. `key` matches the YAML key used by the Python model. */
const FIELDS = [
  { key: 'stop.at', label: 'Simulation length (weeks)', type: 'range', min: 20, max: 1560, step: 20, fmt: (v) => `${v} (${(v / 52).toFixed(1)} yrs)` },
  { key: 'count.of.agents', label: 'People', type: 'range', min: 200, max: 2000, step: 100 },
  { key: 'random.seed', label: 'Random seed', type: 'number', min: 1, max: 99999, step: 1 },
  { key: 'risk.function', label: 'Risk function', type: 'select', options: [['modified', 'Modified (Experiment Set 2)'], ['original', 'Original (Experiment Set 1)']] },
  { key: 'risk.threshold', label: 'Risk threshold for death', type: 'range', min: 0.01, max: 1, step: 'any', fmt: (v) => v.toFixed(2) },
  { key: 'risk.modifier.beta', label: 'Risk modifier β (modified function)', type: 'range', min: 0, max: 0.5, step: 'any', fmt: (v) => v.toFixed(2) },
  { key: 'beta.modifier.male', label: 'Alcohol risk, men', type: 'range', min: 0.001, max: 0.005, step: 'any', fmt: (v) => v.toFixed(4) },
  { key: 'beta.modifier.female', label: 'Alcohol risk, women', type: 'range', min: 0.0005, max: 0.0015, step: 'any', fmt: (v) => v.toFixed(5) },
  { key: 'communicator.max.reach', label: 'Messages reach (people per week)', type: 'range', min: 1, max: 1000, step: 1 },
  { key: 'communication.success', label: 'Peer-to-peer success chance', type: 'range', min: 0, max: 1, step: 'any', fmt: (v) => v.toFixed(2) },
  { key: 'successful.adaptation.knowlege.benefit', label: 'Knowledge gained per success', type: 'range', min: 0, max: 0.1, step: 'any', fmt: (v) => v.toFixed(3) },
  { key: 'theory.distribution.type', label: 'Resource distribution', type: 'select', numeric: true, options: [[1, 'Uniform'], [2, 'Normal'], [3, 'Pareto']] },
  { key: 'drink.distribution.type', label: 'Drinking distribution', type: 'select', numeric: true, options: [[1, 'Uniform'], [2, 'Normal']] },
];

const state = {
  presetKey: 'sim5',
  params: paramsForPreset('sim5'),
  model: null,
  running: false,
  raf: 0,
};

// ------------------------------------------------------------------ controls
function buildFields() {
  const host = $('param-fields');
  host.innerHTML = '';
  for (const f of FIELDS) {
    const wrap = document.createElement('label');
    wrap.className = 'field';
    const id = `p-${f.key}`;
    const label = document.createElement('span');
    label.className = 'field-label';
    label.textContent = f.label;
    wrap.append(label);

    let input;
    if (f.type === 'select') {
      input = document.createElement('select');
      for (const [value, text] of f.options) input.add(new Option(text, value));
    } else {
      input = document.createElement('input');
      input.type = f.type;
      input.min = f.min; input.max = f.max; input.step = f.step;
      if (f.type === 'range') {
        const out = document.createElement('output');
        out.id = `${id}-out`;
        label.append(out);
      }
    }
    input.id = id;
    input.dataset.key = f.key;
    input.addEventListener(f.type === 'range' ? 'input' : 'change', () => onParamChange(f, input));
    wrap.append(input);
    host.append(wrap);
  }
}

function syncFields() {
  for (const f of FIELDS) {
    const input = $(`p-${f.key}`);
    const v = state.params[f.key];
    input.value = v;
    if (f.type === 'range') $(`p-${f.key}-out`).textContent = (f.fmt ?? String)(Number(v));
  }
}

function onParamChange(f, input) {
  let v = input.value;
  if (f.type === 'range' || f.type === 'number' || f.numeric) v = Number(v);
  state.params = { ...state.params, [f.key]: v };
  if (f.type === 'range') $(`p-${f.key}-out`).textContent = (f.fmt ?? String)(v);
  resetModel();
}

function setPreset(key) {
  state.presetKey = key;
  state.params = paramsForPreset(key);
  $('preset-note').textContent = PRESETS[key].note;
  syncFields();
  resetModel();
}

// ------------------------------------------------------------------ run loop
function resetModel() {
  stop();
  state.model = new FCTModel(state.params);
  $('btn-run').textContent = 'Run';
  render(true);
}

function stop() {
  state.running = false;
  cancelAnimationFrame(state.raf);
  $('btn-run').textContent = state.model && state.model.tick > 0 && !state.model.done ? 'Resume' : 'Run';
}

function frame() {
  if (!state.running) return;
  const perFrame = Number($('speed').value);
  const m = state.model;
  if (perFrame === 0) { while (m.step()); } else { for (let i = 0; i < perFrame && m.step(); i++); }
  render();
  if (m.done) { stop(); $('btn-run').textContent = 'Run again'; return; }
  state.raf = requestAnimationFrame(frame);
}

function run() {
  if (state.model.done) resetModel();
  state.running = true;
  $('btn-run').textContent = 'Pause';
  state.raf = requestAnimationFrame(frame);
}

// ------------------------------------------------------------------ rendering
const fitOf = (values) => {
  const slope = gradient(values);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const intercept = mean - slope * 3; // x-mean of 1..5 is 3
  return { at: (x) => intercept + slope * x };
};

function setChip(id, value, ok) {
  const el = $(id);
  el.querySelector('.chip-v').textContent = value === null ? '–' : formatNumber(value);
  el.dataset.ok = value === null ? '' : String(ok);
}

function render() {
  const m = state.model;
  const r = m.results();
  const years = (m.tick / 52).toFixed(1);
  $('readout-week').textContent = `Week ${m.tick}`;
  $('readout-year').textContent = `of ${m.params['stop.at']} · year ${years}`;

  drawBoard($('board'), { areaRows: AREA_ROWS, size: BOARD_SIZE, agents: m.boardSnapshot() });

  const started = m.tick > 0;
  drawBars($('c-deaths'), { values: r.deaths, fit: started ? fitOf(r.deaths) : null });
  drawLines($('c-history'), {
    series: [0, 1, 2, 3, 4].map((d) => r.deathHistory.map((row) => row[d])),
    xMax: m.params['stop.at'],
  });
  drawBars($('c-adapt'), { values: r.adaptationRatio, fit: started ? fitOf(r.adaptationRatio) : null, format: (v) => v.toFixed(2) });
  drawBars($('c-cons'), { values: r.meanConsumption, fit: started ? fitOf(r.meanConsumption) : null, format: (v) => v.toFixed(0) });

  const g = r.gradients;
  setChip('chip-deaths', started ? g.deaths : null, g.deaths > 0);
  setChip('chip-adapt', started ? g.adaptation : null, g.adaptation < 0);
  setChip('chip-cons', started ? g.consumption : null, g.consumption < 0);

  const verdict = $('verdict');
  if (!started) {
    verdict.dataset.state = 'idle';
    $('verdict-title').textContent = 'Press Run to start the simulation';
    $('verdict-sub').textContent = 'The Alcohol Harm Paradox needs all three gradients below, measured across DQ1 to DQ5.';
  } else if (r.ahp) {
    verdict.dataset.state = 'yes';
    $('verdict-title').textContent = m.done ? 'The AHP signature is present in this run' : 'The AHP signature is present so far';
    $('verdict-sub').textContent = 'All three gradients have the expected sign. Check whether it persists with other seeds or a longer run.';
  } else {
    verdict.dataset.state = 'no';
    const missing = [g.deaths <= 0 && 'γ₁', g.adaptation >= 0 && 'γ₂', g.consumption >= 0 && 'γ₃'].filter(Boolean).join(', ');
    $('verdict-title').textContent = m.done ? 'No AHP signature in this run' : 'No AHP signature yet';
    $('verdict-sub').textContent = `${missing} ${missing.includes(',') ? 'do' : 'does'} not have the expected sign.`;
  }

  const alt = (id, text) => $(id).setAttribute('aria-label', text);
  alt('c-deaths', `Total deaths by deprivation quintile, DQ1 to DQ5: ${r.deaths.join(', ')}`);
  alt('c-adapt', `Share of events adapted to by quintile: ${r.adaptationRatio.map((v) => v.toFixed(3)).join(', ')}`);
  alt('c-cons', `Mean weekly units by quintile: ${r.meanConsumption.map((v) => v.toFixed(1)).join(', ')}`);
}

// ------------------------------------------------------------------ seed sweep
let sweeping = false;
async function sweep() {
  if (sweeping) return;
  sweeping = true;
  stop();
  const btn = $('btn-sweep'), out = $('sweep-out');
  btn.disabled = true;
  const runs = 20;
  const tally = { ahp: 0, g1: 0, g2: 0, g3: 0 };
  const sums = { g1: 0, g2: 0, g3: 0 };
  for (let i = 0; i < runs; i++) {
    out.textContent = `Running seed ${i + 1} of ${runs}…`;
    await new Promise((r) => setTimeout(r, 0)); // let the page paint
    const m = new FCTModel({ ...state.params, 'random.seed': i + 1 });
    while (m.step());
    const { gradients: g, ahp } = m.results();
    tally.ahp += ahp; tally.g1 += g.deaths > 0; tally.g2 += g.adaptation < 0; tally.g3 += g.consumption < 0;
    sums.g1 += g.deaths; sums.g2 += g.adaptation; sums.g3 += g.consumption;
  }
  out.innerHTML =
    `<strong>${tally.ahp} of ${runs}</strong> runs show all three AHP conditions.<br>` +
    `γ₁ &gt; 0 in ${tally.g1}, γ₂ &lt; 0 in ${tally.g2}, γ₃ &lt; 0 in ${tally.g3}. ` +
    `Mean γ₁ ${formatNumber(sums.g1 / runs)}, γ₂ ${formatNumber(sums.g2 / runs)}, γ₃ ${formatNumber(sums.g3 / runs)}.`;
  btn.disabled = false;
  sweeping = false;
}

// ------------------------------------------------------------------ boot
function init() {
  const preset = $('preset');
  for (const [key, p] of Object.entries(PRESETS)) preset.add(new Option(p.label, key));
  preset.value = state.presetKey;
  preset.addEventListener('change', () => setPreset(preset.value));

  buildFields();
  $('btn-run').addEventListener('click', () => (state.running ? (stop(), render()) : run()));
  $('btn-step').addEventListener('click', () => { stop(); if (state.model.done) resetModel(); state.model.step(); render(); });
  $('btn-reset').addEventListener('click', resetModel);
  $('btn-sweep').addEventListener('click', sweep);

  let resizeTimer;
  window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => render(), 100); });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => render());

  setPreset(state.presetKey);
}

init();
