"""fjc11 rule FU2: the uncited district decision under review in a federal court of appeals opinion (port of stlink11's
rule U2, ulink2.py, to CoA review of district courts).

    python -X utf8 fjc11_u2.py capm                         -> work/u2_capm.jsonl (caption pass)
    python -X utf8 fjc11_u2.py run [--procs 8] [--tag u1]   -> work/u2/<shard>.rows.jsonl, rows_<tag>.jsonl, stats

Acting decision D: a regional federal court of appeals opinion (tier A, system 0; the Federal Circuit left to
fedcir11) with no v10d review-kind row on a trial / bankruptcy decision (work/base_by_trial.json), citing (graph) no
district decision of its circuit dated 0..6 years before it that shares a party name with its caption (cap >= 1).
Its judgment line (round 6 decide over the district court's phrases) reverses / vacates / modifies (ulink.finish).
Candidates: district decisions of D's circuit (both circuits known and equal; old Fifth / Eighth as round 6) dated
0..6 years before D whose graph caption is D's caption (cap 2, a distinctive shared token: not institutional, in <=
5,000 titles).
Identity (all required; stlink11 U2 unchanged):
 (c) full party names (ties.names_tie on both texts' front-matter `parties`): every named side of T's caption matched
     in D's caption in full (people by given name + surname, organisations by the whole name); frequent litigants
     (United States, agencies, officials, cities, companies that litigate often ...) never count as the tie;
 (b) T is the latest full-name candidate before D; another full-name candidate on T's date = sibling -> no row; no
     decision of D's court or higher with that caption between T and D (round 6 reviewed_before);
 (d) a second independent tie: T's own docket (T's front matter) printed in D in docket context ("No.", letters, or
     >= 6 characters: ties.docket_tie 'strong'; D's own docket excluded), T's reporter citation printed in D (front
     cites_cases or body), or T's decision date printed in D's opinion.
Anchor (ulink.finish): a sentence of D's own majority naming the district court acting ("the district court held /
granted / dismissed ..."), extended back to the sentence holding a full-name party token of T; no district-reporter
citation inside; round 6's guards; disposition, mixed end zone, rule P, own-disposition, dated otherwise.
Reads the round-6 cache, graph/nodes.tsv, court facts, texts (git), v10d history (base set). No key, no list of cases.
"""
import argparse, collections, gzip, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stlink as S  # noqa: E402
import ulink as U  # noqa: E402
import ties  # noqa: E402
from stlink import BO, L, FL  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "u2")
APP_RX = re.compile(r"^(ca\d+|cadc)(\.\d\d)?$")
# no district-reporter citation inside the anchor (the federal counterpart of stlink's APP_REP)
S.APP_REP = re.compile(r"F\.\s?Supp|F\.\s?R\.\s?D|B\.\s?R\.|Fed\.\s?Cas|WL\s+\d|LEXIS", re.I)
G = {}


def init():
    BO.init()
    B4 = os.path.join(L.C2, "round7", "agents", "b4sc", "work")
    S.G["tokdf"] = json.load(open(os.path.join(B4, "tokdf.json"), encoding="utf-8"))
    S.G["inst"] = set(json.load(open(os.path.join(B4, "inst_tokens.json"), encoding="utf-8")))
    FL.G["tokdf"], FL.G["inst"] = S.G["tokdf"], S.G["inst"]
    S.G["based"] = set(json.load(open(os.path.join(HERE, "work", "base_by_trial.json"))))
    S.G["pairs"] = set()
    cm = {}
    p = os.path.join(HERE, "work", "u2_capm.jsonl")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            d = json.loads(l)
            cm[d["n"]] = [j for j, _g in d["m"]]
    G["capm"] = cm


def circ_same(dc, jc, d_date):
    a, b = BO.G["circ"].get(dc, 0), BO.G["circ"].get(jc, 0)
    if not a or not b or a == 13:
        return False
    return BO.circuit_ok(dc, jc, d_date)


def distinct(t):
    t = t.lower().rstrip("s")
    return t not in S.G["inst"] and S.G["tokdf"].get(t, 0) <= 5000


