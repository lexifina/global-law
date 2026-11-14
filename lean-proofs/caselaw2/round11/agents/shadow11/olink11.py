"""shadow11 (round 11, DESIGN11 section 4): the round-10 C6 caption linker (shadow10 cap10/build10) ported to an
order node given as a SPEC instead of a corpus node of the round-6 memo parse.

A spec = (node id, docket, caption as printed, date yyyymmdd, the node's own text, [lower court as named]).
The order list prints captions surname-first in capitals ("VILLARREAL, HECTOR V. UNITED STATES"); norm_caption()
turns a person side into the reporter's style ("Hector VILLARREAL") so the round-9/10 caption rules (memolib
side_match, rules9 given-name guard, cap10 full_names) apply unchanged. Captions already in the reporter's style
are left as they are.

    python -X utf8 round11/agents/shadow11/olink11.py test [--style reporter|list] [--remand-only] [--y0 2010 --y1 2019]
        corpus GVR orders as specs -> C6 links, compared with round-10 shadow10 work/build10_cap_b_links.tsv

Library use (build11.py): make_order(spec) -> order dict (memo-parse shape) or (None, reason); inject(order);
candidates(order) -> {t: rec}; mark_full(order, rec); pick_c6(rec).
No answer-key file is read.
"""
import argparse
import collections
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round10", "agents", "shadow10"))
import cap10  # noqa: E402  (imports rules9 with JOIN and SURNAME on)

R, M, L = cap10.R, cap10.M, cap10.L
S10W = os.path.join(C2, "round10", "agents", "shadow10", "work")
S9W = os.path.join(C2, "round9", "agents", "shadow9", "work")
NL = chr(10)

CUE = {"vacated": ("vacat",), "reversed": ("revers",)}
DISQ = ("would revers", "would vacat", "would affirm")
RX_PREFIX_END = re.compile(r"\b(?:Motions?|Applications?|Petitions?|Stay|Leave|On\s+(?:petition|appeal|motion)|"
                           r"The\s|Probable|Treating|In\s+this)\b")
RX_SCOTUS_DATE = re.compile(r"Supreme Court of (?:the )?United States\.?\s+[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}\.?\s*")
RX_REMAND_TO_LIST = re.compile(
    r"\bremanded\s+to\s+(?:the\s+)?((?:(?![;\[\]]).){4,170}?)(?=\s+(?:for\s+(?:further|the\s+purpose|purposes|"
    r"consideration|reconsideration|proceedings|entry|dismissal)|with\s+(?:instructions|directions)|in\s+light\b|"
    r"to\s+(?:consider|dismiss|enter|vacate|determine|address)\b|so\s+that\b|where\b|on\s+remand\b)|[.;]\s|[.;]?\s*$)",
    re.I)
RX_PERCUR = re.compile(r"^\s*Per\s+Curiam\s*[.:]?\s*", re.I)

# words that make a caption side an organisation / office rather than a natural person (order-list style)
ORG_WORDS = set("""
    inc llc llp lp ltd co corp corporation company companies bank bancorp union local association assn associates
    department dept board city county state states united america commonwealth people commission committee district
    school schools university college trust trustees estate church diocese archdiocese international national
    partnership partners group insurance services service hospital center centre authority agency office bureau
    council government republic federation foundation society institute club enterprises industries holdings systems
    railroad railway airlines motors products communications network fund funds plan administration warden secretary
    director commissioner superintendent sheriff attorney general governor judge clerk officer chief administrator
    executor executrix guardian ex rel parte matter re na fsb pc pa pllc plc
""".split())
SUFFIX = {"jr", "sr", "ii", "iii", "iv", "v"}


def _w(s):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*\.?", s)


def _title(w):
    return "-".join(p[:1].upper() + p[1:].lower() for p in w.split("-"))


