"""Declaration map: the tax-code formalism of "Formalizing the US tax code" beside what was added for the Tax Court work.

    lake env lean tools/TaxAnatomy2.lean > tax-anatomy2.jsonl
    python tools/taxcourt/anatomy_delta.py tax-anatomy2.jsonl out.svg

One dot per Lean definition or theorem, placed by dependency depth (0 = uses no other declaration of the project).
Left panel: the work described in the previous post. Right panel: what was added since. Lines join a declaration to
the ones that use it; lines from the right panel into the left are the places the new work reuses the old.
"""
import collections, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO = re.compile(r"\.(elim|ctorIdx|ctorElim|ctorElimType|noConfusion|noConfusionType|rec|recOn|casesOn|below|brecOn|"
                  r"binductionOn|ibelow|sizeOf_spec|_sizeOf_\d+|inj|injEq|ext|ext_iff|mk|toCtorIdx|ofNat|toNat|"
                  r"ofNat_toCtorIdx|toCtorIdx_ofNat|eq_def|eq_\d+|_unsafe_rec|instReprAux|repr|reprPrec)$")
# (key, label, colour, predicate on module name, panel)
COLS = [
    ("checks", "DRAFTING CHECKS", "#8d7f6c", lambda m: m.startswith(("TaxCode.Model", "TaxCode.Checks", "TaxCode.Certs")), 0),
    ("tax", "2025 INCOME TAX", "#6f8f86", lambda m: m.startswith("TaxCode.Individual"), 0),
    ("search", "LOOPHOLE SEARCHES", "#837d99", lambda m: m.startswith("LegalProofs.USTax") and not m.startswith(
        ("LegalProofs.USTax.TaxCourt", "LegalProofs.USTax.Estate", "LegalProofs.USTax.Family")), 0),
    ("court", "TAX COURT RULES 2012–2024", "#f2b24a", lambda m: m.startswith("LegalProofs.USTax.TaxCourt") and "Rulings" not in m, 1),
    ("rulings", "RULINGS", "#ff7a6b", lambda m: m.startswith("LegalProofs.USTax.TaxCourt.Rulings"), 1),
    ("estate", "ESTATE + FAMILY", "#5fd3b4", lambda m: m.startswith(("LegalProofs.USTax.Estate", "LegalProofs.USTax.Family")), 1),
]


def auto(n):
    return bool(AUTO.search(n)) or re.search(r"\.inst[A-Z]", n) or ".match_" in n or "._" in n


