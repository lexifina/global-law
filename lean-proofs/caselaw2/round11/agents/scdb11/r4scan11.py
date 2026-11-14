"""scdb11 rule R4 (round 11 follow-up; other-court other-target block): a higher court's refusal to review is not the
judgment under review.

    python -X utf8 r4scan11.py run [--procs 8] [--tag x]  -> work/r4_rows<tag>.jsonl, work/r4_remove<tag>.txt,
                                                            work/r4_pairs<tag>.tsv, work/r4_stats<tag>.json

Same machinery as r1scan11.py (R1), with two changes:
  1. The Supreme Court's own text reports T' as a refusal of discretionary review: at every citation of T' in the
     Court's text, the clause the citation closes (or a parenthetical after it) holds a refusal phrase ("The State
     Supreme Court denied certiorari, 246 Ala. 539", "denied review", "denied leave to appeal", "denied the petition
     for review / for a writ of certiorari / for allowance of appeal", "declined to review", "refused the writ",
     "writ refused", "review denied", "certiorari denied", "leave to appeal denied", "dismissed the appeal / petition"
     is NOT included), with no later judicial act verb between the phrase and the citation.
  2. T = a decision of a LOWER court of the same court system as T' (courts2 system and tier rank), decided on or
     before T' and at most 2 years earlier, cited by the Court at some place that is not itself a refusal citation,
     and cited by T' or bearing the same case-name tokens; when several, the latest.
Then: new history row by the Supreme Court opinion on T (same kind, scope, disposition quote as the row on T'),
anchored at a sentence citing T; the row on T' is listed for removal. No answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

C = L.reader_common()
NL = chr(10)
WORK = os.path.join(HERE, "work")
BASE = os.path.join(C2, "round10", "stage", "v10d")
DIAG = os.path.join(C2, "round10", "agents", "scdb10", "work", "diag10_v5.jsonl.gz")
REVIEW = ("reversed", "vacated", "affirmed", "modified", "reviewDismissed")
MAX_GAP = 20000  # yyyymmdd difference: 2 years

REH = r"(?:rehear\w*|reh['’]?g\.?)"
RV = r"(?:certiorari|cert\.|review|leave\s+to\s+appeal|allowance\s+of\s+appeal|discretionary\s+review|the\s+writ|writ\s+of\s+error|(?:a|the|his|her|their|its)\s+(?:petition|application)(?:\s+for\s+(?:a\s+)?(?:writ\s+of\s+certiorari|certiorari|review|leave\s+to\s+appeal|allowance\s+of\s+appeal|discretionary\s+review))?)"
DENY = re.compile(
    r"\b(?:denied|denying|refused|refusing|declined)\s+(?:to\s+(?:grant|review|issue)\s+)?(?:\w+\s+){0,2}?" + RV +
    r"|\b(?:certiorari|cert\.|review|leave\s+to\s+appeal|writ)\s+(?:was\s+|were\s+)?(?:denied|refused)\b"
    r"|\bdeclined\s+to\s+review", re.I)
ACT_AFTER = re.compile(r"\b(?:affirm\w*|revers\w*|vacat\w*|held|holds|granted|granting|modif\w*|amend\w*|adopt\w*|"
                       r"reinstat\w*|withdr[ae]w\w*|substitut\w*|remand\w*)\b", re.I)
WORDS = re.compile(r"\b[a-z]{3,}\b")


def body_start(t):
    e = t.find(NL + "---", 3)
    return e + 4 if t.startswith("---") and e > 0 else 0


def keys_of(n):
    r = L.node_row(n)
    out = set()
    for c in r[5].split("|"):
        k = C.norm_cite(c) if c else None
        if k:
            out.add(k)
    return out


def cite_at(t, off, keys):
    """(start, end, key) of a citation of `keys` starting near `off` (the diag offset)."""
    for m in C.CITE_RX.finditer(t, max(0, off - 5), min(len(t), off + 80)):
        k = C.cite_key(m)
        if k in keys:
            return m.start(), m.end(), k
    return None


def deny_ctx(t, c0, c1, lo):
    """rule 1 at the citation [c0, c1)."""
    s0, s1 = C.sentence_span(t, c0, c1)
    s0 = max(s0, lo)
    seg0 = s0
    if len(WORDS.findall(t[s0:c0])) < 3 and s0 > lo:
        p0, _ = C.sentence_span(t, max(lo, s0 - 2), max(lo, s0 - 1))
        seg0 = max(lo, p0)
    seg = t[seg0:c0]
    last = None
    for m in DENY.finditer(seg):
        last = m
    if last is not None and not ACT_AFTER.search(seg[last.end():]) and             all(C.cite_key(m) in OWN_KEYS for m in C.CITE_RX.finditer(seg[last.end():])):  # R4: the phrase attaches to T' (its parallel cites allowed)
        return True, seg0
    post = t[c1:s1]
    for m in re.finditer(r"\(([^()]{0,200})\)", post):
        if DENY.search(m.group(1)):
            return True, seg0
    return False, seg0


def anchors_for(t, occs, lo):
    """anchor variants for T: each citation's sentence with its previous sentence, then the sentence alone."""
    out = []
    for back in (1, 0, 2, 3, 4, 5):
        for c0, c1 in occs:
            s0, s1 = C.sentence_span(t, c0, c1)
            p0 = max(s0, lo)
            for _ in range(back):
                if p0 <= lo:
                    break
                p0, _e = C.sentence_span(t, max(lo, p0 - 2), max(lo, p0 - 1))
                p0 = max(p0, lo)
            out.append((p0, s1))
    seen, res = set(), []
    for a in out:
        if a not in seen and a[1] - a[0] <= 1400:
            seen.add(a)
            res.append(a)
    return res


