"""Draw "Anatomy of a proof" for the tax work: one dot per Lean definition or theorem, by dependency depth.

    lake env lean tools/TaxAnatomy.lean > tax-anatomy.jsonl
    python tools/taxcode/anatomy.py tax-anatomy.jsonl anatomy.svg

Depth 0 is a declaration that uses no other declaration of the project (amounts, data, basic definitions); a
declaration's depth is one more than the deepest declaration it uses. Lines join each declaration to the ones that use
it. Dot area grows with the number of direct users. Compiler-generated declarations are left out.
"""
import json, math, re, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO = re.compile(r"\.(elim|ctorIdx|ctorElim|ctorElimType|noConfusion|noConfusionType|rec|recOn|casesOn|below|brecOn|"
                  r"binductionOn|ibelow|sizeOf_spec|_sizeOf_\d+|inj|injEq|ext|ext_iff|mk|toCtorIdx|ofNat|toNat|"
                  r"ofNat_toCtorIdx|toCtorIdx_ofNat|eq_def|eq_\d+|_unsafe_rec|instReprAux|repr|reprPrec)$")
COLS = [("checks", "DRAFTING CHECKS · CERTIFICATES", "#e8a85a", lambda m: m.startswith(("TaxCode.Model", "TaxCode.Checks", "TaxCode.Certs"))),
        ("tax", "2025 INCOME TAX", "#5fd3b4", lambda m: m.startswith("TaxCode.Individual")),
        ("search", "LOOPHOLE SEARCHES", "#b79bff", lambda m: m.startswith("LegalProofs.USTax"))]


def auto(n):
    return bool(AUTO.search(n)) or re.search(r"\.inst[A-Z]", n) or ".match_" in n or "._" in n


