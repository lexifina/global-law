"""Pattern 6: 'loopholes' in the rules of precedent themselves, found by searching the rule space (the court tables,
succession, adoption, system rules) with the Python reference (ref/precedent_ref.py, which implements the Lean Spec and
was differentially tested against it) and counting the real decisions each combination touches.

    python p6_rules.py   -> data/p6_*.tsv and a summary on stderr

A  adoption relativity: a decision adopted by two heirs (old Fifth Circuit -> Fifth and Eleventh; D.C. Circuit ->
   D.C. Court of Appeals) that one heir overrules stays binding on the other; the Spec's status is global
   (Spec.citesOverruled: 'Status is not relative to the citing court'), so the other heir's later citations are
   reported as citing overruled law.
B  successor gaps: a succession with no binding adoption row: the old court's decisions bind no court of the new
   structure (orphaned precedent).
C  dual courts of last resort (Texas, Oklahoma): neither binds the other (H2.dualLastResort); the intermediate courts
   are bound by both; treatments between them are direct conflicts no court can resolve except SCOTUS on federal law.
D  unpublished-opinion windows: one decision binding in one court and not in another, or binding only because of the
   date it issued (unpubForce windows x adoption).
E  forum choice: a state court declines to follow a federal court (or the reverse) on the same question; neither
   binds the other (no_cross_system), so the answer depends on the forum.
"""
import json, os, sys
from collections import Counter, defaultdict
import hcommon as C

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ref"))
import precedent_ref as R  # noqa: E402

STATUS_CHANGING = {"overruled", "abrogated", "recededFrom", "disapproved"}


def load():
    D = R.Data(C.DATA, C.log)
    E = R.Engine(D, firm=False)
    E.admit()
    E.asof = 20261112
    return D, E


def courts():
    cs = {}
    for p in C.read_tsv(os.path.join(C.DATA, "courts2.tsv"), header=False):
        cs.setdefault(int(p[0]), dict(name=p[3], system=int(p[4]), tier=p[5], circuit=int(p[7] or 0)))
    return cs


def treatments():
    return [dict(id=p[0], by=int(p[1]), target=int(p[2]), date=int(p[3]), kind=p[4], scope=p[5],
                 explicit=p[7], quote=p[11], part=p[13]) for p in C.read_tsv(os.path.join(C.DATA, "treatments.tsv"), header=False)]


def edges_into(nodes):
    out = defaultdict(set)
    for a, b in C.iter_edges(want_cited=set(nodes)):
        out[b].add(a)
    return out


