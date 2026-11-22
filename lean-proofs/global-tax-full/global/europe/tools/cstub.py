#!/usr/bin/env python3
"""cstub.py PKGFILE: for countries whose texts were not reached in a package pass, write tools/specs/<CC>_<Fam>.py
with no family (nothing computed) and one grade-C `unsupported` summary entry per tax, saying what was tried and what
would unlock it (DESIGN §7.2). PKGFILE is a Python file defining FAM, OECD_TAXES [(oecd, tax-label, statute)], and
TRIED {cc: (tried, unlock)}; an `unsupported` line is listed on every entity so the output never silently omits it."""
import os, sys
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs")
d = {}
exec(open(sys.argv[1], encoding="utf-8").read(), d)
for cc, rows in d["TRIED"].items():
    taxes, uns = [], []
    for oecd, label, statute, tried, unlock in rows:
        taxes.append({"oecd": oecd, "tax": label, "statute": statute, "grade": "C", "status": "unsupported",
                      "kernel_parts": [], "tried": tried, "unsupported": [f"would unlock: {unlock}"]})
        uns.append((d.get("COND", "true"), f"{oecd} {label}: not modelled (grade C: {tried})"))
    S = dict(cc=cc, fam=d["FAM"], families=[], doc=f"# {cc} 2025: {d['FAM']} family not reached (grade C)\n\n"
             + "".join(f"* {o} {l} ({s}): tried {t}; would unlock: {u}\n" for o, l, s, t, u in rows),
             notes=[], unsupported=uns, guards=[], taxes=taxes)
    open(os.path.join(OUT, f"{cc}_{d['FAM']}.py"), "w", encoding="utf-8").write("S = " + repr(S) + "\n")
    print(cc, d["FAM"], "C stub")