def part_of(pm, off):
    return C.part_at(pm, off)[0].rstrip("~")  # part_map2; "~" marks a part read without a heading


ALLOWED = {}
OWN_KEYS = set()


def work(item):
    s, rows, cands, allowed = item
    ALLOWED.update(allowed)
    tx = L.fetch_texts([s] + sorted({r["target"] for r in rows}))
    if s not in tx:
        return {"s": s, "err": "notext"}
    t0 = tx[s][1]
    lo = body_start(t0)
    pm = C.part_map2(t0)
    pm = pm[0] if isinstance(pm, tuple) else pm
    t = L.norm(t0)  # one for one: offsets kept; hard-wrapped lines are not sentence ends
    res = {"s": s, "out": []}
    cby = {c["j"]: c for c in cands}
    for r in rows:
        tp = r["target"]
        if tp not in cby:
            continue
        ktp = keys_of(tp)
        OWN_KEYS.clear()
        OWN_KEYS.update(ktp)
        occ_tp = []
        for o in cby[tp]["occ"]:
            ca = cite_at(t, o[0], ktp)
            if ca and ca[0] >= lo:
                occ_tp.append(ca)
        den = [ca for ca in occ_tp if deny_ctx(t, ca[0], ca[1], lo)[0]]
        if not den or len(den) < len(occ_tp):
            continue
        d_tp = cby[tp]["date"]
        ttxt = tx.get(tp, ("", ""))[1]
        tkeys_in_tp = {C.cite_key(m) for m in C.CITE_RX.finditer(ttxt)}
        tp_name = set(C.name_tokens(L.node_row(tp)[6]))
        best = []
        for c in cands:
            j = c["j"]
            if j == tp or j not in ALLOWED.get((s, tp), ()):
                continue
            kj = keys_of(j)
            occ_j = []
            for o in c["occ"]:
                ca = cite_at(t, o[0], kj)
                if ca and ca[0] >= lo:
                    occ_j.append(ca)
            plain = [ca for ca in occ_j if not deny_ctx(t, ca[0], ca[1], lo)[0]]
            cited_by_tp = bool(kj & tkeys_in_tp) or (bool(tp_name) and set(C.name_tokens(L.node_row(j)[6])) == tp_name)
            best.append((c["date"], j, len(occ_j), len(plain), cited_by_tp, plain))
        ok = [b for b in best if b[3] > 0 and b[4]]
        rec = {"by": s, "tp": tp, "id": r["id"], "kind": r["kind"], "scope": r["scope"],
               "deny_quote": L.norm(t[deny_ctx(t, den[0][0], den[0][1], lo)[1]:den[0][1]])[-300:],
               "cands": [(b[0], b[1], b[2], b[3], b[4]) for b in best]}
        if not ok:
            rec["status"] = "no_T" if not best else "T_not_ok"
            res["out"].append(rec)
            continue
        ok.sort()
        d, j, _n, _p, _c, plain = ok[-1]
        rec["T"] = j
        rec["status"] = "ok"
        rec["anchors"] = []
        for a0, a1 in anchors_for(t, [(p[0], p[1]) for p in plain], lo):
            ks = [p[2] for p in plain if a0 <= p[0] and p[1] <= a1]
            rec["anchors"].append((a0, a1, part_of(pm, a0), ks[0] if ks else plain[0][2]))
        rec["T_quote"] = L.norm(t[rec["anchors"][0][0]:rec["anchors"][0][1]])[:400] if rec["anchors"] else ""
        res["out"].append(rec)
    return res


