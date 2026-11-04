// Part two: the regions. Uses DATA3 (data3.json + growth.json + copy.json).
const LEVELS = [["national", "--c1", "National"], ["region", "--c3", "Regional"], ["city", "--c4", "City"]];
const levelCol = new Map(LEVELS.map(([k, v]) => [k, v]));
legendDots("lg-growth", LEVELS.map(([k, v, n]) => [n, v]));
legendDots("lg-world", LEVELS.map(([k, v, n]) => [n, v]));

// 6. Growth of global-law
{
  const G = DATA3.growth.map(r => ({ t: new Date(r[0]), national: r[1], region: r[2], city: r[3], countries: r[4] }));
  const W = 960, H = 380, m = { t: 20, r: 150, b: 40, l: 52 };
  const svg = d3.select("#f-growth").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleTime().domain(d3.extent(G, d => d.t)).range([m.l, W - m.r]);
  const stack = d3.stack().keys(["national", "region", "city"])(G);
  const y = d3.scaleLinear().domain([0, 700]).range([H - m.b, m.t]);
  svg.append("g").attr("class", "grid").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(7).tickSize(-(W - m.l - m.r)).tickFormat(""))
    .call(g => g.selectAll("line").attr("stroke", "var(--rule)")).call(g => g.select(".domain").remove());
  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.timeDay.every(1)).tickFormat(d3.timeFormat("%-d %b")))
    .call(g => g.select(".domain").attr("stroke", "var(--rule)")).call(g => g.selectAll("line").attr("stroke", "var(--rule)"));
  svg.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(7)).call(g => g.select(".domain").remove()).call(g => g.selectAll("line").remove());
  const area = d3.area().x(d => x(d.data.t)).y0(d => y(d[0])).y1(d => y(d[1])).curve(d3.curveStepAfter);
  svg.append("g").selectAll("path").data(stack).join("path").attr("d", area).attr("fill", s => `var(${levelCol.get(s.key)})`).attr("fill-opacity", .85)
    .attr("stroke", "var(--plate)").attr("stroke-width", 1);
  const last = G.at(-1);
  stack.forEach(s => { const v = s.at(-1); svg.append("text").attr("class", "lbl").attr("x", W - m.r + 8).attr("y", (y(v[0]) + y(v[1])) / 2 + 4)
    .text(`${LEVELS.find(l => l[0] === s.key)[2]} · ${s.key === "national" ? last.national : s.key === "region" ? last.region : last.city}`); });
  svg.append("text").attr("x", W - m.r + 8).attr("y", y(last.national + last.region + last.city) - 10).text(`${last.countries} countries`);
  const bis = d3.bisector(d => d.t).left, rule = svg.append("line").attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--ink)").attr("opacity", 0);
  svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b).attr("fill", "transparent")
    .on("pointermove", ev => { const t = x.invert(d3.pointer(ev)[0]); const d = G[Math.max(0, Math.min(G.length - 1, bis(G, t) - 1))];
      rule.attr("x1", x(d.t)).attr("x2", x(d.t)).attr("opacity", .4);
      showTip(ev, `<b>${d3.timeFormat("%-d %b, %H:%M UTC")(d.t)}</b><br>${d.national + d.region + d.city} corpora in ${d.countries} countries<br><span class="m">national ${d.national} · regional ${d.region} · city ${d.city}</span>`); })
    .on("pointerleave", () => { rule.attr("opacity", 0); hideTip(); });
}

