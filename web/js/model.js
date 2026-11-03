/**
 * Fundamental Cause Theory agent-based model — JavaScript port.
 *
 * A browser-friendly re-implementation of the Python/Repast4Py model in
 * ../../FCT_Model, written for the MEng dissertation "Complex Systems Modelling
 * of Alcohol-related Health Inequalities" (University of Sheffield, 2023).
 *
 * The model follows the Mechanism-Based Social Systems Modelling (MBSSM) layout:
 *
 *   situational mechanism      the communicator broadcasts an event to a random subset of agents
 *   action mechanism           agents try to decode events, pass solved events to network
 *                              neighbours, drink, and carry the resulting risk
 *   transformational mechanism once a year, agents swap deprivation quintiles (DQs)
 *
 * One tick = one week. DQ indices are 0..4 internally (DQ1..DQ5 on screen);
 * DQ1 is the least deprived quintile, DQ5 the most deprived.
 *
 * No DOM access in here, so the same file runs under Node for the tests.
 */
import { makeRng } from './rng.js';
import { AREA_ROWS, BOARD_SIZE } from './areas.js';

export const N_DQ = 5;
const WEEKS_PER_YEAR = 52;
const MAX_AGE = 95;
const RESPAWN_AGE = 18;

/** Mean attributes per DQ: [education, wealth, power, prestige] (DQ1 .. DQ5). */
const THEORY_BASE_MEANS = [
  [2.5, 5, 1, 1],
  [2, 4, 0.75, 0.75],
  [1.5, 3, 0.5, 0.5],
  [1, 2, 0.25, 0.25],
  [0.5, 1, 0, 0],
];

/** Yearly swap probabilities per DQ: [moveUp, moveDown], after Giorgi et al. (dissertation Table 3.2). */
const SWAP_PROBABILITIES = [[0.3, 0], [0.3, 0], [0.4, 0], [0, 0.4], [0, 0.6]];

/** Parameters, named after the YAML keys used by the Python model. */
export const DEFAULT_PARAMS = Object.freeze({
  'random.seed': 1,
  'stop.at': 540,
  'count.of.agents': 1000,
  'risk.function': 'modified', // 'original' (Experiment Set 1) | 'modified' (Experiment Set 2)
  'risk.threshold': 0.5,
  'risk.modifier.beta': 0.25,
  'beta.modifier.male': 0.00389,
  'beta.modifier.female': 0.00101,
  'communicator.max.reach': 200,
  'communication.success': 1,
  'successful.adaptation.knowlege.benefit': 0.05,
  'theory.distribution.type': 1, // 1 uniform, 2 normal, 3 Pareto
  'drink.distribution.type': 1, // 1 uniform, 2 normal
});

/** Parameter sets from the dissertation's appendices, plus the repo defaults. */
export const PRESETS = {
  standard: {
    label: 'Repository defaults',
    note: 'The values in FCT_Model/props/model/standard.yaml, with the modified risk function.',
    params: {},
  },
  sim70: {
    label: 'Experiment Set 1 · Simulation 70',
    note: 'Original risk function. The set-1 run whose death gradient looked most like the AHP (γ₁ = 389.6), though its consumption gradient was positive.',
    params: {
      'risk.function': 'original',
      'beta.modifier.female': 0.001318,
      'beta.modifier.male': 0.001061,
      'communication.success': 0.099509,
      'communicator.max.reach': 91,
      'successful.adaptation.knowlege.benefit': 0.025479,
      'risk.modifier.beta': 0.417671,
      'risk.threshold': 0.20809,
      'theory.distribution.type': 1,
      'drink.distribution.type': 1,
      'stop.at': 520,
    },
  },
  sim5: {
    label: 'Experiment Set 2 · Simulation 5',
    note: 'Modified risk function. The one run, out of 200, in which all three AHP gradients had the expected sign.',
    params: {
      'risk.function': 'modified',
      'beta.modifier.female': 0.000834,
      'beta.modifier.male': 0.002011,
      'communication.success': 0.120978,
      'communicator.max.reach': 664,
      'successful.adaptation.knowlege.benefit': 0.035906,
      'risk.modifier.beta': 0.394013,
      'risk.threshold': 0.064128,
      'theory.distribution.type': 3,
      'drink.distribution.type': 1,
      'stop.at': 520,
    },
  },
  sim5long: {
    label: 'Experiment Set 2 · Simulation 5, extended',
    note: 'The same parameters run for 1200 weeks. In the dissertation the AHP signature disappears (γ₂ and γ₃ turn positive).',
    params: {
      'risk.function': 'modified',
      'beta.modifier.female': 0.000834,
      'beta.modifier.male': 0.002011,
      'communication.success': 0.120978,
      'communicator.max.reach': 664,
      'successful.adaptation.knowlege.benefit': 0.035906,
      'risk.modifier.beta': 0.394013,
      'risk.threshold': 0.064128,
      'theory.distribution.type': 3,
      'drink.distribution.type': 1,
      'stop.at': 1200,
    },
  },
};

