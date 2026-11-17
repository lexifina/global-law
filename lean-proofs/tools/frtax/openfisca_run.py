"""Third implementation: OpenFisca-France on the same returns, compared with M (cal) like the Lean model.

usage: openfisca_run.py cases.jsonl workdir_with_m.jsonl out.json [n]
Only returns whose boxes all map onto OpenFisca inputs are used (see MAP); the others are skipped and counted.
"""
import json, sys, collections, time
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

PERSON = {  # box -> (person index: 0 declarant 1, 1 declarant 2, 2.. dependants, variable)
    "1AJ": (0, "salaire_imposable"), "1BJ": (1, "salaire_imposable"), "1CJ": (2, "salaire_imposable"), "1DJ": (3, "salaire_imposable"),
    "1AK": (0, "frais_reels"), "1BK": (1, "frais_reels"),
    "1AP": (0, "chomage_imposable"), "1BP": (1, "chomage_imposable"),
    "1AS": (0, "retraite_imposable"), "1BS": (1, "retraite_imposable"),
    "1AZ": (0, "pensions_invalidite"), "1BZ": (1, "pensions_invalidite"),
    "1AO": (0, "pensions_alimentaires_percues"), "1BO": (1, "pensions_alimentaires_percues"),
    "1GH": (0, "hsup"), "1HH": (1, "hsup"),
    "7AC": (0, "f7ac"), "7AE": (1, "f7ac"),
}
FOYER = {b: "f" + b.lower() for b in """2DC 2TR 2TS 2CK 2BH 2CA 2CH 3VG 3VH 4BE 4BA 4BB 4BC 4BD 6DE 6GU 6EL
    7UF 7UD 7DB 7DR 7GA 7GB 7GC 7GE 7GF 7GG 7EA 7EB 7EC 7ED 7EF 7EG 7CD""".split()}
BOOL = {"2OP": "f2op", "7DQ": "f7dq", "0BT": "caseT", "0AL": "caseL", "0AP": "caseP", "0AF": "caseF"}
SIT = {"0AC": "celibataire", "0AM": "marie", "0AO": "pacse", "0AD": "divorce", "0AV": "veuf"}
IGNORE = {"0DA", "0DB", "0CF", "0CH", "0CG", "0CI"} | {f"0F{i}" for i in range(8)} | {f"0H{i}" for i in range(6)}


def usable(boxes):
    return all(b in PERSON or b in FOYER or b in BOOL or b in SIT or b in IGNORE for b in boxes) and "0CG" not in boxes and "0CI" not in boxes


def build(cases):
    ind, foy, fam, men = {}, {}, {}, {}
    for c in cases:
        b, y, cid = c["boxes"], c["year"], c["id"]
        sit = next(SIT[k] for k in SIT if k in b)
        couple = sit in ("marie", "pacse")
        people = [f"{cid}_d1"] + ([f"{cid}_d2"] if couple else [])
        ind[people[0]] = {"date_naissance": {str(y): f"{b['0DA']}-01-01"}, "statut_marital": {str(y): sit}}
        if couple:
            ind[people[1]] = {"date_naissance": {str(y): f"{b['0DB']}-01-01"}, "statut_marital": {str(y): sit}}
        kids = []
        for i in range(b.get("0CF", 0)):
            k = f"{cid}_f{i}"
            ind[k] = {"date_naissance": {str(y): f"{b[f'0F{i}']}-01-01"}}
            kids.append(k)
        for i in range(b.get("0CH", 0)):
            k = f"{cid}_h{i}"
            ind[k] = {"date_naissance": {str(y): f"{b[f'0H{i}']}-01-01"}, "garde_alternee": {str(y): True}}
            kids.append(k)
        allp = people + kids
        for box, (pi, var) in PERSON.items():
            if box in b and pi < len(allp):
                ind[allp[pi]].setdefault(var, {})[str(y)] = b[box]
        f = {"declarants": people, "personnes_a_charge": kids}
        for box, var in FOYER.items():
            if box in b:
                f[var] = {str(y): b[box]}
        for box, var in BOOL.items():
            if box in b:
                f[var] = {str(y): True}
        foy[cid] = f
        fam[cid] = {"parents": people, "enfants": kids}
        men[cid] = {"personne_de_reference": people[:1], "conjoint": people[1:], "enfants": kids}
    return {"individus": ind, "foyers_fiscaux": foy, "familles": fam, "menages": men}