// 7. The world's law, packed
{
  const P = DATA3.pack, S = 860;
  const byC = d3.group(P, p => p[0]);
  const root = d3.hierarchy({ children: [...byC].map(([k, v]) => ({ name: v[0][1], children: v.map(p => ({ name: p[2], level: p[3], acts: p[4], repo: p[5], value: Math.sqrt(p[4]) })) })) })
    .sum(d => d.value || 0).sort((a, b) => b.value - a.value);
  d3.pack().size([S, S]).padding(d => d.depth === 0 ? 3 : 1)(root);
  const svg = d3.select("#f-world").attr("viewBox", `0 0 ${S} ${S}`);
  svg.append("g").selectAll("circle").data(root.children).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r)
    .attr("fill", "var(--bg)").attr("stroke", "var(--rule)")
    .on("pointermove", (ev, d) => showTip(ev, `<b>${d.data.name}</b><br>${d.children.length} corpora · ${fmt(d3.sum(d.children, c => c.data.acts))} dated changes`)).on("pointerleave", hideTip);
  svg.append("g").selectAll("circle").data(root.leaves()).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r)
    .attr("fill", d => `var(${levelCol.get(d.data.level)})`).attr("fill-opacity", .85)
    .on("pointermove", (ev, d) => showTip(ev, `<b>${d.parent.data.name}${d.data.name === "national" ? "" : " · " + d.data.name.replace(/-/g, " ")}</b><br>${fmt(d.data.acts)} dated changes · ${d.data.level}<br><span class="m">${d.data.repo}</span>`))
    .on("pointerleave", hideTip);
  svg.append("g").attr("pointer-events", "none").selectAll("text").data(root.children.filter(d => d.r > 26)).join("text").attr("class", "lbl halo")
    .attr("x", d => d.x).attr("y", d => d.children.length > 1 ? d.y - d.r - 3 : d.y + 4).attr("text-anchor", "middle")
    .style("font-size", d => Math.min(13, 8 + d.r / 14) + "px").text(d => d.data.name);
}

// 8. Federation clocks
{
  const C = DATA3.calendars, cols = 4, cell = 236, W = cols * cell, rows = Math.ceil(C.length / cols), H = rows * (cell + 26);
  const svg = d3.select("#f-clocks").attr("viewBox", `0 0 ${W} ${H}`);
  const r0 = 30, r1 = 92, mx = d3.max(C, c => d3.max(c.share));
  const len = d3.scalePow().exponent(.4).domain([0, mx]).range([0, r1 - r0]);
  const firsts = new Set([0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]);
  C.forEach((c, i) => {
    const g = svg.append("g").attr("transform", `translate(${(i % cols) * cell + cell / 2},${Math.floor(i / cols) * (cell + 26) + cell / 2 + 4})`);
    g.append("circle").attr("r", r0).attr("fill", "none").attr("stroke", "var(--rule)");
    g.append("circle").attr("r", r1).attr("fill", "none").attr("stroke", "var(--rule)").attr("stroke-dasharray", "2 3");
    ["J", "A", "J", "O"].forEach((t, k) => { const a = k * Math.PI / 2 - Math.PI / 2;
      g.append("text").attr("x", (r1 + 9) * Math.cos(a)).attr("y", (r1 + 9) * Math.sin(a) + 4).attr("text-anchor", "middle").style("font-size", "9.5px").text(t); });
    g.selectAll("line.d").data(c.share).join("line").attr("class", "d")
      .attr("x1", (v, d) => r0 * Math.cos(d / 366 * 2 * Math.PI - Math.PI / 2)).attr("y1", (v, d) => r0 * Math.sin(d / 366 * 2 * Math.PI - Math.PI / 2))
      .attr("x2", (v, d) => (r0 + len(v)) * Math.cos(d / 366 * 2 * Math.PI - Math.PI / 2)).attr("y2", (v, d) => (r0 + len(v)) * Math.sin(d / 366 * 2 * Math.PI - Math.PI / 2))
      .attr("stroke", (v, d) => firsts.has(d) ? "var(--c2)" : "var(--c1)").attr("stroke-width", (v, d) => firsts.has(d) ? 2 : 1.1).attr("stroke-linecap", "round");
    g.append("text").attr("class", "ser").attr("text-anchor", "middle").attr("y", 2).style("font-size", "12px").text(`${Math.round(c.first * 100)}%`);
    g.append("text").attr("text-anchor", "middle").attr("y", 14).style("font-size", "8.5px").text("on a 1st");
    g.append("text").attr("class", "lbl").attr("text-anchor", "middle").attr("y", r1 + 30).style("font-size", "12px").text(c.name);
    g.append("text").attr("text-anchor", "middle").attr("y", r1 + 44).style("font-size", "10px").text(`${c.corpora} corpora · ${fmt(c.acts)} changes`);
    g.append("circle").attr("r", r1 + 4).attr("fill", "transparent").on("pointermove", ev => {
      const [mx_, my_] = d3.pointer(ev); let a = Math.atan2(my_, mx_) + Math.PI / 2; if (a < 0) a += 2 * Math.PI;
      const d = Math.min(365, Math.floor(a / (2 * Math.PI) * 366)), dt = new Date(2024, 0, 1 + d);
      showTip(ev, `<b>${c.name}, ${d3.timeFormat("%-d %B")(dt)}</b><br>${(c.share[d] * 100).toFixed(c.share[d] < .01 ? 2 : 1)}% of regional changes start this day<br><span class="m">busiest day ${d3.timeFormat("%-d %B")(new Date("2024-" + c.top[0]))} (${fmt(c.top[1])} changes)</span>`); })
      .on("pointerleave", hideTip);
  });
}

