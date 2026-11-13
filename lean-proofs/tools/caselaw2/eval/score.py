"""Score the caselaw-lean-2 Lean run against the held-out gold.

    python tools/caselaw2/eval/score.py [--out <lean out dir>] [--data <data dir>] [--results <dir>] [--v1]

Reads (paths default to ~/Documents/us-caselaw-lean-work/caselaw-lean-2/{out,data,gold}):
  out/status.tsv    node, issue, holding, from, to, status, kind, by, conduct_from, firm   (LEAN.md, planned)
  out/findings.tsv  kind, citing, cited, extra, firm
  out/certs.tsv     file, id, ok|reason
  out/splits.tsv    issue, court1, court2, answer1, answer2, date
  data/treatments.tsv, history.tsv, decisions2.tsv, courts2.tsv, issues.tsv   (SCHEMA.md)
  gold/reports_typed.tsv, reports_typed_pairs.tsv, scdb.tsv, crs_overruled.tsv, splits_resolved.tsv
A file with a header line whose first field is not a number is read by its header names; otherwise by the column
order above. Missing inputs leave their section "pending".

--v1 scores v1 (lean-in-v3 acts + lean-out-v3 validity) on the same gold, as the baseline: every valid v1 act is an
admitted whole-decision overruling.

Writes eval/results.json (or eval/results_v1.json) and eval/tables/*.tsv, and prints a summary.
"""
import argparse, array, collections, json, os, re, sys

W = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(W, "caselaw-lean-2")
NEG_KINDS = {"overruled", "disapproved", "recededFrom", "abrogated"}            # later-case kinds that change status
HIST_KINDS = {"reversed", "vacated"}
SUP = "supersededByEnactment"
GOOD = {"good", "goodLaw", "ok", "binding", "-", ""}
V1 = {"notes_named": 51895, "agree": 13842, "another": 1503, "none": 36550, "agree_rate": 0.27,
      "blind_agreements_held": "36/37 (97%)", "blind_express_found": "36/79 (about half)",
      "heldout_acts_overruling": "94/120", "heldout_acts_right_target": "79/120",
      "crs2016_express_found": "70/236 (30%)", "source": "blog draft sections 4-7; PROGRESS.md"}


def rows(path, cols):
    """Rows of a TSV as dicts keyed by `cols` (or by its own header)."""
    if not os.path.exists(path):
        return None
    out = []
    with open(path, encoding="utf-8") as f:
        first = f.readline()
        if not first:
            return out
        h = first.rstrip("\n").split("\t")
        if h and h[0] and re.fullmatch(r"[A-Za-z_]+", h[0]):
            names = h
        else:
            names = cols
            out.append(dict(zip(names, h)))
        for line in f:
            out.append(dict(zip(names, line.rstrip("\n").split("\t"))))
    return out


def iint(x, d=-1):
    try:
        return int(x)
    except (TypeError, ValueError):
        return d


