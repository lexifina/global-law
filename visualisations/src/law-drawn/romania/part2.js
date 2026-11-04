
// ---- Part two: Romania among its neighbours ----
const GROUPS = [["South-east Europe", "--c2"], ["Rest of the EU", "--c1"], ["Rest of Europe", "--c3"], ["Rest of the world", "--c4"]], GC = new Map(GROUPS);
const nameOf = c => ({ "north-macedonia": "North Macedonia", "hong-kong": "Hong Kong", "new-zealand": "New Zealand", "trinidad-and-tobago": "Trinidad and Tobago",
  "south-korea": "South Korea", "north-korea": "North Korea", "bosnia-and-herzegovina": "Bosnia and Herzegovina" }[c] || c.replace(/-/g, " ").replace(/\b\w/g, m => m.toUpperCase()));

// 9. Emergency-decree deadlines against Romania's observed approvals
{
  const ROWS = [["Italy", 60, "converted within 60 days or void from the start"], ["Albania", 45, "approved within 45 days or void from the start"],
    ["Spain", 30, "Congress votes within 30 days or it lapses"], ["Greece", 130, "submitted within 40 days, ratified within 3 months"]];
  legend("lg-deadline", [["deadline, then the decree lapses", "--c1"], ["Romania: law approving the ordinance", "--c1"], ["Romania: law rejecting it", "--c2"]]);
  document.querySelector("#lg-deadline span i").classList.add("bar");
  const A = DATA.approvals.map(a => ({ oug: a[0], lag: a[2], v: a[3], law: a[4] })), W = 960, rh = 46, m = { t: 20, l: 120, r: 30, b: 40 }, H = m.t + (ROWS.length + 2) * rh + m.b;
  const svg = d3.select("#f-deadline").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleSqrt().domain([0, 5000]).range([m.l, W - m.r]), tv = [30, 180, 365, 730, 1461, 2922, 4383];
  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(tv).tickFormat(d => d < 365 ? `${d} days` : `${Math.round(d / 365.25)} y`)).call(axisStyle);
  svg.append("g").selectAll("line").data(tv).join("line").attr("x1", x).attr("x2", x).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--rule)");
  ROWS.forEach(([n, d, t], i) => { const yy = m.t + i * rh + rh / 2;
    svg.append("text").attr("class", "lbl").attr("x", m.l - 12).attr("y", yy + 4).attr("text-anchor", "end").text(n);
    svg.append("rect").attr("x", m.l).attr("y", yy - 7).attr("width", x(d) - m.l).attr("height", 14).attr("rx", 3).attr("fill", "var(--c1)").attr("opacity", .85);
    svg.append("line").attr("x1", x(d)).attr("x2", x(d)).attr("y1", yy - 12).attr("y2", yy + 12).attr("stroke", "var(--ink)").attr("stroke-width", 2);
    svg.append("text").attr("x", x(d) + 8).attr("y", yy + 4).text(`${d} days · ${t}`); });
  // Romania: the 30-day tacit adoption, then the observed laws
  const y0 = m.t + ROWS.length * rh + rh;
  svg.append("text").attr("class", "lbl").attr("x", m.l - 12).attr("y", y0 + 4).attr("text-anchor", "end").text("Romania");
  svg.append("line").attr("x1", x(30)).attr("x2", x(30)).attr("y1", y0 - rh - 14).attr("y2", y0 + rh).attr("stroke", "var(--ink)").attr("stroke-dasharray", "3 3");
  svg.append("text").attr("class", "lbl halo").attr("x", x(30) - 6).attr("y", y0 - rh - 4).attr("text-anchor", "end").text("30 days: a silent chamber is deemed to adopt");
  const nodes = A.map(a => ({ ...a, x: x(a.lag), y: y0 }));
  const sim = d3.forceSimulation(nodes).force("x", d3.forceX(a => x(a.lag)).strength(1)).force("y", d3.forceY(y0).strength(.08)).force("c", d3.forceCollide(3.2)).stop();
  for (let i = 0; i < 200; i++) sim.tick();
  svg.append("g").selectAll("circle").data(nodes).join("circle").attr("cx", a => a.x).attr("cy", a => Math.max(y0 - rh, Math.min(y0 + rh, a.y))).attr("r", 2.8)
    .attr("fill", a => a.v === "r" ? "var(--c2)" : "var(--c1)").attr("fill-opacity", .85)
    .on("pointermove", (ev, a) => showTip(ev, `<b>${a.oug}</b><br>${a.v === "r" ? "Rejected" : "Approved"} by ${esc(a.law)}<br><span class="m">${fmt(a.lag)} days after publication</span>`)).on("pointerleave", hideTip);
  const med = d3.median(A, a => a.lag);
  svg.append("line").attr("x1", x(med)).attr("x2", x(med)).attr("y1", y0 - rh).attr("y2", y0 + rh).attr("stroke", "var(--ink)");
  svg.append("text").attr("class", "lbl halo").attr("x", x(med) + 6).attr("y", y0 + rh - 2).text(`median ${Math.round(med)} days`);
}

