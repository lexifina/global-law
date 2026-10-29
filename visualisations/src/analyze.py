"""Cross-jurisdiction bridge retrieval: evaluation against two answer keys, plus the candidate list for judging.

Inputs: provisions.jsonl, emb.npy, constitute/tags.json, gold_hand.json. Output: analysis.json, candidates.json.
"""
import json
from pathlib import Path
import numpy as np

rows = [json.loads(l) for l in open("provisions.jsonl", encoding="utf-8")]
ids = [r["id"] for r in rows]
idx = {k: i for i, k in enumerate(ids)}
corp = np.array([r["corpus"] for r in rows])
E = np.load("emb.npy").astype(np.float64)
E /= np.linalg.norm(E, axis=1, keepdims=True)
CODES = ["de", "ch", "gb", "us"]


def variant(name):
    X = E.copy()
    if name == "centred":  # remove each corpus's mean direction, which carries language and drafting style
        for c in CODES:
            X[corp == c] -= X[corp == c].mean(axis=0)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X


VARIANTS = {v: variant(v) for v in ("raw", "centred")}


def rank_of(X, q, cand_mask, relevant):
    s = X[cand_mask] @ X[q]
    cand = np.flatnonzero(cand_mask)
    order = cand[np.argsort(-s)]
    pos = [int(np.flatnonzero(order == r)[0]) + 1 for r in relevant if r in set(order)]
    return min(pos) if pos else None


def score(ranks, pool):
    ranks = [r for r in ranks if r]
    n = len(ranks)
    return {"queries": n, "hit1": sum(r <= 1 for r in ranks) / n, "hit5": sum(r <= 5 for r in ranks) / n,
            "hit10": sum(r <= 10 for r in ranks) / n, "mrr": float(np.mean([1 / r for r in ranks])),
            "median_rank": float(np.median(ranks)), "pool": pool}


results = {}

# Answer key A: Constitute topic tags (German Basic Law <-> Swiss Federal Constitution, paragraph-level tags).
ct = json.loads(Path("constitute/tags.json").read_text(encoding="utf-8"))
tags = {"de": {f"de|Art. {a}": set(t) for a, t in ct["tags"]["de"].items()},
        "ch": {f"ch|BV Art. {a}": set(t) for a, t in ct["tags"]["ch"].items()}}
tags = {c: {k: v for k, v in d.items() if k in idx} for c, d in tags.items()}
for name, X in VARIANTS.items():
    for src, dst in (("de", "ch"), ("ch", "de")):
        mask = corp == dst
        ranks = []
        for q, qt in tags[src].items():
            rel = [idx[k] for k, t in tags[dst].items() if t & qt]
            if rel:
                ranks.append(rank_of(X, idx[q], mask, rel))
        results[f"constitute {src}->{dst} {name}"] = score(ranks, int(mask.sum()))

# Answer key B: hand-written functional counterparts across languages.
gold = json.loads(Path("gold_hand.json").read_text(encoding="utf-8"))
pairs = [(a, b) for a, b, _ in gold if a in idx and b in idx]
for name, X in VARIANTS.items():
    ranks = []
    for a, b in pairs:
        for q, t in ((a, b), (b, a)):
            ca = corp[idx[t]]
            rel = [idx[y if x == q else x] for x, y in pairs if q in (x, y) and corp[idx[y if x == q else x]] == ca]
            ranks.append(rank_of(X, idx[q], corp == ca, rel))
    results[f"hand {name}"] = score(ranks, None)

# Random baseline for scale: expected Hit@1 when picking uniformly in the pool.
for k, v in results.items():
    if v["pool"]:
        v["random_hit1"] = None

# Language gap: mean cosine between corpora, before and after centring.
gap = {}
for name, X in VARIANTS.items():
    gap[name] = {f"{a}-{b}": float((X[corp == a] @ X[corp == b].T).mean()) for i, a in enumerate(CODES) for b in CODES[i:]}

# Candidates: mutual nearest neighbours across every pair of jurisdictions (centred space).
X = VARIANTS["centred"]
cands = []
for i, a in enumerate(CODES):
    for b in CODES[i + 1:]:
        A, B = np.flatnonzero(corp == a), np.flatnonzero(corp == b)
        S = X[A] @ X[B].T
        ab, ba = S.argmax(1), S.argmax(0)
        for ia, jb in enumerate(ab):
            if ba[jb] == ia:
                cands.append({"a": ids[A[ia]], "b": ids[B[jb]], "sim": float(S[ia, jb]), "pair": f"{a}-{b}"})
cands.sort(key=lambda c: -c["sim"])

# Unmatched: provisions whose best foreign match is weak (bottom decile), per corpus.
best = {}
for c in CODES:
    M = np.flatnonzero(corp == c)
    F = np.flatnonzero(corp != c)
    s = (X[M] @ X[F].T).max(1)
    best[c] = {"median_best": float(np.median(s)),
               "loneliest": [ids[M[j]] for j in np.argsort(s)[:8]],
               "best_connected": [ids[M[j]] for j in np.argsort(-s)[:8]]}

Path("analysis.json").write_text(json.dumps({"eval": results, "gap": gap, "isolation": best, "n_candidates": len(cands)}, ensure_ascii=False, indent=1), encoding="utf-8")
Path("candidates.json").write_text(json.dumps(cands, ensure_ascii=False), encoding="utf-8")
for k, v in results.items():
    print(f"{k:32s} n={v['queries']:3d} hit@1={v['hit1']:.2f} hit@5={v['hit5']:.2f} hit@10={v['hit10']:.2f} mrr={v['mrr']:.2f} med={v['median_rank']}")
print("gap", {k: {p: round(s, 3) for p, s in v.items()} for k, v in gap.items()})
from collections import Counter
print(len(cands), "mutual-NN candidates", Counter(c["pair"] for c in cands))
for c in cands[:12]:
    print(round(c["sim"], 3), c["a"], "<->", c["b"])
