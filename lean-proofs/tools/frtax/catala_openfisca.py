"""OpenFisca-France on returns in the 2042 box format, for the Catala head-to-head.

usage: catala_openfisca.py cases.jsonl out.jsonl
Boxes are mapped through OpenFisca's own cerfa_field attributes, keeping only variables still defined in the
income year (end date) and boxes that map to exactly one such variable; family boxes are mapped by hand
(situation, children with their birth years, shared residence, disability, attached adult children, the
half-part ticks). A return with a box that maps to nothing (or to two variables) is not run: {"skip": [boxes]}.
Outputs: nbptr, rbg, rng, rni, rfr, revenu_categoriel_tspr, revenu_categoriel_non_salarial.
"""
import json, sys, time, collections, datetime
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

SIT = {"0AC": "celibataire", "0AM": "marie", "0AO": "pacse", "0AD": "divorce", "0AV": "veuf"}
TICKS = {"0BT": "caseT", "0AL": "caseL", "0AP": "caseP", "0AF": "caseF", "0AW": "caseW", "0AS": "caseS",
         "0AG": "caseG", "0AN": "caseN"}
FAMILY = set(SIT) | set(TICKS) | {"0DA", "0DB", "0CF", "0CH", "0CG", "0CI", "0DJ", "0CR"}
OUTS = ["nbptr", "rbg", "rng", "rni", "rfr", "revenu_categoriel_tspr", "revenu_categoriel_non_salarial"]

tbs = FranceTaxBenefitSystem()


def box_map(year):
    """box -> list of (variable, entity, person index or None, period unit)"""
    m = collections.defaultdict(list)
    lim = datetime.date(year, 12, 31)
    for name, v in tbs.variables.items():
        cf = getattr(v, "cerfa_field", None)
        if not cf or (v.end is not None and v.end < lim):
            continue
        items = cf.items() if isinstance(cf, dict) else [(None, cf)]
        for role, box in items:
            m[box].append((name, v.entity.key, role, str(v.definition_period)))
    return m


def build(cases, bmap):
    ind, foy, fam, men = {}, {}, {}, {}
    for c in cases:
        b, y, cid = c["boxes"], c["year"], c["id"]
        ys = str(y)
        sit = next((SIT[k] for k in SIT if k in b), "celibataire")
        couple = sit in ("marie", "pacse")
        people = [f"{cid}_d1"] + ([f"{cid}_d2"] if couple else [])
        ind[people[0]] = {"date_naissance": {ys: f"{b.get('0DA', y - 40)}-01-01"}, "statut_marital": {ys: sit}}
        if couple:
            ind[people[1]] = {"date_naissance": {ys: f"{b.get('0DB', y - 40)}-01-01"}, "statut_marital": {ys: sit}}
        kids = []
        for i in range(b.get("0CF", 0)):
            k = f"{cid}_f{i}"
            ind[k] = {"date_naissance": {ys: f"{b.get(f'0F{i}', y - 10)}-01-01"},
                      "invalidite": {f"{ys}-01": i < b.get("0CG", 0)}}
            kids.append(k)
        for i in range(b.get("0CH", 0)):
            k = f"{cid}_h{i}"
            ind[k] = {"date_naissance": {ys: f"{b.get(f'0H{i}', y - 10)}-01-01"}, "garde_alternee": {ys: True},
                      "invalidite": {f"{ys}-01": i < b.get("0CI", 0)}}
            kids.append(k)
        for i in range(b.get("0DJ", 0)):
            k = f"{cid}_j{i}"
            ind[k] = {"date_naissance": {ys: f"{b.get(f'0J{i}', y - 20)}-01-01"}}
            kids.append(k)
        for i in range(b.get("0CR", 0)):
            k = f"{cid}_r{i}"
            ind[k] = {"date_naissance": {ys: f"{y - 50}-01-01"}, "invalidite": {f"{ys}-01": True}}
            kids.append(k)
        allp = people + kids
        f = {"declarants": people, "personnes_a_charge": kids}
        for box, val in b.items():
            if box in FAMILY or box[:2] in ("0F", "0H", "0J"):
                continue
            (name, ent, role, unit), = bmap[box]
            if ent == "individu":
                if role is None or role >= len(allp):
                    continue
                # yearly amounts; monthly variables spread them over the months (set_input_divide_by_period)
                ind[allp[role]].setdefault(name, {})[ys] = val
            else:
                f[name] = {ys: val}
        for box, var in TICKS.items():
            if box in b:
                f[var] = {ys: True}
        foy[cid] = f
        fam[cid] = {"parents": people, "enfants": kids}
        men[cid] = {"personne_de_reference": people[:1], "conjoint": people[1:], "enfants": kids}
    return {"individus": ind, "foyers_fiscaux": foy, "familles": fam, "menages": men}


def main():
    cases = [json.loads(l) for l in open(sys.argv[1])]
    out = open(sys.argv[2], "w")
    for year in sorted({c["year"] for c in cases}):
        bmap = box_map(year)
        ok, n_skip = [], 0
        for c in (c for c in cases if c["year"] == year):
            bad = [k for k in c["boxes"] if not (k in FAMILY or k[:2] in ("0F", "0H", "0J")) and len(bmap.get(k, [])) != 1]
            if bad:
                out.write(json.dumps({"id": c["id"], "skip": bad}) + "\n")
                n_skip += 1
            else:
                ok.append(c)
        if not ok:
            continue
        t0 = time.time()
        sim = SimulationBuilder().build_from_entities(tbs, build(ok, bmap))
        res = {}
        for var in OUTS:
            try:
                res[var] = sim.calculate(var, str(year))
            except Exception as e:
                res[var] = None
                print("variable failed", var, repr(e)[:300], file=sys.stderr)
        dt = time.time() - t0
        for i, c in enumerate(ok):
            out.write(json.dumps({"id": c["id"], "of": {k: (float(v[i]) if v is not None else None)
                                                         for k, v in res.items()}}) + "\n")
        print(year, "run", len(ok), "skipped", n_skip, "%.2fs" % dt, file=sys.stderr)


if __name__ == "__main__":
    main()
