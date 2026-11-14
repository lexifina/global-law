"""Round 8 ownact: per-stratum counts of the certified rows (for the audit) -> cert/strata.tsv + strata.json.

    python -X utf8 round8/agents/ownact/strata.py [--cert cert] [--rows rows.jsonl]

Strata: court system (federal = courts2 system 0 / state), decade of the acting decision, verb strength of the
main quote (family: overrul/disapprov/reced/abrogat; strong: reject/repudiat/disavow/abandon/overturn/discard;
follow: "follow"; state: anything else, e.g. "no longer", "cannot survive", "wrongly decided"), scope, joined.
"""
import argparse
import collections
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = "\n"


def verb_class(q):
    ql = q.lower()
    if re.search(r"overrul|disapprov|reced|abrogat", ql):
        return "family"
    if re.search(r"reject|repudiat|disavow|abandon|overturn|discard", ql):
        return "strong"
    if "follow" in ql:
        return "follow"
    return "state"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=os.path.join(HERE, "cert"))
    ap.add_argument("--rows", default=os.path.join(HERE, "rows.jsonl"))
    ap.add_argument("--items", default=os.path.join(HERE, "items8.jsonl.gz"))
    a = ap.parse_args()
    meta = {}
    for line in gzip.open(a.items, "rt", encoding="utf-8"):
        it = json.loads(line)
        meta[it["n"]] = (it["system"], it["date"] // 100000 * 10)
    joined = set()
    jp = os.path.join(a.cert, "joined_delta.tsv")
    if os.path.exists(jp):
        for line in open(jp, encoding="utf-8"):
            joined.add(line.split("\t")[0])
    out = []
    c = collections.Counter()
    for line in open(os.path.join(a.cert, "treatments_delta.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if not p[0].startswith("t8:"):
            continue
        by = int(p[1])
        sysm, dec = meta.get(by, (-1, 0))
        fed = "federal" if sysm == 0 else "state"
        vc = verb_class(p[11])
        row = [p[0], fed, str(dec), vc, p[4], p[5], "joined" if p[0] in joined else "one"]
        out.append(row)
        for k in ("court:" + fed, "decade:%d" % dec, "verb:" + vc, "kind:" + p[4], "scope:" + p[5], "form:" + row[6]):
            c[k] += 1
    with open(os.path.join(a.cert, "strata.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("id\tcourt\tdecade\tverb\tkind\tscope\tform\n")
        for r in out:
            f.write("\t".join(r) + NL)
    c["rows"] = len(out)
    json.dump(dict(sorted(c.items())), open(os.path.join(a.cert, "strata.json"), "w", encoding="utf-8", newline=NL),
              indent=1)
    print(json.dumps(dict(sorted(c.items())), indent=1))


if __name__ == "__main__":
    main()
