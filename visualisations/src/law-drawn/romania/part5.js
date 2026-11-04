
// ---- Part five: Romania against all of global law ----
const SE5 = new Set(["albania", "bosnia-and-herzegovina", "bulgaria", "croatia", "greece", "kosovo", "montenegro", "north-macedonia", "serbia", "slovenia", "moldova", "turkey"]);
const EU5 = new Set(["austria", "belgium", "cyprus", "czechia", "denmark", "estonia", "finland", "france", "germany", "hungary", "ireland", "italy", "latvia", "lithuania", "luxembourg", "malta", "netherlands", "poland", "portugal", "slovakia", "spain", "sweden"]);
const EUR5 = new Set(["united-kingdom", "switzerland", "norway", "iceland", "liechtenstein", "monaco", "andorra", "san-marino", "vatican-city", "ukraine", "belarus", "gibraltar", "faroe-islands", "aland", "greenland", "jersey", "guernsey", "isle-of-man", "georgia", "armenia", "azerbaijan", "russia"]);
const GRP5 = c => c === "romania" ? 0 : SE5.has(c) ? 1 : EU5.has(c) ? 2 : EUR5.has(c) ? 3 : 4;
const GCOL5 = ["--c2", "--c4", "--c1", "--c3", "--ghost"], GNAME5 = ["Romania", "Rest of south-east Europe", "Rest of the EU", "Rest of Europe", "Rest of the world"];
const title5 = s => s.split("-").map(w => ["and", "of", "the"].includes(w) ? w : w[0].toUpperCase() + w.slice(1)).join(" ");

// 24. Every corpus in global-law as a circle inside its country, sized by commits
{
  const PK = DATA.pack, W = 960, H = 720, S = 704;
  const svg = d3.select("#f-pack").attr("viewBox", `0 0 ${W} ${H}`);
  const byC = d3.group(PK, d => d[0].split("/")[0]);
  const root = d3.hierarchy({ children: [...byC].map(([c, rows]) => ({ c, children: rows.map(([p, n]) => ({ c, p, n })) })) }).sum(d => d.n || 0).sort((a, b) => b.value - a.value);
  d3.pack().size([S, S]).padding(d => d.depth === 0 ? 3 : 1.2)(root);
  const g = svg.append("g").attr("transform", `translate(8,8)`);
  g.selectAll("circle.ctry").data(root.children).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r)
    .attr("fill", d => d.data.c === "romania" ? "none" : "var(--tint)").attr("stroke", d => d.data.c === "romania" ? "var(--ink)" : "var(--rule)").attr("stroke-width", d => d.data.c === "romania" ? 1.6 : .6);
  g.selectAll("circle.leaf").data(root.leaves()).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => Math.max(.4, d.r))
    .attr("fill", d => `var(${GCOL5[GRP5(d.data.c)]})`).attr("fill-opacity", d => GRP5(d.data.c) === 0 ? 1 : GRP5(d.data.c) === 4 ? .75 : .7)
    .on("pointermove", (ev, d) => showTip(ev, `<b>${esc(title5(d.data.c))}</b> · ${esc(d.data.p)}<br>${fmt(d.data.n)} commits, ${(100 * d.data.n / root.value).toFixed(1)}% of global law`)).on("pointerleave", hideTip);
  // Country names where the circle is big enough
  root.children.filter(d => d.r > 36 && d.data.c !== "romania").forEach(d => { const big = d.r > 80, name = title5(d.data.c);
    g.append("text").attr("x", d.x).attr("y", d.y + (big ? -d.r + 16 : 4)).attr("text-anchor", "middle").style("font-size", big ? "12.5px" : "10.5px").style("font-weight", 600)
      .style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).style("pointer-events", "none").text(name); });
  // Romania callout
  const ro = root.children.find(d => d.data.c === "romania");
  g.append("text").attr("x", ro.x).attr("y", ro.y + 4).attr("text-anchor", "middle").style("font-size", "13px").style("font-weight", 600).style("fill", "#fff").style("pointer-events", "none").text("Romania");
  // Right column
  const tot = root.value, cs = root.children.map(d => d.value).sort(d3.ascending); let k = 0, s = 0; while (s + cs[k] <= ro.value) s += cs[k++];
  const notes = [[fmt(PK.length), "corpora in global law,", `in ${root.children.length} countries`], ["2nd", "largest corpus: Romania,", `${fmt(ro.value)} commits; France ${fmt(d3.max(PK, d => d[1]))}`],
    [`${(100 * ro.value / tot).toFixed(1)}%`, "of all commits in global law", `are Romanian, of ${fmt(tot)}`], [fmt(k), "smallest countries together", "hold fewer than Romania"]];
  notes.forEach(([b, a, c], i) => { const y = 92 + i * 104;
    svg.append("text").attr("x", 748).attr("y", y).style("font-size", "28px").style("font-weight", 600).style("font-variant-numeric", "tabular-nums").text(b);
    svg.append("text").attr("x", 748).attr("y", y + 21).style("font-size", "11px").text(a);
    svg.append("text").attr("x", 748).attr("y", y + 35).style("font-size", "11px").attr("fill", "var(--muted)").text(c); });
  legend("lg-pack", GNAME5.map((n, i) => [n, GCOL5[i]]));
}

