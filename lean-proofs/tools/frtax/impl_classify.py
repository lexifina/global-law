"""Sort every disagreement of an implementation with Lean (benchmarks random, bound, sim, examples, bareme) into
classes, each found by a rule on the return's boxes and the size of the gap. Unmatched ones are 'other'.

usage: impl_classify.py <KEY> -> runs/impl/<KEY>/classes.json and a printed table with 2 examples per class
"""
import collections, json, math, os, sys

FR = os.path.expanduser("~/fr")
r = lambda x: math.floor(x + 0.5)


def gaps(d):
    """{field: impl - ref} for the fields that differ (ref: Lean, or the stated/printed figure)"""
    ref = d["lean"] if d["ref"] == "lean" else d["expected"]
    out = {}
    for f in d["bad"]:
        a, b = d["impl"].get(f), ref.get(f)
        if a is None or b is None:
            out[f] = None
        else:
            out[f] = (a - b) if f == "NBPT" else r(a) - b
    return out


def has(b, *ks):
    return any(b.get(k) for k in ks)


def ines_rules(d, g0, b, y):
    g = {f: v for f, v in g0.items() if v is None or f == "NBPT" or abs(v) > 2}  # 1-2 EUR gaps: rounding
    if not g:
        return "rounding: INES never rounds to the euro (art. 193, 1657)"
    small = all(v is not None and abs(v) <= 2 for v in g.values())
    if any(k in g for k in ("NBPT",)):
        if has(b, "0CH") and (has(b, "0AV") or has(b, "0BT")):
            return "parts: shared-custody children with case T or a widow(er)"
        if has(b, "0AW", "0AG"):
            return "parts: case W/G half-part (art. 195)"
        return "parts: other"
    if has(b, "5TA", "5TB", "5TE") and any(f in g for f in ("RNI", "IDRS", "IDRS4")):
        return "micro-entrepreneur flat levy: INES decides the option from its lagged RFR (input not in a one-year return)"
    if b.get("1AK", 0) > b.get("1AJ", 0) or b.get("1BK", 0) > b.get("1BJ", 0):
        return "actual expenses above salary: INES caps them at the salary (production nets the excess, F7)"
    if y == 2020 and any(b.get(k, 0) > 5000 for k in ("1GH", "1HH", "1IH", "1JH")):
        return "exempt overtime cap 5,000 EUR for income 2020 (statute 7,500 EUR, loi 2020-473 art. 4)"
    if set(g) <= {"REVKIRE"} and has(b, "2OP") and has(b, "2DC", "2FU"):
        return "RFR: dividends under 2OP added back net of the 40 % allowance (art. 1417 IV 1° c: gross)"
    if set(g) <= {"REVKIRE"} and has(b, "6DD", "6EL", "6EM", "6GP"):
        return "RFR: deductible charges (6DD...) not added back"
    if set(g) <= {"REVKIRE"} and has(b, "1GH", "1HH", "1IH", "1JH"):
        return "RFR: exempt overtime added back gross (Lean/M: net of its share of the 10 % allowance)"
    if set(g) <= {"REVKIRE"} and has(b, "2OP"):
        return "RFR: dividends with 2OP added back without/with the 40 % allowance"
    if set(g) <= {"REVKIRE"}:
        return "RFR: other"
    if set(g) == {"IMPNET"} and has(b, "2DH", "2EE", "2XX", "2YY"):
        return "net tax: levies at source on life insurance (2DH...) left out of INES impot_du"
    if set(g) == {"IMPNET"} and has(b, "3VZ"):
        return "net tax: property gains (3VZ, taxed at source) left out of INES impot_du"
    if set(g) == {"IMPNET"}:
        if has(b, "7UF", "7UD", "7DB", "7GA", "7GE", "7GF", "7GG", "7EA", "7EC", "7EF", "7EB", "7ED", "7EG", "7AC"):
            return "net tax: reductions and credits (gap > 2 EUR)"
        return "net tax: other"
    if small:
        return "rounding: INES never rounds to the euro (art. 193, 1657)"
    if b.get("0DA", 9999) <= y - 65 and "RNI" in g and not has(b, "0AP", "0AF", "0AW", "0AS", "0AG"):
        return "art. 157 bis allowance (age 65+)"
    if has(b, "0AP", "0AF", "0AW", "0AS", "0AG", "0CG", "0CI") and any(f in g for f in ("IDRS", "IDRS4")):
        return "QF cap with invalidity/veteran half-parts: complementary reduction (art. 197, I, 2)"
    return "other"


def publicodes_rules(d, g, b, y):
    small = all(v is not None and abs(v) <= 2 for v in g.values())
    if "0AV" in b and b.get("0CF") and any(v is not None and v > 2 for f, v in g.items() if f in ("IDRS", "IDRS4")):
        return "widow(er) with children: QF cap ignores the widow(er)'s extra part (art. 194, 197 I 2)"
    if b.get("0DA", 9999) <= y - 65 and "RNI" in g:
        return "art. 157 bis allowance (age 65+) not modelled"
    if set(g) <= {"IDEC"} and d["impl"].get("IDEC") is not None and d["impl"]["IDEC"] > (d["impl"].get("IDRS") or 0) + 0.5:
        return "décote reported before its cap at the tax (tax after décote is right)"
    if small or (set(g) <= {"IDEC", "IDRS", "IDRS4", "RNI", "REVKIRE"} and all(v is None or abs(v) <= 2 for v in g.values())):
        return "rounding: no rounding to the euro of the allowance, gross tax or décote (art. 193, 1657; BOFiP)"
    if "IDEC" in g and d["impl"].get("IDEC", 0) > (d["impl"].get("IDRS") or 0) + 0.5:
        return "décote reported before its cap at the tax + rounding"
    return "other"


RULES = {"ines": ines_rules, "publicodes": publicodes_rules}


def main():
    key = sys.argv[1]
    rule = RULES[key]
    out = {}
    for bench in ("bareme", "examples", "random", "bound", "sim"):
        p = f"{FR}/runs/impl/{key}/{bench}_dis.jsonl"
        if not os.path.exists(p):
            continue
        cnt, ex = collections.Counter(), collections.defaultdict(list)
        for l in open(p):
            d = json.loads(l)
            if bench == "sim" and d["ref"] != "expected":
                continue
            g = gaps(d)
            cl = rule(d, g, d["boxes"] or {}, d["year"])
            cnt[cl] += 1
            if len(ex[cl]) < 3:
                ex[cl].append({"id": d["id"], "year": d["year"], "boxes": d["boxes"], "gaps": g,
                               "impl": d["impl"], "ref": d["lean"] if d["ref"] == "lean" else d["expected"]})
        out[bench] = {"counts": dict(cnt.most_common()), "examples": ex}
        print(f"== {key} {bench}: {sum(cnt.values())} disagreements")
        for cl, n in cnt.most_common():
            print(f"  {n:6d}  {cl}")
            for e in ex[cl][:2]:
                print("          ", e["year"], json.dumps(e["boxes"]), "gaps", e["gaps"])
    json.dump(out, open(f"{FR}/runs/impl/{key}/classes.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
