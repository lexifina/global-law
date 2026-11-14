"""shadow10 (round 10, DESIGN10 section 4 + amendment D10-5): history_remand.tsv lines for the remand-bridge rows,
with a Python pre-check of remandBridge.

    python -X utf8 round10/agents/shadow10/remand10.py pre [--out DIR]
        default --out round10/agents/shadow10/cert_remand

Rows: every v9c history row of the classes remandtext-v2 (round9 shadow9 cert_remandtext_v2) and remandcap
(round8 orderdock cert_remandcap) -- ids read from those delta folders and confirmed present in round9/stage/v9c.
Candidate B (general, corpus-wide): a decision of the target's court sharing a docket token with the target
(round-8 docket index, meta.pkl), dated date(O) .. date(O) + 1,826 days.
Checks (first failure is the reason; a row passes when one B passes all):
  remandCourt   court(B) = court(T) (decisions2)
  remandDate    date(O) <= date(B) <= date(O) + 1,826 days and date(T) < date(O)
  remandDocket  a docket token d, compact(d) >= 4 chars with a digit, found (whole, alnum-bounded) in a span <= 200
                chars of B's text and of T's text
  remandCue     a quote of B <= 600 chars whose lower(norm(.)) holds "supreme court" and one of remand_cue
  remandTie     the same quote holds a tie to O: a compact citation key of O (one the index maps to O alone), or
                O's docket (compact, >= 4 chars with a digit), or O's date printed "Month D, YYYY" (full / 3-letter /
                "Sept") compared compact
Output: history_remand_delta.tsv (9 columns), cert_text_delta.tsv, window_sha_delta.tsv (as round-8 bridge
quotes: window [s-400, e+400) of the text, norm'd), cite_index_delta.tsv (O keys the base index lacks but the graph
index maps to O alone), precheck.tsv (one line per row: id, result, reason, detail), stats.json.
No answer-key file is read.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import certify6 as C6  # noqa: E402

L = C6.L
norm, lower, compact = C6.norm, C6.lower, C6.compact
NL, TAB = "\n", "\t"
PAD = 400
QMAX = 600
DMAX = 200
REMAND_CUE = ["vacat", "remand", "in light of", "further consideration"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
V9C = os.path.join(C2, "round9", "stage", "v9c")
CLASSES = [("remandtext-v2", os.path.join(C2, "round9/agents/shadow9/cert_remandtext_v2/history_delta.tsv")),
           ("remandcap", os.path.join(C2, "round8/agents/orderdock/cert_remandcap/history_delta.tsv"))]


RX_LIGHT = re.compile(r"in\s+light\s+of\s+(?:our\s+decision\s+in\s+|the\s+)?([A-Z][^,;()\n]{1,100}?\s+v\.\s+[^,;()\n]{2,100}?)\s*,")


def ordinal(d):
    try:
        return datetime.date(d // 10000, d // 100 % 100, d % 100).toordinal()
    except ValueError:
        return None


ABBR = {1: ["jan."], 2: ["feb."], 3: ["mar."], 4: ["apr."], 8: ["aug."], 9: ["sept.", "sep."], 10: ["oct."],
        11: ["nov."], 12: ["dec."]}


def date_keys(d):
    """D10-6 Q10-1: "<month> <d>, <yyyy>" (full lower-case month name) and "<abbr> <d>, <yyyy>"; matched in the
    lower-cased, norm'd quote (not compact)."""
    y, m, dd = d // 10000, d // 100 % 100, d % 100
    if not (1 <= m <= 12) or dd < 1:
        return []
    forms = [MONTHS[m - 1].lower()] + ABBR.get(m, [])
    return ["%s %d, %d" % (f, dd, y) for f in forms]


def cmap(s):
    out, pos = [], []
    for i, ch in enumerate(s):
        c = compact(ch)
        if c:
            out.append(c)
            pos.append(i)
    return "".join(out), pos


def find_token(text, ctext, cpos, tok):
    """Spans (a, b) of `text` whose compact string is `tok`, bounded by non-alnum characters on both sides."""
    out = []
    j = ctext.find(tok)
    while j >= 0:
        a, b = cpos[j], cpos[j + len(tok) - 1] + 1
        if (a == 0 or not text[a - 1].isalnum()) and (b >= len(text) or not text[b].isalnum()):
            out.append((a, b))
        j = ctext.find(tok, j + 1)
    return out


def body_start(text):
    """The offset after the YAML front matter ('---' ... '---'), 0 when there is none."""
    if text.startswith("---"):
        j = text.find(NL + "---", 3)
        if j >= 0:
            return j + 4
    return 0


