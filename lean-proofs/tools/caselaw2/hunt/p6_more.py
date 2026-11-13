"""Pattern 6, the named cases: probes of the rule space with the Python reference (ref/precedent_ref.py).

    python p6_more.py   -> data/p6f_named_probes.tsv, data/p6g_commission.tsv, data/p6h_rule_values.tsv

F  successor structures named in the brief (Kentucky 1976, D.C. 1971, New Jersey 1948, Eleventh Circuit 1981, Tenth
   Circuit 1929, Federal Circuit 1982): for the last decision of the old court before the cut and the first after it,
   the force on each court of the new structure, one year later and today.
G  commission opinions: decisions by notation and the force each notation carries on the adopting court.
H  the rule values per system that make the forum matter (trialScope, horizontal, firstInTimeControls,
   stateFollowsCircuit), counted.
"""
import os, sys
from collections import Counter, defaultdict
import hcommon as C

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ref"))
import precedent_ref as R  # noqa: E402
import p6_rules as P6      # noqa: E402

TODAY = 20261112
# (label, old court, cut date, destinations)
NAMED = [
    ("Kentucky 1976", 913, 19760101, [914, 917]),
    ("D.C. 1971", 514, 19710201, [627]),
    ("New Jersey 1948 (Court of Errors and Appeals)", 1094, 19480915, [1096, 1099]),
    ("New Jersey 1948 (old Supreme Court)", 1095, 19480915, [1096, 1099]),
    ("Eleventh Circuit 1981 (old Fifth)", 346, 19811001, [241, 346]),
    ("Tenth Circuit 1929 (Eighth)", 430, 19290301, [219, 430]),
    ("Federal Circuit 1982 (CCPA)", 655, 19821001, [520]),
    ("Federal Circuit 1982 (Court of Claims)", 654, 19821001, [520]),
    ("Texas Commission of Appeals", 2948, 19450901, [2927]),
]


def main():
    cs = P6.courts()
    D, E = P6.load()
    by_court = defaultdict(list)
    for n in range(len(D.court)):
        c = D.court[n]
        if c >= 0 and D.date[n] > 0:
            by_court[c].append(n)
    for c in by_court:
        by_court[c].sort(key=lambda n: D.date[n])
    pubcode = R.PUB_I.get("published")
    rows = []
    for label, old, cut, dsts in NAMED:
        decs = by_court.get(old, [])
        before = [n for n in decs if D.date[n] < cut and D.pub[n] == pubcode]
        after = [n for n in decs if D.date[n] >= cut and D.pub[n] == pubcode]
        sysn = cs.get(dsts[0], {}).get("system")
        trial = [c for c, v in cs.items() if v["system"] == sysn and v["tier"] == "T"
                 and (sysn != 0 or v["circuit"] == cs[dsts[0]].get("circuit"))][:1]
        for tag, probe in (("last before the cut", before[-1] if before else None),
                           ("first after the cut", after[0] if after else None)):
            if probe is None:
                rows.append([label, tag, "-", "-", "-", "-", "-", "-", len(before), len(after)])
                continue
            for dst in dsts + trial:
                t1 = max(cut, D.date[probe]) + 10000
                f1 = E.force(probe, None, dst, t1, t1)
                f2 = E.force(probe, None, dst, TODAY, TODAY)
                rows.append([label, tag, probe, D.date[probe], cs.get(old, {}).get("name"), cs.get(dst, {}).get("name"),
                             "%s:%s" % (f1[0], f1[1]), "%s:%s" % (f2[0], f2[1]), len(before), len(after)])
    C.write_tsv(os.path.join(C.HUNT, "data", "p6f_named_probes.tsv"), rows,
                ["case", "probe", "probe_node", "probe_date", "source_court", "destination_court", "force_one_year_after",
                 "force_today", "source_published_decisions_before", "source_published_decisions_after"])
    for r in rows:
        C.log("\t".join(str(x) for x in r))

    # G commission opinions
    com = Counter()
    ex = defaultdict(list)
    for p in C.read_tsv(os.path.join(C.DATA, "commission.tsv"), header=False):
        n = int(p[0])
        if not D.has(n):
            continue
        k = (cs.get(D.court[n], {}).get("name", "?"), p[2])
        com[k] += 1
        if len(ex[k]) < 3:
            ex[k].append(n)
    grows = []
    for (court, notation), v in sorted(com.items(), key=lambda kv: -kv[1]):
        n = ex[(court, notation)][0]
        dst = 2927 if "Texas" in court else D.court[n]
        t = D.date[n] + 10000
        f = E.force(n, None, dst, t, t)
        a = E.authority(n, None, None, dst, t)
        grows.append([court, notation, v, cs.get(dst, {}).get("name"), "%s:%s" % (a[0], a[1]), "%s:%s" % (f[0], f[1]),
                      ",".join(map(str, ex[(court, notation)]))])
    C.write_tsv(os.path.join(C.HUNT, "data", "p6g_commission.tsv"), grows,
                ["court", "notation", "decisions", "probe_destination", "authority", "force", "examples"])
    for r in grows[:25]:
        C.log("\t".join(str(x) for x in r))

    # H rule values
    names = {}
    for p in C.read_tsv(os.path.join(C.DATA, "courts2.tsv"), header=False):
        names.setdefault(int(p[4]), p[3])
    rv = Counter()
    for p in C.read_tsv(os.path.join(C.DATA, "system_rules.tsv"), header=False):
        if p[1] != "unpubForce":
            rv[(p[1], p[2])] += 1
    hrows = [[k[0], k[1], v] for k, v in sorted(rv.items(), key=lambda kv: (kv[0][0], -kv[1]))]
    C.write_tsv(os.path.join(C.HUNT, "data", "p6h_rule_values.tsv"), hrows, ["rule", "value", "systems_or_courts"])
    for r in hrows:
        C.log("\t".join(str(x) for x in r))


if __name__ == "__main__":
    main()
