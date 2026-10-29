
// ---- Round 10: three world maps from the all-repository metadata ----
function worldMap(sel, valueOf, colourOf, legend) {
  const W = 960, H = 500, svg = d3.select(sel).attr("viewBox", `0 0 ${W} ${H}`);
  const proj = d3.geoNaturalEarth1().fitExtent([[10, 10], [W - 10, H - 56]], { type: "Sphere" }), path = d3.geoPath(proj);
  const byFeature = new Map();
  J.forEach(d => {
    if (POINT[d.slug]) return;
    const nm = ATLAS_ALIAS[title(d.slug)] || title(d.slug);
    const f = WORLD.features.find(g => g.properties.name === nm || g.properties.name.replace(/\./g, "") === nm);
    if (f) byFeature.set(f, d);
  });
  svg.append("path").attr("d", path({ type: "Sphere" })).attr("fill", "var(--tint)").attr("stroke", "var(--rule)");
  svg.append("g").selectAll("path").data(WORLD.features).join("path").attr("d", path)
    .attr("fill", f => { const d = byFeature.get(f); if (!d) return "var(--plate)"; const v = valueOf(d); return v == null ? "var(--ghost)" : colourOf(v); })
    .attr("stroke", "var(--rule)").attr("stroke-width", .3)
    .append("title").text(f => { const d = byFeature.get(f); if (!d) return f.properties.name; const v = valueOf(d); return `${d.name}: ${v == null ? "not enough data" : legend.fmt(v)}`; });
  // Points for small and sub-national jurisdictions
  J.filter(d => POINT[d.slug]).forEach(d => {
    const v = valueOf(d), [px, py] = proj(POINT[d.slug]);
    svg.append("circle").attr("cx", px).attr("cy", py).attr("r", 4).attr("fill", v == null ? "var(--ghost)" : colourOf(v)).attr("stroke", "var(--ink)").attr("stroke-width", .6)
      .append("title").text(`${d.name}: ${v == null ? "not enough data" : legend.fmt(v)}`);
  });
  legend.items.forEach(([v, t], i) => {
    svg.append("rect").attr("x", 20 + i * 110).attr("y", H - 40).attr("width", 100).attr("height", 10).attr("fill", colourOf(v));
    svg.append("text").attr("x", 20 + i * 110).attr("y", H - 18).attr("font-size", 11).text(t);
  });
}

// Median delay map
{
  const val = d => d.lag && d.lag.n >= 10 ? d.lag.median : null;
  const col = d3.scaleSequentialLog(d3.interpolateYlOrBr).domain([1, 365]).clamp(true);
  const cf = v => col(Math.max(1, v));
  worldMap("#f-ml", val, cf, { fmt: v => `median ${v} days`, items: [[1, "same day"], [7, "a week"], [30, "a month"], [90, "3 months"], [365, "a year"]] });
  const R = J.filter(d => val(d) != null).sort((a, b) => val(a) - val(b));
  const quick = R.filter(d => val(d) <= 14).map(d => d.name), slow = R.filter(d => val(d) >= 60).map(d => d.name);
  document.getElementById("ml-text").innerHTML = `Median delay from adoption to entry into force, mapped. <b>${quick.length} of ${R.length} jurisdictions apply most law within two weeks (${quick.join(", ")}); ${slow.length} take two months or more (${slow.join(", ")}).</b>`;
}

// Share starting on the 1st
{
  const val = d => d.dom && d3.sum(d.dom) >= 30 ? d.dom[0] / d3.sum(d.dom) : null;
  const col = d3.scaleSequential(d3.interpolatePuRd).domain([0, .8]);
  worldMap("#f-mf", val, col, { fmt: v => `${Math.round(100 * v)}% of acts start on the 1st`, items: [[.05, "5%"], [.2, "20%"], [.4, "40%"], [.6, "60%"], [.8, "80%"]] });
  const R = J.filter(d => val(d) != null), over = R.filter(d => val(d) >= .5).map(d => `${d.name} ${Math.round(100 * val(d))}%`);
  document.getElementById("mf-text").innerHTML = `The share of each country's law that starts on the 1st of a month. If start dates were random, about 3% would. <b>${R.filter(d => val(d) >= .1).length} of ${R.length} jurisdictions put at least a tenth of their law on the 1st, and ${over.length} put half or more: ${over.join(", ")}.</b>`;
}

// Busiest month map
{
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const val = d => d.month && d3.sum(d.month) >= 30 ? d.month.indexOf(Math.max(...d.month)) : null;
  const pal = ["#4e79a7", "#a0cbe8", "#59a14f", "#8cd17d", "#b6992d", "#f1ce63", "#e15759", "#ff9d9a", "#f28e2b", "#ffbe7d", "#79706e", "#d37295"];
  const used = [...new Set(J.map(val).filter(v => v != null))].sort((x, y) => x - y);
  worldMap("#f-mm", val, v => pal[v], { fmt: v => `busiest month ${MONTHS[v]}`, items: used.map(v => [v, MONTHS[v]]) });
  const R = J.filter(d => val(d) != null), tally = d3.rollups(R, v => v.map(d => d.name), d => val(d)).sort((a, b) => b[1].length - a[1].length);
  document.getElementById("mm-text").innerHTML = `The month in which each country's law most often takes effect. <b>${tally.slice(0, 3).map(([mIdx, names]) => `${MONTHS[mIdx]} leads in ${names.length} (${names.join(", ")})`).join("; ")}.</b>`;
}
