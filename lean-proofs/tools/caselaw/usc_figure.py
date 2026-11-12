"""Figure: for each year decided, the share of US Code citations whose cited words a later law has rewritten.

    python tools/caselaw/usc_figure.py <rows_out.tsv> <out.svg>

rows_out.tsv is written by usc_results.py (one row per decision and section cited, with Lean's answers). Each year's bar
is split into: a law has since rewritten the cited words (subsection, or whole section when none is cited); a law has
amended another part of the section; no law has changed the section since.
"""
import collections, sys


def main(rows, out):
    yr = collections.defaultdict(lambda: [0, 0, 0])
    n = 0
    decs, secs = set(), set()
    for l in open(rows, encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        a, sd = f[5] == "1", f[10] == "1"
        y = int(f[2][:4])
        yr[y][0 if (a and sd) else (1 if a else 2)] += 1
        n += 1; decs.add(f[1]); secs.add(f[3])
    years = sorted(y for y in yr if 1995 <= y <= 2026)
    W, X0, X1, Y0, BH = 1400, 120, 1360, 210, 380
    H = Y0 + BH + 130
    F = "IBM Plex Sans,system-ui,sans-serif"
    M = "JetBrains Mono,ui-monospace,monospace"
    col = ["#ff6a55", "#ffb35c", "#2a3a4c"]
    bw = (X1 - X0) / len(years)
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="For each year from 1995 to 2026, the share of US Code citations in US case law whose cited words a later law has rewritten">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">What Congress has changed since, under every US Code citation in US case law</text>']
    stats = [(f"{n:,}", "CITATIONS"), (f"{len(decs):,}", "DECISIONS"), (f"{len(secs):,}", "SECTIONS CITED")]
    for i, (v, s) in enumerate(stats):
        xx = 44 + i * 230
        o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    lx = 760
    for i, lab in enumerate(["a law has rewritten the cited words", "a law has amended another part"]):
        o.append(f'<rect x="{lx + i * 300 - 6}" y="110" width="12" height="12" rx="2" fill="{col[i]}"/>')
        o.append(f'<text x="{lx + 12 + i * 300}" y="120" font-family="{F}" font-size="13" fill="#c9d1db">{lab}</text>')
    for p in (0, 25, 50, 75, 100):
        y = Y0 + BH - BH * p / 100
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="#18222d"/>')
        o.append(f'<text x="{X0 - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="{M}" font-size="11" fill="#7d8896">{p}%</text>')
    for k, y in enumerate(years):
        tot = sum(yr[y])
        x = X0 + k * bw + 3
        base = Y0 + BH
        for c in (0, 1):
            h = BH * yr[y][c] / tot
            base -= h
            o.append(f'<rect x="{x:.1f}" y="{base:.1f}" width="{bw - 6:.1f}" height="{h:.1f}" fill="{col[c]}" fill-opacity=".9"/>')
        if y % 5 == 0 or y == 2026:
            o.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{Y0 + BH + 22}" text-anchor="middle" font-family="{M}" font-size="11" fill="#7d8896">{y}</text>')
    o.append(f'<text x="44" y="{Y0 + BH + 72}" font-family="{F}" font-size="16" fill="#d6dbe2">Each bar is the year decided. The older the decision, the more of the law it applied has been rewritten since.</text>')
    o.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(o))
    print({y: [round(100 * v / sum(yr[y])) for v in yr[y]] for y in years[::5]})


if __name__ == "__main__":
    main(*sys.argv[1:])
