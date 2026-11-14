"""diag step 1: the 66 SCDB implicit misses, their CRS targets, node metadata, and cached texts.

    python prep.py            writes pairs.tsv, nodes_meta.tsv and text/<node>.md (all under round5/diag/)
    python prep.py <node>...  adds extra nodes (meta + text) to the cache

Filter for the 66: rows of round2/recall_misses.tsv with set == 'scdb' and class == 'e'.
"""
import csv
import os
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
W = os.path.dirname(C2)
REPOS = os.path.expanduser("~/Documents/us-caselaw-repos")
TEXT = os.path.join(HERE, "text")


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
    miss = rows(os.path.join(C2, "round2/recall_misses.tsv"))
    r66 = [x for x in miss if x["set"] == "scdb" and x["class"] == "e"]
    crs = rows(os.path.join(C2, "gold/crs_overruled.tsv"))
    bycrs = defaultdict(list)
    for c in crs:
        bycrs[c["by_node"]].append(c)
    pairnote = {}
    for x in miss:
        if x["set"] != "scdb":
            pairnote[(x["by_node"], x["target_node"])] = x
    out = []
    for i, x in enumerate(r66):
        b = x["by_node"]
        cs = bycrs.get(b, [])
        if not cs:
            out.append([str(i), b, "-1", x["label"], "", "", "", x["cause"], x["note"]])
        for c in cs:
            m = pairnote.get((b, c["target_node"]), {})
            out.append([str(i), b, c["target_node"], x["label"], c["target_name"], c["target_cite"],
                        "q=%s;in2016=%s;express2016=%s;current=%s" % (c["qualifier"], c["in_2016"],
                                                                     c["expressly_2016"], c["in_current"]),
                        m.get("cause", x["cause"]), m.get("note", x["note"])])
    with open(os.path.join(HERE, "pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tby_node\ttarget_node\tlabel\ttarget_name\ttarget_cite\tcrs\tr2_cause\tr2_note\n")
        for o in out:
            f.write("\t".join(o) + "\n")
    ids = sorted({o[1] for o in out} | {o[2] for o in out if o[2] != "-1"}, key=int)
    have = cache(ids)
    print("decisions", len(r66), "pairs", len(out), "nodes", len(ids), "cached", len(have))


if __name__ == "__main__":
    main()
