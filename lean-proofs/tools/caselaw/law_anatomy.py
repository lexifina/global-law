"""Declaration map of our three Lean formalisms of US law, side by side: the tax code, the US Code, and US case law.

    lake env lean tools/LawAnatomy.lean > ../law-anatomy.jsonl
    python tools/caselaw/law_anatomy.py ../law-anatomy.jsonl out.svg

One dot per Lean definition or theorem, placed by dependency depth (0 = uses no other declaration of the project), in
the style of tools/taxcourt/anatomy_delta.py. Lines join a declaration to the ones that use it. Gold lines would mark a
declaration of one formalism using another's; the script counts them (there are none at the time of writing).
"""
import collections, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO = re.compile(r"\.(elim|ctorIdx|ctorElim|ctorElimType|noConfusion|noConfusionType|rec|recOn|casesOn|below|brecOn|"
                  r"binductionOn|ibelow|sizeOf_spec|_sizeOf_\d+|inj|injEq|ext|ext_iff|mk|toCtorIdx|ofNat|toNat|"
                  r"ofNat_toCtorIdx|toCtorIdx_ofNat|eq_def|eq_\d+|_unsafe_rec|instReprAux|repr|reprPrec)$")
U = "LegalProofs.USCaseLaw."
# panels: (title, subtitle, run-over line, header colour)
PANELS = [
    ("US TAX CODE", "earlier posts", "Title 26 drafting checks · 2025 income tax · Tax Court rulings", "#8b97a6"),
    ("US CODE", "this post", "135,919 versions of 53 titles · 50,010 amending operations", "#ffb35c"),
    ("US CASE LAW", "this post", "6.9 million decisions · 48 million citations", "#ff6a55"),
]
# columns: (key, label, colour, predicate on module name, panel)
COLS = [
    ("checks", "DRAFTING CHECKS", "#8d7f6c", lambda m: m.startswith(("TaxCode.Model", "TaxCode.Checks", "TaxCode.Certs")), 0),
    ("tax", "2025 INCOME TAX", "#6f8f86", lambda m: m.startswith("TaxCode.Individual"), 0),
    ("search", "LOOPHOLES", "#837d99", lambda m: m.startswith("LegalProofs.USTax") and not m.startswith(
        ("LegalProofs.USTax.TaxCourt", "LegalProofs.USTax.Estate", "LegalProofs.USTax.Family")), 0),
    ("court", "TAX COURT", "#b59a6a", lambda m: m.startswith("LegalProofs.USTax.TaxCourt"), 0),
    ("estate", "ESTATE + FAMILY", "#5f9f8f", lambda m: m.startswith(("LegalProofs.USTax.Estate", "LegalProofs.USTax.Family")), 0),
    ("versions", "VERSIONS + WATCH", "#ffb35c", lambda m: m in (U + "Statute", U + "StatuteText", U + "Watch", U + "Overrides"), 1),
    ("amend", "AMENDING", "#f2c57a", lambda m: m in ("LegalProofs.Amendments", U + "AmendmentCheck"), 1),
    ("structure", "REFERENCES + RESTATEMENTS", "#e0a050", lambda m: m in (U + "CrossRefs", U + "Recodification"), 1),
    ("courts", "COURTS", "#ff8a75", lambda m: m == U + "Courts", 2),
    ("precedent", "PRECEDENT", "#ff6a55", lambda m: m in (U + "Precedent", U + "Examples"), 2),
]


def auto(n):
    return bool(AUTO.search(n)) or re.search(r"\.inst[A-Z]", n) or ".match_" in n or "._" in n


