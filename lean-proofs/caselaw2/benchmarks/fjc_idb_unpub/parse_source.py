#!/usr/bin/env python3
"""Source side: FJC IDB appeal records that the CCAD idb_crosswalk does NOT attach to any published opinion.

Run with python -I (raw files are untrusted text; the zips are read in place, never extracted).
Inputs (raw/, read only):
  raw/ccad_idb_crosswalk/idb_crosswalk.tab   caseid, idb_idx (<file>:<0-based data row>), circuit, docket, dktdate,
                                             reopen, tapeyear, idb_alt_rows
  raw/idb_ap71to07/ap71to07.zip              FJC IDB appeals SY1971-FY2007 (one tab-delimited text member)
  raw/idb_ap08on/ap08on_0.zip                FJC IDB appeals FY2008-June 2026
Outputs (work/):
  idb_resid.tsv       every IDB row NOT crosswalked (MAPPING.md 'Unit'), with the fields used
  excl_dockets.tsv    (DDIST, DDOCKET) of every crosswalked row and every published-PUBSTAT row (node exclusion)
  ddocket_appeals.tsv every IDB row with a district docket (earlier-appeal date bound, as fjc_idb_appeals)
  source_stats.json   counts
"""
import collections
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
WORK = os.path.join(HERE, "work")
FILES = {"ap71to07": os.path.join(RAW, "idb_ap71to07", "ap71to07.zip"),
         "ap08on": os.path.join(RAW, "idb_ap08on", "ap08on_0.zip")}
KEEP = ["CIRCUIT", "DOCKET", "REOPEN", "DKTDATE", "APPELLAN", "APPELLEE", "APPTYPE", "DDIST", "DDOCKET",
        "DDKTDATE", "APPDATE", "DISP", "OUTCOME", "PUBSTAT", "JUDGDATE", "TAPEYEAR", "ENBANC"]
PUBLISHED = {"2", "4", "6"}


def mdy(s):
    s = s.strip()
    if len(s) != 10 or s[2] != "/" or s[5] != "/":
        return 0
    try:
        v = int(s[6:10]) * 10000 + int(s[0:2]) * 100 + int(s[3:5])
    except ValueError:
        return 0
    return 0 if v <= 19000101 else v


def lines_of(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        assert len(names) == 1, names
        with z.open(names[0]) as b:
            yield from io.TextIOWrapper(b, encoding="latin-1", newline="")


def main():
    os.makedirs(WORK, exist_ok=True)
    xw_idx = set()
    xw_nkey = set()
    with open(os.path.join(RAW, "ccad_idb_crosswalk", "idb_crosswalk.tab"), encoding="utf-8", newline="") as f:
        head = f.readline().rstrip("\r\n").split(",")
        assert head[:8] == ["caseid", "idb_idx", "circuit", "docket", "dktdate", "reopen", "tapeyear",
                            "idb_alt_rows"], head
        for line in f:
            p = line.rstrip("\r\n").split(",")
            alts = [a for a in p[7].split(";") if a] if len(p) > 7 else []
            for ix in [p[1]] + alts:
                xw_idx.add(ix)
            xw_nkey.add((p[1].split(":")[0], p[2], p[3], p[4], p[5], p[6]))
    st = collections.Counter()
    st["xw_idx_refs"] = len(xw_idx)
    excl = set()
    res = open(os.path.join(WORK, "idb_resid.tsv"), "w", encoding="utf-8", newline="\n")
    res.write("\t".join(["idb_idx"] + KEEP) + "\n")
    dd = open(os.path.join(WORK, "ddocket_appeals.tsv"), "w", encoding="utf-8", newline="\n")
    for fn, path in FILES.items():
        it = lines_of(path)
        hdr = next(it).rstrip("\r\n").split("\t")
        col = {h.strip(): i for i, h in enumerate(hdr)}
        st["has_PUBSTAT_" + fn] = int("PUBSTAT" in col)
        for i, line in enumerate(it):
            p = line.rstrip("\r\n").split("\t")
            g = lambda k: (p[col[k]].strip() if k in col and col[k] < len(p) else "")
            st["rows_" + fn] += 1
            ix = "%s:%d" % (fn, i)
            ddist, ddocket = g("DDIST"), g("DDOCKET")
            good_dk = ddist not in ("", "-8") and len(ddocket) == 7 and ddocket.isdigit() and ddocket != "0000000"
            if good_dk:
                dd.write("\t".join([ddist, ddocket, str(mdy(g("APPDATE"))), str(mdy(g("JUDGDATE"))), ix,
                                    g("CIRCUIT"), g("DOCKET")]) + "\n")
            nk = (fn, g("CIRCUIT"), g("DOCKET"), g("DKTDATE"), g("REOPEN"), g("TAPEYEAR"))
            # conservative: a row is 'crosswalked' if the crosswalk names its row number OR its natural key
            xw = ix in xw_idx or nk in xw_nkey
            pub = g("PUBSTAT") in PUBLISHED
            if xw or pub:
                st["crosswalked" if xw else "published_not_crosswalked"] += 1
                if good_dk:
                    excl.add((ddist, ddocket))
                continue
            st["resid_" + fn] += 1
            res.write("\t".join([ix] + [g(k).replace("\t", " ") for k in KEEP]) + "\n")
    res.close()
    dd.close()
    with open(os.path.join(WORK, "excl_dockets.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for k in sorted(excl):
            o.write("%s\t%s\n" % k)
    st["excl_dockets"] = len(excl)
    with open(os.path.join(WORK, "source_stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(st), f, indent=1, sort_keys=True)
    print(json.dumps(dict(st), indent=1, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
