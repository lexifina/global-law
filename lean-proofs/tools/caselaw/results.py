"""Aggregate the Lean run over all US case law into summary.json and the tables of the write-up.

    python tools/caselaw/results.py <work-dir>

Reads graph/, lean-in/, lean-out/, events/ and writes results/summary.json, results/most_cited_overruled.tsv and
results/by_system.tsv.
"""
import collections, glob, json, os, sys


def main(w, lin="lean-in", lout="lean-out"):
    out = os.path.join(w, "results")
    os.makedirs(out, exist_ok=True)
    tot = collections.Counter()
    for f in glob.glob(os.path.join(w, lout, "*.summary.json")):
        d = json.load(open(f))
        for k in ("citations", "cites_later", "cites_overruled"):
            tot[k] += d[k]
    courts = {}
    for l in open(os.path.join(w, lin, "courts.tsv"), encoding="utf-8"):
        i, s, t, c = l.rstrip("\n").split("\t")
        courts[int(i)] = (int(s), t, int(c))
    cname = {}
    for l in open(os.path.join(w, lin, "courts_named.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        cname[int(f[0])] = (f[1], f[5])
    dec_court, dec_date = {}, {}
    for l in open(os.path.join(w, lin, "decisions.tsv"), encoding="utf-8"):
        i, c, d = l.split("\t")
        dec_court[int(i)] = int(c)
        dec_date[int(i)] = int(d)
    names, cits = {}, {}
    for l in open(os.path.join(w, "graph", "nodes.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        names[int(f[0])] = f[6]
        cits[int(f[0])] = f[5].split("|")[0]
    systems = collections.Counter()
    for i, c in dec_court.items():
        s, t, _ = courts.get(c, (999, "T", 0))
        systems["federal" if s == 0 else ("unknown" if s == 999 else "state")] += 1
    # acts
    why = collections.Counter()
    valid = 0
    acts = [l.rstrip("\n").split("\t") for l in open(os.path.join(w, lout, "00.acts.tsv"), encoding="utf-8")]
    for y, x, v in acts:
        y, x = int(y), int(x)
        if v == "1":
            valid += 1
            continue
        cy, cx = courts.get(dec_court[y], (999, "T", 0)), courts.get(dec_court[x], (999, "T", 0))
        if dec_date[x] > dec_date[y]:
            why["overruled decision is later"] += 1
        elif cy[0] != cx[0]:
            why["different court system (state/federal or another state)"] += 1
        elif cy[0] == 0 and cy[1] == "A" and cy[2] != cx[2]:
            why["federal court of appeals, another circuit"] += 1
        else:
            why["lower court overruling a higher one"] += 1
    # reports
    rv = collections.Counter()
    rsys = collections.defaultdict(collections.Counter)
    for l in open(os.path.join(w, lout, "00.reports.tsv"), encoding="utf-8"):
        z, x, n, verd, by = l.rstrip("\n").split("\t")
        named = n not in ("-1", "")
        rv[("named" if named else "unnamed", verd)] += 1
        s = courts.get(dec_court[int(x)], (999, "T", 0))[0]
        rsys["federal" if s == 0 else "state"][("named" if named else "unnamed", verd)] += 1
    # cited after being overruled
    after = collections.Counter()
    citing = set()
    for f in glob.glob(os.path.join(w, lout, "*.citations.tsv")):
        for l in open(f, encoding="utf-8"):
            p = l.rstrip("\n").split("\t")
            if p[0] == "overruled":
                after[(int(p[2]), int(p[3]))] += 1
                citing.add(int(p[1]))
    with open(os.path.join(out, "most_cited_overruled.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for (x, by), n in after.most_common(200):
            f.write(f"{n}\t{names[x]}\t{cits[x]}\t{cname[dec_court[x]][0]}\t{dec_date[x]}\t{names[by]}\t{cits[by]}\t{dec_date[by]}\n")
    summ = {"decisions": len(dec_court), "decisions_by_system": systems, **tot,
            "decisions_citing_overruled": len(citing), "overruled_decisions_cited_after": len(after),
            "acts": len(acts), "acts_valid": valid, "acts_invalid_why": why,
            "reports": {f"{a}:{b}": c for (a, b), c in rv.items()},
            "reports_by_system": {s: {f"{a}:{b}": c for (a, b), c in v.items()} for s, v in rsys.items()}}
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
