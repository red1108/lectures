<script setup lang="ts">
import { computed, ref } from 'vue'

// Fixed height-5 tree. With cleanup budget b=8, Algorithm 6 first runs
// the two height-4 blocks one at a time, then height-2 subtrees in pairs.
const batches = [[2], [3], [8, 9], [10, 11], [12, 13], [14, 15], []]
const step = ref(0)
const colors = ['#3d7770', '#72a6e2']
const neutral = '#b9c8bf'
const boundaryColor = '#c9963f'
const nodes = Array.from({ length: 31 }, (_, index) => {
  const id = index + 1
  const level = Math.floor(Math.log2(id))
  return { id, level, x: (id - 2 ** level + .5) * 760 / 2 ** level, y: 28 + level * 70 }
})
const edges = nodes.slice(1).map(child => ({ child, parent: nodes[Math.floor(child.id / 2) - 1] }))
const regions = computed(() => batches[step.value].map((id, index) => {
  const root = nodes[id - 1]
  const members = nodes.filter(node => node.level >= root.level
    && Math.floor(node.id / 2 ** (node.level - root.level)) === id)
  const block = members.filter(node => node.level < root.level + 2)
  const boundary = members.filter(node => node.level === root.level + 2)
  const xs = block.map(node => node.x)
  const ys = block.map(node => node.y)
  return {
    id,
    members: block.map(node => node.id),
    boundary: boundary.map(node => node.id),
    color: colors[index],
    x: Math.min(...xs) - 12,
    y: Math.min(...ys) - 12,
    width: Math.max(...xs) - Math.min(...xs) + 24,
    height: Math.max(...ys) - Math.min(...ys) + 24,
  }
}))
const cleared = computed(() => {
  const result = new Set<number>()
  for (const batch of batches.slice(0, step.value)) {
    for (const root of batch) {
      result.add(root)
      result.add(root * 2)
      result.add(root * 2 + 1)
    }
  }
  return result
})
function hasGhost(id: number) {
  return id !== 1 && !cleared.value.has(id)
}
function nodeColor(id: number) {
  if (regions.value.some(region => region.boundary.includes(id))) return boundaryColor
  return regions.value.find(region => region.members.includes(id))?.color ?? neutral
}
function edgeColor(parent: number, child: number) {
  const block = regions.value.find(region => region.members.includes(parent))
  if (block?.boundary.includes(child)) return boundaryColor
  return block?.members.includes(child) ? block.color : neutral
}
function releaseFocus(event: MouseEvent) {
  (event.target as HTMLElement).closest<HTMLElement>('button')?.blur()
}
</script>

<template>
  <div class="parallel-forest-idea" @click.stop @click.capture="releaseFocus">
    <div class="forest-height">
      <span>Height 5</span>
      <span v-if="regions.length">{{ regions.length }} {{ regions.length === 1 ? 'block' : 'blocks' }} at a time</span>
    </div>
    <svg viewBox="0 0 760 370" role="img" aria-label="Fixed height-five binary tree with highlighted subtrees cleaned in parallel">
      <rect v-for="region in regions" :key="region.id" class="forest-region"
        :x="region.x" :y="region.y" :width="region.width" :height="region.height" rx="12"
        :fill="region.color" fill-opacity=".1" :stroke="region.color" stroke-opacity=".4" stroke-dasharray="5 4" />
      <line v-for="edge in edges" :key="edge.child.id"
        :x1="edge.parent.x" :y1="edge.parent.y" :x2="edge.child.x" :y2="edge.child.y"
        :stroke="edgeColor(edge.parent.id, edge.child.id)" stroke-width="2" />
      <g v-for="node in nodes" :key="node.id" class="forest-vertex" :data-node="node.id" :class="{ghost: hasGhost(node.id)}" :transform="`translate(${node.x},${node.y})`">
        <circle v-if="hasGhost(node.id) && nodeColor(node.id) === boundaryColor" r="14" fill="none" :stroke="boundaryColor" stroke-width="2" />
        <image v-if="hasGhost(node.id)" class="forest-ghost" href="/figures/measurement-ghost.svg" x="-11" y="-11" width="22" height="22" :aria-label="`Ghost ${node.id}`" />
        <circle v-else r="8" :fill="node.id === 1 ? '#3d7770' : 'white'" :stroke="node.id === 1 ? '#315f59' : nodeColor(node.id)" stroke-width="2" />
        <text :y="hasGhost(node.id) ? 22 : 0" text-anchor="middle" dominant-baseline="central" class="forest-node-label"
          :style="{fill: node.id === 1 ? 'white' : nodeColor(node.id) === neutral ? '#84958c' : nodeColor(node.id), fontWeight: nodeColor(node.id) === neutral && node.id !== 1 ? 400 : 700}">{{ node.id }}</text>
      </g>
      <text x="401" y="33" class="root-label">root</text>
      <g transform="translate(240,360)" class="forest-legend">
        <rect x="0" y="-9" width="10" height="10" fill="#3d7770" fill-opacity=".15" stroke="#3d7770" />
        <text x="16">cleanup block</text>
        <circle cx="170" cy="-4" r="5" fill="white" :stroke="boundaryColor" stroke-width="2" />
        <text x="184">boundary</text>
      </g>
    </svg>
    <div class="allocation-caption">
      <span v-if="regions.length">Clear </span>
      <template v-for="(region, index) in regions" :key="region.id"><span v-if="index"> and </span><span :style="{color: region.color}">{{ region.members.join(', ') }}</span></template>
    </div>
    <div class="forest-controls">
      <button type="button" aria-label="Reset forest stages" @click="step = 0">Reset</button>
      <button type="button" aria-label="Previous forest stage" :disabled="step === 0" @click="step--">←</button>
      <span>{{ step + 1 }} / {{ batches.length }}</span>
      <button type="button" aria-label="Next forest stage" :disabled="step === batches.length - 1" @click="step++">→</button>
    </div>
  </div>
</template>

<style scoped>
.parallel-forest-idea { max-width:760px; margin:12px auto 0; color:#3e655e; }
.forest-height { display:flex; justify-content:space-between; padding:0 20px; font-size:18px; color:#617d75; }
svg { display:block; width:100%; height:320px; margin-top:4px; }
.forest-node-label { font-size:10px; pointer-events:none; }
.forest-legend { font-size:12px; fill:#617d75; }
.root-label { font-size:16px; fill:#617d75; }
.allocation-caption { min-height:26px; text-align:center; font-size:20px; margin:8px 0 8px; }
.forest-controls { display:flex; align-items:center; justify-content:center; gap:15px; font-size:14px; color:#70847f; }
.forest-controls button { padding:4px 13px; border:1px solid #c6d2c8; border-radius:5px; background:#fffdf7; color:#344e4d; font-size:14px; cursor:pointer; }
.forest-controls button:disabled { opacity:.35; cursor:default; }
</style>
