"""notarget (round 8): the reader's `no-target` act sentences (state8 rescue.py output, reason == no-target) ->
reader candidates with their target decisions, by the round-7 antecedent resolution reused unchanged
(round7/agents/antecedent/antecands.py through state8 rescue_cands.build: citations in the act sentence or the
2000 characters before it in the same part; names of decisions the opinion cites elsewhere; power and date filter).

    python -X utf8 nt_cands.py

Selected: reason == no-target, not in the own-act queue, not packed by the round-7 antecedent agent, act sentence
naming at most one case group (else multicase), a status-kind shape (state8 rescue_rules.shapes2).
Dropped: candidates whose every near/in-act target pair (W, X) already has an admitted row in v3
(round7/out/v3 certs ok/okUnverifiedBy, explicit, status kind) or a row in the cert/ folders of ownact, multicase,
state8 (round 8).
Out: work/ntcands.jsonl (antecands format + tag, reason, repo), work/ntcands_stats.json, work/profile.json.
No answer-key file is read.
"""
import collections, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
S8 = os.path.join(C2, "round8", "agents", "state8")
sys.path.insert(0, S8)
from common8 import L  # noqa: E402
sys.path.insert(0, os.path.join(C2, "round7", "agents", "antecedent"))
import antecands as AC  # noqa: E402
import rescue_rules as RR  # noqa: E402
import rescue_cands as RC  # noqa: E402
NL = chr(10)
WORK = os.path.join(HERE, "work")
STATUS_KINDS = ("overruled", "disapproved", "abrogated", "recededFrom")
VERB_RX = re.compile(r"\b(overrul\w*|disapprov\w*|reced\w*|abrogat\w*|repudiat\w*|overturn\w*|no longer\w*)", re.I)


