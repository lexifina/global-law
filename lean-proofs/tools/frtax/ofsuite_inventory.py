"""Step 1: inventory of OpenFisca-France's YAML tests: income years, and the income-tax (IR) ones by output variable
and year. An output is IR-relevant when its variable is defined in an income-tax module of openfisca_france
(prelevements_obligatoires/impot_revenu/**) or carries a box (cerfa_field).

usage: ofsuite_inventory.py out.json > report.txt
"""
import collections, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ofsuite_load import load_all, output_vars, input_vars

from openfisca_france import FranceTaxBenefitSystem
TBS = FranceTaxBenefitSystem()
IR_MODULES = {"ir", "ir_prelevement_forfaitaire_unique", "credits_impot", "reductions_impot_plafonnees",
              "reductions_impot_deplafonnees", "reductions_impot_iom", "contribution_differentielle_hauts_revenus",
              "prelevement_forfaitaire_liberatoire", "charges_deductibles", "plus_value", "variables_reductions_credits",
              "foncier", "plus_values_immobilieres"}
EXTRA_IR = {"impots_directs"}  # household aggregate whose largest part is the income tax


def module(v):
    return type(v).__module__.rsplit(".", 1)[-1].split("_", 2)[-1]


def is_ir(name):
    v = TBS.variables.get(name)
    if v is None:
        return False
    return module(v) in IR_MODULES or bool(getattr(v, "cerfa_field", None)) or name in EXTRA_IR


def main():
    recs = load_all()
    byyear = collections.Counter()
    ir_byyear = collections.Counter()
    ir_var_year = collections.defaultdict(collections.Counter)
    ir_dir = collections.Counter()
    unknown_out = collections.Counter()
    rows = []
    for r in recs:
        if "load_error" in r:
            byyear["load error"] += 1
            continue
        y = r["year"]
        byyear[y] += 1
        outs = output_vars(r["output"])
        names = [o[0] for o in outs]
        for n in names:
            if n not in TBS.variables:
                unknown_out[n] += 1
        irs = sorted({n for n in names if is_ir(n)})
        r["ir_outputs"] = irs
        if irs:
            ir_byyear[y] += 1
            top = r["file"].split("/")[0] if "/" in r["file"] else "(root)"
            if r["file"].startswith("formulas/"):
                top = "formulas/" + r["file"].split("/")[1] if r["file"].count("/") > 1 else "formulas"
            if 2020 <= (y or 0) <= 2025:
                ir_dir[top] += 1
                for n in irs:
                    ir_var_year[n][y] += 1
        rows.append({k: r[k] for k in ("id", "year", "ir_outputs", "reforms")})
    json.dump(rows, open(sys.argv[1], "w"), indent=0)
    print("tests by income year (all):", sorted(byyear.items(), key=lambda kv: str(kv[0])))
    print("IR tests by income year:", sorted(ir_byyear.items(), key=lambda kv: str(kv[0])))
    print("IR tests 2020-2025:", sum(v for k, v in ir_byyear.items() if isinstance(k, int) and 2020 <= k <= 2025))
    print("IR tests 2020-2025 by directory:")
    for k, v in ir_dir.most_common():
        print(f"  {v:5d} {k}")
    print("IR output variables 2020-2025 (tests per year):")
    for n, c in sorted(ir_var_year.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {sum(c.values()):5d} {n:50s} " + " ".join(f"{y}:{c[y]}" for y in sorted(c)))
    print("output variables unknown to the tax-benefit system:", unknown_out.most_common(20))


if __name__ == "__main__":
    main()
