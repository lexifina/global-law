"""Corpus counts for the proposed doctrine_reject / doctrine_tie additions (court-part sentences only).

    python -X utf8 cue_counts.py   -> work/cue_counts.json
reject: over every scanned rejection sentence that holds a doctrine label (scan/*.jsonl.gz, t = rej), and over the
items' main quotes; tie: over every strict tie sentence (ties.jsonl.gz) and the items' tie quotes. For each proposed
phrase not in the cue table: sentences holding it, and sentences holding it and no phrase of the current list.
"""
import glob, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dcommon as DC

rej_all, tie_all, dq_main, dq_j, rej_l, tie_l = DC.lists()
new_r = [p for p in DC.PROP_REJECT if p not in rej_l]
new_t = [p for p in DC.PROP_TIE if p not in tie_l]
out = {"reject_lean": rej_l, "tie_lean": tie_l}


def count(sents, new, cur):
    res = {}
    for p in new:
        a = b = 0
        for s in sents:
            if p in s:
                a += 1
                if not any(c in s for c in cur):
                    b += 1
        res[p] = [a, b]
    return res


rs = []
for p in glob.glob(os.path.join(HERE, "scan", "*.jsonl.gz")):
    for l in gzip.open(p, "rt", encoding="utf-8"):
        if '"t":"rej"' in l[:12]:
            rs.append(DC.nq(json.loads(l)["q"]))
ts = []
for l in gzip.open(os.path.join(HERE, "ties.jsonl.gz"), "rt", encoding="utf-8"):
    r = json.loads(l)
    if r["strict"] and r["x"] is not None:
        ts.append(DC.nq(r["q"]))
its = [json.loads(l) for l in open(os.path.join(HERE, "items.jsonl"), encoding="utf-8")]
im = [DC.nq(it["main_q"]) for it in its if "joined_q" in it]
it_ = [DC.nq(it["joined_q"]) for it in its if "joined_q" in it]
out["n_rej_sentences"] = len(rs)
out["n_tie_sentences"] = len(ts)
out["n_items_with_tie"] = len(im)
out["reject_corpus"] = count(rs, new_r, rej_l)
out["reject_items"] = count(im, new_r, rej_l)
out["tie_corpus"] = count(ts, new_t, tie_l)
out["tie_items"] = count(it_, new_t, tie_l)
out["reject_corpus_current_any"] = sum(1 for s in rs if any(c in s for c in rej_l))
out["tie_corpus_current_any"] = sum(1 for s in ts if any(c in s for c in tie_l))
json.dump(out, open(os.path.join(HERE, "work", "cue_counts.json"), "w", encoding="utf-8"), indent=1)
for k in ("reject_corpus", "reject_items", "tie_corpus", "tie_items"):
    print(k, json.dumps(out[k]))
print({k: out[k] for k in ("n_rej_sentences", "n_tie_sentences", "n_items_with_tie", "reject_corpus_current_any",
                            "tie_corpus_current_any")})
