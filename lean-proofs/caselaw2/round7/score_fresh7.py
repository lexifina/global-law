"""Round 7 (DESIGN7 section 6, B3): the fresh-list scorer with two date views, side by side.

    python round7/score_fresh7.py --split dev|test --status <out/status.tsv> --label <name>
                                  [--findings <out/findings.tsv>] [--treatments <data/treatments.tsv>]
                                  [--view model|attributed|both] [--data <data dir>] [--out <dir>]
                                  [--write-status <path>]

Same key, same outcomes and same arguments as round5/gold_fresh/score_fresh.py (which this file imports and does not
change), plus:

  --view model       the model's own timeline (DESIGN5 R5-3). A recognised overruling (path `recognised`, actor Y,
                     W the later court that recognises it) is `unknown:recognisedLater` from date(Y) and
                     `neg:overruled` / `neg:abrogated` only from date(W). This view is score_fresh.py, number for number.
  --view attributed  reporting view "as attributed today": a status row `neg:overruled` / `neg:abrogated` of path
                     `recognised` and actor Y counts as negative from date(Y), date(Y) read from decisions2.tsv of the
                     variant's data folder. Concretely, per (node, issue, holding, actor) group of path-`recognised`
                     rows (any witness row W) that has such a negative row N (the earliest one):
                       - every `unknown:recognisedLater` row of the group that ends before N starts is read with N's
                         status (and class);
                       - the earliest of those rows and N starts at date(Y) (if it starts later than date(Y));
                     every other row is unchanged (partial scope, power unknown, other paths, other actors).
                     No status semantics change; it is a reading of the same status.tsv.
  --view both        (default) both, side by side. Neither replaces the other.
  --data DIR         folder holding decisions2.tsv (default: the --treatments folder, else
                     <status>/../../stage/<name>/, else caselaw-lean-2/data). Only the attributed view reads it.
  --out DIR          dev only: results folder (default round7/results/<label>/). A test run always writes to
                     round5/gold_fresh/sealed/results/ and appends ONE line to sealed/TEST_RUNS.log, as score_fresh.py.
  --write-status P   also write the attributed reading of the whole status.tsv to P (same columns, same row order;
                     only the rows the attributed view reads differently change). For other scorers that read
                     status.tsv on a date (e.g. round5/tests/score_holdout.py --status P).

Outcomes per gold pair (overruling Y, overruled X) are those of score_fresh.py: a (strict), a_date, a_kind, b, c
(lenient = a..c), d, e. Wilson 95% intervals. Dev outputs (in --out):
  fresh7_dev.json                        both views: recall tables, precision side, attribution counts, moves
  fresh7_dev.<view>.pairs.tsv            one row per gold pair (as score_fresh.py's .pairs.tsv)
  fresh7_dev.<view>.unlisted_sample.tsv  as score_fresh.py
  fresh7_dev.moves.tsv                   the pairs whose outcome differs between the views (dev only)
Test outputs: sealed/results/<label>.fresh7.json, .fresh7.<view>.pairs.tsv, .fresh7.<view>.unlisted_sample.tsv
(no moves list); stdout has counts only.
"""
import argparse
import collections
import datetime
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
GOLD = os.path.join(C2, "round5", "gold_fresh")
_spec = importlib.util.spec_from_file_location("score_fresh_r5", os.path.join(GOLD, "score_fresh.py"))
SF = importlib.util.module_from_spec(_spec)
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True     # no __pycache__ inside round5/gold_fresh
_spec.loader.exec_module(SF)
sys.dont_write_bytecode = _dwb

STRICT_KINDS, LENIENT, ORDER, RISK = SF.STRICT_KINDS, SF.LENIENT, SF.ORDER, SF.RISK
iint, table, rate, next_day, split_of, sha1_file = SF.iint, SF.table, SF.rate, SF.next_day, SF.split_of, SF.sha1_file
RECOG_PATH = "recognised"
RECOG_LATER = "unknown:recognisedLater"
VIEWS = ("model", "attributed")


