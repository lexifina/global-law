"""Effect of the three OECD errors on the OECD's own average tax wedge (Taxing Wages 2026, 2025).

    python3 oecd_error_effects.py  -> charts/oecd_error_effects.json

wedge = (income tax + state/local tax + employee SSC + employer SSC - cash transfers) / labour costs, the OECD's
definition; reproduces the OECD's published AV_TW (France M100_100: 44.296 %). The corrected wedge replaces the line in
error by the statute's figure: France from the Lean model (charts/oecd_check.json); Japan from the Japan model's theorem
oecd_single_parent_aw67 (income tax 41,200 yen with the OECD's own premiums) and 10 % of the 300,000-yen resident-tax
deduction (approximate); US: $25 of deduction at 12 %.
"""
import csv, json, os
ROOT = os.path.join(os.path.expanduser("~"), "cmp", "compare")
d = json.load(open(os.path.join(ROOT, "data/oecd/tw_cou_xdc.json")))
chk = {(r["country"], r["type"]): r for r in json.load(open(os.path.join(ROOT, "charts/oecd_check.json")))["rows"]}


def wedge(x, cgitfp=None, slt=None):
    it = x["CGITFP"] if cgitfp is None else cgitfp
    sl = x["SLT"] if slt is None else slt
    return (it + sl + x["EECSSC"] + x["ERCSSC"] - x["CTGG"]) / x["LC"]


out = {"definition": __doc__, "rows": []}
x = d["FRA"]["2025"]["M100_100"]
lean = chk[("FR", "M100_100")]["lines"]["CGITFP"]["ours"]
w0, w1 = wedge(x), wedge(x, cgitfp=lean)
out["rows"].append({"country": "FR", "type": "M100_100", "error": "quotient familial capped at one half-part",
                    "oecd_income_tax": round(x["CGITFP"], 2), "statute_income_tax": lean,
                    "oecd_wedge_pct": round(100 * w0, 3), "corrected_wedge_pct": round(100 * w1, 3),
                    "difference_points": round(100 * (w0 - w1), 3)})
x = d["USA"]["2025"]["SP67"]
w0, w1 = wedge(x), wedge(x, cgitfp=x["CGITFP"] - 25 * 0.12)
out["rows"].append({"country": "US", "type": "SP67", "error": "head-of-household standard deduction $23,600, statute $23,625",
                    "oecd_wedge_pct": round(100 * w0, 3), "corrected_wedge_pct": round(100 * w1, 3),
                    "difference_points": round(100 * (w0 - w1), 4)})
x = d["JPN"]["2025"]["SP67"]
it_stat = round(41200 * 1.021 / 100) * 100
w0, w1 = wedge(x), wedge(x, cgitfp=it_stat, slt=x["SLT"] - 30000)
out["rows"].append({"country": "JP", "type": "SP67", "error": "ひとり親控除 left out (所得税法 第81条)",
                    "oecd_income_tax_with_surtax": x["CGITFP"], "statute_income_tax_with_surtax": it_stat,
                    "oecd_local_tax": x["SLT"], "statute_local_tax_approx": x["SLT"] - 30000,
                    "oecd_wedge_pct": round(100 * w0, 3), "corrected_wedge_pct": round(100 * w1, 3),
                    "difference_points": round(100 * (w0 - w1), 3)})
rows = list(csv.DictReader(open(os.path.join(ROOT, "data/oecd/tw_cou_5.csv"), encoding="utf-8-sig")))
def k(r, n):
    for key in r:
        if key.startswith(n + ":"):
            return r[key]
for r in rows:
    if (k(r, "TIME_PERIOD") == "2025" and k(r, "MEASURE").startswith("AV_TW:") and k(r, "REF_AREA").startswith("FRA")
            and k(r, "HOUSEHOLD_TYPE").startswith("C_C2") and k(r, "INCOME_SPOUSE").startswith("AW100")):
        out["rows"][0]["oecd_published_AV_TW"] = float(k(r, "OBS_VALUE"))
json.dump(out, open(os.path.join(ROOT, "charts/oecd_error_effects.json"), "w"), indent=1, ensure_ascii=False)
for r in out["rows"]:
    print(r)
