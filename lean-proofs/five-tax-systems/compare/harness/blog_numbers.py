"""Every number the blog post quotes, read back from the chart files of the last run, in one place.

    python3 blog_numbers.py   -> charts/blog_numbers.json and a printed digest

Rates are in per cent, rounded to 0.1 (Kakwani and Reynolds-Smolensky to 0.001). Rerun after harness/final_run.sh
and compare with the notes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT  # noqa: E402

CH = os.path.join(ROOT, "charts")
C = ["US", "FR", "UK", "DE", "JP"]
FAMS = ["single", "single_parent_2", "couple_1earner_2", "couple_2earner_2"]


def L(name):
    return json.load(open(os.path.join(CH, name)))


def at(xs, ys, x):
    i = min(range(len(xs)), key=lambda j: abs(xs[j] - x))
    return ys[i]


def p1(v):
    return None if v is None else round(100 * v, 1)


def main():
    out = {}
    cur = {f: L(f"curves_{f}.json") for f in FAMS}
    # A. curves
    A = {}
    for f in FAMS:
        cc = cur[f]["countries"]
        A[f] = {}
        for c in C:
            s = cc[c]
            e = {"avg_it": {x: p1(at(s["x"], s["avg_it"], x)) for x in (0.5, 0.67, 1.0, 1.67, 2.0, 3.0, 5.0)},
                 "avg_all": {x: p1(at(s["x"], s["avg_all"], x)) for x in (0.5, 0.67, 1.0, 1.67, 2.0, 3.0, 5.0)},
                 "mtr10_all": {x: p1(at(s["x_mid"] if len(s["mtr10_all"]) == len(s["x_mid"]) else s["x"], s["mtr10_all"], x))
                               for x in (0.5, 1.0, 2.0, 5.0)}}
            lo = 0.35 if c == "JP" else -1  # the JP lone-earner model boundary below 88,000 yen a month
            m1 = [(m, x) for m, x in zip(s["mtr_all"], s["x_mid"]) if m is not None and x >= lo]
            xs10 = s["x_mid"] if len(s["mtr10_all"]) == len(s["x_mid"]) else s["x"]
            m10 = [(m, x) for m, x in zip(s["mtr10_all"], xs10) if m is not None and x >= lo]
            e["max_mtr1_all"] = [p1(max(m1)[0]), round(max(m1)[1], 3)]
            e["max_mtr10_all"] = [p1(max(m10)[0]), round(max(m10)[1], 3)]
            first = next((x for x, v in zip(s["x"], s["avg_it"]) if v is not None and v > 0.0005 and x > 0), None)
            # income tax starts: the first point after which the average income tax stays positive
            xs, ys = s["x"], s["avg_it"]
            start = None
            for i in range(len(xs)):
                if all((y or 0) > 0.0005 for y in ys[i:] if y is not None) and xs[i] > 0:
                    start = xs[i]
                    break
            e["income_tax_first_positive_aw"] = first
            e["income_tax_positive_from_aw"] = start
            A[f][c] = e
    out["curves"] = A
    # B. PPP
    p = L("curves_ppp.json")["families"]
    B = {}
    for fam in p:
        B[fam] = {}
        for c in C:
            s = p[fam][c]
            B[fam][c] = {str(u): [s["net_usd_ppp"][s["x_usd_ppp"].index(u)], p1(s["avg_all"][s["x_usd_ppp"].index(u)])]
                         for u in (30000, 50000, 100000, 200000, 400000) if u in s["x_usd_ppp"]}
        # from which PPP income on is the US the lowest burden for good?
        xs = p[fam]["US"]["x_usd_ppp"]
        def ok(i):
            us = p[fam]["US"]["avg_all"][i]
            return us is not None and all(p[fam][c]["avg_all"][i] is None or us <= p[fam][c]["avg_all"][i] + 1e-9 for c in C)
        low = [ok(i) for i in range(len(xs))]
        frm = None
        for i in range(len(xs)):
            if all(low[i:]):
                frm = xs[i]
                break
        B[fam]["US_lowest_from_usd"] = frm
    out["ppp"] = B
    # E. family
    f = L("family.json")
    xs = f["x_values"]
    E = {}
    for c in C:
        F = f["countries"][c]
        cv = F["child_value_per_child"]
        mar = F["marriage"]
        sp = F["earner_split"]
        E[c] = {"child_couple1": {x: round(100 * at(xs, cv["couple_one_earner"]["total"], x), 2) for x in (0.5, 1, 2, 3, 5)},
                "child_single_parent": {x: round(100 * at(xs, cv["single_parent_vs_single"]["total"], x), 2) for x in (0.5, 1, 2, 5)},
                "marriage_1earner_nokids": {x: round(100 * at(xs, mar["one_earner_100_0_no_children"]["total"], x), 2) for x in (1, 2, 3, 5)},
                "marriage_1earner_nokids_max": round(100 * max(mar["one_earner_100_0_no_children"]["total"]), 2),
                "marriage_50_50_kids": {x: round(100 * at(xs, mar["split_50_50_two_children"]["total"], x), 2) for x in (0.5, 1, 2, 5)},
                "marriage_50_50_nokids_range": [round(100 * min(mar["split_50_50_no_children"]["total"]), 2),
                                                round(100 * max(mar["split_50_50_no_children"]["total"]), 2)],
                "marriage_min_any": min((round(100 * min(v["total"]), 2), k) for k, v in mar.items()),
                "split_married_nokids": {x: round(100 * at(xs, sp["married_no_children"]["total"], x), 2) for x in (1, 2, 5)}}
    out["family"] = E
    cr = L("child_rank.json")["countries"]
    out["child_rank"] = {c: {lv: [p1(cr[c][lv][k]) for k in ("child1", "child2", "child3")] for lv in cr[c]} for c in C}
    w = L("walls_second_earner.json")["countries"]
    out["walls"] = {c: {k: {x: p1(at(v["spouse_aw"], v["participation_tax_rate"], x)) for x in (0.1, 0.25, 0.5, 0.67, 1.0)}
                        for k, v in w[c].items()} for c in C}
    out["walls_range_married_kids_025_1"] = {c: [p1(min(r for x, r in zip(w[c]["2children/married"]["spouse_aw"], w[c]["2children/married"]["participation_tax_rate"]) if 0.25 <= x <= 1.0 and r is not None)),
                                                 p1(max(r for x, r in zip(w[c]["2children/married"]["spouse_aw"], w[c]["2children/married"]["participation_tax_rate"]) if 0.25 <= x <= 1.0 and r is not None))] for c in C}
    b = L("base.json")["countries"]
    out["base"] = {c: {"marginal_1AW": {k: p1(v["all"]) for k, v in b[c]["marginal"]["1.0"].items()},
                       "marginal_5AW": {k: p1(v["all"]) for k, v in b[c]["marginal"]["5.0"].items()},
                       "marginal_1AW_default": {k: p1(v["all_default"]) for k, v in b[c]["marginal"]["1.0"].items() if "all_default" in v},
                       "only": {k: p1(v["avg_all"]) for k, v in b[c]["only"].items()},
                       "only_default": {k: p1(v["avg_all_default"]) for k, v in b[c]["only"].items() if "avg_all_default" in v},
                       "elections": {k: v.get("election") for k, v in b[c]["only"].items() if v.get("election")}} for c in C}
    t = L("top_rates.json")["countries"]
    out["top50"] = {c: {k: round(100 * t[c][f"{k}@50"]["all"], 2) for k in ("wages", "interest", "dividends", "capitalGains", "rentalIncome")} for c in C}
    g = L("progressivity.json")["countries"]
    out["progressivity"] = {c: {fam: {"kakwani_it": None if v["kakwani_it"] is None else round(v["kakwani_it"], 3),
                                      "kakwani_all": None if v["kakwani_all"] is None else round(v["kakwani_all"], 3),
                                      "rs": round(v["reynolds_smolensky"], 4), "no_income_tax": v["share_no_income_tax"],
                                      "avg_it": p1(v["avg_rate_it"]), "avg_all": p1(v["avg_rate_all"]),
                                      "decile_it": [p1(x) for x in v["decile_rates_it"]]}
                                for fam, v in g[c].items()} for c in C}
    cs = L("cliffs_summary.json")
    out["notches"] = {k: {"country": v["country"], "n": v["notches"], "worst": v["worst"]["net_change"],
                          "at": v["worst"]["gross"], "family": v["worst"]["family"], "families": v["families"]}
                      for k, v in cs["causes"].items()}
    out["notch_causes_per_country"] = {c: sorted(k for k, v in cs["causes"].items() if v["country"] == c and v["notches"] > 0) for c in C}
    out["unexplained"] = cs["unexplained"] if not isinstance(cs["unexplained"], list) else len(cs["unexplained"])
    bands = {}
    for bd in cs["bands_mtr_above_100"]:
        bands.setdefault(bd["country"], []).append((bd["family"], bd["g0"], bd["g1"]))
    out["bands_above_100"] = {c: len(v) for c, v in bands.items()}
    # OECD check: largest absolute difference per country and line, by family
    o = L("oecd_check.json")
    OC = {}
    for r in o["rows"]:
        for ln, v in r["lines"].items():
            if v.get("diff") is None:
                continue
            OC.setdefault(r["country"], {}).setdefault(ln, {})[r["type"]] = round(v["diff"], 2)
    out["oecd_diffs"] = OC
    j = L("oecd_check_jp_age39.json")
    out["oecd_diffs_jp39"] = {}
    for r in j["rows"]:
        for ln, v in r["lines"].items():
            if v.get("diff") is not None:
                out["oecd_diffs_jp39"].setdefault(ln, {})[r["type"]] = round(v["diff"], 2)
    cx = L("complexity.json")["models"]
    out["complexity"] = {c: {"computation": {k: v for k, v in cx[c]["computation"].items() if k in ("lines", "defs", "distinct_literals", "distinct_literals_outside_tables", "files")},
                             "whole": {k: v for k, v in cx[c]["whole_model"].items() if k in ("lines", "defs", "theorems", "checks", "distinct_provisions_cited", "files")},
                             "adapter": {k: v for k, v in (cx[c].get("comparison_adapter") or {}).items() if k in ("lines", "theorems", "distinct_literals", "distinct_provisions_cited")}}
                         for c in C if c in cx}
    json.dump(out, open(os.path.join(CH, "blog_numbers.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps(out, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