export function paramsForPreset(key) {
  return { ...DEFAULT_PARAMS, ...(PRESETS[key]?.params ?? {}) };
}

/** Logistic function. */
const expit = (x) => 1 / (1 + Math.exp(-x));
const clip = (x, lo, hi) => Math.min(hi, Math.max(lo, x));

/** Least-squares slope of y against DQ number 1..5 (the "gradient" used to look for the AHP). */
export function gradient(values) {
  const n = values.length;
  const xs = values.map((_, i) => i + 1);
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = values.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) {
    num += (xs[i] - mx) * (values[i] - my);
    den += (xs[i] - mx) ** 2;
  }
  return den === 0 ? 0 : num / den;
}

/** Draw [education, wealth, power, prestige] for an agent in a DQ (see generate_theory_vector in the Python model). */
export function generateTheoryVector(rng, dq, distributionType) {
  const [mEdu, mWealth, mPower, mPrestige] = THEORY_BASE_MEANS[dq];
  let edu, wealth, power, prestige;
  if (distributionType === 2) {
    const sd = 0.15;
    edu = rng.normal(mEdu, sd); wealth = rng.normal(mWealth, sd);
    power = rng.normal(mPower, sd); prestige = rng.normal(mPrestige, sd);
  } else if (distributionType === 3) {
    const shape = 2;
    edu = rng.pareto(shape) / shape + mEdu; wealth = rng.pareto(shape) / shape + mWealth;
    power = rng.pareto(shape) / shape + mPower; prestige = rng.pareto(shape) / shape + mPrestige;
  } else {
    edu = rng.uniform(mEdu, 4); wealth = rng.uniform(mWealth, 6);
    power = rng.uniform(mPower, 2); prestige = rng.uniform(mPrestige, 2);
  }
  return {
    education: clip(edu, 1, 3),
    wealth: clip(wealth, 1, 5) / 5,
    power: clip(power, 0, 1),
    prestige: clip(prestige, 0, 1),
  };
}

export class FCTModel {
  constructor(params = {}) {
    this.params = { ...DEFAULT_PARAMS, ...params };
    const p = this.params;
    this.rng = makeRng(p['random.seed']);
    this.tick = 0;
    this.nAgents = p['count.of.agents'];

    // Board geometry: cells grouped by DQ, plus an occupancy grid (one agent per cell).
    this.cellsByDq = Array.from({ length: N_DQ }, () => []);
    AREA_ROWS.forEach((row, y) => {
      [...row].forEach((ch, x) => this.cellsByDq[Number(ch) - 1].push(y * BOARD_SIZE + x));
    });
    this.occupancy = new Uint8Array(BOARD_SIZE * BOARD_SIZE);

    // Communicator state: the numeric value of every event ever broadcast (index = event id).
    this.eventValues = [];

    // Running statistics, indexed by DQ.
    this.deathsByDq = new Array(N_DQ).fill(0);
    this.successByDq = new Array(N_DQ).fill(0);
    this.failureByDq = new Array(N_DQ).fill(0);
    this.unitsAccumByDq = new Array(N_DQ).fill(0); // sum over ticks of mean weekly units in the DQ
    this.deathHistory = []; // cumulative deaths by DQ, one row per tick

    this.#initAgents();
    this.#initNetwork();
  }

