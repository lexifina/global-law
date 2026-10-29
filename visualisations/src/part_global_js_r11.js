
// ---- Round 11: volume against delay, calendar styles, the legal year ----
function spearman(xs, ys) {
  const rank = v => { const o = v.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]), r = Array(v.length); o.forEach(([, i], k) => r[i] = k); return r; };
  const rx = rank(xs), ry = rank(ys), mx = d3.mean(rx), my = d3.mean(ry);
  return d3.sum(rx, (x, i) => (x - mx) * (ry[i] - my)) / Math.sqrt(d3.sum(rx, x => (x - mx) ** 2) * d3.sum(ry, y => (y - my) ** 2));
}
function labelledScatter(sel, pts, x, y, W, H, m) {
  const svg = d3.select(sel);
  svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => x(d.vx)).attr("cy", d => y(d.vy)).attr("r", 5.5)
    .attr("fill", "var(--accent)").attr("fill-opacity", .7).append("title").text(d => d.tip);
  const lab = pts.map(d => ({ ...d, px: x(d.vx), ly: y(d.vy) })).sort((a, b) => a.ly - b.ly);
  for (let i = 1; i < lab.length; i++) for (let j = 0; j < i; j++) if (Math.abs(lab[i].px - lab[j].px) < 70 && Math.abs(lab[i].ly - lab[j].ly) < 12) lab[i].ly = lab[j].ly + 12;
  lab.forEach(d => svg.append("text").attr("x", d.px + (d.px > W - 140 ? -8 : 8)).attr("text-anchor", d.px > W - 140 ? "end" : "start").attr("y", d.ly).attr("dy", "0.32em")
    .attr("font-size", 10.5).attr("class", "lbl").attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(d.name));
}

// Volume against delay
{
  const R = J.filter(d => d.lag && d.lag.n >= 10).map(d => ({ ...d, vx: Math.max(.1, d3.sum(d3.range(2015, 2025), y => d.years[y] || 0) / 10), vy: Math.max(.5, d.lag.median) }))
    .filter(d => d.vx > .1);
  const W = 960, H = 440, m = { l: 60, r: 30, t: 20, b: 44 };
  const svg = d3.select("#f-vl").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLog([d3.min(R, d => d.vx) * .7, d3.max(R, d => d.vx) * 1.5], [m.l, W - m.r]);
  const y = d3.scaleLog([.4, d3.max(R, d => d.vy) * 1.6], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(6, "~s"));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([1, 7, 30, 90, 365].filter(v => v <= y.domain()[1])).tickFormat(v => `${v} d`).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  svg.append("text").attr("x", W - m.r).attr("y", H - 8).attr("text-anchor", "end").attr("font-size", 11).text("amending acts per year, 2015–2024");
  svg.append("text").attr("x", m.l + 4).attr("y", m.t - 6).attr("font-size", 11).text("median delay (same day drawn at the bottom)");
  labelledScatter("#f-vl", R.map(d => ({ ...d, tip: `${d.name}: ${d.vx.toFixed(1)} acts a year, median ${d.lag.median} days` })), x, y, W, H, m);
  const rho = spearman(R.map(d => d.vx), R.map(d => d.vy));
  document.getElementById("vl-text").innerHTML = `Each jurisdiction's yearly output of amending acts against how long its law waits to apply. <b>Across ${R.length} jurisdictions the rank correlation is ${rho.toFixed(2)}: ${Math.abs(rho) < .3 ? "volume says little about delay" : rho < 0 ? "busier legislatures tend to apply law sooner" : "busier legislatures tend to wait longer"}.</b>`;
}

