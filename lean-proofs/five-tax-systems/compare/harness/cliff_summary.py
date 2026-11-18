"""Group the exact notches found by analyses.py (cliffs, walls) by their statutory cause.

    python3 cliff_summary.py  -> charts/cliffs_summary.json

A notch is a one-unit rise in gross earnings that lowers net income (found on the 10-unit scan, then located to the
unit). A band is a run where the marginal rate over 1 % of the average wage exceeds 100 %. Each cause was identified
by reading which output line jumps (incomeTax, employeeSocial, benefits) and where, against the statute named; the
rules below only sort the notches into those causes, and anything they do not recognise is listed as unexplained.
"""
import json
import os
from collections import defaultdict

ROOT = os.path.join(os.path.expanduser("~"), "cmp", "compare")
AW = {c: v["aw"] for c, v in json.load(open(os.path.join(ROOT, "data", "params.json")))["countries"].items()}

CAUSES = {
    "US_table": ("US", "Tax Table and EIC table read in $50 bands: the tax (and the EIC) is the amount at the band's "
                       "midpoint (IRC §3; §32(f)), so crossing a band edge by $1 costs up to $12 of tax, and up to "
                       "about $17 where a tax band and an EIC band edge coincide",
                 "26 U.S.C. §3(a); §32(f); 2025 Form 1040 instructions, Tax Table"),
    "US_ctc_step": ("US", "Child tax credit phase-out: reduced by $50 'for each $1,000 (or fraction thereof)' of "
                          "modified AGI over $200,000 ($400,000 joint), so the first dollar of each $1,000 costs $50",
                    "26 U.S.C. §24(b)(1)-(2)"),
    "FR_61": ("FR", "Income tax under 61 euros is not collected, so the first euro that lifts it to 61 costs 61 euros",
              "CGI art. 1657, 1 bis"),
    "FR_cet": ("FR", "AGIRC-ARRCO contribution d'équilibre technique (0.14 % employee share) is due on the whole pay "
                     "once pay exceeds the social security ceiling (PASS, 47,100 euros in 2025): +66 euros at the "
                     "ceiling", "ANI du 17 novembre 2017 (AGIRC-ARRCO), CET; PASS: arrêté du 19 décembre 2024"),
    "FR_af_band": ("FR", "Allocations familiales: above each income ceiling the amount halves, smoothed by a "
                         "'complément dégressif' that withdraws one euro of benefit per euro of resources, so in that "
                         "band the marginal rate (with tax and contributions) exceeds 100 %", "CSS art. D521-1, II; D521-3"),
    "UK_marriage_allowance": ("UK", "Marriage allowance (a £1,260 transfer of personal allowance, worth £252) is lost "
                                    "when the recipient's income exceeds the basic rate limit: £1 more costs £252",
                              "ITA 2007 ss. 55A-55E (s. 55B condition on the recipient's rate)"),
    "UK_hicbc_steps": ("UK", "High income child benefit charge: 1 % of the child benefit for every £200 of adjusted net "
                             "income above £60,000, so each £200 step costs 1 % of the benefit at once (£22.52 for two "
                             "children)", "ITEPA 2003 s. 681C"),
    "JP_insured_second_earner": ("JP", "The '1.06 million yen wall': a dependent spouse who earns 88,000 yen a month or more "
                                       "(large employer) becomes an insured employee and pays health, care and pension "
                                       "premiums on the whole wage at once (+163,354 yen a year)",
                                 "健康保険法 第3条 第1項 第9号; 厚生年金保険法 第12条 第5号 (短時間労働者); 被扶養者: 健康保険法 第3条 第7項"),
    "JP_insured_artifact": ("JP", "Model boundary, not a law: below 88,000 yen a month a worker who is nobody's dependent "
                                  "would pay national pension and national health insurance, which the JP model leaves out "
                                  "(listed in its unsupported field); the jump at 1,056,000 yen for a lone earner is the "
                                  "model's", "JP model EXAMPLE.md (not modelled: 国民年金, 国民健康保険)"),
    "JP_grade": ("JP", "Premiums are charged on standard monthly remuneration grades: one yen of monthly pay across a "
                       "grade boundary raises the year's health and pension premiums by the grade step (10,731 to "
                       "35,776 yen a year in this scan), less the tax saved on the deduction",
                 "健康保険法 第40条; 厚生年金保険法 第20条 (標準報酬月額)"),
    "JP_premium_rounding": ("JP", "Premiums rounded to the yen each month (fractions of 50 sen and under dropped): one "
                                  "yen of pay can add up to 12 yen of premiums a year", "通貨の単位及び貨幣の発行等に関する法律 第3条; 健康保険法施行令"),
    "JP_per_capita_levy": ("JP", "Resident tax per-capita levy (4,000 yen) and forest environment tax (1,000 yen) start "
                                 "in full once income exceeds the non-taxable limit (450,000 yen of income for a single "
                                 "person in the Tokyo wards; higher for single parents)",
                           "地方税法 第24条の5 第3項, 第295条 第3項; 森林環境税及び森林環境譲与税に関する法律 第4条"),
    "JP_basic_deduction_steps": ("JP", "The 2025 basic deduction falls in steps with total income (950,000 / 880,000 / "
                                       "680,000 / 630,000 / 580,000 yen at 1.32 / 3.36 / 4.89 / 6.55 million yen of income): "
                                       "one yen across a step costs 5,000 to 10,150 yen of income tax",
                                 "所得税法 第86条; 租税特別措置法 第41条の16の2 (令和7年度改正)"),
    "JP_spouse_deduction_steps": ("JP", "The principal's spouse special deduction falls in steps as the spouse's income "
                                        "rises: one yen across a step raises the household's income tax (and resident tax)",
                                  "所得税法 第83条の2; 地方税法 第314条の2"),
    "JP_single_parent_cliff": ("JP", "Single-parent deduction (350,000 yen; 300,000 for resident tax) lost in full once total "
                                     "income exceeds 5 million yen: one yen more costs 68,797 yen here",
                               "所得税法 第2条 第1項 第31号 ハ, 第81条; 地方税法 第292条 第1項 第12号の2, 第314条の2"),
    "JP_shotokuwari_relief": ("JP", "Resident income levy just above the non-taxable limit for a family: the levy may not "
                                    "leave income below the limit, so it rises one yen per yen of income until the full levy "
                                    "is due (a 100 % band); the salary-income table's 4,000-yen steps turn it into notches",
                              "地方税法 附則第3条の3 第2項, 第5項 (所得割の非課税限度額); 所得税法 別表第五"),
    "JP_rounding": ("JP", "Taxable income is cut to 1,000 yen and the tax to 100 yen, and below 6.6 million yen salary "
                          "income is read from a table in 4,000-yen steps: one yen can cost 100-900 yen of income and "
                          "resident tax", "国税通則法 第118条, 第119条; 地方税法 第20条の4の2; 所得税法 第28条 第4項, 別表第五"),
    "DE_minijob": ("DE", "Minijob boundary (6,672 euros a year, 556 a month): below it the pay is taxed flat by the "
                         "employer and stays out of the joint assessment, and the employee pays no contributions in "
                         "the model; one euro more puts the whole pay into the couple's splitting tariff (married: "
                         "-1,509 euros) and, for the childless, starts the care-insurance surcharge (0.6 points), "
                         "charged on the transition zone's whole contribution base (about 372 euros a month at the "
                         "boundary) where the employee's own share starts from nothing (childless single: -26 euros "
                         "for 1 euro; with a child the step is 0.30 euros a year)",
                   "EStG § 40a (2), § 40 (3); SGB IV § 8 (1a), § 20 (2a); SGB XI § 55 (3), § 58 (1)"),
}


