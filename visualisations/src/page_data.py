"""Collect everything the bridges page shows -> bridges_page.json"""
import json
from collections import Counter
from pathlib import Path
L = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
B = L("bridges.json"); rep = L("report.json"); an = L("analysis.json")
fam = {k: v.split(" (")[0] for k, v in json.loads(open("results2.jsonl", encoding="utf-8").readline())["out"]["families"].items()}
for b in B["bridges"]:
    b["family"] = fam.get(b["concept"], "Legal machinery")
    for s in ("a", "b"):
        b[s + "_changes"] = [{"date": c["date"], "law": c["law"][:80]} for c in b[s + "_changes"]][:6]
J = Counter()
for r in (json.loads(l) for l in open("results.jsonl", encoding="utf-8")):
    if r["id"].startswith("judge"):
        J[(r["meta"]["pair"], str(r["out"].get("relation")).lower())] += 1
shared = []
for c in B["clusters"]:
    strong = {k: v for k, v in c["counts"].items() if v >= 3}
    if len(strong) >= 2:
        shared.append({"name": c["name"], "counts": c["counts"]})
out = {"bridges": B["bridges"], "matrix": [[p, r, n] for (p, r), n in J.items()], "calibration": rep["calibration"],
       "rerank": rep["rerank"], "eval": an["eval"], "gap": an["gap"]["raw"], "shared_clusters": shared,
       "n_clusters": len(B["clusters"]), "tokens": rep["tokens"]}
Path("bridges_page.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(out["bridges"]), "bridges;", len(shared), "shared clusters:", [s["name"] for s in shared])
print(Counter((b["family"], b["relation"]) for b in out["bridges"] if b["relation"] != "related").most_common(30))
