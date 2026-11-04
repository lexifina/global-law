
// ---- Part four ----
// 19. The Fiscal Code's notice rule on a time spiral: one turn a year, each change a dot at its in-force day with a tail back to publication
{
  const S = DATA.spiral, COL = { Legea: "--c1", OUG: "--c2", OG: "--c4" }, NEED = { Legea: 182, OUG: 15, OG: 15 };
  const W = 960, H = 780, cx = 384, cy = 392, R0 = 44, gap = 29.5;
  const svg = d3.select("#f-spiral").attr("viewBox", `0 0 ${W} ${H}`);
  const tOf = s => { const d = new Date(s + "T12:00:00"), y = d.getFullYear(), a = new Date(y, 0, 1), b = new Date(y + 1, 0, 1); return y + (d - a) / (b - a); };
  const pt = (t, dr = 0) => { const a = 2 * Math.PI * (t - Math.floor(t)) - Math.PI / 2, r = R0 + (t - 2016) * gap + dr; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; };
  const line = d3.line().curve(d3.curveCatmullRom);
  // Guide: the spiral itself, month spokes, month names outside, year labels on the 1 January spoke
  d3.range(12).forEach(mo => { const a = 2 * Math.PI * mo / 12 - Math.PI / 2, r1 = R0 + 11 * gap + 8;
    svg.append("line").attr("x1", cx + (R0 - 10) * Math.cos(a)).attr("y1", cy + (R0 - 10) * Math.sin(a)).attr("x2", cx + r1 * Math.cos(a)).attr("y2", cy + r1 * Math.sin(a))
      .attr("stroke", mo ? "var(--rule)" : "var(--muted)").attr("stroke-width", mo ? .7 : 1.1).attr("stroke-dasharray", mo ? "2 3" : null);
    const am = a + Math.PI / 12;
    svg.append("text").attr("x", cx + (r1 + 12) * Math.cos(am)).attr("y", cy + (r1 + 12) * Math.sin(am) + 4).attr("text-anchor", "middle").style("font-size", "10.5px").attr("fill", "var(--muted)").text(d3.timeFormat("%b")(new Date(2020, mo, 1))); });
  svg.append("path").attr("d", line(d3.range(2016, 2027.001, 1 / 120).map(t => pt(t)))).attr("fill", "none").attr("stroke", "var(--ghost)").attr("stroke-width", .8);
  d3.range(2016, 2027).forEach(y => { const [x, yy] = pt(y); svg.append("text").attr("x", x - 5).attr("y", yy + 3.5).attr("text-anchor", "end").style("font-size", "9.5px").style("font-variant-numeric", "tabular-nums").attr("fill", "var(--muted)").text(y); });
  svg.append("text").attr("x", cx + 6).attr("y", cy - R0 - 11 * gap - 16).style("font-size", "10.5px").style("font-weight", 600).text("1 January");
  // Tails (notice period) then dots (in force), dots on the same day stacked outward
  const g = svg.append("g"), seen = {};
  const ok = s => s[3] >= NEED[s[0]];
  S.forEach(s => { const t0 = tOf(s[1]), t1 = tOf(s[2]);
    if (t1 - t0 > 1 / 365) g.append("path").attr("d", line(d3.range(t0, t1, 1 / 365).concat([t1]).map(t => pt(t)))).attr("fill", "none").attr("stroke", `var(${COL[s[0]]})`).attr("stroke-width", 1.8).attr("stroke-opacity", .5).attr("stroke-linecap", "round"); });
  S.forEach(s => { const n = (seen[s[2]] = (seen[s[2]] || 0) + 1) - 1, [x, y] = pt(tOf(s[2]), Math.min(n, 6) * 3.6);
    g.append("circle").attr("cx", x).attr("cy", y).attr("r", 3.3).attr("fill", ok(s) ? `var(${COL[s[0]]})` : "var(--plate)").attr("stroke", `var(${COL[s[0]]})`).attr("stroke-width", 1.5)
      .on("pointermove", ev => showTip(ev, `<b>${esc(s[4])}</b><br>published ${fmtDate(new Date(s[1]))}, in force ${fmtDate(new Date(s[2]))}<br>${s[3]} day${s[3] === 1 ? "" : "s"} of notice; art. 4 asks ${s[0] === "Legea" ? "six months of a law" : "15 days of an ordinance"}`))
      .on("pointerleave", hideTip); });
  // Annotations: the longest notice, and the ordinance that rewrote art. 4 itself
  const ann = (date, tx, ty, lines, anchor = "start") => { const [x, y] = pt(tOf(date)), g2 = svg.append("g"), dx = tx - x, dy = ty - y;
    g2.append("line").attr("x1", x).attr("y1", y).attr("x2", tx).attr("y2", ty).attr("stroke", "var(--muted)").attr("stroke-width", .8);
    lines.forEach((t, i) => g2.append("text").attr("x", x + dx + (anchor === "start" ? 4 : -4)).attr("y", y + dy + 4 + i * 12.5).attr("text-anchor", anchor).style("font-size", "10.5px").style("fill", i ? "var(--muted)" : "var(--ink)").text(t)); };
  ann("2024-01-01", 640, 30, ["Legea 309/2022: 410 days' notice,", "the longest"]);
  ann("2023-09-20", 10, 735, ["OUG 74/2023 adds an exception to art. 4,", "in force the day it is published"]);
  // Right panel: one square per change, filled when the change had the notice art. 4 asks for
  const P = [["Legea", "Changes made by law", "6 months' notice asked"], ["ORD", "Changes made by ordinance", "15 days' notice asked"]];
  let py = 150; P.forEach(([k, title, rule]) => {
    const L = S.filter(s => k === "ORD" ? s[0] !== "Legea" : s[0] === k), met = L.filter(ok).length, cols = 12, q = 10.5, x0 = 786;
    svg.append("text").attr("x", x0).attr("y", py).attr("class", "ser").style("font-size", "13px").text(title);
    svg.append("text").attr("x", x0).attr("y", py + 15).style("font-size", "10.5px").attr("fill", "var(--muted)").text(rule);
    L.slice().sort((a, b) => ok(b) - ok(a)).forEach((s, i) => svg.append("rect").attr("x", x0 + (i % cols) * q).attr("y", py + 26 + Math.floor(i / cols) * q).attr("width", q - 2).attr("height", q - 2).attr("rx", 1.5)
      .attr("fill", ok(s) ? `var(${COL[s[0]]})` : "var(--plate)").attr("stroke", `var(${COL[s[0]]})`).attr("stroke-width", 1));
    const rows = Math.ceil(L.length / cols);
    svg.append("text").attr("x", x0).attr("y", py + 26 + rows * q + 18).style("font-size", "20px").style("font-weight", 600).style("font-variant-numeric", "tabular-nums").text(`${met} of ${L.length}`);
    svg.append("text").attr("x", x0).attr("y", py + 26 + rows * q + 33).style("font-size", "10.5px").attr("fill", "var(--muted)").text("had that notice");
    py += 26 + rows * q + 92; });
  legend("lg-spiral", [["law", "--c1"], ["emergency ordinance", "--c2"], ["ordinance", "--c4"]]);
}

