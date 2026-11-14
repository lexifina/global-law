"""Round 5, agent `recog`: candidates for the "recognised overruling" rows (DESIGN5 sections 2 and 7).

    python -X utf8 build_candidates.py

Source: round5/tests/split/feed_ids.tsv ONLY (the later-court statements whose speaker may enter the model), joined
by statement id to gold/reports_typed.tsv for the position of the note (section, offset, repo), and the corpus text
of W from git. The holdout and undetermined files are never opened.

Filter (each drop is counted in stats.json, in this order):
  family precedent, a named by-decision, kind overruled / abrogated / disapproved / recededFrom;
  W, X, Y in the corpus and pairwise different;
  date(X) <= date(Y) <= date(W), none 0;
  W has POWER over X: reference Engine.can_change(W, X, 'unknown') == yes (as round5/tests/common.py loads it);
  Y is not shown to lack power over X (can_change(Y, X) != no; the checker would answer noAuthority);
  W's text at HEAD hashes to its decisions2 text_sha, and an overruling word stands at the note's offset;
  the note stands in an opinion-of-the-court part (reader/common.part_map2: majority, perCuriam, plurality).
Reduce: one candidate per (W, X, Y) (the first position in the text), and per (Y, X) the 3 earliest W.
Tiers: T1 = X is a decision of the Supreme Court of the United States; T2 = other X, the pair (Y, X) has no explicit
scope-all status-changing row by Y on X that is `ok` in out/certs.tsv; T3 = other X with such a row.
T0 = the rows of data/treatment_witness.tsv (round 4), to be re-read under the round-5 rule.

Writes (round5/recog/): candidates.tsv, items.jsonl.gz (one JSON per item: ids, dates, names, the part, and W's
text around the note), stats.json.
"""
import collections
import gzip
import json
import os
import re
import sys

import recog_common as R

RC = R.RC
TRIG = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
PAD = 700          # shown to the reader on each side of the note
STORE = 450        # kept beyond the shown window, for the certificate window (quote +-400)
KEEP_W = 3


