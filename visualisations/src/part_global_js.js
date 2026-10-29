
// ---- Global view (round 4) ----
const READY = [["held", "history loaded", "var(--ink)"], ["ready", "ready: dated versions, names the amending act", "var(--now)"],
  ["partial", "partly ready", "color-mix(in srgb, var(--now) 45%, transparent)"], ["scrape", "history online, needs scraping", "var(--later)"],
  ["gazette", "gazette only: rebuild by replaying acts", "color-mix(in srgb, var(--accent) 30%, transparent)"], ["none", "no usable official source", "var(--hi)"]];
const RCOL = Object.fromEntries(READY.map(r => [r[0], r[2]]));
const WORLD = topojson.feature(S.atlas, S.atlas.objects.countries);
const keyOf = f => f.id ?? ("name:" + f.properties.name);
const READY_BY = {}; S.readiness.forEach(r => { if (r.atlas) READY_BY[r.atlas] = r; });
const featOf = r => r.atlas && WORLD.features.find(g => keyOf(g) === r.atlas);
const labelOf = k => READY.find(x => x[0] === k)[1];

// World map of readiness
{
  const W = 960, H = 540, svg = d3.select("#f-world").attr("viewBox", `0 0 ${W} ${H}`);
  const proj = d3.geoNaturalEarth1().fitExtent([[10, 10], [W - 10, H - 86]], { type: "Sphere" }), path = d3.geoPath(proj);
  svg.append("path").attr("d", path({ type: "Sphere" })).attr("fill", "var(--tint)").attr("stroke", "var(--rule)");
  svg.append("g").selectAll("path").data(WORLD.features).join("path").attr("d", path)
    .attr("fill", f => READY_BY[keyOf(f)] ? RCOL[READY_BY[keyOf(f)].build] : "var(--plate)").attr("stroke", "var(--plate)").attr("stroke-width", .4)
    .append("title").text(f => { const r = READY_BY[keyOf(f)]; return r ? `${r.name}: ${labelOf(r.build)}` : f.properties.name; });
  // Small jurisdictions as dots so they stay visible
  const dots = S.readiness.filter(r => r.point || (featOf(r) && d3.geoArea(featOf(r)) < 2e-5));
  const at = r => proj(r.point || d3.geoCentroid(featOf(r)));
  svg.append("g").selectAll("circle").data(dots).join("circle")
    .attr("cx", r => at(r)[0]).attr("cy", r => at(r)[1]).attr("r", r => r.build === "held" ? 4 : 2.6)
    .attr("fill", r => RCOL[r.build]).attr("stroke", "var(--plate)").attr("stroke-width", .8)
    .append("title").text(r => `${r.name}: ${labelOf(r.build)}`);
  const counts = d3.rollup(S.readiness, v => v.length, r => r.build);
  READY.forEach(([k, t, c], i) => {
    const x = 20 + (i % 2) * 470, y = H - 74 + Math.floor(i / 2) * 22;
    svg.append("rect").attr("x", x).attr("y", y).attr("width", 12).attr("height", 12).attr("fill", c).attr("stroke", "var(--ghost)").attr("stroke-width", .5);
    svg.append("text").attr("x", x + 18).attr("y", y + 10).attr("font-size", 11.5).text(`${t} · ${counts.get(k) || 0}`);
  });
}