# ---------------------------------------------------------------------------------------------------------------- A
def part_a(D, E, cs, TR):
    adopt = [(a, s, u, f) for (a, s, u, f, force, tag) in D.adoption if force == "binding"]
    heirs = defaultdict(list)
    for a, s, u, f in adopt:
        heirs[s].append((a, u, f))
    rows = []
    for t in TR:
        if t["kind"] not in STATUS_CHANGING or t["explicit"] != "1":
            continue
        X, B = t["target"], t["by"]
        if not D.has(X) or not D.has(B):
            continue
        sx, sb = D.court[X], D.court[B]
        for a, u, f in heirs.get(sx, []):
            if D.date[X] > u or D.date[B] <= u:
                continue
            # B is the source court after the split, or the adopter: the other heir is the one not acting
            if sb == sx:
                other = a
            elif sb == a:
                other = sx
            else:
                continue
            if cs.get(other, {}).get("tier") not in ("A", "L"):
                continue
            pw = E.can_change(B, X)
            st = E.status(X, None, 20261112, 20261112)
            # force of X on the other heir after B acted, ignoring status (authority) vs with status (force)
            later = D.date[B] + 10000
            auth = E.authority(X, None, None, other, later)
            frc = E.force(X, None, other, later, later)
            rows.append(dict(target=X, by=B, by_court=sb, other=other, kind=t["kind"], scope=t["scope"], date=t["date"],
                             power=pw[0] + ":" + pw[1], status=st[0] + ":" + st[1], authority_on_other=auth[0],
                             force_on_other=frc[0], quote=t["quote"][:250]))
    # the other heir's later citations, and how many the runner reports as citesOverruled
    cites = edges_into({r["target"] for r in rows})
    finds = set()
    for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")):
        if r[0] == "citesOverruled":
            finds.add((int(r[1]), int(r[2])))
    meta = C.nodes(set().union(*cites.values()) | {r["target"] for r in rows} | {r["by"] for r in rows}) if cites else {}
    out = []
    for r in rows:
        later = [c for c in cites.get(r["target"], ()) if c in meta and meta[c]["court2"] == r["other"]
                 and meta[c]["date"] > r["date"]]
        flagged = [c for c in later if (c, r["target"]) in finds]
        mt, mb = meta.get(r["target"], {}), meta.get(r["by"], {})
        out.append([r["target"], mt.get("name", "")[:60], mt.get("cite", "").split("|")[0], mt.get("date"),
                    r["by"], mb.get("name", "")[:60], mb.get("cite", "").split("|")[0], r["date"],
                    cs[r["by_court"]]["name"], cs[r["other"]]["name"], r["kind"], r["scope"], r["power"], r["status"],
                    r["authority_on_other"], r["force_on_other"], len(later), len(flagged),
                    ",".join(str(c) for c in sorted(later)[:8]), r["quote"]])
    out.sort(key=lambda x: (-x[16], x[7]))
    C.write_tsv(os.path.join(C.HUNT, "data", "p6a_adoption_relativity.tsv"), out,
                ["target", "target_name", "target_cite", "target_date", "by", "by_name", "by_cite", "by_date",
                 "by_court", "other_heir", "kind", "scope", "power", "status_global", "authority_on_other_heir",
                 "force_on_other_heir_spec", "other_heir_citations_after", "flagged_citesOverruled",
                 "sample_citers", "quote"])
    C.log("A adoption relativity: treatments", len(out), "with power", sum(1 for x in out if x[12].startswith("yes")),
          "other-heir citations after", sum(x[16] for x in out), "flagged citesOverruled", sum(x[17] for x in out))
    return out


# ---------------------------------------------------------------------------------------------------------------- B
def part_b(D, E, cs):
    adopt = defaultdict(list)
    for (a, s, u, f, force, tag) in D.adoption:
        adopt[(a, s)].append((u, f, force, tag))
    by_court = defaultdict(list)
    for n in range(len(D.court)):
        c = D.court[n]
        if c >= 0:
            by_court[c].append(n)
    rows = []
    for (old, new, date, kind, tag) in D.succession:
        if old == new:
            continue
        ad = adopt.get((new, old), [])
        old_decs = [n for n in by_court.get(old, []) if 0 < D.date[n] < date]
        if not old_decs:
            rows.append([old, cs.get(old, {}).get("name"), new, cs.get(new, {}).get("name"), date, kind, tag,
                         ";".join("%s/%s/%s" % (x[1], x[2], x[3]) for x in ad) or "-", 0, "-", "-", "-", 0, 0])
            continue
        probe = max(old_decs, key=lambda n: D.date[n])
        t = date + 10000
        f_new = E.force(probe, None, new, t, t)
        # a trial-level court of the new structure
        nc = cs.get(new, {})
        trial = [c for c, v in cs.items() if v["system"] == nc.get("system") and v["tier"] == "T"
                 and (nc.get("system") != 0 or v["circuit"] == nc.get("circuit"))]
        f_tr = E.force(probe, None, trial[0], t, t) if trial else ("-", "-")
        gap = int(f_new[0] not in ("binding", "bindingAbsentConflict") and f_tr[0] not in ("binding", "bindingAbsentConflict"))
        rows.append([old, cs.get(old, {}).get("name"), new, nc.get("name"), date, kind, tag,
                     ";".join("%s/%s/%s" % (x[1], x[2], x[3]) for x in ad) or "-", len(old_decs), probe,
                     "%s:%s" % f_new[:2], ("%s@%s:%s" % (trial[0], f_tr[0], f_tr[1])) if trial else "-", gap, 0])
    # later citations of the orphaned decisions by courts of the new structure
    gaps = [r for r in rows if r[12] == 1]
    want = set()
    for r in gaps:
        want.update(n for n in by_court.get(r[0], []) if 0 < D.date[n] < r[4])
    cites = edges_into(want) if want else {}
    for r in gaps:
        sysn = cs.get(r[2], {}).get("system")
        cnt = 0
        for n in by_court.get(r[0], []):
            if 0 < D.date[n] < r[4]:
                for c in cites.get(n, ()):
                    if D.has(c) and D.date[c] >= r[4] and cs.get(D.court[c], {}).get("system") == sysn:
                        cnt += 1
        r[13] = cnt
    C.write_tsv(os.path.join(C.HUNT, "data", "p6b_successor_gaps.tsv"), rows,
                ["old_court", "old_name", "new_court", "new_name", "date", "kind", "tag", "adoption(filter/force/tag)",
                 "old_decisions", "probe_node", "force_on_new", "force_on_trial", "gap", "later_citations_in_new_structure"])
    C.log("B successions", len(rows), "gaps", len(gaps), "orphaned decisions", sum(r[8] for r in gaps),
          "later citations", sum(r[13] for r in gaps))
    return rows


