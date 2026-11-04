
// A. The Constitution's 2003 revision as a wheel: 1991's 152 articles on the inner ring, 2003's 156 on the outer, each article joined to its successor
{
  const K = DATA.const, W = 960, H = 590, cx = 480, cy = 294, i0 = 164, i1 = 178, o0 = 226, o1 = 242;
  document.documentElement.style.setProperty("--lr", "color-mix(in oklab, var(--c1) 40%, var(--ghost))");
  const svg = d3.select("#f-const").attr("viewBox", `0 0 ${W} ${H}`), g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  const nO = K.old.length, nN = K.new.length, aO = n => 2 * Math.PI * (n - .5) / nO, aN = n => 2 * Math.PI * (n - .5) / nN;
  const P = (a, r) => [r * Math.sin(a), -r * Math.cos(a)];
  const CL = [["kept word for word", "--ghost"], ["lightly reworded", "--lr"], ["reworded", "--c1"], ["rewritten", "--c4"]];
  const cls = r => r >= .995 ? 0 : r >= .85 ? 1 : r >= .5 ? 2 : 3;
  const T91 = ["General principles", "Rights, freedoms and duties", "Public authorities", "Economy and public finance", "Constitutional Court", "Revision", "Final provisions"];
  const T03 = ["General principles", "Rights, freedoms and duties", "Public authorities", "Economy and public finance", "Constitutional Court", "Euro-Atlantic integration", "Revision", "Final and transitional provisions"];
  const titleOf = (n, list) => (list === "old" ? K.old : K.new)[n - 1][1];
  // Links first, so the rings sit on top
  const born = new Set(K.born), gone = new Set(K.gone);
  const link = ([i, j]) => { const [x0, y0] = P(aO(i), i1), [x1, y1] = P(aO(i), (i1 + o0) / 2), [x2, y2] = P(aN(j), (i1 + o0) / 2), [x3, y3] = P(aN(j), o0); return `M${x0},${y0}C${x1},${y1} ${x2},${y2} ${x3},${y3}`; };
  const L = g.append("g").attr("fill", "none").selectAll("path").data(K.links.slice().sort((a, b) => cls(a[2]) - cls(b[2]))).join("path").attr("d", link)
    .attr("stroke", d => `var(${CL[cls(d[2])][1]})`).attr("stroke-width", d => cls(d[2]) ? 2.2 : 1.4).attr("stroke-opacity", d => cls(d[2]) === 1 ? 1 : .9)
    .on("pointermove", function (ev, d) { L.attr("stroke-opacity", o => o === d ? 1 : .15); showTip(ev, `<b>${esc(titleOf(d[1], "new"))}</b><br>art. ${d[0]} in 1991 → art. ${d[1]} in 2003<br>${CL[cls(d[2])][0]}, ${Math.round(100 * d[2])}% of the text the same`); })
    .on("pointerleave", () => { L.attr("stroke-opacity", d => cls(d[2]) === 1 ? 1 : .9); hideTip(); });
  // Rings: one cell per article, shaded by Title; new 2003 articles in red, removed 1991 articles hollow
  const cell = (a0, a1, r0, r1) => d3.arc()({ innerRadius: r0, outerRadius: r1, startAngle: a0, endAngle: a1 });
  K.old.forEach(([n, h, t]) => g.append("path").attr("d", cell(aO(n) - Math.PI / nO + .002, aO(n) + Math.PI / nO - .002, i0, i1))
    .attr("fill", gone.has(n) ? "var(--plate)" : t % 2 ? "var(--ghost)" : "var(--muted)").attr("fill-opacity", gone.has(n) ? 1 : .8).attr("stroke", gone.has(n) ? "var(--c2)" : "none").attr("stroke-width", 1.2)
    .on("pointermove", ev => showTip(ev, `<b>1991, art. ${n}</b> · ${esc(h)}${gone.has(n) ? "<br>removed in 2003" : ""}`)).on("pointerleave", hideTip));
  K.new.forEach(([n, h, t]) => g.append("path").attr("d", cell(aN(n) - Math.PI / nN + .002, aN(n) + Math.PI / nN - .002, o0, o1))
    .attr("fill", born.has(n) ? "var(--c2)" : t % 2 ? "var(--ghost)" : "var(--muted)").attr("fill-opacity", born.has(n) ? 1 : .8)
    .on("pointermove", ev => showTip(ev, `<b>2003, art. ${n}</b> · ${esc(h)}${born.has(n) ? "<br>new in 2003" : ""}`)).on("pointerleave", hideTip));
  // Title numerals: 2003's outside the outer ring, 1991's inside the inner ring
  const ROM = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];
  const span = (rows, t, f) => { const ns = rows.filter(r => r[2] === t).map(r => r[0]); return [f(d3.min(ns)), f(d3.max(ns))]; };
  T03.forEach((nm, t) => { const [a0, a1] = span(K.new, t, aN), [x, y] = P((a0 + a1) / 2, o1 + 11); g.append("text").attr("x", x).attr("y", y).attr("dy", ".35em").attr("text-anchor", "middle").style("font-size", "10px").style("font-weight", 600).style("fill", "var(--ink)").text(ROM[t]); });
  T91.forEach((nm, t) => { const [a0, a1] = span(K.old, t, aO), [x, y] = P((a0 + a1) / 2, i0 - 11); g.append("text").attr("x", x).attr("y", y).attr("dy", ".35em").attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", "var(--muted)").text(ROM[t]); });
  // Callouts in two columns: the new 2003 articles (red) and the removed 1991 ones (ink), each with a leader line to its cell
  const NEWN = { 33: "Access to culture", 35: "A healthy environment", 38: "European Parliament elections", 45: "Economic freedom", 75: "Which Chamber debates first", 96: "Impeaching the President",
    133: "Judicial council: role", 141: "Economic and Social Council", 148: "Joining the European Union", 149: "Joining NATO", 155: "Transitional provisions", 156: "Republishing the Constitution" };
  const GONEN = { 51: "Obeying the Constitution", 70: "Members' opinions", 71: "Members' pay", 75: "Bills between Chambers", 76: "Mediation between Chambers", 132: "Judicial council: members", 151: "Existing institutions", 152: "Future institutions" };
  const items = [...K.born.map(n => ({ a: aN(n), r: o1, t: `${n} ${NEWN[n]}`, c: "var(--c2)", k: "new" })), ...K.gone.map(n => ({ a: aO(n), r: i1, t: `${n} ${GONEN[n]}, 1991`, c: "var(--ink)", k: "gone" }))];
  items.forEach(d => { const [x, y] = P(d.a, d.r); d.x = x; d.y = y; d.side = x >= 0 ? 1 : -1; });
  [1, -1].forEach(side => { const col = items.filter(d => d.side === side).sort((p, q) => p.y - q.y); let last = -Infinity;
    col.forEach(d => { d.ly = Math.max(d.y, last + 15); last = d.ly; });
    const over = last - (H / 2 - 18); if (over > 0) col.forEach(d => d.ly -= over);
    col.forEach(d => { const lx = side * 268;
      g.append("path").attr("d", `M${d.x},${d.y}L${side * (Math.abs(d.x) + 8)},${d.y}L${lx - side * 4},${d.ly}`).attr("fill", "none").attr("stroke", d.c).attr("stroke-width", .7).attr("stroke-opacity", .8);
      g.append("text").attr("x", lx).attr("y", d.ly).attr("dy", ".35em").attr("text-anchor", side > 0 ? "start" : "end").style("font-size", "10px").style("fill", d.c).text(d.t); }); });
  // Centre: the counts
  const c = [0, 1, 2, 3].map(k => K.links.filter(d => cls(d[2]) === k).length), moved = K.links.filter(d => d[0] !== d[1]).length;
  g.append("text").attr("y", -74).attr("text-anchor", "middle").attr("class", "ser").style("font-size", "15px").text("1991 inside · 2003 outside");
  [[c[0], "kept word for word"], [moved, "changed their number"], [K.born.length, "new articles, in red"], [K.gone.length, "removed or merged, hollow"]].forEach(([b, t], k) => {
    g.append("text").attr("x", -12).attr("y", -36 + k * 34).attr("text-anchor", "end").style("font-size", "24px").style("font-weight", 600).style("fill", "var(--ink)").style("font-variant-numeric", "tabular-nums").text(b);
    g.append("text").attr("x", -4).attr("y", -42 + k * 34).style("font-size", "10.5px").style("fill", "var(--muted)").text(t.split(", ")[0]);
    if (t.includes(", ")) g.append("text").attr("x", -4).attr("y", -29 + k * 34).style("font-size", "10.5px").style("fill", "var(--muted)").text(t.split(", ")[1]); });
  legend("lg-const", [...CL, ["new in 2003", "--c2"]], true);
}

// B. The Monitorul Oficial's issue numbers as a nautilus: one curve a year, angle = day of the year, distance from the centre = the issue number reached
{
  const MO = DATA.mo, years = Object.keys(MO).map(Number), W = 960, H = 712, cx = 360, cy = 370, R = 318, top = 1350;
  const svg = d3.select("#f-mo").attr("viewBox", `0 0 ${W} ${H}`), g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  const seq = t => d3.interpolateLab(css("--seq-lo"), css("--seq-hi"))(t), col = y => seq(.12 + .88 * (y - 1991) / 34);
  const P = (doy, n) => { const a = 2 * Math.PI * (doy - 1) / 366, r = R * n / top; return [r * Math.sin(a), -r * Math.cos(a)]; };
  // Guides: issue-number rings and month spokes
  [250, 500, 750, 1000, 1250].forEach(n => { g.append("circle").attr("r", R * n / top).attr("fill", "none").attr("stroke", "var(--rule)").attr("stroke-dasharray", "2 3");
    const [tx, ty] = P(64, n); g.append("text").attr("x", tx + 3).attr("y", ty - 3).style("font-size", "9.5px").style("fill", "var(--muted)").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).text(`no. ${fmt(n)}`); });
  [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335].forEach((d, i) => { const [x, y] = P(d, top * 1.02), [lx, ly] = P(d + 15, top * 1.07);
    g.append("line").attr("x2", x).attr("y2", y).attr("stroke", "var(--rule)").attr("stroke-width", i ? .6 : 1);
    g.append("text").attr("x", lx).attr("y", ly).attr("dy", ".35em").attr("text-anchor", "middle").style("font-size", "10px").style("fill", "var(--muted)").text(d3.timeFormat("%b")(new Date(2021, i, 1))); });
  const line = d3.line().curve(d3.curveMonotoneX);
  const mx = {}; years.forEach(y => { let m = 0; mx[y] = MO[y].map(([d, n]) => [d, m = Math.max(m, n)]); });
  const HI = { 2004: "2004: 1,281, the year EU accession talks closed", 2020: "2020: 1,332", 2024: "2024: 1,334, the most" };
  const paths = g.append("g").attr("fill", "none").selectAll("path").data(years).join("path")
    .attr("d", y => "M0,0L" + mx[y].map(([d, n]) => P(d, n).join(",")).join("L"))
    .attr("stroke", y => HI[y] ? "var(--c2)" : col(y)).attr("stroke-width", y => HI[y] ? 2 : 1.3).attr("stroke-opacity", y => HI[y] ? 1 : .85).attr("stroke-linejoin", "round")
    .on("pointermove", function (ev, y) { paths.attr("stroke-opacity", o => o === y ? 1 : .15); const last = mx[y][mx[y].length - 1]; showTip(ev, `<b>${y}</b><br>issue no. ${fmt(last[1])} reached by ${d3.timeFormat("%-d %B")(new Date(y, 0, last[0]))}`); })
    .on("pointerleave", () => { paths.attr("stroke-opacity", y => HI[y] ? 1 : .85); hideTip(); });
  years.filter(y => HI[y]).forEach(y => { const [d, n] = mx[y][mx[y].length - 1], [x, yy] = P(d, n);
    g.append("circle").attr("cx", x).attr("cy", yy).attr("r", 3).attr("fill", "var(--c2)"); });
  [[2024, -352], [2020, -338], [2004, -324]].forEach(([y, ty]) => { const [d, n] = mx[y][mx[y].length - 1], [x, yy] = P(d, n), tx = 170;
    g.append("path").attr("d", `M${x},${yy}L${x + 14},${ty - 4}L${tx - 4},${ty - 4}`).attr("fill", "none").attr("stroke", "var(--c2)").attr("stroke-width", .7);
    g.append("text").attr("x", tx).attr("y", ty).style("font-size", "10.5px").style("fill", "var(--c2)").text(HI[y]); });
  const [x91, y91] = P(mx[1991][mx[1991].length - 1][0], 267); g.append("text").attr("x", x91 - 8).attr("y", y91 + 4).attr("text-anchor", "end").style("font-size", "10.5px").style("fill", "var(--ink)").text("1991: 267");
  // Right panel: the last issue number of each year as a column
  const x0 = 720, bw = 6.2, base = 330, hS = d3.scaleLinear().domain([0, top]).range([0, 190]);
  svg.append("text").attr("x", x0).attr("y", 112).attr("class", "ser").style("font-size", "13px").text("Issues of Partea I each year");
  svg.append("text").attr("x", x0).attr("y", 127).style("font-size", "10px").style("fill", "var(--muted)").text("the highest issue number seen, 1991–2025");
  years.forEach((y, i) => { const n = d3.max(MO[y], d => d[1]); svg.append("rect").attr("x", x0 + i * bw).attr("y", base - hS(n)).attr("width", bw - 1.2).attr("height", hS(n)).attr("fill", HI[y] ? "var(--c2)" : col(y)); });
  [[1991, "267"], [2004, "1,281"], [2024, "1,334"]].forEach(([y, t]) => svg.append("text").attr("x", x0 + (y - 1991) * bw + bw / 2).attr("y", base - hS(d3.max(MO[y], d => d[1])) - 4).attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", y === 1991 ? "var(--muted)" : "var(--c2)").text(t));
  [1991, 2000, 2010, 2025].forEach(y => svg.append("text").attr("x", x0 + (y - 1991) * bw + bw / 2).attr("y", base + 14).attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", "var(--muted)").text(y));
  document.getElementById("lg-mo").innerHTML = `<span>1991</span><span style="width:140px;height:10px;border-radius:3px;display:inline-block;background:linear-gradient(90deg,${col(1991)},${col(2025)})"></span><span>2025</span><span><i class="bar" style="background:var(--c2)"></i>highlighted years</span>`;
}

// C. Ministries in government decisions: a treemap of portfolios, each split into decisions that move property and all others
{
  const MN = DATA.mins, W = 960, H = 540;
  const svg = d3.select("#f-mins").attr("viewBox", `0 0 ${W} ${H}`);
  const root = d3.hierarchy({ children: MN.map(([n, p, o]) => ({ n, children: [{ n, k: "property", v: p }, { n, k: "other", v: o }] })) }).sum(d => d.v || 0).sort((a, b) => b.value - a.value);
  d3.treemap().size([W, H]).paddingOuter(0).paddingInner(3).paddingTop(d => d.depth === 1 ? 34 : 0).tile(d3.treemapSquarify.ratio(1.2)).round(true)(root);
  const ok = (d, w, h) => d.x1 - d.x0 > w && d.y1 - d.y0 > h;
  root.children.forEach(p => { const g = svg.append("g");
    g.append("rect").attr("x", p.x0).attr("y", p.y0).attr("width", p.x1 - p.x0).attr("height", p.y1 - p.y0).attr("fill", "var(--tint)").attr("rx", 3);
    const prop = p.children.find(c => c.data.k === "property").value, share = Math.round(100 * prop / p.value);
    const w = p.x1 - p.x0 - 12, fs = p.value > 200 ? 12.5 : 10.5, fit = (t, f) => t.length * f * .6 <= w;
    const name = fit(p.data.n, fs) ? p.data.n : fit(p.data.n.split(",")[0], fs) ? p.data.n.split(",")[0] : fit(p.data.n.split(" ")[0], fs) ? p.data.n.split(" ")[0] : "";
    const sub = [`${fmt(p.value)} decisions · ${share}% move property`, `${fmt(p.value)} · ${share}% property`, `${fmt(p.value)} · ${share}%`].find(t => fit(t, 10)) || "";
    if (name) g.append("text").attr("x", p.x0 + 7).attr("y", p.y0 + 14).style("font-size", `${fs}px`).style("font-weight", 600).style("fill", "var(--ink)").text(name);
    if (name && sub) g.append("text").attr("x", p.x0 + 7).attr("y", p.y0 + 27).style("font-size", "10px").style("fill", "var(--muted)").text(sub);
    p.children.forEach(c => g.append("rect").attr("x", c.x0).attr("y", c.y0).attr("width", Math.max(0, c.x1 - c.x0)).attr("height", Math.max(0, c.y1 - c.y0)).attr("rx", 2)
      .attr("fill", c.data.k === "property" ? "var(--c4)" : "var(--c1)").attr("fill-opacity", .85)
      .on("pointermove", ev => showTip(ev, `<b>${esc(p.data.n)}</b><br>${fmt(c.value)} decision${c.value > 1 ? "s" : ""} that ${c.data.k === "property" ? "move land or buildings" : "do something else"}, of ${fmt(p.value)}`)).on("pointerleave", hideTip)); });
  legend("lg-mins", [["moves land or buildings: transfers, administration, public domain", "--c4"], ["everything else", "--c1"]], true);
}

// D. The codes as railway lines: each runs from its first version to its repeal or today, with a station at every version; an old code bends into its successor
{
  const CD = DATA.codes, W = 960, rowH = 27, m = { t: 34, l: 214, r: 118 }, H = m.t + CD.length * rowH + 26, today = "2026-11-03";
  const svg = d3.select("#f-codes").attr("viewBox", `0 0 ${W} ${H}`);
  const yr = s => { const d = new Date(s + "T12:00:00"); return d.getFullYear() + (d - new Date(d.getFullYear(), 0, 1)) / 31557600000; };
  const x = d3.scaleLinear().domain([1860, 1990, 2027]).range([m.l, m.l + 150, W - m.r]);
  const y = i => m.t + i * rowH + rowH / 2;
  // Time axis: the long compressed past, then 1990 onwards
  svg.append("rect").attr("x", x(1860)).attr("width", x(1990) - x(1860)).attr("y", m.t - 6).attr("height", CD.length * rowH + 6).attr("fill", "var(--tint)").attr("rx", 3);
  svg.append("text").attr("x", (x(1860) + x(1990)) / 2).attr("y", m.t - 12).attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", "var(--muted)").text("1860–1990, compressed");
  [1870, 1900, 1950].forEach(t => svg.append("text").attr("x", x(t)).attr("y", H - 8).attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", "var(--muted)").text(t));
  d3.range(1990, 2027, 5).forEach(t => { svg.append("line").attr("x1", x(t)).attr("x2", x(t)).attr("y1", m.t - 6).attr("y2", m.t + CD.length * rowH).attr("stroke", "var(--rule)").attr("stroke-dasharray", "2 3");
    svg.append("text").attr("x", x(t)).attr("y", H - 8).attr("text-anchor", "middle").style("font-size", "9.5px").style("fill", "var(--muted)").text(t); });
  const end = r => r[2].startsWith("repealed") ? r[2].slice(9, 19) : today, NEXT = { 0: 1, 2: 1, 3: 4, 6: 7, 8: 9, 10: 11 };
  // Successor bends, drawn first
  Object.entries(NEXT).forEach(([i, j]) => { i = +i; const x0 = x(yr(end(CD[i]))), x1 = x(yr(CD[j][3][0])), y0 = y(i), y1 = y(j), mx = Math.max(x0, x1) + 14;
    svg.append("path").attr("d", `M${x0},${y0}C${mx},${y0} ${mx},${y1} ${x1},${y1}`).attr("fill", "none").attr("stroke", "var(--c2)").attr("stroke-width", 1.6).attr("stroke-dasharray", "3 2"); });
  CD.forEach(([nm, path, st, vs], i) => { const rep = st.startsWith("repealed"), live = !rep, e = end(CD[i]), c = live ? "var(--c1)" : "var(--muted)";
    const g = svg.append("g");
    g.append("line").attr("x1", x(yr(vs[0]))).attr("x2", x(yr(e))).attr("y1", y(i)).attr("y2", y(i)).attr("stroke", c).attr("stroke-width", 5).attr("stroke-linecap", "round").attr("stroke-opacity", live ? .9 : .55);
    vs.forEach(v => g.append("circle").attr("cx", x(yr(v))).attr("cy", y(i)).attr("r", 2.3).attr("fill", "var(--plate)").attr("stroke", c).attr("stroke-width", 1.1));
    if (rep) g.append("line").attr("x1", x(yr(e))).attr("x2", x(yr(e))).attr("y1", y(i) - 7).attr("y2", y(i) + 7).attr("stroke", "var(--ink)").attr("stroke-width", 1.6);
    g.append("text").attr("x", m.l - 10).attr("y", y(i) + 4).attr("text-anchor", "end").style("font-size", "11px").style("font-weight", live ? 600 : 400).style("fill", live ? "var(--ink)" : "var(--muted)").text(nm);
    const span = (new Date(e) - new Date(vs[0])) / 31557600000, rate = vs.length / span;
    g.append("text").attr("x", W - m.r + 12).attr("y", y(i) + 4).style("font-size", "10.5px").style("font-variant-numeric", "tabular-nums").style("fill", live ? "var(--ink)" : "var(--muted)").text(`${vs.length} · ${rate >= 1 ? rate.toFixed(1) : rate.toFixed(2)}/yr`);
    g.append("rect").attr("x", 0).attr("y", y(i) - rowH / 2).attr("width", W).attr("height", rowH).attr("fill", "transparent")
      .on("pointermove", ev => showTip(ev, `<b>${esc(nm)}</b> · ${esc(path)}<br>${vs.length} version${vs.length > 1 ? "s" : ""}, ${vs[0]} to ${vs[vs.length - 1]}<br>status in the corpus: ${esc(st)}`)).on("pointerleave", hideTip); });
  svg.append("text").attr("x", W - m.r + 12).attr("y", m.t - 12).style("font-size", "9.5px").style("fill", "var(--muted)").text("versions · a year");
  legend("lg-codes", [["in force", "--c1"], ["repealed (the bar marks the day)", "--muted"], ["replaced by", "--c2"]], true);
}
