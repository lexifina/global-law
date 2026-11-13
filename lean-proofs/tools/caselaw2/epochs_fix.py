"""Round 2 (agent courts): fill epoch_from / epoch_to in courts2.tsv (rerunnable).

    python -X utf8 epochs_fix.py [--data DIR] [--out FILE] [--report DIR] [--install]

Reads DIR/courts2.pre_round2.tsv when it exists (else DIR/courts2.tsv), DIR/succession.tsv and DIR/decisions2.tsv
(columns node, court_id, date only). Writes FILE (default <report dir>/courts2.tsv). With --install it writes
DIR/courts2.tsv through courts2.tsv.tmp + rename and keeps the input once as courts2.pre_round2.tsv. It also raises
three tags to S in succession.tsv / adoption.tsv (SUCC_VERIFIED, ADOPT_VERIFIED; same install rule).

Before this fix every court's rows tiled 0..99991231, so a court created later "existed" from date 0 and a court
that ceased never ended (DIFFTEST 8.2 / 8.5 data note, DEVIATIONS 69 limit a).

How the engines read epochs (reference `Engine.epoch`, Lean `epochCovers`): a row covers d when from <= d <= to;
to = 0 is read as open (we keep writing 99991231). A date no row covers gives no epoch: unknown force, no power,
an adopter that does not hold, a destination that is skipped.

Rules
-----
G = 366 days. "Anchor" = a dated creation or end of the court.

1. End anchors. succession rows with old = c, new != c: kinds replace, absorb, rename end the old court on the day
   before the succession date. A split ends the old court only when the court has decisions and fewer than 5% of
   them are dated on or after the succession date (Alabama Court of Appeals, Court of Claims, Dakota Territory: ended;
   Fifth and Eighth Circuits, Florida 2d DCA: not). Entries of KNOWN_END are anchors too.
2. Start anchors. succession rows with new = c, old != c (the earliest), and entries of KNOWN_START.
3. The data may only widen a bound, and a data-derived bound is a year edge (the margin): 1 January of the year of
   a first decision, 31 December of the year of a last decision, src `data:first-decision` / `data:last-decision`.
   Start: min(first decision, anchor). If any decision is dated before the anchor the start is data-derived (the id
   then also covers an earlier court, or misdated decisions; a start that is too early has no effect on the successor
   logic). Otherwise an S or L anchor is the start; a U anchor is not used, the start is the year of the first
   decision.
   End: an S or L anchor is the end (the day before the succession date). A U anchor is not used: the end is the
   year of the court's last decision before the anchor, or of the last decision reached by walking forward from the
   anchor while the next decision date is at most G days away (the day is what is uncertain); open when the court
   has no decisions.
4. No anchor. Start: 1 January of the year of the court's first decision, only when that year is at least 25 years
   after the start of its system (the earliest 1st-percentile decision year among the system's courts with 100 or
   more decisions; 1789 for the federal system); otherwise 0. End: never (a court that is thin in the corpus is not
   ended).
5. Rows wholly outside [start, end] are dropped; the first and last remaining rows are clipped. Internal boundaries
   (renames and role changes that keep the id) are not touched.
6. Decisions dated after the end (beyond a gap of more than G days: misrouted or misdated decisions) get their own
   rows, one per cluster of dates (gap <= G), with the exact first and last date, the fields of the court's last row
   and src `data:decision-cluster`. So no decision is dated outside its court's rows, and the court is still gone
   for the successor logic at every other date.

Bound sources are appended to the row's src as ` | from:<source>[<tag>]` and ` | to:<source>[<tag>]`. The row tag is
not changed (it tags the row's name/tier facts and decides whether the firm run keeps the row).
"""
import argparse
import collections
import datetime
import os
import sys

OPEN = 99991231
G = 366
C2 = os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2")

