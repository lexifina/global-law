"""state8 rule R8S, step 2: rescued act sentences -> reader candidates with their target decisions (the round-7
antecedent agent's resolution, round7/agents/antecedent/antecands.py, reused unchanged: citations in the act
sentence or the 2000 characters before it in the same part, names of decisions the opinion cites elsewhere, power
and date filter).

    python -X utf8 rescue_cands.py [--include-multi]

In: work/rescue/*.jsonl (rescue.py). Selected: not in the own-act queue, not packed by the round-7 antecedent agent,
act sentence naming at most one case (else agent `multicase`). Out: work/rcands.jsonl (antecands format + "tag",
"reason"), work/rcands_stats.json. Part of a PF item = majority (the repaired part map). No answer-key file is read.
"""
import argparse, collections, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common8 import C2, L  # noqa: E402
sys.path.insert(0, os.path.join(C2, "round7", "agents", "antecedent"))
import antecands as AC  # noqa: E402
import rescue_rules as RR  # noqa: E402
C = L.reader_common()
NL = chr(10)
OPC = ("majority", "majority~", "perCuriam", "plurality")
HEAD_LINE = re.compile(r"^#+ ", re.M)


def norm(s):
    return s.replace(chr(9), " ").replace(NL, " ").replace(chr(13), " ")


