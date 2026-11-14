#!/usr/bin/env python3
"""Parse the Beim-Hirsch-Kastellec main data file into work/items.tsv (MAPPING.md, Unit). Run with python -I.

Reads : raw/bhk_zip_x/bhk_main_data.csv (untrusted; parsed as text only)
Writes: work/items.tsv   one row per en banc row (source_of_cases bhk_ebs / clark_ebs)
        work/source_profile.json   marginal counts
"""
import collections
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "bhk_zip_x", "bhk_main_data.csv")
WORK = os.path.join(HERE, "work")


def ymd(y, m, d):
    try:
        y, m, d = int(float(y)), int(float(m)), int(float(d))
    except ValueError:
        return "-"
    if not (1900 < y < 2100 and 1 <= m <= 12 and 1 <= d <= 31):
        return "-"
    return "%04d%02d%02d" % (y, m, d)


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\t", " ")).strip()


def main():
    os.makedirs(WORK, exist_ok=True)
    with open(SRC, encoding="latin-1", newline="") as f:
        rows = list(csv.DictReader(f))
    prof = {"rows": len(rows),
            "source_x_grant_x_reverse": dict(collections.Counter(
                "%s|%s|%s" % (r["source_of_cases"], r["eb_grant"], r["eb_reverse"]) for r in rows)),
            }
    cols = ["uid", "unique_id_new", "source", "circuit", "p_cite", "p_date", "p_year", "eb_cite", "eb_date", "eb_year", "eb_reverse",
            "sub", "mult_panel", "songer_casenum", "note"]
    out = []
    for rownum, r in enumerate(rows, 1):  # uid = data row number (unique_id_new repeats once: id 203, rows 792/797)
        if r["source_of_cases"] not in ("bhk_ebs", "clark_ebs"):
            continue
        assert r["eb_grant"] == "1", r["unique_id_new"]
        rev = r["eb_reverse"].strip()
        sub = {"1": "R", "0": "S"}.get(rev, "U")
        note = " / ".join(x for x in (clean(r["bhk_notes_from_ue_coding"]), clean(r["notes_on_clark_ebs"]),
                                      clean(r["bhk_notes_votes_coding"])) if x and x != ".")
        out.append({
            "uid": "row%d" % rownum, "unique_id_new": r["unique_id_new"].strip() or "-", "source": r["source_of_cases"], "circuit": r["circuit"].strip(),
            "p_cite": clean(r["p_cite"]) or "-", "p_date": ymd(r["p_year"], r["p_month"], r["p_day"]),
            "p_year": r["p_year"].strip() or "-",
            "eb_cite": clean(r["eb_cite"]).rstrip(".") or "-", "eb_date": ymd(r["eb_year"], r["eb_month"], r["eb_day"]),
            "eb_year": r["eb_year"].strip() or "-", "eb_reverse": rev or "-", "sub": sub,
            "mult_panel": r["mult_panel"].strip() or "-", "songer_casenum": r["casenum_songer_original"].strip() or "-",
            "note": note[:300] or "-",
        })
    uids = collections.Counter(o["uid"] for o in out)
    assert max(uids.values()) == 1, "duplicate uid"
    prof["unique_id_new_repeated"] = sorted(k for k, v in collections.Counter(o["unique_id_new"] for o in out).items()
                                            if v > 1)
    with open(os.path.join(WORK, "items.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in out:
            o.write("\t".join(str(r[c]) for c in cols) + "\n")
    prof.update({
        "items": len(out),
        "by_source": dict(collections.Counter(r["source"] for r in out)),
        "by_sub": dict(collections.Counter(r["sub"] for r in out)),
        "by_circuit": dict(collections.Counter(r["circuit"] for r in out)),
        "songer_casenum_present": sum(r["songer_casenum"] != "-" for r in out),
        "p_date_missing": sum(r["p_date"] == "-" for r in out),
        "eb_date_missing": sum(r["eb_date"] == "-" for r in out),
    })
    with open(os.path.join(WORK, "source_profile.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(prof, o, indent=1)
        o.write("\n")
    print(json.dumps(prof, indent=1))


if __name__ == "__main__":
    main()