# ---------------------------------------------------------------- status.tsv
def read_status(path):
    """(names, header_present, rows): rows are dicts with the line number `_i` (0 = first line of the file), for the
    rows any view can use: neg:* / unknown:* rows. The header rule is score_fresh.table's."""
    rows = []
    n = 0
    with open(path, encoding="utf-8") as f:
        first = f.readline()
        if not first:
            return SF.STATUS_COLS, False, rows, 0
        h = first.rstrip("\n").split("\t")
        if h[0] and not h[0].lstrip("-").isdigit() and h[0] in (SF.STATUS_COLS[0], "node", "finding", "id", "pair_id"):
            names, has_head, lines, start = h, True, [], 1
        else:
            names, has_head, lines, start = SF.STATUS_COLS, False, [first], 0

        def emit(i, line):
            r = dict(zip(names, line.rstrip("\n").split("\t")))
            st = r.get("status", "")
            if st.startswith("neg:") or st.startswith("unknown:"):
                r["_i"] = i
                rows.append(r)
        for line in lines:
            n += 1
            emit(0, line)
        for i, line in enumerate(f, start):
            n += 1
            emit(i, line)
    return names, has_head, rows, n


def node_dates(path, wanted):
    """node -> date (decisions2.tsv: node, court, date, ...; no header) for the nodes in `wanted`."""
    out = {}
    wb = {str(x).encode() for x in wanted}
    with open(path, "rb") as f:
        for raw in f:
            p = raw.split(b"\t", 3)
            if len(p) >= 3 and p[0] in wb and p[2].isdigit():
                out[int(p[0])] = int(p[2])
    return out


def find_decisions(a):
    cands = []
    if a.data:
        cands.append(a.data)
    if a.treatments:
        cands.append(os.path.dirname(os.path.abspath(a.treatments)))
    sd = os.path.dirname(os.path.abspath(a.status))
    cands.append(os.path.join(os.path.dirname(os.path.dirname(sd)), "stage", os.path.basename(sd)))
    cands.append(os.path.join(C2, "data"))
    for c in cands:
        p = os.path.join(c, "decisions2.tsv")
        if os.path.exists(p):
            return p
    sys.exit("attributed view: no decisions2.tsv found (give --data)")


def attribute(rows, decisions_path):
    """The attributed reading. rows: the neg/unknown rows of read_status (any node). Returns ({line: new row}, stats).
    Only rows of path `recognised` are looked at; a group with no neg:overruled / neg:abrogated row is unchanged."""
    # one group per (node, issue, holding, actor Y): the witness row is not part of the key, because several later
    # courts W may recognise the same overruling and the status row names whichever effect is in force (an
    # `unknown:recognisedLater` row from W1's row can precede the negative row from W2's row).
    groups = collections.defaultdict(list)
    for r in rows:
        if r.get("path") == RECOG_PATH:
            groups[(r.get("node"), r.get("issue"), r.get("holding"), r.get("actor"))].append(r)
    st = collections.Counter()
    st["recognised_rows"] = sum(len(g) for g in groups.values())
    st["groups"] = len(groups)
    need = set()
    for k, g in groups.items():
        negs = [r for r in g if r["status"] in STRICT_KINDS]
        if negs:
            y = iint(k[3])
            if y >= 0:
                need.add(y)
            for r in negs:
                w = r.get("witness_row", "").split(":")
                if len(w) == 5 and w[4].isdigit():
                    need.add(int(w[4]))
    dates = node_dates(decisions_path, need) if need else {}
    slots = {k[:3] for k, g in groups.items() if any(r["status"] in STRICT_KINDS for r in g)}
    by_slot = collections.defaultdict(list)
    for r in rows:
        s = (r.get("node"), r.get("issue"), r.get("holding"))
        if s in slots:
            by_slot[s].append(r)
    mods = {}
    for k, g in sorted(groups.items()):
        negs = [r for r in g if r["status"] in STRICT_KINDS]
        if not negs:
            if any(r["status"] == RECOG_LATER for r in g):
                st["groups_recognisedLater_without_neg_unchanged"] += 1
            continue
        st["groups_with_neg"] += 1
        whole = k[1] == "-"
        st["groups_with_neg_whole" if whole else "groups_with_neg_issue"] += 1
        n0 = min(negs, key=lambda r: (iint(r["from"], 0), r["_i"]))
        f0 = iint(n0["from"], 0)
        y = iint(k[3])
        dy = dates.get(y, 0)
        w = n0.get("witness_row", "").split(":")
        dw = dates.get(int(w[4]), 0) if len(w) == 5 and w[4].isdigit() else 0
        if dw and f0 not in (dw, next_day(dw)):
            st["neg_start_not_dateW"] += 1
        conv = []
        for r in g:
            if r["status"] == RECOG_LATER and iint(r["to"], 0) < f0:
                nr = dict(r)
                nr["status"] = n0["status"]
                nr["class"] = n0.get("class", nr.get("class"))
                mods[r["_i"]] = nr
                conv.append(nr)
        st["recognisedLater_rows_read_negative"] += len(conv)
        if not dy:
            st["dateY_unknown_unchanged_start"] += 1
            continue
        first = min(conv + [n0], key=lambda r: (iint(r["from"], 0), r["_i"]))
        ff = iint(first["from"], 0)
        if ff > dy:
            nr = dict(mods.get(first["_i"], first))
            nr["from"] = str(dy)
            mods[first["_i"]] = nr
            st["start_moved_to_dateY_" + ("after_recognisedLater_rows" if conv else "no_recognisedLater_row")] += 1
            # what the model shows on [date(Y), first start): another actor's negative, or something else
            gap = [r for r in by_slot.get(k[:3], ()) if r.get("actor") != k[3]
                   and iint(r["from"], 0) < ff and iint(r["to"], 0) >= dy]
            st["moved_gap_shows_" + ("other_actor_neg" if any(r["status"].startswith("neg:") for r in gap)
                                     else "other_unknown" if gap else "no_neg_or_unknown_row")] += 1
        elif ff == dy:
            st["start_already_dateY" + ("_via_recognisedLater_rows" if conv else "_dateY_eq_dateW")] += 1
        else:
            st["start_before_dateY_unchanged"] += 1
    st["rows_changed"] = len(mods)
    return mods, dict(sorted(st.items()))


