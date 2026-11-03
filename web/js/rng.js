// Small seeded PRNG (mulberry32) so a given seed always reproduces the same run.
export function makeRng(seed = 1) {
  let a = (seed >>> 0) || 1;
  const next = () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const rng = {
    next,
    /** integer in [lo, hi) */
    int: (lo, hi) => lo + Math.floor(next() * (hi - lo)),
    uniform: (lo, hi) => lo + next() * (hi - lo),
    normal(mean = 0, sd = 1) {
      const u = 1 - next(), v = next();
      return mean + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    },
    /** numpy-style Lomax/Pareto II sample: U^(-1/a) - 1 */
    pareto: (shape) => Math.pow(1 - next(), -1 / shape) - 1,
    pick: (arr) => arr[Math.floor(next() * arr.length)],
    shuffle(arr) {
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(next() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      return arr;
    },
  };
  return rng;
}
