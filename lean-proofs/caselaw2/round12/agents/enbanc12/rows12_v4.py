"""enbanc12 rule EB12 (round 12): the en banc court's own words (or its order's) say the panel opinion was vacated /
withdrawn -> history row on the panel opinion P (never on the order granting rehearing en banc).

    python -X utf8 rows12.py [--procs 8]   -> work/eb12_rows.jsonl, work/eb12_pairs.tsv, work/eb12_stats.json

Inputs: pop12.py's work files (eb_docket.json, eb_feats.jsonl, tgt_feats.json) and the v11d base history (gate).
Rule, general over every decision D of the base whose bench is enBanc / limitedEnBanc (the en banc opinion or the
court's en banc order) and every corpus order O of the same docket whose own text grants rehearing en banc:
  P (target) = the panel opinion: the latest earlier same-court decision (<= 5 years) sharing a docket number with D
      whose text is not an order about rehearing (short text with a grant / denial / vacatur form) and that is not
      itself en banc; or, without a docket link, the earlier same-court same-name decision D cites in the statement's
      own sentence (same tests).
  statement: a sentence of D's majority / per curiam / plurality part (for O: its text) saying the panel / prior /
      original opinion (or judgment) was / is vacated or withdrawn, or "vacated on grant of rehearing en banc",
      "reh'g en banc granted, opinion vacated" after a citation of P;
  gates: no statement of the court's rule (effect of, R. / Rule N, I.O.P., "is to vacate"); no party's request
      (suggest, request, ask, urge, argue, contend, moved, seek) in the clause; no negation / conditional (not, never, denied, would, whether, if, unless) in the statement's clause; no
      other court as actor (certiorari, Supreme Court); no partial words (in part, portion, insofar, to the extent,
      Part / Section N, as to, issue); a citation in the sentence that resolves to a same-court node must be P or an
      order of the docket; D's main parts do not reinstate / adopt the panel opinion; P has no admitted negative
      history row in the base and no row by D; one row per P (earliest acting node).
  evidence: a citation of P within 400 characters of the statement (ev cite:<key>); else the caption of D's head
      matter naming P's parties with an anchor cue (anchor, ev name:<tokens>).
  kind: vacated ('vacat') else withdrawn ('withdr'); scope all.
No answer-key file is read.
"""
import argparse, collections, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round6", "history", "rules", "rehear"))
sys.path.insert(0, HERE)
import r6lib as L  # noqa: E402
import rehear_link as RL  # noqa: E402
import pop12 as P  # noqa: E402

C = L.reader_common()
NL = chr(10)
WORK = P.WORK
PARTS_OK = ("majority", "perCuriam", "plurality")
NEGW = re.compile(r"\b(?:not|never|denied|deny|denying|declin\w*|would|whether|if|unless|should)\b", re.I)
OTHER = re.compile(r"certiorari|supreme\s+court|\bremand(?:ed)?\s+(?:from|by)\b", re.I)
PARTIAL = re.compile(r"\bin\s+part\b|\bportions?\b|\binsofar\b|\bto\s+the\s+extent\b|\b(?:part|section)\s+[IVX\d]|"
                     r"\bas\s+to\b|\bissues?\b|\blimited\b|\bonly\b|\bexcept\b|\bother\s+than\b|\bremainder\b", re.I)
ANCH = re.compile(r"court\s+of\s+(?:civil\s+|criminal\s+)?appeals?|supreme\s+(?:judicial\s+)?court|appellate\s+"
                  r"(?:division|court|term)|superior\s+court|district\s+court|circuit\s+court|en\s+banc|in\s+banc|"
                  r"rehearing", re.I)
# a statement of the court's rule ("the effect of granting rehearing en banc is to vacate"), not of this case's act
RULEW = re.compile(r"\beffect\s+of\b|\bR\.\s*\d|\bRules?\s+\d|\bI\.?\s?O\.?\s?P\b|\bis\s+to\s+vacate|\bshall\s+be\s+to\s+"
                   r"vacate|\boperating\s+procedure|\bgeneral\s+order", re.I)
# a party's request, not the court's act
ASKW = re.compile(r"\b(?:suggest\w*|request\w*|ask\w*|urg\w*|argu\w*|contend\w*|mov(?:ed|es|ing)|seek\w*|sought|pray\w*)\b",
                  re.I)
DQA = ("former appeal", "prior appeal", "first appeal", "earlier appeal", "previous appeal", "see also")


def tokens(title):
    return RL.ascii_tokens(title)


