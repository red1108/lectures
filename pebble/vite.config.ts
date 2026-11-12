import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

export default defineConfig({
  plugins: process.env.PEBBLE_SINGLE_FILE === '1' ? [
    viteSingleFile(),
    {
      name: 'pebble-single-chunk',
      enforce: 'post',
      outputOptions(options) {
        return { ...options, manualChunks: undefined, inlineDynamicImports: true }
      },
    },
  ] : [],
})
