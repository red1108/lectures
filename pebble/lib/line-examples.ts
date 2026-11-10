import type { Round, Trace, State } from './pebbling.ts'

function action(kind: 'p' | 'u' | 'g', vertex: number): Round {
  const step: Round = { p: [], u: [], g: [] }
  step[kind].push(vertex)
  return step
}

function lineTrace(kind: string, rounds: Round[], budget: number, source: string): Trace {
  return { kind, graph: 'path', length: 7, initial: [], rounds, budget, source }
}

const sweep: Round[] = []
for (let vertex = 0; vertex < 8; vertex++) sweep.push(action('p', vertex))
for (let vertex = 6; vertex >= 0; vertex--) sweep.push(action('u', vertex))
export const lineSimple = lineTrace('line-simple', sweep, 8, 'Line example · 8 nodes · starts empty')

const recursive: Round[] = []
function divideAndConquer(offset: number, length: number, operation: 'p' | 'u') {
  if (length === 0) return
  if (length === 1) {
    recursive.push(action(operation, offset))
    return
  }
  const half = Math.ceil(length / 2)
  divideAndConquer(offset, half, 'p')
  divideAndConquer(offset + half, length - half, operation)
  divideAndConquer(offset, half, 'u')
}
divideAndConquer(0, 8, 'p')
export const lineReversible = lineTrace('line-reversible', recursive, 4, 'Reversible divide and conquer · 8 nodes')

const ghostSweep: Round[] = []
const states: State[] = Array(8).fill('empty')
function emit(kind: 'p' | 'u' | 'g', vertex: number) {
  ghostSweep.push(action(kind, vertex))
  states[vertex] = kind === 'p' ? 'pebble' : kind === 'u' ? 'empty' : 'ghost'
}
let remaining = 8
while (remaining > 0) {
  for (let vertex = 0; vertex < remaining - 1; vertex++) {
    emit('p', vertex)
    if (vertex > 0) emit('g', vertex - 1)
  }
  const target = remaining - 1
  if (remaining === 8) emit('p', target)
  else {
    // The manuscript's rule clears a ghost by recomputing and uncomputing.
    if (states[target] === 'ghost') emit('p', target)
    emit('u', target)
  }
  remaining--
  if (remaining > 0) emit('g', remaining - 1)
  while (remaining > 0 && states[remaining - 1] === 'empty') remaining--
}
export const lineSpooky = lineTrace('line-spooky', ghostSweep, 3,
  'Ghost sweep and cleanup · 8 nodes · 3 registers')

export const lineExamples = {
  'line-simple': lineSimple,
  'line-reversible': lineReversible,
  'line-spooky': lineSpooky,
}
