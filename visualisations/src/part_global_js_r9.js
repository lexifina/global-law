
// ---- Round 9: small multiples, day of month, delay shapes, breadth against depth ----

// Small multiples of acts per year
{
  const years = d3.range(1990, 2027), R = J.filter(d => d3.sum(years, y => d.years[y] || 0) >= 3);
  const cols = 6, W = 960, pw = W / cols, ph = 70, H = Math.ceil(R.length / cols) * ph + 10;
  const svg = d3.select("#f-sm").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([1990, 2026], [8, pw - 8]);
  R.forEach((d, i) => {
    const g = svg.append("g").attr("transform", `translate(${(i % cols) * pw},${Math.floor(i / cols) * ph})`);
    const max = d3.max(years, y => d.years[y] || 0) || 1;
    const y = d3.scaleLinear([0, max], [ph - 14, 22]);
    g.append("rect").attr("x", 4).attr("y", 4).attr("width", pw - 8).attr("height", ph - 8).attr("fill", "var(--tint)").attr("rx", 3);
    g.append("path").datum(years).attr("fill", "color-mix(in srgb, var(--accent) 30%, transparent)").attr("stroke", "var(--accent)").attr("stroke-width", 1.2)
      .attr("d", d3.area().x(yr => x(yr)).y0(ph - 14).y1(yr => y(d.years[yr] || 0)));
    g.append("text").attr("x", 10).attr("y", 17).attr("font-size", 11).attr("class", "lbl").text(d.name);
    g.append("text").attr("x", pw - 10).attr("y", 17).attr("text-anchor", "end").attr("font-size", 10).text(fmt(max));
    g.append("rect").attr("x", 4).attr("y", 4).attr("width", pw - 8).attr("height", ph - 8).attr("fill", "transparent")
      .append("title").text(`${d.name}: ${fmt(d3.sum(years, yr => d.years[yr] || 0))} acts 1990–2026, peak ${max} in ${years.find(yr => (d.years[yr] || 0) === max)}`);
  });
  const peaks = R.map(d => years.find(yr => (d.years[yr] || 0) === d3.max(years, y2 => d.years[y2] || 0)));
  const since2020 = peaks.filter(p => p >= 2020).length;
  document.getElementById("sm-eyebrow").textContent = `${R.length} jurisdictions · round 9`;
  document.getElementById("sm-text").innerHTML = `One small chart per jurisdiction: amending acts per year since 1990, each on its own scale so shapes compare even when sizes do not. <b>${since2020} of ${R.length} histories peak in 2020 or later.</b>`;
}

