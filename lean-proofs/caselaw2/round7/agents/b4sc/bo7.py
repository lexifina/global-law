"""b4sc (B4 e) for reviewing courts other than the Supreme Court: shared reporter pages re-pointed.

    python -X utf8 bo7.py keys  [--procs 22]   -> work/bo_multi.json   cache citation keys several decisions carry
    python -X utf8 bo7.py run   [--procs 22]   -> work/bo_rows_raw.jsonl, work/bo_stats.json
    python -X utf8 bo7.py ev                   -> rows_e_other.jsonl (name: evidence in an anchor quote)

Rule (general; round 6's below_other linker `rules/below_other/link.py` imported, not edited):
  A citation of the acting decision D (a `cw` record of the round-6 cache) whose key graph/nodes.tsv gives to two or
  more decisions (one reporter page printing several decisions) is re-pointed to the one holder whose caption D's
  caption picks out (round 6's `cap_rel` = 2, the test of `shared_cite.py`) when exactly one holder does and it is not
  the index node (round 6 dropped these rows). The re-pointed record (court relation recomputed for the new holder:
  same system, lower rank -> "lower") then goes through round 6's whole selection (`link.process`, unchanged: court
  relation, window, caption, signals, earlier-proceeding marks, one decision per court, disposition). Only rows whose
  target is a re-pointed holder are kept (the rest are round 6's own rows).
  Evidence: the compact `cite:` key resolves to another node in the index, so the row carries `name:` evidence = the
  holder's caption tokens that D's caption shares (round 6 caption tokens, >= 3 characters), inside an anchor quote
  that holds them, an anchor cue, and no anchor disqualifier: the round-6 anchor sentence, extended back by up to
  ten sentences (<= 2,500 characters) in the same part, or D's own head-matter caption lines (<= 700 characters).
No answer key is read.
"""
import argparse, collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
R6 = os.path.join(C2, "round6", "history")
BO = os.path.join(R6, "rules", "below_other")
sys.path.insert(0, BO)
sys.path.insert(0, R6)
import link as K  # noqa: E402
import certify6 as C6  # noqa: E402

L = K.L
C = K.C
NL = chr(10)
WORK = os.path.join(HERE, "work")
GG = {}
MAX_BACK = 10        # sentences the anchor may be extended back (same part) to reach the caption tokens
MAX_ANCHOR = 2500    # characters
SIDE_PROC = re.compile(r"\bmandamus\b|\bprohibition\b", re.I)   # a side proceeding (writ to the court below)


def shard_paths():
    return [p for p in L.shards() if not os.path.basename(p).startswith("supreme-court.")]


def work_keys(path):
    ks = set()
    for n, g in L.decisions(path):
        for cw in g["cw"]:
            ks.add(cw["key"])
    return ks