// 9. Russia's regional waves
{
  const R = DATA3.russia, rows = R.rows, nW = R.active.length, W = 960, m = { t: 66, l: 150, r: 12, b: 30 }, rh = 7.4, H = m.t + rows.length * rh + m.b;
  const svg = d3.select("#f-russia").attr("viewBox", `0 0 ${W} ${H}`);
  const t0 = new Date(R.start + "T00:00:00"), x = d3.scaleTime().domain([t0, d3.timeWeek.offset(t0, nW)]).range([m.l, W - m.r]), cw = (W - m.l - m.r) / nW;
  const ya = d3.scaleLinear().domain([0, rows.length]).range([0, 44]);
  svg.append("g").selectAll("rect").data(R.active).join("rect").attr("x", (v, k) => m.l + k * cw).attr("width", Math.max(.8, cw - .3))
    .attr("y", v => m.t - 8 - ya(v)).attr("height", v => ya(v)).attr("fill", v => v >= 50 ? "var(--c2)" : "var(--ghost)");
  svg.append("text").attr("x", m.l - 8).attr("y", m.t - 30).attr("text-anchor", "end").style("font-size", "10px").text("regions publishing");
  const cs = d3.scaleLog().domain([1, 5]).clamp(true);
  const g = svg.append("g");
  rows.forEach((r, i) => {
    g.append("g").selectAll("rect").data(r.weeks.map((v, k) => [v, k]).filter(p => p[0])).join("rect")
      .attr("x", p => m.l + p[1] * cw).attr("y", m.t + i * rh).attr("width", Math.max(1, cw)).attr("height", rh - .8).attr("fill", p => seq(.18 + .82 * cs(p[0])));
    g.append("text").attr("x", m.l - 6).attr("y", m.t + i * rh + rh - 1.2).attr("text-anchor", "end").style("font-size", "6.6px").text(r.region);
  });
  svg.append("g").attr("transform", `translate(0,${m.t + rows.length * rh + 4})`).call(d3.axisBottom(x).ticks(d3.timeYear.every(1)).tickFormat(d3.timeFormat("%Y")))
    .call(a => a.select(".domain").remove()).call(a => a.selectAll("line").attr("stroke", "var(--rule)"));
  svg.append("rect").attr("x", m.l).attr("y", m.t - 56).attr("width", W - m.l - m.r).attr("height", rows.length * rh + 56).attr("fill", "transparent")
    .on("pointermove", ev => { const [px, py] = d3.pointer(ev); const k = Math.floor((px - m.l) / cw), i = Math.floor((py - m.t) / rh);
      const wk = d3.timeFormat("%-d %b %Y")(d3.timeWeek.offset(t0, k));
      if (k < 0 || k >= nW) return hideTip();
      showTip(ev, i >= 0 && i < rows.length ? `<b>${rows[i].region}</b>, week of ${wk}<br>published on ${rows[i].weeks[k]} day${rows[i].weeks[k] === 1 ? "" : "s"}<br><span class="m">${R.active[k]} of ${rows.length} regions published that week</span>`
        : `<b>Week of ${wk}</b><br>${R.active[k]} of ${rows.length} regions published law`); })
    .on("pointerleave", hideTip);
}