  // ---------------------------------------------------------------- set-up
  #initAgents() {
    const { rng, nAgents: n, params: p } = this;

    // Balanced DQs, shuffled (as in generate_agent_json_file).
    const labels = [];
    for (let i = 0; i < n; i++) labels.push(i % N_DQ);
    rng.shuffle(labels);

    this.agents = [];
    for (let id = 0; id < n; id++) {
      const dq = labels[id];
      const sex = rng.next() < 0.5 ? 0 : 1; // 0 female, 1 male
      const age = rng.int(18, 80);
      const status = rng.int(0, 5); // drinking status multiplier, 0..4
      const units = p['drink.distribution.type'] === 2
        ? Math.abs(rng.normal(25, 10))
        : rng.uniform(0, 130);
      const meanWeeklyUnits = Math.round(units * 1000) / 1000;
      const t = generateTheoryVector(rng, dq, p['theory.distribution.type']);

      // Absolute risk of alcohol consumption: rho(c) = 100 * beta * (c - 0.5)  (dissertation Eq. 3.4).
      const consumption = Math.round(status * meanWeeklyUnits * 100) / 100;
      const beta = sex === 0 ? p['beta.modifier.female'] : p['beta.modifier.male'];
      const absRisk = consumption === 0 ? 0 : 100 * beta * (consumption - 0.5);

      this.agents.push({
        id, dq, sex, age, status, meanWeeklyUnits, absRisk,
        education: t.education, wealth: t.wealth, power: t.power, prestige: t.prestige,
        knowledge: t.education / 3,
        targetConnections: 3,
        connections: [],
        solved: [], solvedSet: new Set(), unsolved: [],
        deaths: 0, successes: 0, failures: 0,
        cell: -1,
      });
    }

