
// ---- Across jurisdictions (rebuilt each round) ----
const N2 = { de: "Germany", li: "Liechtenstein", lu: "Luxembourg", ch: "Switzerland", us: "United States", gb: "United Kingdom",
  sk: "Slovakia", si: "Slovenia", ee: "Estonia", mc: "Monaco", mt: "Malta", fi: "Finland", hr: "Croatia", gi: "Gibraltar", dk: "Denmark", hk: "Hong Kong", kg: "Kyrgyzstan", it: "Italy", pt: "Portugal", mg: "Madagascar", rw: "Rwanda" };
const C2 = { de: "var(--de)", li: "var(--gb)", lu: "var(--us)", sk: "var(--ch)", si: "var(--c5)", ee: "var(--c6)", mc: "var(--c7)",
  ch: "var(--ch)", us: "var(--us)", gb: "var(--gb)", mt: "var(--c5)", fi: "var(--ghost)", hr: "var(--c6)", gi: "var(--c7)", dk: "var(--ink)", hk: "var(--c6)", kg: "var(--later)", it: "var(--now)", pt: "var(--hi)", mg: "var(--c7)", rw: "var(--c6)" };
const CONST7 = ["de", "sk", "lu", "li", "mc", "si", "ee", "fi", "hr", "gi", "dk", "kg", "it", "pt", "mg", "rw"].filter(c => S.const_growth[c]);
if (S.round) document.getElementById("roundline").textContent = `Round ${S.round.n}, ${S.round.at}: ${S.round.note}`;

// Endpoint labels that do not overlap: spread them vertically
function spread(items, minGap, lo, hi) {
  items.sort((a, b) => a.y - b.y);
  for (let i = 1; i < items.length; i++) if (items[i].y - items[i - 1].y < minGap) items[i].y = items[i - 1].y + minGap;
  const over = items.length ? items.at(-1).y - hi : 0;
  if (over > 0) items.forEach(d => d.y -= over);
  items.forEach(d => d.y = Math.max(lo, d.y));
  return items;
}

// Constitution growth, indexed to adoption
{
  const W = 960, H = 380, m = { l: 52, r: 190, t: 18, b: 34 };
  const svg = d3.select("#f-const").attr("viewBox", `0 0 ${W} ${H}`);
  const series = CONST7.map(c => {
    const g = S.const_growth[c], t0 = P(g[0].date), w0 = g[0].words;
    const pts = g.map(d => ({ yr: (P(d.date) - t0) / 3.15576e10, v: d.words / w0, law: d.law, date: d.date, words: d.words }));
    pts.push({ ...pts.at(-1), yr: (P("2026-10-28") - t0) / 3.15576e10 });
    return { c, pts, start: g[0].date.slice(0, 4) };
  });
  const x = d3.scaleLinear([0, 160], [m.l, W - m.r]);
  const y = d3.scaleLinear([0.85, 2.2], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(8).tickFormat(d => `${d} yrs`));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([1, 1.25, 1.5, 1.75, 2]).tickFormat(d => `×${d}`).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  const labels = [];
  series.forEach(s => {
    svg.append("path").datum(s.pts).attr("fill", "none").attr("stroke", C2[s.c]).attr("stroke-width", 2.2)
      .attr("d", d3.line().curve(d3.curveStepAfter).x(d => x(d.yr)).y(d => y(d.v)));
    const e = s.pts.at(-1);
    labels.push({ x: x(e.yr), y: y(e.v), y0: y(e.v), s, e });
    svg.append("g").selectAll("circle").data(s.pts.slice(0, -1)).join("circle").attr("cx", d => x(d.yr)).attr("cy", d => y(d.v)).attr("r", 6).attr("fill", "transparent")
      .append("title").text(d => `${N2[s.c]} · ${d.date} · ${d.law}\n${fmt(d.words)} words`);
  });
  // Labels sit in the right margin, joined to each line's end
  spread(labels.map(l => ({ ...l, y: l.y0 })), 15, m.t, H - m.b).forEach(l => {
    svg.append("line").attr("x1", l.x + 2).attr("x2", W - m.r + 12).attr("y1", l.y0).attr("y2", l.y).attr("stroke", C2[l.s.c]).attr("stroke-opacity", .4);
    svg.append("text").attr("x", W - m.r + 16).attr("y", l.y).attr("dy", "0.32em").attr("class", "ser").attr("font-size", 12.5)
      .text(`${N2[l.s.c]} ${l.s.start} · ×${l.e.v.toFixed(2)}`);
  });
}

