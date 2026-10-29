
// ---- Round 17: date concentration and 1 July ----
{
  const R = DOYJ.map(d => {
    const v = Object.entries(d.doy).sort((a, b) => b[1] - a[1]), tot = d3.sum(v, e => e[1]);
    return { name: d.name, v: d3.sum(v.slice(0, 5), e => e[1]) / tot, top: v.slice(0, 5).map(e => dayLabel(e[0])) };
  }).sort((a, b) => b.v - a.v);
  rankedBars("#f-conc", R, r => `${Math.round(100 * r.v)}% · ${r.top.slice(0, 3).join(", ")}`, "var(--accent)");
  const half = R.filter(r => r.v >= .5).map(r => r.name), spread = R.filter(r => r.v < .1).map(r => r.name);
  document.getElementById("conc-text").innerHTML = `The share of each jurisdiction's law that starts on just its five busiest calendar dates. An even spread would put about 1.4% there. <b>${half.length ? `${half.join(", ")} ${half.length === 1 ? "puts half or more of its" : "put half or more of their"} law on five dates a year` : "No jurisdiction puts half its law on five dates"}${spread.length ? `; ${spread.join(", ")} spread it so evenly that five dates hold under a tenth` : ""}.</b>`;
}
{
  const val = d => d.doy && d.acts >= 100 ? (d.doy["07-01"] || 0) / d3.sum(Object.values(d.doy)) : null;
  const col = d3.scaleSequentialSqrt(d3.interpolateOranges).domain([0, .25]);
  worldMap("#f-mj", val, col, { fmt: v => `${(100 * v).toFixed(1)}% of acts start on 1 July`, items: [[0, "0%"], [.02, "2%"], [.05, "5%"], [.1, "10%"], [.25, "25%"]] });
  const R = J.filter(d => val(d) != null).map(d => [d.name, val(d)]).sort((a, b) => b[1] - a[1]);
  document.getElementById("mj-text").innerHTML = `The share of each jurisdiction's law that starts on 1 July, the year's second-busiest start date. <b>Highest: ${R.slice(0, 4).map(([n, v]) => `${n} (${(100 * v).toFixed(1)}%)`).join(", ")}.</b>`;
}