# ---------------------------------------------------------------------------------------------------------------- C
DUAL = {43: (2927, 2928), 36: (2574, 2571)}   # Texas: Supreme Court (civil), Court of Criminal Appeals; Oklahoma


def part_c(D, E, cs, TR):
    rows = []
    for sysn, (civ, crim) in DUAL.items():
        for t in TR:
            if not (D.has(t["by"]) and D.has(t["target"])):
                continue
            a, b = D.court[t["by"]], D.court[t["target"]]
            if {a, b} == {civ, crim} and t["kind"] in STATUS_CHANGING | {"declinedToFollow", "questioned", "limited", "criticized"}:
                pw = E.can_change(t["by"], t["target"])
                # an intermediate court of the system: bound by both?
                inter = [c for c, v in cs.items() if v["system"] == sysn and v["tier"] == "A"]
                tt = D.date[t["by"]] + 1
                fb = E.force(t["by"], None, inter[0], tt, tt) if inter else ("-",)
                fx = E.force(t["target"], None, inter[0], tt, tt) if inter else ("-",)
                rows.append([sysn, t["by"], cs[a]["name"], t["target"], cs[b]["name"], t["date"], t["kind"], t["scope"],
                             pw[0] + ":" + pw[1], "%s:%s" % (fb[0], fb[1]), "%s:%s" % (fx[0], fx[1]), t["quote"][:300]])
    meta = C.nodes({r[1] for r in rows} | {r[3] for r in rows})
    for r in rows:
        r[1:2] = [r[1], meta.get(r[1], {}).get("name", "")[:60] + " " + meta.get(r[1], {}).get("cite", "").split("|")[0]]
        r[4:5] = [r[4], meta.get(r[4], {}).get("name", "")[:60] + " " + meta.get(r[4], {}).get("cite", "").split("|")[0]]
    C.write_tsv(os.path.join(C.HUNT, "data", "p6c_dual_high_courts.tsv"), rows,
                ["system", "by", "by_name", "by_court", "target", "target_name", "target_court", "date", "kind", "scope",
                 "power", "force_of_by_on_intermediate", "force_of_target_on_intermediate", "quote"])
    C.log("C dual high courts: treatments between them", len(rows), Counter((r[0], r[8]) for r in rows))
    return rows


