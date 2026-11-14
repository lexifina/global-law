"""Three single-formalism maps in one style, for the cycling figure of the case-law post:

    US CASE LAW             declaration map, from ../caselaw-anatomy.jsonl (tools/CaseLawAnatomy.lean)
    US TAX CODE             declaration map, from ../law-anatomy.jsonl (tools/LawAnatomy.lean)
    NAVIER-STOKES + EULER   module import map, cut out of the same-scale comparison drawn by tools/taxcode/compare_ns.py

    python tools/caselaw/formalism_views.py OUT_DIR [--ns compare-navier-stokes.svg --ns-src CLONE]

Each map has one title, the counts, the depth axis and the dots: no eyebrow line and no caption inside the image (the
page carries the caption). The column sets and the generated-name filter are the ones of caselaw_v1v2_anatomy.py and
law_anatomy.py. Source-line counts are passed in, because the trees have moved on since the extractions were made:
they are the figures those two scripts printed for the same extractions (caselaw-v1-v2.json; the law-anatomy figure).
The declaration and theorem counts are recomputed here and must equal the recorded ones, or the script stops.
"""
import argparse, collections, json, math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import caselaw_v1v2_anatomy as cl   # noqa: E402
import law_anatomy as la            # noqa: E402

ROOT = HERE.parents[1]              # lean-proofs
F = "IBM Plex Sans,system-ui,sans-serif"
M = "JetBrains Mono,ui-monospace,monospace"
TAX_COLOURS = {"checks": "#ffb35c", "tax": "#5fd3b4", "search": "#b79cf0", "court": "#f08a6b", "estate": "#6fb7e0"}


def header(o, W, title, vals):
    o.append(f'<text x="44" y="60" font-family="{F}" font-weight="600" font-size="26" letter-spacing=".6" fill="#eef1f5">{title}</text>')
    for i, (v, s) in enumerate(vals):
        x = 44 + i * 170
        o.append(f'<text x="{x}" y="118" font-family="{F}" font-weight="600" font-size="26" fill="#eef1f5">{v}</text>')
        o.append(f'<text x="{x}" y="140" font-family="{M}" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')