R1_REMOVED = set(x.strip() for x in open(os.path.join(HERE, "remove_r1.txt"), encoding="utf-8"))  # base = v11a


def run(a):
    sc_nodes = {}
    with gzip.open(DIAG, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("cands"):
                sc_nodes[d["n"]] = d["cands"]
    rows = collections.defaultdict(list)
    have = collections.defaultdict(set)
    with open(os.path.join(BASE, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            by = int(p[2])
            if by not in sc_nodes or p[4] not in REVIEW:
                continue
            if p[0] in R1_REMOVED:
                continue
            rows[by].append({"id": p[0], "target": int(p[1]), "kind": p[4], "scope": p[5], "start": int(p[7]),
                             "end": int(p[8]), "ev": p[10], "part": p[11], "src": p[12]})
            have[by].add(int(p[1]))
    items = []
    F = L.Facts()
    allowed = {}
    for s, rs in rows.items():
        cands = sc_nodes[s]
        cby = {c["j"]: c for c in cands}
        keep = []
        for r in rs:
            c = cby.get(r["target"])
            if not c:
                continue
            ct = int(F.court[r["target"]])
            al = {o["j"] for o in cands if o["j"] != r["target"] and F.system(int(F.court[o["j"]])) == F.system(ct)
                  and F.rank(int(F.court[o["j"]])) < F.rank(ct) and c["date"] - MAX_GAP <= o["date"] <= c["date"]}
            if al:
                keep.append(r)
                allowed[(s, r["target"])] = al
        if keep:
            items.append((s, keep, cands, {k: v for k, v in allowed.items() if k[0] == s}))
    print("SC opinions with a review row and an earlier same-court candidate:", len(items), flush=True)
    st = collections.Counter()
    pairs, newrows, remove = [], [], []
    for res in L.pmap(work, items, procs=a.procs):
        if "err" in res:
            st["err"] += 1
            continue
        for rec in res["out"]:
            st[rec["status"]] += 1
            pairs.append(rec)
    rowsby = {(s, r["target"], r["kind"]): r for s, rs in rows.items() for r in rs}
    for rec in sorted(pairs, key=lambda x: (x["by"], x["tp"])):
        if rec["status"] != "ok":
            continue
        base = rowsby[(rec["by"], rec["tp"], rec["kind"])]
        remove.append(rec["id"])
        if rec["T"] in have[rec["by"]]:
            st["T_has_row"] += 1
            rec["status"] = "ok_T_has_row"
            continue
        for a0, a1, ap, key in rec["anchors"]:
            newrows.append({"rule": "below:sc11_r4", "table": "history", "by": rec["by"], "target": rec["T"],
                            "kind": rec["kind"], "scope": rec["scope"], "disp": [base["start"], base["end"]],
                            "part": base["part"], "anchor": [a0, a1], "anchor_part": ap, "ev": "cite:" + key,
                            "text": "by", "claim": "-",
                            "note": "scdb11 R4: refusal of review %d is not the judgment under review; row moved from "
                                    "%s" % (rec["tp"], rec["id"])})
    tag = a.tag
    with open(os.path.join(WORK, "r4_rows%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for r in newrows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "r4_remove%s.txt" % tag), "w", encoding="utf-8", newline=NL) as f:
        for i in remove:
            f.write(i + NL)
    with open(os.path.join(WORK, "r4_pairs%s.tsv" % tag), "w", encoding="utf-8", newline=NL) as f:
        f.write("status\tby\tdate\tT'\tT\tkind\tscope\tid\tdeny_quote\tT_quote\tcands\n")
        for rec in sorted(pairs, key=lambda x: (x["by"], x["tp"])):
            f.write("\t".join(str(v) for v in (rec["status"], rec["by"], "", rec["tp"], rec.get("T", ""), rec["kind"],
                                               rec["scope"], rec["id"], rec["deny_quote"], rec.get("T_quote", ""),
                                               json.dumps(rec["cands"]))) + NL)
    st["new_row_variants"] = len(newrows)
    st["remove"] = len(remove)
    json.dump(dict(st), open(os.path.join(WORK, "r4_stats%s.json" % tag), "w"), indent=1)
    print(dict(st))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a)


if __name__ == "__main__":
    main()