# ---------------------------------------------------------------------------------------------------------------- D
def part_d(D, E, cs):
    """For every unpublished/table/memorandum decision: its force on its own court and, where an adoption row reaches
    it, on the adopter, one year after it issued. Count decisions whose force differs between the heirs, and decisions
    binding only because of a date window."""
    PUB = {v: k for k, v in R.PUB_I.items()} if hasattr(R, "PUB_I") else None
    unpub_codes = {R.PUB_I[k] for k in ("unpublished", "table", "summaryOrder", "memorandum") if k in R.PUB_I}
    adopt = defaultdict(list)
    for (a, s, u, f, force, tag) in D.adoption:
        adopt[s].append((a, u, f, force))
    cnt = Counter()
    examples = defaultdict(list)
    for n in range(len(D.court)):
        if D.court[n] < 0 or D.pub[n] not in unpub_codes or D.date[n] == 0:
            continue
        c = D.court[n]
        heirs = adopt.get(c, [])
        own = None
        key = None
        if heirs:
            t = D.date[n] + 10000
            own = E.force(n, None, c, t, t)[0]
            for a, u, f, force in heirs:
                fa = E.force(n, None, a, max(t, 19811001 if a == 241 else t), max(t, 19811001 if a == 241 else t))[0]
                key = ("adopted", cs[c]["name"], cs[a]["name"], own, fa, "before" if D.date[n] <= u else "after")
                cnt[key] += 1
                if len(examples[key]) < 5:
                    examples[key].append(n)
        cap = E.unpub_cap(n, [k for k, v in R.PUB_I.items() if v == D.pub[n]][0])[0]
        if cap in ("binding", "bindingAbsentConflict"):
            k2 = ("bindingUnpublished", cs[c]["name"], str(D.date[n])[:4] if False else ("pre1996" if D.date[n] < 19960101 else "1996+"))
            cnt[k2] += 1
            if len(examples[k2]) < 5:
                examples[k2].append(n)
    rows = [[*k, v, ",".join(map(str, examples[k]))] for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])]
    C.write_tsv(os.path.join(C.HUNT, "data", "p6d_unpublished_windows.tsv"), [[" | ".join(map(str, r[:-2])), r[-2], r[-1]] for r in rows],
                ["window", "decisions", "examples"])
    C.log("D unpublished windows", len(rows))
    return rows


# ---------------------------------------------------------------------------------------------------------------- E
def part_e(D, E, cs, TR):
    rows = []
    for t in TR:
        if not (D.has(t["by"]) and D.has(t["target"])):
            continue
        a, b = D.court[t["by"]], D.court[t["target"]]
        sa, sb = cs.get(a, {}).get("system"), cs.get(b, {}).get("system")
        if sa is None or sb is None or sa == sb:
            continue
        if t["kind"] not in ("declinedToFollow", "disapproved", "overruled", "questioned", "criticized", "limited"):
            continue
        d = D.date[t["by"]]
        f = E.force(t["target"], None, a, d, d)
        pw = E.can_change(t["by"], t["target"])
        rows.append([t["by"], cs[a]["name"], cs[a]["tier"], t["target"], cs[b]["name"], cs[b]["tier"], t["date"],
                     t["kind"], "state->federal" if sb == 0 else ("federal->state" if sa == 0 else "state->state"),
                     "%s:%s" % (f[0], f[1]), pw[0] + ":" + pw[1], t["quote"][:300]])
    C.write_tsv(os.path.join(C.HUNT, "data", "p6e_forum_choice.tsv"), rows,
                ["by", "by_court", "by_tier", "target", "target_court", "target_tier", "date", "kind", "direction",
                 "force_of_target_on_by", "power", "quote"])
    C.log("E cross-system departures", len(rows), Counter((r[8], r[7], r[9].split(":")[0]) for r in rows).most_common(12))
    return rows


def main():
    cs = courts()
    TR = treatments()
    D, E = load()
    which = sys.argv[1:] or ["A", "B", "C", "D", "E"]
    if "A" in which:
        part_a(D, E, cs, TR)
    if "B" in which:
        part_b(D, E, cs)
    if "C" in which:
        part_c(D, E, cs, TR)
    if "E" in which:
        part_e(D, E, cs, TR)
    if "D" in which:
        part_d(D, E, cs)


if __name__ == "__main__":
    main()
