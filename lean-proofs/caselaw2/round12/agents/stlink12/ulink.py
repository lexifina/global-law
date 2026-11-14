"""stlink10 rule U: the uncited intermediate decision under review, named only by court in the opinion's own text.

    python -X utf8 ulink.py run [--procs 8] [--tag u1]   -> work/ulink/<shard>.rows.jsonl, rows_<tag>.jsonl

Acting decision D: a state court-of-last-resort opinion (tier L) with no v9c review-kind row on an intermediate
decision, citing NO decision of its state's intermediate courts that shares a party name with its caption (cap >= 1),
whose own judgment line (round 6 decide, named or bare) reverses / vacates / modifies the intermediate court's
decision. Target T: the only decision of the state's intermediate courts dated 0..5 years before D whose caption is
D's caption (cap 2, a distinctive shared party token: not institutional, printed in <= 5,000 titles; from
graph/nodes.tsv, pop.py caption pass); no decision of D's court or a higher one with that caption between T and D.
Anchor (D's own majority / per curiam text): a sentence naming T's court acting ("the Court of Appeals reversed /
affirmed / held ..."), extended back (<= 1,200 characters, same part) to the start of the sentence that holds the
full party names of T's caption (a shared name token of every named side); no citation of another intermediate-court
decision inside; round 6's earlier / interlocutory / later-events / disqualifier guards on the anchor. Evidence
`name:<tokens>`. Disposition, scope: as stlink.py (mixed end zone, rule P, own-disposition, dated otherwise).
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stlink as S  # noqa: E402
from stlink import BO, L, C, FL  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "ulink")
BACK = 1200
WORD = re.compile(r"[A-Za-z0-9]+")


def select(n, g, mrow, st):
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    sysid = F.system(dc)
    d_date = int(F.date[n])
    if sysid in (0, -1) or not d_date:
        return []
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier != "L":
        return []
    st["opinions"] += 1
    if n in S.G["based"]:
        return []
    cands = S.G["capm"].get(n)
    if not cands:
        return []
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    # no cited same-litigation intermediate decision (those are rules s1 / g2)
    for cw in g["cw"]:
        j = cw["j"]
        jc = int(F.court[j])
        if F.system(jc) == sysid and BO.court_at(jc, int(F.date[j]))[1] == "A" and \
                BO.cap_rel(d_all, N.name(j), d_sides) >= 1:
            st["drop:cited_samelit"] += 1
            return []
    good = [j for j in cands if S.distinct_shared(d_all, N.name(j))]
    if len(good) != 1:
        st["drop:not_unique" if good else "drop:no_distinct"] += 1
        return []
    j = good[0]
    later_same = 0
    for cw in g["cw"]:
        if cw["rel"] != "lower" and BO.cap_rel(d_all, N.name(cw["j"]), d_sides) >= 2:
            later_same = max(later_same, int(F.date[cw["j"]]))
    if later_same and int(F.date[j]) <= later_same < d_date:
        st["drop:reviewed_before"] += 1
        return []
    if (n, j) in S.G["pairs"]:
        st["skip:pair_in_base"] += 1
        return []
    d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
    phrases, cls = BO.tphr(int(F.court[j]), int(F.date[j]))
    if cls != "app":
        return []
    ph = {p for p in phrases if p not in d_name}
    if "appellate division" in ph:
        ph.discard("superior court")
    # tokens: one shared token per named side of T's caption
    j_all, j_sides = BO.caption(N.name(j))
    toks = []
    for side in j_sides:
        if not side:
            continue
        sh = sorted(side & d_all, key=lambda t: S.G["tokdf"].get(t.lower().rstrip("s"), 0))
        if not sh:
            st["drop:side_not_shared"] += 1
            return []
        toks.append(sh[0])
    if not toks:
        return []
    st["candidates"] += 1
    return [(j, ph, cls, toks, BO.day(d_date) - BO.day(F.date[j]))]


def finish(n, g, T, cand, st):
    F = BO.G["F"]
    j, phrases, cls, toks, gap = cand
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    disps = BO.dispositions(g)
    res, why = BO.decide(disps, phrases, True)
    if res is None:
        st["drop:disp:" + why] += 1
        return None
    kind, scope, (q0, q1), part, dhow = res
    if kind not in S.NEG:
        st["drop:disp_kind:" + kind] += 1
        return None
    want = (phrases & FL.CUE_PHRASES) | {"court below"}
    low_toks = [t.lower() for t in toks]
    anchor = None
    why = "no_court_act"
    for a, b, p in z["parts"]:
        apart = BO.OKPART.get(p)
        if apart is None:
            continue
        for m in BO.COURT_RX.finditer(T, a, b):
            if BO.norm_ws(m.group(1)) not in want or not S.COURT_ACT.match(T[m.end():m.end() + 90]):
                continue
            s0, s1 = C.sentence_span(T, m.start(), m.end())
            s0, s1 = max(s0, a), min(s1, b)
            lo = max(a, s0 - BACK)
            # earliest start so that [x, s1) holds every token: scan back sentence by sentence
            x = s0
            while True:
                words = {w.group(0).lower() for w in WORD.finditer(T, x, s1)}
                if all(t in words for t in low_toks):
                    break
                if x <= lo:
                    x = None
                    break
                k = x - 1
                while k > lo and T[k] == " ":
                    k -= 1
                x = max(lo, C.sentence_span(T, k, k + 1)[0])
            if x is None:
                why = "tokens_not_near"
                continue
            bad = False
            for cm in C.CITE_RX.finditer(T, x, s1):
                if S.APP_REP.search(cm.group(0)):
                    bad = True
                    break
            if bad:
                why = "app_cite_inside"
                continue
            gw = FL.guard_anchor(T, x, s1, {"c": [s1, s1]})
            if gw:
                why = gw
                continue
            anchor = (x, s1, apart)
            break
        if anchor:
            break
    if anchor is None:
        st["drop:anchor:" + why] += 1
        return None
    a0, a1, apart = anchor
    if scope == "all" and kind in ("reversed", "vacated"):
        zt = " ".join(e[1] for e in (z.get("ends") or []))
        if z.get("full"):
            zt = z["head"][1]
        if z.get("open"):
            zt += " " + z["open"][1]
        if BO.OWN_AFF.search(zt) or BO.OWN_MIXED.search(zt):
            scope = "unknown"
        body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
        if S.PARTIAL_HINT.search(body):
            scope = "unknown"
    dsent = next((d[2] for d in disps if d[0] == q0), "")
    am = BO.ACT.search(dsent)
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    st["rows"] += 1
    st["rows:%s:%s" % (kind, scope)] += 1
    return {"rule": "below:stlink10_u", "table": "history", "claim": "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": "name:" + " ".join(t.lower() for t in toks), "part": part, "text": "by",
            "note": "%s|%s|cap2|gap%dd|L|stlink10 u uncited" % (cls, dhow, gap)}


def run_shard(path):
    if "based" not in S.G:
        S.init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    for n, g in L.decisions(path):
        try:
            cs = select(n, g, meta.get(n), st)
        except Exception as ex:  # noqa: BLE001
            st["error_select"] += 1
            if st["error_select"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        for c in cs:
            pend.append((n, g, c))
    texts = L.fetch_texts([n for n, _, _ in pend]) if pend else {}
    rows = []
    for n, g, c in pend:
        if n not in texts:
            continue
        try:
            r = finish(n, g, L.norm(texts[n][1]), c, st)
        except Exception as ex:  # noqa: BLE001
            st["error_finish"] += 1
            if st["error_finish"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        if r:
            rows.append(r)
    with open(os.path.join(WORK, tag + ".rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--shards")
    ap.add_argument("--tag", default="u1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    import pop
    paths = pop.state_shards()
    if a.shards:
        want = set(a.shards.split(","))
        paths = [p for p in paths if os.path.basename(p)[:-len(".jsonl.gz")] in want]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.procs <= 1:
        S.init()
        for p in paths:
            print(run_shard(p), flush=True)
    else:
        for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=S.init):
            print(tag, k, flush=True)
    if not a.shards:
        tot = collections.Counter()
        rows = []
        for p in sorted(paths):
            tag = os.path.basename(p)[:-len(".jsonl.gz")]
            rp = os.path.join(WORK, tag + ".rows.jsonl")
            if os.path.exists(rp):
                rows += [l for l in open(rp, encoding="utf-8") if l.strip()]
                tot.update(json.load(open(os.path.join(WORK, tag + ".stats.json"))))
        with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
            f.writelines(rows)
        json.dump(dict(sorted(tot.items())), open(os.path.join(HERE, "link_stats_%s.json" % a.tag), "w"), indent=1)
        print("rows", len(rows))


if __name__ == "__main__":
    main()