def keys(procs):
    ks = set()
    for s in L.pmap(work_keys, shard_paths(), procs=procs):
        ks |= s
    print("cw keys", len(ks), flush=True)
    holders = collections.defaultdict(set)
    with open(L.NODES, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7 or not p[5]:
                continue
            for c in p[5].split("|"):
                k = C.norm_cite(c.replace("(", "").replace(")", ""))
                if k in ks:
                    holders[k].add(int(p[0]))
    multi = {k: sorted(v) for k, v in holders.items() if len(v) > 1}
    json.dump(multi, open(os.path.join(WORK, "bo_multi.json"), "w", encoding="utf-8"))
    print("keys carried by several decisions", len(multi))


def init():
    K.init()
    GG["multi"] = json.load(open(os.path.join(WORK, "bo_multi.json"), encoding="utf-8"))


def work_run(path):
    if "multi" not in GG:
        init()
    F, N = K.G["F"], K.G["N"]
    multi = GG["multi"]
    st = collections.Counter()
    out = []
    meta = {}
    for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
        meta[int(p[0])] = p
    for n, g in L.decisions(path):
        if not g["cw"] or not any(cw["key"] in multi for cw in g["cw"]):
            continue
        dc = int(F.court[n])
        d_sys, d_rank = F.system(dc), F.rank(dc)
        d_all, d_sides = K.caption(N.name(n))
        new = []
        rp = {}
        for cw in g["cw"]:
            hs = multi.get(cw["key"])
            if not hs:
                new.append(cw)
                continue
            st["cw_shared"] += 1
            good = [h for h in hs if h != n and K.cap_rel(d_all, N.name(h), d_sides) >= 2]
            if good == [cw["j"]] or len(good) != 1:
                new.append(cw)
                st["cw_shared_kept" if good == [cw["j"]] else "cw_shared_undecided"] += 1
                continue
            x = good[0]
            xc = int(F.court[x])
            xd = int(F.date[x])
            dd = int(F.date[n])
            if F.system(xc) != d_sys or not xd or xd > dd or dd - xd > 100000:
                st["cw_shared_repoint_out_of_scope"] += 1
                new.append(cw)
                continue
            rel = "same" if xc == dc else ("lower" if F.rank(xc) < d_rank else "peer")
            new.append(dict(cw, j=x, rel=rel))
            rp[x] = cw["j"]
            st["cw_repointed"] += 1
        if not rp:
            continue
        st["decisions_with_repoint"] += 1
        g2 = dict(g, cw=new)
        try:
            rows = K.process(n, g2, meta.get(n), collections.Counter(), None)
        except Exception as ex:
            st["error"] += 1
            continue
        for r in rows:
            if r["target"] in rp:
                r["_from"] = rp[r["target"]]
                out.append(r)
                st["rows_repointed"] += 1
    return out, st


def run(procs):
    rows, st = [], collections.Counter()
    import multiprocessing as mp
    with mp.Pool(procs, initializer=init) as pool:
        for o, s in pool.imap_unordered(work_run, shard_paths(), chunksize=1):
            rows.extend(o)
            st.update(s)
    rows.sort(key=lambda r: (r["by"], r["target"]))
    with open(os.path.join(WORK, "bo_rows_raw.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    json.dump(st, open(os.path.join(WORK, "bo_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


def lower(s):
    return C6.lower(s)


def ev(procs):
    K.init()
    N = K.G["N"]
    cue = json.load(open(C6.CUE_JSON, encoding="utf-8"))
    cues = [c for c in cue["anchor"] if c]
    disq = [c for c in cue["disqualify_anchor"] if c]
    rows = [json.loads(x) for x in open(os.path.join(WORK, "bo_rows_raw.jsonl"), encoding="utf-8")]
    T = L.fetch_texts({r["by"] for r in rows})
    st = collections.Counter()
    out = []
    for r in rows:
        text = T[r["by"]][1]
        d_all, _ = K.caption(N.name(r["by"]))
        j_all, _ = K.caption(N.name(r["target"]))
        toks = sorted({C6.compact(t) for t in (j_all & d_all) if len(C6.compact(t)) >= 3})
        if not toks:
            st["drop:no_tokens"] += 1
            continue

        def ok(a0, a1):
            q = L.norm(text[a0:a1])
            ql = lower(q)
            if not any(c in ql for c in cues) or any(c in ql for c in disq):
                return None
            w = C6.words(q)
            pres = [t for t in toks if (" " + t + " ") in w]
            return pres or None
        body0 = 0
        if text.startswith("---"):
            e = text.find(NL + "---", 3)
            body0 = text.find(NL, e + 4) + 1
        pm, _ = (C.part_map2(text) if C.hard_wrapped(text, body0) else C.part_map(text))

        def part_at(x):
            for a, b, p, _s in pm:
                if a <= x < b:
                    return p.rstrip("~")
            return None
        cand = []
        if r["anchor"] is not None:
            a0, a1 = r["anchor"]
            part = r["anchor_part"]
        else:
            # plain row: the citation is within 400 characters of the disposition; anchor = the citation's sentence
            key = C6.compact(r["ev"][5:])
            pos = None
            for m in C.CITE_RX.finditer(text, max(body0, r["disp"][0] - 400), min(len(text), r["disp"][1] + 400)):
                if C6.compact(m.group(0)) and key in C6.compact(text[m.start():m.end() + 2]):
                    pos = m.start()
                    break
            if pos is None:
                st["drop:plain_cite_not_found"] += 1
                continue
            a0, a1 = C.sentence_span(text, pos, pos + 1)
            part = r["part"]
        if SIDE_PROC.search(text[a0:a1]):
            st["drop:side_proceeding"] += 1
            continue
        cand.append((a0, a1, part))
        lo = next((a for a, b, p, _s in pm if a <= a0 < b), body0)
        b0 = a0
        for _ in range(MAX_BACK):
            p = b0 - 1
            while p > lo and text[p] in " \n":
                p -= 1
            if p <= lo:
                break
            s0, _s1 = C.sentence_span(text, p, p + 1)
            s0 = max(s0, lo)
            if a1 - s0 > MAX_ANCHOR:
                break
            b0 = s0
            cand.append((b0, a1, part))
        for a, b, p, _s in pm:
            if p not in ("headmatter", "headmatter~"):
                continue
            pos = a
            lines = []
            for ln in text[a:b].split(NL):
                lines.append((pos, pos + len(ln), ln))
                pos += len(ln) + 1
            for i, (l0, l1, ln) in enumerate(lines):
                if ln.strip() and any((" " + t + " ") in C6.words(ln) for t in toks):
                    for k in range(i, min(len(lines), i + 8)):
                        if lines[k][1] - l0 > 700:
                            break
                        cand.append((l0, lines[k][1], "headmatter"))
                    break
            break
        done = False
        for a0, a1, part in cand:
            while a0 < a1 and text[a0] in " \n\t":
                a0 += 1
            while a1 > a0 and text[a1 - 1] in " \n\t":
                a1 -= 1
            if a1 <= a0 or part not in ("majority", "perCuriam", "plurality", "headmatter"):
                continue
            # the anchor lies inside one part of that label (never the front matter or the title line)
            if a0 < body0 or part_at(a0) != part or part_at(a1 - 1) != part:
                st["cand_part_mismatch"] += 1
                continue
            pres = ok(a0, a1)
            if pres:
                x = {k: v for k, v in r.items() if not k.startswith("_")}
                x["anchor"] = [a0, a1]
                x["anchor_part"] = part
                x["ev"] = "name:" + " ".join(pres)
                x["rule"] = "below:o7_rp_" + r["rule"].split(":")[1]
                x["table"] = "history"
                x["claim"] = "-"
                x["note"] = (x.get("note") or "") + "|b4sc shared page: index node %d" % r["_from"]
                out.append(x)
                st["kept"] += 1
                st["kept:" + x["rule"]] += 1
                st["kept:%s/%s" % (x["kind"], x["scope"])] += 1
                done = True
                break
        if not done:
            st["drop:no_anchor_with_tokens"] += 1
    with open(os.path.join(HERE, "rows_e_other.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + NL)
    json.dump(st, open(os.path.join(WORK, "bo_ev_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=22)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    {"keys": keys, "run": run, "ev": ev}[a.cmd](a.procs)


if __name__ == "__main__":
    main()
