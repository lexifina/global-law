"""AccountsForms: statute vs form, written separately from each text, compared over grids.

Statute functions follow the Code words (sec.py, through Pub. L. 119-138).
Form functions follow the 2025 forms/instructions and the 2026 drafts.
Run: python -I model.py   (prints differences, writes grid_result.json next to this file)
"""
import itertools, json, os
from fractions import Fraction as Fr

OUT = {}
N = 0


def money(x):
    return round(float(x), 2)


# ---------------------------------------------------------------- A. HSA limit, 2025 (Form 8889 lines 3, 7)
BASE = {"S": 4300, "F": 8550}
CU = 1000


def hsa_statute(pat, age55, married):
    """s.223(b)(1),(2),(3),(8)(A). pat: 12 chars of N/S/F, coverage on the 1st of each month."""
    dec = pat[11]
    total = Fr(0)
    for m in pat:
        t = m
        if m == "N" and dec != "N":
            t = dec  # (8)(A)(ii): only months eligible "solely by reason of clause (i)" take December's plan
        if t == "N":
            continue
        total += Fr(BASE[t] + (CU if age55 else 0), 12)
    return total


def hsa_form(pat, age55, married):
    """2025 Instructions for Form 8889: line 3 rules 1-6, Line 3 Limitation Chart, line 7 worksheet."""
    dec = pat[11]

    def chart(t):
        if t == "N":
            return 0
        if t == "S":
            return 5300 if age55 else 4300
        return 9550 if (age55 and not married) else 8550

    if dec == "N":  # rule 5
        line3 = Fr(sum(chart(t) for t in pat), 12)
        fam_months = sum(1 for t in pat if t == "F")
        line7 = Fr(CU * fam_months, 12) if (age55 and married) else 0
        return line3 + line7
    considered = [dec if t == "N" else t for t in pat]  # rule 2
    a = Fr(sum(chart(t) for t in considered), 12)
    b = Fr(BASE[dec])
    any_family = "F" in considered
    if age55 and (not married or not any_family):
        b += CU  # rule 6
    if dec == "F" or b >= a:  # rule 4 and its TIP
        line3, used_b = max(a, b), b >= a
    else:
        line3, used_b = a, False
    line7 = 0
    if age55 and married and any_family:
        fam_months = 12 if (used_b and dec == "F") else sum(1 for t in considered if t == "F")
        line7 = Fr(CU * fam_months, 12)
    return line3 + line7


def patterns():
    seen = set()
    for a, b in itertools.combinations_with_replacement(range(0, 13), 2):
        for t1, t2, t3 in itertools.product("NSF", repeat=3):
            p = t1 * a + t2 * (b - a) + t3 * (12 - b)
            if p not in seen:
                seen.add(p)
                yield p


diffs = []
for pat in patterns():
    for age55 in (False, True):
        for married in (False, True):
            N += 1
            s, f = hsa_statute(pat, age55, married), hsa_form(pat, age55, married)
            if abs(s - f) > Fr(1, 2):
                diffs.append({"months": pat, "age55": age55, "married": married,
                              "statute": money(s), "form": money(f), "form_minus_statute": money(f - s)})
OUT["A_hsa_limit_2025"] = {"n_diff": len(diffs),
                           "max": max(diffs, key=lambda d: d["form_minus_statute"]) if diffs else None,
                           "min": min(diffs, key=lambda d: d["form_minus_statute"]) if diffs else None,
                           "signs": sorted({d["form_minus_statute"] > 0 for d in diffs}),
                           "sample": diffs[:6]}

# ---------------------------------------------------------------- B. 6% tax ceiling (Form 5329 lines 17, 25, 33, 41, 49)
diffs = []
for value_close, excess, late in itertools.product((0, 500, 2000, 10000), (500, 1000, 7000), (0, 1000, 7000)):
    if late > excess:
        continue
    N += 1
    statute = Fr(6, 100) * min(excess, value_close)          # s.4973(a): value "as of the close of the taxable year"
    form = Fr(6, 100) * min(excess, value_close + late)      # "(including 2025 contributions made in 2026)"
    if statute != form:
        diffs.append({"value_dec31": value_close, "excess": excess, "made_next_year_for_this_year": late,
                      "statute": money(statute), "form": money(form)})
OUT["B_value_ceiling"] = {"n_diff": len(diffs), "max": max(diffs, key=lambda d: d["form"] - d["statute"]), "sample": diffs[:5]}

# ---------------------------------------------------------------- C. Trump account excess, 2026 draft Form 5329 Part X / XI
diffs = []
LIM = 5000
for other, exempt, back_frac, value_close, earnings in itertools.product(
        (4000, 5000, 6000, 7500), (0, 1000, 1250), (0, Fr(1, 2), 1), (0, 3000, 20000), (0, 80)):
    N += 1
    excess0 = max(0, other - LIM)
    returned = excess0 * back_frac
    # statute: s.530A(h)(5) (A)+(B) less (d)(5) distributions; s.4973(a) rate and value ceiling; s.530A(d)(5)(C) 100%
    st_excess = excess0 - returned
    st_tax = Fr(6, 100) * min(st_excess, value_close) + (earnings if returned else 0)
    # form: lines 56-61 (no ceiling on line 61), lines 62-63
    line60 = max(0, 0 + excess0 - returned)
    fm_tax = Fr(6, 100) * line60 + (earnings if returned else 0)
    if st_tax != fm_tax:
        diffs.append({"nonexempt": other, "exempt": exempt, "excess_returned": money(returned),
                      "value_dec31": value_close, "statute": money(st_tax), "form": money(fm_tax)})
