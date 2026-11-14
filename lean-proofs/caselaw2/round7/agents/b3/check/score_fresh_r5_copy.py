"""Score a caselaw-lean-2 run against the FRESH key of overruled Supreme Court decisions (round 5).

    python round5/gold_fresh/score_fresh.py --split dev|test --status <out/status.tsv> --label <name>
                                            [--findings <out/findings.tsv>] [--treatments <data/treatments.tsv>]

The key is built by build_gold.py (see GOLD_FRESH.md). `dev` reads dev/dev.tsv; `test` reads sealed/test.tsv and EVERY
test run appends one line (timestamp, label, arguments, result hash) to sealed/TEST_RUNS.log. Model builders use dev only.

For each gold pair (overruling Y, overruled X) the model's rows for X in status.tsv give one outcome:
  a       X is neg:overruled or neg:abrogated, actor = Y, from = date of Y (or the next day)          STRICT hit
  a_date  as a, but the status starts on another date (e.g. a prospective overruling)
  a_kind  actor = Y but another negative kind (neg:vacated, neg:reversed, neg:superseded ...)
  b       X is negative (any neg:*) by some other actor
  c       X is unknown:* (partial scope / power unknown) and never negative
          (`c_with_gold_actor` in the JSON: how many of these name Y as the actor)
  d       no status effect, but findings.tsv has an atRisk row linking X and Y
          (inferredRejection, soft:, claim:, contraryBinding:)
  e       nothing
Recall: strict = a; lenient = a, a_date, a_kind, b, c. Wilson 95% intervals. Reported overall, full vs partial gold rows,
implied vs express (as the source says), by source, by number of sources, and by presence in the burned CRS table.

Precision side ("unlisted", not "wrong": the lists are incomplete): Supreme Court decisions the model marks
neg:overruled / neg:abrogated with a Supreme Court actor. Each such decision belongs to the dev or test half by the same
hash of its U.S. citation that split the key, so a dev run looks only at the dev half of the model's output and reveals
nothing about the sealed pairs. A model pair is `listed` (same pair in the key), `targetListedOtherOverruler`, or
`unlisted`.

Outputs: <dev|sealed>/results/<label>.json, .pairs.tsv, .unlisted_sample.tsv; a summary on stdout (counts only).
"""
import argparse, collections, datetime, hashlib, json, math, os, sys

HERE = r"~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/gold_fresh"
C2 = os.path.dirname(os.path.dirname(HERE))
STRICT_KINDS = {"neg:overruled", "neg:abrogated"}
LENIENT = ("a", "a_date", "a_kind", "b", "c")
ORDER = ("a", "a_date", "a_kind", "b", "c", "d", "e")
RISK = ("inferredRejection", "soft:", "claim:", "contraryBinding")
STATUS_COLS = ["node", "issue", "holding", "from", "to", "status", "class", "firm", "witness_row", "actor", "path"]
FIND_COLS = ["finding", "citing", "cited", "issue", "detail", "firm", "path"]
TREAT_COLS = ["id", "by_node", "target_node", "date", "kind", "scope", "temporal", "explicit", "text_sha", "start",
              "end", "quote", "target_evidence", "part", "reader", "confidence"]


def split_of(cite, node=None):
    key = cite if cite and cite != "-" else f"node:{node}"
    return "dev" if int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % 2 == 0 else "test"


def iint(x, d=-1):
    try:
        return int(x)
    except (TypeError, ValueError):
        return d


def table(path, cols):
    """Yield dict rows; a first line whose first field is a column name is a header."""
    with open(path, encoding="utf-8") as f:
        first = f.readline()
        if not first:
            return
        h = first.rstrip("\n").split("\t")
        if h[0] and not h[0].lstrip("-").isdigit() and h[0] in (cols[0], "node", "finding", "id", "pair_id"):
            names = h
        else:
            names = cols
            yield dict(zip(names, h))
        for line in f:
            yield dict(zip(names, line.rstrip("\n").split("\t")))


