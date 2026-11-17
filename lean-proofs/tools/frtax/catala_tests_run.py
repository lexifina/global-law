"""Step 3a: the lawyer-written tests of catala-examples/impot_revenu/tests, converted to 2042 boxes, through Catala
(our batch driver), Mlang, Lean and OpenFisca, each scored against the test's stated values.

usage: catala_tests_run.py outdir      (writes outdir/tests_cases.jsonl, tests_results.json, tests_scoreboard.txt)

Of the 27 test scopes, 4 are unit tests of the OCaml oracles (ProRata1-3, DéficitsAntérieurs1: no household),
6 declare exceptional or deferred income under art. 163-0 A (case 0XX, a list of amounts with a regime, an
échéance and a category; no box in our format): BIC2, BIC3, TS7, TS8, TS9, TS11. The 17 others map to boxes.
The family boxes the Catala test leaves implicit are filled so that M accepts the return: the situation box
(Catala's interface defaults to a single person) and birth years (declarants 1980/1982, children by age).
Figures compared: NBPT (parts), RBG (the household's revenu brut global: here the single category's total), and
for the BNC tests the non-professional deficit carried forward.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catala_lib import run_catala, run_lean, run_m, mget
from of_calc_tests import in_lean_scope

D1 = {"0DA": 1980}
D2 = {"0DA": 1980, "0DB": 1982}
T = [
    # id, Catala test, year, boxes, stated figures
    ("bic1", "BénéficesIndustrielsCommerciaux1", 2023,
     {"0AC": 1, **D1, "5NO": 7514, "5NP": 3859, "5NC": 11225, "5NG": 1000, "5QS": 3000, "5KC": 60000, "5UI": 500,
      "5KF": 10000}, {"RBG": 65863}),
    ("bnc1", "BénéficesNonCommerciaux1", 2022,
     {"0AM": 1, **D2, "5JG": 1000, "5JJ": 15000, "5LU": 3000}, {"RBG": 0, "DEFNP": 12020}),
    ("bnc2", "BénéficesNonCommerciaux2", 2022,   # prior deficits 2019, 2020, 2021 = 5KT, 5LT, 5MT on the 2022 form
     {"0AC": 1, **D1, "5JG": 15798, "5KT": 5000, "5LT": 2000, "5MT": 15000}, {"RBG": 0, "DEFANT": 6202}),
    ("bnc3", "BénéficesNonCommerciaux3", 2022,   # declarant 3 is a dependant (PAC column 5M.)
     {"0AM": 1, **D2, "0CF": 1, "0F0": 2010, "5JG": 22540, "5JJ": 4000, "5RF": 10000, "5MU": 1000, "5MY": 200,
      "5MD": 500, "5LT": 1000, "5MT": 25000}, {"RBG": 2900}),
    ("bnc4", "BénéficesNonCommerciaux4", 2023,
     {"0AC": 1, **D1, "5KU": 12399, "5JG": 52676, "5JJ": 76988, "5SO": 1374}, {"RBG": 0, "DEFNP": 16129}),
    ("np1", "NombreDeParts1", 2022, {"0AO": 1, **D2, "0CF": 2, "0F0": 2012, "0F1": 2015}, {"NBPT": 3.0}),
    ("np2", "NombreDeParts2", 2022, {"0AM": 1, **D2, "0CF": 3, "0F0": 2008, "0F1": 2011, "0F2": 2014, "0AP": 1},
     {"NBPT": 4.5}),
    # 0DN = 1.5 (attached married children, one of whose children is in shared residence) has no box value:
    # 0DN takes whole persons; the parts do not depend on it, the abattement (9 552 €) is not compared
    ("np3", "NombreDeParts3", 2022, {"0AV": 1, **D1, "0AG": 1, "0CF": 1, "0F0": 2012, "0DJ": 2, "0J0": 2001,
                                     "0J1": 2002}, {"NBPT": 4.0}),
    ("np4", "NombreDeParts4", 2022, {"0AO": 1, **D2, "0CH": 1, "0H0": 2014}, {"NBPT": 2.25}),
    ("np5", "NombreDeParts5", 2022, {"0AM": 1, **D2, "0CF": 2, "0F0": 2012, "0F1": 2015, "0CH": 1, "0H0": 2016,
                                     "0CI": 1}, {"NBPT": 3.75}),
    ("ts1", "TraitementsSalaires1", 2022, {"0AC": 1, **D1, "1AJ": 10000}, {"RBG": 9000}),
    ("ts2", "TraitementsSalaires2", 2022, {"0AC": 1, **D1, "1AJ": 10000, "1AK": 2000}, {"RBG": 8000}),
    ("ts3", "TraitementsSalaires3", 2022, {"0AV": 1, **D1, "1AS": 20000, "1AT": 30000}, {"NBPT": 1.0, "RBG": 18000}),
    ("ts4", "TraitementsSalaires4", 2022, {"0AM": 1, **D2, "1AS": 52000, "1BS": 60000}, {"RBG": 107877}),
    ("ts5", "TraitementsSalaires5", 2022, {"0AM": 1, **D2, "0CF": 1, "0F0": 2010, "1AS": 72000, "1BS": 300,
                                          "1CT": 100000}, {"RBG": 68177}),
    ("ts6", "TraitementsSalaires6", 2022, {"0AM": 1, **D2, "0CF": 1, "0F0": 2006, "1AJ": 48000, "1AK": 4000,
                                          "1BS": 42000, "1BO": 3500, "1CJ": 3000}, {"RBG": 87105}),
    ("ts10", "TraitementsSalaires10", 2022, {"0AM": 1, **D2, "1AJ": 40000, "1BJ": 20000, "1AW": 15000},
     {"RBG": 64500}),
]
UNMAPPED = {"BénéficesIndustrielsCommerciaux2": "0XX (art. 163-0 A)", "BénéficesIndustrielsCommerciaux3": "0XX",
            "TraitementsSalaires7": "0XX", "TraitementsSalaires8": "0XX", "TraitementsSalaires9": "0XX",
            "TraitementsSalaires11": "0XX", "DéficitsAntérieurs1": "oracle unit test", "ProRata1": "oracle unit test",
            "ProRata2": "oracle unit test", "ProRata3": "oracle unit test"}


def figures(who, r):
    """the stated figures as each program reports them (None: not computed / refused / out of scope)"""
    if r is None:
        return {}
    if who == "catala":
        if "ERR" in r:
            return {}
        return {"NBPT": r.get("NBPT"), "RBG": r.get("RBG"), "DEFNP": r.get("BNC_DEFNP"), "DEFANT": r.get("BNC_DEFANT")}
    if who == "m":
        if "_refused" in r:
            return {}
        defs = [mget(r, f"BNCDF{k}") for k in range(1, 7)]
        return {"NBPT": mget(r, "NBPT"), "RBG": mget(r, "RBG1"), "DEFNP": defs[0], "DEFANT": sum(defs[1:])}
    if who == "lean":
        return {"NBPT": r.get("NBPT"), "RBG": r.get("RNG")}   # no charges in these returns: RNG = RBG
    if who == "of":
        if "of" not in r:
            return {}
        o = r["of"]
        return {"NBPT": o.get("nbptr"), "RBG": o.get("rbg")}
    return {}


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    cases = [{"id": i, "year": y, "boxes": b, "catala_test": t, "stated": s} for i, t, y, b, s in T]
    with open(f"{outdir}/tests_cases.jsonl", "w") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    cat = run_catala(cases)
    lean = run_lean([c for c in cases if in_lean_scope(c["boxes"])])
    m = {}
    for y in sorted({c["year"] for c in cases}):
        m.update(run_m(y, [c for c in cases if c["year"] == y]))
    py = os.path.expanduser("~/fr/venv-of/bin/python")
    subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "catala_openfisca.py"),
                    f"{outdir}/tests_cases.jsonl", f"{outdir}/tests_of.jsonl"], check=True)
    of = {json.loads(l)["id"]: json.loads(l) for l in open(f"{outdir}/tests_of.jsonl")}
    rows, score = [], {w: [0, 0, 0] for w in ("catala", "m", "lean", "of")}   # equal, differ, not computed
    for c in cases:
        res = {"catala": cat.get(c["id"]), "m": m.get(c["id"]), "lean": lean.get(c["id"]), "of": of.get(c["id"])}
        row = {"id": c["id"], "test": c["catala_test"], "year": c["year"], "stated": c["stated"], "got": {}, "raw": res}
        for w, r in res.items():
            fg = figures(w, r)
            got, verdict = {}, "equal"
            for k, v in c["stated"].items():
                x = fg.get(k)
                got[k] = x
                if x is None:
                    verdict = "n/c" if verdict == "equal" else verdict
                elif abs(x - v) > (0.01 if k == "NBPT" else 1.0):
                    verdict = "differ"
            if all(got[k] is None for k in c["stated"]):
                verdict = "n/c"
            row["got"][w] = {"figures": got, "verdict": verdict}
            score[w][{"equal": 0, "differ": 1}.get(verdict, 2)] += 1
        rows.append(row)
    json.dump({"rows": rows, "unmapped": UNMAPPED}, open(f"{outdir}/tests_results.json", "w"), ensure_ascii=False,
              indent=1)
    with open(f"{outdir}/tests_scoreboard.txt", "w") as f:
        f.write(f"{len(cases)} household tests mapped to boxes; {len(UNMAPPED)} not mappable: "
                + ", ".join(f"{k} ({v})" for k, v in UNMAPPED.items()) + "\n\n")
        f.write("program  equal  differ  not computed/out of scope (some figure)\n")
        for w, (e, d, n) in score.items():
            f.write(f"{w:7s} {e:6d} {d:7d} {n:6d}\n")
        f.write("\n")
        for r in rows:
            f.write(f"{r['id']:5s} {r['year']} stated {r['stated']}\n")
            for w, g in r["got"].items():
                f.write(f"      {w:7s} {g['verdict']:7s} {g['figures']}\n")
            cr = r["raw"]["catala"] or {}
            if "ERR" in cr or "IGNORED" in cr:
                f.write(f"      catala note: ERR={cr.get('ERR')} IGNORED={cr.get('IGNORED')}\n")
            mr = r["raw"]["m"] or {}
            if "_refused" in mr:
                f.write(f"      M refused: {mr['_refused']}\n")
            o = r["raw"]["of"] or {}
            if "skip" in o:
                f.write(f"      OpenFisca: unmapped boxes {o['skip']}\n")
    print(open(f"{outdir}/tests_scoreboard.txt").read())


if __name__ == "__main__":
    main()
