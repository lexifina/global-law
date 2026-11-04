from pathlib import Path

p = Path(__file__).parent / "template2.html"
t = p.read_text(encoding="utf-8")

STRIPES = r'''// 3. Law stripes: one row per jurisdiction, one stripe per year, darker = closer to its busiest year
{
  const Rr = DATA.ridges, W = 960, rowH = 24, gap = 3, m = { t: 28, l: 178, r: 120, b: 34 }, H = m.t + Rr.length * (rowH + gap) + m.b;
  const svg = d3.select("#f-ridges").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear().domain([1990, 2026]).range([m.l, W - m.r]), sw = x(1991) - x(1990);
  svg.append("g").selectAll("text").data(d3.range(1990, 2026, 5)).join("text").attr("x", d => x(d) + sw / 2).attr("y", H - 12).attr("text-anchor", "middle").text(d => d);
  svg.append("text").attr("x", W - 4).attr("y", m.t - 10).attr("text-anchor", "end").text("busiest year · acts");
  const rows = svg.append("g").selectAll("g").data(Rr).join("g").attr("transform", (r, i) => `translate(0,${m.t + i * (rowH + gap)})`);
  rows.each(function (r) {
    const sel = d3.select(this), mx = r.peak;
    const yrs = d3.range(r.x0, 2026);
    sel.append("rect").attr("x", x(1990)).attr("width", x(r.x0) - x(1990)).attr("height", rowH).attr("fill", "var(--tint)").attr("opacity", r.x0 > 1990 ? .55 : 0);
    sel.selectAll("rect.s").data(yrs).join("rect").attr("class", "s").attr("x", y => x(y)).attr("width", sw + .6).attr("height", rowH)
      .attr("fill", y => seq(Math.pow((r.years[y] || 0) / mx, .75)));
    sel.append("rect").attr("x", x(r.peak_year) + 1).attr("y", 1).attr("width", sw - 2).attr("height", rowH - 2).attr("fill", "none").attr("stroke", "var(--c2)").attr("stroke-width", 1.6).attr("rx", 2);
    sel.append("text").attr("class", "lbl").attr("x", m.l - 12).attr("y", rowH / 2 + 4).attr("text-anchor", "end").text(r.name);
    sel.append("text").attr("x", W - m.r + 12).attr("y", rowH / 2 + 4).text(`${r.peak_year} · ${fmt(r.peak)}`);
    sel.append("rect").attr("x", m.l).attr("width", W - m.l - m.r).attr("height", rowH).attr("fill", "transparent")
      .on("pointermove", ev => { const yr = Math.floor(x.invert(d3.pointer(ev, this)[0]));
        showTip(ev, `<b>${r.name}, ${yr}</b><br>${r.years[yr] != null ? fmt(r.years[yr]) + " acts took effect" : yr < r.x0 ? "before this record begins" : "no dated acts"}<br><span class="m">busiest year ${r.peak_year} (${fmt(r.peak)} acts)</span>`); })
      .on("pointerleave", hideTip);
  });
}

'''
a = t.index("// 3. Ridgeline"); b = t.index("// 4. Circle packing")
t = t[:a] + STRIPES + t[b:]

R = [
    ('<span class="eyebrow">Twenty-one jurisdictions · acts taking effect each year, 1990–2025</span>',
     '<span class="eyebrow">Twenty-one jurisdictions · acts taking effect each year, 1990–2025</span>'),
    ("Each ridge is one jurisdiction's yearly count of acts taking effect, smoothed and scaled to its own busiest year, sorted by when that year came.",
     "Each row is one jurisdiction and each stripe one year, shaded by how many acts took effect that year relative to its own busiest year (outlined in red). Rows are sorted by when that year came."),
    ('<div class="plot"><svg id="f-ridges" role="img" aria-label="Ridgeline chart of acts per year by jurisdiction"></svg></div>',
     '<div class="legend"><span>acts that year, relative to the busiest</span><span>none</span><span class="ramp"></span><span>busiest</span><span style="margin-left:8px"><i style="background:var(--tint)"></i>before the record begins</span></div>\n  <div class="plot"><svg id="f-ridges" role="img" aria-label="Stripes of acts per year by jurisdiction"></svg></div>'),
    ("Gaussian smoothing with a 0.9-year bandwidth. 2026 is left out because the year is not over. Ridges start where each record starts (Malta 2016, Ontario and Canada 2002). Each repository covers a different share of its jurisdiction's law, so heights compare shapes, not volumes.",
     "Shading uses a 0.75 power so quieter years stay visible. 2026 is left out because the year is not over. Rows start where each record starts (Malta 2016, Ontario and Canada 2002). Each repository covers a different share of its jurisdiction's law, so rows compare rhythms, not volumes."),
    # pack labels: only where they fit at the current zoom
    ('  const fs = d => Math.min(11, d.r / 3.3);', '  const fs = d => Math.min(11, d.r / 2.5), fits = (d, k) => d.r * k >= 21;'),
    ('lab.selectAll("text").data(root.leaves().filter(d => NAMES[d.data.id] && d.r >= 17)).join("text").attr("class", "lbl halo").attr("text-anchor", "middle")',
     'lab.selectAll("text").data(root.leaves().filter(d => NAMES[d.data.id])).join("text").attr("class", "lbl halo").attr("text-anchor", "middle").style("opacity", d => fits(d, 1) ? 1 : 0)'),
    ('lab.selectAll("text").transition().duration(650).style("font-size", x => (d === root ? fs(x) : fs(x) / k) + "px").attr("stroke-width", d === root ? 3.5 : 3.5 / k);',
     'const kk = d === root ? 1 : k;\n    lab.selectAll("text").transition().duration(650).style("font-size", x => Math.min(11, x.r * kk / 2.5) / kk + "px").attr("stroke-width", 3 / kk).style("opacity", x => fits(x, kk) ? 1 : 0);'),
    ("Colour shows how often each norm has been amended. Most are amended at least once, and the darkest are the tax and social-security laws. Click a group to zoom in.",
     "Colour shows how often each norm has been amended. Most are amended at least once, and the darkest are the tax and social-security laws. Click a group to zoom in and name its largest norms."),
]
for a_, b_ in R:
    assert a_ in t, a_[:70]; t = t.replace(a_, b_)
p.write_text(t, encoding="utf-8", newline="\n")
print("patched")