// Kaplan-Meier, constitutional wording
{
  const W = 960, H = 360, m = { l: 52, r: 190, t: 18, b: 34 };
  const svg = d3.select("#f-km").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, 100], [m.l, W - m.r]);
  const y = d3.scaleLinear([0, 1], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(10).tickFormat(d => `${d} yrs`));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(d3.format(".0%")).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  svg.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(.5)).attr("y2", y(.5)).attr("stroke", "var(--ghost)").attr("stroke-dasharray", "4 4");
  const labels = [];
  CONST7.filter(c => S.survival_const[c]).forEach(c => {
    const v = S.survival_const[c], maxY = v.max_days / 365.25;
    const pts = v.curve.map(([t, s]) => [t / 365.25, s]).filter(p => p[0] <= 100);
    pts.push([Math.min(100, maxY), pts.at(-1)[1]]);
    svg.append("path").datum(pts).attr("fill", "none").attr("stroke", C2[c]).attr("stroke-width", 2.2)
      .attr("d", d3.line().curve(d3.curveStepAfter).x(d => x(d[0])).y(d => y(d[1])));
    if (v.median_days) svg.append("circle").attr("cx", x(v.median_days / 365.25)).attr("cy", y(.5)).attr("r", 4.5).attr("fill", C2[c])
      .append("title").text(`${N2[c]}: median ${Math.round(v.median_days / 365.25)} years`);
    const e = pts.at(-1);
    labels.push({ x: x(e[0]), y0: y(e[1]), y: y(e[1]), c, v });
  });
  spread(labels, 15, m.t, H - m.b).forEach(l => {
    svg.append("line").attr("x1", l.x + 2).attr("x2", W - m.r + 12).attr("y1", l.y0).attr("y2", l.y).attr("stroke", C2[l.c]).attr("stroke-opacity", .4);
    svg.append("text").attr("x", W - m.r + 16).attr("y", l.y).attr("dy", "0.32em").attr("class", "ser").attr("font-size", 12.5)
      .text(`${N2[l.c]} · ${l.v.median_days ? Math.round(l.v.median_days / 365.25) + " yrs" : "no median yet"}`);
  });
}

// Readability dumbbell
{
  const rows = S.read_groups, W = 960, rowH = 40, m = { l: 160, r: 40, t: 26, b: 34 }, H = rows.length * rowH + m.t + m.b;
  const svg = d3.select("#f-read").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, 75], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(8).tickFormat(d => `${d}`).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  svg.append("text").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").attr("font-size", 11).text("median words per sentence");
  svg.append("circle").attr("cx", m.l + 4).attr("cy", 10).attr("r", 5).attr("fill", "var(--plate)").attr("stroke", "var(--ink)").attr("stroke-width", 1.5);
  svg.append("text").attr("x", m.l + 14).attr("y", 10).attr("dy", "0.32em").attr("font-size", 11).text("founding text");
  svg.append("circle").attr("cx", m.l + 124).attr("cy", 10).attr("r", 5).attr("fill", "var(--hi)");
  svg.append("text").attr("x", m.l + 134).attr("y", 10).attr("dy", "0.32em").attr("font-size", 11).text("wording written by amendment");
  rows.forEach((r, i) => {
    const y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 12).attr("y", y - 6).attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(r.name);
    svg.append("text").attr("x", m.l - 12).attr("y", y + 9).attr("text-anchor", "end").attr("font-size", 10.5).text(`${r.n0} · ${r.n1} versions`);
    svg.append("line").attr("x1", x(r.o)).attr("x2", x(r.a)).attr("y1", y).attr("y2", y).attr("stroke", "var(--hi)").attr("stroke-opacity", .45).attr("stroke-width", 3);
    svg.append("circle").attr("cx", x(r.o)).attr("cy", y).attr("r", 6).attr("fill", "var(--plate)").attr("stroke", "var(--ink)").attr("stroke-width", 1.5);
    svg.append("circle").attr("cx", x(r.a)).attr("cy", y).attr("r", 6).attr("fill", "var(--hi)");
    svg.append("text").attr("x", x(r.a) + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11.5).attr("class", "lbl")
      .text(`${r.o.toFixed(1)} → ${r.a.toFixed(1)} (+${Math.round((r.a / r.o - 1) * 100)}%)`);
  });
}

