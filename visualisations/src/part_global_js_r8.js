
// ---- Round 8: centuries, acceleration, lag trend, adoption calendar ----
const PAL8 = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"];

// Two centuries: acts per decade for long histories
{
  const L = J.filter(d => d.last - d.first >= 80 && d.acts >= 100);
  const decades = d3.range(1800, 2030, 10);
  const W = 960, H = 380, m = { l: 52, r: 120, t: 20, b: 34 };
  const svg = d3.select("#f-cent").attr("viewBox", `0 0 ${W} ${H}`);
  const series = L.map(d => ({ d, pts: decades.map(dc => [dc, d3.sum(d3.range(dc, dc + 10), y => d.years[y] || 0)]).filter(([dc]) => dc >= Math.floor(d.first / 10) * 10) }));
  const x = d3.scaleLinear([1800, 2020], [m.l, W - m.r]);
  const y = d3.scaleSymlog().constant(1).domain([0, d3.max(series, s => d3.max(s.pts, p => p[1]))]).range([H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(12).tickFormat(d3.format("d")));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([0, 10, 100, 1000, 10000, 100000].filter(v => v <= y.domain()[1])).tickFormat(d3.format("~s")).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  const labels = [];
  series.forEach((s, i) => {
    const c = PAL8[i % PAL8.length];
    svg.append("path").datum(s.pts).attr("fill", "none").attr("stroke", c).attr("stroke-width", 2.2).attr("d", d3.line().x(p => x(p[0] + 5)).y(p => y(p[1])));
    svg.append("g").selectAll("circle").data(s.pts).join("circle").attr("cx", p => x(p[0] + 5)).attr("cy", p => y(p[1])).attr("r", 2.6).attr("fill", c)
      .append("title").text(p => `${s.d.name}, ${p[0]}s: ${fmt(p[1])} acts`);
    const e = s.pts.at(-1); labels.push({ x: x(e[0] + 5), y0: y(e[1]), y: y(e[1]), t: s.d.name, c });
  });
  spread(labels, 14, m.t, H - m.b).forEach(l => svg.append("text").attr("x", l.x + 8).attr("y", l.y).attr("dy", "0.32em").attr("font-size", 11.5).attr("fill", l.c).attr("font-weight", 600).text(l.t));
  const fr = J.find(d => d.slug === "france");
  const peakDec = fr ? decades.map(dc => [dc, d3.sum(d3.range(dc, dc + 10), y => fr.years[y] || 0)]).sort((a, b) => b[1] - a[1])[0] : null;
  document.getElementById("cent-text").innerHTML = `Amending acts per decade in the ${L.length} histories that span at least 80 years: ${L.map(d => d.name).join(", ")}. <b>${fr ? `France's busiest decade is the ${peakDec[0]}s, with ${fmt(peakDec[1])} acts. ` : ""}${(() => { const dsum = (d, a) => d3.sum(d3.range(a, a + 10), y => d.years[y] || 0); const ten = L.filter(d => dsum(d, 1950) > 0 && dsum(d, 2000) >= 10 * dsum(d, 1950)); return ten.length ? `${ten.map(d => `${d.name} (×${Math.round(dsum(d, 2000) / dsum(d, 1950))})`).join(" and ")} grew more than tenfold between the 1950s and the 2000s.` : ""; })()}</b> The scale is logarithmic, so equal steps are tenfold increases.`;
}

// Acceleration: 2010–14 against 2020–24
{
  const avg = (d, a, b) => d3.sum(d3.range(a, b + 1), y => d.years[y] || 0) / (b - a + 1);
  const R = J.map(d => ({ ...d, a: avg(d, 2010, 2014), b: avg(d, 2020, 2024) })).filter(d => d.a * 5 >= 20 && d.b * 5 >= 20).sort((p, q) => q.b / q.a - p.b / p.a);
  const W = 960, H = 440, m = { l: 200, r: 200, t: 30, b: 20 };
  const svg = d3.select("#f-acc").attr("viewBox", `0 0 ${W} ${H}`);
  const y = d3.scaleLog([d3.min(R, d => Math.min(d.a, d.b)) * .8, d3.max(R, d => Math.max(d.a, d.b)) * 1.2], [H - m.b, m.t]);
  const x1 = m.l + 40, x2 = W - m.r - 40;
  svg.append("text").attr("x", x1).attr("y", 16).attr("text-anchor", "middle").attr("class", "lbl").attr("font-size", 12).text("2010–2014");
  svg.append("text").attr("x", x2).attr("y", 16).attr("text-anchor", "middle").attr("class", "lbl").attr("font-size", 12).text("2020–2024");
  const L1 = [], L2 = [];
  R.forEach(d => {
    const up = d.b > d.a;
    svg.append("line").attr("x1", x1).attr("x2", x2).attr("y1", y(d.a)).attr("y2", y(d.b)).attr("stroke", up ? "var(--hi)" : "var(--now)").attr("stroke-width", 2).attr("stroke-opacity", .75)
      .append("title").text(`${d.name}: ${d.a.toFixed(1)} → ${d.b.toFixed(1)} acts a year`);
    svg.append("circle").attr("cx", x1).attr("cy", y(d.a)).attr("r", 3.5).attr("fill", "var(--ink)");
    svg.append("circle").attr("cx", x2).attr("cy", y(d.b)).attr("r", 3.5).attr("fill", up ? "var(--hi)" : "var(--now)");
    L1.push({ y0: y(d.a), y: y(d.a), t: `${d.name} ${fmt(Math.round(d.a))}` });
    L2.push({ y0: y(d.b), y: y(d.b), t: `${fmt(Math.round(d.b))} ${d.name} (${up ? "+" : ""}${Math.round(100 * (d.b / d.a - 1))}%)` });
  });
  spread(L1, 13, m.t, H - m.b).forEach(l => svg.append("text").attr("x", x1 - 8).attr("y", l.y).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).text(l.t));
  spread(L2, 13, m.t, H - m.b).forEach(l => svg.append("text").attr("x", x2 + 8).attr("y", l.y).attr("dy", "0.32em").attr("font-size", 11).text(l.t));
  const ups = R.filter(d => d.b > d.a);
  document.getElementById("acc-text").innerHTML = `Average amending acts a year in 2010–2014 against 2020–2024. <b>${ups.length} of ${R.length} jurisdictions legislate more than a decade ago. The biggest rise is ${R[0].name}'s (${Math.round(100 * (R[0].b / R[0].a - 1))}%), the biggest fall ${R.at(-1).name}'s (${Math.round(100 * (R.at(-1).b / R.at(-1).a - 1))}%).</b> Some of the change reflects how each history was assembled, so read single countries with care.`;
}

