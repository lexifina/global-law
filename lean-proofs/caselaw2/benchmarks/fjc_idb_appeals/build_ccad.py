#!/usr/bin/env python3
"""Extract the few CCAD columns needed for linking (run with python -I; the file is untrusted).

Input:  raw/ccad_main/ccad_09-2026.csv.gz
Output: work/ccad_cases.tsv  caseid, source, citation, docket_number, circuit, decision_date (yyyymmdd), is_enbanc
        (only caseids present in the idb_crosswalk)
"""
import csv
import gzip
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
COLS = ["caseid", "source", "citation", "docket_number", "circuit", "decision_date", "is_enbanc"]


def ymd(s):
    m = re.match(r"^\s*(\d{4})-(\d{2})-(\d{2})", s or "")
    return int(m.group(1) + m.group(2) + m.group(3)) if m else 0


def main():
    csv.field_size_limit(1 << 30)
    need = set()
    with open(os.path.join(WORK, "idb_xw.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            need.add(line.split("\t", 1)[0])
    n = k = 0
    with gzip.open(os.path.join(HERE, "raw", "ccad_main", "ccad_09-2026.csv.gz"), "rt", encoding="utf-8",
                   newline="") as f, open(os.path.join(WORK, "ccad_cases.tsv"), "w", encoding="utf-8",
                                          newline="\n") as o:
        r = csv.reader(f)
        hdr = next(r)
        col = {h: i for i, h in enumerate(hdr)}
        missing = [c for c in COLS if c not in col]
        if missing:
            print("missing columns", missing, "header starts", hdr[:20])
            return 1
        o.write("\t".join(COLS) + "\n")
        for row in r:
            n += 1
            cid = row[col["caseid"]]
            if cid not in need:
                continue
            vals = [row[col[c]].replace("\t", " ").replace("\n", " ") for c in COLS]
            vals[5] = str(ymd(vals[5]))
            o.write("\t".join(vals) + "\n")
            k += 1
    print("ccad rows", n, "kept", k, "of crosswalk caseids", len(need))


if __name__ == "__main__":
    sys.exit(main())
