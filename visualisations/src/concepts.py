import json, re
from pathlib import Path
D = Path.home() / "Documents"
C = {
 "Insolvency & debt": r"bankrupt|insolven|debtor|creditor|Konkurs|Betreibung|Schuldner|Gläubiger",
 "Data & privacy": r"personal data|privacy|Personendaten|Datenschutz|Fernmeldegeheimnis|Briefgeheimnis",
 "Education & children": r"\bchild|educat|\bschool|Kinder|\bSchul(?:e|en|wesen|pflicht)\b|Bildung",
 "Courts & judges": r"\bcourt\b|judge|tribunal|Gericht|Richter",
 "Tax & public money": r"\btax|revenue|Steuer|Abgabe|Haushalt",
 "Intellectual property": r"copyright|patent|trademark|Urheber|Patent|geistige",
 "Elections & parliament": r"\belection|\bvote|Congress|\bWahl|Bundestag|Bundesversammlung|Volksabstimmung",
}
roots = {"de": ("grundgesetz", "artikel/*.md"), "ch": ("swiss-law", "*/art-*.md"),
         "gb": ("uk-law-history", "uk*/**/*.md"), "us": ("us-code-history", "title-*/*.md")}
out = {}
for k, (r, g) in roots.items():
    files = list((D / r).glob(g))
    out[k] = {c: sum(1 for f in files if re.search(p, f.read_text(encoding="utf-8", errors="ignore"), re.I)) for c, p in C.items()}
d = json.loads(Path("kg.json").read_text(encoding="utf-8")); d["concepts"] = out
for l in d["laws"]:
    l["baseline"] = len(l["provisions"]) > 50 or l["law"].startswith("Bundeskanzlei")
Path("kg.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print(json.dumps(out, indent=0)); print(sum(not l["baseline"] for l in d["laws"]), "amending laws;", sum(l["baseline"] for l in d["laws"]), "baselines")
for k,v in d["xrefs"].items(): print(k, v[:4])
