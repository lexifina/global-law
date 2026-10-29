
// ---- Round 16: the legal year day by day ----
const DAYS = (() => { const out = []; for (let m = 1; m <= 12; m++) for (let d = 1; d <= new Date(Date.UTC(2024, m, 0)).getUTCDate(); d++) out.push(`${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`); return out; })();
const DOYJ = J.filter(d => d.doy && d.acts >= 100);
const dayLabel = k => { const [m, d] = k.split("-").map(Number); return `${d} ${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][m - 1]}`; };
{
  const R = DOYJ.slice().sort((a, b) => b.acts - a.acts);
  const W = 960, cell = 16, m = { l: 150, r: 10, t: 24, b: 10 }, cw = (W - m.l - m.r) / DAYS.length, H = R.length * cell + m.t + m.b;
  const svg = d3.select("#f-cst").attr("viewBox", `0 0 ${W} ${H}`);
  ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].forEach((t, k) => {
    const j = DAYS.indexOf(`${String(k + 1).padStart(2, "0")}-01`);
    svg.append("text").attr("x", m.l + j * cw).attr("y", m.t - 8).attr("font-size", 10.5).text(t);
    svg.append("line").attr("x1", m.l + j * cw).attr("x2", m.l + j * cw).attr("y1", m.t - 4).attr("y2", H - m.b).attr("stroke", "var(--rule)");
  });
  R.forEach((d, i) => {
    const y0 = m.t + i * cell, tot = d3.sum(Object.values(d.doy)), max = d3.max(Object.values(d.doy));
    const col = d3.scaleSequentialSqrt(d3.interpolateGreys).domain([0, max]);
    svg.append("text").attr("x", m.l - 8).attr("y", y0 + cell / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11).attr("class", "lbl").text(d.name);
    DAYS.forEach((k, j) => {
      const n = d.doy[k] || 0;
      if (n) svg.append("rect").attr("x", m.l + j * cw).attr("y", y0 + 1).attr("width", Math.max(1, cw)).attr("height", cell - 2).attr("fill", col(n))
        .append("title").text(`${d.name}, ${dayLabel(k)}: ${n} acts (${(100 * n / tot).toFixed(1)}%)`);
    });
  });
  const tops = R.map(d => { const e = Object.entries(d.doy).sort((a, b) => b[1] - a[1])[0]; return [d.name, e[0], e[1] / d3.sum(Object.values(d.doy))]; });
  const jan1 = tops.filter(t => t[1] === "01-01").map(t => t[0]);
  document.getElementById("cst-text").innerHTML = `Every calendar day for every jurisdiction with at least 100 dated acts. Vertical lines mark the first of each month. <b>1 January is the single busiest day in ${jan1.length} of ${R.length} (${jan1.join(", ")}).</b> ${tops.filter(t => t[1] !== "01-01").slice(0, 4).map(([n, k, s]) => `${n}'s busiest day is ${dayLabel(k)} (${(100 * s).toFixed(1)}%)`).join("; ")}.`;
}
{
  const shares = DOYJ.map(d => { const tot = d3.sum(Object.values(d.doy)); return { d, s: Object.fromEntries(Object.entries(d.doy).map(([k, n]) => [k, n / tot])) }; });
  const avg = DAYS.map(k => [k, d3.mean(shares, x => x.s[k] || 0)]).sort((a, b) => b[1] - a[1]).slice(0, 15);
  const W = 960, rowH = 26, m = { l: 90, r: 360, t: 6, b: 6 }, H = avg.length * rowH + m.t + m.b;
  const svg = d3.select("#f-td").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, avg[0][1]], [m.l, W - m.r]);
  avg.forEach(([k, v], i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 12).attr("class", "lbl").text(dayLabel(k));
    svg.append("rect").attr("x", m.l).attr("y", y + 5).attr("height", rowH - 10).attr("width", x(v) - m.l).attr("fill", "var(--accent)").attr("rx", 1);
    const lead = shares.map(x2 => [x2.d.name, x2.s[k] || 0]).sort((a, b) => b[1] - a[1]).slice(0, 3);
    svg.append("text").attr("x", x(v) + 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 10.5)
      .text(`${(100 * v).toFixed(1)}% · ${lead.map(([n, s]) => `${n} ${Math.round(100 * s)}%`).join(", ")}`);
  });
  const firsts = avg.filter(([k]) => k.endsWith("-01")).length;
  document.getElementById("td-text").innerHTML = `The calendar dates on which the most law takes effect, averaging each jurisdiction's share so none dominates. <b>${dayLabel(avg[0][0])} leads, carrying ${(100 * avg[0][1]).toFixed(1)}% of a typical jurisdiction's acts, against 0.3% for an average day. ${firsts} of the top ${avg.length} dates are the first of a month.</b>`;
}
