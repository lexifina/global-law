"""scdb11 rule R2 (round 11, move 5): the en banc decision says its own rehearing en banc vacated the panel decision.

    python -X utf8 r2scan11.py run [--procs 8] [--tag x]  -> work/r2_rows<tag>.jsonl, work/r2_pairs<tag>.tsv,
                                                            work/r2_stats<tag>.json

Rule, general over every en banc / limited en banc decision D of the base (decisions2 bench of round10/stage/v10d):
  A citation in D's own text (majority / per curiam / plurality part by part_map2) of an earlier decision T of the
  same court, decided at most 3 years before D, in the same case (the graph case names of T and D give the same
  name tokens), carries D's statement that T was vacated / withdrawn by the grant of rehearing en banc:
    E1 a subsequent-history note right after the citation, in the citation's sentence: "424 F.3d 467 (6th Cir.2005),
       vacated on grant of reh'g en banc (2006)", "..., reh'g en banc granted, opinion vacated", "..., vacated and
       reh'g en banc granted";
    E2 the citation's sentence (or the sentence that a bare citation sentence closes) says the court granted
       rehearing en banc / vacated the panel opinion: "We granted rehearing en banc, vacating the panel opinion.
       See 85 F.3d 1300", "rehearing en banc was granted and the panel opinion vacated";
  no negation (not, denied, deny, declin) in the clause, no "would" (a dissent's wish).
  Row: by D, target T, kind vacated when the statement says vacat; withdrawn when it says withdr; else
  rehearingEnBancGranted; scope all; disposition quote = the statement's sentence(s) (carrying the citation); no
  anchor. Skipped when D already has a history row on T.
No answer-key file is read.
"""
import argparse, collections, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

C = L.reader_common()
NL = chr(10)
WORK = os.path.join(HERE, "work")
BASE = os.path.join(C2, "round10", "stage", "v10d")
CITE_INDEX = os.path.join(L.W, "graph", "cite_index.tsv")
MAX_GAP = 30000
PARTS_OK = ("majority", "perCuriam", "plurality")

EB = r"(?:en\s+banc|in\s+banc)"
REH = r"(?:rehearing|reh['’]?g\.?)"
E1 = re.compile(r"^[^;]{0,90}?(?:\bvacated\b[^;]{0,40}?\b" + REH + r"\s+" + EB + r"|\bwithdrawn\b[^;]{0,40}?\b" + REH +
                r"\s+" + EB + r"|\b" + REH + r"\s+" + EB + r"\s+granted)", re.I)
E2 = re.compile(r"\bgrant(?:ed|ing)?\b[^.;]{0,60}?\b" + REH + r"\s+" + EB + r"|\b" + REH + r"\s+" + EB +
                r"\s+(?:was\s+|were\s+|having\s+been\s+|is\s+)?granted|\bvacat(?:ed|ing)\s+(?:the|our|its|that)\s+"
                r"(?:\w+\s+){0,2}?panel(?:'s|’s)?\s+(?:opinion|decision|judgment)", re.I)
NEG = re.compile(r"\b(?:not|never|denied|deny|denying|declin\w*|would|whether|if)\b", re.I)
WORDS = re.compile(r"\b[a-z]{3,}\b")


# v3 (after audit r11b03): E2 off -- the citation that closes "we granted rehearing en banc" is the order granting
# it, not the panel decision; E1 only when no other citation stands between T's citation and the note, and T's
# citation occurs once in the sentence.
E2_ON = os.environ.get("R2_E2") == "1"


def body_start(t):
    e = t.find(NL + "---", 3)
    return e + 4 if t.startswith("---") and e > 0 else 0


def work(nodes):
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
        for m in C.CITE_RX.finditer(t, lo):
            k = C.cite_key(m)
            if not k:
                continue
            c0, c1 = m.start(), m.end()
            s0, s1 = C.sentence_span(t, c0, c1)
            s0 = max(s0, lo)
            ev = None
            post = t[c1:s1]
            e1 = E1.search(post)
            if e1 and not NEG.search(post[:e1.end()]) and not C.CITE_RX.search(post[:e1.end()])                     and t[s0:s1].count(t[c0:c1]) == 1:
                ev = ("E1", s0, s1, post[:e1.end()])
            elif E2_ON:
                seg0 = s0
                if len(WORDS.findall(t[s0:c0])) < 3 and s0 > lo:
                    p0, _ = C.sentence_span(t, max(lo, s0 - 2), max(lo, s0 - 1))
                    seg0 = max(lo, p0)
                seg = t[seg0:c0]
                e2 = None
                for x in E2.finditer(seg):
                    e2 = x
                if e2 is not None:
                    clause = seg[max(0, seg.rfind(";", 0, e2.start()) + 1):]
                    if not NEG.search(clause):
                        ev = ("E2", seg0, s1, seg[e2.start():])
            if ev is None:
                continue
            part = C.part_at(pm, ev[1])[0].rstrip("~")
            out.append({"d": d, "key": k, "c0": c0, "c1": c1, "ev": ev[0], "q0": ev[1], "q1": ev[2],
                        "part": part, "phrase": ev[3][-200:], "quote": t[ev[1]:ev[2]][:700]})
    return out


