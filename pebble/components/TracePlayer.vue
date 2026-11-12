<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { onSlideLeave } from '@slidev/client'
import native from '../traces/native.json'
import { replay, reversible, spooky, type Trace } from '../lib/pebbling'
import { lineExamples } from '../lib/line-examples'

const props = withDefaults(defineProps<{ example: string, compact?: boolean, intro?: boolean, introMetrics?: boolean, foldedPath?: boolean }>(), { compact: false, intro: false, introMetrics: false })
const kssRoot = (native as any).kss4 as Trace
const rootRound = kssRoot.rounds.findIndex(r => r.p.includes(1)) + 1
const traces: Record<string, Trace> = {
  ...(native as any), reversible, spooky, ...lineExamples,
  'kss-root': {...kssRoot, kind: 'kss-root', rounds: kssRoot.rounds.slice(0, rootRound + 2),
    metrics: undefined, source: 'Native SequentialPebble · H=4 · root phase'},
  'kss-cleanup': { ...kssRoot, kind: 'kss-cleanup' },
}
const trace = computed(() => traces[props.example])
const frames = computed(() => replay(trace.value))
const startStep = computed(() => props.example === 'kss-cleanup' ? rootRound + 2 : 0)
const step = ref(startStep.value)
const playing = ref(false)
const speed = ref(1)
let timer: ReturnType<typeof setInterval> | undefined
watch(() => props.example, () => { stop(); step.value = startStep.value })
watch(speed, () => {
  if (playing.value) startTimer()
})
const frame = computed(() => frames.value[step.value])
const total = computed(() => frames.value.length - 1)
const nodes = computed(() => {
  if (trace.value.graph === 'path') {
    const n = trace.value.length! + 1
    if (props.foldedPath) {
      const topCount = Math.ceil(n / 2), bottomCount = n - topCount
      return Array.from({length:n}, (_,id) => {
        const upper = id < topCount
        const column = upper ? id : id - topCount
        const spacing = 610 / ((upper ? topCount : bottomCount) - 1)
        const x = upper ? 45 + column * spacing : 655 - column * spacing
        return {id, x, y: upper ? 65 : 195}
      })
    }
    return Array.from({length:n}, (_,i) => ({id:i, x:55+i*590/(n-1), y:148}))
  }
  const h = trace.value.height!, n = 2**h - 1
  return Array.from({length:n}, (_,i) => {
    const id=i+1, level=Math.floor(Math.log2(id)), offset=id-2**level
    return {id, x:30+(offset+.5)*640/2**level, y:38+level*(218/Math.max(1,h-1))}
  })
})
const edges = computed(() => trace.value.graph === 'path'
  ? nodes.value.slice(1).map((n,i) => ({a:nodes.value[i], b:n}))
  : nodes.value.slice(1).map(n => ({a:nodes.value[Math.floor(n.id/2)-1], b:n})))
const radius = computed(() => trace.value.height === 4 ? 17 : 20)
const label = computed(() => {
  if (props.example === 'kss-cleanup' && step.value === startStep.value) return 'Cleanup'
  if (step.value === 0) return trace.value.initial.includes(0) ? 'Fixed initial pebble on 0' : 'Empty configuration'
  const a = frame.value.actions
  const pieces = []
  if (a.p.length) pieces.push('PEBBLE ' + a.p.join(', '))
  if (a.u.length) pieces.push('UNPEBBLE ' + a.u.join(', '))
  if (a.g.length) pieces.push('GHOST ' + a.g.join(', '))
  return pieces.join('  ·  ')
})
function stop() { playing.value = false; if(timer) clearInterval(timer); timer=undefined }
function setStep(target:number) {
  step.value = Math.max(startStep.value, Math.min(total.value, target))
}
function jump(delta:number) { stop(); setStep(step.value + delta) }
function releaseFocus(event: MouseEvent) {
  (event.target as HTMLElement).closest<HTMLElement>('button, input')?.blur()
}
function startTimer() {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    setStep(step.value + 1)
    if (step.value === total.value) stop()
  }, 600 / speed.value)
}
function toggle() {
  if (playing.value) return stop()
  if (step.value === total.value) setStep(startStep.value)
  playing.value = true
  startTimer()
}
onSlideLeave(stop)
onBeforeUnmount(stop)
const badge = (id:number) => frame.value.state[id] === 'ghost' ? 'G' : String(id)
const activated = (id:number) => step.value > startStep.value && (frame.value.actions.p.includes(id) || frame.value.actions.u.includes(id) || frame.value.actions.g.includes(id))
function directedEdge(edge: {a: {x:number,y:number}, b: {x:number,y:number}}) {
  const start = trace.value.graph === 'path' ? edge.a : edge.b
  const end = trace.value.graph === 'path' ? edge.b : edge.a
  const distance = Math.hypot(end.x - start.x, end.y - start.y)
  const dx = (end.x - start.x) / distance
  const dy = (end.y - start.y) / distance
  return {x1: start.x + dx * radius.value, y1: start.y + dy * radius.value,
    x2: end.x - dx * (radius.value + 3), y2: end.y - dy * (radius.value + 3)}
}
</script>

