"""fjc8: simulate the oldCircuit claim on the FJC h0 cited population (scorer side; no rule reads this).

    python -X utf8 sim_oc.py CASES.tsv CERTS.tsv HISTORY.tsv CLAIMS.tsv [CLAIMS ...]
A unit whose model class is not NEG_HIST gains NEG_HIST when a claimed reversed/vacated `all` row targeting it was
refused noAuthority (and no other negative row of another kind exists); approximate (Lean's status merge is not run).
"""
import collections, sys

NL = chr(10)


def main():
    cases_p, certs_p, hist_p = sys.argv[1:4]
    claimed = set()
    for f in sys.argv[4:]:
        for l in open(f, encoding="utf-8"):
            claimed.add(l.split("\t")[0])
    ver = {}
    for l in open(certs_p, encoding="utf-8"):
        p = l.rstrip(NL).split("\t")
        if p[0] == "history":
            ver[p[1]] = p[2]
    rows = collections.defaultdict(list)
    for l in open(hist_p, encoding="utf-8"):
        p = l.rstrip(NL).split("\t")
        if len(p) > 5 and p[0] in claimed:
            rows[int(p[1])].append((p[0], p[4], p[5], ver.get(p[0], "?")))
    c = collections.Counter()
    for l in open(cases_p, encoding="utf-8"):
        p = l.rstrip(NL).split("\t")
        if p[0] == "dist_node" or p[3] != "1":
            continue
        rs = rows.get(int(p[0]), [])
        if not rs:
            continue
        neg_all = [r for r in rs if r[1] in ("reversed", "vacated") and r[2] == "all" and r[3] == "noAuthority"]
        neg_unk = [r for r in rs if r[1] in ("reversed", "vacated", "modified") and r[3] == "noAuthority"]
        if neg_all and p[4] != "NEG_HIST":
            c[("to NEG_HIST", p[2], p[4])] += 1
        elif neg_unk and p[4] == "GOOD":
            c[("to UNK_HIST", p[2], p[4])] += 1
        else:
            c[("no change", p[2], p[4])] += 1
    for k, v in sorted(c.items()):
        print(v, *k)


if __name__ == "__main__":
    main()
