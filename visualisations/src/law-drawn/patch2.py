from pathlib import Path

HERE = Path(__file__).parent


def patch(name, pairs):
    p = HERE / name; t = p.read_text(encoding="utf-8")
    for a, b in pairs:
        assert a in t, (name, a[:70]); t = t.replace(a, b)
    p.write_text(t, encoding="utf-8", newline="\n")


patch("analyse2.py", [
    ('order = sorted(names, key=lambda n: (AREA_ORDER.index(area[n]), -sum(M[n].values())))',
     'names = [n for n in names if sum(M[n].values())]   # drop laws that never share an act with another\norder = sorted(names, key=lambda n: (AREA_ORDER.index(area[n]), -sum(M[n].values())))'),
    ('    y = {int(a): b for a, b in R["years"][k].items() if 1990 <= int(a) <= 2026}', '    y = {int(a): b for a, b in R["years"][k].items() if 1990 <= int(a) <= 2025}   # 2026 is a partial year'),
    ('    xs = [y0 + i / 4 for i in range(int((2026.75 - y0) * 4) + 1)]', '    xs = [y0 + i / 4 for i in range(int((2026.0 - y0) * 4) + 1)]'),
])

patch("template2.html", [
    ('Spain · 24 of the most-amended laws', 'Spain · 23 of the most-amended laws'),
    ('The courts laws rarely travel with the rest.', 'The justice laws form their own smaller cluster: civil procedure moves with the administrative courts act (18 acts) and the Civil Code (16).'),
    ("Arc length is a law's total ties to the other 23.", "Arc length is a law's total ties to the other 22. The Customs Ordinances, among the most amended, never changed alongside any of these, so they are left out."),
    ('const S = 860, c = S / 2, ro = 268, ri = ro - 14;', 'const S = 860, c = S / 2, ro = 250, ri = ro - 14;'),
    ('acts taking effect each year, 1990–2026', 'acts taking effect each year, 1990–2025'),
    ('Gaussian smoothing with a 0.9-year bandwidth.', 'Gaussian smoothing with a 0.9-year bandwidth. 2026 is left out because the year is not over.'),
    ('const Rr = DATA.ridges, W = 960, step = 27, amp = 74,', 'const Rr = DATA.ridges, W = 960, step = 27, amp = 50,'),
    ('const x = d3.scaleLinear().domain([1990, 2027]).range([m.l, W - m.r]);', 'const x = d3.scaleLinear().domain([1990, 2026]).range([m.l, W - m.r]);'),
    ('    sel.append("path").attr("d", area(pts)).attr("fill", "var(--plate)");',
     '    sel.append("path").attr("d", area(pts)).attr("fill", "var(--plate)");\n    sel.append("path").attr("d", area(pts)).attr("fill", "var(--c1)").attr("fill-opacity", .12);'),
    ('  svg.append("text").attr("x", W - m.r + 12).attr("y", 14).text("busiest year · acts");',
     '  svg.append("text").attr("x", W - 4).attr("y", 14).attr("text-anchor", "end").text("busiest year · acts");'),
    ('    .attr("fill", d => d.data.amended ? seq(cs(d.data.amended)) : "var(--tint)");',
     '    .attr("fill", d => d.data.amended ? seq(cs(d.data.amended)) : "var(--plate)").attr("stroke", d => d.data.amended ? "none" : "var(--ghost)").attr("stroke-width", .6);'),
    ('<span style="margin-left:8px"><i style="background:var(--tint);border:1px solid var(--rule)"></i>never</span>',
     '<span style="margin-left:8px"><i style="background:var(--plate);border:1px solid var(--ghost)"></i>never amended</span>'),
    ('''  const NAMES = { "BOE-A-1889-4763": "Civil Code", "BOE-A-1882-6036": "Criminal Procedure Act", "BOE-A-2020-4859": "Insolvency Act", "BOE-A-2000-323": "Civil Procedure Act",
    "BOE-A-1995-25444": "Criminal Code", "BOE-A-1985-12666": "Judiciary Act", "BOE-A-1885-6627": "Commercial Code", "BOE-A-1947-3843": "Mortgage Regulation",
    "BOE-A-2010-10544": "Companies Act", "BOE-A-2023-3511": "River basin plans 2023", "BOE-A-2016-439": "River basin plans 2016", "BOE-A-1994-14960": "Social Security Act 1994",
    "BOE-A-2015-11724": "Social Security Act" };
  const lab = g.append("g").attr("pointer-events", "none");
  lab.selectAll("text").data(root.leaves().filter(d => NAMES[d.data.id])).join("text").attr("class", "lbl halo").attr("x", d => d.x).attr("y", d => d.y + 4)
    .attr("text-anchor", "middle").style("font-size", "10.5px").text(d => NAMES[d.data.id]);''',
     '''  const NAMES = { "BOE-A-1889-4763": "Civil|Code", "BOE-A-1882-6036": "Criminal|Procedure", "BOE-A-2020-4859": "Insolvency|Act", "BOE-A-2000-323": "Civil|Procedure",
    "BOE-A-1995-25444": "Criminal|Code", "BOE-A-1985-12666": "Judiciary|Act", "BOE-A-1885-6627": "Commercial|Code", "BOE-A-1947-3843": "Mortgage|Regulation",
    "BOE-A-2010-10544": "Companies|Act", "BOE-A-2023-3511": "Basin|plans 2023", "BOE-A-2016-439": "Basin|plans 2016", "BOE-A-1994-14960": "Social|Security '94",
    "BOE-A-2015-11724": "Social|Security", "BOE-A-1973-330": "Navarre|Civil Law", "BOE-A-1984-12106": "Navy|Ordinances" };
  const fs = d => Math.min(11, d.r / 3.3);
  const lab = g.append("g").attr("pointer-events", "none");
  lab.selectAll("text").data(root.leaves().filter(d => NAMES[d.data.id] && d.r >= 17)).join("text").attr("class", "lbl halo").attr("text-anchor", "middle")
    .attr("x", d => d.x).attr("y", d => d.y).style("font-size", d => fs(d) + "px")
    .selectAll("tspan").data(d => NAMES[d.data.id].split("|").map((s, i) => ({ s, i, d }))).join("tspan")
    .attr("x", t => t.d.x).attr("dy", t => t.i ? "1.15em" : "-0.2em").text(t => t.s);'''),
    ('lab.selectAll("text").transition().duration(650).style("font-size", (d === root ? 10.5 : 10.5 / k) + "px").attr("stroke-width", d === root ? 3.5 : 3.5 / k);',
     'lab.selectAll("text").transition().duration(650).style("font-size", x => (d === root ? fs(x) : fs(x) / k) + "px").attr("stroke-width", d === root ? 3.5 : 3.5 / k);'),
    ('{ children: Object.entries(P).map(([g, v]) => ({ name: g,',
     '{ children: Object.entries(P).map(([g, v]) => ({ name: g === "Resolutions, circulars and instructions" ? "Resolutions and circulars" : g,'),
    ('  const note = A.acts.map((a, i) => [a, i]).filter(([a]) => NOTE[a[1]] || a[1].startsWith("Code civil: 214 provisions (Ordonnance n° 2021-1192"));',
     '''  const best = new Map();
  A.acts.forEach((a, i) => { const lab = NOTE[a[1]] || (a[1].includes("Ordonnance n° 2021-1192") ? "Securities, 2021" : null);
    if (lab && (!best.has(lab) || best.get(lab)[0][2] < a[2])) best.set(lab, [a, i]); });
  const note = [...best.values()];'''),
    ('''  placed.forEach((a, k) => { const ty = 22 + (k % 2) * 20;
    svg.append("line").attr("x1", x(a.mid)).attr("x2", x(a.mid)).attr("y1", ty + 4).attr("y2", base).attr("stroke", "var(--c2)").attr("stroke-width", .8).attr("stroke-dasharray", "2 3");
    svg.append("text").attr("class", "lbl halo").attr("x", x(a.mid)).attr("y", ty).attr("text-anchor", "middle").text(`${a.lab} · ${a[2]} art.`); });''',
     '''  placed.forEach((a, k) => { const ty = 20 + (k % 3) * 19, xx = x(a.mid), anchor = xx > W - 150 ? "end" : xx < 150 ? "start" : "middle";
    svg.append("line").attr("x1", xx).attr("x2", xx).attr("y1", ty + 5).attr("y2", base).attr("stroke", "var(--c2)").attr("stroke-width", .8).attr("stroke-dasharray", "2 3");
    svg.append("text").attr("class", "lbl halo").attr("x", anchor === "end" ? xx + 4 : anchor === "start" ? xx - 4 : xx).attr("y", ty).attr("text-anchor", anchor).text(`${a.lab} · ${a[2]} articles`); });'''),
    ('const arcPath = a => { const x0 = x(a[0]), x1 = x(a[1]), rx = (x1 - x0) / 2, ry = Math.min(rx * .9, base - 30);',
     'const arcPath = a => { const x0 = x(a[0]), x1 = x(a[1]), rx = (x1 - x0) / 2, ry = Math.min(rx * .8, base - 80);'),
    ('.attr("stroke", a => seq(.25 + .75 * yr(a[2]))).attr("stroke-width", 1).attr("stroke-opacity", .5);',
     '.attr("stroke", a => seq(.3 + .7 * yr(a[2]))).attr("stroke-width", 1.1).attr("stroke-opacity", .6);'),
    ('paths.attr("stroke-opacity", .5).attr("stroke-width", 1).attr("stroke", a => seq(.25 + .75 * yr(a[2])));',
     'paths.attr("stroke-opacity", .6).attr("stroke-width", 1.1).attr("stroke", a => seq(.3 + .7 * yr(a[2])));'),
    ('.attr("stroke", p => p[3] === a[3] ? "var(--c2)" : seq(.25 + .75 * yr(p[2])));', '.attr("stroke", p => p[3] === a[3] ? "var(--c2)" : seq(.3 + .7 * yr(p[2])));'),
])
print("patched")
