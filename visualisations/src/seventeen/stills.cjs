// Stills of seventeen-countries-one-at-a-time.html for the visualisations README, and a check of the page.
//
//   node src/seventeen/stills.cjs                      (from visualisations/) writes stills/seventeen-countries-one-at-a-time-NN-<title>.png
//   node src/seventeen/stills.cjs check <dir> <light|dark> <width>   screenshots every chart into <dir> and reports errors
//
// Needs Playwright: PLAYWRIGHT=<path to the playwright package> if it is not installed where node can find it.
// Like src/stills.mjs: 1100 px wide, scale 1.5, light, one PNG per chart, named by its title.
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const viz = path.join(__dirname, '..', '..');
const FILE = 'seventeen-countries-one-at-a-time.html';
const slug = s => s.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50);
const [mode, outDir, scheme, width] = process.argv.slice(2);
(async () => {
  const check = mode === 'check';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: check ? +(width || 1100) : 1100, height: 900 }, deviceScaleFactor: check ? 1 : 1.5, colorScheme: check ? (scheme || 'light') : 'light' });
  const errs = [];
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(`${m.type()}: ${m.text()}`); });
  p.on('pageerror', e => errs.push('pageerror: ' + e.message));
  await p.goto('file:///' + path.join(viz, FILE).split(path.sep).join('/'), { waitUntil: 'networkidle', timeout: 120000 });
  await p.waitForTimeout(3000);
  const figs = await p.$$('figure.chart');
  if (check) {
    fs.mkdirSync(outDir, { recursive: true });
    console.log('figures', figs.length, 'hscroll', await p.evaluate(() => document.documentElement.scrollWidth > innerWidth));
    console.log('error notes', await p.$$eval('p.note', ns => ns.filter(n => n.textContent.startsWith('Error')).map(n => n.closest('figure').id + ': ' + n.textContent)));
    await p.screenshot({ path: path.join(outDir, `top-${scheme}-${width}.png`) });
    for (let i = 0; i < figs.length; i++) await figs[i].screenshot({ path: path.join(outDir, `${scheme}-${width}-${String(i + 1).padStart(2, '0')}.png`) });
  } else {
    const out = path.join(viz, 'stills');
    fs.mkdirSync(out, { recursive: true });
    for (const f of fs.readdirSync(out)) if (f.startsWith(FILE.replace('.html', '') + '-')) fs.unlinkSync(path.join(out, f));
    // the same figures, titles, numbers and names as src/stills.mjs, which lists this page too
    let n = 0;
    for (const fig of await p.$$('figure')) {
      if (!(await fig.isVisible())) continue;
      const info = await fig.evaluate((f) => {
        const h = f.querySelector('h2, h3, figcaption');
        const drawn = f.querySelector('svg *, canvas, img');
        return { title: (h?.textContent || '').trim().replace(/\s+/g, ' '), drawn: !!drawn };
      });
      if (!info.drawn) continue;
      await fig.scrollIntoViewIfNeeded();
      await p.waitForTimeout(400);
      n += 1;
      const name = `${FILE.replace('.html', '')}-${String(n).padStart(2, '0')}-${slug(info.title || 'chart')}.png`;
      await fig.screenshot({ path: path.join(out, name) });
      console.log(`![${(info.title || `Chart ${n}`).replace(/[[\]]/g, '')}](stills/${name})`);
    }
    if (n !== figs.length) console.log(`WARNING: ${n} stills for ${figs.length} charts`);
  }
  if (errs.length) console.log('ERRORS\n' + errs.join('\n'));
  await b.close();
})();