def main():
    st = collections.OrderedDict()
    C = R.tests_common()
    E, pr, meta = C.lite_engine(R.DATA)
    D = E.D

    # ---- 1. feed rows
    rows = []
    with open(R.FEED, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        n = 0
        for line in f:
            n += 1
            p = line.rstrip("\n").split("\t")
            if p[ix["family"]] != "precedent" or p[ix["kind"]] not in R.NEG_KINDS or int(p[ix["by_node"]]) < 0:
                continue
            rows.append({"sid": int(p[ix["id"]]), "w": int(p[ix["note_node"]]), "x": int(p[ix["target_node"]]),
                         "y": int(p[ix["by_node"]]), "kind": p[ix["kind"]], "scope": p[ix["scope"]],
                         "implicit": p[ix["implicit"]], "fpower": p[ix["power"]], "frule": p[ix["rule"]]})
    st["feed_rows"] = n
    st["precedent_named_by"] = len(rows)

    drop = collections.Counter()
    keep = []
    pw = {}
    for r in rows:
        w, x, y = r["w"], r["x"], r["y"]
        if not (D.has(w) and D.has(x) and D.has(y)):
            drop["not-in-corpus"] += 1
            continue
        if w == y or x == y or w == x:
            drop["same-node"] += 1
            continue
        r["wd"], r["xd"], r["yd"] = int(D.date[w]), int(D.date[x]), int(D.date[y])
        if not (r["wd"] and r["xd"] and r["yd"] and r["xd"] <= r["yd"] <= r["wd"]):
            drop["dates"] += 1
            continue
        if (w, x) not in pw:
            pw[(w, x)] = E.can_change(w, x, "unknown")
        cc = pw[(w, x)]
        if cc[0] != "yes":
            drop["w-no-power:" + cc[1]] += 1
            continue
        r["wrule"] = cc[1]
        if (y, x) not in pw:
            pw[(y, x)] = E.can_change(y, x, "unknown")
        cy = pw[(y, x)]
        if cy[0] == "no":
            drop["y-no-power:" + cy[1]] += 1
            continue
        r["ypower"] = cy[0]
        keep.append(r)
    st["after_power_and_dates"] = len(keep)
    R.log("after power and dates:", len(keep))

    # ---- 2. the existing witness rows (T0) and the explicit pairs
    live_t = {p[0]: p for p in R.read_rows(os.path.join(R.DATA, "treatments.tsv"), 16)}
    wit = R.read_rows(os.path.join(R.DATA, "treatment_witness.tsv"), 4)
    certs = {}
    for p in R.read_rows(os.path.join(R.C2, "out", "certs.tsv"), 3):
        if p[0] == "treatment":
            certs[p[1]] = p[2]
    explicit_ok = set()
    for p in live_t.values():
        if p[7] == "1" and p[4] in R.NEG_KINDS and p[5] == "all" and certs.get(p[0]) == "ok":
            explicit_ok.add((int(p[1]), int(p[2])))
    wit_pairs = set()
    t0 = []
    for p in wit:
        t = live_t.get(p[0])
        if t is None:
            continue
        wit_pairs.add((int(t[1]), int(t[2])))
        t0.append({"old_id": p[0], "w": int(p[1]), "x": int(t[2]), "y": int(t[1]), "kind": t[4], "scope": t[5],
                   "start": int(t[9]), "end": int(t[10]), "sha": t[8], "old_by_ev": p[2], "old_x_ev": t[12],
                   "old_cert": certs.get(p[0], "")})
    st["explicit_all_ok_pairs_in_model"] = len(explicit_ok)
    st["t0_witness_rows"] = len(t0)

    # ---- 3. lookups
    want = set()
    for r in keep:
        want.update((r["w"], r["x"], r["y"]))
    for r in t0:
        want.update((r["w"], r["x"], r["y"]))
    R.log("nodes wanted:", len(want))
    ninfo = R.nodes_info(want)
    dinfo = R.decisions_info(want)
    typed = R.typed_rows({r["sid"] for r in keep})
    st["typed_rows_joined"] = len(typed)
    R.log("lookups done")

    def court_name(node):
        c, d = int(D.court[node]), int(D.date[node])
        e = E.epoch(c, d)
        if e is None:
            eps = E.courts.get(c)
            e = eps[0] if eps else None
        return e.name if e is not None else "court %d" % c

    def is_scotus(node):
        e = E.epoch(int(D.court[node]), int(D.date[node]))
        return e is not None and E.is_scotus(e)

    # ---- 4. W's text: part and window per candidate
    by_repo = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in keep:
        tr = typed.get(r["sid"])
        if tr is None or r["w"] not in ninfo or r["w"] not in dinfo:
            drop["no-typed-row-or-node"] += 1
            continue
        r["off_body"] = int(tr["note_offset"])
        r["sec"] = tr["sec"]
        r["form"] = tr["form"]
        repo, path = ninfo[r["w"]][0], ninfo[r["w"]][1]
        by_repo[repo][path].append(r)
    for r in t0:
        if r["w"] not in ninfo or r["w"] not in dinfo:
            r["bad"] = "no-node"
            continue
        repo, path = ninfo[r["w"]][0], ninfo[r["w"]][1]
        by_repo[repo][path].append(r)

    def cut(text, a, b):
        d0, d1 = max(0, a - PAD), min(len(text), b + PAD)
        s0, s1 = max(0, d0 - STORE), min(len(text), d1 + STORE)
        return d0, d1, s0, text[s0:s1]

    done = 0
    for repo in sorted(by_repo):
        paths = sorted(by_repo[repo])
        for k in range(0, len(paths), 300):
            chunk = paths[k:k + 300]
            raws = R.git_texts(repo, chunk)
            for path in chunk:
                rs = by_repo[repo][path]
                raw = raws.get(path)
                wnode = rs[0]["w"]
                if raw is None:
                    for r in rs:
                        r["bad"] = "text-missing"
                    continue
                if R.sha1_bytes(raw) != dinfo[wnode][2]:
                    for r in rs:
                        r["bad"] = "text-sha-differs"
                    continue
                text = R.decode(raw)
                pm, body0 = RC.part_map2(text)
                b0 = R.body_start(text)
                hw = None
                for r in rs:
                    r["sha"] = dinfo[wnode][2]
                    r["len"] = len(text)
                    if "old_id" in r:
                        a, b = r["start"], r["end"]
                        if R.clean(text[a:b]) != live_t[r["old_id"]][11]:
                            r["bad"] = "old-quote-not-at-offsets"
                            continue
                    else:
                        a = b0 + r["off_body"]
                        if not TRIG.search(text[a:a + 90]):
                            r["bad"] = "note-not-at-offset"
                            continue
                        b = a + 40
                    r["off"] = a
                    part, sec = RC.part_at(pm, a)
                    r["part_raw"] = part
                    r["part"] = R.PART_OUT.get(part, part.rstrip("~") or "unknown")
                    r["psec"] = sec
                    r["d0"], r["d1"], r["s0"], r["text"] = cut(text, a, b)
                    s1 = r["s0"] + len(r["text"])
                    r["parts"] = [[max(pa, r["s0"]), min(pb, s1), R.PART_OUT.get(pp, pp.rstrip("~") or "unknown")]
                                  for (pa, pb, pp, _s) in pm if pa < s1 and pb > r["s0"]]
                    if hw is None:
                        hw = RC.hard_wrapped(text, body0)
                    r["intro"], r["para"] = R.para_intro(text, a, r["d0"], hw)
            done += len(chunk)
        R.log("texts", repo, len(paths))
    for r in keep:
        if "bad" in r:
            drop[r["bad"]] += 1
    keep = [r for r in keep if "off" in r and "bad" not in r]
    st["after_text_checks"] = len(keep)
    parts = collections.Counter(r["part"] for r in keep)
    st["note_parts"] = dict(parts)
    for r in keep:
        if r["part"] not in R.CERT_PARTS:
            drop["part:" + r["part"]] += 1
    keep = [r for r in keep if r["part"] in R.CERT_PARTS]
    st["after_part"] = len(keep)

    # ---- 5. reduce
    # one candidate per (W, X, Y) and scope group of the note (all | partialUnknown | otherGrounds): the first
    # position in W's text; then per (Y, X) and scope group the 3 earliest W. The scope group is kept apart because
    # "X, overruled on other grounds by Y" (four notes in five) and "X, overruled by Y" are different statements:
    # the earliest W that says the second fixes the date of the negative status.
    first = {}
    for r in sorted(keep, key=lambda r: (r["w"], r["x"], r["y"], r["off"], r["sid"])):
        first.setdefault((r["w"], r["x"], r["y"], r["scope"]), r)
    st["distinct_W_X_Y_scope"] = len(first)
    st["distinct_W_X_Y"] = len({k[:3] for k in first})
    pairs = collections.defaultdict(list)
    for r in first.values():
        pairs[(r["y"], r["x"], r["scope"])].append(r)
    st["distinct_pairs_Y_X"] = len({k[:2] for k in pairs})
    st["distinct_pairs_Y_X_scope"] = len(pairs)
    cands = []
    for (y, x, _sc), rs in pairs.items():
        rs.sort(key=lambda r: (r["wd"], r["w"]))
        for k, r in enumerate(rs[:KEEP_W]):
            r["rank"] = k + 1
            r["pair_ws"] = len(rs)
            r["pair_explicit"] = 1 if (y, x) in explicit_ok else 0
            r["pair_witness"] = 1 if (y, x) in wit_pairs else 0
            r["x_scotus"] = 1 if is_scotus(x) else 0
            r["tier"] = "T1" if r["x_scotus"] else ("T3" if r["pair_explicit"] else "T2")
            r["id"] = "r%d" % r["sid"]
            cands.append(r)
        drop["later-W-beyond-3"] += max(0, len(rs) - KEEP_W)
    st["candidates"] = len(cands)
    tiers = collections.OrderedDict()
    for t in ("T1", "T2", "T3"):
        cs = [r for r in cands if r["tier"] == t]
        tiers[t] = {"candidates": len(cs), "pairs": len({(r["y"], r["x"]) for r in cs}),
                    "by_note_scope": dict(collections.Counter(r["scope"] for r in cs)),
                    "pairs_with_a_scope_all_note": len({(r["y"], r["x"]) for r in cs if r["scope"] == "all"})}
    t1 = [r for r in cands if r["tier"] == "T1"]
    tiers["T1"]["candidates_pair_already_explicit"] = sum(r["pair_explicit"] for r in t1)
    tiers["T1"]["candidates_pair_not_explicit"] = sum(1 - r["pair_explicit"] for r in t1)
    tiers["T1"]["pairs_already_explicit"] = len({(r["y"], r["x"]) for r in t1 if r["pair_explicit"]})
    tiers["T1"]["pairs_not_explicit"] = len({(r["y"], r["x"]) for r in t1 if not r["pair_explicit"]})
    t0ok = [r for r in t0 if "off" in r and "bad" not in r]
    tiers["T0"] = {"candidates": len(t0ok), "rows_not_staged": collections.Counter(
        r.get("bad", "") for r in t0 if r not in t0ok)}
    st["tiers"] = tiers
    st["kinds"] = dict(collections.Counter(r["kind"] for r in cands))
    st["note_scopes"] = dict(collections.Counter(r["scope"] for r in cands))
    st["w_power_rule"] = dict(collections.Counter(r["wrule"] for r in cands))
    st["y_power"] = dict(collections.Counter(r["ypower"] for r in cands))
    st["dropped"] = dict(sorted(drop.items()))

    # ---- 6. write
    def desc(node):
        ni = ninfo.get(node, ("", "", "", ""))
        return {"node": node, "name": ni[3], "cite": ni[2], "date": int(D.date[node]), "court": court_name(node)}

    cands.sort(key=lambda r: (r["tier"], r["y"], r["x"], r["rank"]))
    R.write_rows(os.path.join(R.HERE, "candidates.tsv"), [[
        "id", "tier", "w", "x", "y", "w_date", "x_date", "y_date", "note_kind", "note_scope", "part", "offset",
        "w_sha", "w_rank", "pair_ws", "pair_explicit_ok", "pair_has_witness", "w_power_rule", "y_power"]] + [[
            r["id"], r["tier"], r["w"], r["x"], r["y"], r["wd"], r["xd"], r["yd"], r["kind"], r["scope"], r["part"],
            r["off"], r["sha"], r["rank"], r["pair_ws"], r["pair_explicit"], r["pair_witness"], r["wrule"],
            r["ypower"]] for r in cands])
    with gzip.open(R.ITEMS + ".part", "wt", encoding="utf-8", newline="\n") as f:
        for k, r in enumerate(sorted(t0ok, key=lambda r: r["old_id"])):
            cc = E.can_change(r["w"], r["x"], "unknown")
            it = {"id": "w%03d" % (k + 1), "tier": "T0", "old_id": r["old_id"], "w": r["w"], "x": r["x"],
                  "y": r["y"], "sha": r["sha"], "len": r["len"], "off": r["off"], "note_end": r["end"],
                  "part": r["part"], "part_raw": r["part_raw"], "sec": r["psec"], "d0": r["d0"], "d1": r["d1"],
                  "s0": r["s0"], "text": r["text"], "parts": r["parts"], "intro": r["intro"], "para": r["para"], "note_kind": r["kind"], "note_scope": r["scope"],
                  "W": desc(r["w"]), "X": desc(r["x"]), "Y": desc(r["y"]), "repo": ninfo[r["w"]][0],
                  "path": ninfo[r["w"]][1], "w_power": cc[0], "w_power_rule": cc[1], "old_cert": r["old_cert"],
                  "pair_explicit": 1 if (r["y"], r["x"]) in explicit_ok else 0}
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
        for r in cands:
            it = {"id": r["id"], "tier": r["tier"], "sid": r["sid"], "w": r["w"], "x": r["x"], "y": r["y"],
                  "sha": r["sha"], "len": r["len"], "off": r["off"], "part": r["part"], "part_raw": r["part_raw"],
                  "sec": r["psec"], "d0": r["d0"], "d1": r["d1"], "s0": r["s0"], "text": r["text"], "parts": r["parts"], "intro": r["intro"], "para": r["para"],
                  "note_kind": r["kind"], "note_scope": r["scope"], "W": desc(r["w"]), "X": desc(r["x"]),
                  "Y": desc(r["y"]), "repo": ninfo[r["w"]][0], "path": ninfo[r["w"]][1], "w_power": "yes",
                  "w_power_rule": r["wrule"], "rank": r["rank"], "pair_explicit": r["pair_explicit"],
                  "pair_witness": r["pair_witness"]}
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    os.replace(R.ITEMS + ".part", R.ITEMS)
    R.write_text(os.path.join(R.HERE, "stats.json"), json.dumps(st, indent=1) + "\n")
    print(json.dumps(st, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