def docket_span(text, a, b):
    """Widen the token span to its line (at most DMAX characters, centred on the token)."""
    ls = text.rfind(NL, 0, a) + 1
    le = text.find(NL, b)
    le = len(text) if le < 0 else le
    s, e = max(ls, a - 60), min(le, b + 60)
    while e - s > DMAX:
        if a - s > e - b:
            s += 1
        else:
            e -= 1
    while s < a and text[s] == " ":
        s += 1
    while e > b and text[e - 1] == " ":
        e -= 1
    return s, e


def quote_search(text, ties):
    """A quote of B (<= QMAX) with 'supreme court' + a remand cue + a tie; returns (status, (s, e), tie) where
    status is 'ok', 'noTie' (cue found, no tie within QMAX), or 'noCue'."""
    nt = lower(norm(text))
    scs = [m.start() for m in re.finditer("supreme court", nt)]
    if not scs:
        return "noCue", None, None
    cues = sorted((m.start(), len(c)) for c in REMAND_CUE for m in re.finditer(re.escape(c), nt))
    ct, cpos = cmap(text)
    tie_pos = []
    for kind, key in ties:
        if kind == "odate":
            for m in re.finditer(re.escape(key), nt):
                tie_pos.append((m.start(), m.end(), kind + ":" + key))
            continue
        j = ct.find(key)
        while j >= 0:
            tie_pos.append((cpos[j], cpos[j + len(key) - 1] + 1, kind + ":" + key))
            j = ct.find(key, j + 1)
    best = None
    cue_seen = False
    for p in scs:
        for c, cl in cues:
            lo, hi = min(p, c), max(p + 13, c + cl)
            if hi - lo > QMAX:
                continue
            cue_seen = True
            for a, b, lab in tie_pos:
                s, e = min(lo, a), max(hi, b)
                if e - s <= QMAX and (best is None or e - s < best[1] - best[0]):
                    best = (s, e, lab)
    if best is None:
        return ("noTie" if cue_seen else "noCue"), None, None
    s, e, lab = best
    # widen to sentence-ish boundaries while it stays <= QMAX
    s2 = max(text.rfind(". ", 0, s) + 2, text.rfind(NL, 0, s) + 1, 0)
    e2c = [x for x in (text.find(". ", e), text.find(NL, e)) if x >= 0]
    e2 = min(e2c) + 1 if e2c else len(text)
    if e - s2 <= QMAX:
        s = s2
    if e2 - s <= QMAX:
        e = e2
    while text[s] in " \n":
        s += 1
    while text[e - 1] in " \n":
        e -= 1
    return "ok", (s, e), lab


def read_decisions(want):
    out = {}
    with open(os.path.join(V9C, "decisions2.tsv"), "rb") as f:
        for line in f:
            i = line.find(b"\t")
            k = int(line[:i])
            if k in want:
                p = line.rstrip(b"\n").decode("utf-8").split(TAB)
                out[k] = (int(p[1]), int(p[2]), p[7])
    return out


