#!/usr/bin/env python3
"""Pool work/orders.tsv rows into one item per Supreme Court docket with its MAPPING.md class.

Writes work/items.tsv: sc_docket, class, sub, order_date (yyyymmdd of the deciding order: first NEG/PART row, else the
last CLEAN row, else the last row), first_date, lower_ct, lower_docket (distinct non-NA values joined by ' || '),
caption, n_rows, action_classes, order_text (clipped).
No model file is read.
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "work")
VAC = re.compile(r"judgments?[^.]{0,250}?vacated")


def d8(s):
    s = (s or "").strip()
    return s.replace("-", "") if re.match(r"^\d{4}-\d\d-\d\d$", s) else "0"


def compact(s):
    return re.sub(r"\s+", "", (s or "").lower())


def row_tag(r):
    a, rel = r["action_class"], r["relief"]
    if a == "GVR":
        return ("NEG", "gvr")
    if a == "Vacate and Remand" and rel in ("NA", "Granted"):
        return ("NEG", "vacated")
    if a in ("Vacate", "Remand") and rel in ("NA", "Granted") and VAC.search(compact(r["action_text"])):
        return ("NEG", "vacated")
    if a == "Reversal":
        return ("NEG", "reversed")
    if a == "Affirmed in Part":
        return ("PART", "affirmed_in_part")
    if a == "DIG":
        return ("DIG", "dig")
    if (a == "Certiorari" and rel == "Granted") or a in ("Probable Jurisdiction", "Jurisdiction Postponed"):
        return ("MERITS", "merits")
    if a == "Rehearings" and rel == "Granted":
        return ("AMBIG", "rehearing_granted")
    if a == "Certiorari" and rel == "Denied":
        return ("CLEAN", "cert_denied")
    if (a == "Certiorari" and rel == "Dismissed") or (a == "Dismiss" and rel == "NA"):
        return ("CLEAN", "cert_dismissed")
    if a in ("Affirmed", "Lack of Quorum"):
        return ("CLEAN", "affirmed")
    return None


def main():
    g = collections.OrderedDict()
    with open(os.path.join(W, "orders.tsv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["non_case"] == "1":
                continue
            g.setdefault(r["docket_number"], []).append(r)
    stat = collections.Counter()
    with open(os.path.join(W, "items.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("sc_docket\tclass\tsub\torder_date\tfirst_date\tlower_ct\tlower_docket\tcaption\tn_rows\t"
                "action_classes\torder_text\n")
        for dk, rows in g.items():
            rows.sort(key=lambda r: (d8(r["date"]), int(r["row"])))
            tags = [(row_tag(r), r) for r in rows]
            tags = [(t, r) for t, r in tags if t]
            kinds = [t[0] for t, _ in tags]
            cls, sub, dec = "OTHER", "-", None
            if "NEG" in kinds:
                t, dec = next((t, r) for t, r in tags if t[0] == "NEG")
                cls, sub = t
            elif "PART" in kinds:
                t, dec = next((t, r) for t, r in tags if t[0] == "PART")
                cls, sub = t
            elif "DIG" in kinds:
                t, dec = next((t, r) for t, r in tags if t[0] == "DIG")
                cls, sub = "CLEAN", "dig"
            elif "MERITS" in kinds:
                t, dec = next((t, r) for t, r in tags if t[0] == "MERITS")
                cls, sub = t
            elif "AMBIG" in kinds:
                t, dec = next((t, r) for t, r in tags if t[0] == "AMBIG")
                cls, sub = t
            elif "CLEAN" in kinds:
                t, dec = [(t, r) for t, r in tags if t[0] == "CLEAN"][-1]
                cls, sub = t
            if dec is None:
                dec = rows[-1]
            lct = []
            ldk = []
            for r in rows:
                if r["lower_ct"] not in ("", "NA") and r["lower_ct"] not in lct:
                    lct.append(r["lower_ct"])
                if r["lower_docket"] not in ("", "NA") and r["lower_docket"] not in ldk:
                    ldk.append(r["lower_docket"])
            cap = "%s v. %s" % (dec["petitioner"], dec["respondent"])
            acs = ",".join(sorted({"%s/%s" % (r["action_class"], r["relief"]) for r in rows}))
            o.write("\t".join([dk, cls, sub, d8(dec["date"]), d8(rows[0]["date"]), " || ".join(lct) or "NA",
                               " || ".join(ldk) or "NA", cap, str(len(rows)), acs, dec["action_text"][:500]]) + "\n")
            stat[(cls, sub, bool(ldk))] += 1
    for k, v in sorted(stat.items(), key=lambda x: -x[1]):
        print(k, v)


if __name__ == "__main__":
    sys.exit(main())
