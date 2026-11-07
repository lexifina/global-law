"""../law-roses/roses2-data.json -> rw-data.json: every country with 30 or more provisions in force.

Per country: n provisions, v[8] provisions by times amended (0, 1, 2-3, 4-7, ... folded at 64+),
b[14] provisions by decade they entered the record. Subnational rows are left out.
Usage: python -I rw_prep.py ../law-roses/roses2-data.json ../geo/countries-50m.json rw-data.json
"""
import json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
at = json.load(open(sys.argv[2], encoding="utf-8"))
names = {g["properties"]["name"] for g in at["objects"]["countries"]["geometries"]}
AT = {"Aland": "Åland", "Antigua and Barbuda": "Antigua and Barb.", "Cayman Islands": "Cayman Is.",
      "Central African Republic": "Central African Rep.", "Cote Divoire": "Côte d'Ivoire",
      "Dominican Republic": "Dominican Rep.", "Dr Congo": "Dem. Rep. Congo", "Eswatini": "eSwatini", "Macau": "Macao",
      "North Macedonia": "Macedonia", "Republic of Congo": "Congo", "Sao Tome and Principe": "São Tomé and Principe",
      "South Sudan": "S. Sudan", "Timor Leste": "Timor-Leste"}
DISP = {"Aland": "Åland", "Cote Divoire": "Côte d'Ivoire", "Dr Congo": "DR Congo", "Timor Leste": "Timor-Leste",
        "Sao Tome and Principe": "São Tomé and Príncipe"}
rows = []
for r in d:
    if r["sub"] or r["name"] == "Pakistan Sindh" or sum(r["versions"]) < 30:
        continue
    a = AT.get(r["name"], r["name"])
    v = r["versions"]
    rows.append({"name": DISP.get(r["name"], r["name"]), "atlas": a if a in names else None,
                 "n": sum(v), "v": v[:7] + [sum(v[7:])], "b": r["born"]})
print(len(rows), "countries; not on the atlas:", [r["name"] for r in rows if not r["atlas"]])
json.dump(rows, open(sys.argv[3], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, separators=(",", ":"))