// 10. Copied ordinances between municipalities
{
  const K = DATA3.copy, S = 860;
  if (K && K.nodes.length) {
    const tc = new Map(K.themes.map((t, i) => [t, ["--c1", "--c2", "--c3", "--c4"][i] || "--ghost"]));
    document.getElementById("lg-copies").innerHTML = K.themes.map(t => `<span><i style="width:16px;height:3px;border-radius:2px;background:var(${tc.get(t)})"></i>${t}</span>`).join("")
      + `<span><i style="background:var(--ink)"></i>town (size: articles shared)</span>`;
    const svg = d3.select("#f-copies").attr("viewBox", `0 0 ${S} ${S}`);
    const nodes = K.nodes.map(n => ({ ...n, name: n.name.replace(/ \(city\)$/, "") })), links = K.links.map(l => ({ source: l[0], target: l[1], n: l[2], theme: l[3] }));
    const wmax = d3.max(links, l => l.n), rr = d3.scaleSqrt().domain([0, d3.max(nodes, n => n.shared)]).range([3, 13]);
    // Seeded start positions, so the layout is the same on every load
    const rnd = d3.randomLcg(7); nodes.forEach(n => { n.x = S / 2 + (rnd() - .5) * 400; n.y = S / 2 + (rnd() - .5) * 400; });
    const sim = d3.forceSimulation(nodes).randomSource(d3.randomLcg(11))
      .force("link", d3.forceLink(links).id(d => d.id).distance(l => 120 - 70 * Math.min(1, l.n / 15)).strength(l => .08 + .4 * Math.min(1, l.n / 10)))
      .force("charge", d3.forceManyBody().strength(-150)).force("collide", d3.forceCollide(d => rr(d.shared) + 5))
      .force("x", d3.forceX(S / 2).strength(.045)).force("y", d3.forceY(S / 2).strength(.045)).stop();
    for (let i = 0; i < 500; i++) sim.tick();
    // Fit the finished layout to the plot
    const [x0, x1] = d3.extent(nodes, n => n.x), [y0, y1] = d3.extent(nodes, n => n.y), k = Math.min((S - 120) / (x1 - x0), (S - 80) / (y1 - y0));
    nodes.forEach(n => { n.x = S / 2 + (n.x - (x0 + x1) / 2) * k; n.y = S / 2 + (n.y - (y0 + y1) / 2) * k; });
    const lk = svg.append("g").selectAll("line").data(links).join("line").attr("x1", l => l.source.x).attr("y1", l => l.source.y).attr("x2", l => l.target.x).attr("y2", l => l.target.y)
      .attr("stroke", l => `var(${tc.get(l.theme)})`).attr("stroke-opacity", l => .35 + .55 * l.n / wmax).attr("stroke-width", l => .8 + 3.6 * Math.sqrt(l.n / wmax));
    const nd = svg.append("g").selectAll("circle").data(nodes).join("circle").attr("cx", n => n.x).attr("cy", n => n.y).attr("r", n => rr(n.shared))
      .attr("fill", "var(--ink)").attr("fill-opacity", .85).attr("stroke", "var(--plate)").attr("stroke-width", 1.5);
    // Label the busiest towns, skipping any label that would overlap one already placed
    const boxes = [], keep = [];
    for (const n of [...nodes].sort((a, b) => b.shared - a.shared).slice(0, 22)) {
      const w = n.name.length * 6.4 + 6, b = [n.x - w / 2, n.y - rr(n.shared) - 16, n.x + w / 2, n.y - rr(n.shared) - 2];
      if (boxes.some(o => b[0] < o[2] && b[2] > o[0] && b[1] < o[3] && b[3] > o[1])) continue;
      boxes.push(b); keep.push(n);
    }
    svg.append("g").attr("pointer-events", "none").selectAll("text").data(keep).join("text").attr("class", "lbl halo")
      .attr("x", n => n.x).attr("y", n => n.y - rr(n.shared) - 5).attr("text-anchor", "middle").style("font-size", "10.5px").text(n => n.name);
    nd.on("pointermove", (ev, n) => { lk.attr("stroke-opacity", l => l.source === n || l.target === n ? .9 : .05);
        const ties = links.filter(l => l.source === n || l.target === n).sort((a, b) => b.n - a.n).slice(0, 4).map(l => `${(l.source === n ? l.target : l.source).name} (${l.n})`);
        showTip(ev, `<b>${n.name}</b> · ${n.group}<br>${n.shared} articles shared word for word with another town<br><span class="m">most with: ${ties.join(", ")}</span>`); })
      .on("pointerleave", () => { lk.attr("stroke-opacity", l => .35 + .55 * l.n / wmax); hideTip(); });
  }
}