def main():
    cases = [json.loads(l) for l in open(sys.argv[1])]
    m = {}
    for l in open(sys.argv[2] + "/m.jsonl"):
        d = json.loads(l)
        m[d["id"]] = d
    lean = {}
    for l in open(sys.argv[2] + "/lean.jsonl"):
        d = json.loads(l)
        lean[d["id"]] = d
    n = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 3000
    allc = "--all" in sys.argv  # also the returns M refused (to put before another arbiter)
    pool = [c for c in cases if (allc or c["id"] in m) and usable(c["boxes"])]
    skipped = sum(1 for c in cases if allc or c["id"] in m) - len(pool)
    tbs = FranceTaxBenefitSystem()
    out = {"pool": len(pool), "skipped_unmappable": skipped, "years": {}}
    for year in sorted({c["year"] for c in pool}):
        sel = [c for c in pool if c["year"] == year][:n]
        t0 = time.time()
        sim = SimulationBuilder().build_from_entities(tbs, build(sel))
        res = {}
        for var in ("nbptr", "rng", "rni", "rfr", "decote", "impot_revenu_restant_a_payer", "ip_net",
                    "contribution_exceptionnelle_hauts_revenus", "contribution_differentielle_hauts_revenus"):
            try:
                res[var] = sim.calculate(var, str(year))
            except Exception as e:
                res[var] = None
                print("variable failed", var, repr(e)[:200])
        dt = time.time() - t0
        stats = collections.Counter()
        rows = []
        for i, c in enumerate(sel):
            mv, lv = m.get(c["id"], {}), lean.get(c["id"], {})
            of = {k: (float(v[i]) if v is not None else None) for k, v in res.items()}
            # OpenFisca's amount left to pay includes the CEHR and the CDHR, which M's IRN does not: take them out
            # OpenFisca's amount left to pay includes the CEHR (which M's IRN does not) but not the CDHR, which it
            # reports on its own as a negative amount
            of_irn = (-of["impot_revenu_restant_a_payer"] - (of["contribution_exceptionnelle_hauts_revenus"] or 0)
                      ) if of["impot_revenu_restant_a_payer"] is not None else None
            checks = {"NBPT": (of["nbptr"], mv.get("NBPT"), lv.get("NBPT")),
                      "RNG": (of["rng"], mv.get("RNG"), lv.get("RNG")),
                      "RNI": (of["rni"], mv.get("RNI"), lv.get("RNI")),
                      "REVKIRE": (of["rfr"], mv.get("REVKIRE"), lv.get("REVKIRE")),
                      "IRN": (of_irn, mv.get("IRN"), lv.get("IMPNET"))}
            allof = alllean = True
            for k, (o, mm, ll) in checks.items():
                okof = o is not None and mm is not None and abs(o - mm) < 0.5
                okl = ll is not None and mm is not None and abs(ll - mm) < 0.5
                stats["of_" + k] += okof
                stats["lean_" + k] += okl
                allof &= okof
                alllean &= okl
            stats["of_all"] += allof
            stats["lean_all"] += alllean
            rows.append({"id": c["id"], "checks": checks, "of": of, "of_irn": of_irn})
        out["years"][year] = {"n": len(sel), "seconds_openfisca": dt, "stats": dict(stats), "rows": rows}
        print(year, "n", len(sel), "openfisca %.1fs" % dt, {k: v for k, v in sorted(stats.items())})
    json.dump(out, open(sys.argv[3], "w"))


if __name__ == "__main__":
    main()
