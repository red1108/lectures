import assert from 'node:assert/strict'
import {boundaryExpansion} from '../lib/boundary-expansion.ts'

for (let height = 1; height <= 6; height++) {
  for (let size = 1; size <= 2 ** (height - 1); size++) {
    const frames = boundaryExpansion(height, size)
    assert.deepEqual(frames[0].boundary, [1])
    for (const frame of frames) {
      assert.equal(new Set(frame.boundary).size, frame.boundary.length)
      assert.ok(frame.boundary.length <= size)
      // A boundary must meet every root-to-leaf path exactly once,
      // including during the visual expansion.
      for (let leaf = 2 ** (height - 1); leaf < 2 ** height; leaf++) {
        let hits = 0
        for (let node = leaf; node >= 1; node = Math.floor(node / 2)) {
          if (frame.boundary.includes(node)) hits++
        }
        assert.equal(hits, 1, `H=${height}, m=${size}, leaf=${leaf}`)
      }
    }
    const final = frames.at(-1)!
    assert.equal(final.boundary.length, size)
    const depths = final.boundary.map(node => Math.floor(Math.log2(node)))
    assert.ok(Math.max(...depths) - Math.min(...depths) <= 1)
    assert.equal(final.expanded.length, size - 1)
  }
}
assert.deepEqual(boundaryExpansion(4, 6).at(-1)!.boundary, [8, 9, 5, 12, 13, 7])
assert.throws(() => boundaryExpansion(4, 9), RangeError)
assert.throws(() => boundaryExpansion(0, 1), RangeError)
assert.throws(() => boundaryExpansion(4, 1.5), RangeError)
console.log('Boundary expansion: all root-to-leaf cuts and balanced sizes H=1–6 OK')
