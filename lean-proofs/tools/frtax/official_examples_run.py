"""Official worked examples (parliamentary reports, BOFiP, brochure pratique, service-public): run those whose facts
map onto 2042 boxes through Lean and Mlang, and compare every stated figure that has an equivalent output.

usage: official_examples_run.py data/official_examples.jsonl out.json
"""
import json, os, re, subprocess, sys, tempfile
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from of_calc_tests import in_lean_scope

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")
# stated figure -> (Lean output, M variable)
MAP = {"impot_brut": ("IDRSCAP", "IDRS2"), "impot_apres_plafonnement": ("IDRS", "IDRS3"),
       "impot_brut_apres_plafonnement_qf_avant_decote": ("IDRS", "IDRS3"), "impot_taux_effectif": ("IDRSCAP", "IDRS2"),
       "decote": ("IDEC", "IDEC"), "impot_apres_decote": ("IDRS4", "IDRS4"),
       "reduction_dons": ("ITRED", "ITRED"), "reduction": ("ITRED", "ITRED"),
       "cehr": ("CHRAPRES", "CHRAPRES"), "cdhr": ("CDHR", "CDHR"), "parts": ("NBPT", "NBPT"),
       "rfr": ("REVKIRE", "REVKIRE"), "rref": ("REVKIRE", "REVKIRE"), "revenu_net_imposable": ("RNI", "RNI"),
       "impot_du": ("IAVCR", "IAN"), "impot_net": ("IAVCR", "IAN"),
       "impot_pfu": ("PFU", "IPROP"), "impot_pfu_dividendes": ("PFU", "IPROP"),
       "credit_cotisations_syndicales": ("CITOT", "IRE")}
MV = sorted({m for _, m in MAP.values()})

ex = [json.loads(l) for l in open(sys.argv[1])]
for e in ex:  # birth years M needs for children (the examples give none: a 10-year-old)
    b = e.get("boxes_guess")
    if b:
        for cnt, pre in (("0CF", "0F"), ("0CH", "0H"), ("0DJ", "0J")):
            for i in range(int(b.get(cnt, 0))):
                b.setdefault(f"{pre}{i}", e["income_year"] - (20 if cnt == "0DJ" else 10))
        for k in ("0DA", "0DB"):
            if k == "0DA" or "0AM" in b or "0AO" in b:
                b.setdefault(k, 1980)
run = [e for e in ex if e.get("boxes_guess") and e["income_year"] in range(2020, 2026)
       and any(k in MAP for k in e["expected"])]
# Lean
inp = "".join(f"{e['id']};{e['income_year']};" + ",".join(f"{k}={v}" for k, v in e["boxes_guess"].items()) + "\n"
              for e in run if in_lean_scope(e["boxes_guess"]))
lean = {}
for l in subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout.splitlines():
    p = l.split(";")
    lean[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
# M
m = {}
for e in run:
    d = tempfile.mkdtemp(); os.makedirs(d + "/o")
    y = e["income_year"]
    body = ["#NOM", "X", "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{y}"] + [f"{k}/{v}" for k, v in e["boxes_guess"].items()]
    body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
             "#RESULTATS-CORRECTIF", "##"]
    open(d + "/x.irj", "w").write("\n".join(body) + "\n")
    r = subprocess.run([f"{BIN}/cal{y}", "-completion", "-m", "p", "-a", str(y), "-dst", d + "/o", d + "/x.irj"],
                       capture_output=True, text=True)
    ko = re.search(r"KO \| (\S+)", r.stdout)
    if os.path.exists(d + "/o/x.irj") and not ko:
        vals = {}
        for line in open(d + "/o/x.irj"):
            k = line.split("/")[0]
            if k in MV and k not in vals:
                vals[k] = float(line.split("/")[1])
        m[e["id"]] = vals if vals.get("NBPT") else {"_refused": "no parts"}
    else:
        m[e["id"]] = {"_refused": ko.group(1) if ko else "?"}
res = []
tot = {"Lean": [0, 0], "M": [0, 0]}
for e in run:
    row = {"id": e["id"], "year": e["income_year"], "flags": e.get("flags"), "figures": {}}
    for k, want in e["expected"].items():
        if k not in MAP or not isinstance(want, (int, float)):
            continue
        lk, mk = MAP[k]
        lv = lean.get(e["id"], {}).get(lk)
        mv = m[e["id"]].get(mk)
        row["figures"][k] = {"stated": want, "Lean": lv, "M": mv}
        for who, v in (("Lean", lv), ("M", mv)):
            if v is not None:
                tot[who][1] += 1
                tot[who][0] += abs(v - want) <= 0.5
    row["m_refused"] = m[e["id"]].get("_refused")
    row["lean_scope"] = e["id"] in lean
    res.append(row)
json.dump(res, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
print(f"examples with mappable boxes and figures: {len(run)} of {len(ex)}; in Lean's scope {len(lean)}; "
      f"M refused {sum(1 for r in res if r['m_refused'])}")
for who, (ok, n) in tot.items():
    print(f"  {who}: {ok}/{n} stated figures reproduced")
for r in res:
    bad = {k: v for k, v in r["figures"].items()
           if any(v[w] is not None and abs(v[w] - v["stated"]) > 0.5 for w in ("Lean", "M"))}
    if bad or r["m_refused"]:
        print("  ", r["id"], r["year"], "M refused " + r["m_refused"] if r["m_refused"] else "", bad, r["flags"] or "")
