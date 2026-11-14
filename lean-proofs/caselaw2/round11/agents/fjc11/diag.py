"""fjc8: where does the pipeline lose a (district decision, appellate opinion) pair?

    python -X utf8 diag.py trace PAIRS.tsv OUT.tsv      PAIRS: district<TAB>appellate[<TAB>extra...] (header ok)

For each pair: is the appellate opinion in the round-6 cache; its cw records of the district node; the round-6
below_other selection traced for that target (first failing step); the round-6 linker's row if any; base history
rows (round8/stage/v8e) targeting the district node, with their Lean verdict (round8/out/v8e/certs.tsv).
Reads no answer key: the pairs come from the h0 per-case outcome file of the base build (case identity only).
"""
import collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BO_DIR = os.path.join(C2, "round6", "history", "rules", "below_other")
sys.path.insert(0, BO_DIR)
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402
import link as BO  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")
APP_RX = re.compile(r"^(ca\d+|cadc|cafc)(\.\d\d)?$")


def shard_index():
    p = os.path.join(WORK, "app_shards.json")
    if os.path.exists(p):
        return {int(k): v for k, v in json.load(open(p)).items()}
    idx = {}
    for s in L.shards():
        tag = os.path.basename(s)[:-len(".jsonl.gz")]
        if not APP_RX.match(tag):
            continue
        for r in L.meta_rows(s[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
            idx[int(r[0])] = tag
    os.makedirs(WORK, exist_ok=True)
    json.dump({str(k): v for k, v in idx.items()}, open(p, "w"))
    return idx


def base_history():
    by_t = collections.defaultdict(list)
    with open(os.path.join(C2, "round8", "stage", "v8e", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 13:
                continue
            try:
                by_t[int(p[1])].append((p[0], int(p[2]), p[4], p[5], p[12]))
            except ValueError:
                continue
    return by_t


def verdicts():
    v = {}
    with open(os.path.join(C2, "round8", "out", "v8e", "certs.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[0] == "history":
                v[p[1]] = p[2]
    return v


def trace_one(n, g, mrow, j, st):
    """First failing step of the round-6 below_other selection for target j in acting decision n."""
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier not in ("L", "A", "B", "D"):
        return "acting_tier_" + d_tier, {}
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
    cws = [c for c in g["cw"] if c["j"] == j]
    info = {"ncw": len(cws), "ncw_all": len(g["cw"])}
    if not cws:
        return "no_cw", info
    reasons = []
    for cw in cws:
        jc = int(F.court[j])
        jt = BO.court_at(jc, int(F.date[j]))[1]
        if cw["rel"] != "lower" and not (cw["rel"] == "peer" and jt in ("B", "D") and d_tier == "A"):
            reasons.append("rel_" + cw["rel"])
            continue
        phrases, cls = BO.tphr(jc, int(F.date[j]))
        if cls in ("app", "bap") and d_tier != "L" and not (jt in ("B", "D") and d_tier == "A"):
            cls = None
        if cls is None:
            reasons.append("target_not_reviewed")
            continue
        if F.system(dc) == 0 and not BO.circuit_ok(dc, jc, d_date):
            reasons.append("other_circuit")
            continue
        cap = BO.cap_rel(d_all, N.name(j), d_sides)
        info["cap"] = max(info.get("cap", -1), cap)
        ok, why, anchor, apart = BO.eval_candidate(cw, cap, phrases, True)
        info.setdefault("part", cw["part"])
        if not ok:
            reasons.append("cand_" + why)
            continue
        if why in ("bare", "subnom"):
            reasons.append("cand_one_side_caption")
            continue
        gap = BO.day(d_date) - BO.day(F.date[j])
        if gap < 0 or gap > BO.MAX_GAP_DAYS:
            reasons.append("window")
            continue
        reasons.append("ok:" + why)
    info["reasons"] = reasons
    if not any(r.startswith("ok:") for r in reasons):
        # the most advanced failure
        order = ["window", "cand_one_side_caption", "cand_later_events", "cand_earlier_proceeding",
                 "cand_interlocutory_ruling", "cand_no_design_cue", "cand_no_court_phrase", "cand_named_other_case",
                 "cand_bare_no_caption", "cand_signal", "cand_history_before_cite", "cand_history_after_cite",
                 "cand_bracket_see", "cand_part", "cand_span", "other_circuit", "target_not_reviewed"]
        for o in order:
            if o in reasons:
                return o, info
        return reasons[0], info
    # full process() for the after-selection steps
    stc = collections.Counter()
    rows = BO.process(n, g, mrow, stc, None)
    mine = [r for r in rows if r["target"] == j]
    info["rows"] = [(r["kind"], r["scope"], r["rule"]) for r in mine]
    if mine:
        return "row", info
    drops = [k for k in stc if k.startswith("drop:")]
    info["drops"] = drops
    return ("after_" + (drops[0][5:] if len(drops) == 1 else "+".join(sorted(d[5:] for d in drops)))) if drops else \
        "after_unknown", info


def run_trace(pairs_path, out_path):
    pairs = []
    with open(pairs_path, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            try:
                pairs.append((int(p[0]), int(p[1]), p[2:]))
            except ValueError:
                continue
    sidx = shard_index()
    BO.init()
    hist = base_history()
    ver = verdicts()
    by_shard = collections.defaultdict(list)
    for d, a, ex in pairs:
        by_shard[sidx.get(a, "-")].append((d, a, ex))
    out = []
    st = collections.Counter()
    for tag, items in sorted(by_shard.items()):
        want = {a for _, a, _ in items}
        groups, meta = {}, {}
        if tag != "-":
            path = os.path.join(L.CACHE, tag + ".jsonl.gz")
            for r in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
                if int(r[0]) in want:
                    meta[int(r[0])] = r
            for n, g in L.decisions(path):
                if n in want:
                    groups[n] = g
        for d, a, ex in items:
            if tag == "-":
                stage, info = "app_not_in_app_shards", {}
            elif a not in groups:
                stage, info = "app_no_cache_record", {}
            elif not groups[a]["cw"]:
                stage, info = "app_no_cw_at_all", {}
            else:
                stage, info = trace_one(a, groups[a], meta.get(a), d, st)
            hs = hist.get(d, [])
            hrow = ";".join("%s|%s|%s|%s|%s|%s" % (h[0], h[1], h[2], h[3], h[4], ver.get(h[0], "?")) for h in hs)
            same = [h for h in hs if h[1] == a]
            out.append([d, a, stage, json.dumps(info, ensure_ascii=False), len(hs), len(same), hrow] + ex)
    with open(out_path, "w", encoding="utf-8", newline=NL) as f:
        f.write("district\tappellate\tstage\tinfo\tn_hist\tn_hist_by_app\thist\textra\n")
        for r in out:
            f.write("\t".join(str(x) for x in r) + NL)
    c = collections.Counter(r[2] for r in out)
    for k, v in c.most_common():
        print(v, k)


if __name__ == "__main__":
    if sys.argv[1] == "trace":
        run_trace(sys.argv[2], sys.argv[3])