// 20. Every act in the corpus as a seed in a sunflower, in order of the day it took effect, oldest at the centre
{
  const SD = DATA.seeds, code = SD.code, N = code.length, W = 960, H = 760, cx = 366, cy = 378, R = 352, c = R / Math.sqrt(N), GA = Math.PI * (3 - Math.sqrt(5));
  const KC = ["--c1", "--c2", "--c4", "--c3", "--ink"], KN = ["law", "emergency ordinance", "ordinance", "government decision", "code or constitution"], SN = ["in force", "only amends other acts", "repealed or withdrawn"];
  const svg = d3.select("#f-seeds").attr("viewBox", `0 0 ${W} ${H}`);
  const YB = Object.entries(SD.years).map(([y, i]) => [+y, i]);
  const yearOf = i => { let y = null; YB.forEach(([yy, ii]) => { if (ii <= i) y = yy; }); return y; };
  const seeds = d3.range(N).map(i => { const v = code.charCodeAt(i), n = v <= 57 ? v - 48 : v - 87, r = c * Math.sqrt(i + .5), a = i * GA, ver = SD.ver[i] || 1;
    return { i, k: Math.floor(n / 3), s: n % 3, ver, x: cx + r * Math.cos(a), y: cy + r * Math.sin(a), r: Math.min(7, 1.5 + .5 * Math.sqrt(ver - 1)) }; });
  const g = svg.append("g");
  g.selectAll("circle").data(seeds.slice().sort((p, q) => (p.s === 1) - (q.s === 1) || p.ver - q.ver).reverse().reverse().sort((p, q) => (q.s === 1) - (p.s === 1) || p.ver - q.ver)).join("circle")
    .attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r)
    .attr("fill", d => d.s === 2 ? "none" : `var(${KC[d.k]})`).attr("fill-opacity", d => d.s === 1 ? .22 : .92)
    .attr("stroke", d => d.s === 2 ? "var(--ink)" : d.ver > 20 ? "var(--plate)" : "none").attr("stroke-width", d => d.s === 2 ? .9 : .6);
  // Year rings where each year's first act falls
  [2007, 2014, 2020, 2025].forEach(y => { const rr = c * Math.sqrt(SD.years[y]);
    svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", rr).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-opacity", .85).attr("stroke-width", 1.3).attr("stroke-dasharray", "4 3").style("pointer-events", "none");
    svg.append("text").attr("x", cx).attr("y", cy - rr - 3).attr("text-anchor", "middle").style("font-size", "11px").style("font-weight", 600).style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).text(y); });
  // The three acts with the most versions
  const call = [[-1, -1], [1, -1], [-1, 1]];
  SD.top.forEach(([i, name, v], j) => { const d = seeds[i], [sx, sy] = call[j], tx = j === 1 ? W - 228 : 22, ty = j === 2 ? H - 40 : 30 + j * 0;
    svg.append("path").attr("d", `M${d.x},${d.y}L${tx + (j === 1 ? -6 : 150)},${ty - 4}`).attr("stroke", "var(--muted)").attr("stroke-width", .8).attr("fill", "none");
    svg.append("circle").attr("cx", d.x).attr("cy", d.y).attr("r", d.r + 2.5).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", 1.2);
    svg.append("text").attr("x", tx).attr("y", ty - 8).style("font-size", "11px").style("font-weight", 600).text(name);
    svg.append("text").attr("x", tx).attr("y", ty + 5).style("font-size", "10.5px").attr("fill", "var(--muted)").text(`${v} versions, the ${["most", "second most", "third most"][j]}`); });
  // Right panel: each kind's acts split by status, as a bar
  const px = 752, pw = 190; let py = 168;
  svg.append("text").attr("x", px).attr("y", py - 34).attr("class", "ser").style("font-size", "13px").text("Each kind of act, by status");
  [0, 1, 2, 3].forEach(k => { const S = [0, 1, 2].map(s => seeds.filter(d => d.k === k && d.s === s).length), tot = d3.sum(S), am = seeds.filter(d => d.k === k && d.ver > 1).length;
    svg.append("text").attr("x", px).attr("y", py).style("font-size", "11.5px").style("font-weight", 600).text(`${KN[k][0].toUpperCase() + KN[k].slice(1)}s · ${fmt(tot)}`);
    let x = px; S.forEach((v, s) => { const w = pw * v / tot; svg.append("rect").attr("x", x).attr("y", py + 7).attr("width", Math.max(0, w - (s < 2 ? 1 : 0))).attr("height", 11).attr("rx", 1.5)
      .attr("fill", s === 2 ? "var(--ink)" : `var(${KC[k]})`).attr("fill-opacity", s === 1 ? .22 : .92); x += w; });
    svg.append("text").attr("x", px).attr("y", py + 33).style("font-size", "10.5px").attr("fill", "var(--muted)").text(`${Math.round(100 * S[0] / tot)}% in force · ${Math.round(100 * am / tot)}% amended since`);
    py += 64; });
  // Hover: nearest seed
  const qt = d3.quadtree(seeds, d => d.x, d => d.y);
  svg.append("rect").attr("width", px - 20).attr("height", H).attr("fill", "transparent").on("pointermove", function (ev) {
    const [mx, my] = d3.pointer(ev, this), d = qt.find(mx, my, 10); if (!d) return hideTip(); const y = yearOf(d.i);
    showTip(ev, `<b>${KN[d.k]}</b>, ${y ? "in force from " + y : "in force before 1990"}<br>${SN[d.s]}${d.ver > 1 ? ` · ${d.ver} versions` : ""}`); }).on("pointerleave", hideTip);
  document.getElementById("lg-seeds").innerHTML = KN.slice(0, 4).map((n, k) => `<span><i style="background:var(${KC[k]})"></i>${n}</span>`).join("") +
    `<span><i style="background:var(--ghost);opacity:.5"></i>faded: only amends other acts</span><span><i style="border:1.2px solid var(--ink);background:transparent"></i>repealed or withdrawn</span><span>larger: more versions</span>`;
}

