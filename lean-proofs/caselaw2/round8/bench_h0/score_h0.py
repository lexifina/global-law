"""Round 8: score one build on the h0 half of the four new benchmark keys (agent infra).

    python round8/bench_h0/score_h0.py --out <Lean out dir> --data <stage dir> --label <x> [--results DIR]
                                       [--asof yyyymmdd] [--only KEY ...]

Runs the h0 shadow scorers round8/bench_h0/<key>/score.py (copies of benchmarks/<key>/score.py: paths and h0-only
output changed, metric code not) on the h0 keys written by round8/bench_h0/build_keys.py, for the keys
fjc_idb_appeals, shadow_docket, scdb_disposition, state_overruled_tables. Results (default
round8/results/<label>/bench/): <key>.h0.json (+ scdb_disposition.federal.h0.json / .state.h0.json) and
<key>.h0.cases.tsv (per-case h0 outcomes), SUMMARY.tsv (one line per key and metric). Prints one line per key: the
primary metric and the sub-metrics as k/n = p [Wilson 95% lo, hi]. Never reads or writes anything under
benchmarks/ (the h0 keys are round8/bench_h0/<key>/key*.tsv). No h1 or `all` output exists.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
KEYS = ("fjc_idb_appeals", "shadow_docket", "scdb_disposition", "state_overruled_tables")
NOWIN = 0x08000000 if sys.platform == "win32" else 0


def fmt(v):
    if not v["n"]:
        return "%d/%d" % (v["k"], v["n"])
    return "%d/%d=%.3f [%.3f,%.3f]" % (v["k"], v["n"], v["p"], v["lo"], v["hi"])


def result_files(res, key):
    out = [os.path.join(res, "%s.h0.json" % key)]
    if key == "scdb_disposition":
        out += [os.path.join(res, "%s.%s.h0.json" % (key, c)) for c in ("federal", "state")]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--results")
    ap.add_argument("--asof", type=int)
    ap.add_argument("--only", action="append", choices=KEYS)
    a = ap.parse_args()
    out, data = os.path.abspath(a.out), os.path.abspath(a.data)
    for p, what in ((os.path.join(out, "status.tsv"), "--out"), (os.path.join(data, "history.tsv"), "--data")):
        if not os.path.exists(p):
            sys.exit("%s: no %s" % (what, p))
    res = os.path.abspath(a.results or os.path.join(C2, "round8", "results", a.label, "bench"))
    os.makedirs(res, exist_ok=True)
    keys = a.only or KEYS
    procs = {}
    for k in keys:
        for f in result_files(res, k) + [os.path.join(res, "%s.h0.cases.tsv" % k)]:
            if os.path.exists(f):
                os.remove(f)
        cmd = [sys.executable, "-B", "-X", "utf8", os.path.join(HERE, k, "score.py"), "--out", out, "--data", data,
               "--label", a.label, "--results", res]
        if a.asof:
            cmd += ["--asof", str(a.asof)]
        log = open(os.path.join(res, "%s.h0.log" % k), "w", encoding="utf-8")
        procs[k] = (subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, creationflags=NOWIN), log, time.time())
    fail = 0
    lines = []
    for k in keys:
        p, log, t0 = procs[k]
        rc = p.wait()
        log.close()
        if rc:
            fail += 1
            print("%s: scorer failed (exit %d), see %s" % (k, rc, os.path.join(res, "%s.h0.log" % k)))
            continue
        for f in result_files(res, k):
            r = json.load(open(f, encoding="utf-8"))
            assert r["split"] == "h0", f
            m = r["metrics"]
            prim = r["primary"]
            name = os.path.basename(f)[:-len(".h0.json")]
            print("%-26s %s %s | %s" % (name, prim, fmt(m[prim]),
                                        "  ".join("%s %s" % (n, fmt(v)) for n, v in m.items() if n != prim)))
            for n, v in [(prim, m[prim])] + [(n, v) for n, v in m.items() if n != prim]:
                lines.append("\t".join(map(str, [name, n, int(n == prim), v["k"], v["n"],
                                                 "%.4f" % v["p"] if v["p"] is not None else "-",
                                                 "%.4f" % v["lo"] if v["lo"] is not None else "-",
                                                 "%.4f" % v["hi"] if v["hi"] is not None else "-"])))
            for n, v in sorted((r.get("extra_metrics") or {}).items()):
                lines.append("\t".join(map(str, [name, "extra:" + n, 0, v["k"], v["n"],
                                                 "%.4f" % v["p"] if v["p"] is not None else "-",
                                                 "%.4f" % v["lo"] if v["lo"] is not None else "-",
                                                 "%.4f" % v["hi"] if v["hi"] is not None else "-"])))
    with open(os.path.join(res, "SUMMARY.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# label %s; out %s; data %s\n" % (a.label, os.path.relpath(out, C2).replace(os.sep, "/"),
                                                   os.path.relpath(data, C2).replace(os.sep, "/")))
        f.write("key\tmetric\tprimary\tk\tn\tp\tlo\thi\n")
        for l in lines:
            f.write(l + "\n")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
