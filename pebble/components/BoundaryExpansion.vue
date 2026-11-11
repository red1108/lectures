<script setup lang="ts">
import {computed, onBeforeUnmount, ref, watch} from 'vue'
import {onSlideLeave} from '@slidev/client'
import {boundaryExpansion} from '../lib/boundary-expansion'

const props = withDefaults(defineProps<{height?: number, size?: number}>(), {height: 4, size: 6})
const frames = computed(() => boundaryExpansion(props.height, props.size))
const step = ref(0)
const playing = ref(false)
const speed = ref(1)
let timer: ReturnType<typeof setInterval> | undefined
const frame = computed(() => frames.value[step.value])
const total = computed(() => frames.value.length - 1)
const lines = [
  'Boundary(T, m)',
  '  v ← root(T)',
  '  if m = 1: return {v}',
  '  B_L ← Boundary(T_L, ⌈m/2⌉)',
  '  B_R ← Boundary(T_R, ⌊m/2⌋)',
  '  return B_L ∪ B_R',
]
const nodes = computed(() => Array.from({length: 2 ** props.height - 1}, (_, i) => {
  const id = i + 1, level = Math.floor(Math.log2(id))
  return {id, x: 16 + (id - 2 ** level + .5) * 608 / 2 ** level, y: 30 + level * 92}
}))
const edges = computed(() => nodes.value.slice(1).map(child => ({child, parent: nodes.value[Math.floor(child.id / 2) - 1]})))
const boundaryPath = computed(() => frame.value.boundary.map(id => {
  const node = nodes.value[id - 1]
  return `${node.x},${node.y}`
}).join(' '))
function stop() {
  playing.value = false
  if (timer) clearInterval(timer)
  timer = undefined
}
function setStep(value: number) { step.value = Math.max(0, Math.min(total.value, value)) }
function jump(delta: number) { stop(); setStep(step.value + delta) }
function startTimer() {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    setStep(step.value + 1)
    if (step.value === total.value) stop()
  }, 850 / speed.value)
}
function toggle() {
  if (playing.value) return stop()
  if (step.value === total.value) setStep(0)
  playing.value = true
  startTimer()
}
function releaseFocus(event: MouseEvent) {
  (event.target as HTMLElement).closest<HTMLElement>('button, input')?.blur()
}
watch(speed, () => { if (playing.value) startTimer() })
watch(() => [props.height, props.size], () => { stop(); step.value = 0 })
onSlideLeave(stop)
onBeforeUnmount(stop)
</script>

