"""Stress test: returns placed exactly on statutory thresholds and one euro either side, both years."""
import json, sys

P = {2024: dict(sal=(504, 14426), pen=(450, 4399), age=(17510, 28170), dec=(889, 1470)),
     2025: dict(sal=(509, 14555), pen=(454, 4439), age=(17670, 28430), dec=(897, 1483))}
out = []
def add(tag, year, boxes):
    out.append({"id": f"{tag}_{year}_{len(out)}", "year": year, "tag": tag, "boxes": boxes})
for y, p in P.items():
    single = {"0AC": 1, "0DA": 1980}
    old = {"0AC": 1, "0DA": 1950}
    couple = {"0AM": 1, "0DA": 1980, "0DB": 1980}
    for d in (-1, 0, 1):
        # salary allowance minimum and maximum: 10 % of salary = min or max
        add("sal_min", y, {**single, "1AJ": 10 * p["sal"][0] + d})
        add("sal_max", y, {**single, "1AJ": 10 * p["sal"][1] + d})
        add("sal_low", y, {**single, "1AJ": p["sal"][0] + d})
        # pension allowance: minimum per pensioner, maximum per household
        add("pen_min", y, {**old, "1AS": 10 * p["pen"][0] + d})
        add("pen_max", y, {**couple, "0DA": 1950, "0DB": 1950, "1AS": 5 * p["pen"][1] + d, "1BS": 5 * p["pen"][1] + d})
        # art. 157 bis bands, entered as pensions so that the revenu net global lands on the band edge
        for t in p["age"]:
            add("age_band", y, {**old, "4BA": t + d})
        # micro minimum 305 €: services 50 % -> 610; sales 71 % -> 430; BNC 34 % -> 897
        add("micro_min", y, {**single, "5KP": 610 + d})
        add("micro_min", y, {**single, "5KO": 430 + d})
        add("micro_min", y, {**single, "5HQ": 897 + d})
        # CEHR and CDHR edges (RFR from flat-taxed dividends)
        for t in (250000, 330000, 500000):
            add("high", y, {**single, "2DC": t + d})
        for t in (500000, 660000, 1000000):
            add("high", y, {**couple, "2DC": t + d})
        # home help and childcare ceilings, gifts limits
        add("7DB", y, {**single, "1AJ": 60000, "7DB": 12000 + d})
        add("7GA", y, {**single, "1AJ": 40000, "0CF": 1, "0F0": y - 2, "7GA": 3500 + d})
        add("gifts", y, {**single, "1AJ": 50000, "7UD": 1000 + d})
        add("gifts20", y, {**single, "1AJ": 50000, "7UF": 9000 + d})
        # retirement savings ceiling
        add("per", y, {**single, "1AJ": 50000, "6NS": 4000 + d, "APS": 4000, "DPS": 0, "CPS": 0, "BPS": 0})
        # décote edge: tax before décote around base / 0.4525
        add("decote", y, {**single, "4BA": int(p["dec"][0] / 0.4525 / 0.11 + 11497 + (103 if y == 2025 else 0)) + d})
open(sys.argv[1], "w").write("".join(json.dumps(c) + "\n" for c in out))
print(len(out))
