"""code_dynamics.svg: four measures of the US Code since 1994, in the house style of usc_figure.py.

    python figure.py
"""
import collections, json, os

OUT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~/Documents/us-caselaw-lean-work")
F = "IBM Plex Sans,system-ui,sans-serif"
M = "JetBrains Mono,ui-monospace,monospace"
RED, AMB, DARK = "#ff6a55", "#ffb35c", "#2a3a4c"
T1, T2, T3, GRID = "#eef1f5", "#9aa6b5", "#7d8896", "#18222d"
W = 1400
PW = 636
COLS = (44, 720)
NAMES = {"42": "Public health", "10": "Armed forces", "26": "Tax", "20": "Education", "16": "Conservation",
         "7": "Agriculture", "49": "Transportation", "22": "Foreign relations", "38": "Veterans", "15": "Commerce",
         "36": "Patriotic societies", "46": "Shipping", "12": "Banks", "50": "War and defense", "18": "Crimes",
         "5": "Government org.", "33": "Navigable waters", "2": "Congress", "21": "Food and drugs", "8": "Aliens",
         "29": "Labor", "47": "Telecom", "19": "Customs"}


def tsv(name, base=OUT):
    return [l.rstrip("\n").split("\t") for l in open(os.path.join(base, name), encoding="utf-8")]


def txt(x, y, s, size=18, fill=T2, font=F, anchor="start", weight=None, extra=""):
    wgt = f' font-weight="{weight}"' if weight else ""
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}"{wgt} fill="{fill}" '
            f'text-anchor="{anchor}"{extra}>{s}</text>')


def head(o, x, y, title, sub):
    o.append(txt(x, y, title, 25, T1, weight=600))
    for i, s in enumerate(sub):
        o.append(txt(x, y + 30 + i * 25, s, 18, T2))


