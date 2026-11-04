from pathlib import Path

HERE = Path(__file__).parent


def patch(name, pairs):
    p = HERE / name; t = p.read_text(encoding="utf-8")
    for a, b in pairs:
        assert a in t, (name, a[:70]); t = t.replace(a, b)
    p.write_text(t, encoding="utf-8", newline="\n")


patch("section3.js", [
    ('    const PAR = [...new Set(K.nodes.map(n => n.group))], pc = new Map(PAR.map((p, i) => [p, ["--c1", "--c2", "--c3", "--c4"][i] || "--ghost"]));\n    legendDots("lg-copies", PAR.map(p => [p, pc.get(p)]));',
     '    const tc = new Map(K.themes.map((t, i) => [t, ["--c1", "--c2", "--c3", "--c4"][i] || "--ghost"]));\n'
     '    document.getElementById("lg-copies").innerHTML = K.themes.map(t => `<span><i style="width:16px;height:3px;border-radius:2px;background:var(${tc.get(t)})"></i>${t}</span>`).join("")\n'
     '      + `<span><i style="background:var(--ink)"></i>town (size: articles shared)</span>`;'),
    ('links = K.links.map(l => ({ source: l[0], target: l[1], n: l[2] }));', 'links = K.links.map(l => ({ source: l[0], target: l[1], n: l[2], theme: l[3] }));'),
    ('      .attr("stroke", "var(--muted)").attr("stroke-opacity", l => .15 + .6 * l.n / wmax).attr("stroke-width", l => .6 + 3.4 * Math.sqrt(l.n / wmax));',
     '      .attr("stroke", l => `var(${tc.get(l.theme)})`).attr("stroke-opacity", l => .35 + .55 * l.n / wmax).attr("stroke-width", l => .8 + 3.6 * Math.sqrt(l.n / wmax));'),
    ('      .attr("fill", n => `var(${pc.get(n.group)})`).attr("stroke", "var(--plate)").attr("stroke-width", 1.5);',
     '      .attr("fill", "var(--ink)").attr("fill-opacity", .85).attr("stroke", "var(--plate)").attr("stroke-width", 1.5);'),
    ('.on("pointerleave", () => { lk.attr("stroke-opacity", l => .15 + .6 * l.n / wmax); hideTip(); });',
     '.on("pointerleave", () => { lk.attr("stroke-opacity", l => .35 + .55 * l.n / wmax); hideTip(); });'),
])
patch("section3.html", [
    ('\n<div class="divider">',
     '\n<style>\n.divider { display: grid; gap: 10px; max-width: 74ch; padding-top: 28px; border-top: 1px solid var(--rule); }\n'
     '.divider h2.part { font: 600 1.8rem/1.15 var(--display); }\n</style>\n<div class="divider">'),
    ("Regions came first, on 30 and 31 October. Cities followed on 1 and 2 November, almost all in Argentina, Brazil and Switzerland.",
     "Most national corpora arrived on 30 October and regions on 30 and 31 October. Cities followed on 1 and 2 November, almost all in Argentina, Brazil and Switzerland."),
])
print("patched")