ORDER = re.compile(r"\b" + REH + r"\s+" + EB + r"[^.]{0,40}?\b(?:is|be|are|was)\s+(?:hereby\s+)?granted|\bpanel\s+"
                   r"(?:opinion|decision)[^.]{0,60}?\b(?:is|be)\s+(?:hereby\s+)?vacated|\bgrant(?:ed|s)?\s+(?:the\s+)?"
                   r"(?:petition|suggestion|motion)[^.]{0,40}?" + REH + r"\s+" + EB + r"|\bordered\s+that\s+(?:this\s+)?"
                   r"(?:case|cause|appeal)[^.]{0,40}?\breheard\s+" + EB, re.I)


def order_check(nodes):
    """targets whose own text is an order granting rehearing en banc (the vacating order, not the panel decision)."""
    tx = L.fetch_texts(nodes)
    out = {}
    for n in nodes:
        if n in tx:
            t = L.norm(tx[n][1])
            out[n] = bool(ORDER.search(t, body_start(tx[n][1])))
    return out


def run(a):
    eb = {}
    with open(os.path.join(BASE, "decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 6)
            if p[4] in ("enBanc", "limitedEnBanc"):
                eb[int(p[0])] = (int(p[1]), int(p[2]))
    print("en banc decisions", len(eb), flush=True)
    have = collections.defaultdict(set)
    with open(os.path.join(BASE, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.split("\t", 3)
            have[int(p[2])].add(int(p[1]))
    nodes = sorted(eb)
    chunks = [nodes[i:i + 60] for i in range(0, len(nodes), 60)]
    hits = []
    for res in L.pmap(work, chunks, procs=a.procs):
        hits.extend(res)
    print("evidence citations", len(hits), flush=True)
    want = {h["key"] for h in hits}
    k2n = collections.defaultdict(set)
    with open(CITE_INDEX, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) >= 2 and p[0] in want:
                k2n[p[0]].add(int(p[1]))
    F = L.Facts()
    tg = sorted({next(iter(k2n[h["key"]])) for h in hits if len(k2n.get(h["key"], ())) == 1})
    is_order = {}
    for res in L.pmap(order_check, [tg[i:i + 60] for i in range(0, len(tg), 60)], procs=a.procs):
        is_order.update(res)
    st = collections.Counter()
    rows, pairs, seen = [], [], set()
    for h in sorted(hits, key=lambda x: (x["d"], x["c0"])):
        d = h["d"]
        cd, dd = eb[d]
        ns = k2n.get(h["key"], set())
        if len(ns) != 1:
            st["key_unresolved" if not ns else "key_ambiguous"] += 1
            continue
        tgt = next(iter(ns))
        if tgt == d:
            st["self"] += 1
            continue
        if int(F.court[tgt]) != int(F.court[d]):
            st["other_court"] += 1
            continue
        td = int(F.date[tgt])
        if not (dd - MAX_GAP <= td < dd):
            st["date_window"] += 1
            continue
        nt = set(C.name_tokens(L.node_row(tgt)[6]))
        nd = set(C.name_tokens(L.node_row(d)[6]))
        if not nt or nt != nd:
            st["other_name"] += 1
            pairs.append(("other_name", d, tgt, h["ev"], h["part"], L.norm(h["quote"])[:400]))
            continue
        if h["part"] not in PARTS_OK:
            st["part_" + h["part"]] += 1
            pairs.append(("part", d, tgt, h["ev"], h["part"], L.norm(h["quote"])[:400]))
            continue
        if is_order.get(tgt):
            st["target_is_order"] += 1
            pairs.append(("target_is_order", d, tgt, h["ev"], h["part"], L.norm(h["quote"])[:400]))
            continue
        if tgt in have[d]:
            st["has_row"] += 1
            pairs.append(("has_row", d, tgt, h["ev"], h["part"], L.norm(h["quote"])[:400]))
            continue
        if (d, tgt) in seen:
            continue
        seen.add((d, tgt))
        ph = h["phrase"].lower()
        kind = "vacated" if "vacat" in ph else "withdrawn" if "withdr" in ph else "rehearingEnBancGranted"
        st["ok_" + h["ev"] + "_" + kind] += 1
        pairs.append(("ok", d, tgt, h["ev"], h["part"], L.norm(h["quote"])[:400]))
        rows.append({"rule": "rehear:sc11_r2_" + h["ev"].lower(), "table": "history", "by": d, "target": tgt,
                     "kind": kind, "scope": "all", "disp": [h["q0"], h["q1"]], "part": h["part"],
                     "anchor": None, "ev": "cite:" + h["key"], "text": "by", "claim": "-",
                     "note": "scdb11 R2: en banc decision's own statement that rehearing en banc vacated T (%s)"
                             % h["ev"]})
    tag = a.tag
    with open(os.path.join(WORK, "r2_rows%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "r2_pairs%s.tsv" % tag), "w", encoding="utf-8", newline=NL) as f:
        f.write("status\tby\ttarget\tev\tpart\tquote\n")
        for p in pairs:
            f.write("\t".join(str(v) for v in p) + NL)
    json.dump(dict(st), open(os.path.join(WORK, "r2_stats%s.json" % tag), "w"), indent=1)
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