def norm_side(side):
    """'VILLARREAL, HECTOR M.' -> 'Hector M. VILLARREAL'; 'SMITH, JOHN, JR., ET AL.' -> 'John SMITH, Jr., et al.'.
    A side not in capitals, or one whose words name an organisation / office, is returned unchanged."""
    s = side.strip()
    letters = [ch for ch in s if ch.isalpha()]
    if not letters or sum(ch.isupper() for ch in letters) < 0.9 * len(letters):
        return s
    chunks = [c.strip() for c in s.split(",")]
    if len(chunks) < 2:
        return s
    head, given = chunks[0], chunks[1]
    hw = [w.lower().rstrip(".") for w in _w(head)]
    gw = [w.lower().rstrip(".") for w in _w(given)]
    if not hw or not gw or len(gw) > 4 or len(hw) > 3:
        return s
    if (set(hw) | set(gw)) & ORG_WORDS or gw[0] in SUFFIX or gw[:2] == ["et", "al"]:
        return s
    if any(len(w) < 2 for w in hw):
        return s
    rest = []
    for c in chunks[2:]:
        cw = [w.lower().rstrip(".") for w in _w(c)]
        if cw and cw[0] in SUFFIX:
            rest.append(c.title() if len(c) > 3 else c)
        elif cw[:2] == ["et", "al"]:
            rest.append("et al.")
        else:
            rest.append(c)
    given_t = " ".join(w if (len(w.rstrip(".")) == 1) else _title(w) for w in given.split())
    out = given_t + " " + head.upper()
    if rest:
        out += ", " + ", ".join(rest)
    return out


def norm_caption(cap):
    cap = re.sub(r"\s+", " ", cap or "").strip()
    cap = re.sub(r"^(?:No\.\s*)?\d{1,4}[-–—]\d{1,6}\s+", "", cap)   # a docket number printed first
    p = re.split(r"\s+(?:V|v|Vs|VS|vs)\.?\s+", cap, maxsplit=1)
    if len(p) != 2:
        return norm_side(cap)
    return norm_side(p[0]) + " v. " + norm_side(p[1])


_COURTS = []


def courts():
    if not _COURTS:
        _COURTS.append(M.Courts())
    return _COURTS[0]


def _resolve_all(caps, generic=False, no_dc=False):
    got = []
    for cap in caps:
        k = courts().resolve(cap, generic=generic)
        if k is not None and not (no_dc and k[0] == "dc") and k not in got:
            got.append(k)
    return got


def make_order(spec, remand_only=False):
    """spec: dict n, docket, caption, date, text, [lower], [part]. -> (order dict, '') or (None, reason)."""
    T = spec["text"]
    cap = norm_caption(spec["caption"])
    # the disposition words: the text after the printed caption (when found), else the whole text
    c0 = 0
    raw = re.sub(r"\s+", " ", spec["caption"]).strip()
    if raw:
        k = T.find(raw)
        if k < 0:
            k = M.lower(T).find(M.lower(raw))
        if k >= 0:
            c0 = k + len(raw)
    core_full = T[c0:]
    msep = M.RX_SEP.search(core_full)
    cut = msep.start() if msep else len(core_full)
    core = core_full[:cut]
    cl = M.classify(core)
    if cl is None:
        return None, "no_disposition"
    kind, scope, (m0, m1) = cl
    if kind not in CUE:
        return None, "kind_" + kind
    a, b = c0 + m0, c0 + m1
    q0, q1 = M.quote_span(T, a, b, c0, c0 + cut)
    ql = M.lower(T[q0:q1])
    if not any(c in ql for c in CUE[kind]) or any(d in ql for d in DISQ) or q1 <= q0:
        q0, q1 = a, b
        ql = M.lower(T[q0:q1])
        if not any(c in ql for c in CUE[kind]) or any(d in ql for d in DISQ):
            return None, "no_cue_in_quote"
    cb = M.blank(M.RX_BRACKET, core)
    keys, src = [], ""
    if spec.get("lower"):
        keys, src = _resolve_all([spec["lower"]], generic=True, no_dc=False), "spec"
    if not keys and not remand_only:
        # the court printed before the disposition ("C. A. 10th Cir. Certiorari granted, judgment vacated ...")
        first = min((m.start() for _k, rx in M.RX_KIND for m in [rx.search(cb)] if m), default=len(cb))
        pre = cb[:first]
        pm = RX_PERCUR.match(pre)
        if pm:
            pre = pre[pm.end():]
        pe = RX_PREFIX_END.search(pre)
        if pe:
            pre = pre[:pe.start()]
        if re.search(r"[A-Za-z]{2}", pre):
            pk = [courts().resolve(x) for x in re.split(r";|\band\b", pre) if re.search(r"[A-Za-z]{2}", x)]
            keys, src = [k for k in pk if k is not None], "prefix"
    if not keys and not remand_only:
        keys, src = _resolve_all([m.group(1) for m in M.RX_TO_COURT.finditer(cb)]), "to"
        if not keys:
            keys, src = _resolve_all([m.group(1) for m in M.RX_JUDG_OF.finditer(cb)], generic=True), "judgment-of"
    if not keys:
        # the remand clause of an order list: "... remanded to the United States Court of Appeals for the Fifth
        # Circuit for further consideration ..." (the whole court name, up to the purpose words)
        keys, src = _resolve_all([m.group(1) for m in RX_REMAND_TO_LIST.finditer(cb)], generic=True, no_dc=True), \
            "remand-clause"
    if not keys:
        keys, src = _resolve_all([m.group(1) for m in M.RX_REMAND_TO.finditer(cb)], generic=True, no_dc=True), \
            "remand-to"
    if not keys:
        src = ""
    o = {"n": spec["n"], "date": int(spec["date"]), "od": M.ordinal(int(spec["date"])),
         "docket": spec.get("docket") or "", "title": cap, "caps": [cap], "kind": kind, "scope": scope,
         "disp": (q0, q1), "part": spec.get("part", "perCuriam"), "courts": keys, "court_src": src, "rb": [],
         "rb_sent": None, "rbn": [], "off": 0, "T": T, "full": 1, "cites": "", "spec_caption": spec["caption"]}
    return o, ""