// Europe inset: most of what we hold is small
{
  const W = 960, H = 480, svg = d3.select("#f-europe").attr("viewBox", `0 0 ${W} ${H}`);
  const proj = d3.geoConicConformal().rotate([-12, 0]).center([0, 52]).parallels([35, 65]).scale(900).translate([W / 2, H / 2 + 10]), path = d3.geoPath(proj);
  const NUDGE = { Liechtenstein: [-7, 10, "end"], Switzerland: [-7, -4, "end"], Monaco: [-7, 6, "end"] };
  svg.append("rect").attr("width", W).attr("height", H).attr("fill", "var(--tint)");
  svg.append("g").selectAll("path").data(WORLD.features).join("path").attr("d", path)
    .attr("fill", f => READY_BY[keyOf(f)] ? RCOL[READY_BY[keyOf(f)].build] : "var(--plate)").attr("stroke", "var(--plate)").attr("stroke-width", .6)
    .append("title").text(f => { const r = READY_BY[keyOf(f)]; return r ? `${r.name}: ${labelOf(r.build)}` : f.properties.name; });
  S.readiness.filter(r => r.build === "held").forEach(r => {
    const f = featOf(r), pt = proj(r.point || (f ? d3.geoCentroid(f) : [0, 0]));
    if (!pt || pt[0] < 0 || pt[0] > W || pt[1] < 0 || pt[1] > H) return;
    svg.append("circle").attr("cx", pt[0]).attr("cy", pt[1]).attr("r", 4.5).attr("fill", "var(--ink)").attr("stroke", "var(--plate)").attr("stroke-width", 1.2);
    const [dx, dy, anchor] = NUDGE[r.name] || [7, 0, "start"];
    svg.append("text").attr("x", pt[0] + dx).attr("y", pt[1] + dy).attr("dy", "0.32em").attr("text-anchor", anchor).attr("font-size", 11.5).attr("class", "lbl")
      .attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(r.name);
  });
}

// Global timeline of amending acts
{
  const A = S.r4.acts_per_year, codes = Object.keys(A).filter(c => c !== "mt").sort((a, b) => d3.sum(Object.values(A[b])) - d3.sum(Object.values(A[a])));
  const PAL = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#86bcb6", "#8cd17d", "#d37295", "#bab0ac", "#499894", "#f1ce63"];
  const TC = Object.fromEntries(codes.map((c, i) => [c, PAL[i % PAL.length]]));
  const years = d3.range(1945, 2027);
  const rows = years.map(y => Object.fromEntries([["y", y], ...codes.map(c => [c, A[c][y] || 0])]));
  const stack = d3.stack().keys(codes)(rows);
  const W = 960, H = 360, m = { l: 44, r: 16, t: 64, b: 30 };
  const svg = d3.select("#f-global").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleBand(years, [m.l, W - m.r]).padding(.12);
  const y = d3.scaleLinear().domain([0, d3.max(stack.at(-1), d => d[1])]).nice().range([H - m.b, m.t]);
  [[1990, 1992, "new constitutions after 1989"], [2004, 2004, "EU enlargement"], [2020, 2021, "COVID-19"]].forEach(([a, b, t]) => {
    svg.append("rect").attr("x", x(a) - 2).attr("width", x(b) + x.bandwidth() - x(a) + 4).attr("y", m.t - 4).attr("height", H - m.b - m.t + 4).attr("fill", "var(--tint)");
    svg.append("text").attr("x", x(b) + x.bandwidth()).attr("y", m.t + 8).attr("text-anchor", "end").attr("font-size", 10.5).text(t);
  });
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues(years.filter(v => v % 5 === 0)));
  stack.forEach(s => svg.append("g").selectAll("rect").data(s).join("rect")
    .attr("x", d => x(d.data.y)).attr("width", x.bandwidth()).attr("y", d => y(d[1])).attr("height", d => y(d[0]) - y(d[1])).attr("fill", TC[s.key])
    .append("title").text(d => `${d.data.y} · ${N2[s.key]}: ${d.data[s.key]} amending act${d.data[s.key] === 1 ? "" : "s"}`));
  const lg = codes.map(c => [c, d3.sum(Object.values(A[c]))]).sort((a, b) => b[1] - a[1]);
  lg.forEach(([c], i) => {
    const lx = m.l + (i % 8) * 112, ly = 6 + Math.floor(i / 8) * 18;
    svg.append("rect").attr("x", lx).attr("y", ly).attr("width", 9).attr("height", 9).attr("fill", TC[c]);
    svg.append("text").attr("x", lx + 13).attr("y", ly + 8).attr("font-size", 10.5).text(N2[c]);
  });
}

