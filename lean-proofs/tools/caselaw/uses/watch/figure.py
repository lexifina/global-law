"""Figure for the blog: a watch list as a timeline, with the diff behind one alert.

    python figure.py demo_practice/firearms.json figure.svg

Rows: the items watched. Marks: a law that changed the words watched (an alert, red), a law that amended another
part of the section (amber), an edition that changed the words watched (hollow: a notice, never an alert).
"""
import html, json, sys


def main(src, out):
    d = json.load(open(src, encoding="utf-8"))
    items = d["items"]
    y0, y1 = int(d["since"][:4]), int(d["today"][:4]) + 1
    W, X0, X1, T = 1400, 330, 1350, 200
    RH = 25
    F = "IBM Plex Sans,system-ui,sans-serif"
    M = "JetBrains Mono,ui-monospace,monospace"
    red, amb, grid = "#ff6a55", "#ffb35c", "#2a3a4c"
    n_al = sum(r["alert"] for r in items)
    laws = {(c["day"], c["law"]) for r in items for c in r.get("changes", []) if c["watched_changed"]}
    n_ed = sum(1 for r in items for c in r.get("editions", []) if c["watched_changed"])
    H = T + RH * len(items) + 330

    def x(day):
        yy, mm, dd = int(day[:4]), int(day[5:7]), int(day[8:10])
        f = (yy - y0) + ((mm - 1) * 30.5 + dd) / 366
        return X0 + (X1 - X0) * f / (y1 - y0)

    e = html.escape
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A watch list of {len(items)} '
         f'firearms and drug sentencing provisions from {y0} to {d["today"][:4]}: which laws changed the words watched">',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="60" font-family="{F}" font-size="24" fill="#9aa6b5">A watch list: firearms and drug sentencing provisions, since {d["since"]}</text>']
    stats = [(str(len(items)), "PROVISIONS WATCHED"), (str(n_al), "WITH AN ALERT"), (str(len(laws)), "LAWS BEHIND THE ALERTS"),
             (str(n_ed), "EDITION NOTICES")]
    for i, (v, s) in enumerate(stats):
        xx = 44 + i * 230
        o.append(f'<text x="{xx}" y="120" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{xx}" y="142" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    lx = 990
    leg = [("circle", red, "a law changed the words watched (alert)"), ("circle", amb, "a law amended another part"),
           ("ring", amb, "an edition changed the words (notice)")]
    for i, (k, c, lab) in enumerate(leg):
        yy = 92 + i * 22
        if k == "circle":
            o.append(f'<circle cx="{lx}" cy="{yy}" r="6" fill="{c}"/>')
        else:
            o.append(f'<circle cx="{lx}" cy="{yy}" r="5" fill="none" stroke="{c}" stroke-width="2"/>')
        o.append(f'<text x="{lx + 14}" y="{yy + 4}" font-family="{F}" font-size="13" fill="#c9d1db">{lab}</text>')
    for yy in range(y0, y1 + 1):
        xx = X0 + (X1 - X0) * (yy - y0) / (y1 - y0)
        o.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{T - 8}" y2="{T + RH * len(items)}" stroke="#18222d"/>')
        if yy < y1:
            o.append(f'<text x="{xx + (X1 - X0) / (y1 - y0) / 2:.1f}" y="{T - 14}" text-anchor="middle" font-family="{M}" font-size="11" fill="#7d8896">{yy}</text>')
    named = {}
    for i, r in enumerate(items):
        cy = T + RH * i + RH / 2
        o.append(f'<line x1="{X0}" x2="{X1}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="{grid}" stroke-width="1"/>')
        lab = r["watched"].replace("U.S.C. § ", "U.S.C. § ")
        o.append(f'<text x="{X0 - 16}" y="{cy + 4:.1f}" text-anchor="end" font-family="{M}" font-size="13" fill="{"#eef1f5" if r["alert"] else "#8b97a6"}">{e(lab)}</text>')
        for c in r.get("editions", []):
            if c["watched_changed"]:
                o.append(f'<circle cx="{x(c["day"]):.1f}" cy="{cy:.1f}" r="5" fill="#0f1720" stroke="{amb}" stroke-width="2"/>')
        for c in r.get("changes", []):
            al = c["watched_changed"]
            o.append(f'<circle cx="{x(c["day"]):.1f}" cy="{cy:.1f}" r="{6.5 if al else 4.5}" fill="{red if al else amb}"/>')
            if al:
                named.setdefault((c["day"], c["short_title"] or c["law"]), []).append(cy)
    # name each law behind an alert once, above its first mark
    placed = []
    for (day, name), ys in sorted(named.items()):
        xx = x(day)
        if any(abs(xx - p) < 150 and abs(min(ys) - q) < 30 for p, q in placed):
            continue
        placed.append((xx, min(ys)))
    base = T + RH * len(items)
    yb = base + 34
    short = {"Servicemember Quality of Life Improvement and National Defense Authorization Act for Fiscal Year 2025": "NDAA for FY2025",
             "Halt All Lethal Trafficking of Fentanyl Act": "HALT Fentanyl Act"}
    names = sorted({(dd[:4], short.get(n, n)) for (dd, n) in named})
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-size="13" fill="#9aa6b5">Laws behind the alerts: '
             + e("; ".join(f"{n} ({yy})" for yy, n in names)) + '.</text>')
    o.append(f'<text x="44" y="{yb + 22}" font-family="{F}" font-size="13" fill="#9aa6b5">The hollow marks on 21 U.S.C. § 841 in 2019 are the First Step Act too: '
             'the record credits that change to the 2018 edition, so it is a notice, not an alert.</text>')
    yb += 22
    # the diff behind one alert
    pick = next(r for r in items if r["watched"].endswith("924(c)(1)(C)"))
    c = next(c for c in pick["changes"] if c["watched_changed"])
    yb += 50
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-weight="600" font-size="17" fill="#eef1f5">{e(pick["watched"])} · {e(c["short_title"])}, in force {c["day"]}</text>')
    yb += 34
    # lay out the diff as wrapped runs
    xx, line_h, maxx = 44, 26, W - 44
    cw = 8.0  # mono 14px advance
    for k, t in c["diff"]:
        if k == "gap":
            t = "…"
        words = t.split()
        for wi, w in enumerate(words):
            wpx = (len(w) + 0.7) * cw
            if xx + wpx > maxx:
                xx, yb = 44, yb + line_h
            col = {"eq": "#c9d1db", "gap": "#5d6b7a", "del": red, "ins": "#5fd1a4"}[k]
            deco = ' text-decoration="line-through"' if k == "del" else ""
            if k in ("del", "ins"):
                o.append(f'<rect x="{xx - 2:.1f}" y="{yb - 16}" width="{wpx:.1f}" height="22" fill="{col}" fill-opacity=".13"/>')
            o.append(f'<text x="{xx:.1f}" y="{yb}" font-family="{M}" font-size="14" fill="{col}"{deco}>{e(w)}</text>')
            if k == "del":
                o.append(f'<line x1="{xx:.1f}" x2="{xx + len(w) * cw:.1f}" y1="{yb - 5}" y2="{yb - 5}" stroke="{red}" stroke-width="1.4"/>')
            xx += wpx
    yb += 50
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-size="16" fill="#d6dbe2">Paragraph (c)(1)(A), the five-year minimum, is watched on its own row: the same law left its words alone, so it raises no alert.</text>')
    H2 = yb + 40
    o[0] = o[0]  # height fixed below
    svg = "\n".join(o) + "\n</svg>\n"
    svg = svg.replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {H2}"').replace(f'height="{H}" rx="14"', f'height="{H2}" rx="14"')
    open(out, "w", encoding="utf-8", newline="\n").write(svg)
    print(len(items), n_al, len(laws), n_ed, H2)


if __name__ == "__main__":
    main(*sys.argv[1:])
