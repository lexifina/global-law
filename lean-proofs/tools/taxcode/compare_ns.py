"""Draw our Lean tax work beside the Navier–Stokes + Euler formalization, as module import graphs at the same scale.

    python compare_ns.py <NavierStokesAndEuler clone> <lean-proofs dir> out.svg

One dot per Lean module, placed by import depth (0 = imports no local module), as in the "Anatomy of a proof" chart of
that repository. Local imports only (Mathlib and Lean core excluded). Source lines include comments and blank lines.
For our side: the modules under TaxCode/ and LegalProofs/USTax/ tracked by git, other than another project's Hunt/.
"""
import collections, math, re, subprocess, sys
from pathlib import Path

IMP = re.compile(r"^\s*import\s+(.+)$", re.M)


def graph(root: Path, files):
    mods = {}
    for f in files:
        name = ".".join(f.relative_to(root).with_suffix("").parts)
        text = f.read_text(encoding="utf-8", errors="replace")
        imps = [i for line in IMP.findall(text) for i in line.split()]
        mods[name] = (imps, len(text.splitlines()))
    deps = {m: [i for i in imps if i in mods] for m, (imps, _) in mods.items()}
    memo = {}

    def depth(m, stack=()):
        if m in memo:
            return memo[m]
        if m in stack:
            return 0
        memo[m] = 1 + max((depth(d, stack + (m,)) for d in deps[m]), default=-1)
        return memo[m]
    for m in mods:
        depth(m)
    users = collections.Counter(d for ds in deps.values() for d in ds)
    return {"depth": memo, "deps": deps, "users": users, "lines": sum(l for _, l in mods.values()),
            "imports": sum(len(v) for v in deps.values())}


def main(ns_dir, ours_dir, out):
    ns_root = Path(ns_dir)
    ns_files = [p for p in ns_root.rglob("*.lean") if ".lake" not in p.parts and p.name != "lakefile.lean"]
    ours_root = Path(ours_dir)
    tracked = subprocess.run(["git", "-C", str(ours_root), "ls-files", "*.lean"], capture_output=True, text=True).stdout.split()
    our_files = [ours_root / t for t in tracked
                 if (t.startswith("TaxCode/") or t.startswith("LegalProofs/USTax")) and "/Hunt" not in t]
    G = [("NAVIER–STOKES + EULER", "#e8a85a", graph(ns_root, ns_files)), ("US TAX CODE (OURS)", "#5fd3b4", graph(ours_root, our_files))]
    maxd = max(max(g["depth"].values()) for _, _, g in G)
    W = 1000; X0 = 92; Y0 = 284; ROW = 13.5; step = 8.4
    colw = [560, 230]; cx = [X0 + 10, X0 + 10 + colw[0] + 60]
    H = Y0 + (maxd + 1) * ROW + 100
    o = [f'<svg viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Module import graphs: Navier–Stokes and Euler beside our tax code, at the same scale">',
         f'<rect width="{W}" height="{H:.0f}" rx="14" fill="#0f1720"/>',
         '<text x="44" y="64" font-family="IBM Plex Sans,system-ui,sans-serif" font-size="19" fill="#9aa6b5">Navier–Stokes + Euler beside the US tax code · Lean module import graphs</text>']
    for k, (lab, c, g) in enumerate(G):
        y = 104 + k * 70
        o.append(f'<circle cx="52" cy="{y + 18}" r="7" fill="{c}"/>')
        o.append(f'<text x="68" y="{y + 24}" font-family="JetBrains Mono,monospace" font-size="13" letter-spacing="1" fill="{c}">{lab}</text>')
        stats = [(f"{len(g['depth']):,}", "MODULES"), (f"{g['imports']:,}", "LOCAL IMPORTS"), (f"{g['lines']:,}", "SOURCE LINES"),
                 (str(max(g['depth'].values())), "MAX DEPTH")]
        for i, (v, s) in enumerate(stats):
            x = 330 + i * 165
            o.append(f'<text x="{x}" y="{y + 24}" font-family="IBM Plex Sans,system-ui,sans-serif" font-weight="600" font-size="26" fill="#eef1f5">{v}</text>')
            o.append(f'<text x="{x}" y="{y + 44}" font-family="JetBrains Mono,monospace" font-size="11" letter-spacing="1" fill="#8b97a6">{s}</text>')
    o.append(f'<text x="44" y="{Y0 - 30}" font-family="JetBrains Mono,monospace" font-size="13" letter-spacing="1" fill="#8b97a6">IMPORT DEPTH ↓ · FOUNDATIONS TO RESULTS</text>')
    for d in range(0, maxd + 1, 12):
        y = Y0 + d * ROW + ROW / 2
        o.append(f'<line x1="{X0 - 6}" x2="{W - 30}" y1="{y:.1f}" y2="{y:.1f}" stroke="#1d2833"/>')
        o.append(f'<text x="{X0 - 20}" y="{y + 4:.1f}" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="13" fill="#7d8896">{d}</text>')
    for k, (lab, c, g) in enumerate(G):
        pos = {}
        rows = collections.defaultdict(list)
        for m, d in g["depth"].items():
            rows[d].append(m)
        per = max(1, int(colw[k] // step))
        for d, ms in rows.items():
            ms.sort()
            # spread rows that overflow into the band below the depth line, as the original does
            for i, m in enumerate(ms):
                r, cidx = divmod(i, per)
                n_in = min(per, len(ms) - r * per)
                x = cx[k] + (colw[k] - n_in * step) / 2 + cidx * step + step / 2
                y = Y0 + d * ROW + ROW / 2 + r * 3.2
                pos[m] = (x, y)
        o.append('<g fill="none" stroke-width=".4">')
        for m, ds in g["deps"].items():
            for dd in ds:
                (x1, y1), (x2, y2) = pos[dd], pos[m]
                o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-opacity=".07"/>')
        o.append('</g>')
        for m, (x, y) in pos.items():
            r = min(4.2, 1.5 + 0.55 * math.sqrt(g["users"][m]))
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}"><title>{m}</title></circle>')
        o.append(f'<text x="{cx[k] + colw[k] / 2:.0f}" y="{Y0 - 8}" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="12" letter-spacing="1" fill="{c}">{lab}</text>')
    yb = Y0 + (maxd + 1) * ROW + 50
    o.append(f'<text x="44" y="{yb}" font-family="IBM Plex Sans,system-ui,sans-serif" font-size="17" fill="#d6dbe2">One dot = one Lean module. Lines connect imports to their users. Both drawn the same way, at the same scale.</text>')
    o.append('</svg>')
    Path(out).write_text("\n".join(o), encoding="utf-8")
    for lab, _, g in G:
        print(lab, len(g["depth"]), "modules", g["imports"], "imports", g["lines"], "lines, depth", max(g["depth"].values()))


if __name__ == "__main__":
    main(*sys.argv[1:4])
