"""scdb11 rule R1 (round 11, move 5): a rehearing denial is not the judgment under review.

    python -X utf8 r1scan11.py run [--procs 8] [--tag x]  -> work/r1_rows<tag>.jsonl (new rows on T),
                                                            work/r1_remove<tag>.txt (ids of the rows on T'),
                                                            work/r1_pairs<tag>.tsv, work/r1_stats<tag>.json

Rule, general over every Supreme Court history row of the base (round10/stage/v10d) whose kind is a review kind
(reversed, vacated, affirmed, modified, reviewDismissed) and whose target is T':
  1. The Supreme Court's own text reports T' as a denial of rehearing: at a citation of T' in the Court's text, the
     clause that the citation closes (the citation's sentence before the citation; the previous sentence when the
     citation's own sentence is a bare citation) or a parenthetical right after the citation holds a rehearing-denial
     phrase ("denied rehearing en banc", "rehearing denied", "denied a petition for rehearing", "dissented from the
     failure to grant rehearing en banc", "decision not to rehear", "rejected its suggestion for rehearing en banc"),
     with no later judicial act verb (affirmed, reversed, vacated, held, granted, modified, amended, adopted,
     reinstated, withdrew, substituted, remanded) between that phrase and the citation.
  2. T = the decision of the same court as T' (round 6 below_sc candidate list of that Supreme Court opinion), decided
     before T' and at most 3 years earlier, cited by the Court at some place that is not itself a rehearing-denial
     citation (rule 1), and cited by T' itself (T' names the decision whose rehearing it denies). When several, the
     latest.
  3. Then the decision under review is T: a new history row by the Supreme Court opinion on T, same kind, scope and
     disposition quote as the row on T', anchored at a sentence of the Court's text that cites T (each citation
     sentence with its previous sentence is offered in text order; the certifier keeps the first that passes), and
     the row on T' is listed for removal (a rehearing-denial order is not the judgment the Court reversed).
     When the Supreme Court opinion already has a review row on T, only the removal is listed.
No answer-key file is read.
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
MAX_GAP = 30000  # yyyymmdd difference: 3 years

REH = r"(?:rehear\w*|reh['’]?g\.?)"
DENY = re.compile(
    r"\bden(?:ied|ies|y|ying|ial\s+of)\b[^.;:]{0,90}?\b" + REH +
    r"|\b" + REH + r"[^.;:]{0,70}?\bden(?:ied|ying)\b"
    r"|\b(?:failure|refusal|refused|declin\w+)\s+to\s+(?:grant\s+|order\s+)?" + REH +
    r"|\b(?:decision|vote|voted|votes)\s+not\s+to\s+(?:grant\s+|order\s+)?" + REH +
    r"|\brejected\s+(?:its|the|a|their|his|her)\s+suggestion\s+for\s+rehearing", re.I)
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
    if last is not None and not ACT_AFTER.search(seg[last.end():]):
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


def work(item):
    s, rows, cands = item
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
            if j == tp or c["court"] != cby[tp]["court"] or not (d_tp - MAX_GAP <= c["date"] < d_tp):
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
            rows[by].append({"id": p[0], "target": int(p[1]), "kind": p[4], "scope": p[5], "start": int(p[7]),
                             "end": int(p[8]), "ev": p[10], "part": p[11], "src": p[12]})
            have[by].add(int(p[1]))
    items = []
    for s, rs in rows.items():
        cands = sc_nodes[s]
        cby = {c["j"]: c for c in cands}
        keep = []
        for r in rs:
            c = cby.get(r["target"])
            if not c:
                continue
            if any(o["j"] != r["target"] and o["court"] == c["court"] and c["date"] - MAX_GAP <= o["date"] < c["date"]
                   for o in cands):
                keep.append(r)
        if keep:
            items.append((s, keep, cands))
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
            newrows.append({"rule": "below:sc11_r1", "table": "history", "by": rec["by"], "target": rec["T"],
                            "kind": rec["kind"], "scope": rec["scope"], "disp": [base["start"], base["end"]],
                            "part": base["part"], "anchor": [a0, a1], "anchor_part": ap, "ev": "cite:" + key,
                            "text": "by", "claim": "-",
                            "note": "scdb11 R1: rehearing denial %d is not the judgment under review; row moved from "
                                    "%s" % (rec["tp"], rec["id"])})
    tag = a.tag
    with open(os.path.join(WORK, "r1_rows%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for r in newrows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "r1_remove%s.txt" % tag), "w", encoding="utf-8", newline=NL) as f:
        for i in remove:
            f.write(i + NL)
    with open(os.path.join(WORK, "r1_pairs%s.tsv" % tag), "w", encoding="utf-8", newline=NL) as f:
        f.write("status\tby\tdate\tT'\tT\tkind\tscope\tid\tdeny_quote\tT_quote\tcands\n")
        for rec in sorted(pairs, key=lambda x: (x["by"], x["tp"])):
            f.write("\t".join(str(v) for v in (rec["status"], rec["by"], "", rec["tp"], rec.get("T", ""), rec["kind"],
                                               rec["scope"], rec["id"], rec["deny_quote"], rec.get("T_quote", ""),
                                               json.dumps(rec["cands"]))) + NL)
    st["new_row_variants"] = len(newrows)
    st["remove"] = len(remove)
    json.dump(dict(st), open(os.path.join(WORK, "r1_stats%s.json" % tag), "w"), indent=1)
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
