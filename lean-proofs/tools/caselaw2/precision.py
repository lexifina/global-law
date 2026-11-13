"""Aggregate reviewer verdicts (verdict_<field>_<n>.tsv) against key_<field>.tsv: precision per field and value.

    python precision.py <val-dir>
Precision = correct / (correct + wrong); `unclear` (the header does not show the answer) is reported separately.
"""
import collections, glob, os, sys


def main(d):
    for fld in ("bench", "publication", "form", "unit"):
        key = {}
        for line in open(os.path.join(d, "key_%s.tsv" % fld), encoding="utf-8"):
            k, node, _, v, code, cid = line.rstrip("\n").split("\t")
            key[k] = (v, code)
        c = collections.defaultdict(collections.Counter)
        seen = set()
        for fn in sorted(glob.glob(os.path.join(d, "verdict_%s_*.tsv" % fld))):
            for line in open(fn, encoding="utf-8"):
                p = line.rstrip("\n").split("\t")
                if len(p) < 3 or p[0] not in key or p[0] in seen:
                    continue
                seen.add(p[0])
                verdict = p[2].strip().lower()
                c[key[p[0]][0]][verdict] += 1
                c["ALL"][verdict] += 1
        print("## %s (judged %d of %d)" % (fld, len(seen), len(key)))
        print("| value | n | correct | wrong | unclear | precision |")
        print("|---|---|---|---|---|---|")
        for v in sorted(c, key=lambda x: (x == "ALL", x)):
            x = c[v]
            dec = x["correct"] + x["wrong"]
            print("| %s | %d | %d | %d | %d | %s |" % (v, sum(x.values()), x["correct"], x["wrong"], x["unclear"],
                                                    "%.0f%%" % (100 * x["correct"] / dec) if dec else "-"))
        print()


if __name__ == "__main__":
    main(sys.argv[1])