// 25. The legal year of each national corpus as a rose: 366 spokes, one per calendar day, from most even to most bunched
{
  const RS = DATA.roses, cols = 6, tw = 160, th = 172, R = 52, r0 = 7, rE = 25, W = cols * tw, H = Math.ceil(RS.length / cols) * th + 6;
  const svg = d3.select("#f-roses").attr("viewBox", `0 0 ${W} ${H}`);
  const len = q => Math.max(1.2, (rE - r0) * (1 + .55 * Math.log10(q)));  // q = the day's share relative to an even year
  const ang = i => 2 * Math.PI * i / 366 - Math.PI / 2;
  RS.forEach(([c, n, days, ev, gp], k) => {
    const g = svg.append("g").attr("transform", `translate(${(k % cols) * tw + tw / 2},${Math.floor(k / cols) * th + R + 8})`), ro = c === "romania";
    // Month ticks and the even-year ring: where every spoke would end if law took effect equally on every day
    d3.range(12).forEach(mo => { const a = ang([0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335][mo]); g.append("line").attr("x1", (r0 - 3) * Math.cos(a)).attr("y1", (r0 - 3) * Math.sin(a)).attr("x2", (r0 - 6) * Math.cos(a)).attr("y2", (r0 - 6) * Math.sin(a)).attr("stroke", "var(--ghost)"); });
    const path = days.map((v, i) => { if (!v) return ""; const a = ang(i), l = r0 + len(366 * v / n); return `M${(r0 * Math.cos(a)).toFixed(1)},${(r0 * Math.sin(a)).toFixed(1)}L${(l * Math.cos(a)).toFixed(1)},${(l * Math.sin(a)).toFixed(1)}`; }).join("");
    g.append("path").attr("d", path).attr("stroke", ro ? "var(--c2)" : `var(${gp === 4 ? "--muted" : GCOL5[gp]})`).attr("stroke-width", .7).attr("stroke-opacity", ro ? 1 : .85).attr("stroke-linecap", "round");
    g.append("circle").attr("r", rE).attr("fill", "none").attr("stroke", "var(--plate)").attr("stroke-width", 2.2).attr("stroke-opacity", .7);
    g.append("circle").attr("r", rE).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", .7).attr("stroke-dasharray", "2 2");
    const j1 = days[0] / n, f1 = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335].reduce((s, i) => s + days[i], 0) / n;
    g.append("text").attr("y", R + 18).attr("text-anchor", "middle").attr("class", "ser").style("font-size", "12.5px").style("font-weight", ro ? 700 : 400).style("fill", ro ? "var(--c2)" : "var(--ink)").text(title5(c));
    g.append("text").attr("y", R + 32).attr("text-anchor", "middle").style("font-size", "9.5px").attr("fill", "var(--muted)").text(`1 January ${(100 * j1).toFixed(j1 < .1 ? 1 : 0)}%`);
    g.append("text").attr("y", R + 44).attr("text-anchor", "middle").style("font-size", "9.5px").attr("fill", "var(--muted)").text(`1st of a month ${Math.round(100 * f1)}%`);
    g.append("rect").attr("x", -tw / 2).attr("y", -R - 8).attr("width", tw).attr("height", th).attr("fill", "transparent")
      .on("pointermove", ev => showTip(ev, `<b>${esc(title5(c))}</b> · ${fmt(n)} dated acts<br>${(100 * j1).toFixed(1)}% take effect on 1 January, ${(100 * f1).toFixed(1)}% on the 1st of a month<br>evenness ${ev.toFixed(3)} (1 = every day alike)`)).on("pointerleave", hideTip);
    if (k === 0) g.append("text").attr("x", 0).attr("x", 6).attr("y", -R + 4).style("font-size", "9px").attr("fill", "var(--muted)").text("1 Jan");
  });
  legend("lg-roses", GNAME5.map((n, i) => [n, i === 4 ? "--muted" : GCOL5[i]]));
}

