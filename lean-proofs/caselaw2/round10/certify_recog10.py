"""Round 5, agent `recog`: reader answers -> staged delta files for recognised-overruling rows (DESIGN5 section 2).

    python -X utf8 certify_recog.py [--answers ans] [--out cert] [--items FILE] [--tiers T0,T1,T1s,T2]
                                    [--skip-explicit] [--all-witnesses] [--allow-quoted]
                                    [--reader ID] [--src SRC] [--cite-only]

Reads <answers>/ans_*.jsonl (READER_BRIEF_RECOG.md) and the items (items.jsonl.gz from build_candidates.py and
items_t1s.jsonl.gz from scan_scotus.py; --items names one file instead). For every answer with
`states: true` it builds a witness row in the round-4 layout (round3/implicit_schema.md, unchanged):

  id tw:<Y>:<X>:<start>:<W>, by_node = Y, target = X, date = date(Y), kind, scope, temporal unknown, explicit 0,
  text_sha / start / end / quote of W's text (offsets into the decision file text at git HEAD, UTF-8 decoded, CR LF
  -> LF; the quote with tabs and newlines as spaces), target evidence, part, reader claude-subagent:recog, confidence

and refuses the answer (rejects.tsv, with the reason) unless every text check of the recognised mode holds here:
  the quote is found in the item's window (exactly; whitespace runs and quote-mark styles tolerated; the window's
  own text is what is certified), is at most 400 characters, holds a recognition cue (cue table list `recognised`,
  at a word start) and no phrase of `disqualify_recognised`, lies in one opinion-of-the-court part, is not inside a
  quotation, and BOTH X and Y resolve inside the quote: a `cite:` whose compact form is in the compact quote and
  which resolves through data/cite_index.tsv (or, when the key is absent there, uniquely through
  graph/cite_index.tsv: then a cite_index delta row is written) to the right node; else `name:` words of the caption
  that stand in the quote as capitalised whole words and are not words of the other caption. The two evidences must
  differ. Dates: date(X) <= date(Y) <= date(W), none 0. W's power over X comes from the item (reference
  can_change(W, X) = yes at candidate time; verify_recog.py recomputes it).

Scope: the reader's, made narrower (never wider) by the quote's own words: "other grounds" -> otherGrounds; "in
part", "to the extent", "insofar" ... or a field limit or a doctrine label -> partialUnknown.

Per (Y, X) the EARLIEST admitted W is staged, and also the earliest admitted W whose scope is `all` when the
earliest is not (it fixes the date of the negative status). Other admitted rows go to rows_spare.tsv
(--all-witnesses stages them all). --skip-explicit leaves out pairs that already have an explicit scope-all row by
Y on X that is `ok` (they go to rows_explicit_pairs.tsv).

Writes to <out>/: treatments_delta.tsv (16 columns), treatment_witness_delta.tsv (4), treatment_class_delta.tsv
(5: id, recognised, field_limit|-, doctrine|-, src), cert_text_delta.tsv, window_sha_delta.tsv,
cite_index_delta.tsv, remove_ids.txt (live ids that a staged row with the SAME id replaces; remove them from
data/treatments.tsv and data/treatment_witness.tsv before appending), t0_map.tsv (round-4 witness row -> the row
the re-reading gives), live_same_triple.tsv (a live witness row with the same Y, X, W as a staged row but another
quote: the old row may be removed, it is not replaced automatically), rows_info.tsv, rows_spare.tsv,
rows_explicit_pairs.tsv, rejects.tsv, stats.json.
A staged row whose id is live gets a class line only when the live row is identical (`live-identical`) or already
passes the recognised text checks with the same kind, scope and part (`live-kept`); otherwise the staged row
replaces it (`replaces-live`, remove_ids.txt). treatments_items_delta.tsv (id, item, how the quote was found,
provenance) is the companion of data/treatments_items.tsv.

List context: when the paragraph (footnote) that holds the quote says, before the quote, that the cases were
overruled "in whole or in part" (item fields `intro`, `para`), a scope `all` becomes partialUnknown.

--reader / --src set the reader column and the src of the witness and class lines (certify_pattern.py uses
`pattern-r5` / `pattern:otherGrounds`); --cite-only refuses name evidence.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

# round 10 (agent `infra10`): copy of round9/certify_recog9.py with the base changed to round9/stage/v9c (nothing else).
# round 9 (agent `infra9`): copy of round8/certify_recog8.py with the base changed to round8/stage/v8e (nothing else).
# round 8 (agent `infra`): copy of round7/agents/queue/certify_recog.py (= round5/recog/certify_recog.py, paths
# only); only paths changed again. recog_common is round 5's (imported from round5/recog); the live tables are the
# round-10 base build round9/stage/v9c; answers, output, items and the pack index are named on the command line.
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(C2, "round5", "recog"))
import recog_common as R  # noqa: E402
R.DATA = os.path.join(C2, "round9", "stage", "v9c")

RC = R.RC
SCOPES = ("all", "partialUnknown", "otherGrounds")
KIND_IN = {"overruled": "overruled", "abrogated": "abrogated", "disapproved": "disapproved",
           "recededfrom": "recededFrom", "receded": "recededFrom", "receded from": "recededFrom"}
STEM_KIND = {v: k for k, v in R.KIND_STEM.items()}


def one_line(s, n=120):
    s = " ".join(str(s or "").split())
    return s[:n] if s else "-"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--answers", required=True, help="folder with ans_*.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--items", required=True, help="items .jsonl.gz")
    ap.add_argument("--index", required=True, help="pack index: item id, pack file name (pack_<x>.md), ...")
    ap.add_argument("--tiers", default="")
    ap.add_argument("--reader", default=R.READER_ID, help="reader column of the treatments rows")
    ap.add_argument("--src", default=None, help="src of the witness and class lines (default: the reader)")
    ap.add_argument("--cite-only", action="store_true", help="X and Y must be named by citation (no name: evidence)")
    ap.add_argument("--skip-explicit", action="store_true")
    ap.add_argument("--all-witnesses", action="store_true")
    ap.add_argument("--allow-quoted", action="store_true")
    a = ap.parse_args(argv)
    a.src = a.src or a.reader
    os.makedirs(a.out, exist_ok=True)
    st = collections.OrderedDict()
    cnt = collections.Counter()

    # ---- answers
    ans, bad, dup = {}, 0, 0
    files = sorted(glob.glob(os.path.join(a.answers, "ans_*.jsonl")))
    for f in files:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                i = str(r["id"]).strip()
            except Exception:
                bad += 1
                continue
            if i in ans:
                dup += 1
            ans[i] = r
    st["answer_files"] = len(files)
    st["answers"] = len(ans)
    st["answer_lines_unparsed"] = bad
    st["answer_ids_repeated"] = dup
    items = R.load_items(a.items, set(ans))
    tiers = {t for t in a.tiers.split(",") if t}
    rejects = []

    def rej(i, stage, why):
        rejects.append([i, stage, why])
        cnt[stage + ":" + why.split(":")[0]] += 1

    # items of an answered pack that have no answer line (packs/index.tsv: item id, pack, ...)
    answered = {os.path.basename(f)[4:-6] + ".md" for f in files}
    for p in R.read_rows(a.index, 2):
        if p[1] in answered and p[0] not in ans:
            rej(p[0], "reader", "no-answer")

    # ---- phase 1: the quote
    rows = []
    for i, r in ans.items():
        it = items.get(i)
        if it is None:
            rej(i, "input", "answer-without-item")
            continue
        if tiers and it["tier"] not in tiers:
            continue
        cnt["answers_read:" + it["tier"]] += 1
        if r.get("states") not in (True, 1, "true", "True", "yes"):
            rej(i, "reader", "not-stated:" + one_line(r.get("reason"), 30))
            continue
        cnt["states_true:" + it["tier"]] += 1
        s0 = it["s0"]
        raw = it["text"]
        cw = R.clean(raw[it["d0"] - s0:it["d1"] - s0])
        prefer = it["off"] - it["d0"]
        pos = R.find_quote(cw, r.get("quote"), prefer)
        how = "quote"
        if pos is None:
            pos = R.find_quote(cw, r.get("quote"), prefer, hyphen=True)
            how = "quote-hyphen"
        if pos is None:
            rej(i, "cert", "quote-not-in-window")
            continue
        q0, q1 = pos
        while q0 < q1 and cw[q0] == " ":
            q0 += 1
        while q1 > q0 and cw[q1 - 1] == " ":
            q1 -= 1
        quote = cw[q0:q1]
        start, end = it["d0"] + q0, it["d0"] + q1
        if not quote:
            rej(i, "cert", "quote-empty")
            continue
        if len(quote) > 400:
            rej(i, "cert", "quote-too-long:%d" % len(quote))
            continue
        if not (R.cue_ok(quote) and R.CUE_WORD.search(quote)):
            if R.CUE_WORD.search(RC.dehyphen_norm(quote)):
                rej(i, "cert", "cue-hyphen-split")
            else:
                rej(i, "cert", "no-cue")
            continue
        dq = R.disqualifiers_in(quote)
        if dq:
            rej(i, "cert", "disqualified:" + dq[0])
            continue
        part = None
        for (pa, pb, pp) in it.get("parts", []):
            if pa <= start < pb:
                part = pp if end <= pb else "crosses-parts"
                break
        if part not in R.CERT_PARTS:
            rej(i, "cert", "part:%s" % part)
            continue
        if not a.allow_quoted and R.quoted(cw, q0, q1):
            rej(i, "cert", "inside-quotation")
            continue
        wd, xd, yd = it["W"]["date"], it["X"]["date"], it["Y"]["date"]
        if not (wd and xd and yd and xd <= yd <= wd):
            rej(i, "cert", "dates")
            continue
        if it.get("w_power") != "yes":
            rej(i, "cert", "w-no-power:" + str(it.get("w_power_rule")))
            continue
        ql = R.ascii_lower(quote)
        kind = KIND_IN.get(str(r.get("kind") or "").strip().lower())
        if kind is None or R.KIND_STEM[kind] not in ql:
            m = R.CUE_WORD.search(quote)
            kind = STEM_KIND[m.group(1).lower()]
        scope_r = r.get("scope") if r.get("scope") in SCOPES else "partialUnknown"
        fl, doc = one_line(r.get("field_limit")), one_line(r.get("doctrine"))
        scope, scope_how = scope_r, "reader"
        if R.OTHER_RX.search(quote):
            if scope != "otherGrounds":
                scope, scope_how = "otherGrounds", "quote-words"
        elif scope == "all" and (R.PART_RX.search(quote) or fl != "-" or doc != "-"):
            scope, scope_how = "partialUnknown", ("quote-words" if R.PART_RX.search(quote) else "field-or-doctrine")
        elif scope == "all":
            # list context: the paragraph (footnote) up to the quote says "in whole or in part"
            p0 = max(it.get("para", start), s0)
            lead = (it.get("intro") or "") + " " + R.clean(raw[p0 - s0:start - s0])
            if R.WHOLE_PART_RX.search(lead):
                scope, scope_how = "partialUnknown", "intro-whole-or-part"
        try:
            conf = max(0.0, min(1.0, float(r.get("confidence", 0.5))))
        except (TypeError, ValueError):
            conf = 0.5
        w0, w1 = max(0, start - 400), min(it["len"], end + 400)
        if w0 < s0 or w1 > s0 + len(raw):
            rej(i, "cert", "window-outside-stored-text")
            continue
        window = R.clean(raw[w0 - s0:w1 - s0])
        assert window[start - w0:end - w0] == quote and len(window) == w1 - w0
        rows.append({"item": i, "it": it, "start": start, "end": end, "quote": quote, "kind": kind, "scope": scope,
                     "scope_reader": scope_r, "scope_how": scope_how, "fl": fl, "doc": doc, "conf": conf,
                     "part": part, "how": how, "win": (it["sha"], w0, w1, window)})

    # ---- phase 2: X and Y inside the quote
    live = R.live_cite_index()
    keys = set()
    for t in rows:
        for k, c in R.cite_keys_in(t["quote"]):
            if c not in live:
                keys.add(k)
    graph = R.graph_cite_rows(keys)
    idx_delta = {}

    def evidence(node, name, other, quote):
        return R.evidence_for(node, name, other, quote, live, graph, a.cite_only)

    good = []
    for t in rows:
        it = t["it"]
        ex, dx = evidence(it["x"], it["X"]["name"], it["Y"]["name"], t["quote"])
        ey, dy = evidence(it["y"], it["Y"]["name"], it["X"]["name"], t["quote"])
        if ex is None:
            rej(t["item"], "cert", "x-not-in-quote")
            continue
        if ey is None:
            rej(t["item"], "cert", "y-not-in-quote")
            continue
        if R.alnum(ex.split(":", 1)[1]) == R.alnum(ey.split(":", 1)[1]):
            rej(t["item"], "cert", "same-evidence")
            continue
        index = dict(live)
        for d in (dx, dy):
            if d:
                index[R.alnum(d[0])] = d[1]
        if not (R.resolve_in_quote(ex, t["quote"], it["x"], index) and
                R.resolve_in_quote(ey, t["quote"], it["y"], index)):
            rej(t["item"], "cert", "evidence-does-not-resolve")
            continue
        t["ex"], t["ey"], t["idx"] = ex, ey, [d for d in (dx, dy) if d]
        t["id"] = "tw:%d:%d:%d:%d" % (it["y"], it["x"], t["start"], it["w"])
        good.append(t)
    st["admitted_statements"] = len(good)

    # ---- phase 3: which rows to stage
    byid = {}
    for t in sorted(good, key=lambda t: (t["id"], -t["conf"], t["item"])):
        byid.setdefault(t["id"], t)
    pairs = collections.defaultdict(list)
    for t in byid.values():
        pairs[(t["it"]["y"], t["it"]["x"])].append(t)
    stage, spare, expl = [], [], []
    for key, ts in pairs.items():
        ts.sort(key=lambda t: (t["it"]["W"]["date"], t["it"]["w"], t["start"]))
        if a.all_witnesses:
            pick = list(ts)
        else:
            pick = [ts[0]]
            if ts[0]["scope"] != "all":
                nxt = next((t for t in ts if t["scope"] == "all"), None)
                if nxt is not None:
                    pick.append(nxt)
        for t in ts:
            if t not in pick:
                spare.append(t)
            elif a.skip_explicit and t["it"].get("pair_explicit"):
                expl.append(t)
            else:
                stage.append(t)
    stage.sort(key=lambda t: (t["it"]["w"], t["it"]["x"], t["start"]))

    # ---- phase 4: against the live tables
    live_t = {p[0]: p for p in R.read_rows(os.path.join(R.DATA, "treatments.tsv"), 16)}
    live_w = {p[0]: p for p in R.read_rows(os.path.join(R.DATA, "treatment_witness.tsv"), 4)}
    shas = {t["win"][0] for t in stage}
    live_win = set()
    with open(os.path.join(R.DATA, "window_sha.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] in shas and len(p) >= 4:
                live_win.add((p[0], int(p[1]), int(p[2]), p[3]))

    def row16(t):
        it = t["it"]
        return [t["id"], it["y"], it["x"], it["Y"]["date"], t["kind"], t["scope"], "unknown", 0, it["sha"],
                t["start"], t["end"], t["quote"], t["ex"], t["part"], a.reader, "%.2f" % t["conf"]]

    def wrow(t):
        return [t["id"], t["it"]["w"], t["ey"], a.src]

    tr, tw, tc, ct, ws, remove, t0map, info, same3, ti = [], [], [], [], [], [], [], [], [], []
    seen_win, idx_rows = set(), {}
    live_triple = collections.defaultdict(list)
    for tid, p in live_w.items():
        lt = live_t.get(tid)
        if lt is not None:
            live_triple[(lt[1], lt[2], p[1])].append(tid)
    for t in stage:
        it = t["it"]
        for old in live_triple.get((str(it["y"]), str(it["x"]), str(it["w"])), []):
            if old != t["id"]:
                same3.append([old, t["id"], t["item"]])
        r16 = [str(x) for x in row16(t)]
        lt = live_t.get(t["id"])
        state = "new"
        if lt is not None:
            lw = live_w.get(t["id"], [None] * 3)
            same = lt[:14] == r16[:14] and lw[1:3] == [str(it["w"]), t["ey"]]
            state = "live-identical" if same else "replaces-live"
            if not same and lw[1] == str(it["w"]) and lt[4] == t["kind"] and lt[5] == t["scope"] and \
                    lt[13] == t["part"] and len(lt[11]) <= 400 and R.cue_ok(lt[11]) and \
                    not R.disqualifiers_in(lt[11]) and R.alnum(lt[12].split(":", 1)[-1]) != \
                    R.alnum(lw[2].split(":", 1)[-1]) and R.resolve_in_quote(lt[12], lt[11], it["x"], live) and \
                    R.resolve_in_quote(lw[2], lt[11], it["y"], live):
                # the live row (same start, another end or evidence) already passes the recognised text checks
                # with the same kind and scope: keep it, claim it
                state = "live-kept"
            if state == "replaces-live":
                remove.append(t["id"])
        if state in ("new", "replaces-live"):
            tr.append(r16)
            tw.append(wrow(t))
            sha, w0, w1, window = t["win"]
            h = R.sha1_text(window)
            if (sha, w0, w1) not in seen_win and (sha, w0, w1, h) not in live_win:
                seen_win.add((sha, w0, w1))
                ct.append([sha, w0, w1, window])
                ws.append([sha, w0, w1, h, "corpus"])
            for k, node in t["idx"]:
                idx_rows[(k, node)] = 1
            ti.append([t["id"], t["item"], t["how"], "recog:%s;by=%d;witness=%d;byEvidence=%s" % (
                it["tier"], it["y"], it["w"], t["ey"])])
        tc.append([t["id"], "recognised", t["fl"], t["doc"], a.src])
        cnt["staged:" + state] += 1
        cnt["staged_tier:" + it["tier"]] += 1
        cnt["staged_kind_scope:%s|%s" % (t["kind"], t["scope"])] += 1
        if it.get("old_id"):
            t0map.append([it["old_id"], t["item"], t["id"],
                          "same-id" if it["old_id"] == t["id"] else "requoted", state, it.get("old_cert", "")])
        info.append([t["id"], t["item"], it["tier"], it["w"], it["x"], it["y"], it["W"]["date"], it["Y"]["date"],
                     it["X"]["date"], t["kind"], t["scope"], t["scope_reader"], t["scope_how"], t["how"],
                     it.get("pair_explicit", 0), "%.2f" % t["conf"], t["fl"], t["doc"], state, t["ey"]])
    staged_old = {m[0] for m in t0map}
    for i, r in ans.items():
        it = items.get(i)
        if it is not None and it.get("old_id") and it["old_id"] not in staged_old and (not tiers or "T0" in tiers):
            t0map.append([it["old_id"], i, "-", "not-recognised", "-", it.get("old_cert", "")])
    t0map.sort()

    def W(name, rs):
        R.write_rows(os.path.join(a.out, name), rs)

    W("treatments_delta.tsv", tr)
    W("treatment_witness_delta.tsv", tw)
    W("treatments_items_delta.tsv", ti)
    W("treatment_class_delta.tsv", tc)
    W("cert_text_delta.tsv", ct)
    W("window_sha_delta.tsv", ws)
    W("cite_index_delta.tsv", sorted([k, n] for (k, n) in idx_rows))
    R.write_text(os.path.join(a.out, "remove_ids.txt"), "".join(i + "\n" for i in remove))
    W("t0_map.tsv", t0map)
    W("live_same_triple.tsv", same3)
    W("rows_info.tsv", [["id", "item", "tier", "w", "x", "y", "w_date", "y_date", "x_date", "kind", "scope",
                         "scope_reader", "scope_how", "quote_how", "pair_explicit_ok", "confidence", "field_limit",
                         "doctrine", "state", "by_evidence"]] + info)
    W("rows_spare.tsv", [[str(x) for x in row16(t)] + [t["it"]["w"], t["ey"], t["fl"], t["doc"]] for t in spare])
    W("rows_explicit_pairs.tsv", [[str(x) for x in row16(t)] + [t["it"]["w"], t["ey"], t["fl"], t["doc"]]
                                  for t in expl])
    W("rejects.tsv", rejects)
    st["staged_class_lines"] = len(tc)
    st["treatments_delta"] = len(tr)
    st["witness_delta"] = len(tw)
    st["cert_text_delta"] = len(ct)
    st["cite_index_delta"] = len(idx_rows)
    st["remove_ids"] = len(remove)
    st["pairs_Y_X_staged"] = len({(t["it"]["y"], t["it"]["x"]) for t in stage})
    st["spare_rows"] = len(spare)
    st["explicit_pair_rows_left_out"] = len(expl)
    st["counts"] = dict(sorted(cnt.items()))
    R.write_text(os.path.join(a.out, "stats.json"), json.dumps(st, indent=1) + "\n")
    print(json.dumps(st, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