// Lag trend by decade of adoption
{
  const R = J.filter(d => d.lag_by_decade && Object.keys(d.lag_by_decade).length >= 2);
  const W = 960, H = 380, m = { l: 56, r: 130, t: 20, b: 34 };
  const svg = d3.select("#f-lt").attr("viewBox", `0 0 ${W} ${H}`);
  const all = R.flatMap(d => Object.entries(d.lag_by_decade).map(([k, v]) => [+k, v.median])).filter(p => p[0] <= 2020 && p[1] >= 0 && p[1] <= 730);
  const offscale = R.flatMap(d => Object.entries(d.lag_by_decade).filter(([k, v]) => +k >= 1940 && +k <= 2020 && (v.median > 730 || v.median < 0)).map(([k]) => `${d.name} ${k}s`));
  const x = d3.scaleLinear([d3.max([1940, d3.min(all, p => p[0])]), 2020], [m.l, W - m.r]);
  const y = d3.scaleSymlog().constant(3).domain([0, d3.max(all, p => p[1]) * 1.1]).range([H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(9).tickFormat(d => `${d}s`));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([0, 7, 14, 30, 90, 180, 365].filter(v => v <= y.domain()[1])).tickFormat(v => v === 0 ? "0" : `${v} d`).tickSize(-(W - m.l - m.r)))
    .call(g => g.select(".domain").remove());
  const labels = [];
  R.forEach((d, i) => {
    const pts = Object.entries(d.lag_by_decade).map(([k, v]) => [+k, v.median, v.n]).filter(p => p[0] >= x.domain()[0] && p[0] <= 2020 && p[1] >= 0 && p[1] <= 730).sort((a, b) => a[0] - b[0]);
    if (pts.length < 2) return;
    const c = PAL8[i % PAL8.length];
    svg.append("path").datum(pts).attr("fill", "none").attr("stroke", c).attr("stroke-width", 2).attr("d", d3.line().x(p => x(p[0])).y(p => y(p[1])));
    svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", p => x(p[0])).attr("cy", p => y(p[1])).attr("r", 3).attr("fill", c)
      .append("title").text(p => `${d.name}, ${p[0]}s: median ${p[1]} days over ${p[2]} acts`);
    const e = pts.at(-1); labels.push({ x: x(e[0]), y0: y(e[1]), y: y(e[1]), t: d.name, c });
  });
  spread(labels, 13, m.t, H - m.b).forEach(l => svg.append("text").attr("x", l.x + 8).attr("y", l.y).attr("dy", "0.32em").attr("font-size", 11).attr("fill", l.c).attr("font-weight", 600).text(l.t));
  const ok = d => Object.entries(d.lag_by_decade).filter(([k, v]) => +k >= 1940 && +k <= 2020 && v.median >= 0 && v.median <= 730).sort((a, b) => a[0] - b[0]);
  const faster = R.filter(d => { const e = ok(d); return e.length >= 2 && e.at(-1)[1].median < e[0][1].median; });
  const counted = R.filter(d => ok(d).length >= 2);
  document.getElementById("lt-text").innerHTML = `Median delay from adoption to entry into force, by the decade a law was adopted. <b>${faster.length} of ${counted.length} jurisdictions apply their law faster in their latest decade than in their earliest: ${faster.map(d => d.name).join(", ")}.</b>${offscale.length ? ` Medians above two years are left off the scale: ${offscale.join(", ")}.` : ""}`;
}

