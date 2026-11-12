<script setup lang="ts">
import { computed, ref } from 'vue'
import { replay, type Round } from '../lib/pebbling'

const rounds = ref<Round[]>([])
const frame = computed(() => replay({
  kind: 'interactive-line',
  graph: 'path',
  length: 3,
  initial: [],
  rounds: rounds.value,
  source: 'Interactive line',
}).at(-1)!)
const labels = ['Start', 'Node 2', 'Node 3', 'Final']

function canToggle(vertex: number) {
  return vertex === 0 || frame.value.state[vertex - 1] === 'pebble'
}

function toggle(vertex: number) {
  if (!canToggle(vertex)) return
  const removing = frame.value.state[vertex] === 'pebble'
  rounds.value.push({
    p: removing ? [] : [vertex],
    u: removing ? [vertex] : [],
    g: [],
  })
}
</script>

<template>
  <div class="pebble-rule" @click.stop @click.capture="($event.target as HTMLElement).closest<HTMLElement>('button')?.blur()">
    <p class="meaning">Pebble = quantum register, Arrow = computation dependency</p>
    <p class="goal"><span aria-hidden="true">🎯</span> GOAL: Compute the final value and clear all other pebbles.</p>
    <div class="chain">
      <svg viewBox="0 0 760 160" aria-hidden="true">
        <defs>
          <marker id="rule-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#9fb1ae" />
          </marker>
        </defs>
        <line v-for="edge in 3" :key="edge"
          :x1="(edge - 1) * 190 + 149" y1="56"
          :x2="edge * 190 + 35" y2="56"
          stroke="#9fb1ae" stroke-width="3" marker-end="url(#rule-arrow)" />
      </svg>
      <div v-for="(label, vertex) in labels" :key="vertex" class="vertex">
        <button type="button" class="stone"
          :class="{ filled: frame.state[vertex] === 'pebble' }"
          :aria-label="label" :aria-pressed="frame.state[vertex] === 'pebble'"
          :disabled="!canToggle(vertex)"
          @click.stop="toggle(vertex)" @keydown.enter.stop @keydown.space.stop />
        <span v-if="vertex === 0 || vertex === 3" class="vertex-label">{{ label.toLowerCase() }}</span>
      </div>
    </div>
    <div class="metrics" aria-live="polite">
      <span>work <b data-test="manual-work">{{ frame.work }}</b></span>
      <span>peak <b data-test="manual-peak">{{ frame.peak }}</b></span>
      <button type="button" class="reset" @click.stop="rounds = []">Reset</button>
    </div>
  </div>
</template>

<style scoped>
.pebble-rule {
  max-width: 760px;
  margin: 45px auto 0;
  text-align: center;
  font-family: var(--slidev-font-sans);
}
.meaning {
  font-size: 22px;
  color: #4d6c65;
  margin: 0;
}
.goal {
  margin: 15px 0 0;
  font-size: 20px;
  color: #4d6c65;
}
.chain {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  height: 180px;
  margin: 40px 0 35px;
}
.chain svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 160px;
  pointer-events: none;
}
.vertex {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stone {
  width: 108px;
  height: 108px;
  margin-top: 2px;
  border: 3px solid #a7b8b0;
  border-radius: 50%;
  background: #faf9f2;
  cursor: pointer;
  transition: background .2s, border-color .2s;
}
.stone.filled {
  background: #3d7770;
  border-color: #315f59;
}
.stone:disabled {
  cursor: default;
}
.stone:enabled:hover {
  outline: 3px solid #e5bb78;
  outline-offset: 5px;
}
.stone:focus-visible {
  outline: 3px solid #d8993b;
  outline-offset: 5px;
}
.vertex-label {
  margin-top: 22px;
  font-size: 21px;
  color: #617d75;
}
.metrics {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 45px;
  font-size: 22px;
  color: #617d75;
}
.metrics b {
  margin-left: 9px;
  color: #284b48;
  font-size: 30px;
  font-variant-numeric: tabular-nums;
}
.reset {
  padding: 5px 16px;
  border: 1px solid #bdcabe;
  border-radius: 5px;
  background: #fffdf7;
  color: #55766a;
  font-size: 16px;
  cursor: pointer;
}
</style>