def inject(o):
    R.orders()[o["n"]] = o


_IDX = {}


TOK11 = os.path.join(HERE, "work", "tokidx11.pkl")


def _idx():
    if not _IDX:
        _IDX["tok"] = pickle.load(open(os.path.join(S9W, "tokidx.pkl"), "rb"))
        if os.path.exists(TOK11):
            # the round-9 index covers the caption tokens / courts of corpus GVR orders only; tokidx11 (same build,
            # for the order-list nodes' tokens and courts) replaces the keys it holds
            _IDX["tok"].update(pickle.load(open(TOK11, "rb")))
        _IDX["F"] = L.Facts()
    return _IDX["tok"], _IDX["F"]


def build_tokidx(orders):
    """round9 remandtext.stage_index for the given (injected) orders' caption tokens and courts -> work/tokidx11.pkl
    ((court, token) -> nodes with a docket number). One pass over graph/nodes.tsv."""
    want_tok, want_ct = set(), set()
    for o in orders:
        for k in o["courts"]:
            if k is not None:
                want_ct.update(courts().group.get(k, ()))
        want_tok |= M.toks(" ".join(o["caps"]) or o["title"])
    node_dk = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb"))["node_dk"]
    F = L.Facts()
    idx = collections.defaultdict(list)
    with open(L.NODES, "rb") as f:
        for n, line in enumerate(f):
            if n not in node_dk:
                continue
            c = int(F.court[n])
            if c not in want_ct:
                continue
            p = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            for w in M.toks(p[6]) & want_tok:
                idx[(c, w)].append(n)
    os.makedirs(os.path.dirname(TOK11), exist_ok=True)
    pickle.dump(dict(idx), open(TOK11, "wb"), protocol=4)
    _IDX.clear()
    print("tokidx11: tokens", len(want_tok), "courts", len(want_ct), "keys", len(idx), flush=True)


def candidates(o):
    """cap10.stage_cand for one injected order: decisions of its one court below 1..1,095 days before it whose
    title ties its caption on both sides (rules9.both_sides, JOIN and SURNAME on)."""
    tokidx, F = _idx()
    ks = {k for k in o["courts"] if k is not None}
    if len(ks) != 1:
        return None, "not_one_court"
    cap = R.one_caption(o, True)
    if cap is None:
        return None, "not_one_caption"
    ids = set(courts().group.get(next(iter(ks)), ()))
    ocap = M.toks(cap)
    od, oo = o["date"], M.ordinal(o["date"])
    Ts = set()
    for c in ids:
        for w in ocap:
            for n in tokidx.get((c, w), ()):
                dn = int(F.date[n])
                if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                    Ts.add(n)
    good = [t for t in sorted(Ts) if R.both_sides(o["n"], t)]
    if not good:
        return None, "no_both_sides"
    rec = {}
    for t in good:
        rec[t] = {"date": int(F.date[t]), "days": oo - M.ordinal(int(F.date[t])), "court": int(F.court[t]),
                  "sibs": sorted(R.sibs(o["n"], t))}
    return {"date": od, "kind": o["kind"], "part": o["part"], "T": rec}, ""


