#!/usr/bin/env python3
"""Parse the Brace & Hall case file (Dataverse tab export) into work/bh_cases.tsv.

Run with `python -I parse_source.py` (the input is an untrusted download; nothing in raw/ is imported).

Input : raw/case_tab_tsv/NSF95-98_beta_July2005.tsv (Dataverse tab export of file 656541, Latin-1 text)
Output: work/bh_cases.tsv, one row per source record (row = 1-based data row number in the input file)

Columns: row, masterid, id_1, state_code, state, title_p1, title_p2, docket, docket_n, reporter, cite, decs_date,
         juris, first_ct, rev_ct, genissue, disp_vars (var=code;...), disp_codes, class
class (MAPPING.md): NEG (2, 3), PART (4, 5), CLEAN (1), OTHER (6, 7, 55, 88, undefined, none).
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "case_tab_tsv", "NSF95-98_beta_July2005.tsv")
WORK = os.path.join(HERE, "work")

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
          "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
          "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
          "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
          "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
          "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
          "West Virginia", "Wisconsin", "Wyoming"]
# reporter code -> normalised reporter (all regional reporters were in their 2d series in 1995-1998)
REPORTER = {"1": "a2d", "2": "ne2d", "3": "nw2d", "4": "p2d", "5": "se2d", "6": "so2d", "7": "sw2d"}
DISP_VARS = {"1": "ca_disp", "2": "cg_disp", "3": "cp_disp", "4": "jv_disp"}
CODE_CLASS = {"1": "CLEAN", "2": "NEG", "3": "NEG", "4": "PART", "5": "PART"}


def combine(classes):
    """FJC-style combination of several scored classes (MAPPING.md)."""
    sc = [c for c in classes if c in ("NEG", "PART", "CLEAN")]
    if not sc:
        return "OTHER"
    if all(c == "NEG" for c in sc):
        return "NEG"
    if all(c == "CLEAN" for c in sc):
        return "CLEAN"
    return "PART"


def num(s):
    s = (s or "").strip()
    return int(s) if s.isdigit() else None


def main():
    os.makedirs(WORK, exist_ok=True)
    cols = ["row", "masterid", "id_1", "state_code", "state", "title_p1", "title_p2", "docket", "docket_n",
            "reporter", "cite", "decs_date", "juris", "first_ct", "rev_ct", "genissue", "disp_vars", "disp_codes",
            "class"]
    n = 0
    with open(SRC, encoding="latin-1", newline="") as f, \
            open(os.path.join(WORK, "bh_cases.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for i, r in enumerate(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE), 1):
            sc = num(r["state_2"])
            state = STATES[sc - 1] if sc and 1 <= sc <= 50 else "-"
            rep = REPORTER.get(r["reporter"].strip())
            vol, page = num(r["rep_vol"]), num(r["rep_page"])
            cite = "%d %s %d" % (vol, rep, page) if rep and vol and page else "-"
            y, m, d = num(r["decs_yr"]), num(r["decs_mo"]), num(r["decs_day"])
            date = "%04d%02d%02d" % (y, m, d) if y and 1990 <= y <= 1999 and m and m <= 12 and d and d <= 31 else "-"
            present = [(v, r[v].strip()) for v in ("ca_disp", "cp_disp", "cg_disp", "jv_disp")
                       if r[v].strip() not in ("", "NA")]
            own = DISP_VARS.get(r["genissue"].strip())
            if own and any(v == own for v, _ in present):
                use = [(v, c) for v, c in present if v == own]
            else:
                use = present
            cls = combine([CODE_CLASS.get(c, "OTHER") for _, c in use]) if use else "OTHER"
            clean = lambda s: " ".join((s or "").replace("\t", " ").split())  # noqa: E731
            o.write("\t".join([str(i), clean(r["masterid"]), clean(r["id_1"]), str(sc or "-"), state,
                               clean(r["title_p1"]) or "-", clean(r["title_p2"]) or "-", clean(r["docket"]) or "-",
                               clean(r["docket_n"]) or "-", rep or "-", cite, date, clean(r["juris"]) or "-",
                               clean(r["first_ct"]) or "-", clean(r["rev_ct"]) or "-", clean(r["genissue"]) or "-",
                               ";".join("%s=%s" % vc for vc in present) or "-",
                               ";".join(c for _, c in use) or "-", cls]) + "\n")
            n += 1
    print("records", n)


if __name__ == "__main__":
    sys.exit(main())