// 10. Romania and Spain, acts per year by number
{
  const Y = d3.range(1990, 2026), I = DATA.issued, S = DATA.spain, yi = y => DATA.years.indexOf(y), sp = (k, y) => (S[k][y] || {}).issued || 0;
  const SER = [["Romania · laws", "--c2", y => I.Legea[yi(y)], false], ["Romania · emergency ordinances", "--c2", y => I.OUG[yi(y)], true],
    ["Spain · laws (Ley and Ley Orgánica)", "--c1", y => sp("Ley", y) + sp("LO", y), false], ["Spain · decree-laws", "--c1", y => sp("RDL", y), true]];
  document.getElementById("lg-spain").innerHTML = SER.map(([n, c, f, dash]) => `<span><svg width="22" height="8" style="min-width:0"><line x1="0" x2="22" y1="4" y2="4" stroke="var(${c})" stroke-width="2.5" ${dash ? 'stroke-dasharray="5 3"' : ""}/></svg>${n}</span>`).join("");
  const W = 960, H = 400, m = { t: 16, r: 140, b: 36, l: 50 };
  const svg = d3.select("#f-spain").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear().domain([1990, 2025]).range([m.l, W - m.r]), y = d3.scaleLog().domain([1, 1000]).range([H - m.b, m.t]).clamp(true);
  svg.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues([1, 3, 10, 30, 100, 300, 1000]).tickFormat(d3.format("d")).tickSize(-(W - m.l - m.r))).call(axisStyle).call(g => g.select(".domain").remove());
  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(9).tickFormat(d3.format("d"))).call(axisStyle);
  const line = f => d3.line().defined(y_ => f(y_) > 0).x(x).y(y_ => y(f(y_))).curve(d3.curveMonotoneX);
  SER.forEach(([n, c, f, dash]) => {
    const yrs = Y.filter(y_ => f(y_) > 0 && (n.startsWith("Spain") ? y_ >= 1990 : y_ >= (n.includes("ordinances") ? 1997 : 1990)));
    svg.append("path").attr("d", line(f)(yrs)).attr("fill", "none").attr("stroke", `var(${c})`).attr("stroke-width", 2.2).attr("stroke-dasharray", dash ? "6 4" : null);
    const last = yrs.at(-1), short = { "Romania · laws": ["Romania, laws", 0], "Romania · emergency ordinances": ["Romania, OUG", 0],
      "Spain · laws (Ley and Ley Orgánica)": ["Spain, laws", 8], "Spain · decree-laws": ["Spain, decree-laws", -6] }[n];
    svg.append("text").attr("class", "lbl halo").attr("x", x(last) + 8).attr("y", y(f(last)) + 4 + short[1]).style("font-size", "10.5px").text(short[0]);
  });
  const rule = svg.append("line").attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--ink)").attr("opacity", 0);
  svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b).attr("fill", "transparent")
    .on("pointermove", ev => { const yr = Math.round(x.invert(d3.pointer(ev)[0])); rule.attr("x1", x(yr)).attr("x2", x(yr)).attr("opacity", .35);
      showTip(ev, `<b>${yr}</b><br>${SER.map(([n, c, f]) => `${n}: ${f(yr) || "–"}`).join("<br>")}`); })
    .on("pointerleave", () => { rule.attr("opacity", 0); hideTip(); });
}

