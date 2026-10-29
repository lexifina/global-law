
// ---- Round 6b: wording life ranked, constitution size, readability everywhere ----
const R10 = S.r10;

// Ranked median life of constitutional wording
{
  const L = R10.life.slice().sort((a, b) => (a.median_years == null) - (b.median_years == null) || (a.median_years ?? 0) - (b.median_years ?? 0) || b.rewritten - a.rewritten);
  const W = 960, rowH = 28, m = { l: 150, r: 220, t: 10, b: 34 }, H = L.length * rowH + m.t + m.b;
  const svg = d3.select("#f-cl").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, 100], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(10).tickFormat(d => `${d} yrs`).tickSize(-(H - m.t - m.b)))
    .call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  L.forEach((d, i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 10).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[d.c]);
    if (d.median_years != null) {
      svg.append("rect").attr("x", m.l).attr("y", y + 6).attr("height", rowH - 12).attr("width", x(d.median_years) - m.l).attr("fill", d.median_years < 15 ? "var(--hi)" : "var(--de)").attr("rx", 1);
      svg.append("text").attr("x", x(d.median_years) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11.5).attr("class", "lbl")
        .text(`${d.median_years.toFixed(1)} years`);
    } else {
      svg.append("rect").attr("x", m.l).attr("y", y + 6).attr("height", rowH - 12).attr("width", x(d.span_years) - m.l).attr("fill", "var(--tint)").attr("stroke", "var(--ghost)").attr("stroke-dasharray", "3 2");
      svg.append("text").attr("x", x(d.span_years) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11)
        .text(`no median: ${Math.round(100 * d.rewritten)}% rewritten in ${Math.round(d.span_years)} yrs`);
    }
  });
  const fast = L.filter(d => d.median_years != null && d.median_years < 15), slow = L.filter(d => d.median_years != null && d.median_years >= 15);
  const still = L.filter(d => d.median_years == null && d.rewritten < .2 && d.span_years > 15);
  document.getElementById("cl-eyebrow").textContent = `${L.length} constitutions · round 6`;
  document.getElementById("cl-text").innerHTML = `How long half of a constitution's wording survives before it is rewritten, ranked. <b>${fast.map(d => N2[d.c]).join(", ")} rewrite half their constitutional text within ${Math.ceil(d3.max(fast, d => d.median_years))} years. ${slow.map(d => N2[d.c]).join(", ")} take ${Math.round(d3.min(slow, d => d.median_years))} to ${Math.round(d3.max(slow, d => d.median_years))}.</b> ${still.map(d => N2[d.c]).join(", ")} have rewritten less than a fifth of their text in more than 15 years. Dashed bars have no median yet and show how long the history runs.`;
}

// Constitution size and article length
{
  const Z = R10.size.slice().sort((a, b) => b.words - a.words);
  const W = 960, rowH = 26, m = { l: 150, r: 40, t: 28, b: 10 }, H = Z.length * rowH + m.t + m.b, mid = 640;
  const svg = d3.select("#f-cs").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, d3.max(Z, d => d.words)], [m.l, mid - 60]);
  const x2 = d3.scaleLinear([0, d3.max(Z, d => d.median_provision)], [mid + 10, W - m.r - 40]);
  svg.append("text").attr("x", m.l).attr("y", 14).attr("font-size", 11).attr("class", "lbl").text("words in force today");
  svg.append("text").attr("x", mid + 10).attr("y", 14).attr("font-size", 11).attr("class", "lbl").text("median words per article");
  Z.forEach((d, i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 10).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[d.c]);
    svg.append("rect").attr("x", m.l).attr("y", y + 5).attr("height", rowH - 10).attr("width", x(d.words) - m.l).attr("fill", C2[d.c] || "var(--c5)").attr("fill-opacity", .8);
    svg.append("text").attr("x", x(d.words) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11).text(fmt(d.words));
    svg.append("rect").attr("x", mid + 10).attr("y", y + 5).attr("height", rowH - 10).attr("width", x2(d.median_provision) - mid - 10).attr("fill", "var(--ghost)");
    svg.append("text").attr("x", x2(d.median_provision) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 11).text(Math.round(d.median_provision));
  });
  const lo = Z.at(-1), hi = Z[0];
  document.getElementById("cs-text").innerHTML = `Every loaded constitution by length today. <b>${N2[hi.c]}'s is the longest at ${fmt(hi.words)} words, ${Math.round(hi.words / lo.words)} times ${N2[lo.c]}'s ${fmt(lo.words)}.</b> Length comes from article size as much as article count: a median ${Math.round(Z.find(d => d.c === "gi")?.median_provision || 0)} words per section in Gibraltar against ${Math.round(Z.find(d => d.c === "ee")?.median_provision || 0)} in Estonia.`;
}

// Readability, founding text against amendments, every constitution
{
  const Rd = R10.read.slice().sort((a, b) => (b.a / b.o) - (a.a / a.o));
  const W = 960, rowH = 30, m = { l: 150, r: 170, t: 26, b: 34 }, H = Rd.length * rowH + m.t + m.b;
  const svg = d3.select("#f-cread").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([10, 35], [m.l, W - m.r]);
  axis(svg.append("g").attr("transform", `translate(0,${H - m.b})`), d3.axisBottom(x).ticks(6).tickSize(-(H - m.t - m.b))).call(g => g.selectAll("line").attr("stroke-dasharray", "2 4"));
  svg.append("text").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").attr("font-size", 11).text("median words per sentence");
  Rd.forEach((r, i) => {
    const y = m.t + i * rowH + rowH / 2, up = r.a > r.o;
    svg.append("text").attr("x", m.l - 10).attr("y", y).attr("dy", "0.32em").attr("text-anchor", "end").attr("class", "lbl").attr("font-size", 12.5).text(N2[r.c]);
    svg.append("line").attr("x1", x(r.o)).attr("x2", x(r.a)).attr("y1", y).attr("y2", y).attr("stroke", up ? "var(--hi)" : "var(--now)").attr("stroke-opacity", .5).attr("stroke-width", 3);
    svg.append("circle").attr("cx", x(r.o)).attr("cy", y).attr("r", 5.5).attr("fill", "var(--plate)").attr("stroke", "var(--ink)").attr("stroke-width", 1.5);
    svg.append("circle").attr("cx", x(r.a)).attr("cy", y).attr("r", 5.5).attr("fill", up ? "var(--hi)" : "var(--now)");
    svg.append("text").attr("x", W - m.r + 10).attr("y", y).attr("dy", "0.32em").attr("font-size", 11.5).attr("class", "lbl")
      .text(`${r.o.toFixed(1)} → ${r.a.toFixed(1)} (${up ? "+" : ""}${Math.round((r.a / r.o - 1) * 100)}%)`);
  });
  const ups = Rd.filter(r => r.a > r.o), downs = Rd.filter(r => r.a <= r.o);
  document.getElementById("cread-text").innerHTML = `Sentence length in each constitution's founding text against wording added later by amendment. <b>In ${ups.length} of ${Rd.length} constitutions amendments write longer sentences${downs.length ? `; ${downs.map(r => N2[r.c]).join(" and ")} ${downs.length === 1 ? "is the exception" : "are the exceptions"}` : ""}.</b> The biggest increases are in ${Rd.slice(0, 3).map(r => `${N2[r.c]} (+${Math.round((r.a / r.o - 1) * 100)}%)`).join(", ")}.`;
}
