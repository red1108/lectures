import { readFile, writeFile, readdir, mkdir } from 'node:fs/promises'
import { resolve, extname, relative, dirname } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const output = resolve(process.argv[2] || resolve(root, '.generated/pebble-talk.html'))
let html = await readFile(resolve(root, '.generated/standalone/index.html'), 'utf8')
const mime = { '.png': 'image/png', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.ico': 'image/x-icon' }
const dataUri = (bytes, type) => `data:${type};base64,${Buffer.from(bytes).toString('base64')}`

// Public assets are referenced from Vue templates and are not bundled by Vite.
async function embedPublic(folder) {
  for (const entry of await readdir(folder, { withFileTypes: true })) {
    const path = resolve(folder, entry.name)
    if (entry.isDirectory()) await embedPublic(path)
    else {
      const name = relative(resolve(root, 'public'), path).replaceAll('\\', '/')
      const uri = dataUri(await readFile(path), mime[extname(path)] || 'application/octet-stream')
      for (const prefix of ['/', './', '']) {
        for (const quote of ['"', "'", '`'])
          html = html.replaceAll(`${quote}${prefix}${name}${quote}`, `${quote}${uri}${quote}`)
      }
    }
  }
}
await embedPublic(resolve(root, 'public'))
html = html.replaceAll('https://cdn.jsdelivr.net/gh/slidevjs/slidev/assets/favicon.png',
  dataUri(await readFile(resolve(root, 'public/figures/cover-spooky.svg')), 'image/svg+xml'))

// Embed the exact web fonts too, so opening the file does not require a network.
for (const match of [...html.matchAll(/<link\b[^>]*href="(https:\/\/fonts\.googleapis\.com\/[^" ]+)"[^>]*>/g)]) {
  const response = await fetch(match[1].replaceAll('&amp;', '&'), {
    headers: { 'User-Agent': 'Mozilla/5.0 Chrome/130.0.0.0 Safari/537.36' },
  })
  if (!response.ok) throw new Error(`Font CSS: ${response.status}`)
  let css = await response.text()
  for (const url of new Set([...css.matchAll(/url\((https:\/\/[^)]+)\)/g)].map(m => m[1]))) {
    const font = await fetch(url)
    if (!font.ok) throw new Error(`Font: ${font.status}`)
    css = css.replaceAll(url, dataUri(await font.arrayBuffer(), font.headers.get('content-type') || 'font/woff2'))
  }
  html = html.replace(match[0], `<style>${css}</style>`)
}
await mkdir(dirname(output), { recursive: true })
await writeFile(output, html)
console.log(`Standalone HTML: ${output} (${(Buffer.byteLength(html) / 1024 / 1024).toFixed(1)} MB)`)
