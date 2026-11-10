<script setup lang="ts">
import {ref} from 'vue'
import native from '../traces/native.json'
import {replay, type Trace} from '../lib/pebbling'
const code = ref(`// Run the captured KSS schedule through the same replay engine.\nconst frames = replay(trace)\nconst last = frames.at(-1)\nprint('rounds = ' + last.step)\nprint('work   = ' + last.work)\nprint('peak   = ' + last.peak)\nprint('root only = ' + (last.state[1] === 'pebble' &&\n  last.state.slice(2).every(x => x === 'empty')))`)
const output = ref('Press Run to execute this code in your browser.')
function run() {
  const lines:string[] = []
  try {
    const fn = new Function('replay', 'trace', 'print', code.value)
    fn(replay, (native as any).kss as Trace, (...xs:any[]) => lines.push(xs.join(' ')))
    output.value = lines.join('\n') || '(no output)'
  } catch(e) { output.value = String(e) }
}
</script>
<template>
  <div class="code-demo" @keydown.stop>
    <div class="code-head"><span>JavaScript · local browser runtime</span><button type="button" @click.stop="run">▶ Run</button></div>
    <textarea v-model="code" spellcheck="false" aria-label="Editable code"></textarea>
    <div class="out-label">OUTPUT</div><pre class="output">{{ output }}</pre>
  </div>
</template>
<style scoped>
.code-demo{font-family:ui-monospace,monospace;background:#203433;color:#e8f4e9;border-radius:10px;overflow:hidden;}
.code-head{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;color:#c4d4c7;font-size:12px;background:#2e4844}
button{background:#e7b767;color:#203433;border:0;border-radius:5px;padding:5px 12px;font-size:12px;cursor:pointer;font-weight:bold}
textarea{display:block;width:100%;height:215px;resize:none;padding:13px 15px;background:#203433;color:#e8f4e9;border:0;outline:0;font:13px/1.48 ui-monospace,monospace;white-space:pre;}
.out-label{padding:7px 15px 0;color:#aec8b8;font-size:10px;letter-spacing:.14em}
.output{margin:0;padding:5px 15px 14px;color:#ffdfaa;min-height:70px;font:12px/1.4 ui-monospace,monospace;white-space:pre-wrap}
</style>