def write_status(src, dst, names, has_head, mods):
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8", newline="\n") as o:
        for i, line in enumerate(f):
            if i in mods and not (has_head and i == 0):
                p = line.rstrip("\n").split("\t")
                r = mods[i]
                for j, nm in enumerate(names):
                    if j < len(p) and nm in r:
                        p[j] = r[nm]
                line = "\t".join(p) + "\n"
            o.write(line)


# ---------------------------------------------------------------- score_fresh.py's scoring, on a list of rows
def score_view(rows, gold, meta, gx, gpairs, risk, treat, split):
    """Exactly score_fresh.main's model-status, outcome and precision parts, on rows (file order)."""
    eff = collections.defaultdict(set)
    model_pairs = {}
    for r in rows:
        st = r.get("status", "")
        x = iint(r["node"])
        if x not in meta:
            continue
        y = iint(r.get("actor"))
        fr = iint(r.get("from"), 0)
        if x in gx:
            eff[x].add((st, fr, y, r.get("path", ""), int(r.get("issue", "-") == "-")))
        if st in STRICT_KINDS and y in meta:
            k = (y, x)
            if k not in model_pairs or fr < model_pairs[k][1]:
                model_pairs[k] = (st, fr)
    out_rows = [["pair_id", "outcome", "by_node", "target_node", "overruling_cite", "overruled_cite", "partial",
                 "implied", "sources", "model_status", "model_actor", "model_from", "actor_is_gold", "whole_decision",
                 "other_effects", "at_risk", "reader_rows"]]
    dims = collections.defaultdict(collections.Counter)
    outcome = {}
    for g in gold:
        y, x = iint(g["by_node"]), iint(g["target_node"])
        dy = meta[y][0]
        E = eff.get(x, set())
        neg = [e for e in E if e[0].startswith("neg:")]
        pick, outc = None, "e"
        cands = [("a", [e for e in neg if e[2] == y and e[0] in STRICT_KINDS and e[1] in (dy, next_day(dy))]),
                 ("a_date", [e for e in neg if e[2] == y and e[0] in STRICT_KINDS]),
                 ("a_kind", [e for e in neg if e[2] == y]),
                 ("b", neg),
                 ("c", [e for e in E if e[0].startswith("unknown:")])]
        for name, es in cands:
            if es:
                outc = name
                pick = sorted(es, key=lambda e: (-e[4], e[1], e[0]))[0]
                break
        rk = sorted(risk.get((y, x), ()))
        if outc == "e" and rk:
            outc = "d"
        outcome[g["pair_id"]] = (outc, pick)
        others = sorted({f"{e[0]}@{e[1]}by{e[2]}" for e in E if e != pick})[:6]
        out_rows.append([g["pair_id"], outc, y, x, g["overruling_cite"], g["overruled_cite"], g["partial"],
                         g["implied"], g["sources"], pick[0] if pick else "-", pick[2] if pick else "-",
                         pick[1] if pick else "-", int(bool(pick) and pick[2] == y), pick[4] if pick else "-",
                         ";".join(others) or "-", ";".join(rk) or "-", ";".join(sorted(treat.get((y, x), ()))) or "-"])
        keys = [("all", "all"), ("scope", "partial" if g["partial"] == "1" else "full"),
                ("express", "implied" if g["implied"] == "1" else "express"),
                ("scope_express", ("partial" if g["partial"] == "1" else "full") + "+"
                 + ("implied" if g["implied"] == "1" else "express")),
                ("n_sources", "1" if g["n_sources"] == "1" else "2+"),
                ("burned_crs", "inCRS" if g["in_crs2016"] == "1" or g["in_crs_current"] == "1" else "notInCRS"),
                ("era", "to1945" if dy < 19460101 else ("1946-1991" if dy < 19920101 else "1992on"))]
        keys += [("source", s) for s in g["sources"].split(",")]
        for k in keys:
            dims[k][outc] += 1
            if outc == "c" and pick[2] == y:
                dims[k]["c_goldActor"] += 1
    summary = {}
    for (dim, key), c in sorted(dims.items()):
        n = sum(c[o] for o in ORDER)
        summary.setdefault(dim, {})[key] = {"n": n, "outcomes": {o: c[o] for o in ORDER},
                                            "c_with_gold_actor": c["c_goldActor"],
                                            "strict": rate(c["a"], n),
                                            "lenient": rate(sum(c[o] for o in LENIENT), n)}
    half = {k: v for k, v in model_pairs.items() if split_of(meta[k[1]][1], k[1]) == split}
    cls = collections.Counter()
    unl = []
    for (y, x), (st, fr) in half.items():
        if meta[y][0] < meta[x][0]:
            c = "actorEarlierThanTarget"
        elif (y, x) in gpairs:
            c = "listed"
        elif x in gx:
            c = "targetListedOtherOverruler"
        else:
            c = "unlisted"
        cls[c] += 1
        if c != "listed":
            unl.append((hashlib.sha1(f"{y}:{x}".encode()).hexdigest(), c, y, x, st, fr))
    unl.sort()
    sample = [["class", "by_node", "overruling_cite", "overruling_name", "overruling_date", "target_node",
               "overruled_cite", "overruled_name", "overruled_date", "model_status", "model_from"]]
    for _, c, y, x, st, fr in unl[:150]:
        sample.append([c, y, meta[y][1], meta[y][2], meta[y][0], x, meta[x][1], meta[x][2], meta[x][0], st, fr])
    tot = sum(cls.values())
    precision = {"model_scotus_on_scotus_overruled_pairs_all": len(model_pairs),
                 "in_this_half": tot, "classes": dict(cls),
                 "listed_share": rate(cls["listed"], tot),
                 "distinct_targets_in_this_half": len({k[1] for k in half}),
                 "note": "unlisted = in no fresh list; the lists are incomplete, so this is not an error count"}
    return {"recall": summary, "precision_side": precision}, out_rows, sample, outcome, len(model_pairs), tot


