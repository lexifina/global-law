"""Round 5, agent `recog`: tier T2p, the "overruled on other grounds by" notes certified by pattern, with no reader.

    python -X utf8 certify_pattern.py [--out cert_pattern] [--tiers T2]

Input: the items of tier T2 (items.jsonl.gz) whose note has scope otherGrounds. Only the strict citator form is
taken, at the note's own position in W's text:

    <X-citation> [, pin] [(court year)] ... , overruled|abrogated|disapproved [of] [in part] on other|another|
    different ground[s] by|in <Y's caption>, <Y-citation>

  - the last citation before the phrase that resolves to X (data/cite_index.tsv, or uniquely graph/cite_index.tsv)
    starts the quote; between it and the phrase (at most 250 characters) there is no other decision: no citation
    that resolves to another node, no " v. ", no history word (aff'd, rev'd, vacated, modified, sub nom., ...),
    no semicolon and no sentence end outside parentheses;
  - the first citation after the phrase (within 200 characters, no ";" before it, no citation of another node
    before it) resolves to Y and ends the quote;
  - the quote is at most 400 characters.
Each match becomes an answer line (pattern/ans/ans_pattern.jsonl: states true, kind from the word, scope
otherGrounds) and goes through certify_recog.py with --cite-only, reader `pattern-r5`, src `pattern:otherGrounds`:
the same cue, disqualifier, part, quotation, date and in-quote resolution checks as for a reader's answer.
Output: the file set of cert/ in <out>/, plus pattern/pattern_rejects.tsv and pattern/pattern_stats.json.
"""
import argparse
import collections
import json
import os
import re
import sys

import recog_common as R
import certify_recog

RC = R.RC
PH = re.compile(r"\b(overruled|abrogated|disapproved)(?:\s+of)?(?:\s+in\s+part)?,?\s+on\s+(?:other|another|different)"
                r"\s+grounds?,?\s+(?:by|in)\b,?\s*", re.I)
HIST = re.compile(r"aff(?:'|’)?d|affirmed|rev(?:'|’)?d|reversed|vacated|sub\s+nom|modified|remanded|superseded|"
                  r"cert\.\s+granted|reh(?:'|’)?g|rehearing", re.I)
VS = re.compile(r"\sv\.?\s|\bIn\s+re\b|\bEx\s+parte\b", re.I)
KIND = {"overruled": "overruled", "abrogated": "abrogated", "disapproved": "disapproved"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(R.HERE, "cert_pattern"))
    ap.add_argument("--tiers", default="T2")
    a = ap.parse_args()
    tiers = set(a.tiers.split(","))
    items = [it for it in R.load_items(R.ITEMS).values() if it["tier"] in tiers and it["note_scope"] == "otherGrounds"]
    items.sort(key=lambda it: it["id"])
    st = collections.OrderedDict()
    st["items_other_grounds"] = len(items)
    cnt = collections.Counter()
    rejects = []

    # pass 1: the phrase and the citations around it
    work = []
    keys = set()
    for it in items:
        s0 = it["s0"]
        cw = R.clean(it["text"])
        off = it["off"] - s0
        m = PH.search(cw, max(0, off - 2), off + 140)
        if m is None or m.start() > off + 60:
            rejects.append([it["id"], "no-strict-phrase"])
            cnt["no-strict-phrase"] += 1
            continue
        b0 = max(0, m.start() - 380)
        before = [(b0 + c.start(), b0 + c.end(), RC.cite_key(c)) for c in RC.CITE_RX.finditer(cw[b0:m.start()])]
        after = [(m.end() + c.start(), m.end() + c.end(), RC.cite_key(c))
                 for c in RC.CITE_RX.finditer(cw[m.end():m.end() + 260])]
        before = [c for c in before if c[2]]
        after = [c for c in after if c[2]]
        keys.update(c[2] for c in before + after)
        work.append((it, cw, m, before, after))
    live = R.live_cite_index()
    graph = R.graph_cite_rows(keys)

    def node_of(k):
        """The node a citation key names: live index first, else the graph index when it names one node. -1 when
        the key is known but ambiguous, None when it is unknown (a parallel reporter)."""
        c = R.alnum(k)
        if c in live:
            return live[c] if live[c] is not None else -1
        g = graph.get(k)
        if not g:
            return None
        return next(iter(g)) if len(g) == 1 else -1

    lines = []
    for it, cw, m, before, after in work:
        def no(why):
            rejects.append([it["id"], why])
            cnt[why] += 1
        xi = [i for i, c in enumerate(before) if node_of(c[2]) == it["x"]]
        if not xi:
            no("x-citation-not-before-phrase")
            continue
        xc = before[xi[-1]]
        if any(node_of(c[2]) not in (None, it["x"]) for c in before[xi[-1] + 1:]):
            no("another-decision-cited-between")
            continue
        between = cw[xc[1]:m.start()]
        if len(between) > 250:
            no("x-citation-too-far")
            continue
        if VS.search(between):
            no("case-name-between")
            continue
        flat = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", "", between) + " x"
        if ";" in between or any(flat[i] in ".!?" and RC._is_end(flat, i) for i in range(len(flat) - 2)):
            no("sentence-or-semicolon-between")
            continue
        if HIST.search(between):
            no("history-word-between")
            continue
        yi = [i for i, c in enumerate(after) if node_of(c[2]) == it["y"]]
        if not yi or after[yi[0]][0] - m.end() > 200:
            no("y-citation-not-after-phrase")
            continue
        yc = after[yi[0]]
        if any(node_of(c[2]) not in (None, it["y"]) for c in after[:yi[0]]):
            no("another-decision-cited-before-y")
            continue
        if ";" in cw[m.end():yc[0]]:
            no("semicolon-before-y")
            continue
        quote = cw[xc[0]:yc[1]]
        if len(quote) > 400:
            no("quote-too-long")
            continue
        if xc[0] + it["s0"] < it["d0"] or yc[1] + it["s0"] > it["d1"]:
            no("outside-window")
            continue
        cnt["pattern-matched"] += 1
        lines.append(json.dumps({"id": it["id"], "states": True, "kind": KIND[m.group(1).lower()],
                                 "scope": "otherGrounds", "field_limit": "", "doctrine": "", "quote": quote,
                                 "confidence": 0.9}, ensure_ascii=False))
    pdir = os.path.join(R.HERE, "pattern")
    R.write_text(os.path.join(pdir, "ans", "ans_pattern.jsonl"), "".join(x + "\n" for x in lines))
    R.write_rows(os.path.join(pdir, "pattern_rejects.tsv"), rejects)
    st["pattern_matched"] = len(lines)
    st["pattern_rejects"] = dict(sorted(cnt.items()))
    R.write_text(os.path.join(pdir, "pattern_stats.json"), json.dumps(st, indent=1) + "\n")
    print(json.dumps(st, indent=1))
    return certify_recog.main(["--answers", os.path.join(pdir, "ans"), "--out", a.out, "--items", R.ITEMS,
                               "--reader", "pattern-r5", "--src", "pattern:otherGrounds", "--cite-only"])


if __name__ == "__main__":
    sys.exit(main())
