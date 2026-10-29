
// ---- Round 14: who makes the law ----
// Mexico's amending decrees are congressional, so the instrument name cannot tell who made them
const MAKER_SKIP = new Set(["mexico"]);
const MK = J.filter(d => d.maker && !MAKER_SKIP.has(d.slug)).map(d => { const t = d3.sum(Object.values(d.maker)); return { ...d, t, p: d.maker.parliament / t, e: d.maker.executive / t, u: d.maker.unclassified / t }; })
  .filter(d => d.t >= 30 && d.u <= .5);
{
  const R = MK.slice().sort((a, b) => b.e - a.e);
  const W = 960, rowH = 22, m = { l: 210, r: 150, t: 28, b: 6 }, H = R.length * rowH + m.t + m.b;
  const svg = d3.select("#f-mk").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, 1], [m.l, W - m.r]);
  const parts = [["e", "executive", "var(--hi)"], ["p", "parliament", "var(--accent)"], ["u", "unclassified", "var(--tint)"]];
  parts.forEach(([, t, c], k) => {
    svg.append("rect").attr("x", m.l + k * 150).attr("y", 6).attr("width", 12).attr("height", 10).attr("fill", c).attr("stroke", "var(--ghost)").attr("stroke-width", k === 2 ? 1 : 0);
    svg.append("text").attr("x", m.l + k * 150 + 18).attr("y", 15).attr("font-size", 11).text(t);
  });
  R.forEach((d, i) => {
    const y = m.t + i * rowH; let acc = 0;
    svg.append("text").attr("x", m.l - 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11.5).attr("class", "lbl").text(d.name);
    parts.forEach(([k, t, c]) => {
      svg.append("rect").attr("x", x(acc)).attr("width", Math.max(0, x(acc + d[k]) - x(acc))).attr("y", y + 4).attr("height", rowH - 8).attr("fill", c)
        .append("title").text(`${d.name}: ${Math.round(100 * d[k])}% ${t} (${fmt(Math.round(d[k] * d.t))} of ${fmt(d.t)})`);
      acc += d[k];
    });
    svg.append("text").attr("x", W - m.r + 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 10.5).text(`${Math.round(100 * d.e)}% exec · n ${fmt(d.t)}`);
  });
  const execMost = R.filter(d => d.e > d.p), parlMost = R.filter(d => d.p > d.e);
  const tE = d3.sum(R, d => d.maker.executive), tP = d3.sum(R, d => d.maker.parliament);
  document.getElementById("mk-text").innerHTML = `Each jurisdiction's dated acts by who made them, as far as the instrument's name tells. <b>Across ${R.length} jurisdictions, ${fmt(tE)} acts are executive and ${fmt(tP)} parliamentary. Governments out-legislate parliaments in ${execMost.length} (${execMost.slice(0, 6).map(d => `${d.name} ${Math.round(100 * d.e)}%`).join(", ")}${execMost.length > 6 ? ", …" : ""}); parliaments lead in ${parlMost.length}.</b> Where a history loads only primary legislation, executive acts are absent by construction, so read those rows as a description of the corpus as much as of the country.`;
}
{
  const byName = Object.fromEntries(MK.map(d => [d.slug, d]));
  const val = d => byName[d.slug] ? byName[d.slug].e / (byName[d.slug].e + byName[d.slug].p || 1) : null;
  const col = d3.scaleSequential(d3.interpolateOrRd).domain([0, 1]);
  worldMap("#f-mx", val, col, { fmt: v => `${Math.round(100 * v)}% of classified acts are executive`, items: [[0, "0%"], [.25, "25%"], [.5, "50%"], [.75, "75%"], [1, "100%"]] });
  const R = J.filter(d => val(d) != null).map(d => [d.name, val(d)]).sort((a, b) => b[1] - a[1]);
  document.getElementById("mx-text").innerHTML = `The executive's share of each country's classified acts, mapped. <b>Highest: ${R.slice(0, 3).map(([n, v]) => `${n} (${Math.round(100 * v)}%)`).join(", ")}. Lowest: ${R.slice(-3).reverse().map(([n, v]) => `${n} (${Math.round(100 * v)}%)`).join(", ")}.</b> A share near zero usually means the history holds only primary legislation, not that the government makes no rules.`;
}
