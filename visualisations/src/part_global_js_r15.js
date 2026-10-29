
// ---- Round 15: executive share over time, delay by law-maker ----
{
  const mixed = MK.filter(d => d.maker_years && d.e / (d.e + d.p) >= .2 && d.p / (d.e + d.p) >= .2);
  const W = 960, H = 380, m = { l: 56, r: 130, t: 20, b: 34 };
  const svg = d3.select("#f-et").attr("viewBox", `0 0 ${W} ${H}`);
  const series = mixed.map(d => {
    const dec = {};
    ["parliament", "executive"].forEach(k => Object.entries(d.maker_years[k] || {}).forEach(([y, n]) => {
      const de = Math.floor(+y / 10) * 10; dec[de] = dec[de] || { p: 0, e: 0 }; dec[de][k === "executive" ? "e" : "p"] += n;
    }));
    return { d, pts: Object.entries(dec).map(([de, v]) => [+de, v.e / (v.e + v.p), v.e + v.p]).filter(p => p[2] >= 30 && p[0] <= 2020).sort((a, b) => a[0] - b[0]) };
  }).filter(s => s.pts.length >= 2);
  const x = d3.scaleLinear([d3.min(series, s => s.pts[0][0]) ?? 1950, 2020], [m.l, W - m.r]);
  const y = d3.scaleLinear([0, 1], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(10).tickFormat(d => `${d}s`));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(d3.format(".0%")).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  const labels = [];
  series.forEach((s, i) => {
    const c = PAL8[i % PAL8.length];
    svg.append("path").datum(s.pts).attr("fill", "none").attr("stroke", c).attr("stroke-width", 2.2).attr("d", d3.line().x(p => x(p[0])).y(p => y(p[1])));
    svg.append("g").selectAll("circle").data(s.pts).join("circle").attr("cx", p => x(p[0])).attr("cy", p => y(p[1])).attr("r", 3).attr("fill", c)
      .append("title").text(p => `${s.d.name}, ${p[0]}s: ${Math.round(100 * p[1])}% executive of ${fmt(p[2])} classified acts`);
    const e = s.pts.at(-1); labels.push({ x: x(e[0]), y0: y(e[1]), y: y(e[1]), t: s.d.name, c });
  });
  spread(labels, 14, m.t, H - m.b).forEach(l => svg.append("text").attr("x", l.x + 8).attr("y", l.y).attr("dy", "0.32em").attr("font-size", 11.5).attr("fill", l.c).attr("font-weight", 600).text(l.t));
  const rose = series.filter(s => s.pts.at(-1)[1] > s.pts[0][1] + .05).map(s => `${s.d.name} (${Math.round(100 * s.pts[0][1])}% in the ${s.pts[0][0]}s → ${Math.round(100 * s.pts.at(-1)[1])}% in the ${s.pts.at(-1)[0]}s)`);
  const fell = series.filter(s => s.pts.at(-1)[1] < s.pts[0][1] - .05).map(s => s.d.name);
  document.getElementById("et-text").innerHTML = `In histories that record both laws and executive instruments, the executive's share of new acts decade by decade. <b>${rose.length ? `It rose in ${rose.join(", ")}` : "No history shows a clear rise"}${fell.length ? `; it fell in ${fell.join(", ")}` : ""}.</b>`;
}
{
  const R = J.filter(d => !MAKER_SKIP.has(d.slug) && d.maker_lag && d.maker_lag.parliament && d.maker_lag.executive)
    .map(d => ({ ...d, lp: d.maker_lag.parliament.median, le: d.maker_lag.executive.median })).sort((a, b) => (a.le - a.lp) - (b.le - b.lp));
  const W = 960, rowH = 30, m = { l: 160, r: 200, t: 30, b: 34 }, H = R.length * rowH + m.t + m.b;
  const svg = d3.select("#f-mlg").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleSymlog([0, d3.max(R, d => Math.max(d.lp, d.le)) * 1.2 || 100], [m.l, W - m.r]).constant(3);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).tickValues([0, 3, 7, 14, 30, 90, 180, 365].filter(v => v <= x.domain()[1])).tickFormat(v => v === 0 ? "same day" : `${v} d`).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  [["var(--accent)", "parliament"], ["var(--hi)", "executive"]].forEach(([c, t], k) => {
    svg.append("circle").attr("cx", m.l + 6 + k * 130).attr("cy", 12).attr("r", 5).attr("fill", c);
    svg.append("text").attr("x", m.l + 16 + k * 130).attr("y", 12).attr("dy", "0.32em").attr("font-size", 11).text(t);
  });
  R.forEach((d, i) => {
    const y = m.t + i * rowH + rowH / 2;
    svg.append("text").attr("x", m.l - 8).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 12).attr("class", "lbl").text(d.name);
    svg.append("line").attr("x1", x(d.lp)).attr("x2", x(d.le)).attr("y1", y).attr("y2", y).attr("stroke", "var(--ghost)").attr("stroke-width", 3);
    svg.append("circle").attr("cx", x(d.lp)).attr("cy", y).attr("r", 6).attr("fill", "var(--accent)").append("title").text(`${d.name} parliament: median ${d.lp} days over ${d.maker_lag.parliament.n} acts`);
    svg.append("circle").attr("cx", x(d.le)).attr("cy", y).attr("r", 6).attr("fill", "var(--hi)").append("title").text(`${d.name} executive: median ${d.le} days over ${d.maker_lag.executive.n} acts`);
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11).text(`laws ${d.lp} d · decrees ${d.le} d`);
  });
  const faster = R.filter(d => d.le < d.lp).map(d => d.name), slower = R.filter(d => d.le > d.lp).map(d => d.name);
  document.getElementById("mlg-text").innerHTML = `Median delay for laws made by parliament against instruments made by the government, where a history holds enough of both. <b>${faster.length ? `Executive acts apply sooner in ${faster.join(", ")}` : "Executive acts never apply sooner"}${slower.length ? `; later in ${slower.join(", ")}` : ""}.</b>`;
}
