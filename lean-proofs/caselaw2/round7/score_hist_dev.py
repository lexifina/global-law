#!/usr/bin/env python3
"""Round 7: score a model output against the DEV half of the Shepardized cases (round6/history/score_dev.py on
round-7 paths; round 6 files are not changed).

  python -I round7/score_hist_dev.py <name> [--out DIR] [--data DIR] [--res DIR] [--asof YYYYMMDD] [--tables]

  <name>   model output round7/out/<name>/ (status.tsv, certs.tsv) built from round7/stage/<name>/ (history.tsv);
           results go to round7/results/<name>/shepardized/
Runs round6/shepardized/compare.py --split dev (the sealed half is never read) and writes, in the results folder:
  tables.tsv, headline.tsv, cases_dev.tsv, dev_misses.tsv (dev NEG / PART cases not matched), dev_fp.tsv (dev CLEAN /
  MOD cases shown negative for a same-case reason, with the model's actor and history row id).
Standard library only.
"""
import argparse
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
COMPARE = os.path.join(C2, "round6", "shepardized", "compare.py")
DEV_CAUSES = os.path.join(C2, "round6", "history", "split", "dev_causes.tsv")


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def write(path, cols, recs):
    with open(path, "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in recs:
            o.write("\t".join(str(r.get(k, "")) for k in cols) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data", default=None)
    ap.add_argument("--res", default=None)
    ap.add_argument("--asof", type=int, default=20101119)
    ap.add_argument("--tables", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out or os.path.join(HERE, "out", a.name))
    data = os.path.abspath(a.data or os.path.join(HERE, "stage", a.name))
    res = os.path.abspath(a.res or os.path.join(HERE, "results", a.name, "shepardized"))
    for p in (os.path.join(out, "status.tsv"), os.path.join(out, "certs.tsv"), os.path.join(data, "history.tsv")):
        if not os.path.exists(p):
            sys.exit("missing " + p)
    os.makedirs(res, exist_ok=True)
    r = subprocess.run([sys.executable, "-I", COMPARE, "--split", "dev", "--out", out, "--data", data,
                        "--asof", str(a.asof), "--results", res], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        sys.exit(r.returncode)
    cases = list(rows(os.path.join(res, "cases_dev.tsv")))
    bucket = {}
    if os.path.exists(DEV_CAUSES):
        bucket = {x["casenum"]: x["bucket"] for x in rows(DEV_CAUSES)}
    miss = [c for c in cases if c["node"] and c["sclass"] in ("NEG", "PART") and c["agree"] == "0"]
    fp = [c for c in cases if c["node"] and c["sclass"] in ("CLEAN", "MOD") and c["agree"] == "0"]
    for c in miss:
        c["baseline_bucket"] = bucket.get(c["casenum"], "")
    key = lambda c: (c["sclass"], c["ssub"], int(c["casenum"]))  # noqa: E731
    write(os.path.join(res, "dev_misses.tsv"),
          ["casenum", "cite", "node", "date", "circuit", "sclass", "ssub", "us1", "us1_key", "us1_node", "us2",
           "us2_key", "us2_node", "mstatus", "mclass", "hist_rows", "baseline_bucket", "name"], sorted(miss, key=key))
    for c in fp:
        c["history_row"] = c["mwitness"]
    write(os.path.join(res, "dev_fp.tsv"),
          ["casenum", "cite", "node", "date", "circuit", "sclass", "ssub", "mstatus", "mclass", "mactor",
           "history_row", "hist_rows", "name"], sorted(fp, key=key))
    if a.tables:
        print(r.stdout.rstrip("\n"))
    else:
        with open(os.path.join(res, "headline.tsv"), encoding="utf-8") as f:
            print(f.read().rstrip("\n"))
    print("\n## dev files (%s)" % res)
    print("dev_misses.tsv\tdev NEG/PART cases not matched\t%d\t(NEG %d, PART %d)" %
          (len(miss), sum(c["sclass"] == "NEG" for c in miss), sum(c["sclass"] == "PART" for c in miss)))
    print("dev_fp.tsv\tdev CLEAN/MOD cases shown negative for a same-case reason\t%d\t(CLEAN %d, MOD %d)" %
          (len(fp), sum(c["sclass"] == "CLEAN" for c in fp), sum(c["sclass"] == "MOD" for c in fp)))


if __name__ == "__main__":
    main()