// 21. How far back amendments reach: an arc from the year the amended act took effect to the year of the change, Parliament above, government below
{
  const AR = DATA.arcs, W = 960, H = 640, y0 = 330, m = { l: 34, r: 20 };
  const svg = d3.select("#f-arcs").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear().domain([1989, 2026]).range([m.l, W - m.r]), k = (y0 - 30) / ((x(2026) - x(1989)) / 2);
  const SIDE = [["Parliament's laws", "--c1", -1], ["The government's ordinances and decisions", "--c2", 1]];
  const hot = d => d[0] < 2007 && d[1] >= 2020;
  svg.append("rect").attr("x", x(2007)).attr("width", x(2026) - x(2007)).attr("y", y0 - .5).attr("height", 1).attr("fill", "var(--ink)");
  svg.append("line").attr("x1", x(1989)).attr("x2", x(2026)).attr("y1", y0).attr("y2", y0).attr("stroke", "var(--ink)").attr("stroke-width", .8);
  const g = svg.append("g").attr("fill", "none");
  const arc = d => { const [a, b, sd] = d, rx = (x(b) - x(a)) / 2, ry = rx * k, dir = SIDE[sd][2]; return `M${x(a)},${y0}A${rx},${ry} 0 0 ${dir < 0 ? 1 : 0} ${x(b)},${y0}`; };
  const paths = g.selectAll("path").data(AR.filter(d => d[1] > d[0]).sort((p, q) => hot(p) - hot(q))).join("path").attr("d", arc)
    .attr("stroke", d => `var(${SIDE[d[2]][1]})`).attr("stroke-width", d => .5 + Math.sqrt(d[3]) * .42).attr("stroke-opacity", d => hot(d) ? .75 : .08).attr("stroke-linecap", "round")
    .on("pointermove", function (ev, d) { paths.attr("stroke-opacity", o => o === d ? .95 : .08); showTip(ev, `<b>${d[0] === 1989 ? "Acts from before 1990" : "Acts in force from " + d[0]}</b>, changed in ${d[1]}<br>${fmt(d[3])} change${d[3] > 1 ? "s" : ""} by ${SIDE[d[2]][0].toLowerCase().replace("the ", "")}, ${d[1] - d[0]} years on`); })
    .on("pointerleave", () => { paths.attr("stroke-opacity", d => hot(d) ? .75 : .08); hideTip(); });
  // Same-year changes as dots on the axis
  const same = d3.rollup(AR.filter(d => d[0] === d[1]), v => d3.sum(v, d => d[3]), d => d[0]);
  // Axis labels and the 2007 rule
  d3.range(1990, 2027, 5).forEach(yr => svg.append("text").attr("x", x(yr)).attr("y", y0 + 4).attr("dy", ".35em").attr("text-anchor", "middle").style("font-size", "10px").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 4).attr("fill", "var(--muted)").text(yr));
  svg.append("text").attr("x", x(1989)).attr("y", y0 - 8).attr("text-anchor", "middle").style("font-size", "9.5px").attr("fill", "var(--muted)").text("earlier");
  svg.append("line").attr("x1", x(2007)).attr("x2", x(2007)).attr("y1", 18).attr("y2", H - 18).attr("stroke", "var(--muted)").attr("stroke-dasharray", "3 3");
  svg.append("text").attr("x", x(2007) + 5).attr("y", 26).style("font-size", "10.5px").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).attr("fill", "var(--muted)").text("1 January 2007: Romania joins the EU");
  svg.append("text").attr("x", x(2007) + 5).attr("y", 39).style("font-size", "10.5px").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).attr("fill", "var(--muted)").text("(bright arcs: law from before it, changed since 2020)");
  SIDE.forEach(([n, c, dir], i) => svg.append("text").attr("x", W - m.r).attr("y", y0 + dir * (y0 - 40) + (dir < 0 ? 0 : 6)).attr("text-anchor", "end").attr("class", "ser").style("font-size", "13px").style("fill", `var(${c})`).text(n));
  // The oldest acts still being changed
  const L = ["Still changed since 2020:", "Legea 61/1991, public order offences · 10", "Legea 10/1995, quality in construction · 10", "Legea 18/1991, the land law · 9", "Legea 107/1996, the water law · 9", "Legea 7/1996, the cadastre law · 8", "Legea 31/1990, the companies law · 8"];
  L.forEach((t, i) => svg.append("text").attr("x", m.l).attr("y", 26 + i * 13.5).style("font-size", i ? "10.5px" : "11px").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).style("font-weight", i ? 400 : 600).style("fill", i ? "var(--muted)" : "var(--ink)").text(t));
}

