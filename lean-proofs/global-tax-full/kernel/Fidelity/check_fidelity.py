"""Kernel fidelity: the UK and German rules re-expressed with TaxKernel parts (`kfid`) against the existing models.

    python3 check_fidelity.py            # writes fidelity/RESULTS.md and fidelity/results.json

UK: every household of the grid through `uktax` (default reading, England) and `kfid uk`; compares income tax,
Class 1 and child benefit net of the HICBC to the penny.
DE: every household through `detax`; for each assessment unit the tariff (§ 32a) and Soli on the zvE / Soli base
`detax` reports, through `kfid de`; and each employee's RV/AV/KV/PV on the wages (members in the Übergangsbereich
or mini-jobs are skipped: a kernel gap).
"""
import json
import os
import subprocess

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
KFID = os.path.join(HERE, "..", ".lake", "build", "bin", "kfid")
UKTAX = os.path.join(HOME, "cmp", "uk", "lean", ".lake", "build", "bin", "uktax")
DETAX = os.path.join(HOME, "cmp", "de", "lean", ".lake", "build", "bin", "detax")


def run(cmd, rows):
    p = subprocess.run(cmd, input="".join(json.dumps(r) + "\n" for r in rows), capture_output=True, text=True,
                       check=True)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]


def p(x):
    return int(round(x * 100))


def uk_grid():
    hs = []
    for w in range(0, 200001, 37):
        hs.append({"id": f"s{w}", "adults": [{"age": 40, "wages": w}]})
    for w in range(40000, 130001, 53):
        hs.append({"id": f"sp{w}", "adults": [{"age": 40, "wages": w}], "children": [{"age": 6}, {"age": 11}]})
    ws = [0, 5000, 11000, 12570, 13000, 15000, 20000, 30000, 37700, 45000, 50270, 50271, 55000, 60000, 70000,
          80000, 99999, 100000, 110000, 125140, 125141, 150000, 250000]
    for a in ws:
        for b in ws:
            for kids in (0, 1, 3):
                for m in (True, False):
                    hs.append({"id": f"c{a}_{b}_{kids}_{int(m)}", "adults": [{"age": 40, "wages": a}, {"age": 40, "wages": b}],
                               "married": m, "children": [{"age": 5 + i} for i in range(kids)]})
    return hs


def uk():
    hs = uk_grid()
    a = run([UKTAX], hs)
    b = run([KFID, "uk"], hs)
    stats = {"incomeTax": [0, 0], "employeeSocial": [0, 0], "benefits": [0, 0]}
    diffs = []
    for h, x, y in zip(hs, a, b):
        for k, kk in [("incomeTax", "incomeTax_p"), ("employeeSocial", "ni_p"), ("benefits", "benefits_p")]:
            stats[k][1] += 1
            if p(x[k]) == y[kk]:
                stats[k][0] += 1
            elif len(diffs) < 30:
                diffs.append({"id": h["id"], "line": k, "uktax_p": p(x[k]), "kernel_p": y[kk], "ma": y.get("ma")})
    return {"households": len(hs), "lines": stats, "first_differences": diffs}


def de_grid():
    hs = []
    for w in range(24000, 400001, 211):
        hs.append({"id": f"s{w}", "adults": [{"age": 40, "wages": w}]})
    for w in range(30000, 600001, 997):
        for share in (1.0, 0.6):
            w1 = round(w * share)
            hs.append({"id": f"m{w}_{share}", "adults": [{"age": 40, "wages": w1}, {"age": 40, "wages": w - w1}],
                       "married": True, "children": [{"age": 6}, {"age": 11}]})
    return hs


def de():
    hs = de_grid()
    outs = run([DETAX], hs)
    cases, mem_ref = [], []
    for h, o in zip(hs, outs):
        units = (o.get("detail") or {}).get("units", [])
        for ui, u in enumerate(units):
            kids = u.get("kidsCounted", 0)
            members = []
            refs = []
            for mi, m in enumerate(u.get("members", [])):
                if m.get("status") != "employee":
                    continue
                wages = h["adults"][mi]["wages"] if len(units) == 1 else h["adults"][ui]["wages"]
                members.append({"wages": wages, "kids": len(h.get("children", [])), "childless": not h.get("children")})
                refs.append(m)
            cases.append({"id": f"{h['id']}#{ui}", "joint": u.get("joint", False), "zvE": u["zvE"],
                          "soliBase": u["soliBase_SolZG3_2"], "members": members})
            mem_ref.append((u, refs))
    ks = run([KFID, "de"], cases)
    stats = {"tariff_32a": [0, 0], "soli": [0, 0], "RV": [0, 0], "AV": [0, 0], "KV": [0, 0], "PV": [0, 0]}
    diffs = []
    for c, k, (u, refs) in zip(cases, ks, mem_ref):
        pairs = [("tariff_32a", u["tariffTax_32a"], k["tariff"]), ("soli", p(u["soli"]), k["soli_c"])]
        for m, km in zip(refs, k["members"]):
            for line in ("RV", "AV", "KV", "PV"):
                pairs.append((line, p(m[line]), km[line + "_c"]))
        for line, ref, ker in pairs:
            stats[line][1] += 1
            if ref == ker:
                stats[line][0] += 1
            elif len(diffs) < 30:
                diffs.append({"id": c["id"], "line": line, "detax": ref, "kernel": ker})
    return {"households": len(hs), "units": len(cases), "lines": stats, "first_differences": diffs}


def main():
    res = {"UK": uk(), "DE": de()}
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    md = ["# Kernel fidelity: UK and German rules rebuilt from kernel parts vs the existing models", "",
          "Generated by `fidelity/check_fidelity.py` (`kfid` = `Fidelity/Uk.lean`, `Fidelity/De.lean`).", ""]
    for c, r in res.items():
        md.append(f"## {c}: {r['households']} households" + (f", {r['units']} assessment units" if "units" in r else ""))
        md.append("")
        md.append("| Line | equal | cases |")
        md.append("|---|---|---|")
        for k, (e, n) in r["lines"].items():
            md.append(f"| {k} | {e} | {n} |")
        md.append("")
        if r["first_differences"]:
            md.append("First differences: " + json.dumps(r["first_differences"][:10]))
            md.append("")
    open(os.path.join(HERE, "RESULTS.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
