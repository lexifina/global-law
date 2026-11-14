"""Round 5, agent `recog`: tier T1s, recognition statements found by our own scan of every opinion of the Supreme
Court of the United States (W, X and Y all Supreme Court decisions). Corpus text only: no notes table, no gold list.

    python -X utf8 scan_scotus.py

For each Supreme Court decision W (text from git HEAD, hashed against decisions2.tsv), each overruling word in an
opinion-of-the-court part (reader/common.part_map2) is a cue: overrul-, abrogat-, disapprov-, reced- ... from (the
stems of the cue list `recognised`; "did not survive" has no such cue and cannot be certified, so it is not
scanned). Around the cue, the Supreme Court decisions MENTIONED are collected: by citation (graph/cite_index.tsv,
a key with one node), or by a distinctive caption word of a decision that W cites somewhere by citation (a word
that names exactly one of them; "Justice Brown", "Brown, J." are not mentions). Among the three mentioned decisions
nearest the cue, every pair gives a candidate: X = the older, Y = the newer, when
date(X) < date(Y) <= date(W), neither is W, and one span of at most 400 characters holds the cue and a mention of
each (the quote the reader must give). Every form is covered ("Y (overruling X)", "X was overruled in Y", "we
overruled X in Y", "X, overruled by Y", "X has been overruled. See Y", "Y abrogated X"); `form` records the order of
the three and whether the wording is one of the tight forms (strict = 1).
Power: the reference's can_change(W, X) must be yes (as for every tier).
Reduce: one candidate per (W, X, Y) (a strict position first, else the first); per (Y, X) the 3 earliest W (and
the earliest W with a strict-form statement when it is not among them); (W, X, Y) triples already in tier T1
(candidates.tsv) are left out.

Writes items_t1s.jsonl.gz, candidates_t1s.tsv, stats_t1s.json.
"""
import bisect
import collections
import gzip
import json
import os
import re
import sys

import recog_common as R

RC = R.RC
CUE = re.compile(r"\b(overrul(?:ed|ing|es|e)|abrogat(?:ed|ing|es|e)|disapprov(?:ed|ing|es|e|al)|"
                 r"reced(?:ed|ing|es|e)\s+from)\b", re.I)
QUAL = (r"(?:\s*,?\s*(?:in\s+part|on\s+other\s+grounds|sub\s+silentio|implicitly|expressly|in\s+effect|effectively|"
        r"in\s+terms|in\s+principle|pro\s+tanto))*")
BY_IN = re.compile(r"^" + QUAL + r"\s*,?\s*(?:by|in)\b", re.I)
JUDGE_BEFORE = re.compile(r"(?:JUSTICE|Justice|Judge|JUDGE|Mr\.|MR\.|Chief|CHIEF)\s+$")
JUDGE_AFTER = re.compile(r"^\s*,\s*(?:C\.\s?J\.|J\.|JJ\.)")
SPAN = 400
PAD = 700
STORE = 450
KEEP_W = 3