// 22. Who amends whom: a directed chord wheel from the kind of the amending act to the kind of the amended act
{
  const M = DATA.chord, N = ["Laws", "Emergency ordinances", "Ordinances", "Government decisions", "Constitutional Court", "Old codes, decree-laws"], C = ["--c1", "--c2", "--c4", "--c3", "--ink", "--ghost"];
  const W = 960, H = 660, cx = 338, cy = 334, R = 258, r0 = R - 14;
  const svg = d3.select("#f-chord").attr("viewBox", `0 0 ${W} ${H}`), g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  const ch = d3.chordDirected().padAngle(.035).sortSubgroups(d3.descending).sortChords(d3.descending)(M);
  const rib = d3.ribbonArrow().radius(r0 - 2).padAngle(.004).headRadius(10);
  const ribs = g.append("g").selectAll("path").data(ch).join("path").attr("d", rib).attr("fill", d => `var(${C[d.source.index]})`).attr("fill-opacity", .62).attr("stroke", "var(--plate)").attr("stroke-width", .5)
    .on("pointermove", function (ev, d) { ribs.attr("fill-opacity", o => o === d ? .9 : .12); showTip(ev, `<b>${N[d.source.index]} → ${N[d.target.index].toLowerCase()}</b><br>${fmt(d.source.value)} changes`); })
    .on("pointerleave", () => { ribs.attr("fill-opacity", .62); hideTip(); });
  const arc = d3.arc().innerRadius(r0).outerRadius(R);
  const grp = g.append("g").selectAll("g").data(ch.groups).join("g");
  grp.append("path").attr("d", arc).attr("fill", d => `var(${C[d.index]})`).attr("stroke", "var(--plate)")
    .on("pointermove", (ev, d) => { ribs.attr("fill-opacity", o => o.source.index === d.index || o.target.index === d.index ? .85 : .08);
      const out = d3.sum(M[d.index]), inn = d3.sum(M, row => row[d.index]); showTip(ev, `<b>${N[d.index]}</b><br>made ${fmt(out)} changes · received ${fmt(inn)}`); })
    .on("pointerleave", () => { ribs.attr("fill-opacity", .62); hideTip(); });
  grp.each(function (d) { const a = (d.startAngle + d.endAngle) / 2, big = d.endAngle - d.startAngle > .12, right = a < Math.PI;
    let lx = Math.sin(a) * (R + 12), ly = -Math.cos(a) * (R + 12);
    if (!big) { const mx = Math.sin(a) * (R + 2), my = -Math.cos(a) * (R + 2); lx = -70; ly = -R - (d.index === 4 ? 40 : 24);
      d3.select(this).append("path").attr("d", `M${mx},${my}L${mx},${ly + 4}L${lx + 4},${ly + 4}`).attr("fill", "none").attr("stroke", "var(--muted)").attr("stroke-width", .7); }
    const t = d3.select(this).append("text").attr("x", lx).attr("y", ly).attr("dy", ".35em").attr("text-anchor", right && big ? "start" : "end").style("font-size", big ? "12px" : "10.5px").style("font-weight", big ? 600 : 400).text(N[d.index]);
    if (!big) t.attr("fill", "var(--muted)"); });
  // Right column: three readings of the wheel
  const col = j => d3.sum(M, row => row[j]), notes = [
    [`${Math.round(100 * M[3][3] / col(3))}%`, "of changes to government decisions", "come from other government decisions"],
    [`${Math.round(100 * (M[1][0] + M[2][0] + M[3][0]) / col(0))}%`, "of changes to Parliament's laws come", `from the government, ${fmt(M[1][0] + M[2][0] + M[3][0])} of ${fmt(col(0))}`],
    [fmt(M[0][1]), "changes by laws to emergency ordinances,", `against ${fmt(M[1][0])} the other way`]];
  notes.forEach(([big, a, b], i) => { const y = 150 + i * 118;
    svg.append("text").attr("x", 690).attr("y", y).style("font-size", "30px").style("font-weight", 600).style("font-variant-numeric", "tabular-nums").text(big);
    svg.append("text").attr("x", 690).attr("y", y + 22).style("font-size", "11.5px").text(a);
    svg.append("text").attr("x", 690).attr("y", y + 37).style("font-size", "11.5px").attr("fill", "var(--muted)").text(b); });
}

