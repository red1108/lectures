<script setup lang="ts">
import { computed } from 'vue'
import native from '../traces/native.json'
import { describeKssCleanup } from '../lib/kss-cleanup'
import type { Trace } from '../lib/pebbling'

const props = defineProps<{ step: number }>()
const { rootEnd, annotations } = describeKssCleanup(native.kss4 as Trace)
const current = computed(() => annotations[props.step])
const lines = [
  { text: 'KSS(T)' },
  { text: '  Pebble(T)', id: 'root' },
  { text: '  Cleanup(left subtree of T)', id: 'kss-left' },
  { text: '  Cleanup(right subtree of T)', id: 'kss-right' },
  { text: '' },
  { text: 'Cleanup(T)' },
  { text: '  v ← root(T)' },
  { text: '  if v is a leaf: return' },
  { text: '  Pebble(left subtree of T)', id: 'prepare-left' },
  { text: '  Pebble(right subtree of T)', id: 'prepare-right' },
  { text: '  Correct(v)', id: 'correct' },
  { text: '  Unpebble(v)', id: 'uncompute' },
  { text: '  Release(left child)', id: 'release-left' },
  { text: '  Release(right child)', id: 'release-right' },
  { text: '  Cleanup(left subtree of T)', id: 'recurse-left' },
  { text: '  Cleanup(right subtree of T)', id: 'recurse-right' },
]
function caller(id?: string) {
  return id === `kss-${current.value?.branch}`
    || (id === 'recurse-left' && current.value?.callers.includes('left'))
    || (id === 'recurse-right' && current.value?.callers.includes('right'))
}
</script>

<template>
  <div class="cleanup-code">
      <div class="cleanup-code-title">Full KSS algorithm</div>
      <pre><template v-for="(line, index) in lines" :key="index"><span :class="{ selected: !!current && line.id === current.line, caller: caller(line.id), completed: line.id === 'root' && step >= rootEnd }">{{ line.text }}</span>{{ index < lines.length - 1 ? '\n' : '' }}</template></pre>
  </div>
</template>

<style scoped>
.cleanup-code{background:#203433;border-radius:9px;overflow:hidden;color:#e9f1e8;font:12px/1.55 ui-monospace,monospace}
.cleanup-code-title{padding:8px 12px;background:#34504a;color:#bbd1c4;font-size:12px}
pre{margin:0;padding:9px 12px;white-space:pre;font:inherit}
pre span{display:inline}
.selected{background:#b4823f;color:white}
.caller{background:#34504a;color:#d5e6d9}
.completed{color:#9ebbb0}
</style>
