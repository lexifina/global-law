"""round13 lead: overlaps of the user-approved held classes (T4, R2 v3, EB12 v6) with v12a and with one another.

    python -X utf8 round13/lead/overlap13.py
history.tsv columns: id, target, by, date, kind, scope, sha, start, end, quote, ev, part, src. No key read.
"""
import collections
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETS = {"T4": "round10/agents/stlink10/delta_T4/history_delta.tsv",
        "R2v3": "round11/agents/scdb11/cert_r2v3/history_delta.tsv",
        "EB12v6": "round12/agents/enbanc12/cert_eb12b/history_delta.tsv"}


def rows(p):
    out = []
    for line in open(os.path.join(C2, p), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 13:
            out.append(f)
    return out


base_pair = collections.defaultdict(list)
base_tgt = collections.defaultdict(list)
for f in rows("round12/stage/v12a/history.tsv"):
    base_pair[(f[2], f[1])].append((f[0], f[4]))
    base_tgt[f[1]].append((f[0], f[2], f[4]))
R = {k: rows(p) for k, p in SETS.items()}
for k, rs in R.items():
    c = collections.Counter()
    for f in rs:
        c["rows"] += 1
        c["kind_" + f[4]] += 1
        if any(x[0] == f[0] for x in base_pair.get((f[2], f[1]), ())):
            c["id_in_v12a"] += 1
        elif base_pair.get((f[2], f[1])):
            ks = {x[1] for x in base_pair[(f[2], f[1])]}
            c["pair_in_v12a_same_kind" if f[4] in ks else "pair_in_v12a_other_kind"] += 1
        elif base_tgt.get(f[1]):
            c["target_has_other_row_in_v12a"] += 1
        else:
            c["new_target"] += 1
    print(k, dict(sorted(c.items())))
# R2 v3 vs EB12 v6
for a, b in (("R2v3", "EB12v6"), ("T4", "R2v3"), ("T4", "EB12v6")):
    pa = {(f[2], f[1]): f for f in R[a]}
    pb = {(f[2], f[1]): f for f in R[b]}
    ta = collections.defaultdict(list)
    for f in R[a]:
        ta[f[1]].append(f)
    same_pair = sorted(set(pa) & set(pb))
    same_tgt = sorted({f[1] for f in R[b]} & set(ta))
    print("%s x %s: same (by, target) %d; same target %d" % (a, b, len(same_pair), len(same_tgt)))
    for t in same_tgt:
        for fb in [f for f in R[b] if f[1] == t]:
            for fa in ta[t]:
                print("  target %s | %s by %s %s %s | %s by %s %s %s" % (t, a, fa[2], fa[3], fa[4], b, fb[2], fb[3],
                                                                         fb[4]))
