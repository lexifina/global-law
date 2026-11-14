"""Round 8 `orderdock`: resolve the history strings (hscan.py) into order -> decision-below links.

    python -X utf8 round8/agents/orderdock/dres.py        -> work/bridge_links.tsv, work/bridge_stats.json

Rule (general, corpus-wide):
  A later text holds "<decision below> ..., <history phrase>, <Supreme Court reference>" in one citation clause.
  - The Supreme Court reference names the order: by its docket number ("No. 15-375": the order whose own docket
    number it is) or by a U.S. / S. Ct. / L. Ed. page that the order carries (pages hold several orders: then the
    order whose court below holds the decision below; a caption tie-check only when still several).
  - The phrase agrees with the order's kind (cert. denied ~ certDenied; vacated ~ vacated; rev'd ~ reversed;
    aff'd ~ affirmed; dismissed ~ reviewDismissed; cert. granted alone names no disposition and is not used).
  - The decision below is the last citation group of the clause before the phrase (after any earlier history
    phrase of the clause), resolved through graph/cite_index.tsv with the round-6 citation forms (r6cite), or the
    lower-court docket number of the clause ("No. 14-10234") through the docket index of the court the order names.
    It must be a decision of a court the order names, dated before the order and at most 10 years older.
  - An order is linked when every bridge record that names it gives the same decision below (unique).
No answer-key file is read.
"""
import collections
import glob
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
sys.path.insert(0, os.path.join(HIST, "citeforms"))
import r6lib as L  # noqa: E402
import r6cite  # noqa: E402
sys.path.insert(0, HERE)
import dock as D  # noqa: E402

C = L.reader_common()
WORK = os.path.join(HERE, "work")
NL = chr(10)
MAXDAYS = 1095   # the decision below is at most three years older than the order

RX_PHRASE_IN_PRE = re.compile(
    r"\b(?:cert(?:iorari|\.)?\s*(?:was\s+)?(?:denied|den\.|granted|dismissed)|(?:judgment\s+)?vacated|rev'?d|"
    r"reversed|aff'?d|affirmed|modified|appeal\s+dismissed|on\s+remand|remanded)\b", re.I)


def phrase_kinds(ph):
    p = ph.lower()
    if p.startswith("cert"):
        if "denied" in p or "den." in p:
            return {"certDenied"}
        if "dismissed" in p:
            return {"reviewDismissed"}
        return set()  # "cert. granted": the disposition follows in another phrase
    if "vacated" in p:
        return {"vacated"}
    if p.startswith("rev"):
        return {"reversed", "vacated"}
    if p.startswith("aff"):
        return {"affirmed"}
    if "dismissed" in p:
        return {"reviewDismissed"}
    if p == "gvr":
        return {"vacated"}
    return set()