def wilson(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def next_day(d):
    try:
        t = datetime.date(d // 10000, d // 100 % 100, d % 100) + datetime.timedelta(days=1)
        return t.year * 10000 + t.month * 100 + t.day
    except ValueError:
        return d + 1


def rate(k, n):
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "wilson95": wilson(k, n)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["dev", "test"])
    ap.add_argument("--status", required=True)
    ap.add_argument("--findings", help="default: findings.tsv beside --status")
    ap.add_argument("--treatments", help="optional data/treatments.tsv: adds what the reader extracted for each pair")
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    if not all(ch.isalnum() or ch in "-_." for ch in a.label):
        sys.exit("--label: letters, digits, - _ . only")
    gold_path = os.path.join(HERE, "dev", "dev.tsv") if a.split == "dev" else os.path.join(HERE, "sealed", "test.tsv")
    res_dir = r"~/Documents/us-caselaw-lean-work/caselaw-lean-2/round7/agents/b3/ref_r5"; assert a.split == "dev"
    gold = list(table(gold_path, ["pair_id"]))
    meta = {}
    for r in table(os.path.join(HERE, "work", "scotus_meta.tsv"), ["node"]):
        meta[int(r["node"])] = (int(r["date"]), r["us_cite"], r["name"], r["type"])
    gx = {iint(g["target_node"]) for g in gold}
    gpairs = {(iint(g["by_node"]), iint(g["target_node"])) for g in gold}

    # ---- model status
    eff = collections.defaultdict(set)      # X -> {(status, from, actor, path, whole)}
    model_pairs = {}                         # (Y, X) -> (status, from) for SCOTUS-on-SCOTUS overrulings
    nrows = 0
    for r in table(a.status, STATUS_COLS):
        nrows += 1
        st = r.get("status", "")
        if not (st.startswith("neg:") or st.startswith("unknown:")):
            continue
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
    # ---- findings (atRisk rows linking X and Y)
    fpath = a.findings or os.path.join(os.path.dirname(os.path.abspath(a.status)), "findings.tsv")
    risk = collections.defaultdict(set)
    if os.path.exists(fpath):
        for r in table(fpath, FIND_COLS):
            if r.get("finding") != "atRisk" or not r.get("detail", "").startswith(RISK):
                continue
            c1, c2 = iint(r["citing"]), iint(r["cited"])
            if (c1, c2) in gpairs:
                risk[(c1, c2)].add(r["detail"])
            if (c2, c1) in gpairs:
                risk[(c2, c1)].add(r["detail"])
    else:
        fpath = None
    # ---- reader rows (diagnostic only)
    treat = collections.defaultdict(set)
    if a.treatments:
        for r in table(a.treatments, TREAT_COLS):
            k = (iint(r["by_node"]), iint(r["target_node"]))
            if k in gpairs:
                treat[k].add(f"{r['kind']}:{r['scope']}:explicit={r['explicit']}"
                             + (":implicitTier" if r.get("reader", "").endswith(":implicit") else ""))

    # ---- one outcome per gold pair
    out_rows = [["pair_id", "outcome", "by_node", "target_node", "overruling_cite", "overruled_cite", "partial",
                 "implied", "sources", "model_status", "model_actor", "model_from", "actor_is_gold", "whole_decision",
                 "other_effects", "at_risk", "reader_rows"]]
    dims = collections.defaultdict(collections.Counter)
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
    # ---- precision side, this half only
    half = {k: v for k, v in model_pairs.items() if split_of(meta[k[1]][1], k[1]) == a.split}
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
    res = {"label": a.label, "split": a.split, "gold_pairs": len(gold),
           "inputs": {"status": os.path.abspath(a.status), "status_rows": nrows, "findings": fpath,
                      "treatments": os.path.abspath(a.treatments) if a.treatments else None,
                      "status_sha1": sha1_file(a.status)},
           "recall": summary, "precision_side": precision}
    os.makedirs(res_dir, exist_ok=True)
    blob = json.dumps(res, indent=1, sort_keys=True)
    with open(os.path.join(res_dir, a.label + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(blob + "\n")
    for name, rows_ in ((".pairs.tsv", out_rows), (".unlisted_sample.tsv", sample)):
        with open(os.path.join(res_dir, a.label + name), "w", encoding="utf-8", newline="\n") as f:
            for r in rows_:
                f.write("\t".join(str(c) for c in r) + "\n")
    rh = hashlib.sha1(blob.encode("utf-8")).hexdigest()
    if a.split == "test":
        with open(os.path.join(HERE, "sealed", "TEST_RUNS.log"), "a", encoding="utf-8", newline="\n") as f:
            f.write("\t".join([datetime.datetime.now().astimezone().isoformat(timespec="seconds"), a.label,
                               " ".join(sys.argv[1:]), "result_sha1=" + rh,
                               "status_sha1=" + res["inputs"]["status_sha1"]]) + "\n")
    # ---- stdout: counts only
    print(f"fresh gold, split={a.split}, label={a.label}, pairs={len(gold)}, result_sha1={rh}")
    print(f"{'dimension':<14}{'key':<26}{'n':>4}  " + " ".join(f"{o:>6}" for o in ORDER)
          + "   strict (95% CI)            lenient (95% CI)")
    for dim, d in summary.items():
        for key, v in d.items():
            s, l = v["strict"], v["lenient"]
            print(f"{dim:<14}{key:<26}{v['n']:>4}  " + " ".join(f"{v['outcomes'][o]:>6}" for o in ORDER)
                  + f"   {s['rate']:.3f} [{s['wilson95'][0]:.3f},{s['wilson95'][1]:.3f}]"
                  + f"      {l['rate']:.3f} [{l['wilson95'][0]:.3f},{l['wilson95'][1]:.3f}]")
    print("precision side (this half of the model's Supreme Court overrulings):", json.dumps(precision["classes"]),
          f"of {tot}; all halves: {len(model_pairs)}")
    print("written:", os.path.join(res_dir, a.label + ".json"))


def sha1_file(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


if __name__ == "__main__":
    main()