def build(items, text):
    """antescan-format records for the rescued sentences of one decision."""
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    # repaired part map (PF): a concurrence~ segment that follows a short majority opening block is majority
    segs = []
    for i, (a, b, p, s_) in enumerate(pm):
        if p == "concurrence~" and i > 0 and pm[i - 1][2] in ("majority", "perCuriam") and \
                pm[i - 1][1] - pm[i - 1][0] < 400 and pm[i - 1][1] == a:
            segs.append((pm[i - 1][0], b, pm[i - 1][2]))
            continue
        if p in OPC:
            segs.append((a, b, p))
    ocites, seen = [], set()
    for a2, b2, p2 in segs:
        for cm in C.CITE_RX.finditer(view, a2, b2):
            k = C.cite_key(cm)
            if k and k not in seen and len(ocites) < 300:
                seen.add(k)
                ocites.append([k, norm(view[max(a2, cm.start() - 90):cm.start()])])
    out = []
    for it in items:
        s0, s1 = it["s0"], it["s1"]
        seg = [sg for sg in segs if sg[0] <= s0 < sg[1]]
        if not seg:
            out.append(("nopart", it))
            continue
        a, b, p = seg[-1]
        s1 = min(s1, b)
        w0 = max(a, s0 - 2000)
        hh = [h.start() for h in HEAD_LINE.finditer(view, w0, s0)]
        if hh:
            w0 = view.find(NL, hh[-1]) + 1 or s0
        cites = []
        for cm in C.CITE_RX.finditer(view, w0, s1):
            k = C.cite_key(cm)
            if k:
                cites.append([k, cm.start(), cm.end()])
        out.append(("ok", {"n": it["n"], "s": [s0, s1], "act": norm(view[s0:s1]), "part": p, "flags": [],
                           "hw": int(hw), "w": [w0, view[w0:s1]], "pstart": a, "cites": cites, "ocites": ocites,
                           "tag": it["tag"], "reason": it["reason"], "rid": it["id"]}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-multi", action="store_true")
    a = ap.parse_args()
    st = collections.Counter()
    sel = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(HERE, "work", "rescue", "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            st["rescued"] += 1
            if r["in_queue"]:
                st["skip_queue"] += 1
                continue
            if r["in_r7ante"]:
                st["skip_r7ante"] += 1
                continue
            if r["refs"] >= 2 and not a.include_multi:
                st["skip_multi"] += 1
                continue
            if r["reason"] == "no-target":
                # the reader's rules already took it as an act; its target was not resolved within 400 characters
                # (round-7 antecedent class), not a rule repair
                st["skip_no_target"] += 1
                continue
            if not RR.shapes2(r["sent"], ["overrule", "disapprove", "recede", "abrogate"]):
                st["skip_not_status_kind"] += 1
                continue
            sel[r["n"]].append(r)
    nodes = sorted(sel)
    recs = []
    for i in range(0, len(nodes), 1500):
        T = L.fetch_texts(nodes[i:i + 1500])
        for n in nodes[i:i + 1500]:
            if n not in T:
                st["no_text"] += len(sel[n])
                continue
            for k, rec in build(sel[n], T[n][1]):
                st["rec_" + k] += 1
                if k == "ok":
                    recs.append(rec)
    print("records", len(recs), dict(st), flush=True)
    # antecands resolution (same functions, same rules)
    F = L.Facts()
    P = AC.Power(F)
    keys = set()
    for r in recs:
        keys.update(k for k, _a, _b in r["cites"])
        keys.update(k for k, _p in r["ocites"])
    res = AC.resolver(keys)
    pairs = AC.base_pairs()
    need = set()
    for r in recs:
        need.add(r["n"])
        for k, _p in r["ocites"]:
            if res.get(k) is not None:
                need.add(res[k])
        for k, _a, _b in r["cites"]:
            if res.get(k) is not None:
                need.add(res[k])
    NM = AC.names_of(need)
    out = open(os.path.join(HERE, "work", "rcands.jsonl"), "w", encoding="utf-8", newline=NL)
    for r in recs:
        n = r["n"]
        s0, s1 = r["s"]
        w0, wt = r["w"]
        rel0 = s0 - w0
        own = C.name_tokens(NM.get(n, ("", ""))[0]) | C.short_name_tokens(NM.get(n, ("", ""))[0])
        tg = {}

        def add(x, how, ev, h0, h1):
            a_, b_ = C.sentence_span(wt, h0 - w0, h1 - w0)
            if h0 >= s0:
                a_, b_, where = rel0, len(wt), "act"
            else:
                b_ = min(b_, rel0)
                where = "far" if rel0 - b_ > AC.GAP else "near"
            a_ += w0
            b_ += w0
            cur = tg.get(x)
            rank = {"act": 0, "near": 1, "far": 2}
            if cur is None or rank[where] < rank[cur["where"]] or (rank[where] == rank[cur["where"]] and (
                    b_ > cur["span"][1] or (b_ == cur["span"][1] and how == "cite" and cur["how"] == "name"))):
                tg[x] = {"t": x, "how": how, "ev": ev, "span": [a_, b_], "where": where, "hit": [h0, h1],
                         "xpara": int(NL in wt[b_ - w0:rel0]) if where == "near" else 0}
        for k, c0, c1 in r["cites"]:
            x = res.get(k)
            if x is None:
                st["cite_unresolved"] += 1
                continue
            if not P.ok(n, x):
                st["cite_nopower"] += 1
                continue
            add(x, "cite", "cite:" + k, c0, c1)
        seen = {}
        for k, pre in r["ocites"]:
            x = res.get(k)
            if x is None or x in seen or x == n:
                continue
            seen[x] = [t for t in AC.printed_tokens(NM.get(x, ("", ""))[0], pre) if t not in own]
        tok_n = collections.Counter(t for toks in seen.values() for t in set(toks))
        for x, toks in seen.items():
            if not P.ok(n, x):
                continue
            toks = [t for t in toks if tok_n[t] == 1]
            if not toks:
                continue
            rx = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(toks)) + r")\b")
            hits = list(rx.finditer(wt, max(0, rel0 - 2000)))
            if not hits:
                continue
            h = hits[-1]
            got = sorted({m.group(0) for m in hits if m.start() >= h.start() - 200})
            add(x, "name", "name:" + " ".join(got[:2]), w0 + h.start(), w0 + h.end())
        near = [v for v in tg.values() if v["where"] in ("near", "act")]
        if not near:
            st["no_near_target"] += 1
            continue
        for v in tg.values():
            nm, cite = NM.get(v["t"], ("", ""))
            v["name"], v["cite"], v["date"], v["court"] = nm, cite, int(F.date[v["t"]]), int(F.court[v["t"]])
            v["base"] = [b[0] for b in pairs.get((n, v["t"]), [])]
        if all(v["base"] for v in near):
            st["all_near_have_base"] += 1
            continue
        st["cands"] += 1
        st["cand_tag:" + r["tag"].split(">")[-1].split(":")[0]] += 1
        rec = {"id": "%d:%d" % (n, s0), "n": n, "s": [s0, s1], "act": r["act"], "part": r["part"], "flags": [],
               "hw": r["hw"], "w0": w0, "pstart": r["pstart"], "wt": wt[max(0, rel0 - 1500):],
               "wt0": w0 + max(0, rel0 - 1500), "by_name": NM.get(n, ("", ""))[0], "by_cite": NM.get(n, ("", ""))[1],
               "by_date": int(F.date[n]), "by_court": int(F.court[n]), "tag": r["tag"], "reason": r["reason"],
               "targets": sorted(tg.values(), key=lambda v: v["hit"][0])}
        out.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + NL)
    out.close()
    json.dump(dict(st), open(os.path.join(HERE, "work", "rcands_stats.json"), "w"), indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
