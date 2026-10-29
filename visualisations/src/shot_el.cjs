const { chromium } = require(process.argv[2]);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  p.on("pageerror", e => console.log("pageerror", e.message));
  await p.goto("file:///" + process.argv[3], { waitUntil: "networkidle" });
  for (const id of process.argv.slice(4)) { await p.locator("#" + id).screenshot({ path: `el-${id}.png` }); }
  await b.close();
})();
