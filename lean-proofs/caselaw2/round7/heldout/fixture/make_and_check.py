#!/usr/bin/env python3
"""Synthetic fixture for score_heldout.py (no real key row, no real model output: every node id is made up and
8 digits long, outside the corpus id range).

    python -I fixture/make_and_check.py

Writes fixture/{key.tsv, orders.tsv, history.tsv, certs.tsv, status.tsv}, runs score_heldout.py on them with the
label fixture-selftest (results in fixture/results/, one RUNS.log line), and checks the tables line by line against
the values worked out by hand below. Exit 0 = all checks pass.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.join(HERE, "..", "score_heldout.py")
END = "20261112"

# order nodes
O1, O2, O3, O4, O5, O6, O7 = "90000001", "90000002", "90000003", "90000004", "90000005", "90000006", "90000007"
O8 = "90000008"
# key: (order, lower, kind, order date, system)
KEY = [
    (O1, "80000001", "reversed", "20210301", "federal"),         # 1 admitted reversed row, status neg by O1
    (O2, "80000002", "vacated", "20210401", "state"),            # 2 row rejected, status good
    (O3, "80000003", "reversed", "20220110", "federal"),         # 3 admitted vacated row (wrong kind, same effect)
    (O4, "80000004", "mixed", "20220210", "federal"),            # 4 reversed row scope unknown, status unknown by O4
    (O5, "80000005", "affirmed", "20230315", "state"),           # 5 affirmed row, status good (issue line ignored)
    (O6, "80000006", "reviewDismissed", "20230420", "federal"),  # 6 wrong reversed row, status neg by O6
    (O1, "80000007", "vacated", "20210301", "federal"),          # 7 no row, status neg by another actor
    (O7, "80000008", "vacated", "20240105", "state"),            # 8 row to another decision; O7 incomplete
    (O8, "80000009", "certDenied", "20250110", "federal"),       # 9 certDenied row (r7 family), status good
]
ORDERS = [(O1, 2, 2, 1), (O2, 1, 1, 1), (O3, 1, 1, 1), (O4, 1, 1, 1), (O5, 1, 1, 1), (O6, 1, 1, 1), (O7, 2, 1, 0), (O8, 1, 1, 1)]
# history rows: (id, target, by, date, kind, scope, src, verdict)
HIST = [
    ("h:a", "80000001", O1, "20210301", "reversed", "all", "r6:below:x", "ok"),
    ("h:b", "80000050", O1, "20210301", "certDenied", "all", "r6:memo:cap-2g", "ok"),       # wrong target
    ("h:c", "80000051", O1, "20210301", "vacated", "all", "r6:memo:cap-2g", "noCue"),       # rejected: not counted
    ("h:d", "80000002", O2, "20210401", "vacated", "all", "r6:below:x", "noCue"),           # rejected
    ("h:e", "80000003", O3, "20220110", "vacated", "all", "r6:below:x", "ok"),
    ("h:f", "80000004", O4, "20220210", "reversed", "unknown", "r6:below:x", "ok"),
    ("h:g", "80000005", O5, "20230315", "affirmed", "all", "r6:below:x", "ok"),
    ("h:h", "80000006", O6, "20230420", "reversed", "all", "r6:below:x", "ok"),
    ("h:i", "80000099", O7, "20240105", "vacated", "all", "r6:memo:cap-2t", "ok"),          # incomplete order
    ("h:k", "80000009", O8, "20250110", "certDenied", "all", "r7:memo:orderHead", "ok"),
    ("h:j", "80000001", "70000001", "20200101", "affirmed", "all", "r6:below:x", "ok"),      # by a non-key node
]
# status lines: (node, issue, holding, from, to, status, actor, path)
STATUS = [
    ("80000001", "-", "-", "0", "20210228", "good", "-", "-"),
    ("80000001", "-", "-", "20210301", END, "neg:reversed", O1, "history"),
    ("80000002", "-", "-", "0", END, "good", "-", "-"),
    ("80000003", "-", "-", "0", "20220109", "good", "-", "-"),
    ("80000003", "-", "-", "20220110", END, "neg:vacated", O3, "history"),
    ("80000004", "-", "-", "0", "20220209", "good", "-", "-"),
    ("80000004", "-", "-", "20220210", END, "unknown:partialScope", O4, "history"),
    ("80000005", "-", "-", "0", END, "good", "-", "-"),
    ("80000005", "k1", "-", "0", END, "neg:reversed", O5, "history"),                     # issue-level: ignored
    ("80000006", "-", "-", "0", "20230419", "good", "-", "-"),
    ("80000006", "-", "-", "20230420", END, "neg:reversed", O6, "history"),
    ("80000007", "-", "-", "0", "20201231", "good", "-", "-"),
    ("80000007", "-", "-", "20210101", END, "neg:reversed", "70000002", "history"),
    ("80000008", "-", "-", "0", "20200101", "good", "-", "-"),
    ("80000008", "-", "-", "20200102", END, "neg:overruled", "70000003", "overruling"),
    ("80000009", "-", "-", "0", END, "good", "-", "-"),
]

# expected lines of tables.tsv: (group, value, measure) -> "k/n"
EXPECT = {
    ("kind", "reversed", "link: admitted row O->L"): "2/2",
    ("kind", "reversed", "kind: right kind"): "1/2",
    ("kind", "reversed", "effect (row): strict"): "2/2",
    ("kind", "reversed", "effect (status at d): strict"): "2/2",
    ("kind", "reversed", "effect (status at d): lenient"): "2/2",
    ("kind", "vacated", "link: admitted row O->L"): "0/3",
    ("kind", "vacated", "kind: right kind"): "0/3",
    ("kind", "vacated", "effect (row): strict"): "0/3",
    ("kind", "vacated", "effect (status at d): strict"): "0/3",
    ("kind", "vacated", "effect (status at d): lenient"): "1/3",
    ("kind", "mixed", "link: admitted row O->L"): "1/1",
    ("kind", "mixed", "kind: right kind"): "1/1",
    ("kind", "mixed", "effect (row): strict"): "1/1",
    ("kind", "mixed", "effect (status at d): strict"): "1/1",
    ("kind", "affirmed", "kind: right kind"): "1/1",
    ("kind", "affirmed", "effect (row): strict"): "1/1",
    ("kind", "affirmed", "effect (status at d): strict"): "1/1",
    ("kind", "reviewDismissed", "link: admitted row O->L"): "1/1",
    ("kind", "reviewDismissed", "kind: right kind"): "0/1",
    ("kind", "reviewDismissed", "effect (row): strict"): "0/1",
    ("kind", "reviewDismissed", "effect (status at d): strict"): "0/1",
    ("kind", "negative (reversed+vacated)", "link: admitted row O->L"): "2/5",
    ("kind", "all", "link: admitted row O->L"): "6/9",
    ("kind", "certDenied", "kind: right kind"): "1/1",
    ("kind", "certDenied", "effect (status at d): strict"): "1/1",
    ("system", "federal", "effect (status at d): strict"): "2/3",
    ("system", "state", "effect (status at d): strict"): "0/2",
    ("year", "2021", "effect (status at d): lenient"): "2/3",
    ("target", "all rows", "row points to a key lower decision of O"): "6/7",
    ("target", "rule family r7:memo", "row points to a key lower decision of O"): "1/1",
    ("target", "row kind certDenied", "row points to a key lower decision of O"): "1/2",
    ("target", "rule family r6:memo", "row points to a key lower decision of O"): "0/1",
    ("target", "rule family r6:below", "row points to a key lower decision of O"): "5/5",
    ("kind", "rows on a key pair", "row kind is right for the pair"): "4/6",
}
EXPECT_COUNT = {
    ("kind", "rows on an affirmed/dismissed/denied pair", "row of a negative kind (false negative effect)"): "1",
}


def write(name, header, rows):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as o:
        if header:
            o.write(header + "\n")
        for r in rows:
            o.write("\t".join(r) + "\n")


def main():
    write("key.tsv", "order_node\tlower_node\tkind\tsub\torder_date\tlower_date\tlower_court2\tsystem\tlink\t"
          "sc_docket", [(o, l, k, k, d, "20200601", "1", s, "exactDate", "00-1") for o, l, k, d, s in KEY])
    write("orders.tsv", "order_node\tdockets\tlinked\tcomplete", [(o, str(a), str(b), str(c)) for o, a, b, c in ORDERS])
    write("history.tsv", None, [(i, t, b, d, k, s, "0" * 40, "0", "1", "x", "name:x", "majority", src)
                                for i, t, b, d, k, s, src, v in HIST])
    write("certs.tsv", None, [("history", i, v, v) for i, t, b, d, k, s, src, v in HIST] +
          [("treatment", "t:1", "ok", "ok")])
    write("status.tsv", "node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath\toclass",
          [(n, i, h, f, t, s, "c", "1", "w", a, p, "-") for n, i, h, f, t, s, a, p in STATUS])
    res = os.path.join(HERE, "results")
    cmd = [sys.executable, "-I", SCORER, "--status", os.path.join(HERE, "status.tsv"), "--history",
           os.path.join(HERE, "history.tsv"), "--certs", os.path.join(HERE, "certs.tsv"), "--label", "fixture-selftest",
           "--key", os.path.join(HERE, "key.tsv"), "--orders", os.path.join(HERE, "orders.tsv"), "--results", res]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    got = {}
    status_rows = {}
    in_status = False
    with open(os.path.join(res, "tables.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if line.startswith("## status of the lower decision"):
                in_status = True
                continue
            if line.startswith("## "):
                in_status = False
            if in_status and p[0] in ("reversed", "vacated", "mixed", "affirmed", "reviewDismissed"):
                status_rows[p[0]] = p[1:]
            if len(p) >= 4:
                got[(p[0], p[1], p[2])] = p[3]
    bad = []
    for k, v in list(EXPECT.items()) + list(EXPECT_COUNT.items()):
        if got.get(k) != v:
            bad.append("%s: expected %s, got %s" % (" | ".join(k), v, got.get(k)))
    # status class table: vacated = 1 neg-history-other (pair 7), 1 neg-other-path (pair 8), 1 good (pair 2)
    exp_vac = ["0", "0", "1", "0", "1", "0", "1", "3"]
    if status_rows.get("vacated") != exp_vac:
        bad.append("status table vacated: expected %s, got %s" % (exp_vac, status_rows.get("vacated")))
    if bad:
        print("FIXTURE FAIL\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("fixture ok: %d checks" % (len(EXPECT) + len(EXPECT_COUNT) + 1))


if __name__ == "__main__":
    main()
