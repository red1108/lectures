import { replay, type Round, type Trace } from './pebbling.ts'

export type CleanupLine = 'prepare-left' | 'prepare-right' | 'correct' | 'uncompute' | 'release-left' | 'release-right'
export type CleanupAnnotation = {
  root: number
  line: CleanupLine
  branch: 'left' | 'right'
  callers: ('left' | 'right')[]
}

/** Locate cleanup calls in the captured C++ trace, checking every action. */
export function describeKssCleanup(trace: Trace) {
  const frames = replay(trace)
  const rootEnd = trace.rounds.findIndex(round => round.p.includes(1)) + 3
  const annotations: (CleanupAnnotation | null)[] = Array(trace.rounds.length + 1).fill(null)
  const lastVertex = 2 ** trace.height! - 1
  let cursor = rootEnd

  function action(kind: keyof Round, vertex: number, context: CleanupAnnotation) {
    const round = trace.rounds[cursor]
    if (!round || round[kind].length !== 1 || round[kind][0] !== vertex
      || round.p.length + round.u.length + round.g.length !== 1) {
      throw new Error(`KSS cleanup annotation disagrees with native step ${cursor + 1}`)
    }
    annotations[++cursor] = context
  }

  function release(vertex: number, context: CleanupAnnotation) {
    action(vertex * 2 > lastVertex ? 'u' : 'g', vertex, context)
  }

  function pebble(vertex: number, context: CleanupAnnotation) {
    if (vertex * 2 <= lastVertex) {
      pebble(vertex * 2, context)
      pebble(vertex * 2 + 1, context)
    }
    action('p', vertex, context)
    if (vertex * 2 <= lastVertex) {
      release(vertex * 2, context)
      release(vertex * 2 + 1, context)
    }
  }

  function cleanup(root: number, branch: 'left' | 'right', callers: ('left' | 'right')[]) {
    const context = (line: CleanupLine): CleanupAnnotation => ({ root, line, branch, callers })
    if (root * 2 > lastVertex) {
      if (frames[cursor].state[root] === 'ghost') {
        action('p', root, context('correct'))
        action('u', root, context('uncompute'))
      }
      return
    }
    pebble(root * 2, context('prepare-left'))
    pebble(root * 2 + 1, context('prepare-right'))
    action('p', root, context('correct'))
    action('u', root, context('uncompute'))
    release(root * 2, context('release-left'))
    release(root * 2 + 1, context('release-right'))
    cleanup(root * 2, branch, [...callers, 'left'])
    cleanup(root * 2 + 1, branch, [...callers, 'right'])
  }

  cleanup(2, 'left', [])
  cleanup(3, 'right', [])
  if (cursor !== trace.rounds.length) throw new Error('KSS cleanup annotation ended before the native trace')
  return { rootEnd, annotations }
}