// 26. Calendar families: a radial tree joining countries whose legal years look alike, closest pairs joined furthest out
{
  const W = 960, H = 720, cx = 340, cy = 362, R = 232;
  const svg = d3.select("#f-tree").attr("viewBox", `0 0 ${W} ${H}`), g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  const root = d3.hierarchy(DATA.tree), hmax = root.data.h, leaves = root.leaves(), N = leaves.length;
  leaves.forEach((d, i) => d.a = 2 * Math.PI * (i + .5) / N);
  root.eachAfter(d => { if (d.children) d.a = (d3.min(d.children, c => c.a) + d3.max(d.children, c => c.a)) / 2; d.r = R * (1 - (d.data.h || 0) / hmax); });
  const P = (a, r) => [r * Math.sin(a), -r * Math.cos(a)];
  const onRo = new Set(); let n = leaves.find(d => d.data.name === "romania"); while (n) { onRo.add(n); n = n.parent; }
  // Distance rings
  [.1, .2, .3, .4, .5].filter(h => h < hmax).forEach(h => { const r = R * (1 - h / hmax); g.append("circle").attr("r", r).attr("fill", "none").attr("stroke", "var(--rule)").attr("stroke-dasharray", "2 3");
    g.append("text").attr("x", 0).attr("y", r + 11).attr("text-anchor", "middle").style("font-size", "9.5px").style("paint-order", "stroke").style("stroke", "var(--plate)").style("stroke-width", 3).attr("fill", "var(--muted)").text(`${h.toFixed(1)}`); });
  svg.append("text").attr("x", 16).attr("y", 26).style("font-size", "10px").attr("fill", "var(--muted)").text("Dashed rings: the distance at which branches join,");
  svg.append("text").attr("x", 16).attr("y", 39).style("font-size", "10px").attr("fill", "var(--muted)").text("0.1 near the rim to 0.5 near the centre");
  // Branches: a radial step from each child to its parent's radius, then an arc across the parent's children
  root.descendants().filter(d => d.children).forEach(d => {
    const a0 = d3.min(d.children, c => c.a), a1 = d3.max(d.children, c => c.a), hot = onRo.has(d);
    g.append("path").attr("d", d3.arc()({ innerRadius: d.r, outerRadius: d.r, startAngle: a0, endAngle: a1 })).attr("fill", "none").attr("stroke", hot ? "var(--c2)" : "var(--muted)").attr("stroke-width", hot ? 2 : 1);
    d.children.forEach(c => { const [x0, y0] = P(c.a, d.r), [x1, y1] = P(c.a, c.r), h2 = onRo.has(c) && hot;
      g.append("line").attr("x1", x0).attr("y1", y0).attr("x2", x1).attr("y2", y1).attr("stroke", h2 ? "var(--c2)" : "var(--muted)").attr("stroke-width", h2 ? 2 : 1); });
  });
  // Leaves and their names
  leaves.forEach(d => { const [x, y] = P(d.a, R), ro = d.data.name === "romania", gp = d.data.g, deg = d.a * 180 / Math.PI - 90, flip = d.a > Math.PI;
    g.append("circle").attr("cx", x).attr("cy", y).attr("r", ro ? 5.5 : 4).attr("fill", `var(${gp === 4 ? "--muted" : GCOL5[gp]})`).attr("stroke", "var(--plate)").attr("stroke-width", 1.2)
      .on("pointermove", ev => { const nb = DATA.near.find(r => r[0] === d.data.name); showTip(ev, `<b>${esc(title5(d.data.name))}</b>${nb ? `<br>distance from Romania's calendar ${nb[1].toFixed(2)}` : ""}`); }).on("pointerleave", hideTip);
    g.append("text").attr("transform", `rotate(${flip ? deg + 180 : deg}) translate(${flip ? -(R + 10) : R + 10},0)`).attr("dy", ".35em").attr("text-anchor", flip ? "end" : "start")
      .style("font-size", ro ? "12.5px" : "11px").style("font-weight", ro ? 700 : 400).style("fill", ro ? "var(--c2)" : "var(--ink)").text(title5(d.data.name)); });
  // Right column: Romania's distance to every other calendar, nearest first
  const NB = DATA.near, x0 = 700, bw = 128, rowH = 12.6, xs = d3.scaleLinear().domain([0, .7]).range([0, bw]);
  svg.append("text").attr("x", x0).attr("y", 54).attr("class", "ser").style("font-size", "13px").text("Distance from Romania's year");
  svg.append("text").attr("x", x0).attr("y", 69).style("font-size", "10px").attr("fill", "var(--muted)").text("0 = the same calendar, 1 = nothing shared");
  NB.forEach(([c, dd], i) => { const y = 88 + i * rowH, gp = DATA.roses.find(r => r[0] === c)[4];
    svg.append("text").attr("x", x0 + 84).attr("y", y + 8).attr("text-anchor", "end").style("font-size", "10px").text(title5(c));
    svg.append("rect").attr("x", x0 + 90).attr("y", y + 1).attr("width", xs(dd)).attr("height", 8).attr("rx", 1.5).attr("fill", `var(${gp === 4 ? "--muted" : GCOL5[gp]})`).attr("fill-opacity", .8);
    svg.append("text").attr("x", x0 + 94 + xs(dd)).attr("y", y + 8).style("font-size", "9.5px").style("font-variant-numeric", "tabular-nums").attr("fill", "var(--muted)").text(dd.toFixed(2)); });
  legend("lg-tree", GNAME5.map((nm, i) => [nm, i === 4 ? "--muted" : GCOL5[i]]));
}
