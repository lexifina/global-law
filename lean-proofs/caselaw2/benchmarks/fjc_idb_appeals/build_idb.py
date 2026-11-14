#!/usr/bin/env python3
"""Join the CCAD idb_crosswalk to the FJC IDB appeals rows (run with python -I; raw files are untrusted text).

Inputs (raw/, read only):
  raw/ccad_idb_crosswalk/idb_crosswalk.tab   caseid, idb_idx (<file>:<0-based data row>), circuit, docket, dktdate, ...
  raw/idb_ap71to07_x/ap71to07.txt            FJC IDB appeals SY1971-FY2007 (tab-delimited, header line)
  raw/idb_ap08on_x/ap08on.txt                FJC IDB appeals FY2008-June 2026
Outputs (work/):
  idb_xw.tsv          one line per (caseid, idb row) in the crosswalk (alt rows included), with the IDB fields used
  ddocket_appeals.tsv every IDB row with a district docket: ddist, ddocket, appdate, judgdate, idb_idx (all appeals,
                      linked or not; used to bound the date window by an earlier appeal from the same district docket)
  idb_stats.json      counts, natural-key check
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
WORK = os.path.join(HERE, "work")
FILES = {"ap71to07": os.path.join(RAW, "idb_ap71to07_x", "ap71to07.txt"),
         "ap08on": os.path.join(RAW, "idb_ap08on_x", "ap08on.txt")}
KEEP = ["CIRCUIT", "DOCKET", "REOPEN", "DKTDATE", "APPELLAN", "APPELLEE", "APPTYPE", "DCIRC", "DDIST", "DOFFICE",
        "DDOCKET", "DDEFNUM", "DDKTDATE", "APPDATE", "DISP", "OUTCOME", "PROCTERM", "PUBSTAT", "JOINAPP", "CONSDKT",
        "JUDGDATE", "TAPEYEAR", "ENBANC", "OPINION"]


def mdy(s):
    """mm/dd/yyyy -> yyyymmdd int (0 if missing / 01/01/1900)."""
    s = s.strip()
    if len(s) != 10 or s[2] != "/" or s[5] != "/":
        return 0
    try:
        v = int(s[6:10]) * 10000 + int(s[0:2]) * 100 + int(s[3:5])
    except ValueError:
        return 0
    return 0 if v <= 19000101 else v


def main():
    os.makedirs(WORK, exist_ok=True)
    xw = []
    need = collections.defaultdict(set)
    with open(os.path.join(RAW, "ccad_idb_crosswalk", "idb_crosswalk.tab"), encoding="utf-8", newline="") as f:
        head = f.readline().rstrip("\r\n").split(",")
        assert head[:8] == ["caseid", "idb_idx", "circuit", "docket", "dktdate", "reopen", "tapeyear", "idb_alt_rows"], head
        for line in f:
            p = line.rstrip("\r\n").split(",")
            alts = [a for a in p[7].split(";") if a] if len(p) > 7 else []
            xw.append((p[0], p[1], p[2], p[3], p[4], p[5], p[6], alts))
            for ix in [p[1]] + alts:
                fn, row = ix.split(":")
                need[fn].add(int(row))
    stats = collections.Counter()
    rows = {}
    nkey = collections.defaultdict(list)  # natural key -> [idb_idx]  (CCAD codebook: use it if the file changed)
    dd = open(os.path.join(WORK, "ddocket_appeals.tsv"), "w", encoding="utf-8", newline="\n")
    for fn, path in FILES.items():
        with open(path, encoding="latin-1", newline="") as f:
            hdr = f.readline().rstrip("\r\n").split("\t")
            col = {h: i for i, h in enumerate(hdr)}
            for i, line in enumerate(f):
                p = line.rstrip("\r\n").split("\t")
                g = lambda k: (p[col[k]].strip() if k in col and col[k] < len(p) else "")
                stats["idb_rows_" + fn] += 1
                ddist, ddocket = g("DDIST"), g("DDOCKET")
                if ddist not in ("", "-8") and ddocket not in ("", "-8", "0000000") and len(ddocket) == 7 and ddocket.isdigit():
                    dd.write("\t".join([ddist, ddocket, str(mdy(g("APPDATE"))), str(mdy(g("JUDGDATE"))),
                                        "%s:%d" % (fn, i), g("CIRCUIT"), g("DOCKET")]) + "\n")
                nkey[(fn, g("CIRCUIT"), g("DOCKET"), g("DKTDATE"), g("REOPEN"), g("TAPEYEAR"))].append("%s:%d" % (fn, i))
                if i in need[fn] or fn == "ap08on":  # ap08on kept whole: natural-key fallback may need any row
                    rows["%s:%d" % (fn, i)] = tuple(g(k) for k in KEEP)
    dd.close()
    out = open(os.path.join(WORK, "idb_xw.tsv"), "w", encoding="utf-8", newline="\n")
    cols = ["caseid", "idb_idx", "alt"] + KEEP
    out.write("\t".join(cols) + "\n")
    for caseid, ix, circ, dkt, dktdate, reopen, tape, alts in xw:
        stats["xw_caseids"] += 1
        r = rows.get(ix)
        if r is None:
            stats["xw_idx_missing"] += 1
            continue
        K = {k: i for i, k in enumerate(KEEP)}
        ok = (r[K["CIRCUIT"]] == circ and r[K["DOCKET"]] == dkt and r[K["DKTDATE"]] == dktdate
              and r[K["TAPEYEAR"]] == tape)
        stats["natural_key_ok" if ok else "natural_key_mismatch"] += 1
        if not ok:
            # the cumulative FY2008+ file is re-issued quarterly, so row numbers move: resolve by natural key
            cand = nkey.get((ix.split(":")[0], circ, dkt, dktdate, reopen, tape), [])
            if len(cand) != 1:
                stats["natural_key_unresolved"] += 1
                continue
            stats["natural_key_resolved"] += 1
            ix = cand[0]
            alts = []
        for j, x in enumerate([ix] + alts):
            rr = rows.get(x)
            if rr is None:
                stats["alt_idx_missing"] += 1
                continue
            vals = [caseid, x, "1" if j else "0"] + [v.replace("\t", " ") for v in rr]
            out.write("\t".join(vals) + "\n")
            stats["xw_rows_written"] += 1
    out.close()
    with open(os.path.join(WORK, "idb_stats.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(stats), f, indent=1, sort_keys=True)
    print(json.dumps(dict(stats), indent=1, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
