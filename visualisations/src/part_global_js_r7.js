
// ---- Round 7: every loaded history, from commit metadata ----
const A11 = S.a11 || {};
const SUBNATIONAL = { "australia-western-australia": "Western Australia", "canada-northwest-territories": "Northwest Territories", "australia-northern-territory": "Northern Territory" };
const titleWords = s => s.split("-").map(w => ["and", "of", "the"].includes(w) ? w : w[0].toUpperCase() + w.slice(1)).join(" ");
const title = s => SUBNATIONAL[s] || (/^(australia|canada|united-states)-./.test(s) ? titleWords(s.replace(/^(australia|canada|united-states)-/, "")) : titleWords(s));
const ATLAS_ALIAS = { "United States": "United States of America", "Czechia": "Czechia", "Hong Kong": "Hong Kong", "Timor Leste": "Timor-Leste",
  "Bosnia And Herzegovina": "Bosnia and Herz.", "Dominican Republic": "Dominican Rep.", "Aland": "Aland", "Cote Divoire": "Côte d'Ivoire" };
const POINT = { "canada-ontario": [-85.0, 50.0], "australia-south-australia": [135.5, -30.0], "australia-tasmania": [146.6, -42.0], "australia-australian-capital-territory": [149.1, -35.3], "canada-newfoundland-and-labrador": [-57.0, 53.0], "united-states-guam": [144.8, 13.45], "faroe-islands": [-6.9, 62.0], bermuda: [-64.75, 32.3], "san-marino": [12.45, 43.94], "australia-western-australia": [121.6, -25.0], "canada-northwest-territories": [-119.0, 64.8], "australia-northern-territory": [133.4, -19.4], gibraltar: [-5.35, 36.14], aland: [19.9, 60.2], monaco: [7.42, 43.74], liechtenstein: [9.55, 47.16], malta: [14.4, 35.9],
  "hong-kong": [114.17, 22.3], luxembourg: [6.13, 49.61] };
const centroidOf = slug => {
  if (POINT[slug]) return POINT[slug];
  const nm = ATLAS_ALIAS[title(slug)] || title(slug);
  const f = WORLD.features.find(g => g.properties.name === nm || g.properties.name.replace(/\./g, "") === nm);
  return f ? d3.geoCentroid(f) : null;
};
const J = Object.entries(A11).map(([slug, v]) => {
  const ys = Object.keys(v.years).map(Number).sort((a, b) => a - b);
  return { slug, name: title(slug), ...v, first: ys[0], last: ys.at(-1), nyears: ys.length };
}).filter(d => d.acts >= 3).sort((a, b) => b.acts - a.acts);
const totalActs = d3.sum(J, d => d.acts);

// Bubble map
{
  const W = 960, H = 520, svg = d3.select("#f-bub").attr("viewBox", `0 0 ${W} ${H}`);
  const proj = d3.geoNaturalEarth1().fitExtent([[10, 10], [W - 10, H - 60]], { type: "Sphere" }), path = d3.geoPath(proj);
  svg.append("path").attr("d", path({ type: "Sphere" })).attr("fill", "var(--tint)").attr("stroke", "var(--rule)");
  svg.append("g").selectAll("path").data(WORLD.features).join("path").attr("d", path).attr("fill", "var(--plate)").attr("stroke", "var(--rule)").attr("stroke-width", .3);
  const r = d3.scaleSqrt([0, d3.max(J, d => d.acts)], [2.5, 34]);
  const col = d3.scaleSequential(d3.interpolateViridis).domain([1850, 2025]);
  const pts = J.map(d => ({ ...d, ll: centroidOf(d.slug) })).filter(d => d.ll).map(d => ({ ...d, xy: proj(d.ll) })).sort((a, b) => b.acts - a.acts);
  svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => d.xy[0]).attr("cy", d => d.xy[1]).attr("r", d => r(d.acts))
    .attr("fill", d => col(Math.max(1850, d.first))).attr("fill-opacity", .72).attr("stroke", "var(--plate)").attr("stroke-width", .8)
    .append("title").text(d => `${d.name}: ${fmt(d.acts)} dated acts, ${d.first}–${d.last}, ${fmt(d.commits)} commits`);
  pts.slice(0, 10).forEach(d => svg.append("text").attr("x", d.xy[0]).attr("y", d.xy[1] - r(d.acts) - 4).attr("text-anchor", "middle").attr("font-size", 11).attr("class", "lbl")
    .attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(d.name));
  [1850, 1900, 1950, 2000, 2025].forEach((v, i) => {
    svg.append("rect").attr("x", 20 + i * 80).attr("y", H - 40).attr("width", 70).attr("height", 10).attr("fill", col(v));
    svg.append("text").attr("x", 20 + i * 80).attr("y", H - 18).attr("font-size", 11).text(i === 0 ? "≤1850" : v);
  });
  svg.append("text").attr("x", 430).attr("y", H - 30).attr("font-size", 11).text("colour: earliest in-force year · size: dated acts");
  const unplaced = J.filter(d => !centroidOf(d.slug)).map(d => d.name);
  document.getElementById("bub-eyebrow").textContent = `${J.length} jurisdictions · round 7`;
  document.getElementById("bub-text").innerHTML = `Every jurisdiction with dated amending acts on disk. <b>${fmt(totalActs)} dated acts across ${J.length} jurisdictions. ${J.slice(0, 3).map(d => `${d.name} (${fmt(d.acts)})`).join(", ")} hold the most.</b> The earliest in-force date belongs to ${d3.least(J, d => d.first).name} (${d3.min(J, d => d.first)}).${unplaced.length ? ` Not on the map: ${unplaced.join(", ")}.` : ""}`;
}

