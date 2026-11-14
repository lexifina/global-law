"""enbanc12 (round 12): population of panel decisions later reheard en banc by the same court, and their v11d status.

    python -X utf8 pop12.py index [--procs 8]   -> work/eb_docket.json  (same-docket earlier nodes of every en banc E)
    python -X utf8 pop12.py texts [--procs 8]   -> work/eb_feats.jsonl  (E's citations of earlier same-court same-name
                                                   nodes, E statement features, candidate texts' order / en banc forms)
    python -X utf8 pop12.py pop                 -> work/pop.tsv, work/pop_stats.json

Population: E = every en banc / limited en banc decision of the base (round11/stage/v11d decisions2 bench). P = an
earlier decision of the same court (<= 5 years before E) that shares a docket number with E or that E cites with the
same case-name tokens, that is not itself en banc, and whose text is not an order about rehearing (O). Per E the P is
the latest such opinion. O = an earlier same-court node of the same docket / cited whose own text is an order granting
rehearing en banc. Corpus text only; no answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "rehear"))
import r6lib as L  # noqa: E402
import rehear_link as RL  # noqa: E402

C = L.reader_common()
NL = chr(10)
WORK = os.path.join(HERE, "work")
BASE = os.path.join(C2, "round11", "stage", "v11d")
OUT = os.path.join(C2, "round11", "out", "v11d")
CITE_INDEX = os.path.join(L.W, "graph", "cite_index.tsv")
GAP = 50000  # 5 years in yyyymmdd arithmetic

EB = r"(?:en\s+banc|in\s+banc)"
REH = r"(?:rehearing|reh['’]?g\.?|reconsideration)"
# an order granting rehearing en banc (own words)
O_GRANT = re.compile(r"\b(?:rehearing|reh['’]?g\.?)\s+" + EB + r"[^.]{0,60}?\b(?:is|be|are|was|shall\s+be)\s+(?:hereby\s+)?granted|"
                     r"\bgrant(?:ed|s)?\s+(?:the\s+)?(?:\w+\s+){0,3}(?:petition|petitions|suggestion|motion|request)s?[^.]{0,60}?"
                     r"(?:rehearing|reh['’]?g\.?)\s+" + EB + r"|\bordered\s+that\s+(?:this\s+)?(?:case|cause|appeal|matter)s?[^.]{0,60}?"
                     r"\b(?:be\s+)?(?:reheard|heard|argued|reargued)\s+(?:by\s+the\s+(?:court|full\s+court)\s+)?" + EB +
                     r"|\b(?:will|shall)\s+be\s+(?:reheard|heard|reargued)\s+" + EB + r"|\bmajority\s+of\s+the\s+"
                     r"(?:\w+\s+){0,3}judges[^.]{0,120}?\bvoted\b[^.]{0,40}?\b(?:rehear|hear|en\s+banc)", re.I)
O_DENY = re.compile(r"\b(?:rehearing|reh['’]?g\.?)[^.]{0,60}?\b(?:is|are|be)\s+(?:hereby\s+)?denied|"
                    r"\bden(?:y|ied|ying)\s+(?:the\s+)?(?:\w+\s+){0,3}(?:petition|suggestion|motion)", re.I)
# the order's own words vacate the panel opinion / judgment
O_VAC = re.compile(r"\b(?:panel|previous|prior|earlier|original)\s+(?:\w+\s+){0,2}?(?:opinion|decision|judgment|"
                   r"opinions)s?\b[^.]{0,160}?\b(?:is|are|be|shall\s+be|were|was|stand)\s+(?:hereby\s+)?vacated|"
                   r"\bvacat(?:e|es|ed|ing)\s+(?:the|our|its)\s+(?:\w+\s+){0,2}?panel(?:['’]s)?\s+(?:opinion|decision|judgment)"
                   r"|\b(?:opinion|judgment|decision)s?\s+(?:of|issued\s+by|filed\s+by)\s+the\s+panel[^.]{0,120}?\b(?:is|are|be)\s+"
                   r"(?:hereby\s+)?vacated", re.I)
# E's own statement that the panel opinion was vacated / superseded / withdrawn
E_VAC = re.compile(r"\bvacat(?:ed|ing|e)\s+(?:the|our|its|that|a)\s+(?:\w+\s+){0,3}?(?:panel|prior|previous|earlier|original)"
                   r"(?:['’]s)?\s+(?:\w+\s+){0,2}?(?:opinion|decision|judgment|opinions)|"
                   r"\b(?:panel|prior|previous|earlier|original)(?:['’]s)?\s+(?:\w+\s+){0,2}?(?:opinion|decision|judgment)s?"
                   r"(?:\s*\([^)]{0,80}\))?[^.;]{0,120}?\b(?:was|were|is|are|been|being|be|stands|stand)\s+(?:hereby\s+|thereby\s+|"
                   r"thus\s+|therefore\s+|accordingly\s+|subsequently\s+|later\s+|then\s+)?(?:vacated|withdrawn|superseded|"
                   r"set\s+aside)|\bvacated\s+(?:on|upon|by)\s+(?:the\s+)?grant\s+of\s+(?:rehearing|reh['’]?g\.?)\s+" + EB +
                   r"|\bvacated[^;]{0,30}?(?:rehearing|reh['’]?g\.?)\s+" + EB + r"\s+granted|"
                   r"(?:rehearing|reh['’]?g\.?)\s+" + EB + r"\s+granted[^;]{0,20}?(?:opinion|judgment)\s+vacated", re.I)
E_ADOPT = re.compile(r"\breinstat(?:e|es|ed|ing)\s+(?:the\s+|our\s+)?(?:\w+\s+){0,3}?(?:panel|original|prior)|"
                     r"\badopt(?:s|ed|ing)?\s+(?:the\s+)?(?:\w+\s+){0,3}?panel(?:['’]s)?\s+(?:\w+\s+){0,2}?(?:opinion|decision)|"
                     r"\bfor\s+the\s+reasons\s+(?:set\s+forth|stated|given)\s+in\s+the\s+(?:\w+\s+){0,2}?(?:panel|original)|"
                     r"\bpanel\s+(?:opinion|decision)\s+is\s+(?:hereby\s+)?reinstated", re.I)
E_REH = re.compile(r"(?:rehearing|reh['’]?g\.?)\s+" + EB, re.I)


def body_start(t):
    e = t.find(NL + "---", 3)
    return e + 4 if t.startswith("---") and e > 0 else 0


def load_eb():
    eb = {}
    with open(os.path.join(BASE, "decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 6)
            if p[4] in ("enBanc", "limitedEnBanc"):
                eb[int(p[0])] = p[4]
    return eb


def _meta(args):
    path, ebset = args
    out = []
    for r in L.meta_rows(path):
        n = int(r[0])
        ds = sorted(RL.dockets(r[5]))
        if not ds:
            continue
        out.append((n, int(r[3]), int(r[4]), ds, r[7], int(r[2] or 0), n in ebset))
    return out


def index(a):
    eb = load_eb()
    ebset = set(eb)
    rows = []
    for res in L.pmap(_meta, [(p, ebset) for p in L.shards(".meta.tsv.gz")], procs=a.procs):
        rows.extend(res)
    print("meta rows with dockets", len(rows), flush=True)
    want = set()
    info = {}
    for n, d, c, ds, title, ln, ise in rows:
        if ise:
            for k in ds:
                want.add((c, k))
    idx = collections.defaultdict(list)
    for n, d, c, ds, title, ln, ise in rows:
        keep = [k for k in ds if (c, k) in want]
        if keep:
            info[n] = (d, c, ds, title, ln)
            for k in keep:
                idx[(c, k)].append(n)
    out = {}
    for e in eb:
        if e not in info:
            continue
        d, c, ds, _t, _l = info[e]
        sd = set()
        for k in ds:
            for m in idx.get((c, k), ()):
                if m != e and info[m][0] < d and info[m][0] >= d - GAP:
                    sd.add(m)
        out[e] = sorted(sd)
    json.dump({"same_docket": {str(k): v for k, v in out.items()},
               "info": {str(k): v for k, v in info.items()}}, open(os.path.join(WORK, "eb_docket.json"), "w"))
    print("en banc with docket", len(out), "with an earlier same-docket node", sum(1 for v in out.values() if v))


def feats_texts(nodes):
    tx = L.fetch_texts(nodes)
    out = {}
    for n in nodes:
        if n not in tx:
            continue
        t0 = tx[n][1]
        lo = body_start(t0)
        t = L.norm(t0)
        b = t[lo:]
        out[n] = {"len": len(b), "grant": bool(O_GRANT.search(b)), "deny": bool(O_DENY.search(b[:3000])),
                  "ovac": bool(O_VAC.search(b)), "head_eb": bool(re.search(EB, t[:lo + 1500], re.I)),
                  "ovac_q": (O_VAC.search(b).group(0)[:200] if O_VAC.search(b) else "")}
    return out


def e_work(args):
    nodes, = args
    tx = L.fetch_texts(nodes)
    out = []
    for d in nodes:
        if d not in tx:
            continue
        t0 = tx[d][1]
        lo = body_start(t0)
        t = L.norm(t0)
        pm = C.part_map2(t0)
        pm = pm[0] if isinstance(pm, tuple) else pm
        cites = []
        for m in C.CITE_RX.finditer(t, lo):
            k = C.cite_key(m)
            if k:
                cites.append((k, m.start()))
        stm = []
        for m in E_VAC.finditer(t, lo):
            part = C.part_at(pm, m.start())[0].rstrip("~")
            stm.append((m.start(), part, t[max(lo, m.start() - 150):m.end() + 150]))
        ad = []
        for m in E_ADOPT.finditer(t, lo):
            part = C.part_at(pm, m.start())[0].rstrip("~")
            ad.append((m.start(), part, t[max(lo, m.start() - 120):m.end() + 120]))
        out.append({"d": d, "cites": cites, "vac": stm, "adopt": ad, "reh": len(E_REH.findall(t, lo)),
                    "len": len(t) - lo})
    return out


def texts(a):
    eb = load_eb()
    nodes = sorted(eb)
    res_all = []
    for res in L.pmap(e_work, [(nodes[i:i + 60],) for i in range(0, len(nodes), 60)], procs=a.procs):
        res_all.extend(res)
    print("E texts", len(res_all), flush=True)
    keys = {k for r in res_all for k, _ in r["cites"]}
    k2n = collections.defaultdict(set)
    with open(CITE_INDEX, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 2 and p[0] in keys:
                k2n[p[0]].add(int(p[1]))
    F = L.Facts()
    dk = json.load(open(os.path.join(WORK, "eb_docket.json")))
    cand = set()
    for r in res_all:
        d = r["d"]
        cd, dd = int(F.court[d]), int(F.date[d])
        nd = set(C.name_tokens(L.node_row(d)[6]))
        cc = {}
        for k, pos in r["cites"]:
            ns = k2n.get(k, set())
            if len(ns) != 1:
                continue
            m = next(iter(ns))
            if m == d or int(F.court[m]) != cd or not (dd - GAP <= int(F.date[m]) < dd):
                continue
            nt = set(C.name_tokens(L.node_row(m)[6]))
            if not nt or not (nt & nd) or len(nt & nd) < min(len(nt), len(nd), 2):
                continue
            cc.setdefault(str(m), []).append([k, pos])
        r["cited_same"] = cc
        cand.update(int(x) for x in cc)
        cand.update(dk["same_docket"].get(str(d), []))
        del r["cites"]
    cand = sorted(cand)
    print("candidate targets", len(cand), flush=True)
    tf = {}
    for res in L.pmap(feats_texts, [cand[i:i + 80] for i in range(0, len(cand), 80)], procs=a.procs):
        tf.update(res)
    with open(os.path.join(WORK, "eb_feats.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in res_all:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    json.dump({str(k): v for k, v in tf.items()}, open(os.path.join(WORK, "tgt_feats.json"), "w"))
    print("done", len(tf))


def is_order(f):
    return f["len"] < 6000 and (f["grant"] or f["deny"] or f["ovac"])


def load_v11d(targets):
    hist = collections.defaultdict(list)
    verdict = {}
    with open(os.path.join(OUT, "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split(chr(9))
            if q[0] == "history":
                verdict[q[1]] = q[2]
    with open(os.path.join(BASE, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split(chr(9))
            t = int(q[1])
            if t in targets:
                hist[t].append((int(q[2]), q[4], q[5], q[-1], verdict.get(q[0], "?")))
    st = {}
    with open(os.path.join(OUT, "status.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            q = line.split(chr(9), 7)
            n = int(q[0])
            if n in targets and q[1] == "-" and q[2] == "-":
                st.setdefault(n, []).append((int(q[3]), int(q[4]), q[5], q[6]))
    return hist, st


def pop(a):
    eb = load_eb()
    dk = json.load(open(os.path.join(WORK, "eb_docket.json")))
    tf = json.load(open(os.path.join(WORK, "tgt_feats.json")))
    F = L.Facts()
    E = {}
    with open(os.path.join(WORK, "eb_feats.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            E[r["d"]] = r
    pairs = []
    for d, r in E.items():
        sd = set(dk["same_docket"].get(str(d), []))
        cs = {int(k) for k in r["cited_same"]}
        cand = sd | cs
        ops, ords = [], []
        for m in cand:
            if m in eb:
                continue
            ft = tf.get(str(m))
            if ft is None:
                continue
            if is_order(ft):
                ords.append(m)
            else:  # (head-matter en banc words are not used: a panel opinion carries its later history there)
                ops.append(m)
        if not ops:
            continue
        ops.sort(key=lambda m: (int(F.date[m]), m))
        # the panel opinion: latest opinion of the same docket if any, else the latest cited one
        sdo = [m for m in ops if m in sd]
        p = sdo[-1] if sdo else ops[-1]
        how = ("docket+cite" if (p in sd and p in cs) else "docket" if p in sd else "cite")
        pairs.append((p, d, how, sorted(ords), len(ops)))
    targets = {p for p, *_ in pairs} | {o for *_, os_, _ in pairs for o in os_}
    hist, st = load_v11d(targets)
    NEGK = {"vacated", "withdrawn", "reversed", "substitutedBy", "rehearingEnBancGranted"}
    stats = collections.Counter()
    by_p = collections.defaultdict(list)
    for p, d, how, ords, nops in pairs:
        by_p[p].append((d, how, ords, nops))
    with open(os.path.join(WORK, "pop.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("\t".join(("P", "E", "court", "Pdate", "Edate", "how", "final_status", "P_rows", "E_row", "orders",
                           "O_rows", "O_vac", "E_vac_main", "E_adopt_main", "cat")) + NL)
        for p, lst in sorted(by_p.items()):
            lst.sort(key=lambda x: int(F.date[x[0]]))
            d, how, ords, nops = lst[0]
            fin = sorted(st.get(p, []))
            final = fin[-1][2] if fin else "nostatus"
            anyneg = any(s[2].startswith("neg:") for s in fin)
            rows = hist.get(p, [])
            prow = ";".join("%d:%s:%s:%s" % (b, k, sc, v) for b, k, sc, _r, v in rows)
            erow = [x for x in rows if x[0] in {y[0] for y in lst}]
            orow = [x for x in rows if x[0] in ords]
            ovac = [o for o in ords if tf[str(o)]["ovac"] and tf[str(o)]["grant"]]
            r = E[d]
            vmain = [v for v in r["vac"] if v[1] in ("majority", "perCuriam", "plurality")]
            amain = [v for v in r["adopt"] if v[1] in ("majority", "perCuriam", "plurality")]
            if anyneg:
                cat = "neg"
            elif final.startswith("unknown"):
                cat = "unknown"
            elif amain:
                cat = "good_E_adopts"
            elif ovac:
                cat = "good_O_vacates"
            elif ords:
                cat = "good_O_grant_only"
            elif vmain:
                cat = "good_E_states"
            else:
                cat = "good_no_statement"
            stats[cat] += 1
            stats["how_" + how] += 1
            f.write(chr(9).join(str(x) for x in (p, d, int(F.court[d]), int(F.date[p]), int(F.date[d]), how, final, prow,
                                                 len(erow), ",".join(map(str, ords)), len(orow), ",".join(map(str, ovac)),
                                                 len(vmain), len(amain), cat)) + NL)
    json.dump(dict(stats), open(os.path.join(WORK, "pop_stats.json"), "w"), indent=1)
    print(dict(stats))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    if a.cmd == "index":
        index(a)
    elif a.cmd == "texts":
        texts(a)
    elif a.cmd == "pop":
        pop(a)


if __name__ == "__main__":
    main()
