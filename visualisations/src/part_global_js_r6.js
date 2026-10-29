
// ---- Round 6: constitutional change rates, scatter and map ----
Object.assign(N2, { it: "Italy", pt: "Portugal", mg: "Madagascar", rw: "Rwanda", kg: "Kyrgyzstan" });
const CR = Object.entries(S.const_growth).filter(([c]) => c !== "ch").map(([c, g]) => {
  const age = (P("2026-10-28") - P(g[0].date)) / 3.15576e10, changes = g.length - 1;
  return { c, age, changes, perDecade: changes / (age / 10), words: g.at(-1).words, born: g[0].date.slice(0, 4) };
}).filter(d => d.age > 1);
const ATLAS_NAME = { de: "Germany", sk: "Slovakia", lu: "Luxembourg", li: "Liechtenstein", mc: "Monaco", si: "Slovenia", ee: "Estonia", fi: "Finland",
  hr: "Croatia", gi: "Gibraltar", dk: "Denmark", kg: "Kyrgyzstan", it: "Italy", pt: "Portugal", mg: "Madagascar", rw: "Rwanda" };

// Scatter: age against changes per decade
{
  const W = 960, H = 420, m = { l: 56, r: 30, t: 20, b: 44 };
  const svg = d3.select("#f-cr").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, d3.max(CR, d => d.age) * 1.05], [m.l, W - m.r]);
  const y = d3.scaleSymlog().constant(1).domain([0, d3.max(CR, d => d.perDecade) * 1.15]).range([H - m.b, m.t]);
  const r = d3.scaleSqrt([0, d3.max(CR, d => d.words)], [3, 18]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(8).tickFormat(d => `${d} yrs`));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([0, 1, 2, 5, 10, 20, 50].filter(v => v <= y.domain()[1])).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  svg.append("text").attr("x", W - m.r).attr("y", H - 8).attr("text-anchor", "end").attr("font-size", 11).text("age of the constitution in our history");
  svg.append("text").attr("x", m.l + 4).attr("y", m.t - 6).attr("font-size", 11).text("changes per decade (log scale)");
  const pts = CR.map(d => ({ ...d, x: x(d.age), y: y(d.perDecade) }));
  svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => r(d.words))
    .attr("fill", d => C2[d.c] || "var(--c5)").attr("fill-opacity", .7).attr("stroke", "var(--plate)")
    .append("title").text(d => `${N2[d.c]} (${d.born}): ${d.changes} changes in ${Math.round(d.age)} years, ${d.perDecade.toFixed(1)} per decade, ${fmt(d.words)} words`);
  const labels = pts.map(d => ({ ...d, ly: d.y })).sort((a, b) => a.ly - b.ly);
  for (let i = 1; i < labels.length; i++) if (Math.abs(labels[i].x - labels[i - 1].x) < 90 && labels[i].ly - labels[i - 1].ly < 14) labels[i].ly = labels[i - 1].ly + 14;
  labels.forEach(d => svg.append("text").attr("x", d.x > W - 160 ? d.x - r(d.words) - 4 : d.x + r(d.words) + 4).attr("text-anchor", d.x > W - 160 ? "end" : "start").attr("y", d.ly).attr("dy", "0.32em").attr("font-size", 11.5).attr("class", "lbl")
    .attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(`${N2[d.c]} ${d.born}`));
  const sorted = CR.slice().sort((a, b) => b.perDecade - a.perDecade), top = sorted[0];
  const young = CR.filter(d => d.age < 40), old = CR.filter(d => d.age >= 40);
  const med = a => d3.median(a, d => d.perDecade);
  const never = CR.filter(d => d.changes === 0).map(d => N2[d.c]);
  document.getElementById("cr-eyebrow").textContent = `${CR.length} constitutions · round 6`;
  document.getElementById("cr-text").innerHTML = `Each constitution's age in our history against how often its text changes. <b>${N2[top.c]} changes fastest, ${top.perDecade.toFixed(1)} times a decade. Constitutions under 40 years old change a median ${med(young).toFixed(1)} times a decade, those 40 or older ${med(old).toFixed(1)}.</b> ${never.length ? never.join(" and ") + " have not changed at all. " : ""}Elkins, Ginsburg and Melton's study of national constitutions found they last about two decades on average. The ones that survive longer keep being amended rather than standing still.`;
}

// World map coloured by change rate
{
  const W = 960, H = 470, svg = d3.select("#f-cm").attr("viewBox", `0 0 ${W} ${H}`);
  const byName = Object.fromEntries(CR.map(d => [ATLAS_NAME[d.c], d]));
  const proj = d3.geoNaturalEarth1().fitExtent([[10, 10], [W - 10, H - 50]], { type: "Sphere" }), path = d3.geoPath(proj);
  const col = d3.scaleSequentialSymlog(d3.interpolateYlOrRd).domain([0, d3.max(CR, d => d.perDecade)]);
  svg.append("path").attr("d", path({ type: "Sphere" })).attr("fill", "var(--tint)").attr("stroke", "var(--rule)");
  svg.append("g").selectAll("path").data(WORLD.features).join("path").attr("d", path)
    .attr("fill", f => byName[f.properties.name] ? col(byName[f.properties.name].perDecade) : "var(--plate)").attr("stroke", "var(--rule)").attr("stroke-width", .3)
    .append("title").text(f => { const d = byName[f.properties.name]; return d ? `${N2[d.c]}: ${d.perDecade.toFixed(1)} changes a decade` : f.properties.name; });
  // Microstates as dots
  const DOT = { gi: [-5.35, 36.14], mc: [7.42, 43.74], li: [9.55, 47.16], lu: [6.13, 49.61] };
  Object.entries(DOT).forEach(([c, ll]) => {
    const d = CR.find(e => e.c === c); if (!d) return;
    const [px, py] = proj(ll);
    svg.append("circle").attr("cx", px).attr("cy", py).attr("r", 4).attr("fill", col(d.perDecade)).attr("stroke", "var(--ink)").attr("stroke-width", .6)
      .append("title").text(`${N2[c]}: ${d.perDecade.toFixed(1)} changes a decade`);
  });
  const ticks = [0, 1, 2, 5, 10].filter(v => v <= col.domain()[1]);
  ticks.forEach((v, i) => {
    svg.append("rect").attr("x", 20 + i * 100).attr("y", H - 34).attr("width", 90).attr("height", 10).attr("fill", col(v));
    svg.append("text").attr("x", 20 + i * 100).attr("y", H - 12).attr("font-size", 11).text(`${v} a decade`);
  });
  const conts = { Africa: ["mg", "rw"], Asia: ["kg"] };
  document.getElementById("cm-text").innerHTML = `The ${CR.length} loaded constitutions on one map, coloured by changes per decade. Most are European, so this is still a map of Europe plus ${Object.entries(conts).map(([k, v]) => `${k} (${v.filter(c => CR.find(d => d.c === c)).map(c => N2[c]).join(", ")})`).join(" and ")}. Each new country loaded adds to the global picture.`;
}
