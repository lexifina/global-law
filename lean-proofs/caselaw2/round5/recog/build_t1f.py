"""Round 5, agent `recog`: tier T1f, the loose T1s items cut down to those that can be certified at all.

    python -X utf8 build_t1f.py [--size 50] [--three-only]
                                [--skip pack_T1s_013.md,pack_T1s_029.md,pack_T1s_045.md,pack_T1s_061.md]

Input: the loose items of tier T1s (items_t1s.jsonl.gz, strict = 0) that are not in the packs named by --skip (the
sample the readers already have).

Test 1 (the three things). An item passes only if some span of at most 400 characters of its WINDOW (the text
shown to the reader, normalised) holds all three things a certifiable quote needs, tested with the certifier's own
functions:
  - a cue: a word-start overrul / abrogat / disapprov / reced (recog_common.CUE_WORD) and a phrase of the cue
    table's list `recognised` (reader/cue_table.py) in the span;
  - an evidence for X that certify_recog.py would take (recog_common.evidence_for: X's citation resolving to X
    through data/cite_index.tsv or uniquely through graph/cite_index.tsv, else a distinctive caption word of X);
  - the same for Y, and the two evidences differ.
A span that holds all three can be moved to begin at the leftmost of them, so the spans tried are those that begin
at a cue, at a citation or at a capitalised word, and run 400 characters.
(scan_scotus.py made its candidates under nearly the same condition, so this test alone drops almost nothing.)

Test 2 (the rest of the precondition; off with --three-only). Every certifiable quote contains one occurrence of
the cue, one of X's evidence and one of Y's, hence the smallest span that covers those three occurrences. The item
passes only if, for some choice of occurrences, that smallest span is at most 400 characters, holds no phrase of
the cue table's list `disqualify_recognised`, and lies inside one opinion-of-the-court part. If every smallest span
fails, no quote can be certified whatever the reader answers. (A caption word of two pieces that are not printed
next to each other is not located; such an item is kept.)

Kept items stay in the order of the T1s packs (by X's date); the length of the shortest passing span is recorded
in the index only.

Writes packs/pack_T1f_<nnn>.md (same item format and ids as the T1s packs), packs/index_T1f.tsv (item id, pack,
tier, W, X, Y, note scope, shortest span), packs/T1f_dropped.tsv (item id, reason) and packs/summary_T1f.json.
It does not touch any other pack, packs/index.tsv or ans/.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

import recog_common as R
import build_packs

RC = R.RC
SPAN = 400
START = re.compile(r"\b(?:[A-Z]|\d)")


def window(it):
    return R.clean(it["text"][it["d0"] - it["s0"]:it["d1"] - it["s0"]])


def three_things(it, cw, live, graph):
    """Test 1 -> (passes, reason)."""
    cues = [(m.start(), m.end()) for m in R.CUE_WORD.finditer(cw)]
    if not cues:
        return False, "no-cue-in-window"
    xn, yn = it["X"]["name"], it["Y"]["name"]
    if R.evidence_for(it["x"], xn, yn, cw, live, graph)[0] is None:
        return False, "x-not-in-window"
    if R.evidence_for(it["y"], yn, xn, cw, live, graph)[0] is None:
        return False, "y-not-in-window"
    starts = sorted({m.start() for m in START.finditer(cw)} | {c[0] for c in cues})
    for (c0, c1) in cues:
        for s in starts:
            if s > c0:
                break
            if c1 > s + SPAN:
                continue
            span = cw[max(0, s - 1):s + SPAN]
            if not (R.cue_ok(span) and R.CUE_WORD.search(span)):
                continue
            sx = R.evidence_for(it["x"], xn, yn, span, live, graph)[0]
            if sx is None:
                continue
            sy = R.evidence_for(it["y"], yn, xn, span, live, graph)[0]
            if sy is None or R.alnum(sx.split(":", 1)[1]) == R.alnum(sy.split(":", 1)[1]):
                continue
            return True, ""
    return False, "not-in-one-span"


def occurrences(node, name, other, cw, live, graph):
    """([(start, end)] of every place in cw that the certifier could take as evidence for the node, unlocated):
    citations that resolve to it, and its distinctive caption words. `unlocated` is True when a caption word of
    several pieces has its pieces in the window but not next to each other."""
    occ = []
    for m in RC.CITE_RX.finditer(cw):
        k = RC.cite_key(m)
        if not k:
            continue
        c = R.alnum(k)
        if live.get(c) == node or (c not in live and graph.get(k) == {node}):
            occ.append((m.start(), m.end()))
    unlocated = False
    words = set(re.findall(r"[0-9A-Za-z]+", cw))
    for pieces in R.caption_words(name, other):
        rx = re.compile(r"(?<![0-9A-Za-z])" + r"[^0-9A-Za-z]+".join(re.escape(p) for p in pieces) + r"(?![0-9A-Za-z])")
        found = [(m.start(), m.end()) for m in rx.finditer(cw)]
        occ.extend(found)
        if not found and len(pieces) > 1 and all(p in words for p in pieces):
            unlocated = True
    return occ, unlocated


def smallest_span(it, cw, live, graph):
    """Test 2 -> (passes, reason, length of the shortest passing span or 0)."""
    xn, yn = it["X"]["name"], it["Y"]["name"]
    cues = [(m.start(), m.end()) for m in R.CUE_WORD.finditer(cw)]
    xo, ux = occurrences(it["x"], xn, yn, cw, live, graph)
    yo, uy = occurrences(it["y"], yn, xn, cw, live, graph)
    if ux or uy:
        return True, "", SPAN
    best = 0
    seen = collections.Counter()
    for (c0, c1) in cues:
        for (x0, x1) in xo:
            for (y0, y1) in yo:
                s, e = min(c0, x0, y0), max(c1, x1, y1)
                if e - s > SPAN:
                    seen["not-in-one-span"] += 1
                    continue
                span = cw[s:e]
                lead = cw[s - 1:s] if s > 0 else ""       # " reced" needs the blank before the word
                if not R.cue_ok(lead + span):
                    seen["not-in-one-span"] += 1
                    continue
                sx = R.evidence_for(it["x"], xn, yn, span, live, graph)[0]
                sy = R.evidence_for(it["y"], yn, xn, span, live, graph)[0]
                if sx is None or sy is None or R.alnum(sx.split(":", 1)[1]) == R.alnum(sy.split(":", 1)[1]):
                    seen["not-in-one-span"] += 1
                    continue
                if R.disqualifiers_in(span):
                    seen["disqualifier-in-every-span"] += 1
                    continue
                a0, a1 = it["d0"] + s, it["d0"] + e
                part = next((pp for (pa, pb, pp) in it.get("parts", []) if pa <= a0 < pb and a1 <= pb), None)
                if part not in R.CERT_PARTS:
                    seen["not-in-one-court-part"] += 1
                    continue
                if not best or e - s < best:
                    best = e - s
    if best:
        return True, "", best
    for why in ("disqualifier-in-every-span", "not-in-one-court-part", "not-in-one-span"):
        if seen[why]:
            return False, why, 0
    return False, "not-in-one-span", 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--three-only", action="store_true", help="test 1 only (cue, X and Y in one span)")
    ap.add_argument("--skip", default="pack_T1s_013.md,pack_T1s_029.md,pack_T1s_045.md,pack_T1s_061.md")
    a = ap.parse_args()
    out = os.path.join(R.HERE, "packs")
    skip_packs = set(a.skip.split(","))
    order, sampled = [], set()
    for p in R.read_rows(os.path.join(out, "index.tsv"), 3):
        if p[2] == "T1s":
            order.append(p[0])
            if p[1] in skip_packs:
                sampled.add(p[0])
    items = R.load_items(R.ITEMS_T1S)
    loose = [items[i] for i in order if i in items and not items[i]["strict"]]
    todo = [it for it in loose if it["id"] not in sampled]
    live = R.live_cite_index()
    keys = set()
    for it in todo:
        keys.update(k for k, c in R.cite_keys_in(window(it)) if c not in live)
    graph = R.graph_cite_rows(keys)
    kept, dropped, why = [], [], collections.Counter()
    pass1 = 0
    for it in todo:
        cw = window(it)
        ok, reason = three_things(it, cw, live, graph)
        best = SPAN
        if ok:
            pass1 += 1
            if not a.three_only:
                ok, reason, best = smallest_span(it, cw, live, graph)
        if ok:
            it["_best"] = best
            kept.append(it)
        else:
            dropped.append([it["id"], reason])
            why[reason] += 1
    # order: as in the T1s packs (by X's date). Ordering by span length was tried and dropped: the shortest spans
    # are "we are asked to overrule X and Y", not statements.
    for f in glob.glob(os.path.join(out, "pack_T1f_*.md")):
        os.remove(f)
    index = []
    packs = [kept[i:i + a.size] for i in range(0, len(kept), a.size)]
    for k, pk in enumerate(packs):
        name = "pack_T1f_%03d.md" % (k + 1)
        R.write_text(os.path.join(out, name), "\n\n".join(build_packs.render(it) for it in pk) + "\n")
        for it in pk:
            index.append([it["id"], name, "T1f", it["w"], it["x"], it["y"], it["note_scope"], it["_best"]])
    R.write_rows(os.path.join(out, "index_T1f.tsv"), index)
    R.write_rows(os.path.join(out, "T1f_dropped.tsv"), dropped)
    lens = sorted(it["_best"] for it in kept)
    summ = {"loose_items": len(loose), "in_sample_packs_not_filtered": len(loose) - len(todo),
            "filtered": len(todo), "pass_test1_three_things": pass1, "kept": len(kept), "dropped": len(dropped),
            "dropped_by_reason": dict(why), "packs": len(packs), "skip_packs": sorted(skip_packs),
            "three_only": a.three_only, "kept_pair_explicit": sum(it["pair_explicit"] for it in kept),
            "shortest_span_quartiles": [lens[len(lens) * q // 4] for q in (1, 2, 3)] if lens else []}
    R.write_text(os.path.join(out, "summary_T1f.json"), json.dumps(summ, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
