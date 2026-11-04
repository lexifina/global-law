// One PNG per figure, at 2x, named like global-law's stills: <page>-<nn>-<heading slug>.png
const { chromium } = require(process.argv[2]);
const fs = require("fs");
const url = "file:///" + process.argv[3].split("\\").join("/"), page = process.argv[4], out = process.argv[5];
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 2, colorScheme: "light" });
  await p.goto(url, { waitUntil: "networkidle" });
  await p.waitForTimeout(800);
  // Stills are static: collapse the table toggles so they don't show as UI
  await p.addStyleTag({ content: "details { display: none !important; } .hint { display: none !important; }" });
  // Captions that invite hovering or clicking mean nothing in a still
  await p.$$eval(".figtext p", ps => ps.forEach(p => { for (const n of [...p.childNodes]) if (n.nodeType === 3)
    n.textContent = n.textContent.replace(/\s*(Hover|Click)[^.]*\./g, ""); }));
  const figs = await p.$$("figure");
  for (const [i, f] of figs.entries()) {
    const h = await f.$eval("h2", e => e.textContent);
    const slug = h.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 50).replace(/-$/, "");
    const file = `${out}/${page}-${String(i + 1).padStart(2, "0")}-${slug}.png`;
    await f.screenshot({ path: file });
    console.log(file);
  }
  await b.close();
})();
