"""Global readiness of official legal sources, from the world-law-repos stubs -> analysis8.json
For each of ~200 jurisdictions: build status (ready / partial / scrape / gazette / none), the first official source's
capabilities, whether we already hold a history, and the world-atlas id to draw it on a map.
"""
import json, re, unicodedata
from pathlib import Path

D = Path.home() / "Documents"
atlas = json.loads(Path("geo/countries-50m.json").read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())
by_name = {norm(g["properties"]["name"]): g.get("id") or "name:" + g["properties"]["name"] for g in atlas["objects"]["countries"]["geometries"]}
ALIAS = {  # register name -> world-atlas name
    "unitedstates": "unitedstatesofamerica", "czechia": "czechia", "bosniaandherzegovina": "bosniaandherz",
    "dominicanrepublic": "dominicanrep", "centralafricanrepublic": "centralafricanrep", "southsudan": "ssudan",
    "equatorialguinea": "eqguinea", "democraticrepublicofthecongo": "demrepcongo", "drcongo": "demrepcongo",
    "republicofthecongo": "congo", "republicofcongo": "congo", "saintvincentandthegrenadines": "stvinandgren", "congo": "congo", "ivorycoast": "cotedivoire", "cotedivoire": "cotedivoire",
    "eswatini": "eswatini", "northmacedonia": "macedonia", "solomonislands": "solomonis", "marshallislands": "marshallis",
    "antiguaandbarbuda": "antiguaandbarb", "saintkittsandnevis": "stkittsandnevis", "saintlucia": "saintlucia",
    "saotomeandprincipe": "saotomeandprincipe",
    "britishvirginislands": "britishvirginis", "caymanislands": "caymanis", "turksandcaicosislands": "turksandcaicosis",
    "isleofman": "isleofman", "faroeislands": "faeroeis", "frenchpolynesia": "frpolynesia", "vaticancity": "vatican",
    "hongkong": "hongkong", "macau": "macao", "palestine": "palestine", "timorleste": "timorleste", "eastimor": "timorleste",
    "westernsahara": "wsahara", "falklandislands": "falklandis", "unitedarabemirates": "unitedarabemirates",
    "northkorea": "northkorea", "southkorea": "southkorea", "micronesia": "micronesia", "capeverde": "caboverde",
}
rows = []
stubs = sorted((D / "world-law-repos").glob("*/jurisdiction.json"))
held = {"de": "germany", "ch": "switzerland", "gb": "united-kingdom", "us": "united-states", "ee": "estonia", "li": "liechtenstein",
        "lu": "luxembourg", "mt": "malta", "mc": "monaco", "sk": "slovakia", "si": "slovenia", "fi": "finland", "hr": "croatia",
        "gi": "gibraltar", "dk": "denmark", "hk": "hong-kong"}
for j in stubs:
    meta = json.loads(j.read_text(encoding="utf-8"))
    src = (j.parent / "SOURCES.md").read_text(encoding="utf-8") if (j.parent / "SOURCES.md").exists() else ""
    off = next((l for l in src.splitlines() if l.startswith("|") and "Official" in l), "")
    cells = [c.strip().lower() for c in off.split("|")[1:-1]]
    cap = {"history": cells[2] if len(cells) > 4 else None, "names_act": cells[3] if len(cells) > 4 else None, "api": cells[4] if len(cells) > 4 else None}
    n = norm(meta["name"]); aid = by_name.get(ALIAS.get(n, n)) or by_name.get(n)
    rows.append({"code": meta["code"], "path": meta["path"], "name": meta["name"], "build": meta.get("build"), **cap, "atlas": aid,
                 "held": meta["path"] in held, "sources": src.count("\n| [")})
# Jurisdictions we hold that have no stub row (sub-national or already moved out of world-law-repos)
have = {r["path"] for r in rows}
for code, slug in held.items():
    if code not in have:
        n = norm(slug.replace("-", " ")); rows.append({"code": code.upper(), "path": code, "name": slug.replace("-", " ").title(), "build": "held",
                                                     "history": "yes", "names_act": "yes", "api": None, "atlas": by_name.get(ALIAS.get(n, n)), "held": True, "sources": 0})
for r in rows:
    if r["held"]: r["build"] = "held"
from collections import Counter
print(len(rows), Counter(r["build"] for r in rows))
print("unmatched:", [r["name"] for r in rows if not r["atlas"]])
print("capabilities:", Counter((r["history"], r["names_act"], r["api"]) for r in rows).most_common(8))
POINTS = {"Gibraltar": [-5.35, 36.14], "Tuvalu": [179.2, -8.5]}
for r in rows:
    if r["name"] in POINTS: r["point"] = POINTS[r["name"]]
Path("analysis8.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