// Coverage spans
{
  const R = J.slice().sort((a, b) => a.first - b.first || b.acts - a.acts);
  const W = 960, rowH = 20, m = { l: 150, r: 160, t: 10, b: 30 }, H = R.length * rowH + m.t + m.b;
  const svg = d3.select("#f-span").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([Math.min(1850, d3.min(R, d => d.first)), 2027], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(12).tickFormat(d3.format("d")).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  R.forEach((d, i) => {
    const y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 8).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11.5).attr("class", "lbl").text(d.name);
    svg.append("line").attr("x1", x(d.first)).attr("x2", x(d.last + 1)).attr("y1", y).attr("y2", y).attr("stroke", "var(--rule)").attr("stroke-width", 8).attr("stroke-linecap", "round");
    Object.keys(d.years).forEach(yr => svg.append("rect").attr("x", x(+yr)).attr("width", Math.max(1.2, x(1) - x(0))).attr("y", y - 4).attr("height", 8).attr("fill", "var(--accent)"));
    svg.append("text").attr("x", W - m.r + 8).attr("y", y).attr("dy", "0.32em").attr("font-size", 10.5).text(`${d.first}–${d.last} · ${fmt(d.acts)}`);
  });
  const deep = R.filter(d => d.first < 1950).map(d => `${d.name} (${d.first})`);
  const recent = R.filter(d => d.first >= 2010).length;
  document.getElementById("span-text").innerHTML = `The years each history covers. <b>${deep.length} reach back before 1950: ${deep.join(", ")}.</b> ${recent} start in 2010 or later.`;
}

// Heatmap: acts per year
{
  const years = d3.range(1990, 2027), R = J.filter(d => d3.sum(years, y => d.years[y] || 0) > 0);
  const W = 960, cell = 18, m = { l: 150, r: 70, t: 24, b: 10 }, cw = (W - m.l - m.r) / years.length, H = R.length * cell + m.t + m.b;
  const svg = d3.select("#f-heat").attr("viewBox", `0 0 ${W} ${H}`);
  const max = d3.max(R, d => d3.max(years, y => d.years[y] || 0));
  const col = d3.scaleSequentialLog(d3.interpolateYlGnBu).domain([1, max]);
  years.forEach((y, j) => { if (y % 5 === 0) svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", m.t - 8).attr("text-anchor", "middle").attr("font-size", 10.5).text(y); });
  R.forEach((d, i) => {
    const y0 = m.t + i * cell;
    svg.append("text").attr("x", m.l - 8).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(d.name);
    years.forEach((y, j) => {
      const n = d.years[y] || 0;
      svg.append("rect").attr("x", m.l + j * cw + .5).attr("y", y0 + .5).attr("width", cw - 1).attr("height", cell - 1)
        .attr("fill", n ? col(n) : "var(--tint)").append("title").text(`${d.name} ${y}: ${n} acts`);
    });
    svg.append("text").attr("x", W - m.r + 6).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("font-size", 10.5).text(fmt(d3.sum(years, y => d.years[y] || 0)));
  });
  const byYear = years.map(y => [y, d3.sum(R, d => d.years[y] || 0)]), peak = d3.greatest(byYear, d => d[1]);
  document.getElementById("heat-text").innerHTML = `Amending acts per year for every jurisdiction, 1990 to 2026. <b>Across all of them the busiest year is ${peak[0]}, with ${fmt(peak[1])} acts in force.</b> The whole statute books (${J.slice(0, 4).map(d => d.name).join(", ")}) dominate the counts. The colour scale is logarithmic so small histories still show.`;
}

// Lag for every jurisdiction
{
  const L = J.filter(d => d.lag && d.lag.n >= 10).sort((a, b) => a.lag.median - b.lag.median || b.lag.n - a.lag.n);
  const W = 960, rowH = 24, m = { l: 150, r: 150, t: 24, b: 34 }, H = L.length * rowH + m.t + m.b;
  const svg = d3.select("#f-lagall").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleSymlog([-30, 2000], [m.l, W - m.r]).constant(3), cx = v => x(Math.max(-30, Math.min(2000, v)));
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues([0, 3, 7, 14, 30, 90, 180, 365, 730]).tickFormat(v => v === 0 ? "same day" : v >= 365 ? `${v / 365} yr` : `${v} d`).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  L.forEach((d, i) => {
    const v = d.lag, y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12).text(d.name);
    svg.append("line").attr("x1", cx(v.p05)).attr("x2", cx(v.p95)).attr("y1", y).attr("y2", y).attr("stroke", "var(--ghost)").attr("stroke-width", 1.5);
    svg.append("rect").attr("x", cx(v.q1)).attr("width", Math.max(2, cx(v.q3) - cx(v.q1))).attr("y", y - 7).attr("height", 14).attr("fill", "var(--accent)").attr("fill-opacity", .45).attr("rx", 2);
    svg.append("line").attr("x1", cx(v.median)).attr("x2", cx(v.median)).attr("y1", y - 9).attr("y2", y + 9).attr("stroke", "var(--ink)").attr("stroke-width", 2.2);
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 10.5).text(`${v.median === 0 ? "same day" : Math.round(v.median) + " d"} · n ${fmt(v.n)}`);
  });
  const all = d3.sum(L, d => d.lag.n), w30 = d3.sum(L, d => d.lag.within30);
  document.getElementById("lagall-eyebrow").textContent = `${L.length} jurisdictions · round 7`;
  document.getElementById("lagall-text").innerHTML = `Days from adoption to entry into force for ${fmt(all)} acts in ${L.length} jurisdictions with at least ten dated pairs. <b>${Math.round(100 * w30 / all)}% take effect within a month. The fastest median is ${L[0].name}'s (${L[0].lag.median === 0 ? "the same day" : L[0].lag.median + " days"}), the slowest ${L.at(-1).name}'s (${Math.round(L.at(-1).lag.median)} days).</b>`;
}

