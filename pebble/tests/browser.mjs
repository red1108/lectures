import {chromium} from '@playwright/test'
import {mkdir} from 'node:fs/promises'
import {readFileSync} from 'node:fs'
const baseURL = (process.env.SLIDEV_URL || 'http://localhost:3039').replace(/\/$/, '')
const launchOptions = {headless: true}
if (process.env.CHROME_PATH) launchOptions.executablePath = process.env.CHROME_PATH
const browser = await chromium.launch(launchOptions)
const page = await browser.newPage({viewport:{width:1280,height:720}, deviceScaleFactor:1})
const errors=[]
page.on('pageerror', e=>errors.push(e.message))
await mkdir('.generated/screens', {recursive:true})
for(let n=1;n<=25;n++) {
  await page.goto(`${baseURL}/${n}`,{waitUntil:'networkidle'})
  await page.waitForTimeout(250)
  const info = await page.locator('.slidev-page:visible').first().evaluate(el=>({text:el.innerText.slice(0,65), overflow:el.scrollHeight>el.clientHeight+2 || el.scrollWidth>el.clientWidth+2})).catch(()=>({text:'',overflow:true}))
  if(!info.text) throw new Error(`Slide ${n} missing text`)
  await page.screenshot({path:`.generated/screens/${String(n).padStart(2,'0')}.png`})
  console.log(`slide ${n}: ${info.text.replace(/\s+/g,' ').slice(0,45)} | page overflow=${info.overflow}`)
}
await page.goto(`${baseURL}/7`,{waitUntil:'networkidle'})
const simpleLine=page.locator('.trace-player:visible').first()
for (let step=0; step<15; step++) await simpleLine.getByRole('button',{name:'Next step'}).click()
if (await simpleLine.locator('.vertex.pebble').count() !== 1) throw new Error('Line goal must retain only the endpoint')
if ((await simpleLine.locator('.vertex.pebble .node-label').textContent())?.trim() !== '7') throw new Error('Wrong line endpoint')
await page.goto(`${baseURL}/12`,{waitUntil:'networkidle'})
const spookyLine=page.locator('.trace-player:visible').first()
for (let step=0; step<15; step++) await spookyLine.getByRole('button',{name:'Next step'}).click()
if (await spookyLine.locator('.vertex.ghost').count() !== 7) throw new Error('Expected ghosts behind the line sweep')
for (let step=15; step<71; step++) await spookyLine.getByRole('button',{name:'Next step'}).click()
if (await page.locator('.trace-player:visible .vertex.ghost').count() !== 0) throw new Error('Line cleanup left ghosts')
await page.goto(`${baseURL}/15`,{waitUntil:'networkidle'})
const player=page.locator('.trace-player:visible').first()
await player.getByRole('button',{name:'Next step'}).click()
if (!(await player.locator('.trace-step').innerText()).includes('1 / 81')) throw new Error('Next step did not advance')
await player.getByRole('button',{name:'Previous step'}).click()
if (!(await player.locator('.trace-step').innerText()).includes('0 / 81')) throw new Error('Previous step did not reverse')
await page.keyboard.press('ArrowRight');await page.waitForTimeout(150)
if (!page.url().endsWith('/16')) throw new Error('Right arrow did not leave the trace slide')
await page.goto(`${baseURL}/14`,{waitUntil:'networkidle'})
const rootPlayer=page.locator('.trace-player:visible').first()
const rootRounds=JSON.parse(readFileSync(new URL('../traces/native.json',import.meta.url),'utf8')).kss.rounds.slice(0,13)
if (await page.locator('.step-code:visible .selected').count()) throw new Error('Initial pseudocode must have no highlighted action')
for (const [index,round] of rootRounds.entries()) {
  await rootPlayer.getByRole('button',{name:'Next step'}).click()
  if (!(await rootPlayer.locator('.trace-step').innerText()).includes(`${index+1} / 13`)) throw new Error('Root trace step failed')
  const expected=round.p.length ? 'Pebble(v)' : round.u.length ? 'Unpebble(u)' : 'Ghost(u)'
  const selected=page.locator('.step-code:visible .selected')
  if (await selected.count() !== 1 || (await selected.innerText()).trim() !== expected) throw new Error(`Pseudocode highlighting is out of sync at step ${index+1}`)
}
await rootPlayer.getByRole('button',{name:'Previous step'}).click()
await rootPlayer.getByRole('button',{name:'Previous step'}).click()
if ((await page.locator('.step-code:visible .selected').innerText()).trim() !== 'Pebble(v)') throw new Error('Pseudocode highlighting failed when stepping backward')
if(errors.length)throw new Error('Browser errors: '+errors.join('; '))
console.log('PASS: steps, slide navigation, code highlighting, no runtime errors')
await browser.close()
