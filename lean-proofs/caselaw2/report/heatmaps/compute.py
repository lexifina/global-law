"""Daily counts behind the vulnerability heatmaps (no Lean run: existing outputs only).

    python compute.py [CACHE_DIR]

Writes series/<name>.tsv (day, count, then one column per part) and series.json (definitions, totals, drops), beside
this file, or under the directory named by the environment variable HEATMAPS_OUT (used for dry runs).
Reads:
  caselaw-lean-2/out/findings.tsv, out/status.tsv, data/decisions2.tsv, data/treatments.tsv, data/history.tsv
  uses/xrefs/dangling_episodes.tsv, uses/xrefs/data/scan.pkl + usc/versions.tsv (duplicate designations, via
  global-law-lean/lean-proofs/tools/caselaw/usc_xrefs.py), uses/amendments/data/{results.tsv,instructions.jsonl}
"""
import collections
import datetime as dt
import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np

HOME = Path.home()
W = HOME / "Documents" / "us-caselaw-lean-work"
C2 = W / "caselaw-lean-2"
HERE = Path(__file__).resolve().parent
DEST = Path(os.environ["HEATMAPS_OUT"]) if os.environ.get("HEATMAPS_OUT") else HERE
DEST.mkdir(parents=True, exist_ok=True)
SER = DEST / "series"
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else None

BAD_KINDS = ["citesOverruled", "citesVacated", "citesWithdrawn", "citesNotCitable", "appliesSupersededHolding"]