_HEADS = {}


def heads(nodes):
    need = sorted(set(nodes) - set(_HEADS))
    for i in range(0, len(need), 5000):
        for n, (_s, t) in L.fetch_texts(need[i:i + 5000]).items():
            _HEADS[n] = re.sub(r"[^a-z0-9]", "", t[:4000].lower())
    return _HEADS


def mark_full(o, rec):
    fn = cap10.full_names(R.one_caption(o, True) or "")
    rec["has_full"] = bool(fn)
    rec["fn"] = fn
    if fn:
        hd = heads(rec["T"])
        for t, r in rec["T"].items():
            r["full"] = bool(t in hd and any(k in hd[t] for k in fn))
    else:
        for r in rec["T"].values():
            r["full"] = False


def pick_c6(rec):
    return cap10.pick(rec, "C6_fullname_unique_nosib")


def link_specs(specs, remand_only=False):
    """specs -> {n: (order, rec, t or None, reason)}. Candidate texts are fetched in bulk."""
    out, recs = {}, {}
    for sp in specs:
        o, why = make_order(sp, remand_only)
        if o is None:
            out[sp["n"]] = (None, None, None, why)
            continue
        inject(o)
        rec, why = candidates(o)
        if rec is None:
            out[sp["n"]] = (o, None, None, why)
            continue
        recs[o["n"]] = (o, rec)
    need = set()
    for o, rec in recs.values():
        if cap10.full_names(R.one_caption(o, True) or ""):
            need |= set(rec["T"])
    heads(need)
    for n, (o, rec) in recs.items():
        mark_full(o, rec)
        t = pick_c6(rec)
        out[n] = (o, rec, t, "linked" if t is not None else ("no_full_name" if not rec["has_full"] else "not_unique"))
    return out


# ------------------------------------------------------------------------------------------------------------------
# remand bridge (round-9 shadow9 remandtext K9 v2): T found through the court below's own remand decision B
_RT = []


def _rt():
    if not _RT:
        sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
        import remandtext as RT  # noqa: E402
        _RT.append(RT)
    return _RT[0]


_EDGE = {}


def out_edges(nodes):
    """graph out-edges of the given nodes (B's citations); one read of graph/edges.bin."""
    import numpy as np
    need = np.array(sorted(set(nodes) - set(_EDGE)), dtype=np.uint32)
    if len(need):
        e = np.fromfile(os.path.join(L.W, "graph", "edges.bin"), dtype=np.uint32).reshape(-1, 2)
        for n in need.tolist():
            _EDGE[n] = set()
        for s, d in e[np.isin(e[:, 0], need)].tolist():
            _EDGE[s].add(d)
        del e
    return _EDGE