    // Initial placement: a random free cell inside the agent's own DQ area.
    for (const a of this.agents) this.#relocate(a);
  }

  /** Move an agent to a random unoccupied cell in its DQ area. */
  #relocate(agent) {
    const cells = this.cellsByDq[agent.dq];
    let target = -1;
    for (let i = 0; i < 200; i++) {
      const c = cells[Math.floor(this.rng.next() * cells.length)];
      if (!this.occupancy[c]) { target = c; break; }
    }
    if (target < 0) target = cells.find((c) => !this.occupancy[c]) ?? -1; // crowded: scan
    if (target < 0) return; // area completely full: stay put
    if (agent.cell >= 0) this.occupancy[agent.cell] = 0;
    this.occupancy[target] = 1;
    agent.cell = target;
  }

  /**
   * Homophilous network: agents prefer to link to someone in the same DQ and within five years
   * of age (the effective rule in the Python model), until each has `targetConnections` links.
   */
  #initNetwork() {
    const { rng, agents } = this;
    const byDq = Array.from({ length: N_DQ }, () => []);
    agents.forEach((a) => byDq[a.dq].push(a));

    const linked = (a, b) => a.connections.includes(b.id);
    const hasRoom = (a) => a.connections.length < a.targetConnections;
    const link = (a, b) => { a.connections.push(b.id); b.connections.push(a.id); };

    for (const a of agents) {
      let guard = 0;
      while (hasRoom(a) && guard++ < 400) {
        let b;
        if (guard <= 300) b = rng.pick(byDq[a.dq]);
        else b = rng.pick(agents); // fall back to anyone with spare capacity
        if (b === a || linked(a, b) || !hasRoom(b)) continue;
        if (guard <= 200 && Math.abs(a.age - b.age) >= 5) continue; // same DQ *and* similar age first
        link(a, b);
      }
    }
    // Isolated agents would make the communication step undefined; connect them to anyone.
    for (const a of agents) {
      while (a.connections.length === 0) {
        const b = rng.pick(agents);
        if (b !== a) link(a, b);
      }
    }
  }

  // ---------------------------------------------------------------- mechanisms
  /** Agent receives an event it has not solved yet. */
  #interpretEvent(agent, eventId) { agent.unsolved.push(eventId); }

  /** Record the outcome of an adaptation attempt (see handle_event in FCT_Agent.py). */
  #handleEvent(agent, eventId, isSolved) {
    if (!isSolved) { agent.unsolved.push(eventId); return; }
    agent.solved.push(eventId);
    agent.solvedSet.add(eventId);
    if (agent.unsolved.includes(eventId)) agent.unsolved = agent.unsolved.filter((e) => e !== eventId);
  }

  /** Situational mechanism: broadcast one random 5-bit event to up to `reach` random agents. */
  #situational() {
    const { rng, agents, params: p } = this;
    const eventId = this.eventValues.length;
    this.eventValues.push(rng.int(0, 32) / 4); // decimal value of a random 5-bit binary string, /4
    const reach = Math.min(p['communicator.max.reach'], agents.length);
    // partial Fisher-Yates to sample `reach` agents without replacement
    const order = this.reachBuffer ?? (this.reachBuffer = agents.map((_, i) => i));
    for (let i = 0; i < reach; i++) {
      const j = i + Math.floor(rng.next() * (order.length - i));
      [order[i], order[j]] = [order[j], order[i]];
      this.#interpretEvent(agents[order[i]], eventId);
    }
  }

  /** Action mechanism: peer-to-peer communication, then each agent's own adaptation attempt, move and drink. */
  #action() {
    const { rng, agents, params: p } = this;

    // 1) Peer communication: each agent offers one solved event to a random neighbour.
    for (const a of agents) {
      if (a.solved.length === 0) continue;
      const b = agents[rng.pick(a.connections)];
      const eventId = rng.pick(a.solved);
      // As in the Python model, a neighbour that has solved nothing yet is skipped.
      if (b.solved.length === 0 || b.solvedSet.has(eventId)) continue;
      this.#handleEvent(b, eventId, rng.next() <= p['communication.success']);
    }

    // 2) Own action: try to decode one pending event, then relocate.
    const order = this.actionOrder ?? (this.actionOrder = agents.map((_, i) => i));
    rng.shuffle(order);
    for (const idx of order) {
      const a = agents[idx];
      if (a.unsolved.length > 0) {
        const eventId = rng.pick(a.unsolved);
        const resources = a.knowledge + a.wealth + a.prestige + a.power;
        if (this.eventValues[eventId] <= resources) {
          a.successes++;
          this.successByDq[a.dq]++;
          if (a.knowledge < 1) a.knowledge += p['successful.adaptation.knowlege.benefit'];
          this.#handleEvent(a, eventId, true);
        } else {
          a.failures++;
          this.failureByDq[a.dq]++;
        }
      }
      this.#relocate(a);
    }
  }

  /** Transformational mechanism: yearly DQ swap between agents tagged "up" and "down". */
  #transformational() {
    const { rng, agents } = this;
    const up = [], down = [];
    for (const a of rng.shuffle(agents.slice())) {
      const [pUp, pDown] = SWAP_PROBABILITIES[a.dq];
      if (rng.next() < pUp) up.push({ agent: a, dq: a.dq });
      else if (rng.next() < pDown) down.push({ agent: a, dq: a.dq });
    }
    if (down.length === 0) return;
    // Pad the shorter list with its last element so every "up" agent finds a partner
    // (matches the Python model; the longer list is otherwise truncated by zip).
    while (up.length > down.length) down.push(down[down.length - 1]);
    const pairs = Math.min(up.length, down.length);
    for (let i = 0; i < pairs; i++) {
      const u = up[i], d = down[i];
      u.agent.dq = d.dq;
      d.agent.dq = u.dq;
    }
  }

  /** Yearly bookkeeping: swap DQs, age everyone, and apply the death rule. */
  #yearly() {
    const { agents, params: p } = this;
    this.#transformational();
    const beta = p['risk.modifier.beta'];
    for (const a of agents) {
      a.age += 1;
      const failed = a.unsolved.length;
      const solved = a.solved.length;
      const logistic = expit((a.age - 45) / 9.5);
      let risk;
      if (p['risk.function'] === 'original') {
        // Original (Experiment Set 1): scale by the share of pending (unsolved) events.
        const total = solved + failed;
        risk = total === 0 ? a.absRisk * logistic : a.absRisk * logistic * (failed / total);
      } else if (failed === 0) {
        risk = a.absRisk * logistic;
      } else {
        // Modified (Experiment Set 2): reward a high solved ratio.
        const ratio = solved / (solved + failed);
        risk = a.absRisk * Math.pow(1 + ratio - 0.5, beta) * logistic;
      }
      if (a.age > MAX_AGE || risk > p['risk.threshold']) {
        a.deaths += 1;
        this.deathsByDq[a.dq] += 1;
        a.age = RESPAWN_AGE;
      }
    }
  }

  // ---------------------------------------------------------------- stepping
  get done() { return this.tick >= this.params['stop.at']; }

  /** Advance the simulation by one week. */
  step() {
    if (this.done) return false;
    this.tick += 1;
    this.#situational();
    this.#action();
    if ((this.tick - 1) % WEEKS_PER_YEAR === 0) this.#yearly(); // yearly events fire on ticks 1, 53, 105, ...

    // consumption bookkeeping (by the DQ each agent currently lives in)
    const sums = new Array(N_DQ).fill(0), counts = new Array(N_DQ).fill(0);
    for (const a of this.agents) { sums[a.dq] += a.meanWeeklyUnits; counts[a.dq]++; }
    for (let d = 0; d < N_DQ; d++) if (counts[d]) this.unitsAccumByDq[d] += sums[d] / counts[d];
    this.deathHistory.push(this.deathsByDq.slice());
    return true;
  }

  // ---------------------------------------------------------------- results
  /** Everything the UI needs to describe the run so far. */
  results() {
    const t = Math.max(this.tick, 1);
    const adaptationRatio = this.successByDq.map((s, d) => {
      const total = s + this.failureByDq[d];
      return total === 0 ? 0 : s / total;
    });
    const meanConsumption = this.unitsAccumByDq.map((u) => u / t);
    const deaths = this.deathsByDq.slice();
    const gradients = {
      deaths: gradient(deaths),
      adaptation: gradient(adaptationRatio),
      consumption: gradient(meanConsumption),
    };
    return {
      tick: this.tick,
      deaths,
      adaptationRatio,
      successes: this.successByDq.slice(),
      failures: this.failureByDq.slice(),
      meanConsumption,
      gradients,
      /** The three conditions from dissertation §4.3 */
      ahp: gradients.deaths > 0 && gradients.adaptation < 0 && gradients.consumption < 0,
      deathHistory: this.deathHistory,
    };
  }

  /** Flat snapshot for drawing the board: one entry per agent. */
  boardSnapshot() {
    return this.agents.map((a) => ({
      x: a.cell % BOARD_SIZE,
      y: Math.floor(a.cell / BOARD_SIZE),
      dq: a.dq,
      resources: a.knowledge + a.wealth + a.prestige + a.power,
    }));
  }
}
