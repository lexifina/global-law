"""Figure: every overruling the Lean model accepts in US case law, by year and court system.

    python tools/caselaw/figure.py <work-dir> <lean-in> <lean-out> <out.svg>

One dot per valid overruling act (lean-out/00.acts.tsv, validity 1), placed at the year of the overruling decision and
the row of its court system (the US Supreme Court, the federal courts of appeals, other federal courts, then each state).
"""
import collections, json, math, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from courts_map import STATES  # noqa: E402


def main(w, lin, lout, out):
    courts = {}
    for l in open(os.path.join(lin, "courts.tsv"), encoding="utf-8"):
        i, s, t, c = l.rstrip("\n").split("\t")
        courts[int(i)] = (int(s), t, int(c))
    dc, dd = {}, {}
    for l in open(os.path.join(lin, "decisions.tsv"), encoding="utf-8"):
        i, c, d = l.split("\t")
        dc[int(i)] = int(c)
        dd[int(i)] = int(d)
    pts = []
    for l in open(os.path.join(lout, "00.acts.tsv"), encoding="utf-8"):
        y, x, v = l.rstrip("\n").split("\t")
        if v != "1":
            continue
        y = int(y)
        s, t, c = courts.get(dc[y], (999, "T", 0))
        if s == 999:
            continue
        if s == 0:
            row = "US Supreme Court" if t == "L" else ("Federal courts of appeals" if t == "A" else "Other federal courts")
        else:
            row = STATES[s - 1] if s - 1 < len(STATES) else "Tribal"
        pts.append((dd[y] // 10000, row, t))
    rows = ["US Supreme Court", "Federal courts of appeals", "Other federal courts"]
    st = collections.Counter(r for _, r, _ in pts)
    rows += sorted([r for r in st if r not in rows], key=lambda r: r)
    W, X0, X1, Y0, RH = 1400, 250, 1360, 200, 15
    H = Y0 + RH * len(rows) + 110
    y0, y1 = 1790, 2026
    xs = lambda yr: X0 + (yr - y0) / (y1 - y0) * (X1 - X0)
    F = "IBM Plex Sans,system-ui,sans-serif"
    M = "JetBrains Mono,ui-monospace,monospace"
    col = {"L": "#f2b24a", "A": "#5fd3b4", "T": "#837d99", "S": "#837d99"}
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Every overruling in US case law accepted by the Lean model, by year and court system">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">Every overruling in US case law, as the Lean model reads it</text>']
    nC = len({(y, r) for y, r, _ in pts})
    stats = [(f"{len(pts):,}", "OVERRULINGS"), (f"{len(rows)}", "COURT SYSTEMS"), (f"{min(p[0] for p in pts)}–{max(p[0] for p in pts)}", "YEARS")]
    for i, (v, s) in enumerate(stats):
        xx = 44 + i * 220
        o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    lx = 720
    for i, (t, lab) in enumerate([("L", "by a court of last resort"), ("A", "by an intermediate appellate court"), ("T", "by a trial or special court")]):
        o.append(f'<circle cx="{lx + i * 230}" cy="116" r="5" fill="{col[t]}"/>')
        o.append(f'<text x="{lx + 12 + i * 230}" y="120" font-family="{F}" font-size="13" fill="#c9d1db">{lab}</text>')
    for yr in range(1800, 2027, 25):
        x = xs(yr)
        o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{Y0 - 14}" y2="{Y0 + RH * len(rows)}" stroke="#18222d"/>')
        o.append(f'<text x="{x:.1f}" y="{Y0 - 22}" text-anchor="middle" font-family="{M}" font-size="11" fill="#7d8896">{yr}</text>')
    for k, r in enumerate(rows):
        y = Y0 + k * RH + RH / 2
        o.append(f'<text x="{X0 - 14}" y="{y + 4:.1f}" text-anchor="end" font-family="{F}" font-size="11" fill="#9aa6b5">{r} ({st[r]:,})</text>')
    jit = collections.Counter()
    o.append('<g>')
    import random
    random.seed(1)
    for yr, r, t in sorted(pts, key=lambda p: "TSAL".index(p[2]) if p[2] in "TSAL" else 0):
        k = rows.index(r)
        x = xs(yr) + random.uniform(-2.2, 2.2)
        y = Y0 + k * RH + RH / 2 + random.uniform(-4.5, 4.5)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{col.get(t, "#837d99")}" fill-opacity=".75"/>')
    o.append('</g>')
    yb = Y0 + RH * len(rows) + 50
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-size="16" fill="#d6dbe2">One dot = one decision overruling an earlier one, in its own words, with the power to do so.</text>')
    o.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(o))
    print(json.dumps({"points": len(pts), "rows": len(rows), "by_row": st.most_common(8)}))


if __name__ == "__main__":
    main(*sys.argv[1:])