def main(inp, out):
    L = [json.loads(l) for l in open(inp, encoding="utf-8")]
    L = [x for x in L if not auto(x["n"])]
    names = {x["n"] for x in L}
    mod = {x["n"]: x["m"] for x in L}
    kind = {x["n"]: x["k"] for x in L}
    col = {}
    for n in names:
        for k, c in enumerate(COLS):
            if c[3](mod[n]):
                col[n] = k
                break
    names = {n for n in names if n in col}
    deps = {x["n"]: [d for d in x["d"] if d in names] for x in L if x["n"] in names}
    users = collections.Counter(d for ds in deps.values() for d in ds)
    pan = lambda n: COLS[col[n]][4]
    sys.setrecursionlimit(100000)
    memo = {}

    def depth(n):
        if n not in memo:
            memo[n] = 0
            memo[n] = 1 + max((depth(m) for m in deps[n]), default=-1)
        return memo[n]
    for n in names:
        depth(n)
    maxd = max(memo.values())

    stats = []
    for p in range(len(PANELS)):
        ns = [n for n in names if pan(n) == p]
        mods = {mod[n] for n in ns}
        lines = sum(len((ROOT / (m.replace(".", "/") + ".lean")).read_text(encoding="utf-8").splitlines())
                    for m in mods if (ROOT / (m.replace(".", "/") + ".lean")).exists())
        stats.append({"decl": len(ns), "thm": sum(1 for n in ns if kind[n] == "thm"), "lines": lines, "mods": len(mods),
                      "depth": max(memo[n] for n in ns)})
    cross = sum(1 for n, ds in deps.items() for d in ds if pan(n) != pan(d))

    W, X0, GAP, PGAP = 1400, 70, 18, 56
    PW = [630, 316, 248]  # panel widths: the small formalisms get room to be read
    counts = [collections.Counter(memo[n] for n in names if col[n] == k) for k in range(len(COLS))]
    widest = [max(c.values()) if c else 1 for c in counts]
    share = [max(w, 12) ** .62 for w in widest]
    cw, cx = [0.0] * len(COLS), [0.0] * len(COLS)
    x = X0
    for p in range(len(PANELS)):
        ks = [k for k in range(len(COLS)) if COLS[k][4] == p]
        usable = PW[p] - GAP * (len(ks) - 1)
        tot = sum(share[k] for k in ks)
        for k in ks:
            cw[k] = usable * share[k] / tot
            cx[k] = x
            x += cw[k] + GAP
        x += PGAP - GAP
    stp = [6.0 if COLS[k][4] == 0 else 9.0 for k in range(len(COLS))]
    per_line = [max(1, int(cw[k] // stp[k])) for k in range(len(COLS))]
    band_h = [max(16, max(math.ceil(counts[k].get(d, 0) / per_line[k]) * stp[k] for k in range(len(COLS))) + 8)
              for d in range(maxd + 1)]
    Y0 = 330
    band_y = [Y0 + sum(band_h[:d]) for d in range(maxd + 1)]
    pos = {}
    for k in range(len(COLS)):
        for d in range(maxd + 1):
            ns = sorted((n for n in names if col[n] == k and memo[n] == d), key=lambda n: (mod[n], n))
            pl, step = per_line[k], stp[k]
            rows = math.ceil(len(ns) / pl) if ns else 0
            for i, n in enumerate(ns):
                r, c = divmod(i, pl)
                n_in = min(pl, len(ns) - r * pl)
                pos[n] = (cx[k] + (cw[k] - n_in * step) / 2 + c * step + step / 2,
                          band_y[d] + (band_h[d] - rows * step) / 2 + r * step + step / 2)
    H = Y0 + sum(band_h) + 100
    F = "IBM Plex Sans,system-ui,sans-serif"; M = "JetBrains Mono,ui-monospace,monospace"
    o = [f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Lean declaration maps of three formalisms of US law side by side: the tax code, the US Code and US case law">',
         f'<rect width="{W}" height="{H:.0f}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="56" font-family="{F}" font-size="24" fill="#9aa6b5">Three formalisms of US law in Lean, side by side</text>']
    pstart = [min(cx[k] for k in range(len(COLS)) if COLS[k][4] == p) for p in range(len(PANELS))]
    pend = [max(cx[k] + cw[k] for k in range(len(COLS)) if COLS[k][4] == p) for p in range(len(PANELS))]
    for p, (title, sub, run, c) in enumerate(PANELS):
        x0 = 44 if p == 0 else pstart[p] + 4
        st = stats[p]
        o.append(f'<text x="{x0}" y="104" font-family="{M}" font-size="12" letter-spacing="1" fill="{c}">{title}'
                 f'<tspan fill="#5d6977"> · {sub.upper()}</tspan></text>')
        vals = [(f"{st['decl']:,}", "DECLARATIONS"), (f"{st['thm']:,}", "THEOREMS"), (f"{st['lines']:,}", "LINES")]
        sp = min(130, (pend[p] - x0 + 10) / 3)
        for i, (v, s) in enumerate(vals):
            xx = x0 + i * sp
            o.append(f'<text x="{xx:.0f}" y="150" font-family="{F}" font-weight="600" font-size="{26 if p == 0 else 22}" fill="#eef1f5">{v}</text>')
            o.append(f'<text x="{xx:.0f}" y="172" font-family="{M}" font-size="{10.5 if p == 0 else 9.5}" letter-spacing=".6" fill="#8b97a6">{s}</text>')
        # run-over line, wrapped at the separator
        parts = run.split(" · ")
        ys = 206
        for part in parts:
            o.append(f'<text x="{x0}" y="{ys}" font-family="{F}" font-size="13" fill="#c9d1db">{part}</text>')
            ys += 18
        if p:
            xm = pstart[p] - PGAP / 2
            o.append(f'<line x1="{xm:.0f}" x2="{xm:.0f}" y1="84" y2="{H - 64:.0f}" stroke="#2a3644" stroke-dasharray="4 5"/>')
    o.append(f'<text x="44" y="{Y0 - 44}" font-family="{M}" font-size="11" letter-spacing="1" fill="#7d8896">DEPENDENCY DEPTH ↓</text>')
    for d in range(0, maxd + 1, 2):
        y = band_y[d] + band_h[d] / 2
        o.append(f'<line x1="{X0 - 6}" x2="{W - 24}" y1="{y:.1f}" y2="{y:.1f}" stroke="#18222d"/>')
        o.append(f'<text x="{X0 - 14}" y="{y + 4:.1f}" text-anchor="end" font-family="{M}" font-size="11" fill="#7d8896">{d}</text>')
    for k, c in enumerate(COLS):
        words = c[1].split(" + ")
        lab = c[1] if len(c[1]) * 6.4 < cw[k] + GAP or len(words) == 1 else None
        if lab:
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 12}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{lab}</text>')
        else:
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 24}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{words[0]} +</text>')
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 11}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{" + ".join(words[1:])}</text>')
    o.append('<g fill="none" stroke-width=".45">')
    for n, ds in deps.items():
        x2, y2 = pos[n]
        for d in ds:
            x1, y1 = pos[d]
            crossing = pan(n) != pan(d)
            stroke, op = ("#ffd27a", .6) if crossing else (COLS[col[n]][2], .1 if pan(n) else .07)
            my = (y1 + y2) / 2
            o.append(f'<path d="M{x1:.1f} {y1:.1f}C{x1:.1f} {my:.1f} {x2:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{stroke}" stroke-opacity="{op}"/>')
    o.append('</g><g>')
    for n in sorted(names, key=lambda n: users[n]):
        x, y = pos[n]
        r = min(4.6, 1.3 + .75 * math.sqrt(users[n])) * (1 if pan(n) == 0 else 1.25)
        c = COLS[col[n]]
        op = (1 if kind[n] == "thm" else .8) * (.6 if c[4] == 0 else 1)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c[2]}" fill-opacity="{op:.2f}"><title>{n}</title></circle>')
    o.append('</g>')
    yb = Y0 + sum(band_h) + 40
    note = ("They share no code: no declaration of one uses another’s." if cross == 0
            else f"Gold lines: {cross} uses of one formalism’s declarations by another.")
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-size="16" fill="#d6dbe2">One dot = one Lean definition or theorem, lower = built on more. {note}</text>')
    o.append('</svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8")
    print(json.dumps({"panels": stats, "cross_links": cross, "maxdepth": maxd,
                      "per_column": {COLS[k][0]: sum(counts[k].values()) for k in range(len(COLS))}}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