// 23. A ternary triangle: each act changed ten or more times, placed by the shares of its changes made by law, emergency ordinance and ordinance
{
  const T = DATA.tri, W = 960, H = 610, side = 580, hgt = side * Math.sqrt(3) / 2;
  const P = [330, 40], U = [P[0] - side / 2, P[1] + hgt], G = [P[0] + side / 2, P[1] + hgt];
  const svg = d3.select("#f-tri").attr("viewBox", `0 0 ${W} ${H}`);
  const at = (a, b, c) => { const s = a + b + c; return [(a * P[0] + b * U[0] + c * G[0]) / s, (a * P[1] + b * U[1] + c * G[1]) / s]; };
  const KC = { lege: "--c1", oug: "--c2", og: "--c4" }, KN = { lege: "law", oug: "emergency ordinance", og: "ordinance" };
  // Majority regions: where one route made more than half of the changes
  [[[1, 0, 0], [1, 1, 0], [1, 0, 1], "--c1"], [[0, 1, 0], [1, 1, 0], [0, 1, 1], "--c2"], [[0, 0, 1], [1, 0, 1], [0, 1, 1], "--c4"]]
    .forEach(([a, b, c, col]) => svg.append("path").attr("d", "M" + [a, b, c].map(v => at(...v).join(",")).join("L") + "Z").attr("fill", `var(${col})`).attr("fill-opacity", .07));
  // Grid at every 20%, for each of the three shares
  const grid = svg.append("g").attr("stroke", "var(--rule)").attr("stroke-width", .8);
  [.2, .4, .6, .8].forEach(t => { [[[t, 1 - t, 0], [t, 0, 1 - t]], [[1 - t, t, 0], [0, t, 1 - t]], [[1 - t, 0, t], [0, 1 - t, t]]].forEach(([p, q]) => {
    const [x1, y1] = at(...p), [x2, y2] = at(...q); grid.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2); }); });
  // Share ticks along the edges: law share on the left edge, ordinance share along the base
  [.2, .4, .6, .8].forEach(t => { const [x, y] = at(t, 1 - t, 0); svg.append("text").attr("x", x - 8).attr("y", y + 3).attr("text-anchor", "end").style("font-size", "9.5px").attr("fill", "var(--muted)").text(`${Math.round(t * 100)}% law`);
    const [x2, y2] = at(0, 1 - t, t); svg.append("text").attr("x", x2).attr("y", y2 + 16).attr("text-anchor", "middle").style("font-size", "9.5px").attr("fill", "var(--muted)").text(`${Math.round(t * 100)}% OG`); });
  svg.append("path").attr("d", `M${P}L${U}L${G}Z`).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", 1.1);
  // Corner names
  svg.append("text").attr("x", P[0]).attr("y", P[1] - 12).attr("text-anchor", "middle").attr("class", "ser").style("font-size", "13.5px").style("fill", "var(--c1)").text("All changes by Parliament's laws");
  svg.append("text").attr("x", U[0]).attr("y", U[1] + 36).attr("text-anchor", "start").attr("class", "ser").style("font-size", "13.5px").style("fill", "var(--c2)").text("All by emergency ordinance");
  svg.append("text").attr("x", G[0]).attr("y", U[1] + 36).attr("text-anchor", "end").attr("class", "ser").style("font-size", "13.5px").style("fill", "var(--c4)").text("All by ordinance");
  const [ex, ey] = at(.12, .16, .72);
  svg.append("text").attr("x", ex).attr("y", ey).attr("text-anchor", "middle").style("font-size", "10.5px").attr("fill", "var(--muted)").text("mostly by ordinance: no act");
  // Acts
  const sz = d => Math.min(13, 1.6 + Math.sqrt(d3.sum(d.slice(2))) * .62);
  svg.append("g").selectAll("circle").data(T.slice().sort((a, b) => d3.sum(b.slice(2)) - d3.sum(a.slice(2)))).join("circle")
    .attr("cx", d => at(d[2], d[3], d[4])[0]).attr("cy", d => at(d[2], d[3], d[4])[1]).attr("r", sz)
    .attr("fill", d => `var(${KC[d[1]]})`).attr("fill-opacity", .6).attr("stroke", "var(--plate)").attr("stroke-width", .8)
    .on("pointermove", (ev, d) => showTip(ev, `<b>${esc(d[0])}</b>, ${KN[d[1]] === "law" ? "a law" : "an " + KN[d[1]]}<br>${d3.sum(d.slice(2))} changes: ${d[2]} by law, ${d[3]} by emergency ordinance, ${d[4]} by ordinance`)).on("pointerleave", hideTip);
  // Named acts
  const NAME = { "Codul fiscal": "Fiscal Code", "Legea nr. 95/2006": "Health reform", "Legea nr. 1/2011": "National education", "OUG nr. 195/2002": "Road traffic", "Codul muncii": "Labour Code", "OUG nr. 114/2018": "OUG 114/2018, fiscal measures", "OUG nr. 107/2024": "OUG 107/2024: every change by OUG" };
  const OFF = { "Codul fiscal": [16, -8], "Legea nr. 95/2006": [-26, 34], "Legea nr. 1/2011": [18, 2], "OUG nr. 195/2002": [18, 8], "Codul muncii": [-16, -4], "OUG nr. 114/2018": [14, 4], "OUG nr. 107/2024": [12, -14] };
  T.filter(d => NAME[d[0]]).forEach(d => { const [x, y] = at(d[2], d[3], d[4]), [dx, dy] = OFF[d[0]];
    svg.append("circle").attr("cx", x).attr("cy", y).attr("r", sz(d) + 2).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", 1.1).style("pointer-events", "none");
    svg.append("text").attr("x", x + dx).attr("y", y + dy).attr("text-anchor", dx < 0 ? "end" : "start").style("font-size", "10.5px").style("font-weight", 600).style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).style("pointer-events", "none").text(NAME[d[0]]); });
  // Right column: each kind's average mix (the + marks in the triangle) and how many of its acts each route changed most
  let py = 110; ["lege", "oug", "og"].forEach(k => { const X = T.filter(d => d[1] === k), share = (d, j) => d[2 + j] / d3.sum(d.slice(2));
    const mean = [0, 1, 2].map(j => d3.mean(X, d => share(d, j))), maj = [0, 1, 2].map(j => X.filter(d => share(d, j) > .5).length), [mx, my] = at(...mean);
    svg.append("path").attr("d", `M${mx - 8},${my}L${mx + 8},${my}M${mx},${my - 8}L${mx},${my + 8}`).attr("stroke", "var(--plate)").attr("stroke-width", 5).style("pointer-events", "none");
    svg.append("path").attr("d", `M${mx - 7},${my}L${mx + 7},${my}M${mx},${my - 7}L${mx},${my + 7}`).attr("stroke", `var(${KC[k]})`).attr("stroke-width", 2.4).style("pointer-events", "none");
    svg.append("text").attr("x", 690).attr("y", py).style("font-size", "12.5px").style("font-weight", 600).style("fill", `var(${KC[k]})`).text(`${X.length} ${KN[k]}s`);
    svg.append("text").attr("x", 690).attr("y", py + 17).style("font-size", "10.5px").text(`average mix: ${Math.round(100 * mean[0])}% law, ${Math.round(100 * mean[1])}% OUG, ${Math.round(100 * mean[2])}% OG`);
    svg.append("text").attr("x", 690).attr("y", py + 32).style("font-size", "10.5px").attr("fill", "var(--muted)").text(`${maj[0]} changed mostly by law`);
    svg.append("text").attr("x", 690).attr("y", py + 46).style("font-size", "10.5px").attr("fill", "var(--muted)").text(`${maj[1]} mostly by emergency ordinance`);
    py += 96; });
  svg.append("text").attr("x", 690).attr("y", py + 4).style("font-size", "10.5px").attr("fill", "var(--muted)").text("+ marks each kind's average mix");
  legend("lg-tri", [["the act is a law", "--c1"], ["an emergency ordinance", "--c2"], ["an ordinance", "--c4"]]);
}