<template>
  <div class="boundary-expansion">
    <div class="boundary-code">
      <div class="algorithm-title">Algorithm 2 · Boundary(T, m)</div>
      <pre><span v-for="(line, i) in lines" :key="i" class="code-line" :class="{selected: i === frame.line}" :data-line="i">{{ line }}</span></pre>
      <div class="current-call">Boundary(T<sub>{{ frame.node }}</sub>, {{ frame.target }})</div>
    </div>
    <div class="boundary-demo">
      <div class="boundary-metrics"><span>Height = {{ height }}</span><span>Boundary: <b>{{ frame.boundary.length }}</b> / {{ size }}</span></div>
      <svg :viewBox="`0 0 640 ${74 + (height - 1) * 92}`" role="img" :aria-label="`Boundary expansion: ${frame.boundary.length} boundary vertices out of ${size}`">
        <g class="edges">
          <line v-for="edge in edges" :key="edge.child.id"
            :x1="edge.parent.x" :y1="edge.parent.y" :x2="edge.child.x" :y2="edge.child.y"
            :class="{expanded: frame.expanded.includes(edge.parent.id), added: frame.added.includes(edge.child.id)}" />
        </g>
        <polyline class="boundary-path" :points="boundaryPath" />
        <g v-for="node in nodes" :key="node.id" :data-node="node.id"
          :transform="`translate(${node.x},${node.y})`" class="boundary-vertex"
          :class="{frontier: frame.boundary.includes(node.id), expanded: frame.expanded.includes(node.id), active: node.id === frame.node}">
          <circle class="active-ring" r="28" />
          <circle class="node" r="21" />
          <text text-anchor="middle" dominant-baseline="central">{{ node.id }}</text>
        </g>
      </svg>
      <div class="boundary-legend"><span><i class="boundary-dot" /> boundary</span><span><i class="expanded-dot" /> expanded</span></div>
      <div class="boundary-caption">{{ frame.label }}</div>
      <div class="boundary-controls" @click.capture="releaseFocus">
        <button type="button" aria-label="Reset boundary expansion" :disabled="step === 0" @click.stop="jump(-step)">↤</button>
        <button type="button" aria-label="Previous boundary step" :disabled="step === 0" @click.stop="jump(-1)">←</button>
        <button type="button" :aria-label="playing ? 'Pause boundary expansion' : 'Play boundary expansion'" @click.stop="toggle">{{ playing ? 'Pause' : 'Play' }}</button>
        <button type="button" aria-label="Next boundary step" :disabled="step === total" @click.stop="jump(1)">→</button>
        <input type="range" min="0" :max="total" :value="step" aria-label="Boundary expansion step"
          @input="stop(); setStep(Number(($event.target as HTMLInputElement).value))"
          @click.stop="($event.target as HTMLInputElement).blur()" @pointerup="($event.target as HTMLInputElement).blur()" />
        <span class="step-count">{{ step }} / {{ total }}</span>
        <div class="boundary-speeds" role="group" aria-label="Boundary playback speed">
          <button v-for="rate in [1, 2, 4]" :key="rate" type="button" :aria-label="`Boundary playback speed ${rate}x`" :aria-pressed="speed === rate" @click.stop="speed = rate">×{{ rate }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.boundary-expansion{display:grid;grid-template-columns:41% 56%;gap:3%;align-items:start;margin-top:6px;color:#344e4d}
.boundary-code{overflow:hidden;background:#203433;border-radius:9px;color:#e9f1e8;font-family:var(--slidev-font-mono),monospace}
.algorithm-title{padding:11px 12px;background:#34504a;color:#bbd1c4;font-size:12px}
pre{margin:0;padding:18px 0;font:12.5px/2 ui-monospace,monospace;white-space:pre}
.code-line{display:block;padding:0 12px}
.code-line.selected{background:#b4823f;color:#fff}
.current-call{padding:14px 12px;border-top:1px solid #47605a;font-size:17px}
.current-call sub{font-size:12px}
.boundary-metrics{display:flex;justify-content:space-between;font-size:16px;color:#617d75;font-variant-numeric:tabular-nums}
.boundary-metrics b{color:#284b48}
svg{display:block;width:100%;height:280px;overflow:visible}
.edges line{stroke:#d8e0db;stroke-width:2}
.edges .expanded{stroke:#9fb1ae}
.edges .added{stroke:#c38b43;stroke-width:3}
.boundary-path{fill:none;stroke:#3d7770;stroke-width:3;stroke-dasharray:5 6;opacity:.65}
.node{fill:#faf9f2;stroke:#bdcac2;stroke-width:2}
.boundary-vertex text{fill:#8a9c94;font-size:18px}
.frontier .node{fill:#3d7770;stroke:#315f59}
.frontier text{fill:#fff;font-weight:600}
.expanded .node{fill:#e4e9e2;stroke:#9fb1ae}
.expanded text{fill:#617d75}
.active-ring{fill:none;stroke:transparent;stroke-width:3}
.active .active-ring{stroke:#c38b43}
.boundary-legend{display:flex;justify-content:center;gap:22px;font-size:12px;color:#617d75}
.boundary-legend span{display:flex;gap:6px;align-items:center}
.boundary-legend i{width:10px;height:10px;border-radius:50%;display:inline-block;border:1px solid #9fb1ae}
.boundary-dot{background:#3d7770}.expanded-dot{background:#e4e9e2}
.boundary-caption{height:32px;display:flex;justify-content:center;align-items:center;margin-top:10px;color:#284b48;font-size:17px;font-variant-numeric:tabular-nums}
.boundary-controls{display:flex;align-items:center;gap:5px;margin-top:8px}
.boundary-controls button{border:1px solid #c6d2c8;background:#fffdf7;border-radius:5px;padding:3px 7px;font:12px var(--slidev-font-sans);color:#344e4d;cursor:pointer;min-height:26px}
.boundary-controls button:hover:not(:disabled){background:#e6f1eb}
.boundary-controls button:disabled{opacity:.35;cursor:default}
.boundary-controls input{flex:1;min-width:25px;accent-color:#3d7770;cursor:pointer}
.step-count{font-size:11px;color:#617d75;white-space:nowrap;font-variant-numeric:tabular-nums}
.boundary-speeds{display:flex;gap:3px}
.boundary-speeds button{padding:3px 4px}
.boundary-speeds [aria-pressed="true"]{background:#3d7770;border-color:#3d7770;color:#fff}
</style>
