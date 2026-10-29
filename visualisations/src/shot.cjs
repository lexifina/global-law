const { chromium } = require(process.argv[2]);
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const [w, scheme] of [[1200, "light"], [400, "dark"]]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    p.on("pageerror", e => out.push("pageerror " + e.stack.slice(0, 400)));
    p.on("console", m => m.type() === "error" && out.push("console " + m.text()));
    await p.goto("file:///" + process.argv[3], { waitUntil: "networkidle" });
    await p.waitForTimeout(800);
    out.push(`${w}: scrollWidth ${await p.evaluate(() => document.documentElement.scrollWidth)}`);
    await p.screenshot({ path: `shot2-${w}.png`, fullPage: true });
  }
  console.log(out.join("\n")); await b.close();
})();