def main():
    st = collections.OrderedDict()
    C = R.tests_common()
    E, pr, meta = C.lite_engine(R.DATA)
    D = E.D

    def is_scotus(node):
        e = E.epoch(int(D.court[node]), int(D.date[node]))
        return e is not None and E.is_scotus(e)

    # ---- Supreme Court decisions
    S = {}
    with open(os.path.join(R.GRAPH, "nodes.tsv"), "rb") as f:
        for raw in f:
            p = raw.split(b"\t", 3)
            if p[1] == b"supreme-court":
                q = raw.rstrip(b"\r\n").decode("utf-8", "replace").split("\t")
                n = int(q[0])
                if D.has(n) and is_scotus(n):
                    S[n] = (q[2], q[5] if len(q) > 5 else "", q[6] if len(q) > 6 else "")
    st["scotus_decisions"] = len(S)
    R.log("Supreme Court decisions:", len(S))
    keys = collections.defaultdict(set)
    path_ci = os.path.join(R.GRAPH, "cite_index.tsv")
    with open(path_ci, "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            n = int(raw[i + 1:].strip())
            if n in S:
                keys[raw[:i]].add(n)
    with open(path_ci, "rb") as f:
        for raw in f:
            i = raw.find(b"\t")
            if raw[:i] in keys:
                keys[raw[:i]].add(int(raw[i + 1:].strip()))
    idx = {k.decode("utf-8"): next(iter(v)) for k, v in keys.items() if len(v) == 1}
    st["citation_keys"] = len(idx)
    dinfo = R.decisions_info(set(S))
    R.log("citation keys:", len(idx))
    explicit_ok, live_t, wit, certs = R.explicit_ok_pairs()
    wit_pairs = set()
    for p in wit:
        t = live_t.get(p[0])
        if t is not None:
            wit_pairs.add((int(t[1]), int(t[2])))
    t1 = set()
    for p in R.read_rows(os.path.join(R.HERE, "candidates.tsv"), 5)[1:]:
        if p[1] == "T1":
            t1.add((int(p[2]), int(p[3]), int(p[4])))

    toks_of = {}

    def toks(n):
        if n not in toks_of:
            nm = S[n][2]
            toks_of[n] = RC.name_tokens(nm) | RC.short_name_tokens(nm)
        return toks_of[n]

    cnt = collections.Counter()
    cands = {}
    paths = sorted((v[0], n) for n, v in S.items())
    tree = R.tree_shas("supreme-court")
    STEP = 3000
    for k in range(0, len(paths), STEP):
        chunk = [(p, n) for p, n in paths[k:k + STEP] if p in tree]
        cnt["text-missing"] += len(paths[k:k + STEP]) - len(chunk)
        blobs = R.git_blobs("supreme-court", [tree[p] for p, _ in chunk])
        for (path, W), raw in zip(chunk, blobs):
            if raw is None:
                cnt["text-missing"] += 1
                continue
            low = raw.lower()
            if b"overrul" not in low and b"abrogat" not in low and b"disapprov" not in low and b"reced" not in low:
                cnt["texts"] += 1
                continue
            if W not in dinfo or R.sha1_bytes(raw) != dinfo[W][2]:
                cnt["text-sha-differs"] += 1
                continue
            text = R.decode(raw)
            cnt["texts"] += 1
            cues = list(CUE.finditer(text))
            if not cues:
                continue
            wd = int(D.date[W])
            if not wd:
                continue
            ment = []
            for m in RC.CITE_RX.finditer(text):
                n = idx.get(RC.cite_key(m) or "")
                if n is not None and n != W and 0 < int(D.date[n]) <= wd:
                    ment.append((m.start(), m.end(), n, "c"))
            cited = {m[2] for m in ment}
            if len(cited) < 2:
                continue
            tm = collections.defaultdict(set)
            for n in cited:
                for t in toks(n):
                    tm[t].add(n)
            tok = {t: next(iter(v)) for t, v in tm.items() if len(v) == 1}
            if tok:
                rx = re.compile(r"\b(" + "|".join(re.escape(t) for t in sorted(tok, key=len, reverse=True)) + r")\b")
                for m in rx.finditer(text):
                    if JUDGE_BEFORE.search(text[max(0, m.start() - 12):m.start()]) or \
                            JUDGE_AFTER.match(text[m.end():m.end() + 10]):
                        continue
                    ment.append((m.start(), m.end(), tok[m.group(1)], "n"))
            ment.sort()
            starts = [m[0] for m in ment]
            pm, body0 = RC.part_map2(text)
            hw = None
            for cm in cues:
                c0, c1 = cm.start(), cm.end()
                part_raw, sec = RC.part_at(pm, c0)
                part = R.PART_OUT.get(part_raw, part_raw.rstrip("~") or "unknown")
                if part not in R.CERT_PARTS:
                    cnt["cue-part:" + part] += 1
                    continue
                cnt["cues-in-court-part"] += 1
                lo = bisect.bisect_left(starts, c0 - SPAN)
                hi = bisect.bisect_right(starts, c1 + SPAN)
                best = {}
                for (a, b, n, how) in ment[lo:hi]:
                    d = c0 - b if b <= c0 else (a - c1 if a >= c1 else 0)
                    if n not in best or d < best[n][0]:
                        best[n] = (d, a, b, how)
                near = sorted(best.items(), key=lambda kv: (kv[1][0], kv[1][1]))[:3]
                if len(near) < 2:
                    continue
                cnt["cues-with-two-decisions"] += 1
                word = cm.group(1).lower()
                for i in range(len(near)):
                    for j in range(i + 1, len(near)):
                        (n1, m1), (n2, m2) = near[i], near[j]
                        d1, d2 = int(D.date[n1]), int(D.date[n2])
                        if d1 == d2:
                            continue
                        (X, mx), (Y, my) = ((n1, m1), (n2, m2)) if d1 < d2 else ((n2, m2), (n1, m1))
                        s0, s1 = min(mx[1], my[1], c0), max(mx[2], my[2], c1)
                        if s1 - s0 > SPAN:
                            continue
                        order = "".join(t for _, t in sorted([(mx[1], "X"), (my[1], "Y"), (c0, "c")]))
                        strict = 0
                        if order == "XcY" and word.endswith("ed") and BY_IN.match(text[c1:my[1]][:90]) \
                                and my[1] - c1 <= 150:
                            strict = 1
                        elif order == "YcX" and word.endswith("ing") and mx[1] - c1 <= 60:
                            strict = 1
                        elif order == "cXY" and not word.endswith("ing") and mx[1] - c1 <= 40 and \
                                my[1] - mx[2] <= 90 and re.search(r"\bin\b|\bby\b", text[mx[2]:my[1]]):
                            strict = 1
                        elif order == "YcX" and not word.endswith("ing") and c0 - my[2] <= 80 and mx[1] - c1 <= 40:
                            strict = 1
                        key = (W, X, Y)
                        old = cands.get(key)
                        if old is not None and (old["strict"], -old["off"]) >= (strict, -c0):
                            continue
                        if hw is None:
                            hw = RC.hard_wrapped(text, body0)
                        d0, d1_ = max(0, c0 - PAD), min(len(text), c1 + PAD)
                        t0, t1_ = max(0, d0 - STORE), min(len(text), d1_ + STORE)
                        span = R.clean(text[s0:s1])
                        cands[key] = {
                            "w": W, "x": X, "y": Y, "off": c0, "note_end": c1, "strict": strict, "form": order,
                            "word": word, "part": part, "part_raw": part_raw, "sec": sec, "d0": d0, "d1": d1_,
                            "s0": t0, "text": text[t0:t1_], "len": len(text), "sha": dinfo[W][2], "path": path,
                            "parts": [[max(pa, t0), min(pb, t1_), R.PART_OUT.get(pp, pp.rstrip("~") or "unknown")]
                                      for (pa, pb, pp, _s) in pm if pa < t1_ and pb > t0],
                            "intro": R.para_intro(text, c0, d0, hw)[0], "para": R.para_intro(text, c0, d0, hw)[1],
                            "scope": "otherGrounds" if R.OTHER_RX.search(span) else (
                                "partialUnknown" if R.PART_RX.search(span) else "all"),
                            "x_how": mx[3], "y_how": my[3]}
        R.log("scanned", min(k + STEP, len(paths)), "of", len(paths), "candidates", len(cands))
    st["texts_scanned"] = cnt["texts"]
    st["triples_W_X_Y"] = len(cands)

    # ---- power, reduce
    keep = []
    for (W, X, Y), c in cands.items():
        cc = E.can_change(W, X, "unknown")
        if cc[0] != "yes":
            cnt["w-no-power:" + cc[1]] += 1
            continue
        c["wrule"] = cc[1]
        keep.append(c)
    pairs = collections.defaultdict(list)
    for c in keep:
        pairs[(c["y"], c["x"])].append(c)
    st["pairs_Y_X"] = len(pairs)
    out = []
    for (y, x), cs in pairs.items():
        cs.sort(key=lambda c: (int(D.date[c["w"]]), c["w"]))
        # the 3 earliest W, and the earliest W with a strict-form statement when it is not one of them
        strict = [c for c in cs if c["strict"]]
        pick = cs[:KEEP_W]
        if strict and strict[0] not in pick:
            pick.append(strict[0])
        for r, c in enumerate(pick):
            if (c["w"], x, y) in t1:
                cnt["already-in-T1"] += 1
                continue
            c["rank"] = r + 1
            c["pair_strict"] = 1 if strict else 0
            c["pair_explicit"] = 1 if (y, x) in explicit_ok else 0
            c["pair_witness"] = 1 if (y, x) in wit_pairs else 0
            out.append(c)
    out.sort(key=lambda c: (c["y"], c["x"], c["rank"]))
    st["candidates"] = len(out)
    st["candidates_strict_form"] = sum(c["strict"] for c in out)
    st["candidates_loose_form"] = sum(1 - c["strict"] for c in out)
    st["pairs"] = len({(c["y"], c["x"]) for c in out})
    st["pairs_strict"] = len({(c["y"], c["x"]) for c in out if c["strict"]})
    st["candidates_pair_already_explicit"] = sum(c["pair_explicit"] for c in out)
    st["candidates_pair_has_round4_witness"] = sum(c["pair_witness"] for c in out)
    st["strict_not_explicit"] = sum(1 for c in out if c["strict"] and not c["pair_explicit"])
    st["by_form"] = dict(collections.Counter("%s%s" % (c["form"], "*" if c["strict"] else "") for c in out))
    st["counts"] = dict(sorted(cnt.items()))

    def desc(node):
        return {"node": node, "name": S[node][2], "cite": S[node][1], "date": int(D.date[node]),
                "court": "Supreme Court of the United States"}

    rows = [["id", "tier", "w", "x", "y", "w_date", "x_date", "y_date", "note_kind", "note_scope", "part", "offset",
             "w_sha", "w_rank", "strict", "form", "pair_explicit_ok", "pair_has_witness", "w_power_rule"]]
    with gzip.open(R.ITEMS_T1S + ".part", "wt", encoding="utf-8", newline="\n") as f:
        for k, c in enumerate(out):
            cid = "s%05d" % (k + 1)
            stem = next(s for s in R.KIND_STEM.values() if c["word"].startswith(s))
            kind = next(kk for kk, s in R.KIND_STEM.items() if s == stem)
            it = {"id": cid, "tier": "T1s", "w": c["w"], "x": c["x"], "y": c["y"], "sha": c["sha"], "len": c["len"],
                  "off": c["off"], "note_end": c["note_end"], "part": c["part"], "part_raw": c["part_raw"],
                  "sec": c["sec"], "d0": c["d0"], "d1": c["d1"], "s0": c["s0"], "text": c["text"],
                  "parts": c["parts"], "intro": c["intro"], "para": c["para"], "note_kind": kind, "note_scope": c["scope"],
                  "W": desc(c["w"]), "X": desc(c["x"]), "Y": desc(c["y"]), "repo": "supreme-court",
                  "path": c["path"], "w_power": "yes", "w_power_rule": c["wrule"], "rank": c["rank"],
                  "pair_explicit": c["pair_explicit"], "pair_witness": c["pair_witness"], "strict": c["strict"],
                  "form": c["form"]}
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            rows.append([cid, "T1s", c["w"], c["x"], c["y"], int(D.date[c["w"]]), int(D.date[c["x"]]),
                         int(D.date[c["y"]]), kind, c["scope"], c["part"], c["off"], c["sha"], c["rank"],
                         c["strict"], c["form"], c["pair_explicit"], c["pair_witness"], c["wrule"]])
    os.replace(R.ITEMS_T1S + ".part", R.ITEMS_T1S)
    R.write_rows(os.path.join(R.HERE, "candidates_t1s.tsv"), rows)
    R.write_text(os.path.join(R.HERE, "stats_t1s.json"), json.dumps(st, indent=1) + "\n")
    print(json.dumps(st, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
