
// ---- Round 5: global lag, whole statute books, Georgian start rules ----
Object.assign(N2, { am: "Armenia", ge: "Georgia" });

// Days from adoption to entry into force, every jurisdiction
{
  const L = S.r5.lag, codes = Object.keys(L).filter(c => L[c].n >= 5).sort((a, b) => L[a].median - L[b].median || L[b].n - L[a].n);
  const W = 960, rowH = 28, m = { l: 150, r: 150, t: 26, b: 34 }, H = codes.length * rowH + m.t + m.b;
  const svg = d3.select("#f-lag2").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleSymlog([-30, 1500], [m.l, W - m.r]).constant(3), cx = v => x(Math.max(-30, Math.min(1500, v)));
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues([0, 3, 7, 14, 30, 90, 180, 365, 730]).tickFormat(v => v === 0 ? "same day" : v >= 365 ? `${v / 365} yr` : `${v} d`).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  codes.forEach((c, i) => {
    const v = L[c], y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[c]);
    svg.append("line").attr("x1", cx(v.p05)).attr("x2", cx(v.p95)).attr("y1", y).attr("y2", y).attr("stroke", "var(--ghost)").attr("stroke-width", 1.5);
    svg.append("rect").attr("x", cx(v.q1)).attr("width", Math.max(2, cx(v.q3) - cx(v.q1))).attr("y", y - 8).attr("height", 16).attr("fill", C2[c] || "var(--c5)").attr("fill-opacity", .55).attr("rx", 2);
    svg.append("line").attr("x1", cx(v.median)).attr("x2", cx(v.median)).attr("y1", y - 10).attr("y2", y + 10).attr("stroke", "var(--ink)").attr("stroke-width", 2.4);
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11)
      .text(`${v.median === 0 ? "same day" : Math.round(v.median) + " d"} · n ${fmt(v.n)}`);
    svg.append("rect").attr("x", m.l).attr("width", W - m.l - m.r).attr("y", y - 12).attr("height", 24).attr("fill", "transparent")
      .append("title").text(`${N2[c]}: median ${v.median} days, middle half ${v.q1} to ${v.q3} days, ${v.n} acts (${v.neg} in force before adoption)`);
  });
  svg.append("text").attr("x", m.l).attr("y", 14).attr("font-size", 11).text("days from adoption to entry into force (log scale)");
  const all = codes.reduce((s, c) => s + L[c].n, 0), fastest = codes[0], slowest = codes.at(-1);
  const within30 = codes.reduce((s, c) => s + L[c].within30, 0);
  document.querySelector("#startlag .eyebrow").textContent = `${codes.length} jurisdictions · round 5`;
  document.getElementById("lag-text").innerHTML = `Days between a law's adoption and the day it applies, for ${fmt(all)} amending acts. <b>${Math.round(100 * within30 / all)}% of them apply within a month. ${N2[fastest]} is fastest (median ${L[fastest].median === 0 ? "the same day" : L[fastest].median + " days"}), ${N2[slowest]} slowest (${Math.round(L[slowest].median)} days).</b> Armenia and Georgia, with more than 23,000 acts between them, sit at two to three weeks. Switzerland's federal law, now loaded in full with its ordinances, waits a median of ${Math.round(L.ch ? L.ch.median : 0)} days.`;
}

// Whole statute books: amending acts per year
{
  const B = S.r5.books, codes = ["mt", "am", "ge"].filter(c => B[c] && Object.keys(B[c]).length);
  const W = 960, H = 320, m = { l: 48, r: 110, t: 20, b: 30 };
  const svg = d3.select("#f-books").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([1995, 2026], [m.l, W - m.r]);
  const y = d3.scaleLinear().domain([0, d3.max(codes, c => d3.max(Object.entries(B[c]).filter(([k]) => +k >= 1995 && +k <= 2025), d => d[1]))]).nice().range([H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(16).tickFormat(d3.format("d")));
  const BC = { mt: "var(--c5)", am: "var(--de)", ge: "var(--ch)" };
  codes.forEach(c => {
    const pts = Object.entries(B[c]).map(([k, n]) => [+k, n]).filter(([k]) => k >= (c === "mt" ? 2021 : 1995) && k <= 2025).sort((a, b) => a[0] - b[0]);
    svg.append("path").datum(pts).attr("fill", "none").attr("stroke", BC[c]).attr("stroke-width", 2.4).attr("d", d3.line().x(d => x(d[0])).y(d => y(d[1])));
    svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => x(d[0])).attr("cy", d => y(d[1])).attr("r", 3).attr("fill", BC[c])
      .append("title").text(d => `${N2[c]} ${d[0]}: ${d[1]} amending acts`);
    const e = pts.at(-1);
    svg.append("text").attr("x", x(e[0]) + 8).attr("y", y(e[1])).attr("dy", "0.32em").attr("class", "ser").attr("font-size", 12.5).text(N2[c]);
  });
  const sum = (c, a, b) => d3.sum(Object.entries(B[c]).filter(([k]) => +k >= a && +k <= b), d => d[1]);
  const avg = c => Math.round(sum(c, 2021, 2025) / 5);
  document.getElementById("books-text").innerHTML = `Amending acts per year in the three jurisdictions whose entire statute book is loaded. 2026 is left out because the year is not over. <b>From 2021 to 2025 Armenia averaged ${avg("am")} amending acts a year, Georgia ${avg("ge")} and Malta ${avg("mt")}.</b> Armenia's rate has more than doubled since 2015 (${sum("am", 2015, 2015)} acts that year against ${sum("am", 2023, 2023)} in 2023). Georgia's swings from year to year, peaking at ${sum("ge", 2018, 2018)} in 2018 and ${sum("ge", 2025, 2025)} in 2025.`;
}

// Georgia: how acts set their start date
{
  const b = S.r5.basis.ge || {}, all = Object.entries(b).sort((a, c) => c[1] - a[1]), total = d3.sum(all, r => r[1]);
  const rows = [...all.slice(0, 5), ["other rules (" + (all.length - 5) + " kinds)", d3.sum(all.slice(5), r => r[1])]];
  const W = 960, rowH = 30, m = { l: 300, r: 90, t: 6, b: 6 }, H = rows.length * rowH + m.t + m.b;
  const svg = d3.select("#f-basis").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, d3.max(rows, r => r[1])], [m.l, W - m.r]);
  rows.forEach(([k, n], i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 10).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "ser").attr("font-size", 13).text(k);
    svg.append("rect").attr("x", m.l).attr("y", y + 6).attr("height", rowH - 12).attr("width", x(n) - m.l).attr("fill", "var(--ch)").attr("rx", 1);
    svg.append("text").attr("x", x(n) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11).attr("class", "lbl").text(`${fmt(n)} · ${Math.round(100 * n / total)}%`);
  });
  const pub = b["on publication"] || 0, dated = b["date in the act"] || 0;
  document.getElementById("basis-text").innerHTML = `Every Georgian amending act states when it starts, and the history records which rule it used. <b>${Math.round(100 * pub / total)}% start on publication, ${Math.round(100 * dated / total)}% on a date written into the act</b>, and ${Math.round(100 * (b["day 15 from publication"] || 0) / total)}% fifteen days after publication. Starting on publication leaves no gap between the text appearing and the duty applying, which fits Georgia's short median lag.`;
}
