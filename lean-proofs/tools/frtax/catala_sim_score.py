"""Score Catala, M and Lean against the production simulator on income 2022-2023: the answers saved by earlier
sessions (catala_saved_sim.py rows) and the 24 sent for this comparison (runs/catala/sim.jsonl).
Figures: parts (NBPT) on every return; revenu brut global (RBG) on returns whose boxes Catala reads in full
(production prints "Revenu brut global ou déficit" only when it is not nil, so a missing line with a nil net
taxable income is read as RBG 0).

usage: catala_sim_score.py   -> runs/catala/sim_score.txt
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catala_lib import run_catala, run_lean, run_m, mget
from of_calc_tests import in_lean_scope

R = os.path.expanduser("~/fr/runs/catala")


def main():
    saved = [json.loads(l) for l in open(f"{R}/saved/saved_rows.jsonl")]
    sims = {json.loads(l)["id"]: json.loads(l)["sim"] for l in open(f"{R}/sim.jsonl")}
    new = [json.loads(l) for l in open(f"{R}/sim_cases.jsonl")]
    k = run_catala(new)
    l = run_lean([c for c in new if in_lean_scope(c["boxes"])])
    m = {}
    for y in (2022, 2023):
        m.update(run_m(y, [c for c in new if c["year"] == y]))
    rows = [dict(r, origin="saved") for r in saved] + [
        {"id": c["id"], "year": c["year"], "boxes": c["boxes"], "sim": sims[c["id"]], "catala": k[c["id"]],
         "m": m[c["id"]], "lean": l.get(c["id"]), "origin": "new"} for c in new]
    st = {p: collections.Counter() for p in ("catala", "m", "lean")}
    for r in rows:
        s = r["sim"]
        prod_ref = "_error" in s
        if not prod_ref and s.get("RBG") is None and s.get("RNI") == 0:
            s = dict(s, RBG=0.0)
        for p in ("catala", "m", "lean"):
            g = r[p]
            if g is None:
                st[p]["out of scope"] += 1
                continue
            refused = ("ERR" in g) if p == "catala" else ("_refused" in g if p == "m" else False)
            if prod_ref:
                st[p]["both refuse" if refused else "computes what production refuses"] += 1
                continue
            if refused:
                st[p]["refuses what production computes"] += 1
                continue
            nb = g.get("NBPT") if p != "m" else mget(g, "NBPT")
            st[p]["parts compared"] += 1
            st[p]["parts equal"] += abs(nb - s["NBPT"]) < 0.01
            in_scope = not (r["catala"] or {}).get("IGNORED") and "ERR" not in (r["catala"] or {})
            if in_scope and s.get("RBG") is not None:
                v = g.get("RBG") if p == "catala" else (mget(g, "RBG1") if p == "m" else g.get("RNG"))
                if p == "lean" and any(b[0] == "6" for b in r["boxes"]):
                    continue
                st[p]["RBG compared"] += 1
                st[p]["RBG equal"] += v is not None and abs(v - s["RBG"]) <= 0.5
    with open(f"{R}/sim_score.txt", "w") as f:
        f.write(f"{len(rows)} production answers for income 2022-2023 ({len(saved)} saved, {len(new)} new)\n")
        for p, c in st.items():
            f.write(f"{p:7s} " + "; ".join(f"{k} {v}" for k, v in sorted(c.items())) + "\n")
    print(open(f"{R}/sim_score.txt").read())


if __name__ == "__main__":
    main()