def panel1(o, x0, y0):
    h = collections.defaultdict(dict)
    for t, c, ch, n, s in tsv("p1_heat.tsv"):
        h[t][int(c)] = (int(ch), int(n))
    tot = {t: sum(v[0] for v in d.values()) for t, d in h.items() if t != "all"}
    rows = ["all"] + sorted(tot, key=lambda t: -tot[t])[:10]
    a = h["all"]
    s104, s117 = a[104][0] / a[104][1], a[118][0] / a[118][1]
    head(o, x0, y0, f"Each Congress rewrites less of the Code",
         [f"Share of sections a law changed, per Congress: {100 * s104:.0f}% in the",
          f"104th (1995–96), {100 * s117:.0f}% in the 118th (2023–24)"])
    LX = x0 + 214
    cw = (x0 + PW - LX) / 16
    rh = 28
    top = y0 + 84
    cap = 0.25

    def col(s):
        k = min(s / cap, 1) ** 0.75
        c0, c1 = (0x1a, 0x26, 0x33), (0xff, 0x6a, 0x55)
        return "#" + "".join(f"{round(a + (b - a) * k):02x}" for a, b in zip(c0, c1))
    for i, t in enumerate(rows):
        y = top + i * rh + (8 if i else 0)
        lab = "All titles" if t == "all" else f"{t}  {NAMES.get(t, '')}"
        o.append(txt(LX - 12, y + rh / 2 + 6, lab, 17, T1 if t == "all" else T2, anchor="end",
                     weight=600 if t == "all" else None))
        for k, c in enumerate(range(104, 120)):
            ch, n = h[t].get(c, (0, 0))
            s = ch / n if n else 0
            o.append(f'<rect x="{LX + k * cw + 1:.1f}" y="{y + 1:.1f}" width="{cw - 2:.1f}" height="{rh - 2:.1f}" '
                     f'rx="3" fill="{col(s)}"><title>Title {t}, {c}th Congress: {100 * s:.1f}%</title></rect>')
    yb = top + len(rows) * rh + 8
    for k, c in enumerate(range(104, 120)):
        if c % 3 == 2 or c == 119:
            o.append(txt(LX + (k + .5) * cw, yb + 22, str(c), 16, T3, M, "middle"))
    o.append(txt(LX - 12, yb + 22, "Congress", 16, T3, M, "end"))
    # legend, on the Congress row's right
    ly = yb + 40
    o.append(txt(LX - 12, ly + 13, "share changed", 16, T3, M, "end"))
    for k in range(6):
        o.append(f'<rect x="{LX + k * 46:.1f}" y="{ly}" width="44" height="16" rx="3" fill="{col(cap * k / 5)}"/>')
    o.append(txt(LX + 6 * 46 + 6, ly + 14, "0% to 25%+", 16, T3, M))
    # survival inset: share of cited sections a law has not amended, by years since the decision
    sv = [(int(a), float(b)) for a, b, n in tsv("survival.tsv", os.path.join(HOME, "usc", "results"))]
    ix0, ix1 = LX, x0 + PW - 50
    iy0, iy1 = ly + 64, ly + 150
    o.append(txt(LX - 12, iy0 + 4, "cited sections", 16, T3, M, "end"))
    o.append(txt(LX - 12, iy0 + 26, "not amended", 16, T3, M, "end"))
    o.append(txt(LX - 12, iy0 + 48, "since the", 16, T3, M, "end"))
    o.append(txt(LX - 12, iy0 + 70, "decision", 16, T3, M, "end"))

    def sy(v):
        return iy1 - (iy1 - iy0) * (100 * v - 50) / 50
    for p in (50, 100):
        y = sy(p / 100)
        o.append(f'<line x1="{ix0}" x2="{ix1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(txt(ix1 + 8, y + 5, f"{p}%", 16, T3, M))
    pts = [(ix0 + (ix1 - ix0) * yr / 31, sy(v)) for yr, v in sv]
    o.append('<polyline fill="none" stroke="%s" stroke-width="3" points="%s"/>' % (AMB, " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)))
    for yr in (10, 30):
        a, b = pts[yr]
        o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="5" fill="{AMB}" stroke="#0f1720" stroke-width="2"/>')
        lab = f"{100 * sv[yr][1]:.0f}% at {yr} years" if yr == 10 else f"{100 * sv[yr][1]:.0f}%"
        o.append(txt(a + (6 if yr == 10 else 0), b - 14, lab, 16, T1, M, "start" if yr == 10 else "middle"))
    o.append(txt(ix0, iy1 + 22, "0", 16, T3, M)); o.append(txt(ix1, iy1 + 22, "31 years", 16, T3, M, "end"))
    return sv


def panel2(o, x0, y0):
    rows = [(int(y), int(w), int(s), int(x)) for y, w, s, x in tsv("p2_complexity.tsv")]
    xr_src = "own count"
    xrp = os.path.join(HOME, "uses", "xrefs", "by_year.tsv")
    if os.path.exists(xrp):
        ext = {}
        for f in tsv("by_year.tsv", os.path.dirname(xrp)):
            try:
                ext[int(f[0])] = int(f[2])
            except ValueError:
                pass
        if all(r[0] in ext for r in rows):
            rows = [(y, w, s, ext[y]) for y, w, s, x in rows]
            xr_src = "xrefs checker"
    b = rows[0]
    ser = [("words", 1, RED), ("references", 3, AMB), ("sections", 2, T2)]
    last = rows[-1]
    head(o, x0, y0, "The Code grew by 78% in words since 1994".replace(
        "78", f"{100 * (last[1] / b[1] - 1):.0f}"),
         [f"{b[1] / 1e6:.1f} million words in 1994, {last[1] / 1e6:.1f} million today; indexed,",
          "1994 = 100, at the end of each year"])
    X0, X1, Y0, Y1 = x0 + 60, x0 + PW - 150, y0 + 100, y0 + 520
    lo, hi = 100, 175
    for p in range(100, 176, 25):
        y = Y1 - (Y1 - Y0) * (p - lo) / (hi - lo)
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(txt(X0 - 10, y + 5, str(p), 16, T3, M, "end"))
    yrs = [r[0] for r in rows]

    def px(y):
        return X0 + (X1 - X0) * (y - yrs[0]) / (yrs[-1] - yrs[0])
    for y in (1994, 2000, 2010, 2020, 2026):
        o.append(txt(px(y), Y1 + 26, str(y), 16, T3, M, "middle"))
    ends = []
    for name, k, c in ser:
        pts = [(px(r[0]), Y1 - (Y1 - Y0) * (100 * r[k] / b[k] - lo) / (hi - lo)) for r in rows]
        o.append('<polyline fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round" points="%s"/>'
                 % (c, " ".join(f"{a:.1f},{v:.1f}" for a, v in pts)))
        ends.append((pts[-1][1], name, 100 * last[k] / b[k], c, last[k]))
    ends.sort()
    prev = -1e9
    for y, name, v, c, raw in ends:
        y = max(y, prev + 44); prev = y
        o.append(txt(X1 + 12, y, f"{v:.0f}", 18, T1, M, weight=600))
        o.append(txt(X1 + 62, y, name, 16, c if False else T2))
        o.append(f'<rect x="{X1 + 12}" y="{y + 8:.1f}" width="22" height="4" rx="2" fill="{c}"/>')
        o.append(txt(X1 + 40, y + 16, f"{raw / 1e6:.1f}M" if raw > 1e6 else f"{raw:,}", 15, T3, M))
    return rows, xr_src


def panel3(o, x0, y0):
    cr = {k: int(v) for k, v in tsv("credit.tsv")}
    tot = sum(cr.values())
    laws = sum(v for k, v in cr.items() if k.isdigit())
    head(o, x0, y0, f"{100 * laws / tot:.0f}% of today's words were written since 1995",
         [f"Today's {tot / 1e6:.1f} million words, by the law that inserted them",
          "(word-level blame along every section's versions)"])
    # 100% bar
    bx, by, bw, bh = x0, y0 + 96, PW, 34
    parts = [("pre", "in force by 1994", DARK), ("edition", "later editions, no law named", "#4f5f72"),
             ("laws", "laws since 1995", RED)]
    vals = {"pre": cr["pre"], "edition": cr["edition"], "laws": laws}
    x = bx
    for k, lab, c in parts:
        wdt = bw * vals[k] / tot
        o.append(f'<rect x="{x + 1:.1f}" y="{by}" width="{wdt - 2:.1f}" height="{bh}" rx="4" fill="{c}"/>')
        o.append(txt(x + 10, by + 24, f"{100 * vals[k] / tot:.0f}%", 18, T1, M, weight=600))
        x += wdt
    lx = bx
    for k, lab, c in parts:
        o.append(f'<rect x="{lx}" y="{by + bh + 14}" width="14" height="14" rx="3" fill="{c}"/>')
        o.append(txt(lx + 20, by + bh + 26, lab, 16, T2))
        lx += 20 + len(lab) * 8.6 + 22
    # bars per Congress, share of today's words
    X0, X1, Y0, Y1 = x0 + 50, x0 + PW, y0 + 210, y0 + 500
    cs = list(range(104, 120))
    mx = 6
    for p in range(0, mx + 1, 2):
        y = Y1 - (Y1 - Y0) * p / mx
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(txt(X0 - 10, y + 5, f"{p}%", 16, T3, M, "end"))
    cw = (X1 - X0) / len(cs)
    for i, c in enumerate(cs):
        v = 100 * cr.get(str(c), 0) / tot
        h = (Y1 - Y0) * v / mx
        o.append(f'<path d="M{X0 + i * cw + 4:.1f},{Y1} v{-(h - 4):.1f} q0,-4 4,-4 h{cw - 16:.1f} q4,0 4,4 v{h - 4:.1f} z" '
                 f'fill="{RED}" fill-opacity=".9"><title>{c}th Congress: {v:.1f}%</title></path>')
        if c % 3 == 2 or c == 119:
            o.append(txt(X0 + (i + .5) * cw, Y1 + 24, str(c), 16, T3, M, "middle"))
    o.append(txt(X0 - 10, Y1 + 24, "", 16, T3, M, "end"))
    o.append(txt(X1, Y1 + 50, "Congress", 16, T3, M, "end"))
    best = max(cs, key=lambda c: cr.get(str(c), 0))
    i = cs.index(best)
    v = 100 * cr[str(best)] / tot
    o.append(txt(X0 + (i + .5) * cw, Y1 - (Y1 - Y0) * v / mx - 12, f"{v:.1f}%", 16, T1, M, "middle"))
    o.append(txt(X0, Y0 - 14, "Share of today's words, by the Congress that wrote them", 16, T2))
    return cr, tot, laws


def panel4(o, x0, y0):
    ev = [(int(k), float(t), float(c)) for k, _, _, t, c in [r for r in tsv("p4_event.tsv")]]
    eff = json.load(open(os.path.join(OUT, "p4_effect.json"), encoding="utf-8"))
    e = eff["post_vs_Yminus1"]
    head(o, x0, y0, f"Rewritten subsections draw {100 * (e['ratio'] - 1):.0f}% more citations",
         [f"Citations of {eff['events']:,} subsections a law rewrote in 2000–15, vs",
          "matched unchanged sections; year before the law = 100"])
    X0, X1, Y0, Y1 = x0 + 60, x0 + PW - 120, y0 + 100, y0 + 500
    lo, hi = 60, 140
    for p in range(lo, hi + 1, 20):
        y = Y1 - (Y1 - Y0) * (p - lo) / (hi - lo)
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(txt(X0 - 10, y + 5, str(p), 16, T3, M, "end"))

    def px(k):
        return X0 + (X1 - X0) * (k + 5) / 10
    o.append(f'<line x1="{px(0):.1f}" x2="{px(0):.1f}" y1="{Y0}" y2="{Y1}" stroke="{T3}" stroke-dasharray="4 5"/>')
    o.append(txt(px(0) + 8, Y0 + 16, "law", 16, T2))
    for k in (-5, -1, 0, 5):
        o.append(txt(px(k), Y1 + 26, f"{k:+d}" if k else "0", 16, T3, M, "middle"))
    o.append(txt((X0 + X1) / 2, Y1 + 52, "years from the law", 16, T3, M, "middle"))
    for name, j, c in (("rewritten", 1, RED), ("matched, unchanged", 2, T2)):
        pts = [(px(k), Y1 - (Y1 - Y0) * (r[j] - lo) / (hi - lo)) for k, r in zip(range(-5, 6), ev)]
        o.append('<polyline fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round" points="%s"/>'
                 % (c, " ".join(f"{a:.1f},{v:.1f}" for a, v in pts)))
        for a, v in pts:
            o.append(f'<circle cx="{a:.1f}" cy="{v:.1f}" r="4.5" fill="{c}" stroke="#0f1720" stroke-width="2"/>')
        a, v = pts[-1]
        o.append(txt(X1 + 14, v + 6, f"{ev[-1][j]:.0f}", 18, T1, M, weight=600))
        o.append(txt(X1 + 14, v + 28, name.split(",")[0], 15, T2))
    o.append(txt(X0, Y1 + 84, f"+{100 * (e['ratio'] - 1):.0f}% over years 1–5 (95% CI "
                 f"{100 * (e['ci95'][0] - 1):+.0f}% to {100 * (e['ci95'][1] - 1):+.0f}%). Who wins is not in the data.", 16, T2))
    return eff


def main():
    H = 1400
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Four measures of the US Code since 1994: how much of it each Congress changes, how it has grown, '
         f'who wrote today\'s words, and how citations of rewritten subsections change">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
         txt(44, 60, "The US Code since 1994: change, growth, authorship and litigation", 26, T2)]
    panel1(o, COLS[0], 110)
    panel2(o, COLS[1], 110)
    panel3(o, COLS[0], 770)
    panel4(o, COLS[1], 770)
    o.append(f'<line x1="44" x2="{W - 44}" y1="735" y2="735" stroke="{GRID}" stroke-width="2"/>')
    o.append(f'<line x1="700" x2="700" y1="110" y2="{H - 40}" stroke="{GRID}" stroke-width="2"/>')
    o.append("</svg>")
    with open(os.path.join(OUT, "code_dynamics.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(o))


if __name__ == "__main__":
    main()