// 11. Default vacatio legis
{
  const V = [["France", 1, "the next day"], ["Romania", 3, "three days (laws); the same day for government acts"], ["Bulgaria", 3, "three days"], ["Portugal", 5, "the fifth day"],
    ["Serbia", 8, "the eighth day"], ["Germany", 14, "the fourteenth day"], ["Italy", 15, "the fifteenth day"], ["Slovenia", 15, "the fifteenth day"], ["Spain", 20, "twenty days"]];
  const SEE = new Set(["Romania", "Bulgaria", "Serbia", "Slovenia"]);
  const W = 960, rh = 34, m = { t: 26, l: 110, r: 30, b: 40 }, H = m.t + V.length * rh + m.b;
  const svg = d3.select("#f-vacatio").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear().domain([0, 24]).range([m.l, W - m.r]);
  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(24).tickFormat(d => d % 5 === 0 || d === 3 || d === 1 || d === 8 || d === 14 ? d : "")).call(axisStyle);
  svg.append("text").attr("x", (m.l + W - m.r) / 2).attr("y", H - 4).attr("text-anchor", "middle").text("days after publication in the official gazette");
  svg.append("text").attr("x", m.l).attr("y", m.t - 10).text("publication");
  V.forEach(([n, d, t], i) => { const yy = m.t + i * rh + rh / 2, col = SEE.has(n) ? "--c2" : "--c1", ro = n === "Romania";
    svg.append("text").attr("class", "lbl").attr("x", m.l - 12).attr("y", yy + 4).attr("text-anchor", "end").style("font-weight", ro ? 600 : null).text(n);
    svg.append("line").attr("x1", x(0)).attr("x2", x(d)).attr("y1", yy).attr("y2", yy).attr("stroke", `var(${col})`).attr("stroke-width", ro ? 3 : 2).attr("stroke-linecap", "round");
    svg.append("circle").attr("cx", x(0)).attr("cy", yy).attr("r", 3).attr("fill", "var(--ghost)");
    svg.append("circle").attr("cx", x(d)).attr("cy", yy).attr("r", ro ? 7 : 6).attr("fill", `var(${col})`).attr("stroke", "var(--plate)").attr("stroke-width", 2);
    svg.append("text").attr("x", x(d) + 12).attr("y", yy + 4).text(t); });
  legend("lg-vacatio", [["South-east Europe", "--c2"], ["Elsewhere in Europe", "--c1"]]);
}

