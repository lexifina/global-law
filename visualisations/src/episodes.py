"""Group detected snapbacks into episodes (one per act and date range), excluding unidentified portal consolidations -> episodes.json"""
import json, re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

a = json.loads(Path("analysis2.json").read_text(encoding="utf-8"))
G = re.compile(r"Legimonaco|PIS RS|Riigi Teataja$|Rechtsdienst|Bundeskanzlei|Finlex|Legilux|Service central|Retsinformation|Department of Justice")
S = [s for s in a["snapbacks"] if not (G.search(s["law"]) or G.search(s["end_law"]))]
S = [s for s in S if s["days"] > 0 and "ispravak" not in s["law"] + s["end_law"]]  # corrections are not temporary law
ep = defaultdict(list)
for s in S:
    ep[(s["c"], s["law"], s["from"], s["to"], s["end_law"])].append(s["p"])
E = [{"c": c, "law": l, "from": f, "to": t, "end_law": el, "days": (date.fromisoformat(t) - date.fromisoformat(f)).days, "provs": ps}
     for (c, l, f, t, el), ps in ep.items()]
E.sort(key=lambda e: (e["from"], e["c"]))
Path("episodes.json").write_text(json.dumps(E, ensure_ascii=False), encoding="utf-8")
print(len(S), "provisions", len(E), "episodes", Counter(e["c"] for e in E), "sunsets", sum(e["law"] == e["end_law"] for e in E))