def fmt_rate(v):
    w = v["wilson95"]
    return f"{v['rate']:.3f} [{w[0]:.3f},{w[1]:.3f}]" if v["rate"] is not None else "-"


def print_table(view, res, split, label, n_gold):
    summary = res["recall"]
    print(f"fresh gold, split={split}, label={label}, view={view}, pairs={n_gold}")
    print(f"{'dimension':<14}{'key':<26}{'n':>4}  " + " ".join(f"{o:>6}" for o in ORDER)
          + "   strict (95% CI)            lenient (95% CI)")
    for dim, d in summary.items():
        for key, v in d.items():
            print(f"{dim:<14}{key:<26}{v['n']:>4}  " + " ".join(f"{v['outcomes'][o]:>6}" for o in ORDER)
                  + f"   {fmt_rate(v['strict'])}      {fmt_rate(v['lenient'])}")
    p = res["precision_side"]
    print(f"precision side ({view} view, this half of the model's Supreme Court overrulings):",
          json.dumps(p["classes"]), f"of {p['in_this_half']}; all halves: {p['model_scotus_on_scotus_overruled_pairs_all']}")
    print()


def print_side_by_side(results):
    m, t = results["model"]["recall"], results["attributed"]["recall"]
    print("side by side (k/n, rate [Wilson 95%]); model = R5-3 timeline, attributed = recognised overrulings dated from Y")
    print(f"{'dimension':<14}{'key':<26}{'n':>4}  {'strict model':<28}{'strict attributed':<28}"
          f"{'lenient model':<28}{'lenient attributed':<28}")
    for dim, d in m.items():
        for key, v in d.items():
            w = t[dim][key]

            def cell(x):
                return f"{x['k']:>3} {fmt_rate(x)}"
            print(f"{dim:<14}{key:<26}{v['n']:>4}  {cell(v['strict']):<28}{cell(w['strict']):<28}"
                  f"{cell(v['lenient']):<28}{cell(w['lenient']):<28}")
    print()