def remand_specs(orders, corpus_cites=False):
    """K9 v2 over injected orders -> {n: (t or None, rec, reason)}.
    Signals per (O, T, B) as remandtext.stage_link, from B's text and B's graph out-edges. An order-list node has no
    page citation and no out-edges: citeBO is False and `reason` comes from B's text only (O's "in light of X v."
    named in B), unless corpus_cites (test on corpus orders: as round 9, through the graph)."""
    RT = _rt()
    tokidx, F = _idx()
    meta = pickle.load(open(os.path.join(C2, "round8/agents/orderdock/work/meta.pkl"), "rb")) if "meta" not in _IDX \
        else _IDX["meta"]
    _IDX["meta"] = meta
    node_dk, idx = meta["node_dk"], meta["idx"]
    trips = {}
    for o in orders:
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts().group.get(k, ()))
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        if not ids or not ocap:
            continue
        od, oo = o["date"], M.ordinal(o["date"])
        Ts = set()
        for c in ids:
            for w in ocap:
                for n in tokidx.get((c, w), ()):
                    dn = int(F.date[n])
                    if dn < od and 0 < oo - M.ordinal(dn) <= 1095:
                        Ts.add(n)
        trip = []
        for t in Ts:
            ct = int(F.court[t])
            for tk in node_dk.get(t, ()):
                for b in idx.get((ct, tk), ()):
                    db = int(F.date[b])
                    if b != t and db >= od and M.ordinal(db) - oo <= 1826:
                        trip.append((t, b, tk))
        if trip:
            trips[o["n"]] = (o, trip)
    allB = sorted({b for _o, tr in trips.values() for _t, b, _k in tr})
    texts = {}
    for i in range(0, len(allB), 3000):
        for n, (_s, tx) in L.fetch_texts(allB[i:i + 3000]).items():
            texts[n] = tx
    bo_all = out_edges(allB + ([o.get("orig", o["n"]) for o, _ in trips.values()] if corpus_cites else []))
    page_nodes = _page_nodes() if corpus_cites else {}
    Cm = L.reader_common()
    out = {}
    for o_n, (o, trip) in trips.items():
        rn = RT.reason_name(o["T"])
        drx = RT.docket_rx(o["docket"])
        ds = RT.date_strs(o["date"])
        ocap = M.toks(" ".join(o["caps"]) or o["title"])
        sib, reasons = set(), set()
        if corpus_cites:
            for c in (o.get("cites") or "").split("|"):
                k = Cm.norm_cite(c.strip())
                if k:
                    sib |= page_nodes.get(k, set())
            reasons = {x for x in bo_all.get(o.get("orig", o_n), ()) if int(F.court[x]) == RT.SC} - sib
        T = {}
        for t, b, tk in trip:
            if b not in texts:
                continue
            tx = texts[b]
            bo = bo_all.get(b, set())
            s = {"cue": RT.has_cue(tx),
                 "citeBO": bool(sib & bo), "citeBT": t in bo,
                 "reason": bool(rn and re.search(r"\b%s\s+v\.\s" % re.escape(rn), tx)) or bool(reasons & bo),
                 "odocket": bool(drx and re.search(drx, tx)),
                 "odate": any(re.search(p, tx) for p in ds),
                 "capB": bool(ocap & M.toks(R.title(b))), "date": int(F.date[b])}
            rec = T.setdefault(t, {"B": {}, "date": int(F.date[t]), "court": int(F.court[t]), "dk": set()})
            rec["dk"].add(tk)
            rec["B"][b] = s
        rec = {"kind": o["kind"], "part": o["part"], "date": o["date"], "T": T}
        t = R.pick(rec, "K9", o_n)
        out[o_n] = (t, rec, "linked" if t is not None else "no_K9")
    return out


def _page_nodes():
    Cm = L.reader_common()
    pn = collections.defaultdict(set)
    for p in L.shards(".meta.tsv.gz"):
        if not os.path.basename(p).startswith("supreme-court"):
            continue
        for r in L.meta_rows(p):
            for c in r[9].split("|"):
                k = Cm.norm_cite(c.strip())
                if k:
                    pn[k].add(int(r[0]))
    return pn


# ------------------------------------------------------------------------------------------------------------------
# test on corpus order nodes
def to_list_style(cap):
    """Reporter caption -> order-list style ('Hector VILLARREAL, petitioner, v. UNITED STATES' ->
    'VILLARREAL, HECTOR V. UNITED STATES'); used only to test norm_caption on a synthetic order-list caption."""
    sides = M.V_RX.split(cap, maxsplit=1)
    out = []
    for side in sides:
        side = re.sub(r",?\s*(?:petitioners?|respondents?|appellants?|appellees?)\b\.?", "", side.strip(),
                      flags=re.I)
        chunks = [c.strip() for c in side.split(",") if c.strip()]
        if not chunks:
            out.append(side.upper())
            continue
        words = chunks[0].split()
        caps = [i for i, w in enumerate(words) if sum(ch.isalpha() for ch in w) >= 2 and w.isupper()]
        if caps and caps[0] > 0 and all(not words[j].isupper() or len(words[j].rstrip(".")) == 1
                                        for j in range(caps[0])):
            nm = " ".join(words[caps[0]:]) + ", " + " ".join(words[:caps[0]])
            rest = chunks[1:]
            out.append(", ".join([nm] + rest).upper())
        elif not caps and 2 <= len(words) <= 4 and not ({w.lower().strip(".,") for w in words} & ORG_WORDS):
            out.append(", ".join([words[-1] + ", " + " ".join(words[:-1])] + chunks[1:]).upper())
        else:
            out.append(", ".join(chunks).upper())
    return " V. ".join(out)