def decl_map(inp, cols, auto, title, lines, expect, out, W=1100, label=None):
    L = [json.loads(l) for l in open(inp, encoding="utf-8")]
    L = [x for x in L if not auto(x["n"])]
    mod = {x["n"]: x["m"] for x in L}
    kind = {x["n"]: x["k"] for x in L}
    col = {}
    for n in mod:
        for k, c in enumerate(cols):
            if c[3](mod[n]):
                col[n] = k
                break
    names = set(col)
    deps = {x["n"]: [d for d in x["d"] if d in names] for x in L if x["n"] in names}
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
    got = (len(names), sum(1 for n in names if kind[n] == "thm"))
    if got != expect:
        sys.exit(f"formalism_views: {title}: {got} declarations/theorems, expected {expect}")

    X0, GAP = 70, 18
    counts = [collections.Counter(memo[n] for n in names if col[n] == k) for k in range(len(cols))]
    share = [max(max(c.values()) if c else 1, 12) ** .62 for c in counts]
    usable = W - X0 - 30 - GAP * (len(cols) - 1)
    cw, cx, x = [], [], X0
    for k in range(len(cols)):
        cw.append(usable * share[k] / sum(share))
        cx.append(x)
        x += cw[k] + GAP
    step = 7.0
    per_line = [max(1, int(cw[k] // step)) for k in range(len(cols))]
    band_h = [max(16, max(math.ceil(counts[k].get(d, 0) / per_line[k]) * step for k in range(len(cols))) + 8)
              for d in range(maxd + 1)]
    Y0 = 232
    band_y = [Y0 + sum(band_h[:d]) for d in range(maxd + 1)]
    pos = {}
    for k in range(len(cols)):
        for d in range(maxd + 1):
            ns = sorted((n for n in names if col[n] == k and memo[n] == d), key=lambda n: (mod[n], n))
            pl = per_line[k]
            rows = math.ceil(len(ns) / pl) if ns else 0
            for i, n in enumerate(ns):
                r, c = divmod(i, pl)
                n_in = min(pl, len(ns) - r * pl)
                pos[n] = (cx[k] + (cw[k] - n_in * step) / 2 + c * step + step / 2,
                          band_y[d] + (band_h[d] - rows * step) / 2 + r * step + step / 2)
    H = Y0 + sum(band_h) + 34
    o = [f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label or title}">',
         f'<rect width="{W}" height="{H:.0f}" rx="14" fill="#0f1720"/>']
    # the same four counts on every map
    header(o, W, title, [(f"{got[0]:,}", "DECLARATIONS"), (f"{got[1]:,}", "THEOREMS"),
                         (f"{len({mod[n] for n in names}):,}", "MODULES"), (f"{lines:,}", "LINES")])
    o.append(f'<text x="44" y="{Y0 - 44}" font-family="{M}" font-size="11" letter-spacing="1" fill="#7d8896">DEPENDENCY DEPTH ↓</text>')
    for d in range(0, maxd + 1, 2):
        y = band_y[d] + band_h[d] / 2
        o.append(f'<line x1="{X0 - 6}" x2="{W - 24}" y1="{y:.1f}" y2="{y:.1f}" stroke="#18222d"/>')
        o.append(f'<text x="{X0 - 14}" y="{y + 4:.1f}" text-anchor="end" font-family="{M}" font-size="11" fill="#7d8896">{d}</text>')
    for k, c in enumerate(cols):
        words = c[1].split(" + ")
        if len(c[1]) * 6.4 < cw[k] + GAP or len(words) == 1:
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 12}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{c[1]}</text>')
        else:
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 24}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{words[0]} +</text>')
            o.append(f'<text x="{cx[k] + cw[k] / 2:.0f}" y="{Y0 - 11}" text-anchor="middle" font-family="{M}" font-size="10" letter-spacing=".5" fill="{c[2]}">{" + ".join(words[1:])}</text>')
    o.append('<g fill="none" stroke-width=".45">')
    for n, ds in deps.items():
        x2, y2 = pos[n]
        for d in ds:
            x1, y1 = pos[d]
            my = (y1 + y2) / 2
            o.append(f'<path d="M{x1:.1f} {y1:.1f}C{x1:.1f} {my:.1f} {x2:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{cols[col[n]][2]}" stroke-opacity=".1"/>')
    o.append('</g><g>')
    for n in sorted(names, key=lambda n: users[n]):
        x, y = pos[n]
        r = min(4.6, 1.3 + .75 * math.sqrt(users[n])) * 1.05
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{cols[col[n]][2]}" fill-opacity="{1 if kind[n] == "thm" else .8:.2f}"><title>{n}</title></circle>')
    o.append('</g></svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8", newline="\n")
    print(title, got, "lines", lines, "depth", maxd, "->", out)


KW = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|partial|unsafe|nonrec|scoped|local)\s+)*"
                r"(theorem|lemma|def|abbrev|structure|inductive|class|instance|opaque|axiom)\b", re.M)


def strip_comments(t):
    out, i, depth = [], 0, 0
    while i < len(t):
        if t.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth and t.startswith("-/", i):
            depth -= 1; i += 2; continue
        if depth:
            if t[i] == "\n":
                out.append("\n")
            i += 1; continue
        if t.startswith("--", i):
            j = t.find("\n", i); i = len(t) if j < 0 else j; continue
        out.append(t[i]); i += 1
    return "".join(out)