def main(inp, out):
    L = [json.loads(l) for l in open(inp, encoding="utf-8")]
    L = [x for x in L if not auto(x["n"])]
    names = {x["n"] for x in L}
    deps = {x["n"]: [d for d in x["d"] if d in names] for x in L}
    mod = {x["n"]: x["m"] for x in L}
    kind = {x["n"]: x["k"] for x in L}
    col = {}
    for n in names:
        for k, c in enumerate(COLS):
            if c[3](mod[n]):
                col[n] = k
                break
    names = {n for n in names if n in col}
    deps = {n: [d for d in deps[n] if d in names] for n in names}
    users = collections.Counter(d for ds in deps.values() for d in ds)
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

    def lines_of(pred):
        mods = {mod[n] for n in names if pred(n)}
        tot = 0
        for m in mods:
            f = ROOT / (m.replace(".", "/") + ".lean")
            if f.exists():
                tot += len(f.read_text(encoding="utf-8").splitlines())
        return tot, len(mods)
    guards = sum(1 for l in (ROOT / "LegalProofs/USTax/TaxCourt/Rulings.lean").read_text(encoding="utf-8").splitlines() if l.startswith("#guard"))
    stats = []
    for panel in (0, 1):
        ns = [n for n in names if COLS[col[n]][4] == panel]
        ln, nm = lines_of(lambda n: COLS[col[n]][4] == panel)
        stats.append({"decl": len(ns), "thm": sum(1 for n in ns if kind[n] == "thm"), "lines": ln, "mods": nm})
    cross = sum(1 for n, ds in deps.items() for d in ds if COLS[col[n]][4] == 1 and COLS[col[d]][4] == 0)

    W, X0, GAP, PGAP = 1400, 86, 28, 64
    counts = [collections.Counter(memo[n] for n in names if col[n] == k) for k in range(len(COLS))]
    widest = [max(c.values()) if c else 1 for c in counts]
    share = [w ** .75 for w in widest]
    usable = W - X0 - 40 - GAP * 5 - PGAP
    cw = [usable * s / sum(share) for s in share]
    cx, x = [], X0
    for k in range(len(COLS)):
        if k == 3:
            x += PGAP
        cx.append(x)
        x += cw[k] + GAP
    steps = [5.5, 7.5, 7.5, 7.0, 9.0, 7.0]
    per_line = [max(1, int(cw[k] // steps[k])) for k in range(len(COLS))]
    band_h = [max(18, max(math.ceil(counts[k].get(d, 0) / per_line[k]) * steps[k] for k in range(len(COLS))) + 8) for d in range(maxd + 1)]
    Y0 = 300
    band_y = [Y0 + sum(band_h[:d]) for d in range(maxd + 1)]
    pos = {}
    for k in range(len(COLS)):
        for d in range(maxd + 1):
            ns = sorted((n for n in names if col[n] == k and memo[n] == d), key=lambda n: (mod[n], n))
            pl, st = per_line[k], steps[k]
            rows = math.ceil(len(ns) / pl) if ns else 0
            for i, n in enumerate(ns):
                r, c = divmod(i, pl)
                n_in = min(pl, len(ns) - r * pl)
                pos[n] = (cx[k] + (cw[k] - n_in * st) / 2 + c * st + st / 2, band_y[d] + (band_h[d] - rows * st) / 2 + r * st + st / 2)
    H = Y0 + sum(band_h) + 110
    F = "IBM Plex Sans,system-ui,sans-serif"; M = "JetBrains Mono,ui-monospace,monospace"
    o = [f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Lean declaration map: the previous tax-code formalism beside what was added for the Tax Court work">',
         f'<rect width="{W}" height="{H:.0f}" rx="14" fill="#0f1720"/>',
         f'<text x="44" y="56" font-family="{F}" font-size="21" fill="#9aa6b5">Recreating Tax Court rulings · what was added to the Lean code</text>']
    xm = cx[3] - PGAP / 2
    heads = [("PREVIOUS POST: FORMALIZING THE US TAX CODE", 44, stats[0], "#8b97a6"), ("ADDED FOR THIS POST", xm + 20, stats[1], "#f2b24a")]
    for lab, x0, st, c in heads:
        o.append(f'<text x="{x0}" y="104" font-family="{M}" font-size="12" letter-spacing="1" fill="{c}">{lab}</text>')
        for i, (v, s) in enumerate([(f"{st['decl']:,}", "DECLARATIONS"), (f"{st['thm']:,}", "THEOREMS"), (f"{st['lines']:,}", "SOURCE LINES")]):
            xx = x0 + i * 140
            o.append(f'<text x="{xx}" y="150" font-family="{F}" font-weight="600" font-size="30" fill="#eef1f5">{v}</text>')
            o.append(f'<text x="{xx}" y="172" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    o.append(f'<text x="{xm + 20}" y="200" font-family="{F}" font-size="14" fill="#c9d1db">+ {guards} court holdings re-checked on every build</text>')
    o.append(f'<text x="{xm + 20}" y="220" font-family="{F}" font-size="14" fill="#ffd27a">{cross} calls into the previous post’s code (gold lines)</text>')
    o.append(f'<line x1="{xm:.0f}" x2="{xm:.0f}" y1="84" y2="{H - 70:.0f}" stroke="#2a3644" stroke-dasharray="4 5"/>')
    o.append(f'<text x="44" y="{Y0 - 40}" font-family="{M}" font-size="12" letter-spacing="1" fill="#8b97a6">DEPENDENCY DEPTH ↓ · FOUNDATIONS TO RESULTS</text>')
    for d in range(0, maxd + 1, 2):
        y = band_y[d] + band_h[d] / 2
        o.append(f'<line x1="{X0 - 6}" x2="{W - 30}" y1="{y:.1f}" y2="{y:.1f}" stroke="#18222d"/>')
        o.append(f'<text x="{X0 - 18}" y="{y + 4:.1f}" text-anchor="end" font-family="{M}" font-size="12" fill="#7d8896">{d}</text>')
    for k, c in enumerate(COLS):
        o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 10}" text-anchor="middle" font-family="{M}" font-size="10.5" letter-spacing=".6" fill="{c[2]}">{c[1]}</text>')
    o.append('<g fill="none" stroke-width=".45">')
    for n, ds in deps.items():
        x2, y2 = pos[n]
        for d in ds:
            x1, y1 = pos[d]
            crossing = COLS[col[n]][4] == 1 and COLS[col[d]][4] == 0
            stroke, op = ("#ffd27a", .55) if crossing else (COLS[col[n]][2], .08)
            my = (y1 + y2) / 2
            o.append(f'<path d="M{x1:.1f} {y1:.1f}C{x1:.1f} {my:.1f} {x2:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{stroke}" stroke-opacity="{op}"/>')
    o.append('</g><g>')
    for n in sorted(names, key=lambda n: users[n]):
        x, y = pos[n]
        r = min(5, 1.3 + .8 * math.sqrt(users[n]))
        c = COLS[col[n]]
        op = (1 if kind[n] == "thm" else .8) * (.55 if c[4] == 0 else 1)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c[2]}" fill-opacity="{op:.2f}"><title>{n}</title></circle>')
    o.append('</g>')
    yb = Y0 + sum(band_h) + 40
    o.append(f'<text x="44" y="{yb}" font-family="{F}" font-size="16" fill="#d6dbe2">One dot = one Lean definition or theorem. Gold lines: new code calling the code from the previous post.</text>')
    o.append('</svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8")
    print(json.dumps({"before": stats[0], "added": stats[1], "cross_links": cross, "guards": guards, "maxdepth": maxd,
                      "per_column": {COLS[k][0]: sum(counts[k].values()) for k in range(len(COLS))}}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
