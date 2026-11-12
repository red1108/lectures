<script setup lang="ts">
import {computed} from 'vue'
import native from '../traces/native.json'
const props=withDefaults(defineProps<{clicks?:number}>(),{clicks:0})
const lines=[
  {text:'Pebble(T)'},
  {text:'  v ← root(T)'},
  {text:'  if v is not a leaf'},
  {text:'    Pebble(left subtree of T)'},
  {text:'    Pebble(right subtree of T)'},
  {text:'  Pebble(v)', action:'p'},
  {text:'  for each child u of v'},
  {text:'    if u is a leaf'},
  {text:'      Unpebble(u)', action:'u'},
  {text:'    else'},
  {text:'      Ghost(u)', action:'g'},
]
const rootEnd=native.kss4.rounds.findIndex(round=>round.p.includes(1))+3
const current=computed(()=>props.clicks>0 ? native.kss4.rounds[Math.min(props.clicks,rootEnd)-1] : null)
const action=computed(()=>current.value?.p.length ? 'p' : current.value?.u.length ? 'u' : current.value?.g.length ? 'g' : '')
</script>
<template>
  <div class="step-code-with-note">
  <div class="step-code">
    <div class="step-code-title">Algorithm 1 · Root computation</div>
    <pre><template v-for="(line,i) in lines" :key="i"><span :class="{selected:line.action === action}">{{ line.text }}</span>{{ i < lines.length - 1 ? '\n' : '' }}</template></pre>
  </div>
  <p class="step-code-note">Called <code>SequentialPebble(T)</code> in the paper.</p>
  </div>
</template>
<style scoped>
.step-code{background:#203433;border-radius:9px;overflow:hidden;color:#e9f1e8;font:14px/1.6 ui-monospace,monospace}
.step-code-title{padding:9px 12px;background:#34504a;color:#bbd1c4;font-size:12px}
pre{margin:0;padding:9px 12px;white-space:pre;font:inherit}pre span{display:inline}.selected{background:#b4823f;color:#fff}
.step-code-note{margin:8px 0 0;padding:0;color:#7a827f;font-family:ui-sans-serif,sans-serif;font-size:11px;line-height:1.4}
.step-code-note code{background:none;padding:0;color:inherit;font:inherit;font-family:ui-monospace,monospace}
</style>