def valid(d):
    try:
        dt.date(d // 10000, d // 100 % 100, d % 100)
        return True
    except ValueError:
        return False


def load_decisions():
    if CACHE and (CACHE / "date.npy").exists():
        return np.load(CACHE / "date.npy"), np.load(CACHE / "court.npy")
    n = 0
    date = np.zeros(7_000_000, np.int32)
    court = np.zeros(7_000_000, np.int32)
    with open(C2 / "data" / "decisions2.tsv", encoding="utf-8") as f:
        for line in f:
            a = line.split("\t", 4)
            i = int(a[0])
            date[i] = int(a[2])
            court[i] = int(a[1])
            n = max(n, i)
    date, court = date[: n + 1], court[: n + 1]
    if CACHE:
        CACHE.mkdir(parents=True, exist_ok=True)
        np.save(CACHE / "date.npy", date)
        np.save(CACHE / "court.npy", court)
    return date, court


def precision_mask(date, court):
    """Court-years whose day-of-month-1 share is far above chance carry month- or year-precision dates on the 1st.

    A decision date is treated as imprecise when it is 1 January (any court, any year), or when it falls on the 1st of
    a month in a court-year where at least 3 decisions and over 12% of all decisions fall on a 1st (chance is about
    3.3%). Returns a boolean array: True = keep the day."""
    y = date // 10000
    dom1 = (date % 100) == 1
    key = court.astype(np.int64) * 10000 + y
    uk, inv = np.unique(key, return_inverse=True)
    n = np.bincount(inv)
    k = np.bincount(inv, weights=dom1)
    bad = (k >= 3) & (k / np.maximum(n, 1) > 0.12)
    imprecise = (dom1 & bad[inv]) | ((date % 10000) == 101) | (date <= 0)
    return ~imprecise, int(bad.sum()), int(len(uk))


def write_series(name, days, parts):
    """days: dict day -> Counter(part -> n). Writes series/<name>.tsv."""
    SER.mkdir(exist_ok=True)
    with open(SER / f"{name}.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("day\tcount\t" + "\t".join(parts) + "\n")
        for d in sorted(days):
            c = days[d]
            f.write(f"{d}\t{sum(c[p] for p in parts)}\t" + "\t".join(str(c[p]) for p in parts) + "\n")


def caselaw(meta):
    date, court = load_decisions()
    keep, bad_cy, all_cy = precision_mask(date, court)
    meta["precision"] = {"court_years_flagged": bad_cy, "court_years": all_cy,
                         "decisions_imprecise": int((~keep).sum()), "decisions": int(len(date))}

    # A. decisions relying on bad law: one per citing decision, parts = finding kinds it has (may overlap)
    kinds = collections.defaultdict(set)
    rows = collections.Counter()
    firm = collections.Counter()
    with open(C2 / "out" / "findings.tsv", encoding="utf-8") as f:
        next(f)
        for line in f:
            a = line.rstrip("\n").split("\t")
            if a[0] in BAD_KINDS:
                kinds[int(a[1])].add(a[0])
                rows[a[0]] += 1
                firm[a[5]] += 1
    days = collections.defaultdict(collections.Counter)
    dropped = 0
    for node, ks in kinds.items():
        d = int(date[node])
        if not keep[node] or not valid(d):
            dropped += 1
            continue
        c = days[d]
        c["_n"] += 1
        for k in ks:
            c[k] += 1
    # count = decisions; parts = decisions with each kind
    SER.mkdir(exist_ok=True)
    with open(SER / "badlaw.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("day\tcount\t" + "\t".join(BAD_KINDS) + "\n")
        for d in sorted(days):
            c = days[d]
            f.write(f"{d}\t{c['_n']}\t" + "\t".join(str(c[k]) for k in BAD_KINDS) + "\n")
    meta["badlaw"] = {"citing_decisions": len(kinds), "dropped_imprecise": dropped, "finding_rows": dict(rows),
                      "finding_rows_firm": dict(firm)}

    # B. precedent broken: distinct witness events of negativeAdmitted status rows, by the actor's decision date
    ev = {}
    first_from = {}
    with open(C2 / "out" / "status.tsv", encoding="utf-8") as f:
        next(f)
        for line in f:
            a = line.rstrip("\n").split("\t")
            if a[6] != "negativeAdmitted":
                continue
            w = a[8]
            if w not in ev:
                ev[w] = (a[5].split(":", 1)[1], a[9], a[10], int(a[0]))
                first_from[w] = int(a[3])
            else:
                first_from[w] = min(first_from[w], int(a[3]))
    src_date = {}
    for fn, col in (("treatments.tsv", 3), ("history.tsv", 3)):
        with open(C2 / "data" / fn, encoding="utf-8") as f:
            for line in f:
                a = line.split("\t", col + 1)
                src_date[a[0]] = int(a[col])
    days = collections.defaultdict(collections.Counter)
    dropped = 0
    by_status = collections.Counter()
    by_path = collections.Counter()
    date_from = collections.Counter()
    for w, (st, actor, path, target) in ev.items():
        by_status[st] += 1
        by_path[path] += 1
        if path == "supersession":  # a statute, no treating decision: the day the effect starts
            d = first_from[w]
            date_from["supersession_first_from"] += 1
            ok = valid(d)
        else:
            an = int(actor)
            d = int(date[an])
            sd = src_date.get(w)
            date_from["actor_date" if sd is None or sd == d else "actor_date_differs_from_row"] += 1
            ok = bool(keep[an]) and valid(d)
        if not ok:
            dropped += 1
            continue
        part = {"abrogated": "overruled"}.get(st, st)
        days[d][part] += 1
    parts = ["overruled", "reversed", "vacated", "withdrawn", "superseded", "depublished"]
    write_series("broken", days, parts)
    meta["broken"] = {"events": len(ev), "dropped_imprecise": dropped, "by_status": dict(by_status),
                      "by_path": dict(by_path), "dated_by": dict(date_from)}
    return date


def usc(meta):
    days = collections.defaultdict(collections.Counter)
    causes = collections.defaultdict(collections.Counter)  # day -> cause label -> n

    # 1. dangling cross-references: broken later or written dangling, by the day the episode starts
    n = collections.Counter()
    with open(W / "uses" / "xrefs" / "dangling_episodes.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in f:
            a = line.rstrip("\n").split("\t")
            cls = a[ix["class"]]
            if cls == "at-start":
                n["at-start (excluded)"] += 1
                continue
            d = int(a[ix["from"]])
            days[d]["xref"] += 1
            causes[d][a[ix["cause"]] or "?"] += 1
            n[cls] += 1
    meta["usc_xref"] = dict(n)

    # 2. amending instructions whose struck words are not in the section (class not_found, main scope)
    approved = {}
    with open(W / "uses" / "amendments" / "data" / "instructions.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("header"):
                approved[r["law"]] = int(r["approved"].replace("-", ""))
    n = collections.Counter()
    with open(W / "uses" / "amendments" / "data" / "results.tsv", encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(hdr)}
        for line in f:
            a = line.rstrip("\n").split("\t")
            if a[ix["law_commit"]] not in ("ok", "ok_multi"):
                continue
            o = a[ix["outcome"]]
            n[o] += 1
            if o != "not_found":
                continue
            d = approved[a[ix["law"]]]
            days[d]["amend"] += 1
            causes[d][a[ix["law"]]] += 1
    meta["usc_amend_main_scope"] = dict(n)

    # 3. duplicate designations among siblings, by the version that first made each one (record start excluded)
    sys.path.insert(0, str(HOME / "Documents" / "global-law-lean" / "lean-proofs" / "tools" / "caselaw"))
    from usc_xrefs import load_versions, pstr  # noqa: E402
    vers = load_versions(str(W / "usc" / "versions.tsv"))
    scan_ = pickle.load(open(W / "uses" / "xrefs" / "data" / "scan.pkl", "rb"))
    first = {}
    for p, vs in vers.items():
        prev = set()
        for v in vs:
            a = scan_.get((p, v[3])) if v[3] else None
            ds = {(pstr(x[0]), x[1]) for x in a[4]} if a and a[0] else set()
            for k in ds - prev:
                first.setdefault((p, k), v)
            prev = ds
    n = collections.Counter()
    for (p, k), v in first.items():
        lab = v[2] + (f" ({v[4]})" if v[4] else "")
        if v[2] == "1994 edition of the US Code":
            n["at record start (excluded)"] += 1
            continue
        days[v[0]]["dup"] += 1
        causes[v[0]][lab] += 1
        n["counted"] += 1
    meta["usc_dup"] = dict(n)

    parts = ["xref", "amend", "dup"]
    write_series("usc", days, parts)
    top = {}
    for d in days:
        top[str(d)] = causes[d].most_common(4)
    with open(SER / "usc_causes.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(top, f, indent=0)


def main():
    meta = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}
    caselaw(meta)
    usc(meta)
    with open(DEST / "series.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
