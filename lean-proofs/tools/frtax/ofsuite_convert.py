"""Step 2: convert OpenFisca-France YAML tests with income-tax outputs into form-2042 boxes plus expected outputs.

The test's own input is loaded into an OpenFisca simulation (as OpenFisca's test runner does), and the boxes are
read back from it: every variable carrying a box (cerfa_field) for the income year, the family-situation boxes
(statut_marital, caseT..., nbF/nbG/nbH/nbI/nbJ/nbR/nbN as OpenFisca derives them from the persons) and the birth
years. So a test written with bare boxes (f4ba, salaire_imposable, ...) gives exactly those boxes, and a test
written with gross pay (salaire_de_base ...) gives the boxes OpenFisca derives from it ("derived" tier).

A test is skipped, with a reason, when it uses a reform or parameter override, has several tax households, sets an
intermediate income-tax variable (one computed from boxes: rfr, rni, nbptr, ...), or has no expected output that
M or Lean compute. The boxes are then checked against the aliases of that year's M source.

usage: ofsuite_convert.py years(e.g. 2019-2025) cases.jsonl skipped.json > report.txt
"""
import collections, datetime, glob, json, os, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ofsuite_load import load_all, output_vars, input_vars, walk_entities, annual

from openfisca_france import FranceTaxBenefitSystem
from openfisca_core.simulations import SimulationBuilder
TBS = FranceTaxBenefitSystem()

# expected output -> (M variable, Lean output or callable, how to compare)
# sign: "neg" = OpenFisca's value is minus the tax (restant à payer > 0 is a refund); "abs" = OpenFisca stores
# a levy as a negative amount; "pct" = OpenFisca gives a rate as a fraction, M as a percentage
OUT = {
    "nbptr": ("NBPT", "NBPT", None),
    "rni": ("RNI", "RNI", None),
    "rbg": ("RBG1", None, None),
    "rfr": ("REVKIRE", "REVKIRE", None),
    "ir_plaf_qf": ("IDRS3", "IDRS", None),
    "decote_gain_fiscal": ("IDEC", "IDEC", None),
    "ip_net": ("IDRS4", "IDRS4", None),
    "iaidrdi": ("IAD11", "IAIDRDI", None),
    "reductions": ("ITRED", "ITRED", None),
    "iai": ("IAN", "IAVCR", None),
    "impot_revenu_restant_a_payer": ("IRN", "IMPNET", "neg"),
    "contribution_exceptionnelle_hauts_revenus": ("CHRAPRES", "CHRAPRES", "abs"),
    "prelevement_forfaitaire_unique_ir": ("IPROP", "PFU", "abs"),
    "ir_taux_marginal": ("TXMARJ", None, "pct"),
}
# boxes by person (declarant 1, declarant 2, dependants) where OpenFisca's cerfa_field is missing or out of date
PERSON_OVERRIDE = {"hsup": ["1GH", "1HH", "1IH", "1JH"],
                   # exceptional value-sharing bonus (loi 2022-1158 art. 1): exempt part in 1AD.. (in the RFR)
                   "prime_partage_valeur_exoneree_exceptionnelle": ["1AD", "1BD", "1CD", "1DD"]}
CASES = {"caseT": "0BT", "caseL": "0AL", "caseP": "0AP", "caseF": "0AF", "caseW": "0AW", "caseS": "0AS",
         "caseG": "0AG", "caseN": "0AN", "caseE": "0AE", "caseK": "0AK", "caseH": "0AH"}
COUNTS = {"nbF": "0CF", "nbG": "0CG", "nbH": "0CH", "nbI": "0CI", "nbJ": "0DJ", "nbN": "0DN", "nbR": "0CR"}
SIT = {"celibataire": "0AC", "marie": "0AM", "pacse": "0AO", "divorce": "0AD", "veuf": "0AV", "jeune_veuf": "0AV"}
IR_MODULES = {"ir", "ir_prelevement_forfaitaire_unique", "credits_impot", "reductions_impot_plafonnees",
              "reductions_impot_deplafonnees", "reductions_impot_iom", "contribution_differentielle_hauts_revenus",
              "prelevement_forfaitaire_liberatoire", "charges_deductibles", "plus_value", "foncier",
              "variables_reductions_credits", "plus_values_immobilieres"}
