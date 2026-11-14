"""calpart9 rule PJ, step 2 (history): re-run the round-6 cache scan (round6/history/r6scan.scan_text, unchanged) with
the PJ-fixed part map on the decisions whose r6scan map PJ changes, into a mini cache in this folder, so the round-6
history linkers can be run on them (their records in `concurrence~` / `dissent~` were dropped).

    python -X utf8 r6mini.py [--procs 8]

In: work/scan/*.jsonl (scan_parts.py, records with an "r6" change list). Out: work/r6mini/cache/<repo>.jsonl.gz and
<repo>.meta.tsv.gz (r6scan format), work/r6mini/stats.json (records before / after per type). No answer-key file is
read.
"""
import argparse
import collections
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
import r6scan as RS  # noqa: E402
import partfix as PF  # noqa: E402

NL = chr(10)
OUT = os.path.join(HERE, "work", "r6mini", "cache")
ORIG = {"pm1": RS.C.part_map, "pm2": RS.C.part_map2}


def fixed1(text):
    pm, b0 = ORIG["pm1"](text)
    return PF.fix_parts(text, pm)[0], b0


def fixed2(text):
    pm, b0 = ORIG["pm2"](text)
    return PF.fix_parts(text, pm)[0], b0


def use(fixed):
    RS.C.part_map = fixed1 if fixed else ORIG["pm1"]
    RS.C.part_map2 = fixed2 if fixed else ORIG["pm2"]


def one(job):
    repo, nodes = job
    if "idx" not in RS.G:
        RS.init()
    st = collections.Counter()
    T = L.fetch_texts(nodes)
    om = os.path.join(OUT, repo + ".meta.tsv.gz")
    oj = os.path.join(OUT, repo + ".jsonl.gz")
    with gzip.open(om, "wt", encoding="utf-8", newline=NL) as fm, gzip.open(oj, "wt", encoding="utf-8",
                                                                             newline=NL) as fj:
        for n in sorted(nodes):
            if n not in T:
                st["no_text"] += 1
                continue
            sha, text = T[n]
            use(False)
            _m0, old = RS.scan_text(n, text)
            use(True)
            meta, recs = RS.scan_text(n, text)
            use(False)
            for r in old:
                st["old_" + r["t"]] += 1
            for r in recs:
                st["new_" + r["t"]] += 1
            st["nodes"] += 1
            st["nodes_more"] += len(recs) > len(old)
            fm.write("\t".join([str(n), sha, str(meta["len"]), str(meta["date"]), str(meta["court"]),
                                RS.clean(" ; ".join(meta["docket"])), RS.clean(" ".join(meta["type"])),
                                RS.clean(meta["title"]), " | ".join(RS.clean(x) for x in meta["parties"]),
                                " | ".join(RS.clean(x) for x in meta["citations"]), meta["flags"]]) + NL)
            for r in recs:
                fj.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + NL)
    with open(os.path.join(OUT, repo + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f)
    return repo, dict(st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    per = collections.defaultdict(list)
    for p in glob.glob(os.path.join(HERE, "work", "scan", "*.jsonl")):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] == "PJ" and "r6" in r:
                per[r["repo"]].append(int(r["n"]))
    print("decisions", sum(len(v) for v in per.values()), "repos", len(per), flush=True)
    tot = collections.Counter()
    for repo, st in L.pmap(one, sorted(per.items(), key=lambda kv: -len(kv[1])), procs=a.procs):
        tot.update(st)
        print(repo, json.dumps(st), flush=True)
    print("TOTAL", json.dumps(dict(tot)), flush=True)
    json.dump(dict(tot), open(os.path.join(HERE, "work", "r6mini", "stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
