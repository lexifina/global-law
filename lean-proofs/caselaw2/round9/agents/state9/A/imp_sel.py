"""state9 part A: seeded random reading sample of the IMP candidates (cands.jsonl.gz from imp_cands.py).

    python -X utf8 imp_sel.py [--n 520] [--seed 9]

Keeps only IN-ACT targets in each record (the act sentence names them), samples --n records uniformly at random
(seeded) from the whole candidate pool, writes sel.jsonl and sel_stats.json (pool counts per tag / federal-state).
No answer key is read.
"""
import argparse, collections, gzip, json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=520)
    ap.add_argument("--seed", type=int, default=9)
    a = ap.parse_args()
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "round6", "history"))
    import r6lib as L
    F = L.Facts()
    pool = []
    st = collections.Counter()
    with gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["targets"] = [v for v in r["targets"] if v["where"] == "act"]
            if not r["targets"]:
                continue
            fed = F.system(r["by_court"]) == 0
            r["fed"] = int(fed)
            st["pool"] += 1
            st["pool_" + ("federal" if fed else "state")] += 1
            st["tag_" + r.get("tag", "?")] += 1
            pool.append(r)
    random.seed(a.seed)
    sel = random.sample(pool, min(a.n, len(pool)))
    for r in sel:
        st["sel_tag_" + r.get("tag", "?")] += 1
        st["sel_" + ("federal" if r["fed"] else "state")] += 1
    with open(os.path.join(HERE, "sel.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in sel:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "sel_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