def write_rows(path, rows_):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows_:
            f.write("\t".join(str(c) for c in r) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["dev", "test"])
    ap.add_argument("--status", required=True)
    ap.add_argument("--findings", help="default: findings.tsv beside --status")
    ap.add_argument("--treatments", help="optional data/treatments.tsv: adds what the reader extracted for each pair")
    ap.add_argument("--label", required=True)
    ap.add_argument("--view", choices=["model", "attributed", "both"], default="both")
    ap.add_argument("--data", help="folder of decisions2.tsv (attributed view)")
    ap.add_argument("--out", help="dev only: results folder (default round7/results/<label>/)")
    ap.add_argument("--write-status", help="write the attributed reading of status.tsv here")
    a = ap.parse_args(argv)
    if not all(ch.isalnum() or ch in "-_." for ch in a.label):
        sys.exit("--label: letters, digits, - _ . only")
    if a.split == "test" and a.out:
        sys.exit("--out is for dev runs; a test run writes to the sealed results folder")
    views = VIEWS if a.view == "both" else (a.view,)
    if a.split == "dev":
        gold_path = os.path.join(GOLD, "dev", "dev.tsv")
        res_dir = a.out or os.path.join(HERE, "results", a.label)
        stem = "fresh7_dev"
    else:
        gold_path = os.path.join(GOLD, "sealed", "test.tsv")
        res_dir = os.path.join(GOLD, "sealed", "results")
        stem = a.label + ".fresh7"
    gold = list(table(gold_path, ["pair_id"]))
    meta = {}
    for r in table(os.path.join(GOLD, "work", "scotus_meta.tsv"), ["node"]):
        meta[int(r["node"])] = (int(r["date"]), r["us_cite"], r["name"], r["type"])
    gx = {iint(g["target_node"]) for g in gold}
    gpairs = {(iint(g["by_node"]), iint(g["target_node"])) for g in gold}

    names, has_head, rows, nrows = read_status(a.status)
    # ---- findings (atRisk rows linking X and Y): as score_fresh.py
    fpath = a.findings or os.path.join(os.path.dirname(os.path.abspath(a.status)), "findings.tsv")
    risk = collections.defaultdict(set)
    if os.path.exists(fpath):
        for r in table(fpath, SF.FIND_COLS):
            if r.get("finding") != "atRisk" or not r.get("detail", "").startswith(RISK):
                continue
            c1, c2 = iint(r["citing"]), iint(r["cited"])
            if (c1, c2) in gpairs:
                risk[(c1, c2)].add(r["detail"])
            if (c2, c1) in gpairs:
                risk[(c2, c1)].add(r["detail"])
    else:
        fpath = None
    treat = collections.defaultdict(set)
    if a.treatments:
        for r in table(a.treatments, SF.TREAT_COLS):
            k = (iint(r["by_node"]), iint(r["target_node"]))
            if k in gpairs:
                treat[k].add(f"{r['kind']}:{r['scope']}:explicit={r['explicit']}"
                             + (":implicitTier" if r.get("reader", "").endswith(":implicit") else ""))

    view_rows = {"model": rows}
    attribution, dpath = None, None
    if "attributed" in views or a.write_status:
        dpath = find_decisions(a)
        mods, attribution = attribute(rows, dpath)
        view_rows["attributed"] = [mods.get(r["_i"], r) for r in rows]
        if a.write_status:
            write_status(a.status, a.write_status, names, has_head, mods)
    results, outs = {}, {}
    for v in views:
        res, out_rows, sample, outcome, _, _ = score_view(view_rows[v], gold, meta, gx, gpairs, risk, treat, a.split)
        results[v] = res
        outs[v] = (out_rows, sample, outcome)

    moves, move_rows = None, None
    if len(views) == 2:
        moves = collections.Counter()
        move_rows = [["pair_id", "by_node", "target_node", "overruling_cite", "overruled_cite", "overruling_date",
                      "model_outcome", "model_status", "model_from", "attributed_outcome", "attributed_status",
                      "attributed_from"]]
        om, oa = outs["model"][2], outs["attributed"][2]
        for g in gold:
            (m, pm), (t, pt) = om[g["pair_id"]], oa[g["pair_id"]]
            if m != t:
                moves[f"{m}->{t}"] += 1
                move_rows.append([g["pair_id"], g["by_node"], g["target_node"], g["overruling_cite"],
                                  g["overruled_cite"], meta[iint(g["by_node"])][0], m, pm[0] if pm else "-",
                                  pm[1] if pm else "-", t, pt[0] if pt else "-", pt[1] if pt else "-"])
        moves = dict(sorted(moves.items()))

    res = {"label": a.label, "split": a.split, "gold_pairs": len(gold), "scorer": "round7/score_fresh7.py",
           "views": results,
           "inputs": {"status": os.path.abspath(a.status), "status_rows": nrows, "findings": fpath,
                      "treatments": os.path.abspath(a.treatments) if a.treatments else None,
                      "status_sha1": sha1_file(a.status), "decisions2": dpath},
           "attribution": attribution, "moves": moves}
    os.makedirs(res_dir, exist_ok=True)
    blob = json.dumps(res, indent=1, sort_keys=True)
    with open(os.path.join(res_dir, stem + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(blob + "\n")
    for v in views:
        write_rows(os.path.join(res_dir, f"{stem}.{v}.pairs.tsv"), outs[v][0])
        write_rows(os.path.join(res_dir, f"{stem}.{v}.unlisted_sample.tsv"), outs[v][1])
    if a.split == "dev" and move_rows is not None:
        write_rows(os.path.join(res_dir, stem + ".moves.tsv"), move_rows)
    rh = hashlib.sha1(blob.encode("utf-8")).hexdigest()
    if a.split == "test":
        with open(os.path.join(GOLD, "sealed", "TEST_RUNS.log"), "a", encoding="utf-8", newline="\n") as f:
            f.write("\t".join([datetime.datetime.now().astimezone().isoformat(timespec="seconds"), a.label,
                               " ".join(sys.argv[1:] if argv is None else argv), "result_sha1=" + rh,
                               "status_sha1=" + res["inputs"]["status_sha1"],
                               "scorer=round7/score_fresh7.py view=" + a.view]) + "\n")
    # ---- stdout: counts only
    print(f"fresh gold (round 7, two date views), split={a.split}, label={a.label}, pairs={len(gold)}, "
          f"result_sha1={rh}")
    print()
    for v in views:
        print_table(v, results[v], a.split, a.label, len(gold))
    if len(views) == 2:
        print_side_by_side(results)
        print("moves model -> attributed:", json.dumps(moves))
    if attribution is not None:
        print("attributed reading of status.tsv:", json.dumps(attribution))
    if a.write_status:
        print("attributed status written:", os.path.abspath(a.write_status))
    print("written:", os.path.join(res_dir, stem + ".json"))


if __name__ == "__main__":
    main()