# court_id -> (date, source, tag). S only where the date is verified in the succession table or in a primary source
# already cited in COURTS.md; L = from memory; U = uncertain (not used as a bound, rule 3).
KNOWN_START = {
    914: (19760101, "known: Kentucky Court of Appeals (intermediate) from 1 Jan 1976; succession 913->917 "
                    "(SCR 1.030(8)(a)) and adoption 914<-913 up to 19751231", "S"),
    1099: (19480915, "known: N.J. Const. 1947, Judicial Article in force 15 Sept 1948 (doctrine 3.2 NJ)", "L"),
    1222: (19480915, "known: N.J. Const. 1947, Judicial Article in force 15 Sept 1948 (doctrine 3.2 NJ)", "L"),
    3018: (19850101, "known: Court of Appeals of Virginia began 1 Jan 1985 (COURTS.md, Virginia)", "L"),
    649: (19100618, "known: Commerce Court, Mann-Elkins Act of 18 June 1910, 36 Stat. 539", "L"),
    664: (19420130, "known: Emergency Court of Appeals, Emergency Price Control Act of 30 Jan 1942, 56 Stat. 23", "L"),
}
KNOWN_END = {
    1095: (19480914, "known: the old Supreme Court of New Jersey ended with the 1947 constitution's Judicial Article, "
                     "in force 15 Sept 1948 (doctrine 3.2 NJ; same date as succession 1094->1096)", "L"),
    649: (19131231, "known: Commerce Court abolished 31 Dec 1913 (Act of 22 Oct 1913, 38 Stat. 208, 219)", "L"),
    664: (19620418, "known: Emergency Court of Appeals terminated 1962 (day uncertain)", "U"),
    635: (19930429, "known: Temporary Emergency Court of Appeals abolished by Pub. L. 102-572 sec. 102 "
                    "(six months after 29 Oct 1992; day uncertain)", "U"),
    679: (19930429, "known: Temporary Emergency Court of Appeals abolished by Pub. L. 102-572 sec. 102 "
                    "(six months after 29 Oct 1992; day uncertain)", "U"),
}
# The old United States circuit courts (trial courts) were abolished on 1 Jan 1912 (Judicial Code of 1911, sec. 289,
# 36 Stat. 1087, 1167). Applied to federal trial rows whose name says "Circuit Court" and not "of Appeals".
CIRCUIT_COURT_END = (19111231, "known: U.S. circuit courts abolished 1 Jan 1912 (Judicial Code of 1911 sec. 289, "
                               "36 Stat. 1167)", "L")
# Tags checked in round 2 against a primary source read in the corpus: South Corp. v. United States, 690 F.2d 1368,
# 1369 (Fed. Cir. 28 Oct 1982, in banc; node 1612455): the Federal Circuit was "established October 1, 1982 by the
# Federal Courts Improvement Act of 1982, Pub.L.No.97-164, 96 Stat. 25"; the holdings of the Court of Claims and the
# CCPA "announced ... before the close of business September 30, 1982, shall be binding as precedent in this court".
SOUTH = "South Corp. v. United States, 690 F.2d 1368, 1369 (Fed. Cir. 1982) (in banc; read in the corpus, round2 courts)"
SUCC_VERIFIED = {
    ("655", "520", "19821001"): "doctrine F11 (Pub. L. 97-164; Fed. Cir. established 1 Oct 1982: %s)" % SOUTH,
    ("654", "520", "19821001"): "doctrine F11 (appellate functions to the Fed. Cir., established 1 Oct 1982: %s)" % SOUTH,
}
ADOPT_VERIFIED = {
    ("520", "655", "19820930"): "doctrine F11(a): %s: holdings announced before the close of business 30 Sept 1982 "
                                "bind" % SOUTH,
}


