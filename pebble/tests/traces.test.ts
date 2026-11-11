import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {replay, reversible, spooky, type Trace} from '../lib/pebbling.ts'
import {lineExamples} from '../lib/line-examples.ts'
import './boundary.test.ts'
const native = JSON.parse(readFileSync(new URL('../traces/native.json', import.meta.url), 'utf8'))
for (const [name, t] of Object.entries({...native, reversible, spooky, ...lineExamples})) {
  if (['revision', 'source_sha256', 'source_changes'].includes(name)) continue
  const trace = t as Trace
  const frames = replay(trace), last = frames.at(-1)!
  const desired = trace.graph === 'tree' ? [1] : [...trace.initial, trace.length!].sort((a,b) => a-b)
  assert.deepEqual(last.state.flatMap((s,i) => s === 'pebble' ? [i] : []), desired, name)
  assert.equal(last.state.filter(s => s === 'ghost').length, 0, name)
  if (trace.metrics) {
    assert.equal(last.work, trace.metrics.work, `${name} work`)
    assert.equal(last.step, trace.metrics.depth, `${name} rounds`)
    assert.equal(last.peak, trace.metrics.peak, `${name} peak`)
  }
  if (name === 'kmrv') assert.equal(last.step, 2*trace.length!-1)
  if (name === 'line-simple') assert.equal(last.peak, 8)
  if (name === 'line-reversible') assert.equal(last.peak, 4)
  if (name === 'line-spooky') assert.equal(last.peak, 3)
  console.log(name, `steps=${last.step} work=${last.work} peak=${last.peak}`, 'OK')
}
assert.throws(() => replay({kind:'bad', graph:'tree', height:2, budget:3, initial:[], source:'test',
  rounds:[{p:[1],u:[],g:[]}]}), /Missing input/)
assert.throws(() => replay({kind:'bad', graph:'tree', height:2, budget:1, initial:[], source:'test',
  rounds:[{p:[2,3],u:[],g:[]}]}), /Space exceeded/)
assert.throws(() => replay({kind:'bad', graph:'tree', height:2, budget:3, initial:[], source:'test',
  rounds:[{p:[],u:[],g:[2]}]}), /Illegal ghost/)
console.log('Illegal actions and budget overflow are rejected')
