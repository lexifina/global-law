#!/usr/bin/env python3
"""Parse the Federal Circuit Dataset Project document file into work/fc_docs.tsv (source only; run with python -I).

One output row per source document (uniqueID), with the class of MAPPING.md and the key-item flag.
"""
import collections
import csv
import os
import re
import sys

csv.field_size_limit(10 ** 8)
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "docs_2025_12_31", "cafc_documents_2025-12-31.tab")

CLASS = {"Reversed": "NEG", "Vacated": "NEG", "Affirmed-in-part": "PART", "Affirmed": "CLEAN"}
DOCTYPES = {"Opinion", "Rule 36", "Rule 36 Judgment", "Order - Merits"}
ORIGINS = {"DCT", "CFC", "CIT", "CAVC"}


def ymd(s):
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2,4})\s*$", s or "")
    if not m:
        return "-"
    mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100:
        y += 2000 if y < 50 else 1900
    return "%04d%02d%02d" % (y, mo, d)


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\t", " ")).strip() or "-"


def main():
    out = os.path.join(HERE, "work", "fc_docs.tsv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n = 0
    cnt = collections.Counter()
    cols = ["uid", "case_name", "appeal", "origin", "trib", "prec", "doc_date", "doc_type", "en_banc", "disp",
            "replaced", "full_cite", "orig_dockets", "data_source", "class", "key_item", "excl_reason"]
    with open(SRC, encoding="utf-8", errors="replace", newline="") as f, \
            open(out, "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in csv.DictReader(f, delimiter="\t"):
            n += 1
            cls = CLASS.get(r["DispGeneral"].strip(), "OTHER")
            reason = ""
            if r["origin"].strip() not in ORIGINS:
                reason = "origin_not_in_scope"
            elif r["docType"].strip() not in DOCTYPES:
                reason = "doctype_not_merits"
            elif cls == "OTHER":
                reason = "disp_not_scored"
            elif r["Replaced"].strip():
                reason = "cafc_doc_replaced"
            elif ymd(r["docDate"]) == "-":
                reason = "no_date"
            key = int(not reason)
            cnt[(key, reason, cls)] += 1
            o.write("\t".join([
                clean(r["uniqueID"]), clean(r["caseName"]), clean(r["appealNumber"]), clean(r["origin"]),
                clean(r["TribOfOrigin"]), clean(r["PrecedentialStatus"]), ymd(r["docDate"]), clean(r["docType"]),
                clean(r["enBanc"]), clean(r["DispGeneral"]), clean(r["Replaced"]), clean(r["Full_Cite"]),
                clean(r["Orig_Trib_Dockets"]), clean(r["DataSource"]), cls, str(key), reason or "-"]) + "\n")
    print("documents", n)
    for k, v in sorted(cnt.items()):
        print(k, v)


if __name__ == "__main__":
    main()