<template>
  <div class="trace-layout" :class="{ 'with-code': !!$slots.code }">
  <div v-if="$slots.code"><slot name="code" :step="step" /></div>
  <div class="trace-player" :class="{compact, intro}">
    <div v-if="!intro" class="trace-top"><span class="trace-step">{{ step }} / {{ total }}</span></div>
    <svg class="graph" viewBox="0 0 700 280" role="img" :aria-label="trace.graph === 'tree' ? 'Binary-tree pebbling state' : 'Path pebbling state'">
      <defs><marker :id="`arrow-${example}`" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#82999a" /></marker></defs>
      <g class="edges"><line v-for="(e,i) in edges" :key="i" v-bind="directedEdge(e)" :marker-end="`url(#arrow-${example})`" /></g>
      <g v-for="node in nodes" :key="node.id" :transform="`translate(${node.x},${node.y})`" class="vertex" :class="[frame.state[node.id], { active: activated(node.id) }]">
        <circle class="active-ring" :r="radius+7" />
        <circle class="node" :r="radius" />
        <text class="node-label" text-anchor="middle" dominant-baseline="central">{{ badge(node.id) }}</text>
        <text v-if="frame.state[node.id] === 'ghost'" class="vertex-id" :y="radius+14" text-anchor="middle">{{ node.id }}</text>
      </g>
    </svg>
    <div class="actionline"><span class="action-name">{{ label }}</span><span v-if="frame.corrected.length" class="correction">phase corrected: {{ frame.corrected.join(', ') }}</span></div>
    <div v-if="!intro" class="trace-stats">
      <span><b>{{ frame.work }}</b> work</span><span><b>{{ frame.space }}</b> live</span><span><b>{{ frame.peak }}</b> peak</span><span v-if="trace.budget">budget {{ trace.budget }}</span>
      <span class="legend"><i class="dot empty"/> empty <i class="dot peb"/> pebble <i class="dot gh"/> ghost</span>
    </div>
    <div class="controls" data-test="controls" @click.capture="releaseFocus">
      <button type="button" @click.stop="jump(-step)" aria-label="Reset trace">↤</button>
      <button type="button" @click.stop="jump(-1)" aria-label="Previous step">←</button>
      <button type="button" @click.stop="toggle" :aria-label="playing ? 'Pause trace' : 'Play trace'">{{ playing ? 'Pause' : 'Play' }}</button>
      <button type="button" @click.stop="jump(1)" aria-label="Next step">→</button>
      <input type="range" :min="startStep" :max="total" :value="step" aria-label="Trace step" tabindex="-1" @input="stop();setStep(Number(($event.target as HTMLInputElement).value))" @click.stop="($event.target as HTMLInputElement).blur()" @pointerup="($event.target as HTMLInputElement).blur()" />
      <div class="speed-controls" role="group" aria-label="Playback speed">
        <button v-for="rate in [1, 2, 4]" :key="rate" type="button"
          :aria-label="`Playback speed ${rate}x`" :aria-pressed="speed === rate"
          @click.stop="speed = rate">×{{ rate }}</button>
      </div>
    </div>
    <div v-if="introMetrics" class="intro-metrics">
      <span>work <b>{{ frame.work }}</b></span>
      <span>peak space <b>{{ frame.peak }}</b></span>
    </div>
  </div>
  </div>
</template>

<style scoped>
.trace-player{width:100%; color:#243141; font-family:var(--slidev-font-sans);}
.with-code{display:grid;grid-template-columns:46% 51%;gap:3%;align-items:start}
.trace-top{display:flex;justify-content:flex-end;align-items:center;font-size:13px;color:#68747a;letter-spacing:.01em;}
.trace-step{font-variant-numeric:tabular-nums;font-weight:700;color:#334d57;}
.graph{display:block;width:100%;height:240px;overflow:visible}
.edges line{stroke:#82999a;stroke-width:2.2}
.node{fill:#faf9f2;stroke:#9fb1ae;stroke-width:2.3;transition:fill .2s,stroke .2s}
.pebble .node{fill:#3d7770;stroke:#315f59}
.ghost .node{fill:#f4e6d7;stroke:#bd805b;stroke-dasharray:5 4}
.active-ring{fill:none;stroke:transparent;stroke-width:3;transition:stroke .2s}
.active .active-ring{stroke:#eaa143}
.node-label{fill:#839694;font-size:17px;font-weight:700}
.pebble .node-label{fill:#fff}
.ghost .node-label{fill:#a45f3e}
.vertex-id{font-size:12px;fill:#a45f3e}
.actionline{height:25px;display:flex;align-items:center;gap:8px;font-size:13px;white-space:nowrap}
.action-name{color:#344e4d;font-weight:700;letter-spacing:.02em}
.correction{color:#b4653e;font-size:12px}
.trace-stats{display:flex;align-items:center;gap:16px;color:#697c79;font-size:12px;white-space:nowrap;}
.trace-stats b{font-size:17px;color:#243b3a;font-variant-numeric:tabular-nums}
.legend{margin-left:auto;display:flex;align-items:center;gap:4px;font-size:11px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:6px}.dot.empty{background:#faf9f2;border:1px solid #9fb1ae}.dot.peb{background:#3d7770}.dot.gh{background:#f4e6d7;border:1px dashed #bd805b}
.controls{display:flex;align-items:center;gap:7px;margin-top:8px}
.controls button{border:1px solid #c6d2c8;background:#fffdf7;border-radius:5px;padding:3px 10px;font-size:12px;color:#344e4d;cursor:pointer;min-height:26px}
.controls button:hover{background:#e6f1eb}.controls input{flex:1;min-width:0;accent-color:#3d7770;cursor:pointer}
.speed-controls{display:flex;gap:3px;margin-left:3px}
.speed-controls button{padding:3px 6px}
.speed-controls button[aria-pressed="true"]{background:#3d7770;border-color:#3d7770;color:white}
.compact .graph{height:180px}.compact .trace-top{font-size:11px}
.intro .graph{height:260px}
.intro .actionline{justify-content:center;font-size:16px;height:30px}
.intro .controls{max-width:650px;margin:12px auto 0}
.intro-metrics{display:flex;justify-content:center;gap:45px;margin-top:20px;font-size:20px;color:#617d75}
.intro-metrics b{margin-left:9px;font-size:28px;color:#284b48;font-variant-numeric:tabular-nums}
</style>
