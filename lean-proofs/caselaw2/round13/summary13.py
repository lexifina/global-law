"""Round 13: one-page summary of a scored variant (round13/results/<name>/summary.txt; called by score13.sh).
= round11/summary11.py on round-13 paths (agent infra12); round-11 (t11: / h11:) and round-13 (t13: / h13:) rows
counted by verdict. Round 11: = round10/summary10.py on round-11 paths.
Round 10: one-page summary of a scored variant (round10/results/<name>/summary.txt; called by score10.sh).
= round9/summary9.py on round-10 paths; round-8, round-9 and round-10 (t10: / h10:) rows counted by verdict;
Lean zone and remand counters shown when present; the four round-8 keys on h0 only.
(round 9: = round8/summary8.py on round-9 paths, zone counters.)
(round 8: = round7/summary7.py on round-8 paths, plus the four new keys on h0.)

    python round13/summary13.py <name>
Reads only the files score13.sh wrote in round13/results/<name>/ and the variant's Lean summary/certs. Dev only (new keys: h0 only).
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def kn(d):
    if not d:
        return "-"
    w = d.get("wilson95") or [float("nan"), float("nan")]
    return "%d/%d = %.1f%% (%.1f-%.1f)" % (d["k"], d["n"], 100 * d["rate"], 100 * w[0], 100 * w[1])


def main():
    n = sys.argv[1]
    R = os.path.join(HERE, "results", n)
    O = os.path.join(HERE, "out", n)
    L = []
    L.append("round 12 variant %s: dev-side scores (results in round13/results/%s/)" % (n, n))
    L.append(rd(os.path.join(R, "run.log")).strip())
    man = rd(os.path.join(HERE, "stage", n, "MANIFEST.txt"))
    m = re.search(r"^args: (.*)$", man, re.M)
    L.append("stage args: %s" % (m.group(1) if m else "?"))
    run = rd(os.path.join(O, "RUN.txt")).strip()
    L.append("Lean run: %s" % (run or "?"))
    # Lean counters
    summ = rd(os.path.join(O, "summary.tsv"))
    first = {}
    for line in summ.splitlines():
        p = line.split("\t")
        if len(p) == 2 and p[0] not in first and p[0] not in ("shard", "load_ms", "run_ms"):
            first[p[0]] = p[1]
    keys = [k for k in first if k in ("rows_admitted", "rows_rejected") or re.search(
        r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows|zone|remand", k,
        re.I)]
    L.append("Lean summary (shard 0): " + ", ".join("%s %s" % (k, first[k]) for k in keys))
    cv = collections.Counter()
    cv9 = collections.Counter()
    cv10 = collections.Counter()
    cv11 = collections.Counter()
    cv12 = collections.Counter()
    try:
        with open(os.path.join(O, "certs.tsv"), encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.split("\t", 3)
                if len(p) >= 3 and (p[1].startswith("t8:") or p[1].startswith("h8:")):
                    cv["%s %s" % (p[1][:2], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t9:") or p[1].startswith("h9:")):
                    cv9["%s %s" % (p[1][:2], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t10:") or p[1].startswith("h10:")):
                    cv10["%s %s" % (p[1][:3], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t11:") or p[1].startswith("h11:")):
                    cv11["%s %s" % (p[1][:3], p[2])] += 1
                elif len(p) >= 3 and (p[1].startswith("t13:") or p[1].startswith("h13:")):
                    cv12["%s %s" % (p[1][:3], p[2])] += 1
    except OSError:
        pass
    if cv:
        L.append("round-8 rows by verdict: " + ", ".join("%s %d" % kv for kv in sorted(cv.items())))
    L.append("round-9 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv9.items())) or "none"))
    L.append("round-10 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv10.items())) or "none"))
    L.append("round-11 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv11.items())) or "none"))
    L.append("round-13 rows by verdict: " + (", ".join("%s %d" % kv for kv in sorted(cv12.items())) or "none"))
    L.append("")
    # fresh lists
    try:
        fj = json.load(open(os.path.join(R, "fresh_dev.json"), encoding="utf-8"))
        a = fj["recall"]["all"]["all"]
        L.append("FRESH LISTS, dev (%d pairs): strict %s; lenient %s" % (a["n"], kn(a["strict"]), kn(a["lenient"])))
        ps = fj.get("precision_side", {})
        L.append("  precision side: listed %s; classes %s" % (kn(ps.get("listed_share")),
                                                               json.dumps(ps.get("classes", {}))))
    except (OSError, KeyError, ValueError) as e:
        L.append("FRESH LISTS, dev: not available (%s)" % type(e).__name__)
    f7 = None
    for cand in (os.path.join(R, "fresh7", "fresh7_dev.json"), os.path.join(R, "fresh7_dev.json")):
        if os.path.exists(cand):
            f7 = cand
            break
    if f7:
        try:
            j = json.load(open(f7, encoding="utf-8"))
            for v, res in sorted(j.get("views", {}).items()):
                a = res["recall"]["all"]["all"]
                L.append("  view %-10s strict %s; lenient %s" % (v, kn(a["strict"]), kn(a["lenient"])))
        except (OSError, KeyError, ValueError) as e:
            L.append("  score_fresh7: unreadable (%s)" % type(e).__name__)
    elif os.path.exists(os.path.join(os.path.dirname(HERE), "round7", "score_fresh7.py")):
        L.append("  score_fresh7: no output (see fresh7_dev.txt)")
    # no leak
    lk = rd(os.path.join(R, "leak.txt"))
    m = re.findall(r"^exit (\d+)", lk, re.M)
    L.append("NO-LEAK: exit %s (0 = no leak)" % (m[-1] if m else "?"))
    # holdout
    ho = rd(os.path.join(R, "holdout.txt"))
    for pat in (r"^\s*precedent, Y named\s+strict.*$", r"^\s*precedent, explicitly admitted pairs.*$",
                r"^\s*history\s+\d+/\d+.*$", r"^\s*precedent\s+\d+/\d+.*$", r"^\s*alsoInFeed\s+strict.*$", r"^\s*holdoutOnly\s+strict.*$"):
        m = re.search(pat, ho, re.M)
        if m:
            L.append("HOLDOUT NOTES: " + " ".join(m.group(0).split()))
    # behaviour
    if os.path.exists(os.path.join(R, "behaviour.txt")):
        L.append("BEHAVIOUR: see behaviour.txt")
    # old lists
    try:
        ob = json.load(open(os.path.join(R, "old_by_class.json"), encoding="utf-8"))
        e, f = ob["selfAnnounced+operativeWords"], ob["selfAnnounced+operativeWords+recognised"]
        L.append("OLD LISTS (burned, non-blind): SCDB %d/%d explicit rows, %d/%d with recognised; CRS current %d/%d, "
                 "%d/%d with recognised; rows by class %s" % (
                     e["scdb_found"], e["scdb_flagged"], f["scdb_found"], f["scdb_flagged"],
                     e["crs_current_table"][0], e["crs_current_table"][1], f["crs_current_table"][0],
                     f["crs_current_table"][1], json.dumps(ob.get("_rows", {}))))
    except (OSError, KeyError, ValueError):
        L.append("OLD LISTS: not run")
    # Shepardized dev
    sh = rd(os.path.join(R, "shepardized", "headline.tsv"))
    if sh:
        L.append("SHEPARDIZED, dev half (raw k/n share [95%]; with documented errors set aside):")
        for line in sh.splitlines():
            p = line.split("\t")
            if len(p) >= 10 and p[0] in ("(a) recall", "(b) precision", "(c) clean", "agreement"):
                L.append("  %-14s %-62s %s %s [%s-%s]; set aside %s %s" % (p[0], p[1][:62], p[2], p[3], p[4], p[5],
                                                                         p[6], p[7]))
            elif p[0] == "recall by subclass" and len(p) >= 4:
                L.append("  %-14s %-62s %s %s" % ("subclass", p[1], p[2], p[3]))
    else:
        L.append("SHEPARDIZED, dev: not available")
    m = re.search(r"dev_fp\.tsv.*$", rd(os.path.join(R, "shepardized_dev.txt")), re.M)
    if m:
        L.append("  " + " ".join(m.group(0).split("\t")))
    # round 8: the four new keys, h0 half only (round8/bench_h0/score_h0.py -> results/<name>/bench/SUMMARY.tsv)
    bs = rd(os.path.join(R, "bench", "SUMMARY.tsv"))
    if bs:
        L.append("NEW KEYS, h0 half only (k/n = share (Wilson 95%); primary first):")
        by = {}
        for line in bs.splitlines():
            p = line.split("\t")
            if line.startswith("#") or len(p) < 8 or p[0] == "key" or p[1].startswith("extra:"):
                continue
            by.setdefault(p[0], []).append(p)
        for key, ps in by.items():
            def one(p):
                if p[5] == "-":
                    return "%s %s/%s" % (p[1], p[3], p[4])
                return "%s %s/%s = %.1f%% (%.1f-%.1f)" % (p[1], p[3], p[4], 100 * float(p[5]), 100 * float(p[6]),
                                                           100 * float(p[7]))
            prim = [p for p in ps if p[2] == "1"]
            rest = [p for p in ps if p[2] != "1" and p[1] in ("precision", "clean", "part", "recall_any",
                                                              "actor_agreement", "link_rate")]
            L.append("  %-26s %s; %s" % (key, "; ".join(one(p) for p in prim), "; ".join(one(p) for p in rest)))
    else:
        L.append("NEW KEYS, h0: not available (round8/bench_h0/score_h0.py not run)")
    print("\n".join(L))


if __name__ == "__main__":
    main()
