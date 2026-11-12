import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

export default defineConfig({
  plugins: process.env.PEBBLE_SINGLE_FILE === '1' ? [
    viteSingleFile(),
    {
      name: 'pebble-single-chunk',
      enforce: 'post',
      transform(code, id) {
        if (id.replaceAll('\\', '/').endsWith('/usePreloadImages.ts')) {
          // Slidev's preloader otherwise treats embedded data URIs as file paths.
          return code.replace(/url\.startsWith\((['"])http\1\)/g,
            "url.startsWith('data:') || $&")
        }
      },
      outputOptions(options) {
        return { ...options, manualChunks: undefined, inlineDynamicImports: true }
      },
    },
  ] : [],
})