def test():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--style", default="reporter")
    ap.add_argument("--remand-only", action="store_true")
    ap.add_argument("--y0", type=int, default=2010)
    ap.add_argument("--y1", type=int, default=2019)
    a = ap.parse_args()
    ref = {}
    for line in open(os.path.join(S10W, "build10_cap_b_links.tsv"), encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        ref[int(p[0])] = int(p[1])
    orders = dict(R.orders())
    specs, back = [], {}
    base = 900_000_000
    for i, o in enumerate(sorted(orders.values(), key=lambda x: x["n"])):
        if o["kind"] not in ("vacated", "reversed") or not (a.y0 <= o["date"] // 10000 <= a.y1):
            continue
        cap = R.one_caption(o, True)
        if cap is None:
            continue
        if a.style == "list":
            cap = to_list_style(cap)
        n = base + i
        back[n] = o["n"]
        # the node's own text: the stored text with the caption line first (as an order-list node prints it)
        # the order's words as the memo parse cut them (after the part heading, or after the head matter's
        # "Supreme Court of the United States <date>" line)
        T = o["T"]
        st = None
        if o["part"] == "headmatter":
            ms = list(RX_SCOTUS_DATE.finditer(T, 0, max(0, o["disp"][0] - o["off"])))
            st = ms[-1].end() if ms else None
        else:
            j = T.rfind("## ", 0, max(0, o["disp"][0] - o["off"]))
            k = T.find("  ", j) if j >= 0 else -1
            st = k + 2 if k >= 0 else None
        text = cap + NL + (T[st:] if st is not None else T)
        specs.append({"n": n, "docket": o["docket"], "caption": cap, "date": o["date"], "text": text,
                      "part": o["part"]})
    res = link_specs(specs, a.remand_only)
    if a.cmd == "test-remand":
        ref9 = {}
        for i, line in enumerate(open(os.path.join(S9W, "k9_links_v2.tsv"), encoding="utf-8")):
            if i:
                p = line.rstrip(NL).split("\t")
                ref9[int(p[0])] = int(p[1])
        objs = []
        for n, (o, _rec, _t, _why) in res.items():
            if o is not None:
                o["orig"] = back[n]
                o["cites"] = orders[back[n]].get("cites", "")
                objs.append(o)
        for cc in (True, False):
            rr = remand_specs(objs, corpus_cites=cc)
            c = collections.Counter()
            for o in objs:
                on = o["orig"]
                t = rr.get(o["n"], (None,))[0]
                r = ref9.get(on)
                c["ref" if r is not None else "noref"] += 1
                if r is None and t is None:
                    continue
                c["new" if r is None else "lost" if t is None else "same" if r == t else "other"] += 1
            print("K9 v2 port, corpus_cites=%s:" % cc, dict(sorted(c.items())), flush=True)
        return
    c = collections.Counter()
    diffs = []
    for n, (o, rec, t, why) in res.items():
        on = back[n]
        r = ref.get(on)
        c["specs"] += 1
        c["why_" + why] += 1
        if r is None and t is None:
            c["both_none"] += 1
        elif r is None:
            c["new_link"] += 1
            diffs.append(("new", on, t, why))
        elif t is None:
            c["lost"] += 1
            diffs.append(("lost", on, r, why))
        elif r == t:
            c["same"] += 1
        else:
            c["other"] += 1
            diffs.append(("other", on, r, t))
    ref_in = sum(1 for on in back.values() if on in ref)
    print("ref C6 links in range", ref_in, dict(sorted(c.items())))
    for d in diffs[:40]:
        on = d[1]
        print(d, "|", R.one_caption(orders[on], True)[:90], "|", norm_caption(to_list_style(R.one_caption(orders[on], True)))[:90] if a.style == "list" else "")


if __name__ == "__main__":
    {"test": test, "test-remand": test}[sys.argv[1]]()
