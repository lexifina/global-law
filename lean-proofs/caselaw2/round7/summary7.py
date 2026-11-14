"""Round 7: one-page summary of a scored variant (round7/results/<name>/summary.txt; called by score7.sh).

    python round7/summary7.py <name>
Reads only the files score7.sh wrote in round7/results/<name>/ and the variant's Lean summary/certs. Dev only.
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
    L.append("round 7 variant %s: dev-side scores (results in round7/results/%s/)" % (n, n))
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
        r"anchor|joined|hclaim|class_|recognised_rows|operative_rows|doctrine|orderhead|setaside|bad_rows", k, re.I)]
    L.append("Lean summary (shard 0): " + ", ".join("%s %s" % (k, first[k]) for k in keys))
    cv = collections.Counter()
    try:
        with open(os.path.join(O, "certs.tsv"), encoding="utf-8") as f:
            next(f)
            for line in f:
                p = line.split("\t", 3)
                if len(p) >= 3 and (p[1].startswith("t7:") or p[1].startswith("h7:")):
                    cv["%s %s" % (p[1][:2], p[2])] += 1
    except OSError:
        pass
    if cv:
        L.append("round-7 rows by verdict: " + ", ".join("%s %d" % kv for kv in sorted(cv.items())))
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
    elif os.path.exists(os.path.join(HERE, "score_fresh7.py")):
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
    print("\n".join(L))


if __name__ == "__main__":
    main()
