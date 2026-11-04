from pathlib import Path

p = Path(__file__).parent / "template_ro.html"
t = p.read_text(encoding="utf-8")
R = [
    # 1. Prime-minister strip: neutral tints with surnames, so it does not reuse the act colours
    ('''  PM.forEach(([n, a, b, bl]) => { const x0 = tx(a), x1 = Math.min(tx(b), W - m.r);
    svg.append("rect").attr("x", x0).attr("width", Math.max(1, x1 - x0 - 1)).attr("y", pb).attr("height", 8).attr("fill", `var(${BLOC[bl]})`).attr("opacity", .8)''',
     '''  PM.forEach(([n, a, b, bl], k) => { const x0 = tx(a), x1 = Math.min(tx(b), W - m.r), sur = n.split(" ").slice(-1)[0].replace("Popescu-", "");
    svg.append("rect").attr("x", x0).attr("width", Math.max(1, x1 - x0 - 1)).attr("y", pb - 8).attr("height", 16).attr("fill", k % 2 ? "var(--tint)" : "var(--rule)").attr("rx", 2)
      .on("pointermove", ev => showTip(ev, `<b>${n}</b><br>${fmtDate(new Date(a))} to ${fmtDate(new Date(b))}<br><span class="m">${bl}</span>`)).on("pointerleave", hideTip);
    if (x1 - x0 > sur.length * 5.6 + 6) svg.append("text").attr("x", (x0 + x1) / 2).attr("y", pb + 3.5).attr("text-anchor", "middle").attr("pointer-events", "none").style("font-size", "9px").attr("class", "lbl").text(sur);
    if (false) svg.append("rect")'''),
    ('svg.append("text").attr("x", m.l - 8).attr("y", pb + 7).attr("text-anchor", "end").style("font-size", "10px").text("PM");',
     'svg.append("text").attr("x", m.l - 8).attr("y", pb + 4).attr("text-anchor", "end").style("font-size", "10px").text("PM");'),
    ("The strip below the axis shows who was prime minister.", "The strip below shows who was prime minister; hover it for full names and dates."),
    # 2. Prime-minister chart: room for names and terms
    ('const P = DATA.pm, W = 960, rh = 26, m = { t: 8, l: 200, r: 120, b: 30 }', 'const P = DATA.pm, W = 960, rh = 26, m = { t: 8, l: 250, r: 120, b: 30 }'),
    ('''    svg.append("text").attr("x", m.l - 10).attr("y", yy + rh / 2 + 4).attr("text-anchor", "end").attr("dx", -p.name.length * 6.6 - 8).style("font-size", "10px").text(`${p.from.slice(0, 4)}–${p.to.slice(2, 4)}`);''',
     '''    svg.append("text").attr("x", 4).attr("y", yy + rh / 2 + 4).style("font-size", "10px").text(`${p.from.slice(0, 4)}–${p.to.slice(0, 4)}`);'''),
    # 3. Codes: smaller ring, readable names, labels spaced apart
    ('const Hb = DATA.hubs, keys = Object.keys(Hb), COL = ["--c1", "--c2", "--c3", "--c4", "--ghost"], S = 820, c = S / 2, R = 330;',
     'const Hb = DATA.hubs, keys = Object.keys(Hb), COL = ["--c1", "--c2", "--c3", "--c4", "--ghost"], S = 820, c = S / 2, R = 292;'),
    ('''  const hard = d3.rollups(links, v => d3.sum(v, l => l.n), l => l.t).sort((a, b) => b[1] - a[1]).slice(0, 10).map(d => d[0]);''',
     '''  const NICE = { "Codul civil din 1864": "Civil Code of 1864", "Codul comercial din 1887": "Commercial Code of 1887", "Codul de procedură civilă din 1865": "Civil Procedure Code of 1865",
    "Codul penal din 1969": "Criminal Code of 1969", "Codul de procedură penală din 1969": "Criminal Procedure Code of 1969" };
  const ranked = d3.rollups(links, v => d3.sum(v, l => l.n), l => l.t).sort((a, b) => b[1] - a[1]).map(d => d[0]), hard = [];
  for (const t of ranked) { if (hard.length >= 10) break; const a = ang.get(t); if (hard.every(h => Math.abs(Math.atan2(Math.sin(a - ang.get(h)), Math.cos(a - ang.get(h)))) > .2)) hard.push(t); }'''),
    ('.attr("text-anchor", t => Math.cos(ang.get(t)) < 0 ? "end" : "start").attr("dy", "0.35em").text(t => t.replace("Codul ", "Cod. ").slice(0, 34));',
     '.attr("text-anchor", t => Math.cos(ang.get(t)) < 0 ? "end" : "start").attr("dy", "0.35em").text(t => NICE[t] || t);'),
    # 4. Approval chart: median label rounded and clear of the dots
    ('''  svg.append("text").attr("class", "lbl halo").attr("x", W - m.r - 4).attr("y", y(med) - 6).attr("text-anchor", "end").text(`median ${med} days`);''',
     '''  svg.append("text").attr("class", "lbl halo").attr("x", m.l + 6).attr("y", y(med) - 6).text(`median ${Math.round(med)} days`);'''),
    # 5. Fiscal and rectification source notes
    ('"Unexplained" means the official consolidation changed with no act named.</p>',
     '"Unexplained" means the official consolidation changed with no act named. The record holds almost no changes for 2011 and 2012, which is likely a gap in the sources rather than a quiet spell.</p>'),
    ('matched to the corrected act\'s publication date. The axis is logarithmic.</p>',
     'matched to the corrected act\'s first publication date. A correction to a later republication still counts from the first, which is why a few come years later. The axis is logarithmic.</p>'),
    ("`${d3.median(lags)} days`", "`${Math.round(d3.median(lags))} days`"),
]
for a, b in R:
    assert a in t, a[:80]; t = t.replace(a, b)
p.write_text(t, encoding="utf-8", newline="\n")
print("patched")
