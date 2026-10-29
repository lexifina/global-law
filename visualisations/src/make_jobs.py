"""Build the model jobs: rerank (answer-key queries), judge (mutual-NN bridges), and concept clusters -> jobs.jsonl, clusters.json"""
import json, re
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans

rows = [json.loads(l) for l in open("provisions.jsonl", encoding="utf-8")]
ids = [r["id"] for r in rows]
idx = {k: i for i, k in enumerate(ids)}
corp = np.array([r["corpus"] for r in rows])
E = np.load("emb.npy").astype(np.float64)
E /= np.linalg.norm(E, axis=1, keepdims=True)
NAME = {"de": "Germany, Basic Law (German)", "ch": "Switzerland, federal law (German)", "gb": "United Kingdom, SEND law", "us": "United States Code"}


def snippet(i, n=1100):
    t = re.sub(r"^---.*?---\s*", "", rows[i]["text"], flags=re.S)
    t = re.sub(r"\s+", " ", t)
    return f"[{ids[i]}] {t[:n]}"


jobs = []
SYS_RERANK = ("You compare statutes across legal systems. Given one provision and numbered candidates from another system, "
              "pick the candidate that does the same legal job (its functional counterpart), judging by what the rule does, "
              "not by shared words. Reply in JSON: {\"best\": <number or null if none fits>, \"why\": \"<12 words>\"}.")

# Rerank queries from both answer keys
ct = json.loads(Path("constitute/tags.json").read_text(encoding="utf-8"))
queries = set()
for a in ct["tags"]["de"]:
    queries.add((f"de|Art. {a}", "ch"))
for a in ct["tags"]["ch"]:
    queries.add((f"ch|BV Art. {a}", "de"))
for a, b, _ in json.loads(Path("gold_hand.json").read_text(encoding="utf-8")):
    queries.add((a, b.split("|")[0])); queries.add((b, a.split("|")[0]))
for q, dst in sorted(queries):
    if q not in idx: continue
    cand = np.flatnonzero(corp == dst)
    top = cand[np.argsort(-(E[cand] @ E[idx[q]]))[:10]]
    user = f"Provision ({NAME[corp[idx[q]]]}):\n{snippet(idx[q], 1400)}\n\nCandidates ({NAME[dst]}):\n" + "\n\n".join(f"{k + 1}. {snippet(j, 700)}" for k, j in enumerate(top))
    jobs.append({"id": f"rerank|{q}|{dst}", "system": SYS_RERANK, "user": user, "meta": {"q": q, "dst": dst, "top": [ids[j] for j in top]}})

# Judge mutual-NN bridges
SYS_JUDGE = ("You compare statutes across legal systems. Classify how two provisions relate. relation: \"equivalent\" (same legal rule or "
             "institution), \"analogous\" (different mechanism, same function), \"related\" (same subject, different job), or \"unrelated\". "
             "concept: the shared legal concept in 2-4 plain English words (e.g. \"freedom of religion\", \"bankruptcy estate\"). "
             "note: one sentence in English naming the most important difference. Reply in JSON: {\"relation\":..., \"concept\":..., \"note\":...}.")
for c in json.loads(Path("candidates.json").read_text(encoding="utf-8")):
    user = f"A:\n{snippet(idx[c['a']])}\n\nB:\n{snippet(idx[c['b']])}"
    jobs.append({"id": f"judge|{c['a']}|{c['b']}", "system": SYS_JUDGE, "user": user, "meta": c})

# Concept clusters (corpus-centred space so language does not split clusters)
X = E.copy()
for c in set(corp):
    X[corp == c] -= X[corp == c].mean(0)
X /= np.linalg.norm(X, axis=1, keepdims=True)
km = KMeans(n_clusters=90, n_init=8, random_state=7).fit(X)
clusters = []
for k in range(90):
    m = np.flatnonzero(km.labels_ == k)
    counts = {c: int((corp[m] == c).sum()) for c in ["de", "ch", "gb", "us"]}
    cen = km.cluster_centers_[k]
    near = m[np.argsort(-(X[m] @ cen))]
    sample = []
    for c in ["de", "ch", "gb", "us"]:
        sample += [j for j in near if corp[j] == c][:3]
    clusters.append({"k": k, "counts": counts, "members": [ids[j] for j in m], "sample": [ids[j] for j in sample]})
SYS_NAME = ("Name each cluster of statutory provisions with a 2-4 word plain-English legal concept (e.g. \"debt enforcement by seizure\"). "
            "Reply in JSON: {\"names\": {\"<cluster number>\": \"<name>\", ...}}.")
body = "\n\n".join(f"Cluster {c['k']}:\n" + "\n".join(snippet(idx[s], 160) for s in c["sample"]) for c in clusters)
jobs.append({"id": "name|clusters", "system": SYS_NAME, "user": body, "meta": {}})
Path("clusters.json").write_text(json.dumps(clusters, ensure_ascii=False), encoding="utf-8")
Path("jobs.jsonl").write_text("\n".join(json.dumps(j, ensure_ascii=False) for j in jobs), encoding="utf-8")
from collections import Counter
print(Counter(j["id"].split("|")[0] for j in jobs), "chars", sum(len(j["user"]) for j in jobs))
print("multi-jurisdiction clusters:", sum(sum(v > 0 for v in c["counts"].values()) >= 2 for c in clusters))
