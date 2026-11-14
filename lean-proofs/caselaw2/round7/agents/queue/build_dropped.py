"""Round 7, agent `queue`: items for the feed statements that round 5 dropped with the "3 earliest W per (Y, X,
scope group)" cut (round5/recog/build_candidates.py, step 5).

    python -X utf8 build_dropped.py

The filter and the reduction are round5/recog/build_candidates.py, unchanged (same sources, same order, same
functions from round5/recog/recog_common.py): feed_ids.tsv only, joined to gold/reports_typed.tsv through
recog_common.typed_rows (feed ids only); power and dates through the round-5 tests' reference engine; W's text at git
HEAD; the note in an opinion-of-the-court part; one per (W, X, Y, scope group); then per (Y, X, scope group) sorted by
(date(W), W). Round 5 kept ranks 1-3 (the candidates); this script writes the items of ranks 4 and up, in the item
format of round5/recog/items.jsonl.gz (so build_packs.render and certify_recog.py take them unchanged), with
`rank` = the rank and `queue_src` = "cut".

Check: the reproduced ranks 1-3 must be exactly the ids of round5/recog/candidates.tsv (else exit 1).
Writes (this folder): items_dropped.jsonl.gz, dropped_stats.json. Holdout and undetermined files are never opened.
"""
import collections
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RECOG = os.path.join(C2, "round5", "recog")
sys.path.insert(0, RECOG)
import recog_common as R  # noqa: E402

RC = R.RC
TRIG = re.compile(r"overrul|abrogat|disapprov|reced", re.I)
PAD = 700
STORE = 450
KEEP_W = 3
OUT = os.path.join(HERE, "items_dropped.jsonl.gz")


