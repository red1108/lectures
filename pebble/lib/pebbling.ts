/** Pebble-game replay shared by every animation; no arithmetic oracle is simulated. */
export type State = 'empty' | 'pebble' | 'ghost'
export type Round = { p: number[], u: number[], g: number[] }
export type Trace = {
  kind: string, graph: 'tree' | 'path', height?: number, length?: number,
  budget?: number, initial: number[], rounds: Round[], source: string,
  metrics?: {work: number, depth: number, peak: number}
}
export type Frame = {
  state: State[], step: number, work: number, space: number, peak: number,
  actions: Round, corrected: number[]
}

export function replay(trace: Trace): Frame[] {
  const n = trace.graph === 'tree' ? (2 ** trace.height! - 1) : trace.length! + 1
  const lo = trace.graph === 'tree' ? 1 : 0
  const max = trace.graph === 'tree' ? n : n - 1
  const state: State[] = Array(max + 1).fill('empty')
  for (const v of trace.initial) {
    if (v < lo || v > max || state[v] !== 'empty') throw new Error('Invalid initial pebble')
    state[v] = 'pebble'
  }
  const occupied = () => state.filter(v => v === 'pebble').length
  let work = 0, peak = occupied()
  const snapshot = (step: number, actions: Round, corrected: number[]): Frame => ({
    state: [...state], step, work, space: occupied(), peak, actions, corrected,
  })
  const frames = [snapshot(0, {p: [], u: [], g: []}, [])]
  const inputs = (v: number): number[] => trace.graph === 'path'
    ? (v === 0 ? [] : [v - 1])
    : (2 * v <= max ? [2 * v, 2 * v + 1] : [])
  for (const [index, r] of trace.rounds.entries()) {
    if (!r.p.length && !r.u.length && !r.g.length) throw new Error(`Empty round ${index + 1}`)
    const before = [...state], used = new Set<number>(), targets = new Set<number>()
    for (const [kind, list] of [['p', r.p], ['u', r.u]] as const) {
      for (const v of list) {
        if (!Number.isInteger(v) || v < lo || v > max) throw new Error(`Invalid vertex ${v}`)
        if (kind === 'p' && before[v] === 'pebble') throw new Error(`Already pebbled ${v}`)
        if (kind === 'u' && before[v] !== 'pebble') throw new Error(`No value to uncompute ${v}`)
        const active = [v, ...inputs(v)]
        if (inputs(v).some(c => before[c] !== 'pebble')) throw new Error(`Missing input at ${v}, step ${index + 1}`)
        if (active.some(c => used.has(c))) throw new Error(`Active sets overlap at step ${index + 1}`)
        for (const c of active) used.add(c)
        targets.add(v)
      }
    }
    const during = occupied() + r.p.length
    peak = Math.max(peak, during)
    if (trace.budget != null && during > trace.budget) throw new Error(`Space exceeded at step ${index + 1}`)
    const corrected = r.p.filter(v => before[v] === 'ghost')
    for (const v of r.p) state[v] = 'pebble'
    for (const v of r.u) state[v] = 'empty'
    const ghosts = new Set<number>()
    for (const v of r.g) {
      if (v < lo || v > max || ghosts.has(v) || state[v] !== 'pebble' || r.u.includes(v))
        throw new Error(`Illegal ghost at ${v}, step ${index + 1}`)
      ghosts.add(v); state[v] = 'ghost'
    }
    work += r.p.length + r.u.length
    frames.push(snapshot(index + 1, r, corrected))
  }
  return frames
}

const round = (action: 'p' | 'u' | 'g', vertex: number): Round => ({p: [], u: [], g: [], [action]: [vertex]})
function treeTrace(kind: string, ops: [string, number][], budget: number): Trace {
  return {kind, graph: 'tree', height: 3, budget, initial: [], source: 'Teaching example; H=3',
    rounds: ops.map(([a, v]) => round(a as 'p' | 'u' | 'g', v))}
}
export const reversible = treeTrace('reversible', [
  ['p',4],['p',5],['p',2],['u',5],['u',4],
  ['p',6],['p',7],['p',3],['p',1],['u',3],['u',7],['u',6],
  ['p',4],['p',5],['u',2],['u',5],['u',4],
], 5)
export const spooky = treeTrace('spooky', [
  ['p',4],['p',5],['p',2],['u',4],['u',5],
  ['p',6],['p',7],['p',3],['u',6],['u',7],['p',1],
  ['g',2],['g',3],
  ['p',4],['p',5],['p',2],['u',2],['u',4],['u',5],
  ['p',6],['p',7],['p',3],['u',3],['u',6],['u',7],
], 4)