# inputs that describe the person or the household and that OpenFisca turns into boxes itself
SITUATION = {"date_naissance", "age", "age_en_mois", "statut_marital", "invalidite", "handicap", "garde_alternee",
             "taux_incapacite", "enceinte", "rempli_obligation_scolaire", "en_couple", "activite",
             "maries_ou_pacses", "celibataire_ou_divorce", "veuf", "jeune_veuf"}
# gross-pay inputs: OpenFisca derives the taxable amounts (boxes) from them
GROSS = {"salaire_de_base", "retraite_brute", "chomage_brut", "traitement_indiciaire_brut", "primes_fonction_publique",
         "primes_salaires", "prime_partage_valeur", "prime_partage_valeur_exceptionnelle",
         "prime_exceptionnelle_pouvoir_achat", "allocation_retour_emploi", "heures_remunerees_volume",
         "contrat_de_travail", "contrat_de_travail_type", "categorie_salarie", "effectif_entreprise",
         "accord_interessement", "depcom_entreprise", "regime_securite_sociale", "secteur_activite_employeur",
         "taches_salarie_type", "contrat_duree_determinee_type", "exposition_accident", "ratio_alternants",
         "choix_exoneration_cotisations_employeur_agricole", "allegement_cotisation_maladie_mode_recouvrement",
         "allegement_cotisation_allocations_familiales_mode_recouvrement", "allegement_general_mode_recouvrement"}
# inputs that only feed housing, benefits or local taxes (not income tax)
NOT_IR = {"depcom", "loyer", "statut_occupation_logement", "ass_precondition_remplie", "autonomie_financiere",
          "valeur_locative_cadastrale_brute", "rsa_jeune_condition_heures_travail_remplie", "ass_mat", "empl_dir",
          "gar_dom", "part_meubles_tourisme_classes", "part_bnc_non_cipav", "b1ab"}


def module(v):
    return type(v).__module__.rsplit(".", 1)[-1].split("_", 2)[-1]


def m_aliases(year):
    srcs = sorted(glob.glob(os.path.expanduser(f"~/fr/mlang/ir-calcul/sources{year}m_*")))
    al = set()
    for f in glob.glob(srcs[-1] + "/tgv*.m"):
        al |= set(re.findall(r"\balias\s+(\w+)\s*:", open(f, encoding="latin-1").read()))
    return al


BOXVARS = []  # (name, entity, cerfa, period)
for n, v in TBS.variables.items():
    cf = getattr(v, "cerfa_field", None)
    if n in PERSON_OVERRIDE:
        cf = {i: b for i, b in enumerate(PERSON_OVERRIDE[n])}
    # ppe_*: the employment bonus (prime pour l'emploi, ended with income 2015) keeps cerfa codes that later forms
    # reuse: ppe_du_sa (hours paid, computed for every employee) is tagged 1AV, the 2022+ value-sharing-bonus tick
    if cf and n not in CASES and n not in COUNTS and not n.startswith("ppe_"):
        BOXVARS.append((n, v.entity.key, cf, v.definition_period))


def box_code(name, cf, aliases):
    """The M alias for an OpenFisca box variable: its cerfa_field when M knows it, else the code in its name
    (f7uf -> 7UF, f7xx_2020 -> 7XX)."""
    if cf in aliases:
        return cf
    m = re.fullmatch(r"f(\d[a-z]{2})(_\d{4})?", name)
    if m and m.group(1).upper() in aliases:
        return m.group(1).upper()
    if re.fullmatch(r"[A-Z]{2}", str(cf)) and m and (m.group(1)[0] + cf) in aliases:
        return m.group(1)[0] + cf
    return None


def num(x):
    if hasattr(x, "item"):
        x = x.item()
    if isinstance(x, bool):
        return 1 if x else 0
    return x


def expected_values(t, year, g, fids):
    """Expected outputs for tax household number g (ids fids): a list gives one value per household, an entity
    block names the household; a scalar applies to every household (as OpenFisca's test runner compares it)."""
    exp, notes = {}, []
    for name, ent, gid, raw in output_vars(t["output"]):
        if name not in OUT:
            continue
        if gid is not None and gid != "_g0" and gid != fids[g]:
            continue
        v, note = annual(raw, year)
        if isinstance(v, list):
            if len(v) == len(fids):
                v = v[g]
            elif len(v) == 1:
                v = v[0]
            else:
                notes.append(f"{name}: {len(v)} values for {len(fids)} households")
                continue
        if v is None or isinstance(v, (str, dict)):
            notes.append(f"{name}: {note or 'not a number'}")
            continue
        exp[name] = float(v)
    return exp, notes