// Captions computed from the data, so they stay true as rounds add jurisdictions
{
  const A = S.r4.acts_per_year, codes = Object.keys(A).filter(c => c !== "mt");
  const byYear = {}; codes.forEach(c => Object.entries(A[c]).forEach(([y, n]) => { byYear[y] = (byYear[y] || 0) + n; }));
  const total = d3.sum(Object.values(byYear)), peak = Object.entries(byYear).sort((a, b) => b[1] - a[1])[0];
  const since2010 = d3.sum(Object.entries(byYear).filter(([y]) => +y >= 2010).map(([, n]) => n));
  const wave = ["ee", "sk", "si", "hr"].filter(c => S.const_growth[c]).map(c => `${N2[c]} ${S.const_growth[c][0].date.slice(0, 4)}`).join(", ");
  document.querySelector("#global-timeline .eyebrow").textContent = `${codes.length} jurisdictions · 1945–2026`;
  document.getElementById("gt-text").innerHTML = `Every amending act in the loaded histories, by the year it took effect, stacked by jurisdiction. <b>${fmt(total)} acts in all; the busiest year is ${peak[0]} with ${peak[1]}, and ${Math.round(100 * since2010 / total)}% fall after 2010</b>, partly because most histories start recently. The bands mark the post-1989 constitutional wave (${wave}), the 2004 EU enlargement and the COVID-19 years.`;
  const G = S.const_growth, lc = Object.keys(G);
  const amendN = c => G[c].length - 1;
  const most = lc.slice().sort((a, b) => amendN(b) - amendN(a))[0], never = lc.filter(c => amendN(c) === 0).map(c => N2[c]);
  const oldest = lc.slice().sort((a, b) => G[a][0].date.localeCompare(G[b][0].date))[0];
  document.querySelector("#lifelines .eyebrow").textContent = `${lc.length} constitutions · ${G[oldest][0].date.slice(0, 4)}–2026`;
  document.getElementById("life-text").innerHTML = `Each constitution from its adoption to today, with a tick for every change to its text. <b>${N2[most]} has the most changes (${amendN(most)}); ${never.length ? never.join(" and ") + " never changed a word" : "every one has changed"}.</b> The oldest, ${N2[oldest]}'s of ${G[oldest][0].date.slice(0, 4)}, was first changed in ${G[oldest][1] ? G[oldest][1].date.slice(0, 4) : "no year yet"}.`;
}

// Constitutional lifelines
{
  const G = S.const_growth, codes = Object.keys(G).sort((a, b) => G[a][0].date.localeCompare(G[b][0].date));
  const W = 960, rowH = 30, m = { l: 130, r: 130, t: 10, b: 30 }, H = codes.length * rowH + m.t + m.b;
  const svg = d3.select("#f-life").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleUtc([P("1860-01-01"), P("2027-01-01")], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(d3.utcYear.every(20)).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  codes.forEach((c, i) => {
    const y = m.t + i * rowH + rowH / 2, g = G[c], born = g[0].date, amends = g.slice(1);
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[c]);
    svg.append("line").attr("x1", x(P(born))).attr("x2", x(P("2026-10-28"))).attr("y1", y).attr("y2", y).attr("stroke", C2[c] || "var(--ink)").attr("stroke-opacity", .3).attr("stroke-width", 8).attr("stroke-linecap", "round");
    svg.append("circle").attr("cx", x(P(born))).attr("cy", y).attr("r", 5).attr("fill", C2[c] || "var(--ink)").append("title").text(`${N2[c]}: adopted ${born}`);
    svg.append("g").selectAll("line").data(amends).join("line").attr("x1", d => x(P(d.date))).attr("x2", d => x(P(d.date))).attr("y1", y - 9).attr("y2", y + 9)
      .attr("stroke", "var(--ink)").attr("stroke-width", 1.4).append("title").text(d => `${d.date} · ${d.law}`);
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11).text(`${born.slice(0, 4)} · ${amends.length} change${amends.length === 1 ? "" : "s"}`);
  });
}
