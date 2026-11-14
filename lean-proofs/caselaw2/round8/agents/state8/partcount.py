"""Count decisions (with reader candidates) whose Majority section is cut after a short head block by a
"<judge>, J., concurring" joining line, so the opinion of the court is labelled concurrence~ (reader common.part_map).

    python -X utf8 partcount.py [--procs 10]
Source: data/reader_work/cand*/<repo>.jsonl.gz decision records ("d": parts). No answer-key file is read.
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common8 import RW, L  # noqa: E402

HEAD_MAX = 400


def one(path):
    c = collections.Counter()
    cands = collections.Counter()
    hit_nodes = set()
    rej = {}
    repo = os.path.basename(path).replace(".jsonl.gz", "")
    rp = os.path.join(RW, "res", repo + ".rejects.tsv.gz")
    if os.path.exists(rp) and "/cand/" in path.replace("\\", "/"):
        with gzip.open(rp, "rt", encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                rej[p[0]] = p[1]
    seg = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["t"] == "d":
                parts = r["parts"]
                bad = None
                for i, (a, b, p) in enumerate(parts):
                    if p in ("majority", "perCuriam") and i + 1 < len(parts) and parts[i + 1][2] == "concurrence~" \
                            and b - a < HEAD_MAX and parts[i + 1][1] - parts[i + 1][0] > 2 * (b - a):
                        bad = (parts[i + 1][0], parts[i + 1][1])
                        break
                c["decisions"] += 1
                if bad:
                    c["cut"] += 1
                    seg[r["n"]] = bad
                    hit_nodes.add(r["n"])
            elif r["t"] == "c" and r["n"] in seg:
                a, b = seg[r["n"]]
                if a <= r["s0"] < b:
                    cands["cand_in_cut"] += 1
                    fam = r.get("fam") or ["?"]
                    cands["fam:" + fam[0]] += 1
    return repo, c, cands, sorted(hit_nodes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    paths = sorted(os.path.join(RW, "cand", f) for f in os.listdir(os.path.join(RW, "cand")) if f.endswith(".jsonl.gz"))
    tot = collections.Counter()
    out = {}
    for repo, c, cands, nodes in L.pmap(one, paths, procs=a.procs):
        tot.update(c)
        tot.update(cands)
        out[repo] = {"c": dict(c), "cands": dict(cands), "nodes": nodes}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "partcut.json"), "w"))
    print(dict(tot))
    for repo, v in sorted(out.items(), key=lambda kv: -kv[1]["c"].get("cut", 0))[:25]:
        print(repo, v["c"].get("cut", 0), v["c"]["decisions"], v["cands"].get("cand_in_cut", 0), v["cands"].get("fam:overrule", 0))


if __name__ == "__main__":
    main()
