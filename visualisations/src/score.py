"""Score the model results and build the bridge graph -> report.json, bridges.json"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

res = [json.loads(l) for l in open("results.jsonl", encoding="utf-8")]
ok = [r for r in res if "out" in r]
rows = {json.loads(l)["id"]: json.loads(l) for l in open("provisions.jsonl", encoding="utf-8")}
ct = json.loads(Path("constitute/tags.json").read_text(encoding="utf-8"))
gold = json.loads(Path("gold_hand.json").read_text(encoding="utf-8"))
tags = {**{f"de|Art. {a}": set(t) for a, t in ct["tags"]["de"].items()}, **{f"ch|BV Art. {a}": set(t) for a, t in ct["tags"]["ch"].items()}}
hand = defaultdict(set)
for a, b, _ in gold:
    hand[a].add(b); hand[b].add(a)
report = {"models": Counter(r.get("model") for r in res), "errors": sum("error" in r for r in res),
          "tokens": [sum(r.get("tokens", [0, 0])[i] for r in res) for i in (0, 1)]}

# 1. Rerank vs embedding top-1, on the same queries
ev = defaultdict(lambda: {"n": 0, "emb1": 0, "llm1": 0, "ceiling": 0, "abstain": 0})
for r in ok:
    if not r["id"].startswith("rerank"): continue
    q, dst, top = r["meta"]["q"], r["meta"]["dst"], r["meta"]["top"]
    if q in hand and any(t.split("|")[0] == dst for t in hand[q]):
        rel, key = {t for t in hand[q] if t.split("|")[0] == dst}, "hand"
    elif q in tags and q.split("|")[0] in ("de", "ch") and dst in ("de", "ch"):
        rel = {k for k, t in tags.items() if k.split("|")[0] == dst and t & tags[q]}
        key = "constitute"
    else:
        continue
    if not rel: continue
    best = r["out"].get("best")
    pick = top[int(best) - 1] if isinstance(best, (int, float)) and 1 <= int(best) <= len(top) else None
    e = ev[key]; e["n"] += 1
    e["emb1"] += top[0] in rel; e["llm1"] += pick in rel; e["ceiling"] += bool(rel & set(top)); e["abstain"] += pick is None
report["rerank"] = {k: {**v, **{f"{m}_rate": v[m] / v["n"] for m in ("emb1", "llm1", "ceiling")}} for k, v in ev.items()}

# 2. Judged bridges: relation mix overall, by jurisdiction pair and by similarity band
J = [r for r in ok if r["id"].startswith("judge")]
for r in J:
    r["rel"] = str(r["out"].get("relation", "")).lower().strip()
report["relations"] = Counter(r["rel"] for r in J)
report["by_pair"] = {p: Counter(r["rel"] for r in J if r["meta"]["pair"] == p) for p in sorted({r["meta"]["pair"] for r in J})}
sims = np.array([r["meta"]["sim"] for r in J])
bands = np.quantile(sims, [0, .2, .4, .6, .8, 1])
cal = []
for lo, hi in zip(bands[:-1], bands[1:]):
    sel = [r for r in J if lo <= r["meta"]["sim"] <= hi]
    cal.append({"lo": float(lo), "hi": float(hi), "n": len(sel),
                "usable": sum(r["rel"] in ("equivalent", "analogous") for r in sel) / len(sel),
                "equivalent": sum(r["rel"] == "equivalent" for r in sel) / len(sel)})
report["calibration"] = cal

# 3. Bridge graph: accepted bridges grouped by concept
def norm(c):
    c = re.sub(r"[^a-z ]", "", str(c).lower()).strip()
    return re.sub(r"\s+", " ", c)
bridges = []
for r in J:
    if r["rel"] not in ("equivalent", "analogous", "related"): continue
    a, b = r["meta"]["a"], r["meta"]["b"]
    bridges.append({"a": a, "b": b, "pair": r["meta"]["pair"], "sim": round(r["meta"]["sim"], 3), "relation": r["rel"],
                    "concept": norm(r["out"].get("concept")), "note": r["out"].get("note", ""),
                    "a_heading": rows[a]["heading"][:90], "b_heading": rows[b]["heading"][:90]})
bridges.sort(key=lambda x: (-["related", "analogous", "equivalent"].index(x["relation"]), -x["sim"]))

# 4. Change history on each side of a bridge (do bridged provisions move together?)
kg = json.loads(Path("kg.json").read_text(encoding="utf-8"))
changes = defaultdict(list)
for l in kg["laws"]:
    if l["baseline"]: continue
    for p in l["provisions"]:
        changes[f"{l['corpus']}|{p}"].append({"date": l["date"], "law": l["law"]})
for b in bridges:
    b["a_changes"], b["b_changes"] = changes.get(b["a"], []), changes.get(b["b"], [])
both = [b for b in bridges if b["a_changes"] and b["b_changes"]]
report["co_changed"] = len(both)

# 5. Clusters: names and jurisdiction spread
cl = json.loads(Path("clusters.json").read_text(encoding="utf-8"))
names = next((r["out"].get("names", {}) for r in ok if r["id"] == "name|clusters"), {})
for c in cl:
    c["name"] = names.get(str(c["k"])) or names.get(f"Cluster {c['k']}") or f"cluster {c['k']}"
    c["spread"] = sum(v > 0 for v in c["counts"].values())
report["clusters"] = sorted(({"name": c["name"], "counts": c["counts"], "spread": c["spread"]} for c in cl), key=lambda c: (-c["spread"], -sum(c["counts"].values())))

Path("report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=dict), encoding="utf-8")
Path("bridges.json").write_text(json.dumps({"bridges": bridges, "clusters": cl}, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: report[k] for k in ("models", "errors", "tokens", "rerank", "relations", "by_pair", "calibration", "co_changed")}, indent=1, default=dict))
print(len(bridges), "bridges kept;", sum(c["spread"] >= 2 for c in cl), "clusters span 2+ jurisdictions")
for c in report["clusters"][:25]: print(c["spread"], c["counts"], c["name"])
for b in both[:10]: print(b["a"], "<->", b["b"], b["concept"], [x["date"] for x in b["a_changes"]], [x["date"] for x in b["b_changes"]])
