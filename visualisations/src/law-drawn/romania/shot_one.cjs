// Render chosen figures of the built page in light and dark, and report script errors and phone overflow.
// usage: node shot_one.cjs <playwright> <page.html> <outdir> id [id ...]
const { chromium } = require(process.argv[2]);
const fs = require("fs");
const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>${fs.readFileSync(process.argv[3], "utf8")}</body></html>`;
const out = process.argv[4], ids = process.argv.slice(5);
(async () => {
  const b = await chromium.launch();
  for (const scheme of ["light", "dark"]) {
    const p = await b.newPage({ viewport: { width: 1100, height: 900 }, colorScheme: scheme });
    const errs = []; p.on("pageerror", e => errs.push(e.message)); p.on("console", m => m.type() === "error" && errs.push(m.text()));
    await p.setContent(html, { waitUntil: "networkidle" }); await p.waitForTimeout(700);
    for (const id of ids) await (await p.$("#" + id)).screenshot({ path: `${out}/p3-${scheme}-${id}.png` });
    console.log(scheme, errs.length ? errs : "no errors");
  }
  const m = await b.newPage({ viewport: { width: 390, height: 800 } });
  await m.setContent(html, { waitUntil: "networkidle" });
  console.log("phone overflow:", await m.evaluate(() => document.documentElement.scrollWidth > innerWidth));
  await b.close();
})();
