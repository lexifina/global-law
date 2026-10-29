
// ---- Round 12: retroactivity, same-day law, weekend starts ----
function rankedBars(sel, rows, fmtv, colour) {
  const W = 960, rowH = 22, m = { l: 160, r: 120, t: 6, b: 6 }, H = rows.length * rowH + m.t + m.b;
  const svg = d3.select(sel).attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear([0, d3.max(rows, r => r.v) || 1], [m.l, W - m.r]);
  rows.forEach((r, i) => {
    const y = m.t + i * rowH;
    svg.append("text").attr("x", m.l - 8).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("text-anchor", "end").attr("font-size", 11.5).attr("class", "lbl").text(r.name);
    svg.append("rect").attr("x", m.l).attr("y", y + 4).attr("height", rowH - 8).attr("width", Math.max(1, x(r.v) - m.l)).attr("fill", colour).attr("rx", 1)
      .append("title").text(`${r.name}: ${fmtv(r)}`);
    svg.append("text").attr("x", x(r.v) + 6).attr("y", y + rowH / 2).attr("dy", "0.32em").attr("font-size", 10.5).text(fmtv(r));
  });
}

// Retroactive application
{
  const R = J.filter(d => d.lag_n >= 10).map(d => ({ name: d.name, v: d.lag_neg / d.lag_n, k: d.lag_neg, n: d.lag_n })).sort((a, b) => b.v - a.v);
  rankedBars("#f-retro", R, r => `${(100 * r.v).toFixed(1)}% (${fmt(r.k)} of ${fmt(r.n)})`, "var(--hi)");
  const any = R.filter(r => r.k > 0), none = R.filter(r => r.k === 0).map(r => r.name), tot = d3.sum(R, r => r.k), all = d3.sum(R, r => r.n);
  document.getElementById("retro-text").innerHTML = `How often an act's recorded in-force date is earlier than its adoption date. <b>${fmt(tot)} of ${fmt(all)} dated acts (${(100 * tot / all).toFixed(1)}%) apply before they are adopted, in ${any.length} of ${R.length} jurisdictions. The highest share is ${R[0].name}'s (${(100 * R[0].v).toFixed(1)}%).</b> ${none.length ? `${none.join(", ")} record none.` : ""} Some of these are deliberate retroactive provisions, such as a patent provision in the US Consolidated Appropriations Act 2021 that applied from 179 days before enactment; others may be recording errors worth checking.`;
}

// Same-day application
{
  const R = J.filter(d => d.lag_n >= 10 && d.lag_hist).map(d => ({ name: d.name, v: d.lag_hist[0] / d.lag_n, k: d.lag_hist[0], n: d.lag_n })).sort((a, b) => b.v - a.v);
  rankedBars("#f-sd", R, r => `${Math.round(100 * r.v)}%`, "var(--now)");
  const half = R.filter(r => r.v >= .5).map(r => r.name), rare = R.filter(r => r.v < .02).map(r => r.name);
  document.getElementById("sd-text").innerHTML = `The share of acts that apply on the very day they are adopted. <b>${half.length ? `${half.length > 1 ? half.slice(0, -1).join(", ") + " and " + half.at(-1) : half[0]} apply at least half their acts the same day` : "No jurisdiction applies half its acts the same day"}; ${rare.length} jurisdictions almost never do (under 2%): ${rare.join(", ")}.</b>`;
}

// Weekend starts, mapped
{
  const val = d => d.weekday && d3.sum(d.weekday) >= 30 ? (d.weekday[5] + d.weekday[6]) / d3.sum(d.weekday) : null;
  const col = d3.scaleSequential(d3.interpolateBuPu).domain([0, .45]);
  worldMap("#f-mw", val, col, { fmt: v => `${Math.round(100 * v)}% start at the weekend`, items: [[0, "0%"], [.1, "10%"], [.2, "20%"], [.29, "29% (random)"], [.45, "45%"]] });
  const R = J.filter(d => val(d) != null).map(d => [d.name, val(d)]).sort((a, b) => b[1] - a[1]);
  const low = R.filter(r => r[1] < .05).map(r => r[0]);
  document.getElementById("mw-text").innerHTML = `The share of each jurisdiction's law whose start date is a Saturday or Sunday. A random date would give 29%. <b>${R.slice(0, 3).map(([n, v]) => `${n} (${Math.round(100 * v)}%)`).join(", ")} start the most law at weekends; ${low.length ? `${low.join(", ")} almost never do (under 5%)` : "no jurisdiction is under 5%"}.</b>`;
}