def app_shards():
    return [p for p in L.shards() if APP_RX.match(os.path.basename(p)[:-len(".jsonl.gz")])]


def capm():
    """caption pass: for every acting CoA opinion (not based), the district decisions of its circuit 0..6 years before
    it with its caption (cap 2)."""
    init()
    F = BO.G["F"]
    acts = {}
    idx = collections.defaultdict(list)
    for p in app_shards():
        for r in L.meta_rows(p[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
            n = int(r[0])
            if n in S.G["based"]:
                continue
            dc, dd = int(F.court[n]), int(F.date[n])
            if F.system(dc) != 0 or not dd or BO.court_at(dc, dd)[1] != "A" or BO.G["circ"].get(dc, 0) in (0, 13):
                continue
            d_all, d_sides = BO.caption(r[7])
            if not d_all:
                d_all, d_sides = BO.caption("", r[8].split(" | ")[:2])
            dt = [t for t in d_all if distinct(t)]
            if not dt:
                continue
            acts[n] = (dc, dd, d_all, d_sides)
            for t in dt:
                idx[t].append(n)
    print("acting opinions", len(acts), flush=True)
    found = collections.defaultdict(list)
    for q in sorted(glob.glob(os.path.join(L.CACHE, "*district*.meta.tsv.gz"))):
        with gzip.open(q, "rt", encoding="utf-8") as f:
            for line in f:
                p = line.rstrip(NL).split("\t")
                j = int(p[0])
                jc, jd = int(F.court[j]), int(F.date[j])
                if not jd:
                    continue
                if BO.tphr(jc, jd)[1] != "trial":
                    continue
                j_all, _ = BO.caption(p[7])
                seen = set()
                for t in j_all:
                    for n in idx.get(t, ()):
                        if n in seen:
                            continue
                        seen.add(n)
                        dc, dd, d_all, d_sides = acts[n]
                        gap = BO.day(dd) - BO.day(jd)
                        if gap < 0 or gap > BO.MAX_GAP_DAYS or not circ_same(dc, jc, dd):
                            continue
                        if BO.cap_rel(d_all, p[7], d_sides) >= 2:
                            found[n].append((j, gap))
    with open(os.path.join(HERE, "work", "u2_capm.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for n, v in found.items():
            f.write(json.dumps({"n": n, "m": v}) + NL)
    print("opinions with a same-caption district decision", len(found), "pairs", sum(len(v) for v in found.values()))


def select(n, g, mrow, st):
    F, N = BO.G["F"], BO.G["N"]
    cands = G["capm"].get(n)
    if not cands:
        return None
    dc = int(F.court[n])
    d_date = int(F.date[n])
    st["op_with_capm"] += 1
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    for cw in g["cw"]:
        j = cw["j"]
        jc = int(F.court[j])
        if BO.tphr(jc, int(F.date[j]))[1] not in ("trial", "bankr"):
            continue
        gap = BO.day(d_date) - BO.day(F.date[j])
        if 0 <= gap <= BO.MAX_GAP_DAYS and BO.circuit_ok(dc, jc, d_date) and \
                BO.cap_rel(d_all, N.name(j), d_sides) >= 1:
            st["drop:cited_samelit"] += 1
            return None
    later_same = 0
    for cw in g["cw"]:
        if cw["rel"] != "lower" and BO.cap_rel(d_all, N.name(cw["j"]), d_sides) >= 2:
            later_same = max(later_same, int(F.date[cw["j"]]))
    d_cname, _t = BO.court_at(dc, d_date)
    d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
    return {"cands": list(cands), "later_same": later_same, "d_all": d_all, "d_sides": d_sides, "d_name": d_name,
            "d_date": d_date}


def identity(n, sel, texts, st):
    F = BO.G["F"]
    D = ties.parse(texts[n][1])
    df = D["front"]
    dfull = "\n".join("%s: %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in df.items() if k != "docket") + \
        "\n" + D["body"]
    full = []
    best = collections.Counter()
    for j in sel["cands"]:
        if j not in texts:
            continue
        Tp = ties.parse(texts[j][1])
        tf = Tp["front"]
        nm, nd = ties.names_tie(df.get("parties"), tf.get("parties"))
        best[nm] += 1
        if nm == "full":
            full.append((int(F.date[j]), j, tf, nd))
    if not full:
        for k in ("mismatch", "surname_only", "frequent_only", "none", "no_parties"):
            if best[k]:
                st["drop:names:" + k] += 1
                return None
        st["drop:names:no_text"] += 1
        return None
    full.sort()
    td, j, tf, nd = full[-1]
    if any(d == td and k != j for d, k, _t, _n in full):
        st["drop:sibling_same_date"] += 1
        return None
    if sel["later_same"] and td <= sel["later_same"] < sel["d_date"]:
        st["drop:reviewed_before"] += 1
        return None
    forms = []
    dk, _tok, _ctx = ties.docket_tie(dfull, df, tf)
    if dk == "strong":
        forms.append("docket")
    ct, _c = ties.cite_tie(dfull, df, L.node_row(j)[5])
    if ct in ("front", "body"):
        forms.append("cite")
    if ties.date_tie(D["body"], tf) == "present":
        forms.append("date")
    if not forms:
        st["drop:no_second_tie"] += 1
        return None
    return j, forms, nd


def run_shard(path):
    if "capm" not in G:
        init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    for n, g in L.decisions(path):
        try:
            sel = select(n, g, meta.get(n), st)
        except Exception as ex:  # noqa: BLE001
            st["error_select"] += 1
            if st["error_select"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        if sel:
            pend.append((n, g, sel))
    F, N = BO.G["F"], BO.G["N"]
    rows = []
    for k in range(0, len(pend), 300):
        chunk = pend[k:k + 300]
        want = set()
        for n, _g, sel in chunk:
            want.add(n)
            want |= set(sel["cands"])
        texts = L.fetch_texts(sorted(want))
        for n, g, sel in chunk:
            r = None
            if n not in texts:
                st["drop:no_text"] += 1
                continue
            try:
                idt = identity(n, sel, texts, st)
                if idt is None:
                    continue
                j, forms, nd = idt
                phrases, cls = BO.tphr(int(F.court[j]), int(F.date[j]))
                if cls != "trial":
                    st["drop:not_trial"] += 1
                    continue
                ph = {p for p in phrases if p not in sel["d_name"]}
                toks = []
                for e in nd.split("|"):
                    if ties.is_frequent(e):
                        continue
                    if ties.is_org(e):
                        ws = [w for w in re.findall(r"[a-z]{3,}", ties.org_key(e)) if w not in S.G["inst"]]
                        ws.sort(key=lambda t: S.G["tokdf"].get(t.rstrip("s"), 0))
                        if ws:
                            toks = [ws[0]]
                            break
                    else:
                        sur = ties.person_key(e)[1]
                        if sur and len(sur) >= 3 and re.fullmatch(r"[a-z]+", sur):
                            toks = [sur]
                            break
                if not toks:
                    st["drop:no_name_token"] += 1
                    continue
                st["identified"] += 1
                st["ident_forms:" + "+".join(forms)] += 1
                gap = BO.day(sel["d_date"]) - BO.day(F.date[j])
                r = U.finish(n, g, L.norm(texts[n][1]), (j, ph, cls, toks, gap), st)
            except Exception as ex:  # noqa: BLE001
                st["error_finish"] += 1
                if st["error_finish"] <= 3:
                    sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
                continue
            if r:
                r["rule"] = "below:fjc11_u2"
                r["note"] = r["note"].replace("|L|stlink10 u uncited", "|A|fjc11 u2 " + "+".join(forms))
                st["rows_tie:" + "+".join(forms)] += 1
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
    ap.add_argument("--tag", default="u1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    if a.cmd == "capm":
        capm()
        return
    paths = app_shards()
    paths.sort(key=os.path.getsize, reverse=True)
    for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
        print(tag, k, flush=True)
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