def work(items):
    """items: [(D, P, kind_of_D, cited_keys_of_P)] -> candidate rows."""
    nodes = sorted({x[0] for x in items})
    tx = L.fetch_texts(nodes)
    out = []
    for d, p, src, pkeys, okt in items:
        if d not in tx:
            continue
        t0 = tx[d][1]
        lo = P.body_start(t0)
        t = L.norm(t0)
        pm = C.part_map2(t0)
        pm = pm[0] if isinstance(pm, tuple) else pm
        # reinstatement / adoption anywhere in a main part -> no row
        ad = [m for m in P.E_ADOPT.finditer(t, lo) if C.part_at(pm, m.start())[0].rstrip("~") in PARTS_OK]
        if ad and src == "E":
            out.append({"d": d, "p": p, "drop": "adopts", "q": t[max(0, ad[0].start() - 100):ad[0].end() + 100]})
            continue
        best = None
        why = "no_statement"
        for m in P.E_VAC.finditer(t, lo):
            part = C.part_at(pm, m.start())[0].rstrip("~")
            if src == "E" and part not in PARTS_OK:
                why = "part_" + part
                continue
            s0, s1 = C.sentence_span(t, m.start(), m.end())
            s0 = max(s0, lo)
            sent = t[s0:s1]
            clause = sent[max(0, sent.rfind(";", 0, m.start() - s0) + 1):m.end() - s0]
            if NEGW.search(clause):
                why = "negation"
                continue
            if RULEW.search(sent):
                why = "rule_statement"
                continue
            if ASKW.search(clause):
                why = "party_request"
                continue
            if OTHER.search(sent):
                why = "other_court"
                continue
            if PARTIAL.search(sent):
                why = "partial"
                continue
            # citations in the sentence: each must be P or an order of the docket (okt), or unresolved
            bad = False
            ckeys = []
            for c in C.CITE_RX.finditer(sent):
                k = C.cite_key(c)
                if k:
                    ckeys.append(k)
            ph = m.group(0).lower()
            kind = "vacated" if "vacat" in ph else "withdrawn" if "withdr" in ph else None
            if kind is None:
                why = "kind"
                continue
            best = {"q0": s0, "q1": s1, "part": part, "kind": kind, "ckeys": ckeys, "quote": sent[:600]}
            break
        if best is None:
            out.append({"d": d, "p": p, "drop": why})
            continue
        # evidence: a citation of P within 400 characters of the quote
        win0, win1 = max(0, best["q0"] - 400), min(len(t), best["q1"] + 400)
        win = t[win0:win1]
        ev = None
        for c in C.CITE_RX.finditer(win):
            k = C.cite_key(c)
            if k and k in pkeys:
                ev = "cite:" + k
                break
        anchor = None
        if ev is None:
            # caption of the head matter naming P's parties
            # (an order / slip opinion without head matter: the opening of its first main part, which carries the
            # caption)
            hm = [(a, b, "headmatter") for a, b, nm, _l in pm if nm == "headmatter"]
            if not hm:
                hm = [(a, b, nm.rstrip("~")) for a, b, nm, _l in pm if nm.rstrip("~") in PARTS_OK][:1]
            if hm:
                a, b, apart = hm[0]
                cap = t[a:min(b, a + 2500)]
                ptok = tokens(L.node_row(p)[6])
                w = RL.words(cap)
                have = [x for x in sorted(ptok) if " " + x.lower() + " " in w]
                mm = ANCH.search(cap)
                if have and mm and not any(x in cap.lower() for x in DQA):
                    # end the anchor at the first anchor cue after the last name token
                    lastpos = max(cap.lower().find(x.lower()) for x in have[:3])
                    m2 = ANCH.search(cap, lastpos)
                    if m2:
                        anchor = [a, a + m2.end()]
                        ev = "name:" + " ".join(have[:3])
        if ev is None:
            out.append({"d": d, "p": p, "drop": "no_evidence", "q": best["quote"]})
            continue
        out.append({"d": d, "p": p, "drop": "", "ev": ev, "anchor": anchor, "src": src,
                    "apart": apart if anchor else None, **best})
    return out


