#!/usr/bin/env python3
"""Score a frozen build's same-case history against the round-7 held-out time-split key (HELDOUT.md).

    python -I score_heldout.py --status OUT/status.tsv --history STAGE/history.tsv --certs OUT/certs.tsv
                               --label NAME [--key key/timesplit_key.tsv] [--orders key/timesplit_orders.tsv]
                               [--results DIR]

The key is SCORED ONCE per frozen build, by the lead, after round7/FREEZE.md (HELDOUT.md section 6). Every run,
including fixture runs, appends one line to round7/heldout/RUNS.log (time, label, arguments, sha1 of the inputs,
sha1 of the result tables). Output is aggregate only: no per-pair line is printed or written.
Guards on the real key (key/timesplit_key.tsv): refused unless round7/FREEZE.md exists; refused when RUNS.log
already holds a run of the same key on the same status.tsv (sha1), unless --again '<reason>' is given (the reason
is logged with the arguments). A fixture key (--key elsewhere) has no guard.

Key: one line per (order node O = the acting Supreme Court decision, lower node L = the decision it reviewed)
with the expected kind K (reversed | vacated | mixed | affirmed | reviewDismissed | certDenied) and the order date d.

Model side:
  history rows (history.tsv: id, target, by, date, kind, scope, 6 CERT columns, src); a row is ADMITTED when its
  certs.tsv line (table "history") has a first verdict starting with "ok";
  status lines (status.tsv: node, issue, holding, from, to, status, class, firm, witness_row, actor, path, oclass):
  the decision-level line of L (issue "-", holding "-") with from <= d <= to.

Measures, per expected kind (and in total, by system, by order year):
  link      an admitted row by O on L exists (any kind);
  kind      an admitted row by O on L has the right kind (mixed: a reversed / vacated / affirmed / modified row whose
            scope is not "all", or a modified row);
  effect    the right status effect, read two ways:
              row:     the admitted rows by O on L give effect NEG (a reversed/vacated/withdrawn/substitutedBy/
                       depublished row with scope "all"), PART (such a row with another scope) or NONE;
                       expected NEG for reversed/vacated, PART for mixed (lenient: NEG or PART), NONE for
                       affirmed/reviewDismissed/certDenied;
              status:  strict = L's status at d is neg:* (reversed/vacated) / unknown:* (mixed) on path "history"
                       with actor O; lenient = neg:* or unknown:* on path "history" with any actor (reversed/
                       vacated/mixed); for affirmed/reviewDismissed/certDenied the status at d is NOT a history-path neg:* or
                       unknown:* with actor O (no false negative effect).
Precision side (orders whose every docket was linked: "complete" in timesplit_orders.tsv):
  target    of the admitted history rows by such an O, the share whose target is a key lower decision of O
            (the rest point to another decision); broken down by row kind and by rule family (src prefix);
  kind      of the admitted rows by O on a key L, the share with the right kind.
Wilson 95% intervals throughout.
"""
import argparse
import collections
import datetime
import hashlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS_LOG = os.path.join(HERE, "RUNS.log")
REAL_KEY = os.path.join(HERE, "key", "timesplit_key.tsv")
FREEZE = os.path.join(HERE, "..", "FREEZE.md")
KINDS = ["reversed", "vacated", "mixed", "affirmed", "reviewDismissed", "certDenied"]
NEG_KINDS = {"reversed", "vacated", "withdrawn", "substitutedBy", "depublished"}
MIXED_KINDS = {"reversed", "vacated", "affirmed", "modified"}


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k, n):
    if n == 0:
        return "%d/%d\t-\t-\t-" % (k, n)
    lo, hi = wilson(k, n)
    return "%d/%d\t%.1f%%\t%.1f%%\t%.1f%%" % (k, n, 100.0 * k / n, 100 * lo, 100 * hi)


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_tsv_header(path):
    with open(path, encoding="utf-8") as f:
        cols = f.readline().rstrip("\n").split("\t")
        for line in f:
            if line.strip():
                yield dict(zip(cols, line.rstrip("\n").split("\t")))


def kind_ok(expected, rows):
    """rows: [(kind, scope)] admitted rows by O on L."""
    if expected == "mixed":
        return any((k in MIXED_KINDS and s != "all") or k == "modified" for k, s in rows)
    return any(k == expected for k, s in rows)