// Temporary law detector, one row per episode
{
  const rows = S.episodes, W = 960, rowH = 30, m = { l: 290, r: 20, t: 26, b: 30 }, H = rows.length * rowH + m.t + m.b;
  const svg = d3.select("#f-det").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleUtc([P("1999-06-01"), P("2025-06-01")], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(d3.utcYear.every(2)).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  [["var(--ink)", "sunset written into the law"], ["var(--hi)", "undone by a later act"]].forEach(([c, t], k) => {
    svg.append("rect").attr("x", m.l + k * 220).attr("y", 4).attr("width", 12).attr("height", 10).attr("fill", c);
    svg.append("text").attr("x", m.l + k * 220 + 18).attr("y", 13).attr("font-size", 11).text(t);
  });
  rows.forEach((r, i) => {
    const y = m.t + i * rowH + rowH / 2, x0 = x(P(r.from)), x1 = Math.max(x(P(r.to)), x0 + 3), sunset = r.law === r.end_law;
    svg.append("text").attr("x", m.l - 10).attr("y", y - 5).attr("text-anchor", "end").attr("font-size", 12).attr("class", "lbl")
      .text(`${N2[r.c]} · ${r.provs.length > 1 ? r.provs.length + " provisions" : r.provs[0]}`);
    svg.append("text").attr("x", m.l - 10).attr("y", y + 9).attr("text-anchor", "end").attr("font-size", 10.5)
      .text(r.law.replace(/^Pub\. L\. ([\d-]+) \((.*)\)$/, "$2").replace("Coronavirus Aid, Relief, and Economic Security Act", "CARES Act").replace(/^(S\.I\. \d+\/\d+) \(.*$/, "$1").slice(0, 38));
    svg.append("rect").attr("x", x0).attr("width", x1 - x0).attr("y", y - 6).attr("height", 12).attr("rx", 2).attr("fill", sunset ? "var(--ink)" : "var(--hi)")
      .append("title").text(`${r.provs.join(", ")}\n${r.from} to ${r.to} (${r.days} days)\nchanged by ${r.law}\nrestored by ${r.end_law}`);
    const late = x1 > W - 140;
    svg.append("text").attr("x", late ? x0 - 6 : x1 + 6).attr("text-anchor", late ? "end" : "start").attr("y", y).attr("dy", "0.32em").attr("font-size", 10.5)
      .text(`${r.days} days`);
  });
}

// Calendar: which day law takes effect
{
  const order = Object.entries(S.calendar).filter(([, v]) => v.n >= 10)
    .sort((a, b) => ((b[1].jan1 || 0) + (b[1].first || 0)) / b[1].n - ((a[1].jan1 || 0) + (a[1].first || 0)) / a[1].n);
  const W = 960, rowH = 28, m = { l: 160, r: 60, t: 28, b: 10 }, H = order.length * rowH + m.t + m.b;
  const svg = d3.select("#f-cal").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, 1], [m.l, W - m.r]);
  const parts = [["jan1", "1 January", "var(--de)"], ["first", "1st of another month", "color-mix(in srgb, var(--de) 45%, transparent)"], ["other", "any other day", "var(--tint)"]];
  parts.forEach(([, t, c], k) => {
    svg.append("rect").attr("x", m.l + k * 190).attr("y", 4).attr("width", 12).attr("height", 10).attr("fill", c).attr("stroke", "var(--ghost)").attr("stroke-width", k === 2 ? 1 : 0);
    svg.append("text").attr("x", m.l + k * 190 + 18).attr("y", 13).attr("font-size", 11).text(t);
  });
  order.forEach(([c, v], i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 10).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[c]);
    let acc = 0;
    parts.forEach(([k, , col2]) => {
      const share = (v[k] || 0) / v.n;
      svg.append("rect").attr("x", x(acc)).attr("width", x(acc + share) - x(acc)).attr("y", y + 5).attr("height", rowH - 10).attr("fill", col2)
        .append("title").text(`${N2[c]}: ${Math.round(share * 100)}% (${v[k] || 0} of ${v.n})`);
      if (k !== "other" && share >= .08) svg.append("text").attr("x", x(acc) + 5).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 10.5).attr("fill", k === "jan1" ? "var(--plate)" : "var(--ink)").text(`${Math.round(share * 100)}%`);
      acc += share;
    });
    svg.append("text").attr("x", W - m.r + 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 10.5).text(`n = ${v.n}`);
  });
}

