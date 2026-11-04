// Zoom the circle packing into one group and hover one arc, to check the interactive states render.
const { chromium } = require(process.argv[2]);
const url = "file:///" + process.argv[3].split("\\").join("/");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  const errs = []; p.on("pageerror", e => errs.push(e.message));
  await p.goto(url, { waitUntil: "networkidle" });
  await p.evaluate(() => {
    const g = [...document.querySelectorAll("#f-pack circle.grp")].find(c => c.__data__.data.name === process_name);
  }).catch(() => {});
  await p.evaluate(name => { const c = [...document.querySelectorAll("#f-pack circle.grp")].find(c => c.__data__.data.name === name); c.dispatchEvent(new MouseEvent("click", { bubbles: true })); }, process.argv[4] || "Laws");
  await p.waitForTimeout(900);
  await (await p.$("#pack")).screenshot({ path: "zoom-pack.png" });
  const box = await (await p.$("#f-arcs")).boundingBox();
  await p.mouse.move(box.x + box.width * .55, box.y + box.height * .74);
  await p.waitForTimeout(200);
  await (await p.$("#arcs")).screenshot({ path: "hover-arcs.png" });
  console.log(errs.length ? errs : "no errors");
  await b.close();
})();