// Day of the month heatmap
{
  const R = J.filter(d => d3.sum(d.dom || []) >= 30), days = d3.range(1, 32);
  const W = 960, cell = 18, m = { l: 150, r: 90, t: 24, b: 10 }, cw = (W - m.l - m.r) / 31, H = R.length * cell + m.t + m.b;
  const svg = d3.select("#f-dom").attr("viewBox", `0 0 ${W} ${H}`);
  const col = d3.scaleSequentialSqrt(d3.interpolatePuRd).domain([0, .6]);
  days.forEach((dd, j) => { if (dd === 1 || dd % 5 === 0) svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", m.t - 8).attr("text-anchor", "middle").attr("font-size", 10.5).text(dd); });
  const firsts = [];
  R.slice().sort((a, b) => b.dom[0] / d3.sum(b.dom) - a.dom[0] / d3.sum(a.dom)).forEach((d, i) => {
    const y0 = m.t + i * cell, tot = d3.sum(d.dom);
    firsts.push([d.name, d.dom[0] / tot]);
    svg.append("text").attr("x", m.l - 8).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(d.name);
    d.dom.forEach((n, j) => svg.append("rect").attr("x", m.l + j * cw + .5).attr("y", y0 + .5).attr("width", cw - 1).attr("height", cell - 1)
      .attr("fill", col(n / tot)).append("title").text(`${d.name}, day ${j + 1}: ${Math.round(100 * n / tot)}% (${n} of ${tot})`));
    svg.append("text").attr("x", W - m.r + 6).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("font-size", 10.5).text(`${Math.round(100 * d.dom[0] / tot)}% on 1st`);
  });
  const median1st = d3.median(firsts, f => f[1]);
  document.getElementById("dom-text").innerHTML = `The day of the month each act takes effect, sorted by the share starting on the 1st. <b>${firsts.slice(0, 3).map(([n, s]) => `${n} starts ${Math.round(100 * s)}%`).join(", ")} of its acts on the 1st; the median jurisdiction ${Math.round(100 * median1st)}%.</b> At the other end, ${firsts.slice(-2).map(([n, s]) => `${n} (${Math.round(100 * s)}%)`).join(" and ")} spread their start dates across the month.`;
}

// Ridgeline of delay distributions
{
  const R = J.filter(d => d.lag_hist && d3.sum(d.lag_hist) >= 30).sort((a, b) => a.lag.median - b.lag.median);
  const bins = ["same day", "1", "2–3", "4–7", "8–15", "16–31", "32–63", "64–127", "128–255", "256–511", "512–1023", "1024+"];
  const W = 960, rowH = 30, over = 26, m = { l: 150, r: 20, t: 30, b: 30 }, H = R.length * rowH + m.t + m.b + over;
  const svg = d3.select("#f-ridge").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scalePoint(d3.range(12), [m.l + 20, W - m.r - 20]);
  bins.forEach((b, j) => { if (j % 2 === 0 || j === 11) svg.append("text").attr("x", x(j)).attr("y", H - 8).attr("text-anchor", "middle").attr("font-size", 10.5).text(b === "same day" ? b : `${b} d`); });
  R.forEach((d, i) => {
    const base = m.t + over + i * rowH, max = d3.max(d.lag_hist), hh = rowH + over - 4;
    const pts = d.lag_hist.map((n, j) => [x(j), base - hh * n / max]);
    svg.append("path").datum(pts).attr("fill", "color-mix(in srgb, var(--accent) 35%, var(--plate))").attr("stroke", "var(--accent)").attr("stroke-width", 1.3)
      .attr("d", d3.area().curve(d3.curveMonotoneX).x(p => p[0]).y0(base).y1(p => p[1]));
    svg.append("text").attr("x", m.l - 8).attr("y", base - 4).attr("text-anchor", "end").attr("font-size", 11.5).attr("class", "lbl").text(d.name);
  });
  const sameDay = R.map(d => [d.name, d.lag_hist[0] / d3.sum(d.lag_hist)]).sort((a, b) => b[1] - a[1]);
  const twoPeak = R.filter(d => { const h = d.lag_hist; let peaks = 0; for (let j = 1; j < h.length - 1; j++) if (h[j] > h[j - 1] && h[j] >= h[j + 1] && h[j] > .15 * d3.max(h)) peaks++; if (h[0] > h[1] && h[0] > .15 * d3.max(h)) peaks++; return peaks >= 2; });
  document.getElementById("ridge-text").innerHTML = `The full distribution behind each median delay, ordered from fastest to slowest. <b>${sameDay.slice(0, 2).map(([n, s]) => `${n} puts ${Math.round(100 * s)}%`).join(" and ")} of acts into force on the day they are adopted.</b> ${twoPeak.length ? `${twoPeak.map(d => d.name).join(", ")} ${twoPeak.length === 1 ? "has" : "have"} two peaks: one set of acts applies at once and another waits weeks or months.` : ""}`;
}

// Breadth against depth
{
  const R = J.filter(d => d.files > 0 && d.acts > 0);
  const W = 960, H = 440, m = { l: 60, r: 30, t: 20, b: 44 };
  const svg = d3.select("#f-bd").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLog([d3.min(R, d => d.files) * .7, d3.max(R, d => d.files) * 1.4], [m.l, W - m.r]);
  const y = d3.scaleLog([d3.min(R, d => d.acts) * .7, d3.max(R, d => d.acts) * 1.4], [H - m.b, m.t]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(6, "~s"));
  axis(svg.append("g").attr("transform", `translate(${m.l},0)`), d3.axisLeft(y).tickValues([10, 100, 1000, 10000, 100000].filter(v => v >= y.domain()[0] && v <= y.domain()[1])).tickFormat(d3.format("~s")).tickSize(-(W - m.l - m.r))).call(g => g.select(".domain").remove());
  svg.append("text").attr("x", W - m.r).attr("y", H - 8).attr("text-anchor", "end").attr("font-size", 11).text("provision files today (breadth)");
  svg.append("text").attr("x", m.l + 4).attr("y", m.t - 6).attr("font-size", 11).text("dated amending acts (depth)");
  const pts = R.map(d => ({ ...d, px: x(d.files), py: y(d.acts) }));
  svg.append("g").selectAll("circle").data(pts).join("circle").attr("cx", d => d.px).attr("cy", d => d.py).attr("r", 5).attr("fill", "var(--accent)").attr("fill-opacity", .7)
    .append("title").text(d => `${d.name}: ${fmt(d.files)} files, ${fmt(d.acts)} dated acts`);
  const lab = pts.filter(d => d.acts >= 100 || d.files >= 3000).sort((a, b) => a.py - b.py);
  for (let i = 1; i < lab.length; i++) if (Math.abs(lab[i].px - lab[i - 1].px) < 80 && lab[i].py - (lab[i - 1].ly ?? lab[i - 1].py) < 12) lab[i].ly = (lab[i - 1].ly ?? lab[i - 1].py) + 12;
  lab.forEach(d => svg.append("text").attr("x", d.px + 7).attr("y", d.ly ?? d.py).attr("dy", "0.32em").attr("font-size", 10.5).attr("class", "lbl")
    .attr("paint-order", "stroke").attr("stroke", "var(--plate)").attr("stroke-width", 3).text(d.name));
  const wide = R.slice().sort((a, b) => b.files - a.files)[0], deep = R.slice().sort((a, b) => b.acts / b.files - a.acts / a.files)[0];
  document.getElementById("bd-text").innerHTML = `How much law each repository holds today against how much history it records. <b>${wide.name} is the broadest (${fmt(wide.files)} files); ${deep.name} has the most history per file (${(deep.acts / deep.files).toFixed(1)} dated acts each).</b> Points high and to the left are deep histories of a few laws; points low and to the right are broad statute books with comparatively few dated amendments.`;
}