def row_effect(rows):
    if any(k in NEG_KINDS and s == "all" for k, s in rows):
        return "NEG"
    if any(k in NEG_KINDS for k, s in rows):
        return "PART"
    return "NONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", required=True)
    ap.add_argument("--history", required=True)
    ap.add_argument("--certs", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--key", default=os.path.join(HERE, "key", "timesplit_key.tsv"))
    ap.add_argument("--orders", default=os.path.join(HERE, "key", "timesplit_orders.tsv"))
    ap.add_argument("--results", default=None, help="default round7/heldout/results/<label>/")
    ap.add_argument("--again", default=None, help="reason for a second run of the real key on the same build "
                                                  "(written to RUNS.log)")
    a = ap.parse_args()
    res = a.results or os.path.join(HERE, "results", a.label)
    # the real key: only after round7/FREEZE.md, and once per frozen build (same status.tsv sha1) unless --again
    if os.path.normcase(os.path.abspath(a.key)) == os.path.normcase(REAL_KEY):
        if not os.path.exists(FREEZE):
            sys.exit("refused: the held-out key is scored only after round7/FREEZE.md exists. Nothing was read.")
        ks, ss = sha1(a.key), sha1(a.status)
        if os.path.exists(RUNS_LOG) and not a.again:
            with open(RUNS_LOG, encoding="utf-8") as f:
                for line in f:
                    if "key_sha1=%s" % ks in line and "status_sha1=%s" % ss in line:
                        sys.exit("refused: this build (status.tsv sha1 %s) was already scored on the held-out key "
                                 "(RUNS.log). Use --again '<reason>' only if the lead decides so." % ss)

    key = list(read_tsv_header(a.key))
    complete = {r["order_node"] for r in read_tsv_header(a.orders) if r["complete"] == "1"}
    O = {r["order_node"] for r in key}
    L = {r["lower_node"] for r in key}
    lower_of = collections.defaultdict(set)
    for r in key:
        lower_of[r["order_node"]].add(r["lower_node"])

    # admitted history rows
    adm = set()
    with open(a.certs, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0] == "history" and p[2].startswith("ok"):
                adm.add(p[1])
    by_pair = collections.defaultdict(list)  # (O, L) -> [(kind, scope)]
    by_order = collections.defaultdict(list)  # O -> [(target, kind, scope, src)]
    n_hist = 0
    with open(a.history, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 6:
                continue
            n_hist += 1
            if p[2] not in O or p[0] not in adm:
                continue
            by_order[p[2]].append((p[1], p[4], p[5], p[-1]))
            by_pair[(p[2], p[1])].append((p[4], p[5]))
    # decision-level status lines of the key's lower decisions
    st = collections.defaultdict(list)
    with open(a.status, encoding="utf-8") as f:
        f.readline()
        for line in f:
            i = line.find("\t")
            if line[:i] not in L:
                continue
            p = line.rstrip("\n").split("\t")
            if p[1] == "-" and p[2] == "-":
                st[p[0]].append((int(p[3]), int(p[4]), p[5], p[9], p[10]))

    recs = []
    for r in key:
        o, l, k, d = r["order_node"], r["lower_node"], r["kind"], int(r["order_date"])
        rows = by_pair.get((o, l), [])
        line = next((x for x in st.get(l, []) if x[0] <= d <= x[1]), None)
        status, actor, path = (line[2], line[3], line[4]) if line else ("good", "-", "-")
        hist_neg = path == "history" and status.startswith("neg:")
        hist_unk = path == "history" and status.startswith("unknown:")
        rec = dict(kind=k, system=r.get("system", "-"), year=r["order_date"][:4], link_how=r.get("link", "-"),
                   link=int(bool(rows)), kok=int(kind_ok(k, rows)), reff=row_effect(rows))
        if k in ("reversed", "vacated"):
            rec["row_ok"] = int(rec["reff"] == "NEG")
            rec["row_len"] = rec["row_ok"]
            rec["st_strict"] = int(hist_neg and actor == o)
            rec["st_len"] = int(hist_neg or hist_unk)
        elif k == "mixed":
            rec["row_ok"] = int(rec["reff"] == "PART")
            rec["row_len"] = int(rec["reff"] in ("PART", "NEG"))
            rec["st_strict"] = int(hist_unk and actor == o)
            rec["st_len"] = int(hist_neg or hist_unk)
        else:
            rec["row_ok"] = int(rec["reff"] == "NONE")
            rec["row_len"] = rec["row_ok"]
            rec["st_strict"] = int(not ((hist_neg or hist_unk) and actor == o))
            rec["st_len"] = rec["st_strict"]
        rec["status_class"] = ("neg-history-O" if hist_neg and actor == o else "neg-history-other" if hist_neg else
                               "unknown-history-O" if hist_unk and actor == o else
                               "unknown-history-other" if hist_unk else
                               "neg-other-path" if status.startswith("neg:") else
                               "unknown-other-path" if status.startswith("unknown:") else "good")
        recs.append(rec)

    out = []
    w = out.append
    w("# round-7 held-out time split; label %s; key %s (%d pairs, %d orders, %d complete)" %
      (a.label, os.path.basename(a.key), len(key), len(O), len(O & complete)))
    w("# history rows read %d; admitted history ids %d" % (n_hist, len(adm)))
    hdr = "group\tvalue\tmeasure\tk/n\tshare\tlo95\thi95"

    def block(title, groups):
        w("\n## " + title)
        w(hdr)
        for gname, gval, sel in groups:
            if not sel:
                continue
            for m, lab in (("link", "link: admitted row O->L"), ("kok", "kind: right kind"),
                           ("row_ok", "effect (row): strict"), ("row_len", "effect (row): lenient"),
                           ("st_strict", "effect (status at d): strict"), ("st_len", "effect (status at d): lenient")):
                w("%s\t%s\t%s\t%s" % (gname, gval, lab, pct(sum(x[m] for x in sel), len(sel))))

    block("recall by expected kind", [("kind", k, [x for x in recs if x["kind"] == k]) for k in KINDS] +
          [("kind", "negative (reversed+vacated)", [x for x in recs if x["kind"] in ("reversed", "vacated")]),
           ("kind", "all", recs)])
    block("recall by lower-court system (negative kinds: reversed+vacated)",
          [("system", s, [x for x in recs if x["system"] == s and x["kind"] in ("reversed", "vacated")])
           for s in sorted({x["system"] for x in recs})])
    block("recall by order year (negative kinds: reversed+vacated)",
          [("year", y, [x for x in recs if x["year"] == y and x["kind"] in ("reversed", "vacated")])
           for y in sorted({x["year"] for x in recs})])
    block("recall by lower link method (all kinds)",
          [("link", h, [x for x in recs if x["link_how"] == h]) for h in sorted({x["link_how"] for x in recs})])

    w("\n## status of the lower decision at the order date, by expected kind (counts)")
    classes = ["neg-history-O", "unknown-history-O", "neg-history-other", "unknown-history-other", "neg-other-path",
               "unknown-other-path", "good"]
    w("kind\t" + "\t".join(classes) + "\ttotal")
    for k in KINDS:
        sel = [x for x in recs if x["kind"] == k]
        if sel:
            c = collections.Counter(x["status_class"] for x in sel)
            w("%s\t%s\t%d" % (k, "\t".join(str(c[s]) for s in classes), len(sel)))

    w("\n## row effect by expected kind (counts of NEG / PART / NONE from admitted rows O->L)")
    w("kind\tNEG\tPART\tNONE\ttotal")
    for k in KINDS:
        sel = [x for x in recs if x["kind"] == k]
        if sel:
            c = collections.Counter(x["reff"] for x in sel)
            w("%s\t%d\t%d\t%d\t%d" % (k, c["NEG"], c["PART"], c["NONE"], len(sel)))

    # precision side
    w("\n## precision: admitted history rows by a complete key order")
    w(hdr)
    rows_c = [(o, t, k, s, src) for o in sorted(O & complete) for (t, k, s, src) in by_order.get(o, [])]
    good = [x for x in rows_c if x[1] in lower_of[x[0]]]
    w("target\tall rows\trow points to a key lower decision of O\t" + pct(len(good), len(rows_c)))
    for kd in sorted({x[2] for x in rows_c}):
        sel = [x for x in rows_c if x[2] == kd]
        w("target\trow kind %s\trow points to a key lower decision of O\t" % kd +
          pct(sum(x[1] in lower_of[x[0]] for x in sel), len(sel)))
    fam = lambda src: src.split(":")[0] + (":" + src.split(":")[1] if src.count(":") >= 1 else "")
    for fm in sorted({fam(x[4]) for x in rows_c}):
        sel = [x for x in rows_c if fam(x[4]) == fm]
        w("target\trule family %s\trow points to a key lower decision of O\t" % fm +
          pct(sum(x[1] in lower_of[x[0]] for x in sel), len(sel)))
    exp = {(r["order_node"], r["lower_node"]): r["kind"] for r in key}
    kp = [(exp[(x[0], x[1])], x[2], x[3]) for x in good]
    w("kind\trows on a key pair\trow kind is right for the pair\t" +
      pct(sum(kind_ok(e, [(k, s)]) for e, k, s in kp), len(kp)))
    neg_wrong = sum(1 for e, k, s in kp if e in ("affirmed", "reviewDismissed", "certDenied") and k in NEG_KINDS)
    w("kind\trows on an affirmed/dismissed/denied pair\trow of a negative kind (false negative effect)\t%d" % neg_wrong)
    w("orders\tcomplete key orders with no admitted history row at all\t\t%d of %d" %
      (sum(1 for o in O & complete if not by_order.get(o)), len(O & complete)))

    os.makedirs(res, exist_ok=True)
    tpath = os.path.join(res, "tables.tsv")
    with open(tpath, "w", encoding="utf-8", newline="\n") as o:
        o.write("\n".join(out) + "\n")
    print("\n".join(out))
    rh = sha1(tpath)
    with open(RUNS_LOG, "a", encoding="utf-8", newline="\n") as o:
        o.write("%s\tlabel=%s\targs=%s\tkey_sha1=%s\tstatus_sha1=%s\thistory_sha1=%s\tcerts_sha1=%s\t"
                "result_sha1=%s\n" % (datetime.datetime.now().astimezone().isoformat(timespec="seconds"), a.label,
                                      " ".join(sys.argv[1:]), sha1(a.key), sha1(a.status), sha1(a.history),
                                      sha1(a.certs), rh))
    sys.stderr.write("results: %s (sha1 %s); RUNS.log appended\n" % (tpath, rh))


if __name__ == "__main__":
    main()