def source_counts(root):
    """Declarations and theorems of a Lean tree, counted from the source by keyword (no build needed). This counts
    what is written; Lean's own count, used for our two maps, also includes what a `structure` generates, so it runs
    higher (CaseLaw2 as published: 688 and 140 by keyword, 992 and 165 by Lean)."""
    root = Path(root)
    files = [p for p in root.rglob("*.lean") if ".lake" not in p.parts and p.name != "lakefile.lean"]
    c = collections.Counter()
    lines = 0
    for f in files:
        t = f.read_text(encoding="utf-8", errors="replace")
        lines += len(t.splitlines())
        c.update(m.group(1) for m in KW.finditer(strip_comments(t)))
    return len(files), lines, sum(c.values()), c["theorem"] + c["lemma"]


def ns_map(src, out, ns_src, title="NAVIER–STOKES + EULER"):
    """The Navier-Stokes column of the same-scale comparison, on its own: same dots, same positions."""
    L = Path(src).read_text(encoding="utf-8").split("\n")
    num = [re.search(r">([^<]+)</text>", l).group(1) for l in L[5:13:2]]
    lab = [re.search(r">([^<]+)</text>", l).group(1) for l in L[6:13:2]]
    assert lab == ["MODULES", "LOCAL IMPORTS", "SOURCE LINES", "MAX DEPTH"], lab
    H0 = float(re.search(r'viewBox="0 0 1000 (\d+)"', L[0]).group(1))
    UP, SHIFT = 62, 120
    H = H0 - 100 - UP + 34          # the original leaves 100 below the last row for its caption
    axis = [re.sub(r">[^<]*</text>", ">DEPENDENCY DEPTH ↓</text>", l) for l in L if "IMPORT DEPTH" in l]
    grid = [l for l in L if 'stroke="#1d2833"' in l or ('fill="#7d8896"' in l and 'text-anchor="end"' in l)]
    edges = [l for l in L if l.startswith("<line") and "#e8a85a" in l]
    dots = [l for l in L if l.startswith("<circle") and "#e8a85a" in l and "<title>" in l]
    assert len(dots) == int(num[0].replace(",", "")), (len(dots), num)
    o = [f'<svg viewBox="0 0 1000 {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Module import map of the Navier–Stokes and Euler formalization in Lean">',
         f'<rect width="1000" height="{H:.0f}" rx="14" fill="#0f1720"/>']
    nmod, nlines, ndecl, nthm = source_counts(ns_src)
    # the clone must be the tree the comparison was drawn from
    assert (f"{nmod:,}", f"{nlines:,}") == (num[0], num[2]), (nmod, nlines, num)
    header(o, 1000, title, [(f"{ndecl:,}", "DECLARATIONS"), (f"{nthm:,}", "THEOREMS"), (num[0], "MODULES"), (num[2], "LINES")])
    o.append(f'<g transform="translate(0,-{UP})">')
    o += axis + grid
    o.append(f'<g transform="translate({SHIFT},0)"><g fill="none" stroke-width=".4">')
    o += edges
    o.append('</g>')
    o += dots
    o.append('</g></g></svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8", newline="\n")
    print(title, num, "->", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--ns", default=None, help="compare-navier-stokes.svg from tools/taxcode/compare_ns.py")
    ap.add_argument("--ns-src", default=None, help="a clone of openai/NavierStokesAndEuler, for its declaration counts")
    a = ap.parse_args()
    out = Path(a.out_dir)
    v2 = [c for c in cl.COLS if c[4] == 1]
    decl_map(ROOT.parent / "caselaw-anatomy.jsonl", v2, cl.auto, "US CASE LAW", 5676, (992, 165), out / "caselaw-v2.svg",
             label="Lean declaration map of the US case-law model")
    tax = [(c[0], c[1], TAX_COLOURS[c[0]], c[3], 0) for c in la.COLS if c[4] == 0]
    decl_map(ROOT.parent / "law-anatomy.jsonl", tax, la.auto, "US TAX CODE", 19995, (3361, 662), out / "tax-code.svg",
             label="Lean declaration map of our formalization of the US tax code")
    if a.ns:
        ns_map(a.ns, out / "navier-stokes.svg", a.ns_src)