// Malta, month by month
{
  const M = S.malta.months.filter(d => d.m >= "2021-01"), W = 960, H = 300, m = { l: 44, r: 16, t: 30, b: 30 };
  const svg = d3.select("#f-mt").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleBand(M.map(d => d.m), [m.l, W - m.r]).padding(.18);
  const y = d3.scaleLinear().domain([0, d3.max(M, d => (d.Act || 0) + (d["Legal Notice"] || 0))]).nice().range([H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues(M.map(d => d.m).filter(k => k.endsWith("-01"))).tickFormat(k => k.slice(0, 4)));
  M.forEach(d => {
    const a = d.Act || 0, l = d["Legal Notice"] || 0;
    svg.append("rect").attr("x", x(d.m)).attr("width", x.bandwidth()).attr("y", y(l)).attr("height", y(0) - y(l)).attr("fill", "var(--c5)");
    svg.append("rect").attr("x", x(d.m)).attr("width", x.bandwidth()).attr("y", y(l + a)).attr("height", y(l) - y(l + a)).attr("fill", "var(--ink)");
    svg.append("rect").attr("x", x(d.m)).attr("width", x.bandwidth()).attr("y", m.t).attr("height", H - m.b - m.t).attr("fill", "transparent")
      .append("title").text(`${d.m}: ${l} Legal Notices, ${a} Acts, ${d.units} units changed`);
  });
  [["var(--c5)", "Legal Notices"], ["var(--ink)", "Acts of Parliament"]].forEach(([c, t], k) => {
    svg.append("rect").attr("x", m.l + 8 + k * 150).attr("y", 6).attr("width", 12).attr("height", 10).attr("fill", c);
    svg.append("text").attr("x", m.l + 26 + k * 150).attr("y", 15).attr("font-size", 11).text(t);
  });
}

// Constitution against election act
{
  const C = ["ee", "sk", "si"].filter(c => S.elect && S.elect[c]), W = 960, laneH = 34, gH = 2 * laneH + 26, m = { l: 230, r: 120, t: 10, b: 30 }, H = C.length * gH + m.t + m.b;
  const svg = d3.select("#f-el").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleUtc([P("1991-06-01"), P("2027-01-01")], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(d3.utcYear.every(5)).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  const yrs = d => (P("2026-10-28") - P(d)) / 3.15576e10;
  C.forEach((c, i) => {
    const e = S.elect[c], y0 = m.t + i * gH;
    [["const", "Constitution", C2[c]], ["elect", "Election act", "var(--hi)"]].forEach(([k, t, col2], j) => {
      const y = y0 + j * laneH + laneH / 2, start = e["start_" + k], rate = e[k].length / yrs(start);
      svg.append("text").attr("x", m.l - 12).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(`${N2[c]} · ${t}`);
      svg.append("line").attr("x1", x(P(start))).attr("x2", x(P("2026-10-28"))).attr("y1", y).attr("y2", y).attr("stroke", "var(--rule)").attr("stroke-width", 6).attr("stroke-linecap", "round");
      svg.append("g").selectAll("line").data(e[k]).join("line").attr("x1", d => x(P(d.date))).attr("x2", d => x(P(d.date))).attr("y1", y - 8).attr("y2", y + 8)
        .attr("stroke", col2).attr("stroke-width", 2).append("title").text(d => `${d.date} · ${d.law} (${d.n} provisions)`);
      svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11.5).attr("class", "lbl").text(`${rate.toFixed(2)} a year`);
    });
  });
}

// Obligations and prohibitions per 1,000 words
{
  const rows = Object.entries(S.obligations).map(([c, v]) => ({ c, v })).filter(r => r.v.const || r.v.ordinary);
  const per = (g, k) => g && g.words ? 1000 * g[k] / g.words : null;
  rows.sort((a, b) => (per(b.v.const, "pro") ?? -1) - (per(a.v.const, "pro") ?? -1));
  const W = 960, rowH = 30, m = { l: 150, r: 30, t: 40, b: 30 }, H = rows.length * rowH + m.t + m.b, mid = (m.l + W - m.r) / 2;
  const svg = d3.select("#f-obl").attr("viewBox", `0 0 ${W} ${H}`);
  const xo = d3.scaleLinear([0, 14], [m.l + 10, mid - 20]), xp = d3.scaleLinear([0, 6], [mid + 20, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(xo).ticks(7));
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(xp).ticks(6));
  svg.append("text").attr("x", (m.l + mid) / 2).attr("y", 14).attr("text-anchor", "middle").attr("class", "lbl").attr("font-size", 12).text("obligations per 1,000 words");
  svg.append("text").attr("x", (mid + W - m.r) / 2).attr("y", 14).attr("text-anchor", "middle").attr("class", "lbl").attr("font-size", 12).text("prohibitions per 1,000 words");
  [["var(--plate)", "constitution", "var(--ink)"], ["var(--hi)", "ordinary law", "var(--hi)"]].forEach(([f, t, s], k) => {
    svg.append("circle").attr("cx", m.l + 16 + k * 130).attr("cy", 30).attr("r", 5).attr("fill", f).attr("stroke", s).attr("stroke-width", 1.5);
    svg.append("text").attr("x", m.l + 26 + k * 130).attr("y", 30).attr("dy", "0.32em").attr("font-size", 11).text(t);
  });
  rows.forEach((r, i) => {
    const y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[r.c]);
    svg.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y).attr("y2", y).attr("stroke", "var(--rule)");
    [["obl", xo], ["pro", xp]].forEach(([k, sc]) => {
      const a = per(r.v.const, k), b = per(r.v.ordinary, k);
      if (a != null && b != null) svg.append("line").attr("x1", sc(Math.min(a, 14))).attr("x2", sc(Math.min(b, 14))).attr("y1", y).attr("y2", y).attr("stroke", "var(--ghost)").attr("stroke-width", 2);
      if (b != null) svg.append("circle").attr("cx", sc(Math.min(b, k === "obl" ? 14 : 6))).attr("cy", y).attr("r", 5.5).attr("fill", "var(--hi)")
        .append("title").text(`${N2[r.c]} ordinary law: ${b.toFixed(2)} per 1,000 words (${r.v.ordinary[k]} in ${fmt(r.v.ordinary.words)})`);
      if (a != null) svg.append("circle").attr("cx", sc(Math.min(a, k === "obl" ? 14 : 6))).attr("cy", y).attr("r", 5.5).attr("fill", "var(--plate)").attr("stroke", "var(--ink)").attr("stroke-width", 1.5)
        .append("title").text(`${N2[r.c]} constitution: ${a.toFixed(2)} per 1,000 words (${r.v.const[k]} in ${fmt(r.v.const.words)})`);
    });
  });
}

