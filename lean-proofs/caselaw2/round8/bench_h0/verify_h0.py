"""Round 8 (agent infra): check that the h0 shadow reproduces the full scorers' published h0 results.

    python -B round8/bench_h0/verify_h0.py round6 round4

For each label (round4 = out/ + data/, round6 = round6/history/out/final2 + stage/final2, as benchlib.BUILDS) runs
score_h0.py into round8/agents/infra/verify/<label>/ and compares, by script, the `metrics` (and `extra_metrics`,
`link`) dicts of each shadow result with benchmarks/<key>/results/<label>.h0.json (and, for scdb_disposition,
<label>.federal.h0.json / <label>.state.h0.json): those are h0 files already public. Reads no other file under
benchmarks/. Prints per file: identical or the differing metric names.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
BUILDS = {"round4": ("out", "data"),
          "round6": ("round6/history/out/final2", "round6/history/stage/final2"),
          "v3": ("round7/out/v3", "round7/stage/v3")}
FILES = [("fjc_idb_appeals", ""), ("shadow_docket", ""), ("scdb_disposition", ""),
         ("scdb_disposition", ".federal"), ("scdb_disposition", ".state"), ("state_overruled_tables", "")]


def main():
    bad = 0
    for label in sys.argv[1:]:
        o, d = BUILDS[label]
        res = os.path.join(C2, "round8", "agents", "infra", "verify", label)
        rc = subprocess.call([sys.executable, "-B", os.path.join(HERE, "score_h0.py"), "--out", os.path.join(C2, o),
                              "--data", os.path.join(C2, d), "--label", label, "--results", res])
        if rc:
            print("%s: score_h0 failed" % label)
            bad += 1
            continue
        if label == "v3":
            continue
        for key, suf in FILES:
            ref_p = os.path.join(C2, "benchmarks", key, "results", "%s%s.h0.json" % (label, suf))
            if not os.path.exists(ref_p):
                print("%s %s%s: no published h0 result" % (label, key, suf))
                continue
            ref = json.load(open(ref_p, encoding="utf-8"))
            got = json.load(open(os.path.join(res, "%s%s.h0.json" % (key, suf)), encoding="utf-8"))
            diffs = []
            for part in ("metrics", "extra_metrics", "link"):
                a, b = ref.get(part), got.get(part)
                if a == b:
                    continue
                if isinstance(a, dict) and isinstance(b, dict):
                    diffs += ["%s.%s" % (part, k) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
                else:
                    diffs.append(part)
            same_rest = all(ref.get(k) == got.get(k) for k in ("dataset", "split", "primary", "row_label", "asof"))
            print("%-7s %-34s metrics %s; link %s; extra %s; header %s%s" % (
                label, key + suf + ".h0", "IDENTICAL" if ref["metrics"] == got["metrics"] else "DIFFER",
                "same" if ref.get("link") == got.get("link") else "differs",
                "same" if ref.get("extra_metrics") == got.get("extra_metrics") else "differs",
                "same" if same_rest else "differs", ("  " + ", ".join(diffs)) if diffs else ""))
            bad += bool(diffs) or not same_rest
    print("VERIFY %s" % ("OK" if not bad else "FAILED (%d)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
