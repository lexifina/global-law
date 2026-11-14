"""diag2 step 1: the dev pairs with baseline outcome c / d / e, node metadata, cached texts, the model's rows.

    python prep2.py            writes pairs.tsv, nodes_meta.tsv, text/<node>.md, model_rows.tsv (all under round5/diag2/)
    python prep2.py <node>...  adds extra nodes (meta + text) to the cache

Reads only round5/gold_fresh/dev/ (never sealed/).
"""
import csv
import os
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R5 = os.path.dirname(HERE)
C2 = os.path.dirname(R5)
W = os.path.dirname(C2)
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
TEXT = os.path.join(HERE, "text")
DEV = os.path.join(R5, "gold_fresh", "dev")


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def lookup(ids):
    ids = set(ids)
    want = {}
    with open(os.path.join(W, "graph/nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] in ids:
                want[p[0]] = p
                if len(want) == len(ids):
                    break
    return want


def fetch(want):
    by = defaultdict(list)
    for n, p in want.items():
        by[p[1]].append((n, p[2]))
    out = {}
    for repo, items in by.items():
        inp = "".join("HEAD:%s\n" % p for _, p in items).encode()
        res = subprocess.run(["git", "-C", os.path.join(REPOS, repo), "cat-file", "--batch"], input=inp,
                             capture_output=True).stdout
        i = 0
        for n, _ in items:
            nl = res.index(b"\n", i)
            hdr = res[i:nl].split()
            i = nl + 1
            if hdr[1] == b"missing":
                continue
            size = int(hdr[2])
            out[n] = res[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
            i += size + 1
    return out


def cache(ids):
    os.makedirs(TEXT, exist_ok=True)
    meta_path = os.path.join(HERE, "nodes_meta.tsv")
    have = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8", newline="") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                have[p[0]] = p
    need = [i for i in ids if i not in have or not os.path.exists(os.path.join(TEXT, i + ".md"))]
    if need:
        want = lookup(need)
        texts = fetch(want)
        for n, p in want.items():
            have[n] = p
            if n in texts:
                with open(os.path.join(TEXT, n + ".md"), "w", encoding="utf-8", newline="\n") as f:
                    f.write(texts[n])
        with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
            for n in sorted(have, key=int):
                f.write("\t".join(have[n]) + "\n")
    return have


def main():
    if len(sys.argv) > 1:
        have = cache(sys.argv[1:])
        for n in sys.argv[1:]:
            print("\t".join(have.get(n, [n, "MISSING"])))
        return
    dev = {r["pair_id"]: r for r in rows(os.path.join(DEV, "dev.tsv"))}
    base = rows(os.path.join(DEV, "results", "baseline-round4.pairs.tsv"))
    sel = [b for b in base if b["outcome"] in ("c", "d", "e")]
    order = {"c": 0, "d": 1, "e": 2}
    sel.sort(key=lambda b: (order[b["outcome"]], int(b["by_node"]), int(b["target_node"])))
    out = []
    for i, b in enumerate(sel):
        d = dev[b["pair_id"]]
        out.append({
            "idx": str(i), "pair_id": b["pair_id"], "outcome": b["outcome"], "by_node": b["by_node"],
            "target_node": b["target_node"], "label": d["overruling_name"], "by_cite": d["overruling_cite"],
            "by_date": d["overruling_date"], "target_name": d["overruled_name"], "target_cite": d["overruled_cite"],
            "target_date": d["overruled_date"], "partial": d["partial"], "implied": d["implied"],
            "explicit_hint": d["explicit_hint"], "sources": d["sources"], "key_note": d["note"],
            "model_status": b["model_status"], "model_actor": b["model_actor"], "at_risk": b["at_risk"],
            "reader_rows": b["reader_rows"]})
    cols = list(out[0].keys())
    with open(os.path.join(HERE, "pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for o in out:
            f.write("\t".join(o[c].replace("\t", " ") for c in cols) + "\n")
    ids = sorted({o["by_node"] for o in out} | {o["target_node"] for o in out}, key=int)
    have = cache(ids)
    # the model's rows for these pairs (either direction is not needed: by = Y, target = X)
    want = {(o["by_node"], o["target_node"]): o for o in out}
    wit = {}
    wp = os.path.join(C2, "data", "treatment_witness.tsv")
    if os.path.exists(wp):
        with open(wp, encoding="utf-8", newline="") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                wit[p[0]] = p
    n = 0
    with open(os.path.join(C2, "data", "treatments.tsv"), encoding="utf-8", newline="") as f, \
            open(os.path.join(HERE, "model_rows.tsv"), "w", encoding="utf-8", newline="\n") as g:
        g.write("idx\tpair_id\toutcome\tid\tby_node\ttarget_node\tdate\tkind\tscope\ttemporal\texplicit\ttext_sha\t"
                "start\tend\tquote\ttarget_evidence\tpart\treader\tconfidence\twitness_node\tby_evidence\n")
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            o = want.get((p[1], p[2]))
            if not o:
                continue
            w = wit.get(p[0], ["", "", "", ""])
            g.write("\t".join([o["idx"], o["pair_id"], o["outcome"]] + p[:16] + [w[1], w[2]]) + "\n")
            n += 1
    print("pairs", len(out), "nodes", len(ids), "cached", len(have), "model rows", n)


if __name__ == "__main__":
    main()