def classify_inputs(t):
    """-> (reason or None, tier, unmapped list)"""
    tier = "box"
    unmapped = []
    for name, ent, gid, raw in input_vars(t["input"]):
        v = TBS.variables.get(name)
        if v is None:
            return f"unknown variable {name}", tier, unmapped
        if getattr(v, "cerfa_field", None) or name in PERSON_OVERRIDE or name in SITUATION:
            continue
        if name in GROSS:
            tier = "derived"
            continue
        if name in NOT_IR:
            continue
        if name == "depcom_foyer":
            vals = raw.values() if isinstance(raw, dict) else [raw]
            if any(str(x).startswith("97") for x in vals):
                unmapped.append("depcom_foyer (overseas)")
            continue
        if v.formulas and module(v) in IR_MODULES:
            return f"sets intermediate IR variable {name}", tier, unmapped
        if v.formulas:
            unmapped.append(f"{name} (computed variable set as input)")
        else:
            unmapped.append(name)
    return None, tier, unmapped


def build_sim(t):
    """The simulation as OpenFisca's test runner leaves it: built from the input, then every expected output
    computed in the order the YAML lists them. The order matters: tests whose CSG rate depends on the RFR (a
    cycle cut by max_spiral_loops) get a different taxable pension when the RFR is asked for first (e.g.
    leximpact/2024/celibataire_retraite_1.2_SMIC_d4: 1AS 25 444 asked first, 24 375 in the runner's order)."""
    b = SimulationBuilder()
    b.set_default_period(t["period"])
    sim = b.build_from_dict(TBS, t["input"])
    if t.get("max_spiral_loops"):
        sim.max_spiral_loops = t["max_spiral_loops"]
    for name, ent, gid, raw in output_vars(t["output"]):
        if name not in TBS.variables:
            continue
        periods = [str(k) for k in raw] if isinstance(raw, dict) else [str(t["period"])]
        for per in periods:
            try:
                sim.calculate(name, per)
            except Exception:
                pass
    return sim


