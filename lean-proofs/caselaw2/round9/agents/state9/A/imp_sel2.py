"""state9 part A, rule v2 (after audit r9s02): seeded random reading sample of the IMP candidates.

    python -X utf8 imp_sel2.py [--n 800] [--seed 92]

Rule v2 = rule v1 (imp_cands.py) minus the `nolonger` cue family, minus act sentences with an intervening-cause word
(statute / legislature / amendment / enact / supersede / "in light of"), minus every item already read in v1
(sel.jsonl). In-act targets only. Writes sel2.jsonl and sel2_stats.json. No answer key is read.
"""
import argparse, collections, gzip, json, os, random, re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)
INTERVENING = re.compile(r"\b(?:in\s+light\s+of|supersed\w*|legislat\w*|statut\w*|amend\w*|enact\w*)", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=800)
    ap.add_argument("--seed", type=int, default=92)
    a = ap.parse_args()
    read = {json.loads(l)["id"] for l in open(os.path.join(HERE, "sel.jsonl"), encoding="utf-8")}
    pool = []
    st = collections.Counter()
    with gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            r["targets"] = [v for v in r["targets"] if v["where"] == "act"]
            if not r["targets"]:
                continue
            st["v1_pool"] += 1
            if r.get("tag") == "nolonger":
                st["drop_nolonger"] += 1
                continue
            if INTERVENING.search(r["act"]):
                st["drop_intervening"] += 1
                continue
            st["v2_pool"] += 1
            if r["id"] in read:
                st["drop_read_v1"] += 1
                continue
            pool.append(r)
    random.seed(a.seed)
    sel = random.sample(pool, min(a.n, len(pool)))
    for r in sel:
        st["sel_tag_" + r.get("tag", "?")] += 1
    with open(os.path.join(HERE, "sel2.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in sel:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "sel2_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