def main(inp, out):
    L = [json.loads(l) for l in open(inp, encoding="utf-8")]
    L = [x for x in L if not auto(x["n"])]
    names = {x["n"] for x in L}
    deps = {x["n"]: [d for d in x["d"] if d in names] for x in L}
    mod = {x["n"]: x["m"] for x in L}
    kind = {x["n"]: x["k"] for x in L}
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
    col = {}
    for n in names:
        for k, (key, _, _, f) in enumerate(COLS):
            if f(mod[n]):
                col[n] = k
    maxd = max(memo.values())
    # source lines of the modules drawn
    mods = {mod[n] for n in names}
    lines = sum(len((ROOT / (m.replace(".", "/") + ".lean")).read_text(encoding="utf-8").splitlines())
                for m in mods if (ROOT / (m.replace(".", "/") + ".lean")).exists())
    # layout: columns side by side; each depth band holds its dots in a grid
    W, X0, GAP = 1000, 92, 46
    counts = [collections.Counter(memo[n] for n in names if col[n] == k) for k in range(3)]
    widest = [max(c.values()) for c in counts]
    share = [w ** .8 for w in widest]
    usable = W - X0 - 40 - GAP * 2
    cw = [usable * s / sum(share) for s in share]
    cx = [X0 + sum(cw[:k]) + GAP * k for k in range(3)]
    steps = [6.0, 9.0, 9.0]          # the certificates' evidence data packs denser
    per_line = [max(1, int(cw[k] // steps[k])) for k in range(3)]
    band_h = [max(22, max(math.ceil(counts[k].get(d, 0) / per_line[k]) * steps[k] for k in range(3)) + 10) for d in range(maxd + 1)]
    Y0 = 254
    band_y = [Y0 + sum(band_h[:d]) for d in range(maxd + 1)]
    H_plot = sum(band_h)
    pos = {}
    for k in range(3):
        for d in range(maxd + 1):
            ns = sorted((n for n in names if col[n] == k and memo[n] == d), key=lambda n: (mod[n], n))
            pl = per_line[k]; step = steps[k]
            rows = math.ceil(len(ns) / pl) if ns else 0
            for i, n in enumerate(ns):
                r, c = divmod(i, pl)
                in_row = min(pl, len(ns) - r * pl)
                x = cx[k] + (cw[k] - in_row * step) / 2 + c * step + step / 2
                y = band_y[d] + (band_h[d] - rows * step) / 2 + r * step + step / 2
                pos[n] = (x, y)
    H = Y0 + H_plot + 100
    o = [f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" class="anat" '
         f'aria-label="Dependency map of the Lean tax code: {len(names)} declarations by depth">',
         f'<rect width="{W}" height="{H:.0f}" rx="14" fill="#0f1720"/>',
         '<text x="44" y="64" font-family="IBM Plex Sans,system-ui,sans-serif" font-size="20" fill="#9aa6b5">Formalizing the US tax code · a Lean declaration map</text>']
    stats = [(f"{len(names):,}", "DECLARATIONS"), (f"{sum(1 for n in names if kind[n] == 'thm'):,}", "THEOREMS"),
             (f"{sum(len(v) for v in deps.values()):,}", "DEPENDENCIES"), (f"{lines:,}", "SOURCE LINES"), (str(maxd), "MAX DEPTH")]
    for i, (v, lab) in enumerate(stats):
        x = 44 + i * 190
        o.append(f'<text x="{x}" y="124" font-family="IBM Plex Sans,system-ui,sans-serif" font-weight="600" font-size="34" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{x}" y="150" font-family="JetBrains Mono,monospace" font-size="13" letter-spacing="1" fill="#8b97a6">{lab}</text>')
    for k, (_, lab, c, _) in enumerate(COLS):
        o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 14}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="13" letter-spacing="1" fill="{c}">{lab}</text>')
    o.append(f'<text x="44" y="{Y0 - 52}" font-family="JetBrains Mono,monospace" font-size="13" letter-spacing="1" fill="#8b97a6">DEPENDENCY DEPTH ↓ · FOUNDATIONS TO RESULTS</text>')
    for d in range(0, maxd + 1):
        y = band_y[d] + band_h[d] / 2
        o.append(f'<line x1="{X0 - 8}" x2="{W - 30}" y1="{y:.1f}" y2="{y:.1f}" stroke="#1d2833" stroke-width="1"/>')
        o.append(f'<text x="{X0 - 22}" y="{y + 4:.1f}" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="13" fill="#7d8896">{d}</text>')
    o.append('<g stroke-width=".5" fill="none">')
    for n, ds in deps.items():
        x2, y2 = pos[n]
        for d in ds:
            x1, y1 = pos[d]
            c = COLS[col[n]][2]
            my = (y1 + y2) / 2
            o.append(f'<path d="M{x1:.1f} {y1:.1f}C{x1:.1f} {my:.1f} {x2:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{c}" stroke-opacity=".09"/>')
    o.append('</g><g>')
    for n in sorted(names, key=lambda n: users[n]):
        x, y = pos[n]
        r = min(5.5, (1.2 if col[n] == 0 else 1.7) + 0.9 * math.sqrt(users[n]))
        c = COLS[col[n]][2]
        op = 1 if kind[n] == "thm" else .78
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" fill-opacity="{op}"><title>{n}</title></circle>')
    o.append('</g>')
    yb = Y0 + H_plot + 40
    for i, t in enumerate(["One dot = one Lean definition or theorem. Lines join each one to the declarations that use it.",
                           "Larger dots have more direct users. Depth is the longest chain of definitions beneath it."]):
        o.append(f'<text x="44" y="{yb + i * 26}" font-family="IBM Plex Sans,system-ui,sans-serif" font-size="17" fill="#d6dbe2">{t}</text>')
    o.append('</svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8")
    print(len(names), "declarations;", sum(len(v) for v in deps.values()), "edges; depth", maxd, "; lines", lines,
          "; per column", [sum(counts[k].values()) for k in range(3)])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