// Calendar styles: share on the 1st against share in January
{
  const R = J.filter(d => d.dom && d3.sum(d.dom) >= 30).map(d => ({ ...d, vx: d.dom[0] / d3.sum(d.dom), vy: d.month[0] / d3.sum(d.month) }));
  const W = 960, H = 440, m = { l: 60, r: 30, t: 30, b: 44 };
  const svg = d3.select("#f-cs2").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, Math.max(.85, d3.max(R, d => d.vx) * 1.05)], [m.l, W - m.r]);
  const y = d3.scaleLinear([0, Math.max(.5, d3.max(R, d => d.vy) * 1.1)], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(8).tickFormat(d3.format(".0%")));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).ticks(5).tickFormat(d3.format(".0%")).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  svg.append("line").attr("x1", x(1 / 30.4)).attr("x2", x(1 / 30.4)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--ghost)").attr("stroke-dasharray", "4 4");
  svg.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(1 / 12)).attr("y2", y(1 / 12)).attr("stroke", "var(--ghost)").attr("stroke-dasharray", "4 4");
  svg.append("text").attr("x", W - m.r).attr("y", H - 8).attr("text-anchor", "end").attr("font-size", 11).text("share of acts starting on the 1st of a month");
  svg.append("text").attr("x", m.l + 4).attr("y", m.t - 10).attr("font-size", 11).text("share starting in January");
  labelledScatter("#f-cs2", R.map(d => ({ ...d, tip: `${d.name}: ${Math.round(100 * d.vx)}% on the 1st, ${Math.round(100 * d.vy)}% in January` })), x, y, W, H, m);
  const both = R.filter(d => d.vx >= .4 && d.vy >= .25).map(d => d.name), neither = R.filter(d => d.vx < .15 && d.vy < .15).map(d => d.name);
  document.getElementById("cs2-text").innerHTML = `Two habits that shape a lawyer's calendar: starting law on the 1st of a month, and starting it in January. <b>${both.length ? `${both.join(", ")} do both` : "No jurisdiction does both strongly"}: at least 40% on the 1st and a quarter in January.</b> ${neither.length ? `${neither.join(", ")} do neither, and spread new law across the year and the month.` : ""}`;
}

// The legal year, radial
{
  const R = J.filter(d => d.month && d3.sum(d.month) >= 30), shares = R.map(d => d.month.map(n => n / d3.sum(d.month)));
  const mean = d3.range(12).map(k => d3.mean(shares, s => s[k]));
  const W = 960, H = 520, cx = W / 2, cy = H / 2 + 6, R0 = 40, R1 = 230;
  const svg = d3.select("#f-ly").attr("viewBox", `0 0 ${W} ${H}`);
  const rmax = Math.max(.35, d3.max(shares, s => d3.max(s)));
  const r = d3.scaleLinear([0, rmax], [R0, R1]), ang = k => (k / 12) * 2 * Math.PI - Math.PI / 2;
  [.1, .2, .3].filter(v => v <= rmax).forEach(v => {
    svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", r(v)).attr("fill", "none").attr("stroke", "var(--rule)");
    svg.append("text").attr("x", cx + 4).attr("y", cy - r(v) - 3).attr("font-size", 10).text(`${Math.round(100 * v)}%`);
  });
  svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", r(1 / 12)).attr("fill", "none").attr("stroke", "var(--ghost)").attr("stroke-dasharray", "4 4");
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  MON.forEach((t, k) => svg.append("text").attr("x", cx + (R1 + 18) * Math.cos(ang(k))).attr("y", cy + (R1 + 18) * Math.sin(ang(k))).attr("text-anchor", "middle").attr("dy", "0.32em").attr("font-size", 12).attr("class", "lbl").text(t));
  const line = d3.lineRadial().angle((v, k) => (k / 12) * 2 * Math.PI).radius(v => r(v)).curve(d3.curveCardinalClosed.tension(.4));
  shares.forEach((s, i) => svg.append("path").datum(s).attr("transform", `translate(${cx},${cy})`).attr("d", line).attr("fill", "none").attr("stroke", "var(--accent)").attr("stroke-opacity", .22).attr("stroke-width", 1)
    .append("title").text(R[i].name));
  svg.append("path").datum(mean).attr("transform", `translate(${cx},${cy})`).attr("d", line).attr("fill", "color-mix(in srgb, var(--hi) 15%, transparent)").attr("stroke", "var(--hi)").attr("stroke-width", 2.6);
  const order = mean.map((v, k) => [k, v]).sort((a, b) => b[1] - a[1]);
  const FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  document.getElementById("ly-text").innerHTML = `When the world's law takes effect over the year, with each of ${R.length} jurisdictions counted once. <b>${FULL[order[0][0]]} carries ${Math.round(100 * order[0][1])}% of a typical jurisdiction's new law, ${(order[0][1] * 12).toFixed(1)} times an even share. ${FULL[order[1][0]]} is second (${Math.round(100 * order[1][1])}%), and ${FULL[order.at(-1)[0]]} is the quietest (${Math.round(100 * order.at(-1)[1])}%).</b>`;
}
