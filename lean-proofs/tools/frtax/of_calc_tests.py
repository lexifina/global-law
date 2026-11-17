"""Benchmark: OpenFisca-France's tests/calculateur_impots, whose expected values were read off the DGFiP's online
calculator for each year. Each test is converted to the boxes of form 2042 and run through Mlang (the M code of
that year, cal<year>) and the Lean model (years it covers). Scored against the calculator's values.

usage: of_calc_tests.py out.json
"""
import glob, json, os, re, subprocess, sys, tempfile, collections
import yaml

OF = os.path.expanduser("~/fr/refs/openfisca-france/tests/calculateur_impots/yaml")
LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")

PERSON_VARS = {  # OpenFisca individual variable -> box letter pattern (declarant 1, declarant 2, dependants)
    "salaire_imposable": ["1AJ", "1BJ", "1CJ", "1DJ", "1EJ", "1FJ"],
    "retraite_imposable": ["1AS", "1BS", "1CS", "1DS", "1ES", "1FS"],
    "chomage_imposable": ["1AP", "1BP", "1CP", "1DP", "1EP", "1FP"],
    "frais_reels": ["1AK", "1BK", "1CK", "1DK", "1EK", "1FK"],
    "pensions_alimentaires_percues": ["1AO", "1BO", "1CO", "1DO", "1EO", "1FO"],
    "pensions_invalidite": ["1AZ", "1BZ", "1CZ", "1DZ"],
    "hsup": ["1GH", "1HH", "1IH", "1JH"],
}
CASES = {"caseT": "0BT", "caseL": "0AL", "caseP": "0AP", "caseF": "0AF", "caseW": "0AW", "caseS": "0AS", "caseG": "0AG",
         "caseN": "0AN", "caseE": "0AE", "caseK": "0AK", "caseH": "0AH"}
COUNTS = {"nbF": "0CF", "nbG": "0CG", "nbH": "0CH", "nbI": "0CI", "nbJ": "0DJ", "nbN": "0DN", "nbR": "0CR"}
SIT = {"celibataire": "0AC", "marie": "0AM", "pacse": "0AO", "divorce": "0AD", "veuf": "0AV"}
OUT = {"nbptr": ("NBPT", "NBPT"), "rni": ("RNI", "RNI"), "rfr": ("REVKIRE", "REVKIRE"),
       "iai": ("IAN", "IAVCR"), "impot_revenu_restant_a_payer": ("IRN", "IMPNET")}
# boxes the Lean model reads (anything else makes the return out of its scope)
LEAN_BOXES = set("""0AC 0AM 0AO 0AD 0AV 0DA 0DB 0CF 0CG 0CH 0CI 0CR 0DJ 0DN 0BT 0AL 0AP 0AF 0AW 0AS 0AG
1AJ 1BJ 1CJ 1DJ 1EJ 1FJ 1AP 1BP 1CP 1DP 1EP 1FP 1AA 1BA 1CA 1DA 1GB 1HB 1IB 1JB 1AK 1BK 1CK 1DK 1EK 1FK 1GH 1HH 1IH 1JH 1KH 1LH
1AS 1BS 1CS 1DS 1ES 1FS 1AZ 1BZ 1CZ 1DZ 1AO 1BO 1CO 1DO 1EO 1FO 1AW 1BW 1CW 1DW
2DC 2TR 2TS 2FU 2CH 2OP 2CK 2BH 2CA 2AB 2CG 2DH 2UU 2VV 2WW 2ZZ 2YY 2EE 3VG 3VH 3VZ 4BE 4BA 4BB 4BC 4BD
5KO 5KP 5HQ 5LO 5LP 5IQ 5MO 5MP 5JQ 5ND 5OD 5PD 5KC 5LC 5MC 5QC 5RC 5SC 5HC 5IC 5JC 5TA 5TB 5TE 5UA 5UB 5UE 5VA 5VB 5VE
6DE 6EL 6EM 6GI 6GJ 6GU 6GP 6DD 6NS 6NT 6NU 6RS 6RT 6RU 6QR 7UF 7UD 7UQ 7VA 7VM 7UJ 7UO 7VC 7UH 7DB 7DR 7DQ 7DG 7DL
7GA 7GB 7GC 7GE 7GF 7GG 7EA 7EB 7EC 7ED 7EF 7EG 7CD 7CE 7AC 7AE 7AG 7XS 7XT 7XU 7XW 7XY
APS DPS CPS BPS APT DPT CPT BPT
1AD 1BD 1CD 1DD 1ED 1FD 1AV 1BV 1CV 1DV 1EV 1FV""".split())
def in_lean_scope(b):
    return all(k in LEAN_BOXES or re.fullmatch(r"0[FHJ]\d", k) for k in b)


def val(v):
    if isinstance(v, dict):
        v = next(iter(v.values()))
    if isinstance(v, bool):
        return 1 if v else 0
    try:
        return int(round(float(v)))
    except Exception:
        return None


