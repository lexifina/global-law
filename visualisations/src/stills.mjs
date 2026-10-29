// Static renders of every chart in law-in-motion.html and legal-system-bridges.html, for the folder README.
//
//   node src/stills.mjs            (from visualisations/)
//
// Each visible <figure> with a drawing becomes stills/<page>-NN-<title>.png, and the README's gallery between the
// "stills" markers is rewritten to show them in page order. Uses Playwright from the Lexifina repo's saas-webpage.
import { createRequire } from 'node:module'
import { readFileSync, writeFileSync, mkdirSync, readdirSync, rmSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const viz = join(here, '..')
const require = createRequire(join(viz, '..', '..', '..', '..', 'saas-webpage', 'package.json'))
const { chromium } = require('playwright')

const PAGES = [
  ['law-in-motion.html', 'Law in Motion'],
  ['legal-system-bridges.html', 'Legal system bridges'],
]
const out = join(viz, 'stills')
rmSync(out, { recursive: true, force: true })
mkdirSync(out, { recursive: true })

const slug = (s) => s.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50)
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1.5, colorScheme: 'light' })
const sections = []
for (const [file, label] of PAGES) {
  await page.goto(pathToFileURL(join(viz, file)).href, { waitUntil: 'networkidle', timeout: 120000 })
  await page.waitForTimeout(3000)
  const figs = await page.$$('figure')
  const items = []
  let n = 0
  for (const fig of figs) {
    if (!(await fig.isVisible())) continue
    const info = await fig.evaluate((f) => {
      const h = f.querySelector('h2, h3, figcaption')
      const drawn = f.querySelector('svg *, canvas, img')
      return { title: (h?.textContent || '').trim().replace(/\s+/g, ' '), drawn: !!drawn }
    })
    if (!info.drawn) continue
    await fig.scrollIntoViewIfNeeded()
    await page.waitForTimeout(400)
    n += 1
    const name = `${file.replace('.html', '')}-${String(n).padStart(2, '0')}-${slug(info.title || 'chart')}.png`
    await fig.screenshot({ path: join(out, name) })
    items.push([info.title || `Chart ${n}`, name])
  }
  sections.push([label, file, items])
  console.log(`${file}: ${items.length} charts`)
}
await browser.close()

const readme = join(viz, 'README.md')
const BEGIN = '<!-- stills:begin -->'
const END = '<!-- stills:end -->'
const lines = [BEGIN, '', '## The charts', '',
  'Still images of every chart, rendered from the two pages by `src/stills.mjs`. Open the HTML pages for the interactive versions and the full text.', '']
for (const [label, file, items] of sections) {
  lines.push(`### ${label} (\`${file}\`)`, '')
  for (const [title, name] of items) lines.push(`![${title.replace(/[[\]]/g, '')}](stills/${name})`, '')
}
lines.push(END)
let text = readFileSync(readme, 'utf8')
const block = lines.join('\n')
if (text.includes(BEGIN)) text = text.slice(0, text.indexOf(BEGIN)) + block + text.slice(text.indexOf(END) + END.length)
else text = text.replace('\n## Rebuilding', '\n' + block + '\n\n## Rebuilding')
writeFileSync(readme, text)
console.log(`${readdirSync(out).length} stills; README gallery written`)
