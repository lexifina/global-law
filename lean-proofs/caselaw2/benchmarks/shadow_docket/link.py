#!/usr/bin/env python3
"""Link each Shadow Docket item (one Supreme Court docket) to exactly one corpus decision by lower-court docket number.

Inputs: work/items.tsv (items.py), work/docket_index.tsv.gz (build_index.py). No model file is read.
Rule (never guesses):
  1. court: `lower_ct` -> a court filter (federal circuit by number; Armed Forces / Veterans Claims / Federal Claims /
     Tax Court by id; other federal courts = any non-circuit federal court; state courts = every court of that state
     system). Unparseable -> `court_unmapped`.
  2. docket: each lower docket number in the item -> normalised key (sdlib.docket_key); corpus decisions of a court
     that passes the filter with that key (exact key first; if none, the key without trailing letter-only groups on
     both sides, e.g. '18-2975-cr' = '18-2975').
  3. date: if the Supreme Court docket page (deposited raw JSON -> work/docket_dates.tsv) gives the lower court's
     decision date D, the decision must be dated within 3 days of D (failing that, of the rehearing-denied date R,
     then of the discretionary-review date S; each step used only when it leaves exactly one decision) and before
     the first Supreme Court order; no decision on those dates -> `date_mismatch`. Without a docket-page date: the
     decision is dated before the item's first Supreme Court order and no more than 4 years before the deciding
     order (`only_after_order` / `only_too_old` when all hits fall outside).
  4. exactly one decision left -> `linked`. Otherwise: `no_docket_in_source`, `court_unmapped`,
     `docket_not_in_corpus` (no corpus decision of that court system carries the key), `date_mismatch`,
     `only_after_order`, `only_too_old`, `multiple_candidates`.
Also: whether the Supreme Court order itself is in the corpus (a supreme-court decision whose docket key equals the
item's Supreme Court docket, dated within 45 days of the deciding order) -> `sc_in_corpus`, `sc_node`.
Split halves (benchlib.split_half on the Supreme Court docket number) are assigned here, before any model row is read.
Writes: key.tsv, links_summary.tsv.
"""
import collections
import datetime
import gzip
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sdlib  # noqa: E402
from sdlib import benchlib  # noqa: E402

W = sdlib.WORK
SCORE_CLASSES = ("NEG", "PART", "CLEAN")
CIRC = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
        "ninth": 9, "tenth": 10, "eleventh": 11, "district of columbia": 12, "federal": 13}
STATES = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida",
          "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
          "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska",
          "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
          "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas",
          "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
          "district of columbia", "puerto rico", "guam", "virgin islands"]
SYS = {s: i + 1 for i, s in enumerate(STATES)}
WINDOW_DAYS = 4 * 365 + 1