def derive_boxes(sim, t, year, aliases, g):
    """Read back the boxes of tax household number g from OpenFisca's simulation of the test."""
    ff = sim.populations["foyer_fiscal"]
    persons = sim.populations["individu"]
    roles = [r.key for r in ff.members_role]
    pos = list(ff.members_position)
    mine = [i for i in range(persons.count) if int(ff.members_entity_id[i]) == g]
    # box columns: declarant principal 0, conjoint 1, dependants 2, 3, ... (by position)
    decl = [i for i in mine if roles[i] == "declarant_principal"]
    conj = [i for i in mine if roles[i] == "conjoint"]
    pac = sorted([i for i in mine if roles[i] == "personne_a_charge"], key=lambda i: pos[i])
    if len(decl) != 1 or len(conj) > 1:
        return None, f"declarants not resolved ({roles})", None
    order = decl + conj + pac
    idx_of = {decl[0]: 0}
    if conj:
        idx_of[conj[0]] = 1
    idx_of.update({p: k + 2 for k, p in enumerate(pac)})
    boxes, problems = {}, []
    y = str(year)
    for name, ent, cf, per in BOXVARS:
        try:
            if per.name == "MONTH" or str(per) == "month":
                vals = sim.calculate_add(name, y)
            elif str(per).lower().endswith("year"):
                vals = sim.calculate(name, y)
            else:
                continue
        except Exception as e:
            continue
        dv = num(TBS.variables[name].default_value)
        dflt = {0, dv, dv * 12} if isinstance(dv, (int, float)) else {0}
        if ent == "foyer_fiscal":
            x = num(vals[g])
            if x not in dflt:
                code = box_code(name, cf if isinstance(cf, str) else None, aliases)
                if code is None:
                    problems.append(f"{name}={x} (" + ("computed, ignored" if TBS.variables[name].formulas else f"no {year} M box for {cf}") + ")")
                else:
                    boxes[code] = boxes.get(code, 0) + x
        else:
            for p in mine:
                x = num(vals[p])
                if x in dflt:
                    continue
                k = idx_of.get(p)
                cfd = cf if isinstance(cf, dict) else {}
                code = cfd.get(k) if k is not None else None
                if code and code not in aliases:
                    code = None
                if code is None:
                    problems.append(f"{name}[{k}]={x} (" + ("computed, ignored" if TBS.variables[name].formulas else "no box") + ")")
                else:
                    boxes[code] = boxes.get(code, 0) + x
    # 1AD above 3 000 €: the employer has a profit-sharing agreement (1AV ticked) for the 6 000 € limit
    try:
        ai = sim.calculate("accord_interessement", f"{y}-01")
        for p in mine:
            k = idx_of.get(p)
            if k is not None and k < 4 and boxes.get("1" + "ABCD"[k] + "D", 0) > 3000 and ai[p]:
                boxes["1" + "ABCD"[k] + "V"] = 1
    except Exception:
        pass
    # family situation, as OpenFisca's income tax reads it (these flags may be set directly by a test)
    sm = sim.calculate("statut_marital", f"{y}-01")
    sm_name = sm.decode_to_str()[order[0]] if hasattr(sm, "decode_to_str") else str(sm[order[0]])
    flags = {n: bool(num(sim.calculate(n, y)[g])) for n in ("maries_ou_pacses", "celibataire_ou_divorce", "veuf", "jeune_veuf")}
    if flags["maries_ou_pacses"]:
        sit = "0AO" if sm_name == "pacse" else "0AM"
    elif flags["veuf"] or flags["jeune_veuf"]:
        sit = "0AV"
    elif flags["celibataire_ou_divorce"]:
        sit = "0AD" if sm_name == "divorce" else "0AC"
    else:
        sit = SIT.get(sm_name, "0AC")
        problems.append(f"no situation flag set (statut_marital {sm_name})")
    boxes[sit] = 1
    if flags["jeune_veuf"]:
        problems.append("jeune_veuf read as 0AV")
    for n, code in CASES.items():
        if n not in TBS.variables:
            continue
        if num(sim.calculate(n, y)[g]):
            boxes[code] = 1
    for n, code in COUNTS.items():
        x = num(sim.calculate(n, y)[g])
        if x:
            boxes[code] = int(x)
    # birth years: "age" in the input -> year - age (the age OpenFisca uses = the age the statute counts on
    # 31 December only for someone born on 1 January; this makes both conditions agree); else date_naissance
    given_age = {}
    persons_in, _, flat = walk_entities(t["input"])
    ids = list(persons.ids)
    if flat:
        if "age" in t["input"]:
            a, _ = annual(t["input"]["age"], year)
            given_age[0] = a
    else:
        for pid, d in persons_in.items():
            if "age" in d and pid in ids:
                a, _ = annual(d["age"], year)
                if isinstance(a, (int, float)):
                    given_age[ids.index(pid)] = a
    dn = sim.calculate("date_naissance", y)
    def birth(p):
        if p in given_age and given_age[p] is not None:
            return int(year - given_age[p])
        return int(str(dn[p])[:4])
    boxes["0DA"] = birth(order[0])
    if conj:
        boxes["0DB"] = birth(order[1])
    elif sit in ("0AM", "0AO"):
        boxes["0DB"] = 1970  # a couple flag with one person in the test: OpenFisca's default birth date
        problems.append("couple flag with one person: 0DB 1970")
    # dependants: alternating custody -> 0H, adults attached (0DJ) -> 0J, the others -> 0F
    ga = sim.calculate("garde_alternee", f"{y}-01") if "garde_alternee" in TBS.variables else None
    lists = {"F": [], "H": [], "J": []}
    for p in pac:
        by = birth(p)
        if ga is not None and ga[p]:
            lists["H"].append(by)
        elif year - by >= 18 and boxes.get("0DJ"):
            lists["J"].append(by)
        else:
            lists["F"].append(by)
    for letter, cnt, dflt in (("F", "0CF", 10), ("H", "0CH", 8), ("J", "0DJ", 20)):
        n = boxes.get(cnt, 0)
        ls = sorted(lists[letter])
        if len(ls) != n:
            problems.append(f"{cnt}={n} but {len(ls)} dependants of that kind")
        for i in range(n):
            boxes[f"0{letter}{i}"] = ls[i] if i < len(ls) else year - dflt
    for k, v in list(boxes.items()):
        if isinstance(v, float):
            boxes[k] = int(round(v))
    return boxes, None, problems


