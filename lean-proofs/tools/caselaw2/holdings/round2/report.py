"""Before/after tables for round 2 splits.
    python report.py <out before> <out after> [--write]
Prints counts; with --write also writes C2/round2/splits_resolved_links.tsv."""
import os, sys, json, collections
import common as C
o0, o1 = sys.argv[1], sys.argv[2]
def rd(p):
    return [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")] if os.path.exists(p) else []
inst = json.load(open(os.path.join(C.PRIV, "work", "installed_rows.json"), encoding="utf-8"))
px = os.path.join(C.PRIV, "work", "installed_rowsx.json")
if os.path.exists(px):
    inst["rows"] += json.load(open(px, encoding="utf-8"))["rows"]
res = [r for r in inst["rows"] if r["stream"] == "res"]
xc_issues = {i[0] for i in inst["issues"]}
S0, S1 = rd(os.path.join(o0, "splits.tsv")), rd(os.path.join(o1, "splits.tsv"))
A0, A1 = rd(os.path.join(o0, "splits_asof.tsv")), rd(os.path.join(o1, "splits_asof.tsv"))
K0, K1 = rd(os.path.join(o0, "conflicts_asof.tsv")), rd(os.path.join(o1, "conflicts_asof.tsv"))
k5 = lambda r: tuple(r[:5])
out = {"splits_rows": [len(S0), len(S1)], "splits_asof": [len(A0), len(A1)], "conflicts_asof": [len(K0), len(K1)],
       "split_questions_ever": [len({r[0] for r in S0}), len({r[0] for r in S1})],
       "new_question_rows_in_splits": sum(1 for r in S1 if r[0] in xc_issues),
       "new_questions_with_a_split_row": len({r[0] for r in S1 if r[0] in xc_issues}),
       "new_question_rows_asof": sum(1 for r in A1 if r[0] in xc_issues),
       "new_question_conflicts_asof": sum(1 for r in K1 if r[0] in xc_issues)}
a1 = {k5(r) for r in A1}; s1 = {k5(r) for r in S1}; c1 = {tuple(r[:2]) for r in K1}
gone_asof = [r for r in A0 if k5(r) not in a1]
gone_ever = [r for r in S0 if k5(r) not in s1]
gone_conf = [r for r in K0 if tuple(r[:2]) not in c1]
out["baseline_asof_splits_now_resolved"] = len(gone_asof)
out["baseline_asof_split_questions_now_resolved"] = len({r[0] for r in gone_asof})
out["baseline_split_rows_that_no_longer_arise"] = len(gone_ever)
out["baseline_conflict_rows_removed"] = len(gone_conf)
out["new_asof_rows_on_old_questions"] = sum(1 for r in A1 if k5(r) not in {k5(x) for x in A0} and r[0] not in xc_issues)
by_issue = collections.defaultdict(list)
for r in res: by_issue[r["issue"]].append(r)
links = [["issue", "usc", "question", "scotus_node", "scotus_name", "scotus_cite", "scotus_date", "answer", "holding_id",
          "reader_conf", "baseline_split_rows", "baseline_asof_rows", "asof_rows_resolved", "conflict_rows_removed",
          "asof_rows_left"]]
by_dec = collections.Counter()
for r in sorted(res, key=lambda r: (r["date"], r["issue"])):
    k = r["issue"]
    n_s0 = sum(1 for x in S0 if x[0] == k); n_a0 = sum(1 for x in A0 if x[0] == k)
    n_res = sum(1 for x in gone_asof if x[0] == k); n_c = sum(1 for x in gone_conf if x[0] == k)
    n_left = sum(1 for x in A1 if x[0] == k)
    by_dec["%s, %s (%s)" % (r["name"], r["cite"], str(r["date"])[:4])] += n_res
    links.append([k, r["usc"], r["question"], r["node"], r["name"], r["cite"], r["date"], r["answer"], r["hid"], r["conf"],
                  n_s0, n_a0, n_res, n_c, n_left])
out["links"] = len(res)
out["links_resolving_a_baseline_asof_row"] = sum(1 for l in links[1:] if l[12] > 0)
out["resolved_rows_by_decision"] = dict(by_dec.most_common())
unexplained = [r for r in gone_asof if r[0] not in by_issue]
out["resolved_rows_not_on_a_linked_issue"] = len(unexplained)
if "--write" in sys.argv:
    with open(os.path.join(C.C2, "round2", "splits_resolved_links.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for l in links: f.write("\t".join(str(x).replace("\t", " ") for x in l) + "\n")
print(json.dumps(out, indent=1, ensure_ascii=False))