class Meta:
    """Court, date and system of every node: decisions2/courts2 when present, else v1's lean-in-v3."""

    def __init__(self, data):
        self.court = array.array("i")
        self.date = array.array("I")
        d2 = os.path.join(data, "decisions2.tsv")
        src = d2 if os.path.exists(d2) else os.path.join(W, "lean-in-v3", "decisions.tsv")
        for line in open(src, encoding="utf-8"):
            f = line.split("\t")
            if not f[0].isdigit():
                continue
            i = int(f[0])
            while len(self.court) < i:
                self.court.append(-1)
                self.date.append(0)
            self.court.append(int(f[1]))
            self.date.append(int(f[2]))
        self.sys, self.tier, self.circ = {}, {}, {}
        c2 = os.path.join(data, "courts2.tsv")
        if os.path.exists(c2) and src == d2:
            for line in open(c2, encoding="utf-8"):
                f = line.rstrip("\n").split("\t")
                if f[0].lstrip("-").isdigit():
                    c = int(f[0])
                    self.sys[c], self.tier[c], self.circ[c] = int(f[4]), f[5], iint(f[7], 0)
        else:
            for line in open(os.path.join(W, "lean-in-v3", "courts.tsv"), encoding="utf-8"):
                i, s, t, c = line.rstrip("\n").split("\t")
                self.sys[int(i)], self.tier[int(i)], self.circ[int(i)] = int(s), t, int(c)
        self.sysname = {0: "federal"}
        for line in open(os.path.join(W, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if f[5] == "L" and int(f[4]) not in self.sysname:
                self.sysname[int(f[4])] = re.sub(r"\s+(Supreme Court|Court of Appeals|Supreme Judicial Court).*", "",
                                                 f[1])

    def system(self, n):
        c = self.court[n] if 0 <= n < len(self.court) else -1
        s = self.sys.get(c, 999)
        return self.sysname.get(s, f"system{s}") if s != 999 else "unknown"

    def decade(self, n):
        d = self.date[n] if 0 <= n < len(self.date) else 0
        return f"{d // 100000 * 10}s" if d else "unknown"

    def is_scotus(self, n):
        c = self.court[n] if 0 <= n < len(self.court) else -1
        return self.sys.get(c) == 0 and self.tier.get(c) == "L"


def ratio(a, b):
    return round(a / b, 4) if b else None


def load_model(a, meta):
    """Admitted treatments {(by, target): (kind, scope)}, status {target: [(from, kind, by, scope)]},
    cert rejection reasons, all treatment rows."""
    if a.v1:
        acts = [l.rstrip("\n").split("\t") for l in open(os.path.join(W, "lean-out-v3", "00.acts.tsv"),
                                                           encoding="utf-8")]
        adm = {}
        for y, x, v in acts:
            if v == "1":
                adm[(int(y), int(x))] = ("overruled", "all")
        status = collections.defaultdict(list)
        for (y, x), (k, sc) in adm.items():
            status[x].append((meta.date[y], k, y, sc))
        rej = collections.Counter("valid" if v == "1" else "noAuthority" for _, _, v in acts)
        return adm, status, rej, None, {"treatments": len(acts), "admitted": len(adm)}
    tr = rows(os.path.join(a.data, "treatments.tsv"),
              ["id", "by_node", "target_node", "date", "kind", "scope", "temporal", "explicit", "text_sha", "start",
               "end", "quote", "target_evidence", "part", "reader", "confidence"])
    hi = rows(os.path.join(a.data, "history.tsv"),
              ["id", "target_node", "by_node", "date", "kind", "scope", "text_sha", "start", "end", "quote",
               "target_evidence", "part", "src"])
    certs = rows(os.path.join(a.out, "certs.tsv"), ["file", "id", "result"])
    st = rows(os.path.join(a.out, "status.tsv"),
              ["node", "issue", "holding", "from", "to", "status", "kind", "by", "conduct_from", "firm"])
    if tr is None and st is None:
        return None, None, None, None, {"pending": "data/treatments.tsv and out/status.tsv not yet written"}
    ok = {}
    rej = collections.Counter()
    if certs is not None:
        for c in certs:
            res = c.get("result_all") or c.get("result") or c.get("ok") or c.get("status") or ""
            f = os.path.basename(c.get("table") or c.get("file") or "treatments").replace(".tsv", "").rstrip("s") + "s"
            ok[(f, c.get("id"))] = res
            rej[(f, res.split(":")[0] if res != "ok" else "ok")] += 1
    adm = {}
    for r in tr or []:
        res = ok.get(("treatments", r["id"]), "ok" if certs is None else "missing")
        # round 2: the implicit tier (explicit = 0, reader `...:implicit`, later-court notes) is never an admitted
        # overruling here: it is left out of the recall and precision tables and reported by implicit_tier()
        if r.get("reader", "").endswith(":implicit"):
            continue
        if res == "ok" and r.get("explicit", "1") == "1" and r["kind"] in NEG_KINDS | {SUP}:
            adm[(iint(r["by_node"]), iint(r["target_node"]))] = (r["kind"], r["scope"])
    status = collections.defaultdict(list)
    if st is not None:
        for r in st:
            if r.get("status", "") not in GOOD:
                status[iint(r["node"])].append((iint(r.get("from"), 0), r.get("kind") or r.get("class") or r.get("status"),
                                                iint(r.get("by") or r.get("actor")), r.get("issue", "all")))
    else:  # no Lean status yet: the admitted treatments and history rows stand in for it
        for (y, x), (k, sc) in adm.items():
            status[x].append((meta.date[y] if 0 <= y < len(meta.date) else 0, k, y, sc))
    for r in hi or []:
        if r["kind"] in HIST_KINDS and ok.get(("history", r["id"]), "ok" if certs is None else "missing") == "ok":
            if st is None:
                status[iint(r["target_node"])].append((iint(r["date"], 0), r["kind"], iint(r["by_node"]), r["scope"]))
    info = {"treatments": len(tr or []), "admitted": len(adm), "history": len(hi or []),
            "status_rows": len(st) if st is not None else "pending (using admitted treatments)",
            "certs": len(certs) if certs is not None else "pending"}
    return adm, status, rej, tr, info


def score_reports(gold, adm, status, meta, tables):
    """Recall of later notes by Lean status (v1's three outcomes), per kind/scope/system/decade, and precision of the
    admitted treatments against the notes."""
    pairs = rows(os.path.join(gold, "reports_typed_pairs.tsv"), [])
    if pairs is None:
        return {"pending": "gold/reports_typed_pairs.tsv"}
    fam = {"overruled": "neg", "disapproved": "neg", "recededFrom": "neg", "abrogated": "neg",
           "reversed": "hist", "vacated": "hist", SUP: "sup"}
    res = collections.Counter()
    by_dim = collections.defaultdict(collections.Counter)
    noted_by = collections.defaultdict(set)   # target -> treating nodes named by notes (any negative kind)
    noted_any = set()
    for p in pairs:
        x, k, b, sc = iint(p["target_node"]), p["kind"], iint(p["by_node"]), p["scope"]
        noted_any.add((x, fam.get(k)))
        if b >= 0:
            noted_by[x].add(b)
        if b < 0 or fam.get(k) not in ("neg", "hist"):
            continue
        fd = iint(p["first_note_date"], 99999999)
        evs = [e for e in status.get(x, []) if e[0] <= fd]
        if any(e[2] == b for e in evs):
            v = "agree"
        elif evs:
            v = "another"
        else:
            v = "none"
        res[(k, sc, v)] += 1
        for dim, key in (("kind", k), ("scope", f"{k}:{sc}"), ("system", meta.system(x)), ("decade", meta.decade(b))):
            by_dim[dim][(key, v)] += 1
    recall = {}
    for k in sorted({k for k, _, _ in res}):
        n = sum(c for (kk, _, _), c in res.items() if kk == k)
        a_ = sum(c for (kk, _, v), c in res.items() if kk == k and v == "agree")
        o_ = sum(c for (kk, _, v), c in res.items() if kk == k and v == "another")
        recall[k] = {"notes_named": n, "agree": a_, "another": o_, "none": n - a_ - o_, "agree_rate": ratio(a_, n)}
        for sc in ("all", "partialUnknown", "otherGrounds"):
            m = sum(c for (kk, s, _), c in res.items() if kk == k and s == sc)
            ag = res[(k, sc, "agree")]
            recall[k][f"scope:{sc}"] = f"{ag}/{m}"
    for dim, cnt in by_dim.items():
        keys = sorted({k for k, _ in cnt})
        tables[f"recall_by_{dim}"] = [["key", "notes", "agree", "another", "none", "agree_rate"]] + [
            [k, sum(cnt[(k, v)] for v in ("agree", "another", "none")), cnt[(k, "agree")], cnt[(k, "another")],
             cnt[(k, "none")], ratio(cnt[(k, "agree")], sum(cnt[(k, v)] for v in ("agree", "another", "none")))]
            for k in keys]
    # precision: admitted treatments whose target has a note naming the same treating decision
    prec = collections.Counter()
    pdim = collections.defaultdict(collections.Counter)
    for (y, x), (k, sc) in adm.items():
        if y in noted_by.get(x, ()):
            v = "noteNamesSameBy"
        elif (x, "neg") in noted_any or (x, "sup") in noted_any:
            v = "noteOtherOrUnnamed"
        else:
            v = "noNote"
        prec[(k, sc, v)] += 1
        for dim, key in (("kind", k), ("scope", f"{k}:{sc}"), ("system", meta.system(x)), ("decade", meta.decade(y))):
            pdim[dim][(key, v)] += 1
    precision = {}
    for k in sorted({k for k, _, _ in prec}):
        n = sum(c for (kk, _, _), c in prec.items() if kk == k)
        same = sum(c for (kk, _, v), c in prec.items() if kk == k and v == "noteNamesSameBy")
        other = sum(c for (kk, _, v), c in prec.items() if kk == k and v == "noteOtherOrUnnamed")
        precision[k] = {"admitted": n, "noteNamesSameBy": same, "noteOtherOrUnnamed": other,
                        "noNote": n - same - other, "confirmed_rate": ratio(same, n),
                        "confirmed_rate_among_noted": ratio(same, same + other)}
    for dim, cnt in pdim.items():
        keys = sorted({k for k, _ in cnt})
        vs = ("noteNamesSameBy", "noteOtherOrUnnamed", "noNote")
        tables[f"precision_by_{dim}"] = [["key", "admitted", *vs, "confirmed_rate"]] + [
            [k, sum(cnt[(k, v)] for v in vs), *(cnt[(k, v)] for v in vs),
             ratio(cnt[(k, "noteNamesSameBy")], sum(cnt[(k, v)] for v in vs))] for k in keys]
    return {"recall_of_notes": recall, "precision_of_admitted": precision}


def score_scdb_crs(gold, adm, meta):
    out = {}
    sc = rows(os.path.join(gold, "scdb.tsv"), [])
    if sc is not None:
        flagged = {iint(r["node"]) for r in sc if r["precedentAlteration"] == "1" and iint(r["node"]) >= 0}
        allsc = {iint(r["node"]) for r in sc if iint(r["node"]) >= 0}
        acting = {y for (y, x) in adm if y in allsc and meta.is_scotus(x)}
        out["scdb"] = {"flagged_decisions": len(flagged),
                       "flagged_with_admitted_overruling": len(flagged & acting),
                       "recall": ratio(len(flagged & acting), len(flagged)),
                       "scotus_decisions_with_admitted_overruling_of_scotus": len(acting),
                       "of_which_flagged": len(acting & flagged), "precision": ratio(len(acting & flagged), len(acting)),
                       "unflagged_examples": sorted(acting - flagged)[:25]}
    cr = rows(os.path.join(gold, "crs_overruled.tsv"), [])
    if cr is not None:
        res = {}
        for name, sel in (("current_table", lambda r: r["in_current"] == "1"),
                          ("2016_express", lambda r: r["in_2016"] == "1" and r["expressly_2016"] == "1"),
                          ("2016_all", lambda r: r["in_2016"] == "1")):
            pr = [(iint(r["by_node"]), iint(r["target_node"])) for r in cr if sel(r)]
            res_ = [p for p in pr if p[0] >= 0 and p[1] >= 0]
            hit = [p for p in res_ if p in adm]
            res[name] = {"pairs": len(pr), "resolved": len(res_), "found": len(hit), "recall": ratio(len(hit), len(res_))}
        crs_pairs = {(iint(r["by_node"]), iint(r["target_node"])) for r in cr}
        sc_adm = [p for p in adm if meta.is_scotus(p[0]) and meta.is_scotus(p[1])]
        res["admitted_scotus_on_scotus"] = len(sc_adm)
        res["of_which_in_crs"] = sum(p in crs_pairs for p in sc_adm)
        out["crs"] = res
    return out


def implicit_tier(a, tr, certs_ok):
    """Round 2: rows of the implicit tier (explicit = 0; evidence = a later decision of the overruling court). Row id
    `ti:<stating decision>:<target>:<offset>:<overruling decision>`. Counted apart from every other table."""
    rows_ = [r for r in tr or [] if r.get("reader", "").endswith(":implicit")]
    if not rows_:
        return {"rows": 0}
    out = {"rows": len(rows_), "by_kind": dict(collections.Counter(r["kind"] for r in rows_)),
           "by_cert": dict(collections.Counter(certs_ok.get(r["id"], "missing") for r in rows_))}
    pairs = set()
    for r in rows_:
        if certs_ok.get(r["id"], "ok") == "ok":
            pairs.add((iint(r["id"].rsplit(":", 1)[-1]), iint(r["target_node"])))
    cr = rows(os.path.join(a.gold, "crs_overruled.tsv"), [])
    if cr is not None:
        gp = {(iint(r["by_node"]), iint(r["target_node"])) for r in cr}
        out["pairs_in_crs_any_edition"] = len(pairs & gp)
    out["note"] = "atRisk only; not in recall_of_notes, precision_of_admitted, scdb or crs"
    return out


def score_splits(a, gold, meta, tables):
    g = rows(os.path.join(gold, "splits_resolved.tsv"), [])
    sp = rows(os.path.join(a.out, "splits.tsv"), ["issue", "court1", "court2", "answer1", "answer2", "date"])
    iss = rows(os.path.join(a.data, "issues.tsv"), ["issue_key", "label", "domain", "usc", "question", "src"])
    if g is None:
        return {"pending": "gold/splits_resolved.tsv"}
    gs = [r for r in g if r["statutory"] == "1"]
    hc = [r for r in gs if "conflictLanguage" in r["src"]]
    base = {"gold_statutory": len(gs), "gold_statutory_conflict_language": len(hc)}
    if sp is None or iss is None:
        base["pending"] = "out/splits.tsv and data/issues.tsv"
        return base
    usc_of = {r["issue_key"]: r["usc"] for r in iss}

    def sect(u):
        return re.sub(r"\(.*$", "", u or "-")
    found = collections.defaultdict(list)
    first_split = {}  # issue -> first split date (round 3: honest recall)
    for r in sp:
        u = usc_of.get(r["issue"], "-")
        if u == "-":
            continue
        c1, c2 = iint(r["court1"]), iint(r["court2"])
        if "date" in r:
            sd = iint(r["date"], 0)
        else:  # the split arises once both sides have held: max over sides of each side's earliest holding
            def side(h):
                ds = [meta.date[int(m.group(1))] for x in (h or "").split(",")
                      for m in [re.match(r"^[A-Za-z]?(\d+)\.", x)] if m and int(m.group(1)) < len(meta.date)]
                return min(ds) if ds else 0
            sd = max(side(r.get("holdings1")), side(r.get("holdings2")))
        if r.get("kind", "split") != "split" and r.get("court2", "-") == "-":
            continue  # intra-court conflicts are not circuit splits
        found[sect(u)].append((sd, {meta.circ.get(c1, 0), meta.circ.get(c2, 0)}, u, r["issue"]))
        first_split[r["issue"]] = min(first_split.get(r["issue"], 99999999), sd)
    res = collections.Counter()
    after = 0
    rowsout = [["scotus_node", "date", "usc", "circuits", "verdict"]]
    for r in gs:
        d, u = iint(r["date"], 0), r["usc"]
        circs = {int(c) for c in r["circuits"].split(",") if c.isdigit()}
        cand = [f for f in found.get(sect(u), []) if f[0] < d]
        after += sum(1 for f in found.get(sect(u), []) if f[0] >= d)
        if any(f[2] == u for f in cand) and any(len(f[1] & circs) >= 2 for f in cand):
            v = "subsection+circuits"
        elif any(len(f[1] & circs) >= 2 for f in cand):
            v = "section+circuits"
        elif cand:
            v = "section"
        else:
            v = "missed"
        res[v] += 1
        res[(v, "hc")] += "conflictLanguage" in r["src"]
        rowsout.append([r["node"], d, u, r["circuits"], v])
    tables["splits_recall"] = rowsout
    n = len(gs)
    base.update({k: v for k, v in res.items() if isinstance(k, str)})
    base["recall_section"] = ratio(n - res["missed"], n)
    base["recall_section_hc"] = ratio(len(hc) - res[("missed", "hc")], len(hc))
    base["splits_detected_on_or_after_resolution"] = after
    base["splits_rows"] = len(sp)
    try:  # round 3, additive: recall counted only where the gold row's own conflict decisions are in the split question
        base.update(splits_honest(a, gs, first_split))
    except Exception as e:
        base["honest_error"] = repr(e)[:160]
    return base


def splits_honest(a, gs, first_split):
    """Honest split recall. Denominator: statutory gold rows with at least one conflict decision (conflict_nodes).
    honest_any: a split question, first split before the resolution date, has a holding of one of the row's conflict
        decisions (the round-2 'node level' measure: 25/464 -> 28/464).
    honest_opposite: the row's conflict decisions are holdings on BOTH sides (opposite answers) of one such question.
    Section-level hits that are neither are coincidental (same section, another question)."""
    by = collections.defaultdict(lambda: collections.defaultdict(set))  # issue -> answer -> nodes
    with open(os.path.join(a.data, "holdings.tsv"), encoding="utf-8") as fh:
        for line in fh:
            f = line.split("	", 5)
            if f[2] in first_split and f[4] in ("yes", "no") and f[1].isdigit():
                by[f[2]][f[4]].add(int(f[1]))
    tot = any_ = opp = 0
    for r in gs:
        cn = {int(x) for x in r["conflict_nodes"].split(",") if x.isdigit()}
        if not cn:
            continue
        tot += 1
        d = iint(r["date"], 0)
        ks = [k for k in by if first_split[k] < d]
        any_ += any((by[k]["yes"] | by[k]["no"]) & cn for k in ks)
        opp += any((by[k]["yes"] & cn) and (by[k]["no"] & cn) for k in ks)
    return {"honest_gold_rows_with_conflict_decisions": tot, "honest_any": any_, "honest_opposite": opp,
            "honest_recall_any": ratio(any_, tot), "honest_recall_opposite": ratio(opp, tot)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(C2, "out"))
    ap.add_argument("--data", default=os.path.join(C2, "data"))
    ap.add_argument("--gold", default=os.path.join(C2, "gold"))
    ap.add_argument("--v1", action="store_true")
    ap.add_argument("--results", default=os.path.join(C2, "eval"),
                    help="directory for results.json and tables/ (default: caselaw-lean-2/eval)")
    a = ap.parse_args()
    meta = Meta(a.data if not a.v1 else "/nonexistent")
    adm, status, rej, tr, info = load_model(a, meta)
    tables = {}
    res = {"model": "v1 (lean-out-v3)" if a.v1 else "caselaw-lean-2", "inputs": info, "v1_published": V1}
    if adm is not None:
        res["reports"] = score_reports(a.gold, adm, status, meta, tables)
        res.update(score_scdb_crs(a.gold, adm, meta))
        res["cert_reasons"] = {f"{f}:{r}": n for (f, r), n in rej.items()} if rej and not a.v1 else dict(rej or {})
        if not a.v1:
            cok = {}
            cf = rows(os.path.join(a.out, "certs.tsv"), ["file", "id", "result"])
            for c in cf or []:
                if (c.get("table") or c.get("file") or "").startswith("treatment"):
                    cok[c.get("id")] = c.get("result_all") or c.get("result") or ""
            res["implicit_tier"] = implicit_tier(a, tr, cok)
    if not a.v1:
        res["splits"] = score_splits(a, a.gold, meta, tables)
        fi = rows(os.path.join(a.out, "findings.tsv"), ["kind", "citing", "cited", "extra", "firm"])
        res["findings"] = dict(collections.Counter(r.get("kind") or r.get("finding") for r in fi)) if fi is not None else "pending"
    ed = a.results
    os.makedirs(os.path.join(ed, "tables"), exist_ok=True)
    sfx = "_v1" if a.v1 else ""
    json.dump(res, open(os.path.join(ed, f"results{sfx}.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              default=str)
    for k, t in tables.items():
        with open(os.path.join(ed, "tables", f"{k}{sfx}.tsv"), "w", encoding="utf-8", newline="\n") as f:
            for r in t:
                f.write("\t".join(str(c) for c in r) + "\n")
    print(json.dumps(res, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