def load_cite_index(need):
    idx = {}
    with open(os.path.join(L.W, "graph", "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            k, _t, v = line.rstrip(NL).partition("\t")
            if k in need:
                idx[k] = int(v)
    return idx


def main():
    import memolib as M
    courts = M.Courts()
    F = L.Facts()
    orders = pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]
    meta = pickle.load(open(os.path.join(WORK, "meta.pkl"), "rb"))
    dk_idx = meta["idx"]
    del meta
    by_dock = collections.defaultdict(list)
    by_page = collections.defaultdict(list)
    oinfo = {}
    ocites = {}
    for o in orders:
        ids = set()
        for k in o["courts"]:
            if k is not None:
                ids.update(courts.group.get(k, ()))
        oinfo[o["n"]] = (o["date"], o["kind"], frozenset(ids), o["title"], o["caps"])
        ocites[o["n"]] = {k for k in (C.norm_cite(c.strip()) for c in (o["cites"] or "").split("|")) if k}
        for t in re.findall(r"\d{2}[-–]\d{1,5}[A-Z]?", o["docket"] or ""):
            by_dock[t.replace("–", "-")].append(o["n"])
        for c in (o["cites"] or "").split("|"):
            k = C.norm_cite(c.strip())
            if k:
                by_page[k].append(o["n"])
    recs = []
    need = set()
    for p in sorted(glob.glob(os.path.join(WORK, "hist", "*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if not phrase_kinds(r["ph"]):
                    continue
                recs.append(r)
                for k, a, b in r["cites"]:
                    for kk in r6cite.keys(r["snip"][a - r["s0"]:b - r["s0"]] or k):
                        need.add(kk)
                    need.add(k)
    idx = load_cite_index(need)
    st = collections.Counter()
    _tt = {}

    def ttoks(t):
        if t not in _tt:
            row = L.node_row(t)
            _tt[t] = set(M.toks(row[6]))
        return _tt[t]
    votes = collections.defaultdict(lambda: collections.defaultdict(list))  # order -> target -> [(bridge, how)]
    for r in recs:
        kinds = phrase_kinds(r["ph"])
        dn = int(F.date[r["n"]])
        # --- the order(s) named
        cand_o = set()
        how_o = ""
        for typ, key, _a, _b in r["refs"]:
            if typ == "d":
                got = [o for o in by_dock.get(key, ()) if oinfo[o][1] in kinds]
                if got:
                    cand_o.update(got)
                    how_o = "dock"
        if not cand_o:
            for typ, key, _a, _b in r["refs"]:
                if typ == "c":
                    got = [o for o in by_page.get(key, ()) if oinfo[o][1] in kinds]
                    cand_o.update(got)
                    how_o = "page"
                    if got:
                        break
        # every page reference of the clause in a reporter the order carries must be one of the order's own pages
        crefs = [key for typ, key, _a, _b in r["refs"] if typ == "c"]
        keep_o = set()
        for o in cand_o:
            own = ocites[o]
            orep = {k.split(" ")[1] for k in own}
            if all(k in own or k.split(" ")[1] not in orep for k in crefs):
                keep_o.add(o)
        if cand_o and not keep_o:
            st["refs_disagree"] += 1
        cand_o = keep_o
        cand_o = {o for o in cand_o if oinfo[o][0] <= dn}
        if not cand_o:
            st["no_order"] += 1
            continue
        # --- the decision below: last citation group of the clause (after any earlier history phrase)
        pre_off = r["s0"]
        cut = 0
        snip = r["snip"]
        pre_len = r["p"][0] - pre_off
        for m in RX_PHRASE_IN_PRE.finditer(snip[:pre_len]):
            cut = m.end()
        tgt_c = set()
        for k, a, b in r["cites"]:
            if a - pre_off < cut:
                continue
            s = snip[a - pre_off:b - pre_off]
            for kk in r6cite.keys(s) if s else [k]:
                if kk in idx:
                    tgt_c.add(idx[kk])
                    break
        dock_toks = [d for d, a, b in r["docks"] if a - pre_off >= cut]
        res = collections.defaultdict(set)
        for o in cand_o:
            od, okind, ids, _t, _c = oinfo[o]
            if not ids:
                continue
            oo = M.ordinal(od)
            for t in tgt_c:
                ct = int(F.court[t])
                d = int(F.date[t])
                if ct in ids and d < od and 0 < oo - M.ordinal(d) <= MAXDAYS:
                    res[o].add((t, "cite"))
            for dt in dock_toks:
                for tok in D.docket_tokens(dt):
                    for ct in ids:
                        for t in dk_idx.get((ct, tok), ()):
                            d = int(F.date[t])
                            if d < od and 0 < oo - M.ordinal(d) <= MAXDAYS:
                                res[o].add((t, "ldock"))
        if not res:
            st["no_target"] += 1
            continue
        # caption tie-check (always): the order's caption and the decision below share a party-name token
        keep = {}
        for o, ts in res.items():
            ocap = " ".join(oinfo[o][4]) or oinfo[o][3]
            ot = set(M.toks(ocap))
            ok = {x for x in ts if ot & ttoks(x[0])}
            if ok:
                keep[o] = ok
        if not keep:
            st["caption_disagrees"] += 1
            continue
        if len(keep) != 1:
            st["several_orders"] += 1
            continue
        if len(res) > 1:
            how_o += "+cap"
        res = keep
        (o, ts), = res.items()
        tnodes = {t for t, _h in ts}
        if len(tnodes) != 1:
            st["several_targets"] += 1
            continue
        t = next(iter(tnodes))
        hows = "|".join(sorted({h for _t, h in ts}))
        votes[o][t].append((r["n"], how_o + ":" + hows, r["p"][0]))
        st["record_ok"] += 1
    out = []
    for o, tv in votes.items():
        if len(tv) != 1:
            st["order_conflict"] += 1
            continue
        (t, bl), = tv.items()
        out.append((o, t, len(bl), ";".join("%d@%d:%s" % (b, p, h) for b, h, p in bl[:6])))
        st["order_linked"] += 1
    out.sort()
    with open(os.path.join(WORK, "bridge_links.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("order\ttarget\tn_bridges\tbridges" + NL)
        for row in out:
            f.write("\t".join(str(x) for x in row) + NL)
    kc = collections.Counter(oinfo[o][1] for o, *_ in out)
    st2 = dict(st)
    st2["linked_by_kind"] = dict(kc)
    st2["linked_ge2013"] = sum(1 for o, *_ in out if oinfo[o][0] >= 20130101)
    json.dump(st2, open(os.path.join(WORK, "bridge_stats.json"), "w"), indent=1)
    print(st2)


if __name__ == "__main__":
    main()
