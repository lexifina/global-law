"""Compare the default grids printed in BOFiP BOI-BAREME-000037 (text extract) with data/pas_grids.jsonl.
Usage: python3 -I harness/auth_grid_check.py BOFIP_TXT RATE_YEAR"""
import json, re, sys
t = open(sys.argv[1], encoding="utf-8").read().replace(" ", " ")
ry = int(sys.argv[2])
parts = re.split(r"\n?(?:I|II|III)\. Grille des taux par défaut", t)[1:4]
grids = [json.loads(l) for l in open("data/pas_grids.jsonl")]
mine = [g for g in grids if g.get("rate_year", g.get("rateYear")) == ry]
for i, p in enumerate(parts):
    bounds = [int(x.replace(" ", "")) for x in re.findall(r"Inférieure à ([\d ]+?) euros", p)[:1] + re.findall(r"inférieure à ([\d ]+?) euros", p)]
    print("zone", i, len(bounds), bounds)
for g in mine: print({k: v for k, v in g.items() if k not in ("rates",)})
