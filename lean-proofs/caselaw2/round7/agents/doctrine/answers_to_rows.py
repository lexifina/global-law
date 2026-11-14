"""Round 7, agent doctrine: reader answers -> DESIGN7 section 4 rows (input of round7/certify7.py).

    python -X utf8 answers_to_rows.py [--ans ans] [--items items.jsonl] [--out rows.jsonl]
    python -X utf8 answers_to_rows.py --dry --out work/rows_dry.jsonl      (every rule-ok item as if read yes)

A row is written for an item whose answer has reject = true and tie = true. The reader's main_quote and tie_quote
are located in W's git-HEAD text near the item's sentences (exact, else tolerant of whitespace and quote styles; the
text's own characters are used). The label D (the item's label) must stand, normalised and lower-cased, in both
located quotes; the evidence for X is taken inside the located tie quote alone (a citation the index maps to X, else
X's caption words). Kind disapproved, scope all (a doctrine row is always demoted: DESIGN7 2.4), claim doctrine,
joined line rel doctrineTie with label D. field_limit = the reader's field limit (display text) or "-".
Writes the rows and <out>_skipped.tsv (item, why). No answer key is read.
"""
import argparse, collections, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round6/history"))
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog"))
import r6lib as L  # noqa: E402
import dcommon as DC  # noqa: E402
import recog_common as RCm  # noqa: E402
NL = "\n"


def iid(it):
    return "%d:%d:%d" % (it["w"], it["main"][0], it["x"])


def locate(text, quote, near0, near1, pad=1500):
    """(start, end) of the quote in text, searched in [near0 - pad, near1 + pad)."""
    a0, a1 = max(0, near0 - pad), min(len(text), near1 + pad)
    win = L.norm(text[a0:a1])
    hit = RCm.find_quote(win, quote, near0 - a0, hyphen=True)
    if not hit:
        return None
    return a0 + hit[0], a0 + hit[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ans", default=os.path.join(HERE, "ans"))
    ap.add_argument("--items", default=os.path.join(HERE, "items.jsonl"),
                    help="the current items (for --dry, and the live candidate check)")
    ap.add_argument("--items-map", default="1-8=work/items_read1.jsonl,9-99=work/items_new2.jsonl",
                    help="pack number ranges -> the items file each pack was built from")
    ap.add_argument("--out", default=os.path.join(HERE, "rows.jsonl"))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    def load(path):
        out = {}
        for l in open(path if os.path.isabs(path) else os.path.join(HERE, path), encoding="utf-8"):
            it = json.loads(l)
            if "joined_q" in it:
                out[iid(it)] = it
        return out
    current = load(a.items)
    # the live candidate set: a read item whose (W, X, label key) is no longer a candidate is not written
    live_keys = {(it["w"], it["x"], it["lk"]) for it in current.values()}
    ranges = []
    for part in a.items_map.split(","):
        rg, path = part.split("=")
        lo, hi = rg.split("-")
        ranges.append((int(lo), int(hi or 999), load(path)))
    answers, items = {}, {}
    if a.dry:
        items = current
        for k, it in items.items():
            if it["rule_ok"]:
                answers[k] = {"id": k, "reject": True, "tie": True, "main_quote": it["main_q"],
                              "tie_quote": it["joined_q"],
                              "field_limit": "" if it["field_limit"] == "-" else it["field_limit"],
                              "confidence": 1.0, "reader": "dry-run"}
    else:
        for p in sorted(glob.glob(os.path.join(a.ans, "*.jsonl"))):
            num = int(os.path.basename(p)[5:8])
            src = next((m for lo, hi, m in ranges if lo <= num <= hi), {})
            for l in open(p, encoding="utf-8"):
                l = l.strip()
                if not l:
                    continue
                try:
                    o = json.loads(l)
                except ValueError:
                    continue
                o["reader"] = "claude-subagent:doctrine:" + os.path.basename(p)
                k = o.get("id")
                if k in src:
                    items[k + "@" + os.path.basename(p)] = src[k]
                    answers[k + "@" + os.path.basename(p)] = o
                else:
                    answers["?" + str(k)] = o
    st = collections.Counter()
    yes = {k: o for k, o in answers.items() if o.get("reject") is True and o.get("tie") is True and k in items}
    gone = [k for k in yes if (items[k]["w"], items[k]["x"], items[k]["lk"]) not in live_keys]
    for k in gone:
        yes.pop(k)
    st["answers_yes_no_longer_candidate"] = len(gone)
    st["answers"] = len(answers)
    st["answers_unknown_id"] = sum(1 for k in answers if k not in items)
    st["answers_yes"] = len(yes)
    texts = L.fetch_texts({items[k]["w"] for k in yes})
    live = RCm.live_cite_index()
    rows, skipped = [], []
    # one row per item; items of the stratum-A packs (rule ok) first, so that certify7's "first passing (by, target,
    # kind) stands" prefers them
    for k, o in sorted(yes.items(), key=lambda kv: (not items[kv[0]]["rule_ok"], kv[0])):
        it = items[k]
        w, x = it["w"], it["x"]
        if w not in texts:
            skipped.append((k, "no-text"))
            continue
        sha, text = texts[w]
        if sha != it["sha"]:
            skipped.append((k, "text-changed"))
            continue
        ms = it.get("main_sentence", it["main"])
        m = locate(text, o.get("main_quote") or "", ms[0], ms[1])
        t = locate(text, o.get("tie_quote") or "", it["joined"][0], it["joined"][1])
        if not m or not t:
            skipped.append((k, "quote-not-found:" + ("main" if not m else "tie")))
            continue
        d = it["label"]
        mq, tq = L.norm(text[m[0]:m[1]]), L.norm(text[t[0]:t[1]])
        if d not in DC.nq(mq) or d not in DC.nq(tq):
            skipped.append((k, "label-not-in-quotes"))
            continue
        graph = RCm.graph_cite_rows({kk for kk, _ in RCm.cite_keys_in(tq)})
        ev, _delta = RCm.evidence_for(x, it["x_name"], it["w_name"], tq, live, graph)
        if not ev:
            skipped.append((k, "evidence-not-in-tie-quote"))
            continue
        fl = (o.get("field_limit") or "").strip() or "-"
        rows.append({"rule": "doctrine:%s:%s" % (it["form"], "A" if it["rule_ok"] else "B"), "table": "treatments", "by": w, "target": x,
                     "kind": "disapproved", "scope": "all", "main": [m[0], m[1]], "part": it["part"], "ev": ev,
                     "joined": [{"rel": "doctrineTie", "span": [t[0], t[1]], "part": it["joined_part"], "label": d}],
                     "claim": "doctrine", "doctrine": d, "field_limit": fl, "anchor": None, "anchor_part": "",
                     "reader": o.get("reader", ""), "confidence": o.get("confidence", 1.0),
                     "note": "item %s; stratum %s; registry key %s; %s" % (k, "A" if it["rule_ok"] else "B", it["lk"],
                                                                           (o.get("why") or "")[:160])})
    with open(a.out, "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.splitext(a.out)[0] + "_skipped.tsv", "w", encoding="utf-8", newline=NL) as f:
        for k, why in skipped:
            f.write("%s\t%s\n" % (k, why))
    st["rows"] = len(rows)
    st.update(collections.Counter("skip:" + why.split(":")[0] for _, why in skipped))
    for kk, v in sorted(st.items()):
        print(kk, v)


if __name__ == "__main__":
    main()