// Malta hotspots
{
  const rows = S.malta_hot.top, W = 960, rowH = 26, m = { l: 390, r: 60, t: 8, b: 10 }, H = rows.length * rowH + m.t + m.b;
  const svg = d3.select("#f-mth").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, d3.max(rows, r => r.changes)], [m.l, W - m.r]);
  rows.forEach((r, i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 10).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "ser").attr("font-size", 12.5)
      .text(`${r.title.length > 44 ? r.title.slice(0, 42) + "…" : r.title} · Cap. ${r.cap}`);
    svg.append("rect").attr("x", m.l).attr("y", y + 5).attr("height", rowH - 10).attr("width", x(r.changes) - m.l).attr("fill", "var(--c5)").attr("rx", 1)
      .append("title").text(`${r.title}: ${r.changes} changes by ${r.instruments} instruments, ${fmt(r.units)} units`);
    svg.append("text").attr("x", x(r.changes) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11).attr("class", "lbl").text(r.changes);
  });
}

// Hubs: cited by other articles against times amended
{
  const H0 = S.hubs.hubs, W = 960, H = 380, m = { l: 52, r: 24, t: 20, b: 40 };
  const svg = d3.select("#f-hub").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([-0.5, d3.max(H0, h => h.cited) + 0.5], [m.l, W - m.r]);
  const y = d3.scaleLinear([-0.5, d3.max(H0, h => h.amended) + 0.5], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(6).tickFormat(d3.format("d")));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(6).tickFormat(d3.format("d")).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  svg.append("text").attr("x", W - m.r).attr("y", H - 6).attr("text-anchor", "end").attr("font-size", 11).text("cited by this many other articles");
  svg.append("text").attr("x", m.l + 4).attr("y", m.t - 6).attr("font-size", 11).text("times amended");
  const pts = H0.map(h => ({ ...h, x: x(h.cited), y: y(h.amended) }));
  d3.forceSimulation(pts).force("x", d3.forceX(d => x(d.cited)).strength(.9)).force("y", d3.forceY(d => y(d.amended)).strength(.9)).force("c", d3.forceCollide(4.6)).stop().tick(120);
  svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", 4)
    .attr("fill", d => d.cited >= 3 ? "var(--de)" : "var(--ghost)").attr("fill-opacity", .8)
    .append("title").text(d => `Art. ${d.art}: cited by ${d.cited}, amended ${d.amended} times`);
  const used = {};
  pts.filter(d => d.cited >= 4 || d.amended >= 7).forEach(d => { const key = `${d.cited}|${d.amended}`; const k = used[key] = (used[key] ?? -1) + 1; svg.append("text").attr("x", d.x + 7).attr("y", d.y + k * 14).attr("dy", "0.32em").attr("class", "lbl").attr("font-size", 11)
    .attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(`Art. ${d.art}`); });
}