// Adoption weekday and month, reusing the share heatmap
shareHeat("#f-awd", "adopt_weekday", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "awd-text", R => {
  const RR = R.filter(d => d3.sum(d.adopt_weekday || []) >= 30);
  const names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const tops = RR.map(d => [d.name, d.adopt_weekday.indexOf(Math.max(...d.adopt_weekday)), Math.max(...d.adopt_weekday) / d3.sum(d.adopt_weekday)]).sort((a, b) => b[2] - a[2]);
  return `The weekday each act was adopted: signed, enacted or voted, depending on what each source records. <b>${(() => { const wk = RR.map(d => [d.name, (d.adopt_weekday[5] + d.adopt_weekday[6]) / d3.sum(d.adopt_weekday)]); const hi = wk.filter(w => w[1] >= .1); return hi.length ? `Fewer than a tenth of acts are adopted at weekends everywhere except ${hi.map(([n, s]) => `${n} (${Math.round(100 * s)}%)`).join(", ")}.` : "Fewer than a tenth of acts are adopted at weekends everywhere."; })()}</b> The sharpest single-day habits are ${tops.slice(0, 3).map(([n, w, s]) => `${n} on ${names[w]}s (${Math.round(100 * s)}%)`).join(", ")}.`;
});
shareHeat("#f-amon", "adopt_month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "amon-text", R => {
  const RR = R.filter(d => d3.sum(d.adopt_month || []) >= 30);
  const dec = RR.map(d => [d.name, d.adopt_month[11] / d3.sum(d.adopt_month)]).sort((a, b) => b[1] - a[1]);
  const decTop = RR.filter(d => d.adopt_month.indexOf(Math.max(...d.adopt_month)) === 11);
  const aug = RR.map(d => [d.name, d.adopt_month[7] / d3.sum(d.adopt_month)]).sort((a, b) => a[1] - b[1]);
  return `The month each act was adopted. <b>December is the busiest month in ${decTop.length} of ${RR.length} jurisdictions</b>, led by ${dec.slice(0, 3).map(([n, s]) => `${n} (${Math.round(100 * s)}%)`).join(", ")}. August is the quietest month in ${RR.filter(d => d.adopt_month[7] === Math.min(...d.adopt_month)).length} of ${RR.length}.`;
});