def of_values(sim, exp, year, g):
    out = {}
    for name in exp:
        try:
            out[name] = float(sim.calculate(name, str(year))[g])
        except Exception as e:
            out[name] = None
    return out


def main():
    y0, y1 = map(int, sys.argv[1].split("-"))
    recs = [r for r in load_all() if "load_error" not in r and r["year"] and y0 <= r["year"] <= y1]
    aliases = {y: m_aliases(y) for y in range(y0, y1 + 1)}
    cases, skipped = [], []
    reasons = collections.Counter()
    unm = collections.Counter()
    unm_tests = collections.Counter()
    for t in recs:
        year = t["year"]
        outs = {o[0] for o in output_vars(t["output"])}
        rec = {"id": t["id"], "file": t["file"], "name": t["name"], "year": year}
        def skip(reason, **kw):
            reasons[reason.split(":")[0] if reason.startswith("sets") is False else reason] += 1
            skipped.append(dict(rec, reason=reason, outputs=sorted(outs), **kw))
        if not outs & set(OUT):
            continue  # not an income-tax test M or Lean can score (counted by the inventory)
        if t["reforms"] or t["extensions"]:
            skip("uses a reform or extension")
            continue
        raw = yaml_keys = None
        reason, tier, unmapped = classify_inputs(t)
        if reason:
            skip(reason)
            continue
        if unmapped:
            for u in set(unmapped):
                unm[u] += 1
            unm_tests[tuple(sorted(set(unmapped)))] += 1
            skip("input with no box: " + ", ".join(sorted(set(unmapped))), unmapped=sorted(set(unmapped)))
            continue
        try:
            sim = build_sim(t)
        except Exception as e:
            skip(f"OpenFisca cannot build the test: {repr(e)[:120]}")
            continue
        fids = [str(x) for x in sim.populations["foyer_fiscal"].ids]
        for g in range(len(fids)):
            sub = dict(rec, id=t["id"] + (f"/{fids[g]}" if len(fids) > 1 else ""), households=len(fids))
            def skip_g(reason, **kw):
                skipped.append(dict(sub, reason=reason, outputs=sorted(outs), **kw))
            try:
                boxes, why, problems = derive_boxes(sim, t, year, aliases[year], g)
            except Exception as e:
                skip_g(f"OpenFisca cannot build the test: {repr(e)[:120]}")
                continue
            if why:
                skip_g(why)
                continue
            hard = [p for p in problems if "no box" in p or ("M box" in p and "ignored" not in p)]
            if hard:
                for p in hard:
                    unm[p.split("=")[0].split("[")[0] + " (no M box that year)"] += 1
                skip_g("box OpenFisca sets has no M box: " + "; ".join(hard), unmapped=hard)
                continue
            exp, notes = expected_values(t, year, g, fids)
            if not exp:
                skip_g("expected values unusable: " + "; ".join(notes))
                continue
            ofv = of_values(sim, exp, year, g)
            cases.append(dict(sub, tier=tier, boxes=boxes, expected=exp, of=ofv, notes=problems + notes,
                              margin=t["margin"]))
    with open(sys.argv[2], "w") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    json.dump(skipped, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
    print(f"tests {y0}-{y1} with an output M or Lean computes: {len(cases) + len(skipped)}")
    print(f"  converted: {len(cases)}  (tier box {sum(c['tier'] == 'box' for c in cases)}, "
          f"derived from gross pay {sum(c['tier'] == 'derived' for c in cases)})")
    print(f"  skipped: {len(skipped)}")
    rs = collections.Counter()
    for s in skipped:
        r = s["reason"]
        r = re.sub(r"input with no box: .*", "input with no box", r)
        r = re.sub(r"box OpenFisca sets has no M box: .*", "box OpenFisca sets has no M box that year", r)
        rs[r] += 1
    for k, v in rs.most_common():
        print(f"    {v:4d} {k}")
    print("  unmapped inputs (tests they would bring in):")
    for k, v in unm.most_common():
        print(f"    {v:4d} {k}")
    by = collections.Counter((c["year"], c["file"].split("/")[0]) for c in cases)
    print("  converted by year/directory:", sorted(by.items()))


if __name__ == "__main__":
    main()
