<script setup lang="ts">
import {computed} from 'vue'
import native from '../traces/native.json'
import source from '../snippets/sequential_pebble.cpp?raw'
const props=withDefaults(defineProps<{clicks?:number}>(),{clicks:0})
const lines=source.trimEnd().split('\n')
const current=computed(()=>props.clicks>0 ? native.kss.rounds[Math.min(props.clicks,13)-1] : null)
const mode=computed(()=>current.value?.p.length ? 'compute' : current.value ? 'release' : '')
function highlighted(line:string) {
  return mode.value==='compute' ? line.includes('qc.pebble(x)')
    : mode.value==='release' && (line.includes('release(qc, left)') || line.includes('release(qc, right)'))
}
</script>
<template>
  <div class="step-code">
    <div class="step-code-title">core/sequential_schedule.hpp</div>
    <pre><template v-for="(line,i) in lines" :key="i"><span :class="{selected:highlighted(line)}">{{ line }}</span>{{ i < lines.length - 1 ? '\n' : '' }}</template></pre>
  </div>
</template>
<style scoped>
.step-code{background:#203433;border-radius:9px;overflow:hidden;color:#e9f1e8;font:12px/1.42 ui-monospace,monospace}
.step-code-title{padding:9px 12px;background:#34504a;color:#bbd1c4}
pre{margin:0;padding:9px 12px;white-space:pre;font:inherit}pre span{display:inline}.selected{background:#b4823f;color:#fff}
</style>