def classify(c, fam, g, ch, dnet):
    it = ch.get("incomeTax", 0)
    soc = ch.get("employeeSocial", 0)
    ben = ch.get("benefits", 0)
    if c == "US":
        if fam == "single_parent_2" and g > 200000 and 45 <= it <= 60:
            return "US_ctc_step"
        if abs(dnet) <= 25 and ben == 0 and g < 140000:  # Tax Table: taxable income under $100,000
            return "US_table"
    if c == "FR":
        if 60 <= it <= 63 and abs(soc) <= 2:
            return "FR_61"
        if 60 <= soc <= 70:
            return "FR_cet"
        if ben < 0 and abs(dnet) <= 5:
            return "FR_af_band"
        if abs(dnet) <= 3 and ben == 0:
            return "FR_af_band"
    if c == "UK":
        if 240 <= it <= 260:
            return "UK_marriage_allowance"
        if -24 <= ben <= -21:
            return "UK_hicbc_steps"
    if c == "DE":
        if it > 1000 or (abs(g - 6680) <= 10 and soc > 0):
            return "DE_minijob"
    if c == "JP":
        loc = ch.get("localIncomeTax", 0)
        if fam == "single_parent_2" and it >= 30000 and loc >= 25000:
            return "JP_single_parent_cliff"
        if soc >= 100000:
            return "JP_insured_second_earner" if fam.startswith("second earner") else "JP_insured_artifact"
        if soc >= 1000:
            return "JP_grade"
        if abs(dnet) <= 15 and it == 0 and loc == 0:
            return "JP_premium_rounding"
        if 4000 <= loc <= 5100 and abs(it) < 100:
            return "JP_per_capita_levy"
        if loc >= 1000 and abs(it) <= 200 and abs(soc) <= 1:
            return "JP_shotokuwari_relief"
        if it >= 1000 and (fam == "couple_2earner_2" or fam == "second earner (married)"):
            return "JP_spouse_deduction_steps"
        if it >= 2000 and fam.startswith("second earner") and "married" in fam and "unmarried" not in fam:
            return "JP_spouse_deduction_steps"
        if it >= 2500:
            return "JP_basic_deduction_steps"
        if 0 <= it <= 500 and 0 <= loc <= 600:
            return "JP_rounding"
    return None