// Size of amending acts
{
  const order = Object.entries(S.hubs.size).filter(([, v]) => v.length >= 4).sort((a, b) => d3.median(a[1]) - d3.median(b[1]) || b[1].length - a[1].length);
  const W = 960, laneH = 34, m = { l: 150, r: 160, t: 10, b: 34 }, H = order.length * laneH + m.t + m.b;
  const svg = d3.select("#f-size").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLog([1, 400], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues([1, 2, 5, 10, 20, 50, 100, 300]).tickFormat(d3.format("d")).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  order.forEach(([c, v], i) => {
    const y = m.t + i * laneH + laneH / 2;
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[c]);
    const sample = v.length > 600 ? v.filter((_, k) => k % Math.ceil(v.length / 600) === 0) : v;
    const pts = sample.map((n, k) => ({ n, x: x(n) + (((k * 7919) % 97) / 97 - .5) * 6, y: y + (((k * 104729) % 89) / 89 - .5) * (laneH - 12) }));
    svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => d.x).attr("cy", d => d.y).attr("r", c === "mt" ? 1.6 : 2.8)
      .attr("fill", C2[c] || "var(--ink)").attr("fill-opacity", c === "mt" ? .35 : .7);
    const med = d3.median(v);
    svg.append("line").attr("x1", x(med)).attr("x2", x(med)).attr("y1", y - 13).attr("y2", y + 13).attr("stroke", "var(--ink)").attr("stroke-width", 2);
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11).text(`median ${med} · n ${v.length}`);
  });
}