// Weekday and month heatmaps
function shareHeat(sel, key, labels, textId, sentence) {
  const R = J.filter(d => d3.sum(d[key] || []) >= 30), W = 960, cell = 20, m = { l: 150, r: 20, t: 26, b: 10 }, cw = (W - m.l - m.r) / labels.length, H = R.length * cell + m.t + m.b;
  const svg = d3.select(sel).attr("viewBox", `0 0 ${W} ${H}`);
  const col = d3.scaleSequential(d3.interpolateOrRd).domain([0, .5]);
  labels.forEach((t, j) => svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", m.t - 8).attr("text-anchor", "middle").attr("font-size", 11).text(t));
  R.forEach((d, i) => {
    const y0 = m.t + i * cell, tot = d3.sum(d[key]);
    svg.append("text").attr("x", m.l - 8).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(d.name);
    d[key].forEach((n, j) => {
      const s = n / tot;
      svg.append("rect").attr("x", m.l + j * cw + .5).attr("y", y0 + .5).attr("width", cw - 1).attr("height", cell - 1).attr("fill", col(Math.min(.5, s)))
        .append("title").text(`${d.name}, ${labels[j]}: ${Math.round(100 * s)}% (${n} of ${tot})`);
      if (s >= .2) svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("text-anchor", "middle").attr("font-size", 10).style("fill", s > .28 ? "#fff" : "var(--ink)").text(`${Math.round(100 * s)}%`);
    });
  });
  document.getElementById(textId).innerHTML = sentence(R);
}
shareHeat("#f-wd", "weekday", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "wd-text", R => {
  const tot = R.reduce((a, d) => a.map((v, i) => v + d.weekday[i] / d3.sum(d.weekday)), Array(7).fill(0)).map(v => v / R.length);
  const names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], top = tot.indexOf(Math.max(...tot));
  const weekend = R.filter(d => (d.weekday[5] + d.weekday[6]) / d3.sum(d.weekday) > .2).map(d => d.name);
  return `The weekday each act took effect, as a share of each jurisdiction's acts. <b>Averaged across jurisdictions, ${names[top]} is the most common start day (${Math.round(100 * tot[top])}%).</b> ${weekend.length ? `In ${weekend.join(", ")} more than a fifth of acts start on a Saturday or Sunday.` : ""}`;
});
shareHeat("#f-mon", "month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "mon-text", R => {
  const jan = R.map(d => [d.name, d.month[0] / d3.sum(d.month)]).sort((a, b) => b[1] - a[1]);
  const jul = R.map(d => [d.name, d.month[6] / d3.sum(d.month)]).sort((a, b) => b[1] - a[1]);
  return `The month each act took effect. <b>January leads in ${R.filter(d => d.month.indexOf(Math.max(...d.month)) === 0).length} of ${R.length} jurisdictions</b>, led by ${jan.slice(0, 3).map(([n, s]) => `${n} (${Math.round(100 * s)}%)`).join(", ")}. July is the second peak, strongest in ${jul.slice(0, 2).map(([n, s]) => `${n} (${Math.round(100 * s)}%)`).join(" and ")}.`;
});