def main():
    cl = json.load(open(os.path.join(ROOT, "charts", "cliffs.json")))
    wl = json.load(open(os.path.join(ROOT, "charts", "walls_second_earner.json")))
    groups = defaultdict(list)
    unexplained = []
    for e in cl["exact_notches"]:
        k = classify(e["country"], e["family"], e["gross_after"], e["changes"], e["net_change"])
        rec = {"family": e["family"], "gross": e["gross_after"], "gross_aw": e["gross_aw"],
               "net_change": round(e["net_change"], 2), "changes": e["changes"]}
        (groups[k].append(rec) if k else unexplained.append(dict(rec, country=e["country"])))
    for e in wl["net_falls"]:
        fam2 = f"second earner ({'married' if e['married'] else 'unmarried'})"
        k = classify(e["country"], fam2, e["spouse_after"], e["changes"], e["net_change"])
        rec = {"family": f"second earner ({e['kids']}, {'married' if e['married'] else 'unmarried'}), principal at 1 x AW",
               "gross": e["spouse_after"], "gross_aw": e["spouse_aw"], "net_change": round(e["net_change"], 2),
               "changes": e["changes"], "resolution": "10 units"}
        (groups[k].append(rec) if k else unexplained.append(dict(rec, country=e["country"])))
    bands = [e for e in cl["coarse_events"] if e["kind"] == "mtr_above_100"]
    out = {"title": "Notches and >100 % bands by cause", "sources": [os.path.join(ROOT, "charts", "cliffs.json"),
                                                                       os.path.join(ROOT, "charts", "walls_second_earner.json")],
           "causes": {}, "bands_mtr_above_100": bands, "unexplained": unexplained}
    for k, recs in groups.items():
        c, text, cite = CAUSES[k]
        worst = min(recs, key=lambda r: r["net_change"])
        fams = sorted(set(r["family"] for r in recs))
        out["causes"][k] = {"country": c, "cause": text, "law": cite, "notches": len(recs), "families": fams,
                            "first_gross": min(r["gross"] for r in recs), "last_gross": max(r["gross"] for r in recs),
                            "worst": worst, "examples": sorted(recs, key=lambda r: r["gross"])[:5]}
    json.dump(out, open(os.path.join(ROOT, "charts", "cliffs_summary.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in out["causes"].items():
        print(k, v["notches"], "notches; worst", v["worst"]["net_change"], "at", v["worst"]["gross"], v["families"])
    print("bands >100%:", [(b["country"], b["family"], b["g0"], b["g1"]) for b in bands])
    print("unexplained:", len(unexplained))
    for u in unexplained[:30]:
        print("  ", u)


if __name__ == "__main__":
    main()
