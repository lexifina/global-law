
// ---- Round 18: calendar similarity and predictability ----
{
  const R = J.filter(d => d.month && d.acts >= 100).map(d => { const t = d3.sum(d.month); return { ...d, v: d.month.map(n => n / t) }; })
    .sort((a, b) => b.v[0] - a.v[0] || b.v[6] - a.v[6]);
  const cos = (a, b) => d3.sum(a, (x, i) => x * b[i]) / Math.sqrt(d3.sum(a, x => x * x) * d3.sum(b, x => x * x));
  const n = R.length, cell = Math.min(24, Math.floor(700 / Math.max(n, 1))), m = { l: 150, t: 120 }, W = 960, H = m.t + n * cell + 20;
  const svg = d3.select("#f-sim").attr("viewBox", `0 0 ${W} ${H}`);
  const col = d3.scaleSequential(d3.interpolateYlGnBu).domain([.4, 1]).clamp(true);
  R.forEach((a, i) => {
    svg.append("text").attr("x", m.l - 6).attr("y", m.t + i * cell + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(a.name);
    svg.append("text").attr("transform", `translate(${m.l + i * cell + cell / 2},${m.t - 6}) rotate(-60)`).attr("font-size", 10.5).text(a.name);
    R.forEach((b, j) => {
      const s = cos(a.v, b.v);
      svg.append("rect").attr("x", m.l + j * cell + .5).attr("y", m.t + i * cell + .5).attr("width", cell - 1).attr("height", cell - 1).attr("fill", i === j ? "var(--tint)" : col(s))
        .append("title").text(`${a.name} and ${b.name}: ${s.toFixed(2)}`);
    });
  });
  const pairs = [];
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) pairs.push([R[i].name, R[j].name, cos(R[i].v, R[j].v)]);
  pairs.sort((a, b) => b[2] - a[2]);
  const lx = m.l + n * cell + 30;
  [.4, .6, .8, 1].forEach((v, k) => {
    svg.append("rect").attr("x", lx).attr("y", m.t + k * 22).attr("width", 16).attr("height", 16).attr("fill", col(v));
    svg.append("text").attr("x", lx + 24).attr("y", m.t + k * 22 + 8).attr("dy", "0.32em").attr("font-size", 11).text(v === .4 ? "≤0.4" : v.toFixed(1));
  });
  document.getElementById("sim-text").innerHTML = `How alike each pair of countries' legal calendars is, month by month. <b>The closest pairs are ${pairs.slice(0, 3).map(([a, b, s]) => `${a} and ${b} (${s.toFixed(2)})`).join(", ")}; the least alike, ${pairs.at(-1)[0]} and ${pairs.at(-1)[1]} (${pairs.at(-1)[2].toFixed(2)}).</b>`;
}
{
  const R = DOYJ.map(d => {
    const v = Object.values(d.doy), t = d3.sum(v), H = -d3.sum(v, n => (n / t) * Math.log(n / t));
    return { name: d.name, v: 1 - H / Math.log(366) };
  }).sort((a, b) => b.v - a.v);
  rankedBars("#f-pred", R, r => r.v.toFixed(2), "var(--c5)");
  document.getElementById("pred-text").innerHTML = `A single score for how concentrated each country's start dates are across the year. <b>${R.slice(0, 3).map(r => `${r.name} (${r.v.toFixed(2)})`).join(", ")} are the most predictable; ${R.slice(-3).reverse().map(r => `${r.name} (${r.v.toFixed(2)})`).join(", ")} the least.</b>`;
}