OUT["C_trump_excess"] = {"n_diff": len(diffs), "max": max(diffs, key=lambda d: d["form"] - d["statute"]) if diffs else None,
                         "all_have_value_below_excess": all(d["value_dec31"] < d["nonexempt"] - LIM for d in diffs)}

# ---------------------------------------------------------------- D. Qualified HSA funding distribution and s.4973(g)
diffs = []
for cov, own, employer, qhfd in itertools.product("SF", (0, 1000, 4300), (0, 1000), (0, 2000, 4300, 8550)):
    limit = BASE[cov]
    if qhfd > limit:
        continue
    N += 1
    room = max(0, limit - employer - qhfd)          # s.223(b)(4)(B),(C)
    deduction = min(own, room)
    excl_106d = min(employer, max(0, limit - qhfd))
    # statute, read literally: s.4973(g)(1) counts every contribution "neither excludable ... under section 106(d)
    # nor allowable as a deduction under section 223"; a funding distribution is excluded by s.408(d)(9) instead
    st_excess = (own - deduction) + (employer - excl_106d) + qhfd
    # form: 8889 line 13 discussion + 5329 line 47 (line 2 over line 12, plus excess employer contributions)
    fm_excess = max(0, own - room) + max(0, employer - max(0, limit - qhfd))
    if st_excess != fm_excess:
        diffs.append({"coverage": cov, "own": own, "employer": employer, "funding_distribution": qhfd,
                      "statute_literal_tax": money(Fr(6, 100) * st_excess), "form_tax": money(Fr(6, 100) * fm_excess)})
OUT["D_hsa_funding_4973g"] = {"n_diff": len(diffs),
                              "max": max(diffs, key=lambda d: d["statute_literal_tax"] - d["form_tax"]),
                              "every_diff_has_funding_distribution": all(d["funding_distribution"] > 0 for d in diffs)}

# ---------------------------------------------------------------- E. Form 8606 (2026 draft) and s.530A(h)(4)
diffs = []
agg_effect = []
for ira_val, ira_basis, ira_dist, t_val, t_basis in itertools.product(
        (0, 20000, 100000), (0, 6000, 20000), (0, 5000, 20000), (0, 30000), (0, 10000, 25000)):
    if ira_basis > ira_val + ira_dist or ira_dist > ira_val + ira_dist or t_basis > t_val or (ira_val + ira_dist) == 0:
        continue
    N += 1
    # statute: s.408(d)(2) applied to non-Trump plans alone (s.530A(h)(4)); s.72(e)(8) ratio
    st_nontax = Fr(ira_basis) * Fr(ira_dist, ira_val + ira_dist)
    # form: lines 2, 6, 7 leave Trump accounts out ("does not include Trump accounts"); lines 9-13
    line2, line6, line7 = ira_basis, ira_val, ira_dist
    line9 = line6 + line7
    line10 = min(Fr(1), Fr(line2, line9)) if line9 else Fr(0)
    fm_nontax = line10 * line7
    if st_nontax != fm_nontax:
        diffs.append((ira_val, ira_basis, ira_dist, t_val, t_basis))
    wrong = Fr(ira_basis + t_basis) * Fr(ira_dist, ira_val + ira_dist + t_val)
    if wrong != st_nontax:
        agg_effect.append(money(wrong - st_nontax))
OUT["E_8606_trump_prorata"] = {"n_diff": len(diffs),
                               "if_it_had_aggregated_range": [min(agg_effect), max(agg_effect)] if agg_effect else None}

# ---------------------------------------------------------------- F. Age and date gates
diffs = []
for birth_year, mmdd, year in itertools.product(range(2007, 2031), ((1, 1), (1, 2), (6, 30), (12, 31)), range(2026, 2047)):
    N += 1
    attains18_year = birth_year + 18                      # birthday rule (Rev. Rul. 2003-72 style)
    # s.530A(b)(2)(A) election year; s.530A(c)(2) contribution made before the year of 18; s.530A(h)(5) taxable year
    st_elect = not (attains18_year <= year)
    st_growth = year < attains18_year
    # Form 4547 instr.: "under age 18 at the end of the year ... born after December 31, 2008" for 2026
    fm_elect = birth_year > year - 18
    # draft 5329 Parts III/X: "has not attained age 18 by the end of 2026"
    fm_growth = (year - birth_year) < 18
    if st_elect != fm_elect or st_growth != fm_growth:
        diffs.append((birth_year, mmdd, year))
    # s.6434(c)(1) born after 12/31/2024 and before 1/1/2029 vs form "born in 2025-2028"
    if (2025 <= birth_year <= 2028) != (birth_year > 2024 and birth_year < 2029):
        diffs.append(("pilot", birth_year))
OUT["F_age_gates"] = {"n_diff": len(diffs)}

diffs = []
for anticipated, actual in itertools.product((True, False), repeat=2):
    N += 1
    st = 1000 if actual else 0            # s.6434(c): "a qualifying child (as defined in section 152(c))"
    fm = 1000 if anticipated else 0       # Form 4547 instr. / Notice 2025-68 B-1: "anticipated to be"
    if st != fm:
        diffs.append({"anticipated": anticipated, "qualifying_child_in_fact": actual, "statute": st, "form": fm})
OUT["F_pilot_qualifying_child"] = {"n_diff": len(diffs), "cases": diffs}

OUT["grid_points"] = N
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "grid_result.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(OUT, fh, indent=1)
print(json.dumps(OUT, indent=1))