def run(a):
    eb = P.load_eb()
    dk = json.load(open(os.path.join(WORK, "eb_docket.json")))
    tf = json.load(open(os.path.join(WORK, "tgt_feats.json")))
    F = L.Facts()
    E = {}
    with open(os.path.join(WORK, "eb_feats.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            E[r["d"]] = r
    # keys of every candidate node
    items = []
    st = collections.Counter()
    for d, r in E.items():
        sd = set(dk["same_docket"].get(str(d), []))
        cs = {int(k) for k in r["cited_same"]}
        ops, ords = [], []
        for m in sd | cs:
            if m in eb:
                continue
            ft = tf.get(str(m))
            if ft is None:
                continue
            if P.is_order(ft):
                ords.append(m)
            elif not ft["head_eb"]:
                ops.append(m)
        if not ops:
            continue
        ops.sort(key=lambda m: (int(F.date[m]), m))
        sdo = [m for m in ops if m in sd]
        p = sdo[-1] if sdo else ops[-1]
        if not r["vac"]:
            continue
        items.append((d, p, "E", None, ords))
        # orders of the docket (not en banc bench) after P whose own text vacates the panel opinion
        for o in ords:
            ft = tf[str(o)]
            if ft["ovac"] and ft["grant"] and int(F.date[o]) >= int(F.date[p]) and o not in E:
                items.append((o, p, "O", None, ords))
    items = list({(x[0], x[1]): x for x in items}.values())
    print("items", len(items), flush=True)
    # P's citation keys
    pset = {x[1] for x in items}
    pkeys = collections.defaultdict(set)
    with open(P.CITE_INDEX, encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split(chr(9))
            if len(q) >= 2 and q[1].isdigit() and int(q[1]) in pset:
                pkeys[int(q[1])].add(q[0])
    items = [(d, p, s, pkeys.get(p, set()), o) for d, p, s, _k, o in items]
    res = []
    for r in L.pmap(work, [items[i:i + 40] for i in range(0, len(items), 40)], procs=a.procs):
        res.extend(r)
    # a citation in the statement's sentence that resolves to a same-court node other than P / an order of the docket
    want = {k for h in res if not h["drop"] for k in h["ckeys"]}
    k2n = collections.defaultdict(set)
    with open(P.CITE_INDEX, encoding="utf-8") as f:
        for line in f:
            q = line.rstrip(NL).split(chr(9))
            if len(q) >= 2 and q[0] in want:
                k2n[q[0]].add(int(q[1]))
    okt = {(x[0], x[1]): set(x[4]) for x in items}
    # a cited same-court node whose own text is an order about rehearing (or that sits en banc) is the grant order /
    # the en banc court, not another opinion
    other = sorted({m for h in res if not h["drop"] for k in h["ckeys"] for m in k2n.get(k, ())
                    if m != h["p"] and m != h["d"] and int(F.court[m]) == int(F.court[h["d"]])})
    ofe = {}
    for r in L.pmap(P.feats_texts, [other[i:i + 80] for i in range(0, len(other), 80)], procs=a.procs):
        ofe.update(r)
    order_like = {m for m, fe in ofe.items() if P.is_order(fe) or fe["head_eb"]} | {m for m in other if m in eb}
    for h in res:
        if h["drop"]:
            continue
        cd = int(F.court[h["d"]])
        for k in h["ckeys"]:
            for m in k2n.get(k, ()):
                if m != h["p"] and m not in okt[(h["d"], h["p"])] and m not in order_like and int(F.court[m]) == cd \
                        and m != h["d"]:
                    h["drop"] = "cites_other"
                    h["q"] = h["quote"]
    # base gate
    hist, _st = P.load_v11d(pset)
    NEGK = {"vacated", "withdrawn", "reversed", "substitutedBy", "rehearingEnBancGranted", "modified"}
    rows, pairs, seen = [], [], set()
    for h in sorted(res, key=lambda x: (int(F.date[x["d"]]), x["d"])):
        d, p = h["d"], h["p"]
        if h["drop"]:
            st["drop_" + h["drop"]] += 1
            pairs.append((h["drop"], d, p, "", "", (h.get("q") or "")[:300]))
            continue
        # a cited same-court node in the sentence other than P / an order of the docket
        prior = hist.get(p, [])
        if any(b == d for b, *_x in prior):
            st["has_row_by_d"] += 1
            pairs.append(("has_row_by_d", d, p, h["src"], h["kind"], h["quote"][:300]))
            continue
        if any(k in NEGK and v.startswith("ok") for _b, k, _s, _r, v in prior):
            st["p_already_negative"] += 1
            pairs.append(("p_already_negative", d, p, h["src"], h["kind"], h["quote"][:300]))
            continue
        if p in seen:
            st["p_dup"] += 1
            continue
        seen.add(p)
        st["ok_%s_%s_%s" % (h["src"], h["kind"], "anch" if h["anchor"] else "cite")] += 1
        pairs.append(("ok", d, p, h["src"], h["kind"], h["quote"][:300]))
        rows.append({"rule": "rehear:eb12_%s" % h["src"].lower(), "table": "history", "by": d, "target": p,
                     "kind": h["kind"], "scope": "all", "main": [h["q0"], h["q1"]], "part": h["part"],
                     "ev": h["ev"], "joined": [], "claim": "-", "doctrine": "-", "field_limit": "-", "text": "by",
                     "anchor": h["anchor"], "anchor_part": h["apart"],
                     "note": "enbanc12 EB12: the en banc court's own words say the panel opinion was %s" % h["kind"]})
    with open(os.path.join(WORK, "eb12_rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "eb12_pairs.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write(chr(9).join(("status", "by", "target", "src", "kind", "quote")) + NL)
        for p in pairs:
            f.write(chr(9).join(L.norm(str(v)) for v in p) + NL)
    json.dump(dict(st), open(os.path.join(WORK, "eb12_stats.json"), "w"), indent=1)
    print(len(rows), dict(st))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    run(a)


if __name__ == "__main__":
    main()