def convert(t):
    year = int(t["period"])
    inp = t["input"]
    foy = inp.get("foyer_fiscal") or next(iter(inp.get("foyers_fiscaux", {}).values()), {})
    ind = inp.get("individus") or {}
    b, unknown = {}, []
    decl = foy.get("declarants", list(ind)[:1])
    pac = foy.get("personnes_a_charge", [])
    order = list(decl) + list(pac)
    sit = None
    for i, pid in enumerate(decl):
        person = ind.get(pid, {})
        sm = person.get("statut_marital")
        if isinstance(sm, dict):
            sm = next(iter(sm.values()))
        if i == 0:
            sit = SIT.get(sm, "0AC")
        dn = person.get("date_naissance")
        if isinstance(dn, dict):
            dn = next(iter(dn.values()))
        if dn:
            b["0DA" if i == 0 else "0DB"] = int(str(dn)[:4])
    b[sit or "0AC"] = 1
    births_f = []
    for pid in pac:
        dn = ind.get(pid, {}).get("date_naissance")
        if isinstance(dn, dict):
            dn = next(iter(dn.values()))
        births_f.append(int(str(dn)[:4]) if dn else year - 10)
    for pid, person in ind.items():
        idx = order.index(pid) if pid in order else None
        for k, v in person.items():
            if k in PERSON_VARS and idx is not None and idx < len(PERSON_VARS[k]):
                n = val(v)
                if n:
                    b[PERSON_VARS[k][idx]] = b.get(PERSON_VARS[k][idx], 0) + n
            elif k not in ("date_naissance", "statut_marital", "activite", "handicap", "garde_alternee", "invalide",
                           "age", "age_en_mois") and val(v):
                unknown.append(k)
    for k, v in foy.items():
        if k in ("declarants", "personnes_a_charge"):
            continue
        n = val(v)
        if k in CASES:
            if n:
                b[CASES[k]] = 1
        elif k in COUNTS:
            if n:
                b[COUNTS[k]] = n
        elif re.fullmatch(r"f\d[a-z]{2}(_\d{4})?", k):
            if n:
                b[k[1:4].upper()] = n
        elif n:
            unknown.append(k)
    nf = b.get("0CF", 0)
    for i in range(nf):
        b[f"0F{i}"] = births_f[i] if i < len(births_f) else year - 10
    for i in range(b.get("0CH", 0)):
        b[f"0H{i}"] = year - 8
    for i in range(b.get("0DJ", 0)):
        b[f"0J{i}"] = year - 20
    return year, b, unknown


def run_m(year, cases):
    cal = f"{BIN}/cal{year}"
    if not os.path.exists(cal):
        return {}
    d = tempfile.mkdtemp()
    os.makedirs(d + "/o")
    files = []
    for cid, boxes in cases:
        p = f"{d}/{cid}.irj"
        body = ["#NOM", cid, "#ENTREES-PRIMITIF", "REGCO/1"] + [f"{k}/{v}" for k, v in boxes.items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                 "#RESULTATS-CORRECTIF", "##"]
        open(p, "w").write("\n".join(body) + "\n")
        files.append(p)
    r = subprocess.run([cal, "-completion", "-m", "p", "-a", str(year), "-dst", d + "/o"] + files,
                       capture_output=True, text=True)
    rejected = dict(re.findall(r'traitement du fichier "([^"]+)\.irj"\n(?:[^\n]*\n)*?ATRT000 \| KO \| (\S+)', r.stdout))
    out = {}
    for cid, _ in cases:
        p = f"{d}/o/{cid}.irj"
        if os.path.exists(p):
            g = subprocess.run(["grep", "-E", "^(NBPT|RBG|RNI|REVKIRE|IAN|IRN|IINET)/", p], capture_output=True, text=True).stdout
            out[cid] = {l.split("/")[0]: float(l.split("/")[1]) for l in g.splitlines()}
        else:
            out[cid] = {"_rejected": rejected.get(cid, "rejected")}
    return out


def run_lean(year, cases):
    inp = "".join(f"{cid};{year};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n" for cid, b in cases)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        p = l.split(";")
        if p[0] != "ERR":
            out[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:]}
    return out


def main():
    tests = []
    for f in sorted(glob.glob(OF + "/*.yaml")):
        docs = yaml.safe_load(open(f))
        for i, t in enumerate(docs if isinstance(docs, list) else [docs]):
            if "input" not in t or "output" not in t:
                continue
            if "foyers_fiscaux" in t["input"] and len(t["input"]["foyers_fiscaux"]) > 1:
                continue
            year, boxes, unknown = convert(t)
            exp = {k: val(v) for k, v in t["output"].items() if k in OUT and val(v) is not None}
            tests.append(dict(id=f"{os.path.basename(f)[:-5]}_{i}", file=os.path.basename(f), name=t.get("name"),
                              year=year, boxes=boxes, unknown=unknown, expected=exp))
    byyear = collections.defaultdict(list)
    for t in tests:
        byyear[t["year"]].append(t)
    for year, ts in sorted(byyear.items()):
        cases = [(t["id"], t["boxes"]) for t in ts if not t["unknown"]]
        m = run_m(year, cases)
        l = run_lean(year, [c for c in cases if in_lean_scope(c[1])]) if year >= 2020 else {}
        for t in ts:
            t["m"] = m.get(t["id"])
            t["lean"] = l.get(t["id"])
    json.dump(tests, open(sys.argv[1], "w"), indent=1)
    # score: a test passes when every expected figure is within 1 euro
    def score(t, who):
        got = t.get(who)
        if not got or "_rejected" in got or (who == "m" and not got.get("NBPT")):
            return None
        for k, want in t["expected"].items():
            mk, lk = OUT[k]
            key = mk if who == "m" else lk
            if key is None:
                continue
            g = got.get(key)
            if k == "impot_revenu_restant_a_payer":
                want = -want
            if g is None or abs(g - want) > 1.01:
                return False
        return True
    tab = collections.defaultdict(collections.Counter)
    for t in tests:
        y = t["year"]
        tab[y]["tests"] += 1
        if t["unknown"]:
            tab[y]["unmappable"] += 1
            continue
        for who in ("m", "lean"):
            s = score(t, who)
            tab[y][f"{who}_" + ("n/a" if s is None else ("pass" if s else "fail"))] += 1
    for y in sorted(tab):
        print(y, dict(tab[y]))


if __name__ == "__main__":
    main()