// Activity by year, small multiples
{
  const A = S.r4.activity, order = Object.keys(A).filter(c => Object.keys(A[c]).length).sort((a, b) => Math.min(...Object.keys(A[a]).map(Number)) - Math.min(...Object.keys(A[b]).map(Number)));
  const W = 960, rowH = 30, m = { l: 150, r: 150, t: 8, b: 30 }, H = order.length * rowH + m.t + m.b;
  const svg = d3.select("#f-act").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([1918, 2027], [m.l, W - m.r]), bw = Math.max(2, (x(2) - x(1)) - 1);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(11).tickFormat(d3.format("d")).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  order.forEach((c, i) => {
    const y0 = m.t + i * rowH, v = A[c], max = Math.max(...Object.values(v)), peak = Object.keys(v).find(k => v[k] === max);
    svg.append("text").attr("x", m.l - 10).attr("y", y0 + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[c]);
    Object.entries(v).forEach(([yr, n]) => {
      const h = (rowH - 6) * n / max;
      svg.append("rect").attr("x", x(+yr) - bw / 2).attr("width", bw).attr("y", y0 + rowH - 3 - h).attr("height", h).attr("fill", C2[c] || "var(--ink)")
        .append("title").text(`${N2[c]} ${yr}: ${fmt(n)} ${c === "mt" ? "units" : "provisions"} changed`);
    });
    svg.append("text").attr("x", W - m.r + 10).attr("y", y0 + rowH / 2).attr("dy", "0.32em").attr("font-size", 11).text(`peak ${peak}: ${fmt(max)}`);
  });
}

// Co-amendment matrix
{
  const arts = S.r4.coamend.arts, W = 960, cell = 21, m = { l: 80, t: 70 }, n = arts.length, H = m.t + n * cell + 10;
  const svg = d3.select("#f-co").attr("viewBox", `0 0 ${W} ${H}`);
  const idx = Object.fromEntries(arts.map((a, i) => [a, i]));
  const max = Math.max(...S.r4.coamend.pairs.map(p => p[2]));
  arts.forEach((a, i) => {
    svg.append("text").attr("x", m.l - 8).attr("y", m.t + i * cell + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(`Art. ${a}`);
    svg.append("text").attr("transform", `translate(${m.l + i * cell + cell / 2},${m.t - 8}) rotate(-60)`).attr("font-size", 10.5).text(a);
  });
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++)
    svg.append("rect").attr("x", m.l + j * cell + 1).attr("y", m.t + i * cell + 1).attr("width", cell - 2).attr("height", cell - 2).attr("fill", i === j ? "var(--tint)" : "var(--plate)").attr("stroke", "var(--rule)");
  S.r4.coamend.pairs.forEach(([a, b, k]) => [[a, b], [b, a]].forEach(([p, q]) => {
    svg.append("rect").attr("x", m.l + idx[q] * cell + 1).attr("y", m.t + idx[p] * cell + 1).attr("width", cell - 2).attr("height", cell - 2)
      .attr("fill", "var(--de)").attr("fill-opacity", .25 + .75 * k / max).append("title").text(`Art. ${p} and Art. ${q}: rewritten together by ${k} act${k > 1 ? "s" : ""}`);
  }));
  const lx = m.l + n * cell + 30;
  svg.append("text").attr("x", lx).attr("y", m.t + 10).attr("font-size", 11).text("rewritten together by");
  for (let k = 1; k <= max; k++) {
    svg.append("rect").attr("x", lx).attr("y", m.t + 6 + k * 22).attr("width", 16).attr("height", 16).attr("fill", "var(--de)").attr("fill-opacity", .25 + .75 * k / max);
    svg.append("text").attr("x", lx + 24).attr("y", m.t + 14 + k * 22).attr("dy", "0.32em").attr("font-size", 11).text(`${k} act${k > 1 ? "s" : ""}`);
  }
}
