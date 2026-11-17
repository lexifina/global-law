"""Which 2042 boxes does the Lean model read? For every box code in the DGFiP 2042-nat dataset, add it to a few
base households and see whether any Lean output changes. usage: pop_boxprobe.py year out.json"""
import csv, json, subprocess, sys, os
LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
year = int(sys.argv[1]); out = sys.argv[2]
rows = [r for r in csv.DictReader(open(os.path.expanduser("~/fr/data/pop/raw/ir-declarations-2042-nat.csv"), encoding="utf-8-sig"), delimiter=";") if r["annee"] == str(year)]
y = year
bases = [
    {"0AC": 1, "0DA": y - 44, "1AJ": 40000},
    {"0AM": 1, "0DA": y - 45, "0DB": y - 43, "0CF": 2, "0F0": y - 8, "0F1": y - 12, "1AJ": 60000, "1BJ": 30000,
     "2DC": 5000, "2TR": 1000, "2OP": 1, "4BA": 8000, "1AS": 0},
    {"0AV": 1, "0DA": y - 80, "1AS": 25000, "2DC": 3000, "2TR": 2000},
    {"0AC": 1, "0DA": y - 35, "0CF": 1, "0F0": y - 3, "0BT": 1, "1AJ": 25000, "6NS": 500, "APS": 4500, "BPS": 0, "CPS": 0, "DPS": 0},
    {"0AM": 1, "0DA": y - 50, "0DB": y - 50, "1AJ": 300000, "1BJ": 250000, "2DC": 200000, "5HQ": 20000, "5KC": 30000},
]
def run(cases):
    inp = "".join(f"{i};{y};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n" for i, b in cases)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    res = {}
    for line in r.stdout.splitlines():
        p = line.split(";")
        res[p[0]] = ";".join(x for x in p[1:] if not x.startswith(("TXFOYER", "PAS")))
    return res
cases = []
for j, b in enumerate(bases):
    cases.append((f"b{j}", b))
    for r in rows:
        k = r["nom"]
        if k in b:
            continue
        flag = float(r["nombre"]) == float(r["montant"])
        for v in ((1,) if flag else (1000, 15000)):
            nb = dict(b); nb[k] = v
            cases.append((f"{k}_{j}_{v}", nb))
res = run(cases)
mod = {}
for r in rows:
    k = r["nom"]
    mod[k] = any(res.get(f"{k}_{j}_{v}") not in (None, res[f"b{j}"]) for j in range(len(bases)) for v in (1, 1000, 15000)) or any(k in b for b in bases)
json.dump(mod, open(out, "w"), indent=0)
print(sum(mod.values()), "of", len(mod), "boxes change a Lean output")
