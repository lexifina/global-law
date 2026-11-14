"""Round 5, agent `recog`: mechanical re-check of every staged recognised row, from the delta files, the live data
tables and the corpus at git HEAD (not from the items or the answers).

    python -X utf8 verify_recog.py [--cert cert] [--no-engine]

Checked rows: every id of <cert>/treatment_class_delta.tsv (its treatments / witness row is the delta row, or the
live row when the id is live and not in remove_ids.txt). For each row, every failure is listed:

  shape            16 columns, id = tw:<Y>:<X>:<start>:<W>, explicit 0, a status-changing kind, a known scope, part
                   majority | plurality | perCuriam, a witness line naming W, a class line `recognised` of 5 fields,
                   field_limit / doctrine one line each
  duplicate        the id occurs twice, or is live and not listed for removal
  text-sha         W's bytes at HEAD hash to the row's text_sha and to W's text_sha in decisions2.tsv
  quote            the normalised text at [start, end) equals the quote; the quote is at most 400 characters
  window           a window row (delta or live cert_text.tsv) covers the quote, equals the corpus cut, and its hash
                   is in window_sha (delta or live)
  cue              the lower-cased quote holds a phrase of the cue list `recognised`
  disqualified     ... and none of `disqualify_recognised`
  x-evidence       the target evidence resolves INSIDE the quote to X (cite: compact form in the compact quote and
                   data/cite_index.tsv + delta gives X, a key with two nodes resolving to nothing; name: every
                   word of 3+ characters is a whole word of the quote)
  y-evidence       the same for the by-evidence and Y
  same-evidence    the two evidences are the same text
  dates            date(X) <= date(Y) <= date(W), none 0; the row's date is date(Y)
  part             reader/common.part_map2 of W's text puts [start, end) in one opinion-of-the-court part, the one
                   the row names
  power            (engine) the reference's can_change(W, X) is yes; can_change(Y, X) is not no
  provenance       (W, X) is a (note_node, target_node) pair of round5/tests/split/feed_ids.tsv, or the row
                   re-reads a round-4 witness row of the same (Y, X, W), or (W, X, Y) is a candidate of our own
                   Supreme Court scan (candidates_t1s.tsv)

Writes <cert>/verify_failures.tsv (id, check, detail) and <cert>/verify_summary.json. Exit 1 when any row fails.
"""
import argparse
import collections
import json
import os
import re
import sys

import recog_common as R

