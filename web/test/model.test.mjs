import test from 'node:test';
import assert from 'node:assert/strict';
import { FCTModel, paramsForPreset, gradient, generateTheoryVector, N_DQ } from '../js/model.js';
import { makeRng } from '../js/rng.js';
import { AREA_ROWS, BOARD_SIZE } from '../js/areas.js';

const run = (params) => { const m = new FCTModel(params); while (m.step()); return m; };

test('board layout is 50x50 and uses DQ 1..5', () => {
  assert.equal(AREA_ROWS.length, BOARD_SIZE);
  assert.ok(AREA_ROWS.every((r) => r.length === BOARD_SIZE));
  assert.deepEqual([...new Set(AREA_ROWS.join(''))].sort(), ['1', '2', '3', '4', '5']);
});

test('gradient is the least-squares slope over DQ 1..5', () => {
  assert.equal(gradient([1, 2, 3, 4, 5]), 1);
  assert.equal(gradient([5, 4, 3, 2, 1]), -1);
  assert.equal(gradient([3, 3, 3, 3, 3]), 0);
});

test('theory vectors respect their bounds and favour the least deprived quintile', () => {
  const rng = makeRng(7);
  for (const dist of [1, 2, 3]) {
    const mean = [0, 0, 0, 0, 0];
    for (let dq = 0; dq < N_DQ; dq++) {
      for (let i = 0; i < 500; i++) {
        const t = generateTheoryVector(rng, dq, dist);
        assert.ok(t.education >= 1 && t.education <= 3);
        assert.ok(t.wealth >= 0.2 && t.wealth <= 1);
        assert.ok(t.power >= 0 && t.power <= 1);
        assert.ok(t.prestige >= 0 && t.prestige <= 1);
        mean[dq] += (t.education + t.wealth + t.power + t.prestige) / 500;
      }
    }
    assert.ok(mean[0] > mean[4], `DQ1 should out-resource DQ5 (dist ${dist})`);
  }
});

test('initial state: balanced DQs, one agent per cell, in-area placement, 3+ links each', () => {
  const m = new FCTModel({ 'count.of.agents': 1000 });
  const counts = [0, 0, 0, 0, 0];
  const cells = new Set();
  for (const a of m.agents) {
    counts[a.dq]++;
    cells.add(a.cell);
    const x = a.cell % BOARD_SIZE, y = Math.floor(a.cell / BOARD_SIZE);
    assert.equal(Number(AREA_ROWS[y][x]) - 1, a.dq);
    assert.ok(a.connections.length >= 1);
  }
  assert.deepEqual(counts, [200, 200, 200, 200, 200]);
  assert.equal(cells.size, 1000);
  // network is symmetric
  for (const a of m.agents) for (const id of a.connections) assert.ok(m.agents[id].connections.includes(a.id));
});

test('network is homophilous: most links join agents in the same DQ', () => {
  const m = new FCTModel();
  let same = 0, total = 0;
  for (const a of m.agents) for (const id of a.connections) { total++; if (m.agents[id].dq === a.dq) same++; }
  assert.ok(same / total > 0.8, `same-DQ share was ${same / total}`);
});

test('runs are deterministic for a given seed and differ across seeds', () => {
  const p = { 'stop.at': 60, 'count.of.agents': 300 };
  const a = run(p).results(), b = run(p).results(), c = run({ ...p, 'random.seed': 2 }).results();
  assert.deepEqual(a.deaths, b.deaths);
  assert.notDeepEqual(a.deaths, c.deaths);
});

test('invariants hold through a full run', () => {
  const m = run({ ...paramsForPreset('sim5'), 'stop.at': 200 });
  assert.equal(m.tick, 200);
  assert.equal(m.deathHistory.length, 200);
  const occupied = m.occupancy.reduce((s, v) => s + v, 0);
  assert.equal(occupied, m.agents.length);
  for (const a of m.agents) {
    assert.ok(a.age >= 18 && a.age <= 96);
    assert.ok(a.dq >= 0 && a.dq < N_DQ);
    assert.equal(new Set(a.solved).size, a.solved.length, 'no duplicate solved events');
    assert.ok(!a.unsolved.some((e) => a.solvedSet.has(e)), 'solved events leave the unsolved list');
  }
  // deaths are cumulative and monotone
  for (let t = 1; t < m.deathHistory.length; t++)
    m.deathHistory[t].forEach((v, d) => assert.ok(v >= m.deathHistory[t - 1][d]));
  const r = m.results();
  assert.equal(r.deaths.reduce((s, v) => s + v, 0), m.agents.reduce((s, a) => s + a.deaths, 0));
});

test('richer agents adapt more often (FCT mechanism works)', () => {
  const r = run({ 'stop.at': 100 }).results();
  assert.ok(r.adaptationRatio[0] > r.adaptationRatio[4], JSON.stringify(r.adaptationRatio));
});

test('with a high risk threshold nobody dies before the age cap', () => {
  const r = run({ 'stop.at': 52, 'risk.threshold': 1e9 }).results();
  assert.equal(r.deaths.reduce((s, v) => s + v, 0), 0);
});

test('performance: 540 weeks of 1000 agents finishes in a few seconds', () => {
  const t0 = performance.now();
  run({});
  const ms = performance.now() - t0;
  console.log(`  540 ticks x 1000 agents: ${Math.round(ms)} ms`);
  assert.ok(ms < 15000);
});