def ordinal(d):
    y, m, dd = max(d // 10000, 1), min(max(d // 100 % 100, 1), 12), max(d % 100, 1)
    while True:
        try:
            return datetime.date(y, m, dd).toordinal()
        except ValueError:          # a day the month does not have (noisy data): step back
            dd -= 1


def prev_day(d):
    x = datetime.date.fromordinal(ordinal(d) - 1)
    return x.year * 10000 + x.month * 100 + x.day


def jan1(d):
    return d // 10000 * 10000 + 101


def dec31(d):
    return d // 10000 * 10000 + 1231


def read_rows(path):
    with open(path, encoding="utf-8", newline="\n") as f:
        return [l.rstrip("\n").split("\t") for l in f if l.strip("\n")]


def load_dates(path):
    """court -> Counter(date) for dated decisions."""
    out = collections.defaultdict(collections.Counter)
    with open(path, encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.split("\t", 3)
            d = int(p[2])
            if d:
                out[int(p[1])][d] += 1
    return out


def covered(rows, d):
    return any(int(r[1]) <= d <= (int(r[2]) or OPEN) for r in rows)


def violations(by_court, dates):
    n, per = 0, {}
    for c, cnt in dates.items():
        rows = by_court.get(c, [])
        k = sum(v for d, v in cnt.items() if not covered(rows, d))
        if k:
            per[c] = k
            n += k
    return n, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(C2, "data"))
    ap.add_argument("--report", default=os.path.join(C2, "work", "round2", "courts"))
    ap.add_argument("--out")
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    J = lambda n: os.path.join(a.data, n)
    backup = J("courts2.pre_round2.tsv")
    src_path = backup if os.path.exists(backup) else J("courts2.tsv")
    rows = read_rows(src_path)
    tables = verified_tables(J)
    succ = tables["succession.tsv"][0]
    dates = load_dates(J("decisions2.tsv"))
    order, by_court = [], collections.defaultdict(list)
    for r in rows:
        c = int(r[0])
        if c not in by_court:
            order.append(c)
        by_court[c].append(list(r))
    for v in by_court.values():
        v.sort(key=lambda r: int(r[1]))

    # system start (rule 4)
    sys_p1 = collections.defaultdict(list)
    sys_first = collections.defaultdict(list)
    for c, cnt in dates.items():
        if c not in by_court:
            continue
        s = int(by_court[c][0][4])
        ds = sorted(cnt.elements())
        sys_first[s].append(ds[0] // 10000)
        if len(ds) >= 100:
            sys_p1[s].append(ds[len(ds) // 100] // 10000)
    sys_start = {s: min(sys_p1[s]) if sys_p1.get(s) else min(v) for s, v in sys_first.items()}
    sys_start[0] = 1789

    start_anchor, end_anchor = {}, {}
    for (old, new, d, kind, ssrc, tag) in ((int(s[0]), int(s[1]), int(s[2]), s[3], s[4], s[5]) for s in succ):
        if old == new:
            continue
        label = "succession %d->%d %d %s" % (old, new, d, kind)
        if new not in start_anchor or d < start_anchor[new][0]:
            start_anchor[new] = (d, label, tag)
        ends = kind != "split"
        if kind == "split":
            cnt = dates.get(old)
            if cnt:
                tot = sum(cnt.values())
                late = sum(v for dd, v in cnt.items() if dd >= d)
                ends = late / tot < 0.05
        if ends and (old not in end_anchor or d > end_anchor[old][0]):
            end_anchor[old] = (d, label, tag)          # date = first day without the court
    for c, (d, s, t) in KNOWN_START.items():        # a known S/L date goes before a U succession date
        if c in by_court and (c not in start_anchor or start_anchor[c][2] == "U"):
            start_anchor[c] = (d, s, t)
    for c, (d, s, t) in KNOWN_END.items():
        if c in by_court and (c not in end_anchor or end_anchor[c][2] == "U"):
            end_anchor[c] = (next_day(d), s, t)
    for c, v in by_court.items():
        r = v[0]
        if r[4] == "0" and r[5] == "T" and "Circuit Court" in r[3] and "Appeals" not in r[3] and c not in end_anchor:
            end_anchor[c] = (next_day(CIRCUIT_COURT_END[0]), CIRCUIT_COURT_END[1], CIRCUIT_COURT_END[2])

    before_n, before_per = violations(by_court, dates)
    stats_before = bound_stats(by_court)

    log, new_by_court, src_count = [], {}, collections.Counter()
    cluster_rows = []
    for c in order:
        v = [list(r) for r in by_court[c]]
        ds = sorted(dates.get(c, ()))
        cnt = dates.get(c, {})
        ords = [ordinal(d) for d in ds]
        old_from, old_to = int(v[0][1]), int(v[-1][2]) or OPEN
        nf, fsrc, nt, tsrc = old_from, None, old_to, None

        # ---- start
        if c in start_anchor:
            A, label, tag = start_anchor[c]
            if ds and ds[0] < A:
                nf = jan1(ds[0])
                fsrc = "data:first-decision(%d; %d decisions dated before %s)[-]" % (
                    ds[0], sum(cnt[d] for d in ds if d < A), label)
            elif tag in ("S", "L"):
                nf, fsrc = A, "%s[%s]" % (label, tag)
            else:
                later = [d for d in ds if d >= A]
                if later:
                    nf = jan1(later[0])
                    fsrc = "data:first-decision(%d; %s is tagged U and not used)[-]" % (later[0], label)
        elif old_from == 0 and ds:
            y = ds[0] // 10000
            s = int(v[0][4])
            if y >= sys_start.get(s, y) + 25:
                nf, fsrc = jan1(ds[0]), "data:first-decision(%d)[-]" % ds[0]
        # ---- end
        if c in end_anchor:
            A, label, tag = end_anchor[c]
            E = prev_day(A)
            if tag in ("S", "L"):
                nt, tsrc = E, "%s[%s]" % (label, tag)
            else:
                earlier = [d for d in ds if d <= E]
                cur, oc = (earlier[-1] if earlier else E), ordinal(E)
                for d, o in zip(ds, ords):
                    if d <= E:
                        continue
                    if o - oc <= G:
                        cur, oc = d, o
                    else:
                        break
                if earlier or cur > E:
                    nt, tsrc = dec31(cur), "data:last-decision(%d; %s is tagged U and not used)[-]" % (cur, label)
        if nt < nf:                      # anchors that cross (no decisions between): keep the old bounds
            log.append("court %d: start %d after end %d, bounds left as they were" % (c, nf, nt))
            nf, fsrc, nt, tsrc = old_from, None, old_to, None

        # ---- clip rows (rule 5)
        kept = [r for r in v if (int(r[2]) or OPEN) >= nf and int(r[1]) <= nt]
        if not kept:
            kept = [v[0]] if nt < int(v[0][1]) else [v[-1]]
        dropped = len(v) - len(kept)
        if dropped:
            log.append("court %d: %d row(s) wholly outside %d-%d dropped" % (c, dropped, nf, nt))
        if int(kept[0][1]) < nf or fsrc:
            kept[0][1] = str(nf)
        if (int(kept[-1][2]) or OPEN) > nt or tsrc:
            kept[-1][2] = str(nt)
        if fsrc:
            kept[0][9] = kept[0][9] + " | from:" + fsrc
            src_count["from:" + kind_of(fsrc)] += 1
        if tsrc:
            kept[-1][9] = kept[-1][9] + " | to:" + tsrc
            src_count["to:" + kind_of(tsrc)] += 1

        # ---- clusters (rule 6)
        main = list(kept)
        out_dates = [d for d in ds if not covered(kept, d)]
        clusters = []
        for d in out_dates:
            if clusters and ordinal(d) - ordinal(clusters[-1][-1]) <= G:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        for cl in clusters:
            base = main[0] if cl[-1] < int(main[0][1]) else main[-1]
            n = sum(cnt[d] for d in cl)
            r = list(base)
            r[1], r[2] = str(cl[0]), str(cl[-1])
            r[9] = base[9].split(" | from:")[0].split(" | to:")[0] + \
                " | data:decision-cluster(n=%d dated after the court's end, rows %s-%s: misrouted or misdated "                 "decisions)[-]" % (n, main[0][1], main[-1][2])
            kept.append(r)
            cluster_rows.append((c, cl[0], cl[-1], n, base[3]))
            src_count["cluster rows"] += 1
        kept.sort(key=lambda r: int(r[1]))
        new_by_court[c] = kept

    out_rows = [r for c in order for r in new_by_court[c]]
    after_n, after_per = violations(new_by_court, dates)
    stats_after = bound_stats(new_by_court)

    os.makedirs(a.report, exist_ok=True)
    out_path = a.out or os.path.join(a.report, "courts2.tsv")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for r in out_rows:
            f.write("\t".join(r) + "\n")
    with open(os.path.join(a.report, "epoch_clusters.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for (c, d0, d1, n, name) in cluster_rows:
            f.write("%d\t%d\t%d\t%d\t%s\n" % (c, d0, d1, n, name))
    rep = []
    rep.append("input %s: %d rows, %d court ids" % (src_path, len(rows), len(by_court)))
    rep.append("output %s: %d rows" % (out_path, len(out_rows)))
    rep.append("decisions dated outside their court's rows: before %d (%d courts), after %d (%d courts)" % (
        before_n, len(before_per), after_n, len(after_per)))
    rep.append("court ids with a non-zero first epoch_from: before %d, after %d" % (stats_before[0], stats_after[0]))
    rep.append("court ids with a closed last epoch_to:     before %d, after %d" % (stats_before[1], stats_after[1]))
    rep.append("bounds set by source: " + ", ".join("%s %d" % kv for kv in sorted(src_count.items())))
    rep.append("cluster rows: %d rows, %d courts, %d decisions" % (
        len(cluster_rows), len({x[0] for x in cluster_rows}), sum(x[3] for x in cluster_rows)))
    rep.extend(log)
    with open(os.path.join(a.report, "epochs_report.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rep) + "\n")
    print("\n".join(rep[:7]))
    if after_n:
        print("ERROR: decisions outside epochs remain", sorted(after_per.items())[:10])
        sys.exit(1)
    for name, (trows, n) in tables.items():
        print("%s: %d tag(s) raised to S (South Corp.)" % (name, n))
        with open(os.path.join(a.report, name), "w", encoding="utf-8", newline="\n") as f:
            for r in trows:
                f.write("\t".join(r) + "\n")
    if a.install:
        install(J("courts2.tsv"), out_rows, backup)
        print("installed", J("courts2.tsv"), "(original kept as", backup + ")")
        for name, (trows, n) in tables.items():
            if n:
                install(J(name), trows, J(name.replace(".tsv", ".pre_round2.tsv")))
                print("installed", J(name))


def install(path, rows, backup):
    """Write through <path>.tmp + rename; keep the original once as <backup>."""
    if not os.path.exists(backup):
        with open(path, "rb") as f, open(backup + ".tmp", "wb") as g:
            g.write(f.read())
        os.replace(backup + ".tmp", backup)
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    os.replace(path + ".tmp", path)


def verified_tables(J):
    """succession.tsv / adoption.tsv with the round 2 tag checks applied (idempotent)."""
    out = {}
    for name, table in (("succession.tsv", SUCC_VERIFIED), ("adoption.tsv", ADOPT_VERIFIED)):
        rows = read_rows(J(name))
        n = 0
        for r in rows:
            k = (r[0], r[1], r[2])
            # Alabama Act No. 987 (1969): the Court of Appeals became the Court of Criminal Appeals (the row's own
            # src says so), a continuation and not a split; the Court of Civil Appeals (1 -> 2) was new
            if name == "succession.tsv" and k == ("1", "3", "19691001") and r[3] == "split":
                r[3] = "rename"
                n += 1
            if k in table and (r[-1] != "S" or r[-2] != table[k]):
                r[-2], r[-1] = table[k], "S"
                n += 1
        out[name] = (rows, n)
    return out


def next_day(d):
    x = datetime.date.fromordinal(ordinal(d) + 1)
    return x.year * 10000 + x.month * 100 + x.day


def kind_of(s):
    if s.startswith("data:first-decision"):
        return "data:first-decision"
    if s.startswith("data:last-decision"):
        return "data:last-decision"
    tag = s[-3:]
    return ("succession" if s.startswith("succession") else "known") + tag


def bound_stats(by_court):
    nf = sum(1 for v in by_court.values() if min(int(r[1]) for r in v) != 0)
    nt = sum(1 for v in by_court.values() if max((int(r[2]) or OPEN) for r in v) != OPEN)
    return nf, nt


if __name__ == "__main__":
    main()