RC = R.RC
SCOPES = ("all", "partialUnknown", "otherGrounds")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cert", default=os.path.join(R.HERE, "cert"))
    ap.add_argument("--no-engine", action="store_true")
    a = ap.parse_args()

    def rd(name, minf=1):
        return R.read_rows(os.path.join(a.cert, name), minf)

    d_t, d_w, d_c = rd("treatments_delta.tsv"), rd("treatment_witness_delta.tsv"), rd("treatment_class_delta.tsv")
    remove = {p[0] for p in rd("remove_ids.txt")}
    live_t = {p[0]: p for p in R.read_rows(os.path.join(R.DATA, "treatments.tsv"), 16)}
    live_w = {p[0]: p for p in R.read_rows(os.path.join(R.DATA, "treatment_witness.tsv"), 4)}
    fails = []
    idc = collections.Counter(p[0] for p in d_t)
    dt = {p[0]: p for p in d_t}
    dw = {p[0]: p for p in d_w}
    rows = []
    for c in d_c:
        tid = c[0]
        t = dt.get(tid) or live_t.get(tid)
        w = dw.get(tid) or live_w.get(tid)
        if t is None or w is None:
            fails.append([tid, "shape", "class line without a treatments row or a witness line"])
            continue
        if idc[tid] > 1:
            fails.append([tid, "duplicate", "id %d times in the delta" % idc[tid]])
        if tid in dt and tid in live_t and tid not in remove:
            fails.append([tid, "duplicate", "id is live and not in remove_ids.txt"])
        rows.append((tid, t, w, c))
    for tid in dt:
        if tid not in {c[0] for c in d_c}:
            fails.append([tid, "shape", "delta row without a class line"])
    for tid, n in collections.Counter(c[0] for c in d_c).items():
        if n > 1:
            fails.append([tid, "duplicate", "class line %d times" % n])

    wnodes = set()
    for tid, t, w, c in rows:
        try:
            wnodes.update((int(w[1]), int(t[1]), int(t[2])))
        except ValueError:
            pass
    ninfo = R.nodes_info(wnodes)
    dinfo = R.decisions_info(wnodes)

    # texts of the W's
    need = collections.defaultdict(dict)
    for tid, t, w, c in rows:
        wn = int(w[1])
        if wn in ninfo:
            need[ninfo[wn][0]][ninfo[wn][1]] = wn
    text, tsha, pmap = {}, {}, {}
    for repo, paths in need.items():
        raws = R.git_texts(repo, sorted(paths))
        for path, wn in paths.items():
            raw = raws.get(path)
            if raw is not None:
                tsha[wn] = R.sha1_bytes(raw)
                text[wn] = R.decode(raw)

    # windows and hashes (delta, then live for the same shas)
    shas = {t[8] for _, t, _, _ in rows}
    wins = collections.defaultdict(list)
    for p in rd("cert_text_delta.tsv", 4):
        wins[p[0]].append((int(p[1]), int(p[2]), "\t".join(p[3:])))
    with open(os.path.join(R.DATA, "cert_text.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            i = line.find("\t")
            if line[:i] in shas:
                p = line.rstrip("\n").rstrip("\r").split("\t", 3)
                if len(p) == 4:
                    wins[p[0]].append((int(p[1]), int(p[2]), p[3]))
    whash = collections.defaultdict(set)
    for p in rd("window_sha_delta.tsv", 4):
        whash[(p[0], int(p[1]), int(p[2]))].add(p[3])
    with open(os.path.join(R.DATA, "window_sha.tsv"), encoding="utf-8") as f:
        for line in f:
            i = line.find("\t")
            if line[:i] in shas:
                p = line.rstrip("\n").split("\t")
                whash[(p[0], int(p[1]), int(p[2]))].add(p[3])

    # the citation index as the checkers will load it after the delta is installed
    m = collections.defaultdict(set)
    for p in R.read_rows(os.path.join(R.DATA, "cite_index.tsv"), 2) + rd("cite_index_delta.tsv", 2):
        k = R.alnum(p[0])
        if k:
            m[k].add(int(p[1]))
    index = {k: (next(iter(v)) if len(v) == 1 else None) for k, v in m.items()}

    # provenance: feed pairs (W, X); the feed file only
    feed = set()
    want_pairs = {(int(w[1]), int(t[2])) for _, t, w, _ in rows}
    with open(R.FEED, encoding="utf-8") as f:
        f.readline()
        for line in f:
            p = line.split("\t", 4)
            k = (int(p[1]), int(p[3]))
            if k in want_pairs:
                feed.add(k)
    old_triples = set()
    for tid, w in live_w.items():
        t = live_t.get(tid)
        if t is not None:
            old_triples.add((int(t[1]), int(t[2]), int(w[1])))
    # tier T1s: our own scan of the Supreme Court's opinions (scan_scotus.py), W and X both Supreme Court decisions
    for p in R.read_rows(os.path.join(R.HERE, "candidates_t1s.tsv"), 5)[1:]:
        old_triples.add((int(p[4]), int(p[3]), int(p[2])))

    E = None
    if not a.no_engine:
        C = R.tests_common()
        E, _pr, _meta = C.lite_engine(R.DATA)

    for tid, t, w, c in rows:
        def bad(check, detail=""):
            fails.append([tid, check, detail])
        if len(t) != 16:
            bad("shape", "%d columns" % len(t))
            continue
        _id, by, x, date, kind, scope, temporal, expl, sha, s, e, q, ev, part, reader, conf = t
        try:
            by, x, date, s, e, wn = int(by), int(x), int(date), int(s), int(e), int(w[1])
        except ValueError:
            bad("shape", "non-numeric field")
            continue
        if tid != "tw:%d:%d:%d:%d" % (by, x, s, wn):
            bad("shape", "id is not tw:<Y>:<X>:<start>:<W>")
        if expl != "0" or kind not in R.NEG_KINDS or scope not in SCOPES or part not in R.CERT_PARTS:
            bad("shape", "explicit/kind/scope/part: %s %s %s %s" % (expl, kind, scope, part))
        if len(w) != 4 or len(c) != 5 or c[1] != "recognised" or not c[2] or not c[3]:
            bad("shape", "witness line or class line")
        if wn not in dinfo or x not in dinfo or by not in dinfo:
            bad("dates", "a node has no decisions2 row")
            continue
        xd, yd, wd = dinfo[x][1], dinfo[by][1], dinfo[wn][1]
        if not (xd and yd and wd and xd <= yd <= wd) or date != yd:
            bad("dates", "X %d Y %d W %d row %d" % (xd, yd, wd, date))
        tx = text.get(wn)
        if tx is None:
            bad("text-sha", "no text for W at HEAD")
            continue
        if not (tsha[wn] == sha == dinfo[wn][2]):
            bad("text-sha", "HEAD %s row %s decisions2 %s" % (tsha[wn][:10], sha[:10], dinfo[wn][2][:10]))
        if R.clean(tx[s:e]) != q or len(q) != e - s:
            bad("quote", "text at offsets differs from the quote")
        if len(q) > 400:
            bad("quote", "%d characters" % len(q))
        cover = [(a0, b0, wt) for (a0, b0, wt) in wins.get(sha, []) if a0 <= s and e <= b0]
        okw = [1 for (a0, b0, wt) in cover if R.clean(tx[a0:b0]) == wt and len(wt) == b0 - a0
               and R.sha1_text(wt) in whash.get((sha, a0, b0), ())]
        if not okw:
            bad("window", "no covering window that equals the corpus cut with a matching hash (%d cover)" % len(cover))
        if not R.cue_ok(q):
            bad("cue")
        dq = R.disqualifiers_in(q)
        if dq:
            bad("disqualified", dq[0])
        if not R.resolve_in_quote(ev, q, x, index):
            bad("x-evidence", ev)
        if not R.resolve_in_quote(w[2], q, by, index):
            bad("y-evidence", w[2])
        if R.alnum(ev.split(":", 1)[-1]) == R.alnum(w[2].split(":", 1)[-1]):
            bad("same-evidence", ev)
        if wn not in pmap:
            pmap[wn] = RC.part_map2(tx)[0]
        p0 = [(pa, pb, pp) for (pa, pb, pp, _s) in pmap[wn] if pa <= s < pb]
        if not p0 or e > p0[0][1] or R.PART_OUT.get(p0[0][2], p0[0][2]) != part:
            bad("part", "part map: %s" % (p0[0][2] if p0 else "none"))
        if (wn, x) not in feed and (by, x, wn) not in old_triples:
            bad("provenance", "(W, X) is not a feed pair; no round-4 witness row or T1s candidate has this (Y, X, W)")
        if E is not None:
            cc = E.can_change(wn, x, "unknown")
            if cc[0] != "yes":
                bad("power", "W over X: %s %s" % cc)
            cy = E.can_change(by, x, "unknown")
            if cy[0] == "no":
                bad("power", "Y over X: %s %s" % cy)

    R.write_rows(os.path.join(a.cert, "verify_failures.tsv"), fails)
    failed = {f[0] for f in fails}
    summ = {"rows_checked": len(rows), "rows_failing": len(failed), "failures": len(fails),
            "by_check": dict(collections.Counter(f[1] for f in fails)), "engine": E is not None}
    R.write_text(os.path.join(a.cert, "verify_summary.json"), json.dumps(summ, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    for f in fails[:40]:
        print("\t".join(f))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
