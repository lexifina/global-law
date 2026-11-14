"""infra: copy the four benchmark scorers (+ benchlib, sdlib) into round8/bench_h0/ by exact replacements.

Changes: paths (benchlib ROOT; results folder = --results; result file names <dataset>[.<court>].h0.json and
<dataset>.h0.cases.tsv) and h0-only output (the split loops run h0 only; the per-case tables keep h0 units only; the
shadow-docket federal/state files, which are `all`-split, are not written). Metric code is unchanged.
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
B = os.path.join(C2, "benchmarks")
O = os.path.join(C2, "round8", "bench_h0")


def tr(src, dst, reps):
    s = open(os.path.join(B, src), "rb").read().decode("utf-8")
    assert "\r" not in s
    for a, b in reps:
        assert s.count(a) == 1, (src, a[:70])
        s = s.replace(a, b)
    p = os.path.join(O, dst)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(s.encode("utf-8"))


HDR = ("# round 8 h0 shadow (agent infra): copy of benchmarks/%s; changes: paths, results folder (--results), h0-only\n"
       "# output (see round8/bench_h0/README.md). Reads the h0 key written by round8/bench_h0/build_keys.py.\n")

tr("common/benchlib.py", "common/benchlib.py", [
    ('ROOT = os.path.dirname(BENCH)  # caselaw-lean-2',
     'ROOT = os.path.dirname(os.path.dirname(BENCH))  # caselaw-lean-2 (round 8 copy: round8/bench_h0/common)'),
    ('"""Shared helpers for the benchmarks/ scorers',
     '"""(round 8 h0 shadow copy of benchmarks/common/benchlib.py: only ROOT changed.)\nShared helpers for the benchmarks/ scorers'),
])

tr("fjc_idb_appeals/score.py", "fjc_idb_appeals/score.py", [
    ('import argparse\n', HDR % "fjc_idb_appeals/score.py" + 'import argparse\n'),
    ('    ap.add_argument("--results", default=os.path.join(HERE, "results"))\n',
     '    ap.add_argument("--results", required=True)\n'),
    ('os.path.join(a.results, "%s.cases.tsv" % a.label)', 'os.path.join(a.results, "%s.h0.cases.tsv" % DS)'),
    ('        for u in units:\n            s = benchlib.status_of(st, u["dist_node"])',
     '        for u in units:\n            if u["half"] != "h0":\n                continue\n'
     '            s = benchlib.status_of(st, u["dist_node"])'),
    ('    for split in ("h0", "h1", "all"):', '    for split in ("h0",):'),
    ('os.path.join(a.results, "%s.%s.json" % (a.label, split))', 'os.path.join(a.results, "%s.%s.json" % (DS, split))'),
])

tr("shadow_docket/sdlib.py", "shadow_docket/sdlib.py", [
    ('ROOT = os.path.dirname(BENCH)  # caselaw-lean-2',
     'ROOT = os.path.dirname(os.path.dirname(BENCH))  # caselaw-lean-2 (round 8 copy: round8/bench_h0/shadow_docket)'),
    ('"""Shared helpers for the shadow_docket benchmark',
     '"""(round 8 h0 shadow copy of benchmarks/shadow_docket/sdlib.py: only ROOT changed.)\nShared helpers for the shadow_docket benchmark'),
])

tr("shadow_docket/score.py", "shadow_docket/score.py", [
    ('import argparse\n', HDR % "shadow_docket/score.py" + 'import argparse\n'),
    ('    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n    a = ap.parse_args()\n',
     '    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n'
     '    ap.add_argument("--results", required=True)\n    a = ap.parse_args()\n'),
    ('    res_dir = os.path.join(HERE, "results")\n', '    res_dir = a.results\n    os.makedirs(res_dir, exist_ok=True)\n'),
    ('    for split in ("h0", "h1", "all"):', '    for split in ("h0",):'),
    ('os.path.join(res_dir, "%s.%s.json" % (a.label, split))', 'os.path.join(res_dir, "%s.%s.json" % (sdlib.DATASET, split))'),
    ('    for ck in ("federal", "state"):', '    for ck in ():  # round 8 h0 shadow: the federal/state files are `all` split'),
    ('os.path.join(res_dir, "%s.cases.tsv" % a.label)', 'os.path.join(res_dir, "%s.h0.cases.tsv" % sdlib.DATASET)'),
    ('        for c in sorted(cases, key=lambda c: (c["class"], c["node"])):',
     '        for c in sorted((c for c in cases if c["half"] == "h0"), key=lambda c: (c["class"], c["node"])):'),
])

tr("scdb_disposition/score.py", "scdb_disposition/score.py", [
    ('import argparse\n', HDR % "scdb_disposition/score.py" + 'import argparse\n'),
    ('    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n    a = ap.parse_args()\n',
     '    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n'
     '    ap.add_argument("--results", required=True)\n    a = ap.parse_args()\n'),
    ('    resdir = os.path.join(HERE, "results")\n', '    resdir = a.results\n'),
    ('os.path.join(resdir, "%s.cases.tsv" % a.label)', 'os.path.join(resdir, "%s.h0.cases.tsv" % DATASET)'),
    ('        for c in sorted(cases, key=lambda c: c["caseId"]):',
     '        for c in sorted((c for c in cases if c["half"] == "h0"), key=lambda c: c["caseId"]):'),
    ('        for split in ("h0", "h1", "all"):', '        for split in ("h0",):'),
    ('os.path.join(resdir, "%s%s.%s.json" % (a.label, suffix, split))',
     'os.path.join(resdir, "%s%s.%s.json" % (DATASET, suffix, split))'),
])

tr("state_overruled_tables/score.py", "state_overruled_tables/score.py", [
    ('import argparse\n', HDR % "state_overruled_tables/score.py" + 'import argparse\n'),
    ('    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n    a = ap.parse_args()\n',
     '    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)\n'
     '    ap.add_argument("--results", required=True)\n    a = ap.parse_args()\n'),
    ('    rd = os.path.join(HERE, "results")\n', '    rd = a.results\n'),
    ('os.path.join(rd, a.label + ".cases.tsv")', 'os.path.join(rd, DATASET + ".h0.cases.tsv")'),
    ('        for r in out_rows:\n            o.write(',
     '        for r in out_rows:\n            if r[2] != "h0":\n                continue\n            o.write('),
    ('    for sp in ("h0", "h1", "all"):', '    for sp in ("h0",):'),
    ('os.path.join(rd, "%s.%s.json" % (a.label, sp))', 'os.path.join(rd, "%s.%s.json" % (DATASET, sp))'),
])
print("written")
