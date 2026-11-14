"""diag2 reading aid: everything known about one pair before reading.

    python show.py <idx>              pair line, the model's rows (kind, scope, quote), later-statement candidates
    python show.py <idx> -n 40        more candidates per type (default 14 'both', 6 'weakx', 4 'weaky')
    python show.py <idx> -all         include candidates in dissents / concurrences / head matter
    python show.py -s <shard>         the idx list of a shard
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(fn):
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a and a[0] == "-s":
        for r in rows("pairs.tsv"):
            if r.get("shard") == a[1]:
                print(r["idx"], r["outcome"], r["by_node"], r["target_node"], r["label"], "=>", r["target_name"])
        return
    idx = a[0]
    n = int(a[a.index("-n") + 1]) if "-n" in a else None
    allp = "-all" in a
    pr = [r for r in rows("pairs.tsv") if r["idx"] == idx][0]
    print("PAIR idx=%s pair_id=%s outcome=%s shard=%s" % (idx, pr["pair_id"], pr["outcome"], pr.get("shard", "")))
    print("  Y %s  %s, %s (%s)" % (pr["by_node"], pr["label"], pr["by_cite"], pr["by_date"]))
    print("  X %s  %s, %s (%s)" % (pr["target_node"], pr["target_name"], pr["target_cite"], pr["target_date"]))
    print("  key: partial=%s implied=%s | %s" % (pr["partial"], pr["implied"], pr["explicit_hint"]))
    print("  key note: %s" % pr["key_note"])
    print("  baseline: status=%s actor=%s at_risk=%s reader_rows=%s" % (pr["model_status"], pr["model_actor"],
                                                                        pr["at_risk"], pr["reader_rows"]))
    mr = [r for r in rows("model_rows.tsv") if r["idx"] == idx]
    print("MODEL ROWS (data/treatments.tsv, by=Y target=X): %d" % len(mr))
    for r in mr:
        print("  %s kind=%s scope=%s explicit=%s part=%s @%s-%s reader=%s witness=%s by_ev=%s" % (
            r["id"], r["kind"], r["scope"], r["explicit"], r["part"], r["start"], r["end"], r["reader"],
            r["witness_node"] or "-", r["by_evidence"] or "-"))
        print("     quote: %s" % r["quote"])
        print("     target_evidence: %s" % r["target_evidence"])
    cs = [r for r in rows("later_cands.tsv") if r["idx"] == idx]
    sep = ("dissent", "concur", "head")
    for typ, dflt in (("both", 14), ("weakx", 6), ("weaky", 4)):
        c = [r for r in cs if r["type"] == typ]
        maj = [r for r in c if not r["part"].lower().startswith(sep)]
        use = c if allp else maj
        k = n or dflt
        print("LATER %s: %d candidates (%d not in a separate opinion / head matter); showing %d earliest%s" % (
            typ, len(c), len(maj), min(k, len(use)), "" if allp else " of those"))
        for r in use[:k]:
            print("  W %s %s %s [%s] @%s refs=%s yform=%s" % (r["w_node"], r["w_date"], r["w_name"][:50], r["part"],
                                                              r["offset"], r["refs"], r["yform"]))
            print("     %s" % r["span"])


if __name__ == "__main__":
    main()