// 12. First of the month and weekends
{
  legend("lg-calendar", GROUPS);
  const C = DATA.cmp.filter(r => r.acts >= 300).sort((a, b) => a.first - b.first);
  const W = 960, rh = 19, m = { t: 30, l: 170, r: 24, b: 34 }, H = m.t + C.length * rh + m.b, gap = 40, pw = (W - m.l - m.r - gap) / 2;
  const svg = d3.select("#f-calendar").attr("viewBox", `0 0 ${W} ${H}`);
  const xa = d3.scaleLinear().domain([0, .8]).range([m.l, m.l + pw]), xb = d3.scaleLinear().domain([0, .6]).range([m.l + pw + gap, W - m.r]);
  [[xa, "starts on the first of a month", [0, .2, .4, .6, .8]], [xb, "starts on a Saturday or Sunday", [0, .2, .4, .6]]].forEach(([x, t, tv]) => {
    svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(tv).tickFormat(d3.format(".0%"))).call(axisStyle);
    svg.append("g").selectAll("line").data(tv).join("line").attr("x1", x).attr("x2", x).attr("y1", m.t - 6).attr("y2", H - m.b).attr("stroke", "var(--rule)");
    svg.append("text").attr("class", "lbl").attr("x", x.range()[0]).attr("y", m.t - 14).text(t); });
  C.forEach((r, i) => { const yy = m.t + i * rh + rh / 2, ro = r.country === "romania", col = `var(${GC.get(r.group)})`;
    if (ro) svg.append("rect").attr("x", 4).attr("y", yy - rh / 2).attr("width", W - 8).attr("height", rh).attr("fill", "var(--tint)").attr("rx", 4);
    svg.append("text").attr("class", "lbl").attr("x", m.l - 10).attr("y", yy + 4).attr("text-anchor", "end").style("font-weight", ro ? 600 : null).style("font-size", "10.5px").text(nameOf(r.country));
    [[xa, r.first], [xb, r.weekend]].forEach(([x, v]) => {
      svg.append("line").attr("x1", x(0)).attr("x2", x(v)).attr("y1", yy).attr("y2", yy).attr("stroke", "var(--rule)");
      svg.append("circle").attr("cx", x(v)).attr("cy", yy).attr("r", ro ? 6 : 4.5).attr("fill", col).attr("stroke", ro ? "var(--ink)" : "var(--plate)").attr("stroke-width", ro ? 1.5 : 1); });
    svg.append("rect").attr("x", 0).attr("y", yy - rh / 2).attr("width", W).attr("height", rh).attr("fill", "transparent")
      .on("pointermove", ev => showTip(ev, `<b>${nameOf(r.country)}</b> · ${r.group}<br>${(r.first * 100).toFixed(0)}% start on the first of a month<br>${(r.weekend * 100).toFixed(0)}% start at the weekend<br><span class="m">${fmt(r.acts)} dated acts</span>`)).on("pointerleave", hideTip); });
}

// 13. Days from adoption to force
{
  const L = DATA.cmp.filter(r => r.lag_median != null && r.lag_n >= 50);
  legend("lg-wait", GROUPS);
  const W = 960, rh = 64, m = { t: 14, l: 150, r: 30, b: 40 }, H = m.t + GROUPS.length * rh + m.b;
  const svg = d3.select("#f-wait").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleSqrt().domain([0, 100]).range([m.l, W - m.r]), tv = [0, 1, 3, 7, 14, 30, 60, 90];
  svg.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues(tv).tickFormat(d => d === 1 ? "1 day" : d === 0 ? "same day" : `${d}`)).call(axisStyle);
  svg.append("g").selectAll("line").data(tv).join("line").attr("x1", x).attr("x2", x).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--rule)");
  GROUPS.forEach(([g, c], i) => { const yy = m.t + i * rh + rh / 2, pts = L.filter(r => r.group === g).map(r => ({ ...r, x: x(r.lag_median), y: yy }));
    svg.append("text").attr("class", "lbl").attr("x", m.l - 12).attr("y", yy + 4).attr("text-anchor", "end").text(g);
    const sim = d3.forceSimulation(pts).force("x", d3.forceX(r => x(r.lag_median)).strength(1)).force("y", d3.forceY(yy).strength(.1)).force("c", d3.forceCollide(7.5)).stop();
    for (let k = 0; k < 160; k++) sim.tick();
    svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", r => r.x).attr("cy", r => r.y).attr("r", r => r.country === "romania" ? 8 : 6)
      .attr("fill", `var(${c})`).attr("stroke", r => r.country === "romania" ? "var(--ink)" : "var(--plate)").attr("stroke-width", r => r.country === "romania" ? 2 : 1.2)
      .on("pointermove", (ev, r) => showTip(ev, `<b>${nameOf(r.country)}</b><br>median ${r.lag_median} days from adoption to force<br><span class="m">${fmt(r.lag_n)} acts with both dates</span>`)).on("pointerleave", hideTip);
    const lab = new Set(["romania", "france", "spain", "italy", "finland", "denmark", "greece", "georgia"]);
    svg.append("g").selectAll("text").data(pts.filter(r => lab.has(r.country))).join("text").attr("class", "lbl halo").attr("x", r => r.x).attr("y", r => r.y - 11)
      .attr("text-anchor", "middle").style("font-size", "10.5px").style("font-weight", r => r.country === "romania" ? 600 : null).text(r => `${nameOf(r.country)} ${r.lag_median}`); });
}
