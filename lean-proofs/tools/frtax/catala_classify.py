"""Classify every Catala / M / Lean disagreement in a catala_compare.py run.

usage: catala_classify.py rundir [rundir ...]   -> rundir/classes.txt (and a combined table on stdout)

Parts classes (first rule that matches; a return can carry several features, the others are listed):
  P1 attached adult children (0DJ): Catala adds a flat half part per person (art. 196 B, first sentence), M and
     Lean count them as dependants (rank, widow(er) base, box T)
  P2 disabled person under the roof (0CR, art. 196 A bis): Catala adds only the disability half part
  P3 box W or S with the person under 75 (art. 195, 1, f and 6): Catala has no ages
  P4 widow(er) whose children are all in shared residence: Catala keeps the single base
  P5 box G (war widow's pension) with children, not a couple: Catala adds the art. 195, 5 half part
  P6 couple with P or F and S: Catala adds both art. 195, 3 and 195, 6
  P7 box L with box N (not living alone): Catala has no box N
  P? anything else
RBG classes:
  R1 a person with two or more kinds of pension (1AS, 1AZ, 1AO, 1AL, 1AM): Catala takes the 10 % allowance, its
     rounding and its minimum per kind of pension (art. 158, 5, a)
  R? anything else
Refusals: Catala assertion (which check) against M's anomaly.
"""
import collections, json, os, sys


def fam(b):
    return {k: v for k, v in b.items() if k[0] == "0" and k[:2] not in ("0F", "0H", "0J")}


def over74(b, year, box):
    v = b.get(box, 0)
    return v > 0 and v <= year - 74


def parts_features(b, year):
    couple = "0AM" in b or "0AO" in b
    f = []
    if b.get("0DJ"):
        f.append("P1")
    if b.get("0CR"):
        f.append("P2")
    if ("0AW" in b and not over74(b, year, "0DA")) or (
            "0AS" in b and not (over74(b, year, "0DA") or over74(b, year, "0DB"))):
        f.append("P3")
    if "0AV" in b and not b.get("0CF") and b.get("0CH"):
        f.append("P4")
    if "0AG" in b and not couple and (b.get("0CF") or b.get("0CH")):
        f.append("P5")
    if couple and "0AS" in b and ("0AP" in b or "0AF" in b):
        f.append("P6")
    if "0AL" in b and "0AN" in b:
        f.append("P7")
    return f or ["P?"]


def rbg_features(b):
    multi = any(sum(1 for t in "SZOLM" if b.get(f"1{p}{t}", 0) > 0) >= 2 for p in "ABCDEF")
    return ["R1"] if multi else ["R?"]


def main():
    tot = collections.defaultdict(collections.Counter)
    for rundir in sys.argv[1:]:
        rows = [json.loads(l) for l in open(f"{rundir}/rows.jsonl")]
        cls = collections.Counter()
        ex = {}
        ref_cnt = collections.Counter()
        for r in rows:
            b, y = r["boxes"], r["year"]
            c = r["catala"]
            m, l = r["m"] or {}, r["lean"] or {}
            mref = "_refused" in m
            # refusals
            if "ERR" in c:
                key = ("refusal", c["ERR"], "M refuses too" if mref else ("M computes" if m else "M not run"))
                ref_cnt[key] += 1
                continue
            ref = m.get("NBPT") if not mref else None
            lref = l.get("NBPT")
            target = ref if ref is not None else lref
            if target is not None and abs(c["NBPT"] - target) > 0.01:
                fs = parts_features(b, y)
                k = (fs[0], round(c["NBPT"] - target, 2), "vs M" if ref is not None else "vs Lean (M refuses)")
                cls[k] += 1
                ex.setdefault(k, (r["id"], y, fam(b), c["NBPT"], ref, lref, fs))
            cp, mp = r["catala_proj"], r["m_proj"] or {}
            if "RBG" in cp and "_refused" not in mp and mp:
                if abs(cp["RBG"] - mp.get("RBG1", 0.0)) > 0.5:
                    fs = rbg_features(b)
                    k = (fs[0], "RBG", "vs M")
                    cls[k] += 1
                    ex.setdefault(k, (r["id"], y, {k2: v for k2, v in b.items() if k2[0] in "15" and k2 not in r["dropped"]},
                                      cp["RBG"], mp.get("RBG1"), (r["lean_proj"] or {}).get("RNG"), fs))
        with open(f"{rundir}/classes.txt", "w") as f:
            f.write(f"{rundir}: {len(rows)} returns\n\nDisagreements (class, Catala - reference, reference): count, example\n")
            for k, v in sorted(cls.items(), key=lambda x: (x[0][0], -x[1])):
                f.write(f"{v:6d}  {k}  e.g. {ex[k]}\n")
                tot[rundir][k[0]] += v
            f.write("\nCatala stops (assertion / no rule) and what M does:\n")
            for k, v in ref_cnt.most_common():
                f.write(f"{v:6d}  {k}\n")
        print(open(f"{rundir}/classes.txt").read())
    print("per class:", {k: dict(v) for k, v in tot.items()})


if __name__ == "__main__":
    main()
