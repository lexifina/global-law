#!/usr/bin/env python3
"""Parse the Shadow Docket CSV (untrusted; run with `python -I parse.py <csv>`) into work/orders.tsv.

One output row per CSV row (one docket x one order action). Columns kept: row index, docket_number, term, date,
action_class, relief, cert_granted, non_case, lower_ct, lower_docket, petitioner, respondent, action_text (clipped).
Also prints the marginal counts used to write MAPPING.md (work/profile.txt).
"""
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "work")
KEEP = ["docket_number", "term", "date", "action_class", "relief", "cert_granted", "non_case", "lower_ct",
        "lower_docket", "petitioner", "respondent"]


def cl(s, n=None):
    s = (s or "").replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()
    return s[:n] if n else s


def main():
    csv.field_size_limit(1 << 30)
    os.makedirs(OUT, exist_ok=True)
    prof = collections.Counter()
    ac_rel = collections.Counter()
    ac_year = collections.defaultdict(collections.Counter)
    lower = collections.Counter()
    with open(sys.argv[1], encoding="utf-8", errors="replace", newline="") as f, \
            open(os.path.join(OUT, "orders.tsv"), "w", encoding="utf-8", newline="\n") as o:
        r = csv.DictReader(f)
        o.write("row\t" + "\t".join(KEEP) + "\taction_text\n")
        for i, row in enumerate(r):
            o.write(str(i) + "\t" + "\t".join(cl(row.get(k)) for k in KEEP) + "\t" + cl(row.get("action_text"), 700) + "\n")
            ac = row.get("action_class")
            prof["rows"] += 1
            ac_rel[(ac, row.get("relief"))] += 1
            ac_year[ac][(row.get("term") or "")] += 1
            lower[(ac, row.get("lower_docket") not in (None, "", "NA"))] += 1
    with open(os.path.join(OUT, "profile.txt"), "w", encoding="utf-8", newline="\n") as p:
        p.write("rows %d\n\naction_class x relief\n" % prof["rows"])
        for (a, rl), n in sorted(ac_rel.items(), key=lambda x: -x[1]):
            p.write("%s\t%s\t%d\n" % (a, rl, n))
        p.write("\naction_class x has lower_docket\n")
        for (a, h), n in sorted(lower.items(), key=lambda x: -x[1]):
            p.write("%s\t%s\t%d\n" % (a, h, n))
        p.write("\naction_class x term\n")
        for a in sorted(ac_year, key=lambda x: str(x)):
            p.write("%s\t%s\n" % (a, " ".join("%s:%d" % kv for kv in sorted(ac_year[a].items()))))
    print("rows", prof["rows"])


if __name__ == "__main__":
    main()
