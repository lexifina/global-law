"""Round 7, agent `antecedent`: counts for the report -> summary.json (and printed).

    python -X utf8 summarize.py [--cert cert]

Reading: packs answered / items / act true, by tier. Rows (rows.jsonl) and certified rows (cert/treatments_delta.tsv,
cert/joined_delta.tsv) by rule, kind and court group (federal: courts2 system 0, SCOTUS separately; state: by tier).
"""
import argparse, collections, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
NL = chr(10)


def group(F, n):
    c = int(F.court[n])
    if F.is_scotus(c):
        return "scotus"
    return ("federal" if F.system(c) == 0 else "state") + ":" + F.tier(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=os.path.join(HERE, "cert"))
    a = ap.parse_args()
    F = L.Facts()
    items = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(HERE, "packs", "map.jsonl"), encoding="utf-8")}
    packs = collections.defaultdict(lambda: collections.Counter())
    for p in sorted(glob.glob(os.path.join(HERE, "ans", "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            it = items.get(r.get("id"))
            if not it:
                continue
            c = packs[it["tier"]]
            c["answered"] += 1
            c["act_true"] += int(r.get("act") is True)
    total_items = collections.Counter(it["tier"] for it in items.values())
    answered_packs = sorted(os.path.basename(p)[4:-6] for p in glob.glob(os.path.join(HERE, "ans", "*.jsonl")))
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    rc = collections.Counter((r["rule"], r["kind"]) for r in rows)
    cert = []
    tp = os.path.join(a.cert, "treatments_delta.tsv")
    if os.path.exists(tp):
        for line in open(tp, encoding="utf-8"):
            p = line.rstrip(NL).split("\t")
            cert.append(p)
    joined = {line.split("\t")[0] for line in open(os.path.join(a.cert, "joined_delta.tsv"), encoding="utf-8")} \
        if os.path.exists(os.path.join(a.cert, "joined_delta.tsv")) else set()
    ck = collections.Counter()
    for p in cert:
        by = int(p[1])
        ck[("joined" if p[0] in joined else "plain", p[4], group(F, by))] += 1
    out = {"items_by_tier": dict(total_items), "reading_by_tier": {k: dict(v) for k, v in packs.items()},
           "packs_answered": len(answered_packs), "packs_answered_list": answered_packs,
           "rows_by_rule_kind": {"%s|%s" % k: v for k, v in sorted(rc.items())},
           "certified": len(cert), "certified_joined": sum(1 for p in cert if p[0] in joined),
           "certified_by_form_kind_group": {"%s|%s|%s" % k: v for k, v in sorted(ck.items())},
           "certified_by_kind": dict(collections.Counter(p[4] for p in cert)),
           "certified_by_group": dict(collections.Counter(group(F, int(p[1])) for p in cert)),
           "certified_by_scope": dict(collections.Counter(p[5] for p in cert))}
    with open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "packs_answered_list"}, indent=1))


if __name__ == "__main__":
    main()
