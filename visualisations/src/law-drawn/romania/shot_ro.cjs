// One look at the built page: each figure in light and dark, console errors, and phone-width overflow.
const { chromium } = require(process.argv[2]);
const fs = require("fs");
const src = fs.readFileSync(process.argv[3], "utf8");
// The publish step wraps the file in a document skeleton; mimic it for the local look
const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>${src}</body></html>`;
const out = process.argv[4];
(async () => {
  const b = await chromium.launch();
  for (const scheme of ["light", "dark"]) {
    const p = await b.newPage({ viewport: { width: 1100, height: 900 }, colorScheme: scheme });
    const errs = []; p.on("pageerror", e => errs.push(e.message)); p.on("console", m => m.type() === "error" && errs.push(m.text()));
    await p.setContent(html, { waitUntil: "networkidle" }); await p.waitForTimeout(700);
    for (const id of ["deadline", "spain", "vacatio", "calendar", "wait"]) await (await p.$("#" + id)).screenshot({ path: `${out}/ro2-${scheme}-${id}.png` });
    if (scheme === "light") await p.screenshot({ path: `${out}/ro-top.png`, clip: { x: 0, y: 0, width: 1100, height: 900 } });
    console.log(scheme, errs.length ? errs : "no errors");
  }
  const m = await b.newPage({ viewport: { width: 390, height: 800 } });
  await m.setContent(html, { waitUntil: "networkidle" });
  console.log("phone overflow:", await m.evaluate(() => document.documentElement.scrollWidth > innerWidth));
  await b.close();
})();
