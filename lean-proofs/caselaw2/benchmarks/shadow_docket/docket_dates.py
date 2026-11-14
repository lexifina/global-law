#!/usr/bin/env python3
"""Extract lower-court decision dates from the deposited Supreme Court docket pages (untrusted JSON).

Run: python -I docket_dates.py <out tsv> <json> [<json> ...]
Each JSON maps a Supreme Court docket number to the text of its docket page. From each page: `Lower Ct:`,
`Case Nos.:` / `Case Numbers:`, `Decision Date:`, `Rehearing Denied:`, `Discretionary Court Decision Date:`.
Output columns: sc_docket, lower_ct, case_numbers, decision_date, rehearing_denied, discretionary_date, file.
Dates yyyymmdd (0 if absent or unparseable). Later files override earlier ones only where they have a decision date.
"""
import datetime
import json
import os
import re
import sys

MON = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                         "september", "october", "november", "december"])}
SP = r"[\s ]*"


def field(t, names):
    for nm in names:
        m = re.search(nm + SP + r":" + SP + r"([^\n]*(?:\n[^\n]*)?)", t)
        if m:
            return re.sub(r"\s+", " ", m.group(1).replace(" ", " ")).strip()
    return ""


def date_of(t, names):
    for nm in names:
        m = re.search(nm + SP + r":" + SP + r"([A-Z][a-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", t)
        if m and m.group(1).lower() in MON:
            try:
                return datetime.date(int(m.group(3)), MON[m.group(1).lower()], int(m.group(2))).strftime("%Y%m%d")
            except ValueError:
                return "0"
    return "0"


def main():
    out = sys.argv[1]
    rows = {}
    for path in sys.argv[2:]:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for k, t in d.items():
            if not isinstance(t, str):
                continue
            dk = re.sub(r"[‐-―]", "-", k).strip()
            lct = field(t, [r"Lower Ct"]).split("  ")[0][:200]
            lct = re.split(r"\s(?:Case Nos?\.|Case Numbers)", lct)[0].strip()
            cn = ""
            m = re.search(r"Case (?:Nos?\.|Numbers)" + SP + r":" + SP + r"(\([^)]*\))", t)
            if m:
                cn = re.sub(r"\s+", " ", m.group(1))[:300]
            dd = date_of(t, [r"(?<!Court )Decision Date"])
            rh = date_of(t, [r"Rehearing Denied"])
            ds = date_of(t, [r"Discretionary Court Decision Date"])
            if dk in rows and dd == "0":
                continue
            rows[dk] = [dk, lct, cn, dd, rh, ds, os.path.basename(path)]
        del d
    with open(out, "w", encoding="utf-8", newline="\n") as o:
        o.write("sc_docket\tlower_ct\tcase_numbers\tdecision_date\trehearing_denied\tdiscretionary_date\tfile\n")
        for r in rows.values():
            o.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    n = len(rows)
    nd = sum(1 for r in rows.values() if r[3] != "0")
    print("dockets", n, "with decision date", nd)


if __name__ == "__main__":
    main()
