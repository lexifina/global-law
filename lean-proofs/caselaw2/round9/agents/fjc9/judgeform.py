"""fjc9: of the W drops 'wide_no_phrase' / 'wide_no_court_act', how many name the court below as a judge
("the district judge", "the magistrate judge", "Judge <Name>") in the citation sentence or the 600 characters
before it (a form the round-8 anchor cue list cannot certify)?

    python -X utf8 judgeform.py
"""
import collections, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import L  # noqa: E402

JUDGE = re.compile(r"\b(?:district|magistrate|trial|bankruptcy)\s+judge\b|\bJudge\s+[A-Z][a-z]+", re.I)


def main():
    want = collections.defaultdict(set)
    for p in glob.glob(os.path.join(HERE, "work", "link", "*.why.tsv")):
        for line in open(p, encoding="utf-8"):
            n, j, k = line.rstrip("\n").split("\t")
            if k in ("drop:anchor:wide_no_phrase", "drop:anchor:wide_no_court_act"):
                want[int(n)].add((int(j), k))
    sidx = diag.shard_index()
    by = collections.defaultdict(list)
    for n in want:
        by[sidx[n]].append(n)
    st = collections.Counter()
    for tag, ns in by.items():
        path = os.path.join(L.CACHE, tag + ".jsonl.gz")
        s = set(ns)
        for n, g in L.decisions(path):
            if n not in s:
                continue
            for j, k in want[n]:
                hit = False
                for cw in g["cw"]:
                    if cw["j"] != j:
                        continue
                    w0, wt = cw["w"]
                    s0, s1 = cw["s"][0] - w0, cw["s"][1] - w0
                    if JUDGE.search(wt[max(0, s0 - 600):s1]):
                        hit = True
                st["%s judge_form=%s" % (k, hit)] += 1
    for k in sorted(st):
        print(st[k], k)


if __name__ == "__main__":
    main()
