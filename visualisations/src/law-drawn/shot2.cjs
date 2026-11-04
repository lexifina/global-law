const { chromium } = require(process.argv[2]);
const url = "file:///" + process.argv[3].split("\\").join("/");
(async () => {
  const b = await chromium.launch();
  for (const scheme of ["light", "dark"]) {
    const p = await b.newPage({ viewport: { width: 1100, height: 900 }, colorScheme: scheme });
    const errs = []; p.on("pageerror", e => errs.push(e.message)); p.on("console", m => m.type() === "error" && errs.push(m.text()));
    await p.goto(url, { waitUntil: "networkidle" });
    await p.waitForTimeout(800);
    for (const id of ["growth", "world", "clocks", "russia", "copies"]) await (await p.$("#" + id)).screenshot({ path: `s3-${scheme}-${id}.png` });
    console.log(scheme, errs.length ? errs : "no errors");
  }
  const m = await b.newPage({ viewport: { width: 390, height: 800 } });
  await m.goto(url, { waitUntil: "networkidle" });
  console.log("mobile overflow:", await m.evaluate(() => document.documentElement.scrollWidth > innerWidth));
  await b.close();
})();