def pairs_v3_and_round8():
    ok = set()
    for line in open(os.path.join(C2, "round7", "out", "v3", "certs.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] == "treatment" and p[2] in ("ok", "okUnverifiedBy"):
            ok.add(p[1])
    pairs = {}
    for line in open(os.path.join(C2, "round7", "stage", "v3", "treatments.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if p[0] in ok and p[7] == "1" and p[4] in STATUS_KINDS:
            pairs.setdefault((int(p[1]), int(p[2])), []).append(p[0])
    for ag in ("ownact", "multicase", "state8"):
        fp = os.path.join(C2, "round8", "agents", ag, "cert", "treatments_delta.tsv")
        if os.path.exists(fp):
            for line in open(fp, encoding="utf-8"):
                p = line.rstrip(NL).split("\t")
                if len(p) > 3:
                    pairs.setdefault((int(p[1]), int(p[2])), []).append(p[0])
        fp = os.path.join(C2, "round8", "agents", ag, "cert", "history_delta.tsv")
        if os.path.exists(fp):
            for line in open(fp, encoding="utf-8"):
                p = line.rstrip(NL).split("\t")
                if len(p) > 3:
                    try:
                        pairs.setdefault((int(p[1]), int(p[2])), []).append(p[0])
                    except ValueError:
                        pass
    return pairs


def main():
    os.makedirs(WORK, exist_ok=True)
    st = collections.Counter()
    prof = collections.defaultdict(collections.Counter)
    sel = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(S8, "work", "rescue", "*.jsonl"))):
        repo = os.path.basename(p)[:-6]
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["reason"] != "no-target":
                continue
            st["no_target"] += 1
            prof["repo_all"][repo] += 1
            vm = VERB_RX.search(r["sent"])
            prof["verb_all"][(vm.group(1).lower()[:8] if vm else "-")] += 1
            prof["tag_all"][r["tag"].split(">")[-1]] += 1
            if r["in_queue"]:
                st["skip_queue"] += 1
                continue
            if r["in_r7ante"]:
                st["skip_r7ante"] += 1
                continue
            if r["refs"] >= 2:
                st["skip_multi"] += 1
                continue
            if not RR.shapes2(r["sent"], ["overrule", "disapprove", "recede", "abrogate"]):
                st["skip_not_status_kind"] += 1
                prof["verb_notstatus"][(vm.group(1).lower()[:8] if vm else "-")] += 1
                continue
            r["repo"] = repo
            sel[r["n"]].append(r)
    nodes = sorted(sel)
    print("selected sentences", sum(len(v) for v in sel.values()), "decisions", len(nodes), dict(st), flush=True)
    recs = []
    for i in range(0, len(nodes), 1500):
        T = L.fetch_texts(nodes[i:i + 1500])
        for n in nodes[i:i + 1500]:
            if n not in T:
                st["no_text"] += len(sel[n])
                continue
            reps = {it["id"]: it["repo"] for it in sel[n]}
            for k, rec in RC.build(sel[n], T[n][1]):
                st["rec_" + k] += 1
                if k == "ok":
                    rec["repo"] = reps.get(rec["rid"], "?")
                    recs.append(rec)
        print("texts", min(i + 1500, len(nodes)), "/", len(nodes), "recs", len(recs), flush=True)
    F = L.Facts()
    P = AC.Power(F)
    keys = set()
    for r in recs:
        keys.update(k for k, _a, _b in r["cites"])
        keys.update(k for k, _p in r["ocites"])
    res = AC.resolver(keys)
    pairs = pairs_v3_and_round8()
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
    C = RC.C
    out = open(os.path.join(WORK, "ntcands.jsonl"), "w", encoding="utf-8", newline=NL)
    for r in recs:
        n = r["n"]
        s0, s1 = r["s"]
        w0, wt = r["w"]
        rel0 = s0 - w0
        dec = (int(F.date[n]) // 100000) * 10 if F.date[n] else 0
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
        best = "none"
        if tg:
            best = min(tg.values(), key=lambda v: {"act": 0, "near": 1, "far": 2}[v["where"]])
            best = best["where"] + ":" + best["how"]
        prof["resolution"][best] += 1
        if not near:
            st["no_near_target"] += 1
            continue
        for v in tg.values():
            nm, cite = NM.get(v["t"], ("", ""))
            v["name"], v["cite"], v["date"], v["court"] = nm, cite, int(F.date[v["t"]]), int(F.court[v["t"]])
            v["base"] = pairs.get((n, v["t"]), [])
        if any(v["base"] for v in near):
            # brief: drop items whose (acting, any candidate target) pair already has a row
            st["some_near_has_row"] += 1
            continue
        st["cands"] += 1
        tag = r["tag"].split(">")[-1].split(":")[0]
        st["cand_tag:" + tag] += 1
        prof["cand_repo"][r["repo"]] += 1
        prof["cand_decade"][str(dec)] += 1
        prof["cand_resolution"][best] += 1
        prof["cand_ntargets_near"][str(len(near))] += 1
        vm = VERB_RX.search(r["act"])
        prof["cand_verb"][(vm.group(1).lower()[:8] if vm else "-")] += 1
        rec = {"id": "%d:%d" % (n, s0), "n": n, "s": [s0, s1], "act": r["act"], "part": r["part"], "flags": [],
               "hw": r["hw"], "w0": w0, "pstart": r["pstart"], "wt": wt[max(0, rel0 - 1500):],
               "wt0": w0 + max(0, rel0 - 1500), "by_name": NM.get(n, ("", ""))[0], "by_cite": NM.get(n, ("", ""))[1],
               "by_date": int(F.date[n]), "by_court": int(F.court[n]), "tag": r["tag"], "reason": r["reason"],
               "repo": r["repo"], "decade": dec, "best": best,
               "targets": sorted(tg.values(), key=lambda v: v["hit"][0])}
        out.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + NL)
    out.close()
    json.dump(dict(st), open(os.path.join(WORK, "ntcands_stats.json"), "w"), indent=1)
    json.dump({k: dict(v.most_common()) for k, v in prof.items()}, open(os.path.join(WORK, "profile.json"), "w"),
              indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
