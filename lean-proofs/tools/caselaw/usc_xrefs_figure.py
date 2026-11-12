"""Figure: cross-references inside the US Code that newly dangle each year, by cause.

    python tools/caselaw/usc_xrefs_figure.py <by_year_detail.tsv> <out.svg>

Each bar is a year (1996-2026): references that started to dangle that year because the target changed under them
(broken later) and references written by a law or edition that pointed at nothing (written dangling). The line is the
number dangling at the end of each year.
"""
import sys


def main(inp, out):
    rows = [l.rstrip("\n").split("\t") for l in open(inp, encoding="utf-8")][1:]
    rows = [r for r in rows if int(r[0]) >= 1996]
    years = [int(r[0]) for r in rows]
    broken = [int(r[6]) for r in rows]
    written = [int(r[5]) for r in rows]
    dang = [int(r[3]) for r in rows]
    refs = [int(r[2]) for r in rows]
    W, X0, X1, Y0, BH = 1400, 120, 1300, 210, 380
    H = Y0 + BH + 130
    F = "IBM Plex Sans,system-ui,sans-serif"
    M = "JetBrains Mono,ui-monospace,monospace"
    col = ["#ff6a55", "#ffb35c", "#2a3a4c"]
    bw = (X1 - X0) / len(years)
    top = 1000
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="For each year from 1996 to 2026, the cross-references inside the US Code that newly dangle, broken by a change to their target or written dangling, and the number dangling at each year end">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">Cross-references inside the US Code that point at nothing</text>']
    stats = [(f"{refs[-1]:,}", "REFERENCES IN FORCE"), (f"{dang[-1]:,}", "DANGLING TODAY"),
             (f"{sum(broken):,}", "BROKEN LATER SINCE 1996"), (f"{sum(written):,}", "WRITTEN DANGLING")]
    for i, (v, s) in enumerate(stats):
        xx = 44 + i * 250
        o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    lx = 1060
    for i, lab in enumerate(["broken later", "written dangling"]):
        o.append(f'<rect x="{lx - 6}" y="{102 + i * 24}" width="12" height="12" rx="2" fill="{col[i]}"/>')
        o.append(f'<text x="{lx + 12}" y="{112 + i * 24}" font-family="{F}" font-size="13" fill="#c9d1db">{lab}</text>')
    for p in (0, 250, 500, 750, 1000):
        y = Y0 + BH - BH * p / top
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="#18222d"/>')
        o.append(f'<text x="{X0 - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="{M}" font-size="11" fill="#7d8896">{p}</text>')
    # right axis: dangling at year end, 0..5000
    rtop = 5000
    for p in (0, 2500, 5000):
        y = Y0 + BH - BH * p / rtop
        o.append(f'<text x="{X1 + 12}" y="{y + 4:.1f}" font-family="{M}" font-size="11" fill="#c9d1db">{p:,}</text>')
    pts = []
    for k, y in enumerate(years):
        x = X0 + k * bw + 3
        base = Y0 + BH
        for c, v in enumerate((broken[k], written[k])):
            h = BH * min(v, top) / top
            base -= h
            o.append(f'<rect x="{x:.1f}" y="{base:.1f}" width="{bw - 6:.1f}" height="{h:.1f}" fill="{col[c]}" fill-opacity=".9"/>')
        pts.append(f"{x + (bw - 6) / 2:.1f},{Y0 + BH - BH * dang[k] / rtop:.1f}")
        if y % 5 == 0 or y == 2026:
            o.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{Y0 + BH + 22}" text-anchor="middle" font-family="{M}" font-size="11" fill="#7d8896">{y}</text>')
    o.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#eef1f5" stroke-width="2" stroke-opacity=".8"/>')
    k14 = years.index(2014)
    x14 = X0 + k14 * bw + bw / 2
    o.append(f'<text x="{x14 - 10:.1f}" y="{Y0 + BH - BH * min(broken[k14] + written[k14], top) / top - 10:.1f}" text-anchor="end" font-family="{F}" font-size="13" fill="#c9d1db">title 54 enacted; most fixed within weeks</text>')
    o.append(f'<text x="44" y="{Y0 + BH + 72}" font-family="{F}" font-size="16" fill="#d6dbe2">Bars: references that started to dangle that year (left axis). Line: dangling at the end of each year (right axis).</text>')
    o.append('</svg>')
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(o))


if __name__ == "__main__":
    main(*sys.argv[1:])