def ordn(d):
    d = int(d)
    try:
        return datetime.date(d // 10000, d // 100 % 100 or 1, d % 100 or 1).toordinal()
    except ValueError:
        return 0


def court_filter(lct):
    """-> (label, predicate(court2, system, tier, circuit, repo)) or (None, None)."""
    s = re.sub(r"\s+", " ", lct.lower())
    s = s.replace("ofnew", "of new")
    m = re.search(r"court of appeals for the (first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
                  r"eleventh|district of columbia|federal) circuit", s)
    if m and "united states" in s:
        k = CIRC[m.group(1)]
        return "ca%d" % k, (lambda c2, sy, t, ci, rp, k=k: sy == 0 and ci == k and t == "A")
    if "armed forces" in s:
        return "caaf", (lambda c2, sy, t, ci, rp: c2 == 650)
    if "veterans claims" in s or "veterans appeals" in s:
        return "cavc", (lambda c2, sy, t, ci, rp: c2 == 651)
    if "court of federal claims" in s:
        return "cfc", (lambda c2, sy, t, ci, rp: c2 == 656)
    if "tax court" in s and "united states" in s:
        return "tax", (lambda c2, sy, t, ci, rp: rp == "tax-court")
    if s.startswith("united states") or "united states district court" in s or "bankruptcy" in s:
        return "fed-other", (lambda c2, sy, t, ci, rp: sy == 0 and t != "A")
    best = None
    for st in STATES:
        if re.search(r"\b" + st + r"\b", s):
            if best is None or len(st) > len(best):
                best = st
    if best is None:
        return None, None
    k = SYS[best]
    return "state:" + best, (lambda c2, sy, t, ci, rp, k=k: sy == k)


_TRAIL = re.compile(r"(-[A-Z]+)+$")


def core(k):
    c = _TRAIL.sub("", k)
    return c if sum(ch.isdigit() for ch in c) >= 3 else ""


def load_dates():
    dd = {}
    p = os.path.join(W, "docket_dates.tsv")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            next(f)
            for line in f:
                q = line.rstrip("\n").split("\t")
                dd[q[0]] = (int(q[3]), int(q[4]), int(q[5]))
    return dd


def near(d, ref):
    return ref > 0 and abs(ordn(d) - ordn(ref)) <= 3


def main():
    dates = load_dates()
    items = []
    with open(os.path.join(W, "items.tsv"), encoding="utf-8") as f:
        hdr = next(f).rstrip("\n").split("\t")
        for line in f:
            items.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
    need = set()
    for it in items:
        it["keys"] = [] if it["lower_docket"] == "NA" else sdlib.docket_keys(it["lower_docket"].replace(" || ", ";"))
        for k in it["keys"]:
            need.add(k)
            if core(k):
                need.add(core(k))
        it["sckey"] = sdlib.docket_key(it["sc_docket"])
        need.add("SC:" + it["sckey"])
    exact = collections.defaultdict(list)
    cored = collections.defaultdict(list)
    sc = collections.defaultdict(list)
    with gzip.open(os.path.join(W, "docket_index.tsv.gz"), "rt", encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            k = p[0]
            row = (int(p[1]), int(p[2]), int(p[3]) if p[3].lstrip("-").isdigit() else -1, int(p[4]), p[5],
                   int(p[6]), p[7], p[9])
            if p[7] == "supreme-court":
                if ("SC:" + k) in need:
                    sc[k].append(row)
                continue
            if k in need:
                exact[k].append(row)
            ck = core(k)
            if ck and ck in need:
                cored[ck].append(row)
    stat = collections.Counter()
    bycls = collections.Counter()
    out = open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n")
    cols = ["sc_docket", "half", "class", "sub", "order_date", "first_date", "lower_ct", "court_label", "lower_docket",
            "link", "node", "node_date", "node_repo", "node_title", "n_candidates", "candidates", "key_mode",
            "sc_in_corpus", "sc_node", "lower_decision_date", "caption"]
    out.write("\t".join(cols) + "\n")
    for it in items:
        half = benchlib.split_half(sdlib.DATASET, it["sc_docket"])
        od, fd = int(it["order_date"]), int(it["first_date"])
        lo = ordn(od) - WINDOW_DAYS
        hi = ordn(fd)
        label = "-"
        link, node, cands, mode = "", "", [], "-"
        if not it["keys"]:
            link = "no_docket_in_source"
        else:
            label, pred = court_filter(it["lower_ct"].split(" || ")[0])
            if pred is None:
                link = "court_unmapped"
                label = "-"
            else:
                for mode_try, table, keys in (("exact", exact, it["keys"]),
                                              ("core", cored, [core(k) for k in it["keys"] if core(k)])):
                    hits = {}
                    for k in keys:
                        for r in table.get(k, ()):
                            if pred(r[2], r[3], r[4], r[5], r[6]):
                                hits[r[0]] = r
                    if hits:
                        mode = mode_try
                        break
                dpage = dates.get(it["sc_docket"], (0, 0, 0))
                if not hits:
                    link = "docket_not_in_corpus"
                elif dpage[0] > 0:
                    before = {n: r for n, r in hits.items() if ordn(r[1]) < hi}
                    link = "date_mismatch"
                    cands = sorted(hits.values(), key=lambda r: r[1])
                    for tag, ref in (("D", dpage[0]), ("R", dpage[1]), ("S", dpage[2])):
                        m_ = {n: r for n, r in before.items() if near(r[1], ref)}
                        if len(m_) == 1:
                            link, node = "linked", next(iter(m_))
                            cands = list(m_.values())
                            mode += "+date" + tag
                            break
                        if len(m_) > 1:
                            link = "multiple_candidates"
                            cands = sorted(m_.values(), key=lambda r: r[1])
                            break
                else:
                    inwin = {n: r for n, r in hits.items() if lo <= ordn(r[1]) < hi}
                    cands = sorted(hits.values(), key=lambda r: r[1])
                    if not inwin:
                        link = "only_after_order" if all(ordn(r[1]) >= hi for r in cands) else "only_too_old"
                    elif len(inwin) == 1:
                        link = "linked"
                        node = next(iter(inwin))
                        cands = sorted(inwin.values(), key=lambda r: r[1])
                        mode += "+window"
                    else:
                        link = "multiple_candidates"
                        cands = sorted(inwin.values(), key=lambda r: r[1])
        scn = [r for r in sc.get(it["sckey"], ()) if abs(ordn(r[1]) - ordn(od)) <= 45]
        sc_in = "yes" if scn else "no"
        nd = nrepo = ntitle = ""
        if node:
            r = cands[0]
            nd, nrepo, ntitle = str(r[1]), r[6], r[7]
        cstr = ";".join("%d@%d:%s" % (r[0], r[1], r[6]) for r in cands[:8])
        out.write("\t".join([it["sc_docket"], half, it["class"], it["sub"], it["order_date"], it["first_date"],
                             it["lower_ct"], label, it["lower_docket"], link, str(node), nd, nrepo, ntitle[:150],
                             str(len(cands)), cstr, mode, sc_in, ",".join(str(r[0]) for r in scn[:3]),
                             str(dates.get(it["sc_docket"], (0, 0, 0))[0]), it["caption"][:200]]) + "\n")
        stat[(it["class"] in SCORE_CLASSES, link)] += 1
        bycls[(it["class"], link)] += 1
    out.close()
    with open(os.path.join(HERE, "links_summary.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("class\tlink\titems\n")
        for (c, l), n in sorted(bycls.items()):
            o.write("%s\t%s\t%d\n" % (c, l, n))
    for k, v in sorted(stat.items()):
        print(k, v)


if __name__ == "__main__":
    main()
