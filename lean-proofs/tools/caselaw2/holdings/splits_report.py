"""Split candidates and recall against Supreme Court-resolved conflicts, from data/holdings.tsv + issues.tsv + raw_splits.

    python splits_report.py
writes data/holdings_work/split_candidates.tsv:
    issue_key, usc, question, yes_circuits, no_circuits, first_split_date, scotus_node, scotus_date, scotus_answer,
    example_yes_holding, example_no_holding
and data/holdings_work/split_recall.json (gold = Supreme Court decisions in the selected set that say they resolve a
conflict among the courts of appeals, with the conflict question clustered onto an issue_key).
A split here: two different circuits whose latest published holdings on the issue (before the date) answer oppositely.
Lean decides the formal version (binding, good law on the date); this is the data-side count.
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

DATA = os.path.join(text.WORK, "caselaw-lean-2", "data")
OUT = os.path.join(DATA, "holdings_work")
MINC = 0.6


def load():
    kinds, dates, unpub = {}, {}, {}
    gold = []
    seen = set()
    for l in open(os.path.join(OUT, "raw_splits.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        kinds[r["nid"]] = r["kind"]
        dates[r["nid"]] = r["date"]
        unpub[r["nid"]] = r.get("unpub", 0)
    cl = {}
    for l in open(os.environ.get("CLUSTERS") or os.path.join(OUT, "split_clusters.jsonl"), encoding="utf-8"):
        c = json.loads(l)
        cl[c["key"]] = c
        asg = {it["id"]: it for it in c["items"]}
        for i, (nid, h) in enumerate(c["item_index"]):
            if h == -1 and i in asg and (c["key"], nid) not in seen:
                seen.add((c["key"], nid))
                gold.append({"key": c["key"], "nid": nid, "issue": f"usc:{c['key']}:q{asg[i]['c']}", "date": dates.get(nid, 0),
                             "question": c["item_q"][i]})
    issues = {}
    for l in open(os.path.join(DATA, "issues.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        issues[f[0]] = f
    hold = collections.defaultdict(list)
    for l in open(os.path.join(DATA, "holdings.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if not f[2].startswith("usc:") or f[4] not in ("yes", "no") or float(f[13]) < MINC:
            continue
        nid = int(f[1])
        hold[f[2]].append({"hid": f[0], "nid": nid, "kind": kinds.get(nid), "date": dates.get(nid, 0), "answer": f[4],
                           "unpub": unpub.get(nid, 0), "prop": f[3], "quote": f[9]})
    return hold, issues, gold


def state(hs, before, published=True):
    """circuit -> latest answer before date"""
    last = {}
    for h in sorted(hs, key=lambda h: h["date"]):
        if h["kind"] in (None, 0) or h["date"] >= before or (published and h["unpub"]):
            continue
        last[h["kind"]] = h
    return last


def split_at(hs, before, published=True):
    last = state(hs, before, published)
    y = {c for c, h in last.items() if h["answer"] == "yes"}
    n = {c for c, h in last.items() if h["answer"] == "no"}
    return y, n, last


def main():
    hold, issues, gold = load()
    rows = []
    for key, hs in hold.items():
        sc = sorted((h for h in hs if h["kind"] == 0), key=lambda h: h["date"])
        y, n, last = split_at(hs, 99999999)
        # was there ever a split (any date)? find the first date at which one existed
        first = 0
        for h in sorted(hs, key=lambda h: h["date"]):
            yy, nn, _ = split_at(hs, h["date"] + 1)
            if yy and nn:
                first = h["date"]
                break
        if not first:
            continue
        later_sc = [h for h in sc if h["date"] > first]
        _, _, st = split_at(hs, first + 1)
        ey = next(h for c, h in st.items() if h["answer"] == "yes")
        en = next(h for c, h in st.items() if h["answer"] == "no" and c != ey["kind"])
        rows.append([key, issues[key][3], issues[key][4], ",".join(map(str, sorted(y))), ",".join(map(str, sorted(n))), str(first),
                     str(later_sc[0]["nid"]) if later_sc else "-", str(later_sc[0]["date"]) if later_sc else "-",
                     later_sc[0]["answer"] if later_sc else "-", ey["hid"], en["hid"]])
    rows.sort(key=lambda r: r[0])
    with open(os.path.join(OUT, "split_candidates.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    # recall against Supreme Court-resolved conflicts
    res = []
    for g in gold:
        hs = hold.get(g["issue"], [])
        y, n, last = split_at(hs, g["date"], published=False)
        yp, np_, _ = split_at(hs, g["date"], published=True)
        circ_before = {h["kind"] for h in hs if h["kind"] and h["date"] < g["date"]}
        res.append({**g, "circuits_before": len(circ_before), "detected": bool(y and n), "detected_published": bool(yp and np_)})
    def rate(rs, f):
        k = sum(1 for r in rs if r[f])
        return {"n": len(rs), "hit": k, "recall": round(k / len(rs), 3) if rs else None}
    from math import sqrt
    def wilson(k, n, z=1.96):
        if not n:
            return None
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return [round(c - h, 3), round(c + h, 3)]
    out = {"split_candidates": len(rows),
           "split_candidates_resolved_by_later_scotus_holding": sum(1 for r in rows if r[6] != "-"),
           "gold_scotus_conflicts": len(gold),
           "recall_any": rate(res, "detected"), "recall_published": rate(res, "detected_published"),
           "gold_with_2plus_circuits_before": rate([r for r in res if r["circuits_before"] >= 2], "detected")}
    for k in ("recall_any", "recall_published", "gold_with_2plus_circuits_before"):
        out[k]["wilson95"] = wilson(out[k]["hit"], out[k]["n"])
    out["gold"] = res
    json.dump(out, open(os.path.join(OUT, "split_recall.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "gold"}, indent=1))


if __name__ == "__main__":
    main()