def load_rows():
    rows = []
    for cls, path in CLASSES:
        for p in C6.read_tsv(path):
            rows.append((p[0], cls, int(p[2]), int(p[1]), p[4]))   # id, class, O, T, kind
    ids = {r[0] for r in rows}
    present = set()
    with open(os.path.join(V9C, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            i = line.split(TAB, 1)[0]
            if i in ids:
                present.add(i)
    return [r for r in rows if r[0] in present], len(rows) - len(present)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--out", default=os.path.join(HERE, "cert_remand"))
    ap.add_argument("--shared", action="store_true", help="also tie by O's shared order-list page citation")
    ap.add_argument("--reason", action="store_true", help="also tie by the reason case O's own text names")
    ap.add_argument("--odocket", action="store_true", help="also tie by O's own Supreme Court docket (not in D10-6)")
    ap.add_argument("--bdocket", action="store_true",
                    help="diagnosis: D10-6 tie (b) (the B/T docket in B's quote; dropped by D10-7)")
    ap.add_argument("--no-reason", action="store_true", help="diagnosis: without the D10-7 reason-case tie (c2)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    st = collections.Counter()
    rows, missing = load_rows()
    st["rows"] = len(rows)
    st["rows_not_in_v9c"] = missing
    meta = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))
    node_dk, idx = meta["node_dk"], meta["idx"]
    del meta
    orders = {o["n"]: o for o in pickle.load(open(os.path.join(C2, "round6/history/rules/memo/work/orders.pkl"),
                                                      "rb"))["orders"]}
    os_ = {r[2] for r in rows}
    ts = {r[3] for r in rows}
    dec0 = read_decisions(os_ | ts)
    cands = {}
    for rid, cls, o, t, kind in rows:
        if t not in dec0 or o not in dec0:
            cands[rid] = []
            continue
        ct, dO = dec0[t][0], dec0[o][1]
        oo = ordinal(dO)
        bs = set()
        for tk in node_dk.get(t, ()):
            for n in idx.get((ct, tk), ()):
                if n != t:
                    bs.add(n)
        cands[rid] = sorted(bs)
    allb = {b for v in cands.values() for b in v}
    dec = read_decisions(os_ | ts | allb)
    # candidate B must be dated in [O, O+1826] (the generator; the check repeats it)
    for rid, cls, o, t, kind in rows:
        dO = dec.get(o, (0, 0, ""))[1]
        oo = ordinal(dO) if dO else None
        keep = []
        for b in cands[rid]:
            db = dec.get(b, (0, 0, ""))[1]
            ob = ordinal(db) if db else None
            if oo and ob and 0 <= ob - oo <= 1826:
                keep.append(b)
        cands[rid] = keep
    need = {b for v in cands.values() for b in v} | ts | os_
    texts = L.fetch_texts(sorted(need))
    # O's citation keys: base index keys mapping to O alone; memo cites mapped to O alone by graph U base
    base_idx = collections.defaultdict(set)
    for p in C6.read_tsv(os.path.join(V9C, "cite_index.tsv")):
        if len(p) >= 2:
            base_idx[compact(p[0])].add(int(p[1]))
    okeys = collections.defaultdict(set)
    for c, ns in base_idx.items():
        for n in ns:
            if n in os_ and ns == {n}:
                okeys[n].add((c, "base"))
    memo_keys = {}
    for o in os_:
        od = orders.get(o)
        if od:
            for c in (od.get("cites") or "").split("|"):
                k = compact(c.strip())
                if k:
                    memo_keys.setdefault(k, set()).add(o)
    # O's parallel citations (S. Ct., L. Ed.) from the graph citation index
    with open(os.path.join(L.W, "graph", "cite_index.tsv"), "rb") as f:
        for line in f:
            i = line.rfind(b"\t")
            try:
                n = int(line[i + 1:])
            except ValueError:
                continue
            if n in os_:
                k = compact(line[:i].decode("utf-8", "replace"))
                if k:
                    memo_keys.setdefault(k, set()).add(n)
    hits = C6.graph_hits(set(memo_keys))
    for k, os2 in memo_keys.items():
        nodes = {n for _, n in hits.get(k, ())} | base_idx.get(k, set())
        for o in os2:
            if nodes == {o} and (k, "base") not in okeys[o]:
                okeys[o].add((k, "graph"))
    lines, wins, cite_out, pre = [], {}, set(), []
    order_of = ["remandCourt", "remandDate", "remandDocket", "remandCue", "remandTie"]
    for rid, cls, o, t, kind in rows:
        od = orders.get(o, {})
        ties = [("cite", k) for k, _src in sorted(okeys.get(o, ()))]
        if a.shared:
            # O's own reporter citations (memo parse) even when the page holds several orders (diagnosis variant)
            uk = {k for k, _s in okeys.get(o, ())}
            for c in (od.get("cites") or "").split("|"):
                k = compact(c.strip())
                if k and k not in uk:
                    ties.append(("citeShared", k))
        ospan = {}
        if not a.no_reason and od and o in texts and texts[o][0] == dec.get(o, (0, 0, ""))[2]:
            # D10-7 (c2): the reason case named in O's own text at its disposition ("in light of X v. Y,"); the O span
            # runs from "in light of" to the end of the name (<= 300 chars) and must start before the disposition
            # quote's end + 50
            otx = texts[o][1]
            q0, q1 = od["disp"]
            lo_ = max(0, q0 - 50)
            for m in RX_LIGHT.finditer(otx, lo_, min(len(otx), q1 + 300)):
                if m.start() > q1 + 50:
                    break
                sp0, sp1 = m.start(), m.end(1)
                tie_s = m.group(1)
                k = compact(tie_s)
                if len(k) >= 8 and sp1 - sp0 <= 300 and "in light of" in lower(norm(otx[sp0:sp1]))                         and k in compact(otx[sp0:sp1]):
                    ties.append(("reason", k))
                    ospan[k] = (norm(tie_s).strip(), sp0, sp1)
        odk = compact((od.get("docket") or "").split(",")[0])
        if a.odocket and len(odk) >= 4 and re.search(r"\d", odk):
            ties.append(("odocket", odk))
        if o in dec:
            ties += [("odate", k) for k in date_keys(dec[o][1])]
        if not cands[rid]:
            pre.append((rid, cls, "fail", "noCandidateB", ""))
            st[cls + ":fail:noCandidateB"] += 1
            continue
        best = None   # (progress, detail, line)
        for b in sorted(cands[rid], key=lambda n: (dec[n][1], n)):
            prog, detail, got = 0, "", None
            if dec[b][0] != dec[t][0]:
                detail = "court"
            else:
                prog = 1
                ob, oo, ot = ordinal(dec[b][1]), ordinal(dec[o][1]), dec[t][1]
                if not (ob and oo and 0 <= ob - oo <= 1826 and ot < dec[o][1]):
                    detail = "date"
                else:
                    prog = 2
                    if b not in texts or t not in texts:
                        detail = "textMissing"
                    elif texts[b][0] != dec[b][2] or texts[t][0] != dec[t][2]:
                        detail = "shaMismatch"
                    else:
                        tb, tt = texts[b][1], texts[t][1]
                        cb, pb = cmap(tb)
                        ctt, pt = cmap(tt)
                        dk = None
                        for tok in sorted(set(node_dk.get(t, ())) & set(node_dk.get(b, ()))):
                            k = compact(tok)
                            if len(k) < 4 or not re.search(r"\d", k):
                                continue
                            sb = find_token(tb, cb, pb, k)
                            stt = find_token(tt, ctt, pt, k)
                            if sb and stt:
                                # prefer the docket as printed in the text's body (after the front matter)
                                fb, ft = body_start(tb), body_start(tt)
                                sb1 = next((x for x in sb if x[0] >= fb), sb[0])
                                st1 = next((x for x in stt if x[0] >= ft), stt[0])
                                dk = (k, docket_span(tb, *sb1), docket_span(tt, *st1))
                                break
                        if dk is None:
                            detail = "docketNotInBothTexts"
                        else:
                            prog = 3
                            status, q, lab = quote_search(tb, ties)
                            if status != "ok" and a.bdocket:
                                # D10-6 tie (b): compact(docket) -- the docket shared by B and T -- in B's quote
                                s2, q2, l2 = quote_search(tb, ties + [("bdocket", dk[0])])
                                if s2 == "ok":
                                    status, q, lab = s2, q2, l2
                            if status == "noCue":
                                detail = "noCueQuote"
                            elif status == "noTie":
                                prog = 4
                                detail = "noTieInCueQuote(ties:%s)" % ",".join(sorted({x for x, _ in ties}))
                            else:
                                prog = 5
                                detail = lab
                                got = (b, q, dk)
            if best is None or prog > best[0]:
                best = (prog, b, detail, got)
            if prog == 5:
                break
        prog, b, detail, got = best
        if prog == 5:
            b, (q0, q1), (k, (d0, d1), (e0, e1)) = got
            spans = [(b, q0, q1), (b, d0, d1), (t, e0, e1)]
            if detail.startswith("reason:"):
                tie_s, o0, o1 = ospan[detail[7:]]
                spans.append((o, o0, o1))
            else:
                tie_s, o0, o1 = "", 0, 0
            lines.append((rid, b, q0, q1, k, d0, d1, e0, e1, tie_s.replace(TAB, " "), o0, o1))
            for node, s, e in spans:
                tx = texts[node][1]
                s0, e1_ = max(0, s - PAD), min(len(tx), e + PAD)
                wins[(dec[node][2], s0, e1_)] = norm(tx[s0:e1_])
            if detail.startswith("cite:"):
                key = detail[5:]
                if (key, "graph") in okeys.get(o, ()):
                    cite_out.add((key, o))
            pre.append((rid, cls, "pass", "", "B=%d %s" % (b, detail)))
            st[cls + ":pass"] += 1
            st[cls + ":pass_tie_" + detail.split(":")[0]] += 1
        else:
            reason = order_of[prog]
            pre.append((rid, cls, "fail", reason, "best B=%d %s" % (b, detail)))
            st[cls + ":fail:" + reason] += 1

    def write(name, items):
        p = os.path.join(a.out, name)
        with open(p, "w", encoding="utf-8", newline=NL) as f:
            for it in items:
                f.write(TAB.join(map(str, it)) + NL)

    write("history_remand_delta.tsv", lines)
    wk = sorted(wins)
    write("cert_text_delta.tsv", ((s, s0, e0, wins[(s, s0, e0)]) for s, s0, e0 in wk))
    write("window_sha_delta.tsv", ((s, s0, e0, hashlib.sha1(wins[(s, s0, e0)].encode("utf-8")).hexdigest(), "corpus")
                                   for s, s0, e0 in wk))
    write("cite_index_delta.tsv", sorted(cite_out))
    write("precheck.tsv", pre)
    st["lines"] = len(lines)
    st["windows"] = len(wins)
    st["cite_index_lines"] = len(cite_out)
    json.dump(dict(sorted(st.items())), open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
