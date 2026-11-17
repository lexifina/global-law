"""Step 3d (free part): every production-simulator answer already saved for income 2022 or 2023 (runs/*.jsonl,
earlier sessions), run through Catala, M and Lean on the same boxes. Production prints the number of parts and the
revenu brut global, the two figures Catala computes.

usage: catala_saved_sim.py outdir
Writes outdir/saved_rows.jsonl and outdir/saved_report.txt.
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catala_lib import run_catala, run_lean, run_m, mget
from of_calc_tests import in_lean_scope

R = os.path.expanduser("~/fr/runs")
SIMS = ["sim_targets_v2.jsonl", "sim_fam.jsonl", "pas/sim_prod.jsonl", "loop/sim.jsonl", "ofsuite/sim.jsonl"]
INPUTS = ["targets.jsonl", "fam.jsonl", "pas/prod_cases.jsonl", "loop/sim.jsonl", "ofsuite/sim_cases.jsonl",
          "ofsuite/sim_cases2.jsonl"]   # later files win (sim_cases2 = the corrected pension boxes)


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    sims = {}
    for f in SIMS:
        for l in open(f"{R}/{f}"):
            d = json.loads(l)
            if d.get("year") in (2022, 2023) and isinstance(d.get("sim"), dict):
                sims[d["id"]] = (f, d["sim"])
    cases = {}
    for f in INPUTS:
        for l in open(f"{R}/{f}"):
            d = json.loads(l)
            if "boxes" in d and d["id"] in sims and d.get("year") in (2022, 2023):
                cases[d["id"]] = {"id": d["id"], "year": d["year"], "boxes": d["boxes"]}
    cs = list(cases.values())
    cat = run_catala(cs)
    lean = run_lean([c for c in cs if in_lean_scope(c["boxes"])])
    m = {}
    for y in (2022, 2023):
        m.update(run_m(y, [c for c in cs if c["year"] == y]))
    st = collections.Counter()
    lines = []
    with open(f"{outdir}/saved_rows.jsonl", "w") as f:
        for c in cs:
            src, s = sims[c["id"]]
            k, mm, ll = cat.get(c["id"], {}), m.get(c["id"]), lean.get(c["id"])
            row = {"id": c["id"], "year": c["year"], "src": src, "boxes": c["boxes"], "sim": s, "catala": k,
                   "m": mm, "lean": ll}
            f.write(json.dumps(row) + "\n")
            st["n"] += 1
            if "_error" in s:
                st["prod_refused"] += 1
                st["prod_refused_catala_err"] += "ERR" in k
                continue
            sp = s.get("NBPT")
            if sp is None:
                continue
            st["prod_parts"] += 1
            if "ERR" in k:
                st["catala_err_on_computed"] += 1
                lines.append(f"{c['id']} {c['year']} production computes, Catala stops: {k['ERR']}  {fam(c)}")
                continue
            ok = abs(k["NBPT"] - sp) < 0.01
            st["catala_parts_eq"] += ok
            if mget(mm, "NBPT") is not None:
                st["m_parts_n"] += 1
                st["m_parts_eq"] += abs(mget(mm, "NBPT") - sp) < 0.01
            if ll is not None:
                st["lean_parts_n"] += 1
                st["lean_parts_eq"] += abs(ll["NBPT"] - sp) < 0.01
            if not ok:
                lines.append(f"{c['id']} {c['year']} parts: production {sp} Catala {k['NBPT']} M {mget(mm, 'NBPT')} "
                             f"Lean {(ll or {}).get('NBPT')}  {fam(c)}")
            if not k.get("IGNORED") and s.get("RBG") is not None:
                st["rbg_in_scope"] += 1
                okr = abs(k["RBG"] - s["RBG"]) <= 0.5
                st["catala_rbg_eq"] += okr
                if not okr:
                    lines.append(f"{c['id']} {c['year']} RBG: production {s['RBG']} Catala {k['RBG']} "
                                 f"M {mget(mm, 'RBG1')}  {c['boxes']}")
    with open(f"{outdir}/saved_report.txt", "w") as f:
        f.write(json.dumps(dict(st), indent=1) + "\n\n" + "\n".join(lines) + "\n")
    print(open(f"{outdir}/saved_report.txt").read())


def fam(c):
    return {k: v for k, v in c["boxes"].items() if k[0] == "0" and k[:2] not in ("0F", "0H", "0J")}


if __name__ == "__main__":
    main()
