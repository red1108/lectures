<script setup lang="ts">
import { computed, ref } from 'vue'

const stage = ref(0)
const captions = ['Choose a block', 'Hold the boundary values', 'Recompute the block', 'Clear the block with the same boundary']
const block = [2, 4, 5]
const boundary = [8, 9, 10, 11]
const nodes = Array.from({ length: 15 }, (_, offset) => {
  const id = offset + 1
  const level = Math.floor(Math.log2(id))
  return { id, x: (id - 2 ** level + .5) * 760 / 2 ** level, y: 35 + level * 80 }
})
const edges = nodes.slice(1).map(node => ({ child: node, parent: nodes[Math.floor(node.id / 2) - 1] }))
const caption = computed(() => captions[stage.value])

function state(id: number) {
  if (id === 1 || (boundary.includes(id) && stage.value >= 1)) return 'pebble'
  if (block.includes(id)) return ['ghost', 'ghost', 'pebble', 'empty'][stage.value]
  return id < 8 ? 'ghost' : 'empty'
}

function releaseFocus(event: MouseEvent) {
  (event.target as HTMLElement).closest<HTMLElement>('button')?.blur()
}
</script>

<template>
  <div class="block-idea" @click.stop @click.capture="releaseFocus">
    <div class="idea-caption">{{ caption }}</div>
    <svg viewBox="0 0 760 350" role="img" :aria-label="caption">
      <defs>
        <marker id="block-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#9aada5" />
        </marker>
      </defs>
      <rect class="selected-block" x="51" y="77" width="278" height="157" rx="24" />
      <text class="region-label" x="72" y="99">block</text>
      <rect v-if="stage >= 1" class="boundary-band" x="18" y="246" width="344" height="58" rx="26" />
      <g class="edges">
        <line v-for="edge in edges" :key="edge.child.id"
          :x1="edge.child.x" :y1="edge.child.y - 22"
          :x2="edge.parent.x + (edge.child.x < edge.parent.x ? -18 : 18)" :y2="edge.parent.y + 20"
          marker-end="url(#block-arrow)" />
      </g>
      <g v-for="node in nodes" :key="node.id" :transform="`translate(${node.x},${node.y})`"
        class="vertex" :class="[state(node.id), { muted: node.id !== 1 && !block.includes(node.id) && !boundary.includes(node.id) }]">
        <circle r="22" />
        <text v-if="state(node.id) === 'ghost'" text-anchor="middle" dominant-baseline="central">G</text>
      </g>
      <text class="output-label" x="418" y="41">output</text>
      <text v-if="stage >= 1" class="boundary-label" x="190" y="332" text-anchor="middle">retained boundary</text>
    </svg>
    <div class="idea-controls">
      <button type="button" aria-label="Reset block idea" @click="stage = 0">Reset</button>
      <button type="button" aria-label="Previous idea step" :disabled="stage === 0" @click="stage--">←</button>
      <span>{{ stage + 1 }} / 4</span>
      <button type="button" aria-label="Next idea step" :disabled="stage === 3" @click="stage++">→</button>
    </div>
  </div>
</template>

<style scoped>
.block-idea { margin: 5px auto 0; max-width: 760px; font-family: var(--slidev-font-sans); }
.idea-caption { text-align: center; font-size: 25px; color: #3e655e; margin-bottom: 12px; }
svg { display: block; width: 100%; height: 350px; }
.edges line { stroke: #9aada5; stroke-width: 2; }
.selected-block { fill: #fcf0dc; stroke: #d6a55e; stroke-width: 2; stroke-dasharray: 7 5; }
.boundary-band { fill: #e1eee2; }
.region-label { fill: #b08146; font-size: 15px; }
.vertex circle { fill: #faf9f2; stroke: #9fb1ae; stroke-width: 2; transition: fill .35s, stroke .35s; }
.vertex.pebble circle { fill: #3d7770; stroke: #315f59; }
.vertex.ghost circle { fill: #f4e6d7; stroke: #bd805b; stroke-dasharray: 4 3; }
.vertex text { font-size: 18px; fill: #a45f3e; }
.vertex.muted { opacity: .45; }
.output-label { fill: #617d75; font-size: 16px; }
.boundary-label { fill: #3d7770; font-size: 18px; }
.idea-controls { display: flex; justify-content: center; align-items: center; gap: 15px; color: #70847f; font-size: 14px; }
.idea-controls button { padding: 4px 13px; border: 1px solid #c6d2c8; border-radius: 5px; background: #fffdf7; color: #344e4d; font-size: 14px; cursor: pointer; }
.idea-controls button:disabled { opacity: .35; cursor: default; }
</style>