def main():
    st = collections.OrderedDict()
    C = R.tests_common()
    E, pr, meta = C.lite_engine(R.DATA)
    D = E.D

    rows = []
    with open(R.FEED, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[ix["family"]] != "precedent" or p[ix["kind"]] not in R.NEG_KINDS or int(p[ix["by_node"]]) < 0:
                continue
            rows.append({"sid": int(p[ix["id"]]), "w": int(p[ix["note_node"]]), "x": int(p[ix["target_node"]]),
                         "y": int(p[ix["by_node"]]), "kind": p[ix["kind"]], "scope": p[ix["scope"]]})
    st["precedent_named_by"] = len(rows)

    keep, pw = [], {}
    for r in rows:
        w, x, y = r["w"], r["x"], r["y"]
        if not (D.has(w) and D.has(x) and D.has(y)) or w == y or x == y or w == x:
            continue
        r["wd"], r["xd"], r["yd"] = int(D.date[w]), int(D.date[x]), int(D.date[y])
        if not (r["wd"] and r["xd"] and r["yd"] and r["xd"] <= r["yd"] <= r["wd"]):
            continue
        if (w, x) not in pw:
            pw[(w, x)] = E.can_change(w, x, "unknown")
        cc = pw[(w, x)]
        if cc[0] != "yes":
            continue
        r["wrule"] = cc[1]
        if (y, x) not in pw:
            pw[(y, x)] = E.can_change(y, x, "unknown")
        if pw[(y, x)][0] == "no":
            continue
        r["ypower"] = pw[(y, x)][0]
        keep.append(r)
    st["after_power_and_dates"] = len(keep)

    explicit_ok, live_t, wit, _certs = R.explicit_ok_pairs()
    wit_pairs = {(int(live_t[p[0]][1]), int(live_t[p[0]][2])) for p in wit if p[0] in live_t}

    want = set()
    for r in keep:
        want.update((r["w"], r["x"], r["y"]))
    ninfo = R.nodes_info(want)
    dinfo = R.decisions_info(want)
    typed = R.typed_rows({r["sid"] for r in keep})

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

    by_repo = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in keep:
        tr = typed.get(r["sid"])
        if tr is None or r["w"] not in ninfo or r["w"] not in dinfo:
            r["bad"] = "no-typed-row-or-node"
            continue
        r["off_body"] = int(tr["note_offset"])
        by_repo[ninfo[r["w"]][0]][ninfo[r["w"]][1]].append(r)

    def cut(text, a, b):
        d0, d1 = max(0, a - PAD), min(len(text), b + PAD)
        s0, s1 = max(0, d0 - STORE), min(len(text), d1 + STORE)
        return d0, d1, s0, text[s0:s1]

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
        R.log("texts", repo, len(paths))
    keep = [r for r in keep if "off" in r and "bad" not in r]
    st["after_text_checks"] = len(keep)
    keep = [r for r in keep if r["part"] in R.CERT_PARTS]
    st["after_part"] = len(keep)

    first = {}
    for r in sorted(keep, key=lambda r: (r["w"], r["x"], r["y"], r["off"], r["sid"])):
        first.setdefault((r["w"], r["x"], r["y"], r["scope"]), r)
    st["distinct_W_X_Y_scope"] = len(first)
    st["same_W_X_Y_scope_repeats_not_queued"] = len(keep) - len(first)
    pairs = collections.defaultdict(list)
    for r in first.values():
        pairs[(r["y"], r["x"], r["scope"])].append(r)
    cands, dropped = [], []
    for (y, x, _sc), rs in pairs.items():
        rs.sort(key=lambda r: (r["wd"], r["w"]))
        for k, r in enumerate(rs):
            r["rank"] = k + 1
            r["pair_ws"] = len(rs)
            r["pair_explicit"] = 1 if (y, x) in explicit_ok else 0
            r["pair_witness"] = 1 if (y, x) in wit_pairs else 0
            r["tier"] = "T1" if is_scotus(x) else ("T3" if r["pair_explicit"] else "T2")
            r["id"] = "r%d" % r["sid"]
            (cands if k < KEEP_W else dropped).append(r)
    st["candidates_reproduced"] = len(cands)
    st["dropped_by_cut"] = len(dropped)

    r5 = {p[0] for p in R.read_rows(os.path.join(RECOG, "candidates.tsv"), 2)[1:]}
    mine = {r["id"] for r in cands}
    st["reproduction_matches_round5_candidates"] = (mine == r5)
    st["reproduction_diff"] = [len(mine - r5), len(r5 - mine)]
    if mine != r5:
        print(json.dumps(st, indent=1))
        R.log("reproduction differs from round5/recog/candidates.tsv: not writing items")
        return 1
    st["dropped_by_tier"] = dict(collections.Counter(r["tier"] for r in dropped))
    st["dropped_by_note_scope"] = dict(collections.Counter(r["scope"] for r in dropped))
    st["dropped_pairs_Y_X"] = len({(r["y"], r["x"]) for r in dropped})

    def desc(node):
        ni = ninfo.get(node, ("", "", "", ""))
        return {"node": node, "name": ni[3], "cite": ni[2], "date": int(D.date[node]), "court": court_name(node)}

    dropped.sort(key=lambda r: (r["tier"], r["y"], r["x"], r["rank"]))
    with gzip.open(OUT + ".part", "wt", encoding="utf-8", newline="\n") as f:
        for r in dropped:
            it = {"id": r["id"], "tier": r["tier"], "sid": r["sid"], "w": r["w"], "x": r["x"], "y": r["y"],
                  "sha": r["sha"], "len": r["len"], "off": r["off"], "part": r["part"], "part_raw": r["part_raw"],
                  "sec": r["psec"], "d0": r["d0"], "d1": r["d1"], "s0": r["s0"], "text": r["text"],
                  "parts": r["parts"], "intro": r["intro"], "para": r["para"],
                  "note_kind": r["kind"], "note_scope": r["scope"], "W": desc(r["w"]), "X": desc(r["x"]),
                  "Y": desc(r["y"]), "repo": ninfo[r["w"]][0], "path": ninfo[r["w"]][1], "w_power": "yes",
                  "w_power_rule": r["wrule"], "y_power": r["ypower"], "rank": r["rank"],
                  "pair_explicit": r["pair_explicit"], "pair_witness": r["pair_witness"], "queue_src": "cut"}
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    os.replace(OUT + ".part", OUT)
    R.write_text(os.path.join(HERE, "dropped_stats.json"), json.dumps(st, indent=1) + "\n")
    print(json.dumps(st, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
