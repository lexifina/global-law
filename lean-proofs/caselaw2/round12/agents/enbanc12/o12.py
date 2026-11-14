"""enbanc12 rule OP12 (round 12): a corpus order O of the court granting rehearing en banc whose own words vacate the
panel opinion / judgment -> history row by O on the panel opinion P.

    python -X utf8 o12.py   -> work/op12_rows.jsonl, work/op12_pairs.tsv, work/op12_stats.json

Population (pop12.py work files): for every en banc decision E of the base, the same-docket / cited earlier
same-court nodes; O = such a node that is not itself en banc in decisions2, whose text is short (< 6,000 characters
after the front matter) and both grants rehearing en banc and says the panel's / previous opinion or judgment is
vacated (pop12 O_GRANT and O_VAC); P = the latest earlier same-court opinion of the same docket (not an order by
the same test, not en banc) decided before O and at most 2 years before it.
Row: by O, target P, kind vacated, scope all; quote = O's sentence carrying the vacatur words; gates: no negation /
conditional, no partial words (rows12 NEGW / PARTIAL); evidence = a citation of P in or next to the sentence, else
O's caption (head matter or opening of its main part) naming P's parties with an anchor cue. Skipped when P already
has an admitted negative history row or a row by O. No answer-key file is read; no audit answer was used.
"""
import collections, datetime, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pop12 as P  # noqa: E402
import rows12 as R  # noqa: E402

L, C, RL, NL = P.L, P.C, P.RL, P.NL
WORK = P.WORK


def main():
    eb = P.load_eb()
    dk = json.load(open(os.path.join(WORK, "eb_docket.json")))
    tf = json.load(open(os.path.join(WORK, "tgt_feats.json")))
    F = L.Facts()
    pairs = {}
    with open(os.path.join(WORK, "eb_feats.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            d = r["d"]
            sd = set(dk["same_docket"].get(str(d), []))
            for o in sd:
                ft = tf.get(str(o))
                if o in eb or ft is None or not (ft["len"] < 6000 and ft["grant"] and ft["ovac"]):
                    continue
                od = RL.days(int(F.date[o]))
                ops = [m for m in sd if m not in eb and str(m) in tf and not P.is_order(tf[str(m)])
                       and int(F.date[m]) <= int(F.date[o]) and od - RL.days(int(F.date[m])) <= 730]
                if not ops:
                    continue
                p = sorted(ops, key=lambda m: (int(F.date[m]), m))[-1]
                pairs[(o, p)] = d
    print("O,P pairs", len(pairs), flush=True)
    tx = L.fetch_texts(sorted({o for o, _ in pairs}))
    pk = collections.defaultdict(set)
    want = {p for _, p in pairs}
    with open(P.CITE_INDEX, encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split(chr(9))
            if len(q) >= 2 and q[1].isdigit() and int(q[1]) in want:
                pk[int(q[1])].add(q[0])
    hist, _s = P.load_v11d(want)
    NEGK = {"vacated", "withdrawn", "reversed", "substitutedBy", "rehearingEnBancGranted", "modified"}
    st = collections.Counter()
    rows, out = [], []
    seen = set()
    for (o, p), d in sorted(pairs.items()):
        if o not in tx:
            continue
        t0 = tx[o][1]
        lo = P.body_start(t0)
        t = L.norm(t0)
        pm = C.part_map2(t0)
        pm = pm[0] if isinstance(pm, tuple) else pm
        m = P.O_VAC.search(t, lo)
        if not m:
            st["no_vac"] += 1
            continue
        s0, s1 = C.sentence_span(t, m.start(), m.end())
        s0 = max(s0, lo)
        sent = t[s0:s1]
        part = C.part_at(pm, m.start())[0].rstrip("~")
        if part not in R.PARTS_OK:
            st["part_" + part] += 1
            out.append(("part", o, p, sent[:300]))
            continue
        clause = sent[max(0, sent.rfind(";", 0, m.start() - s0) + 1):m.end() - s0]
        if R.NEGW.search(clause) or R.PARTIAL.search(sent):
            st["neg_or_partial"] += 1
            out.append(("neg_or_partial", o, p, sent[:300]))
            continue
        ev, anchor, apart = None, None, None
        a0, _x = C.sentence_span(t, max(lo, s0 - 2), max(lo, s0 - 1))
        _y, b1 = C.sentence_span(t, min(len(t) - 1, s1 + 1), min(len(t), s1 + 2))
        for c in C.CITE_RX.finditer(t[max(lo, a0):b1]):
            k = C.cite_key(c)
            if k and k in pk[p]:
                ev = "cite:" + k
                break
        if ev is None:
            hm = [(a, b, "headmatter") for a, b, nm, _l in pm if nm == "headmatter"]
            if not hm:
                hm = [(a, b, nm.rstrip("~")) for a, b, nm, _l in pm if nm.rstrip("~") in R.PARTS_OK][:1]
            if hm:
                a, b, ap = hm[0]
                cap = t[a:min(b, a + 2500)]
                w = RL.words(cap)
                have = [x for x in sorted(R.tokens(L.node_row(p)[6])) if " " + x.lower() + " " in w]
                if have and not any(x in cap.lower() for x in R.DQA):
                    lastpos = max(cap.lower().find(x.lower()) for x in have[:3])
                    m2 = R.ANCH.search(cap, lastpos)
                    if m2:
                        anchor, apart, ev = [a, a + m2.end()], ap, "name:" + " ".join(have[:3])
        if ev is None:
            st["no_evidence"] += 1
            out.append(("no_evidence", o, p, sent[:300]))
            continue
        prior = hist.get(p, [])
        if any(b == o for b, *_r in prior):
            st["has_row_by_o"] += 1
            out.append(("has_row_by_o", o, p, sent[:300]))
            continue
        if any(k in NEGK and v.startswith("ok") for _b, k, _s, _r, v in prior):
            st["p_already_negative"] += 1
            out.append(("p_already_negative", o, p, sent[:300]))
            continue
        if p in seen:
            st["p_dup"] += 1
            continue
        seen.add(p)
        st["ok_" + ev.split(":")[0]] += 1
        out.append(("ok", o, p, sent[:300]))
        rows.append({"rule": "rehear:op12", "table": "history", "by": o, "target": p, "kind": "vacated",
                     "scope": "all", "main": [s0, s1], "part": part, "ev": ev, "joined": [], "claim": "-",
                     "doctrine": "-", "field_limit": "-", "text": "by", "anchor": anchor, "anchor_part": apart,
                     "note": "enbanc12 OP12: the order granting rehearing en banc vacates the panel opinion in its own words"})
    with open(os.path.join(WORK, "op12_rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "op12_pairs.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(chr(9).join(L.norm(str(v)) for v in x) + NL)
    json.dump(dict(st), open(os.path.join(WORK, "op12_stats.json"), "w"), indent=1)
    print(len(rows), dict(st))


if __name__ == "__main__":
    main()
