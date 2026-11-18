"""Head-to-head analyses on the five Lean models. Each writes a chart data file in charts/ and a summary in
runs/<analysis>/latest/summary.json; the blog post reads the numbers from these files.

    python3 analyses.py curves|cliffs|walls|family|base|progressivity|all [--countries US,FR,...]

Definitions used throughout (all per household, per year, local currency):
  gross      = earnings + pensions + investment and rental income (the contract's inputs)
  taxes_it   = incomeTax (central government, after credits; refundable credits make it negative)
  taxes_tax  = incomeTax + surtaxes + localIncomeTax
  taxes_all  = incomeTax + surtaxes + localIncomeTax + employeeSocial - benefits = gross - net
  average rate = taxes / gross; marginal rate = change in taxes / change in gross between neighbouring points.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import AW, COUNTRIES, CUR, PPP, ROOT, adult, available, household  # noqa: E402
import run as runner  # noqa: E402
from scenarios import CHILD_AGES, FAMILIES, fam_household  # noqa: E402

CHARTS = os.path.join(ROOT, "charts")
os.makedirs(CHARTS, exist_ok=True)


def avail(countries):
    return [c for c in countries if available(c)]


def dump(name, obj):
    obj.setdefault("generated", time.strftime("%Y-%m-%dT%H:%M:%S"))
    p = os.path.join(CHARTS, name)
    json.dump(obj, open(p, "w"), indent=1, ensure_ascii=False)
    return p


def tx(r, kind):
    if kind == "it":
        return r["incomeTax"]
    if kind == "tax":
        return r["incomeTax"] + r["surtaxes"] + r["localIncomeTax"]
    if kind == "social":
        return r["employeeSocial"]
    if kind == "benefits":
        return r["benefits"]
    return r["gross"] - r["net"]


def rate(a, b):
    return None if b == 0 else a / b


def r4(x):
    return None if x is None else round(x, 4)


# ---------------------------------------------------------------------------------------------------------------
# A. Average and marginal rate curves
# ---------------------------------------------------------------------------------------------------------------

def curves(countries):
    run_dir, rows, info = runner.run("curves", avail(countries), slim=True)
    by = {}
    for r in rows:
        by.setdefault((r["country"], r["family"]), []).append(r)
    summary = {"run": run_dir, "exes": info["countries"], "points": {}}
    for fam in FAMILIES:
        out = {"title": f"Average and marginal rates, {fam.replace('_', ' ')}, 0 to 5 x average wage",
               "x": "household gross earnings, multiples of the country's 2025 average wage (OECD Taxing Wages 2026)",
               "family": fam, "households": FAMILY_TEXT[fam],
               "series_definition": {"avg_it": "central income tax / gross",
                                     "avg_tax": "(income tax + surtaxes + local income tax) / gross",
                                     "avg_all": "(income tax + surtaxes + local + employee social - benefits) / gross",
                                     "mtr_*": "change in the same taxes / change in gross between neighbouring points "
                                              "(1 % of the average wage apart), at the midpoint x_mid",
                                     "mtr10_*": "the same over 10 % of the average wage (x - 5 % to x + 5 %), at x; it "
                                                "averages over the steps of grade and band tables (Japan's premium "
                                                "grades, the US Tax Table), so it shows the rate a person faces over a "
                                                "raise rather than at one unit"},
               "model_boundaries": {"JP": "Below 1,056,000 yen of pay (0.185 x AW) a worker who is nobody's dependent "
                                          "would pay national pension and national health insurance premiums, which "
                                          "the JP model leaves out: rates there are too low, and the jump at 0.185 x "
                                          "AW for a lone earner is the model's, not the law's (for a dependent spouse "
                                          "it is the law's '1.06 million yen wall')"},
               "source": os.path.join(run_dir, "results.jsonl"), "countries": {}}
        for c in countries:
            rs = sorted(by.get((c, fam), []), key=lambda r: r["h_aw"])
            if not rs:
                continue
            s = {"x": [], "avg_it": [], "avg_tax": [], "avg_all": [], "x_mid": [], "mtr_it": [], "mtr_tax": [],
                 "mtr_all": [], "gross": [], "net": [], "mtr10_it": [], "mtr10_tax": [], "mtr10_all": []}
            for r in rs:
                s["x"].append(r["h_aw"])
                s["gross"].append(r["gross"])
                s["net"].append(r["net"])
                for k in ("it", "tax", "all"):
                    s["avg_" + k].append(r4(rate(tx(r, k), r["gross"])))
            for a, b in zip(rs, rs[1:]):
                dg = b["gross"] - a["gross"]
                s["x_mid"].append(round((a["h_aw"] + b["h_aw"]) / 2, 4))
                for k in ("it", "tax", "all"):
                    s["mtr_" + k].append(r4(rate(tx(b, k) - tx(a, k), dg)))
            for i in range(len(rs)):
                a, b = rs[max(0, i - 5)], rs[min(len(rs) - 1, i + 5)]
                dg = b["gross"] - a["gross"]
                for k in ("it", "tax", "all"):
                    s["mtr10_" + k].append(r4(rate(tx(b, k) - tx(a, k), dg)))
            out["countries"][c] = s
            pts = {}
            for xq in (0.5, 0.67, 1.0, 1.67, 2.0, 3.0, 5.0):
                i = min(range(len(s["x"])), key=lambda j: abs(s["x"][j] - xq))
                pts[str(xq)] = {"avg_it": s["avg_it"][i], "avg_all": s["avg_all"][i], "gross": s["gross"][i],
                                "net": s["net"][i]}
            # first point where central income tax is positive; where the household becomes a net payer
            first_it = next((s["x"][i] for i in range(len(s["x"])) if rs[i]["incomeTax"] > 0), None)
            first_payer = next((s["x"][i] for i in range(len(s["x"])) if rs[i]["gross"] - rs[i]["net"] > 0), None)
            mt = [m for m in s["mtr_all"] if m is not None]
            pts["first_income_tax_at_aw"] = first_it
            pts["first_net_payer_at_aw"] = first_payer
            pts["max_mtr_all"] = max(mt) if mt else None
            pts["mtr_all_at_5aw"] = s["mtr_all"][-1]
            pts["mtr_it_at_5aw"] = s["mtr_it"][-1]
            summary["points"][f"{c}/{fam}"] = pts
        dump(f"curves_{fam}.json", out)
    json.dump(summary, open(os.path.join(run_dir, "summary.json"), "w"), indent=1)
    return summary


FAMILY_TEXT = {
    "single": "one adult aged 40, no children, all income from wages",
    "single_parent_2": "one adult aged 40 with two children aged 6 and 11, all income from wages",
    "couple_1earner_2": "married couple aged 40, two children aged 6 and 11, one earner",
    "couple_2earner_2": "married couple aged 40, two children aged 6 and 11, earnings split 60:40",
}


# ---------------------------------------------------------------------------------------------------------------
# B. Cliffs and notches: a fine scan of gross earnings, then a one-unit refinement around every event
# ---------------------------------------------------------------------------------------------------------------

STEP = {"US": 10, "FR": 10, "UK": 10, "DE": 10, "JP": 1000}
FIELDS = ["incomeTax", "surtaxes", "localIncomeTax", "employeeSocial", "benefits"]


def events_in(rs, step, window):
    """Points where net income falls as gross rises (between neighbours), and runs of the window marginal rate above
    100 %. `rs` sorted by gross."""
    ev = []
    for a, b in zip(rs, rs[1:]):
        if b["net"] < a["net"]:
            ev.append({"kind": "net_falls", "g0": a["gross"], "g1": b["gross"], "net_change": b["net"] - a["net"],
                       "changes": {k: (b[k] - a[k]) for k in FIELDS if b[k] != a[k]}})
    # runs where the marginal rate over `window` neighbours exceeds 100 %
    run_start = None
    for i in range(len(rs) - window):
        a, b = rs[i], rs[i + window]
        m = (b["gross"] - b["net"] - (a["gross"] - a["net"])) / (b["gross"] - a["gross"])
        if m > 1.0:
            if run_start is None:
                run_start = i
        elif run_start is not None:
            ev.append({"kind": "mtr_above_100", "g0": rs[run_start]["gross"], "g1": rs[i - 1 + window]["gross"]})
            run_start = None
    if run_start is not None:
        ev.append({"kind": "mtr_above_100", "g0": rs[run_start]["gross"], "g1": rs[-1]["gross"]})
    return ev


def cliffs(countries):
    cs = avail(countries)
    run_dir, rows, info = runner.run("scan", cs, slim=True)
    by = {}
    for r in rows:
        by.setdefault((r["country"], r["family"]), []).append(r)
    found = []
    for (c, fam), rs in sorted(by.items()):
        rs.sort(key=lambda r: r["gross"])
        window = max(1, int(round(0.01 * AW[c] / STEP[c])))
        for e in events_in(rs, STEP[c], window):
            e.update({"country": c, "family": fam, "g0_aw": round(e["g0"] / AW[c], 4),
                      "g1_aw": round(e["g1"] / AW[c], 4)})
            found.append(e)
    # refine each net_falls event to one currency unit (JPY: 1 yen) by scanning [g0, g1]
    refine = {}
    for e in found:
        if e["kind"] != "net_falls":
            continue
        c = e["country"]
        refine.setdefault(c, [])
        for g in range(e["g0"], e["g1"] + 1, 1 if c != "JP" else 1):
            hid = f"ref-{c}-{e['family']}-{g}"
            na, married, kids, share = FAMILIES[e["family"]]
            if na == 1:
                ads = [adult(wages=g)]
            else:
                w1 = round(g * share)
                ads = [adult(wages=w1), adult(wages=g - w1)]
            refine[c].append((hid, e, household(hid, ads, married=married, children=kids)))
    exact = []
    if refine:
        def gen(cs2):
            out, meta = {}, {}
            for c in cs2:
                out[c] = [h for (_, _, h) in refine.get(c, [])]
                for hid, e, h in refine.get(c, []):
                    meta[hid] = {"family": e["family"], "event_g0": e["g0"]}
            return out, meta
        rdir, rrows, _ = runner.run("scan_refine", list(refine), slim=True, gen=gen)
        byev = {}
        for r in rrows:
            byev.setdefault((r["country"], r["family"], r["event_g0"]), []).append(r)
        for (c, fam, g0), rs in byev.items():
            rs.sort(key=lambda r: r["gross"])
            for a, b in zip(rs, rs[1:]):
                if b["net"] < a["net"]:
                    exact.append({"country": c, "family": fam, "gross_before": a["gross"], "gross_after": b["gross"],
                                  "gross_aw": round(b["gross"] / AW[c], 4), "net_change": b["net"] - a["net"],
                                  "changes": {k: (b[k] - a[k]) for k in FIELDS if b[k] != a[k]},
                                  "detail_hint": None})
    res = {"title": "Cliffs and notches: where one more unit of gross earnings lowers net income, and bands where "
                    "the marginal rate (over 1 % of the average wage) exceeds 100 %",
           "scan": {c: f"0 to 5 x AW in steps of {STEP[c]} {CUR[c]}" for c in cs},
           "families": FAMILY_TEXT, "source": os.path.join(run_dir, "results.jsonl"),
           "coarse_events": found, "exact_notches": exact}
    dump("cliffs.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# B2. Second-earner walls: the spouse's earnings from 0 to 1 x AW with the principal at 1 x AW (married, 2 children)
# ---------------------------------------------------------------------------------------------------------------

def walls(countries, principal=1.0, top=1.0):
    cs = avail(countries)
    units = {"US": 10, "FR": 10, "UK": 10, "DE": 10, "JP": 1000}

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            w1 = round(principal * AW[c])
            n = int(top * AW[c] // units[c])
            for kids_name, kids in (("2children", CHILD_AGES), ("nochildren", ())):
                for married in (True, False):
                    for i in range(n + 1):
                        g2 = i * units[c]
                        hid = f"wall-{c}-{kids_name}-{'m' if married else 'u'}-{i}"
                        hs.append(household(hid, [adult(wages=w1), adult(wages=g2)], married=married, children=kids))
                        meta[hid] = {"kids": kids_name, "married": married, "spouse_wages": g2}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("walls", cs, slim=True, gen=gen)
    by = {}
    for r in rows:
        by.setdefault((r["country"], r["kids"], r["married"]), []).append(r)
    out = {"title": "Second earner: household net income as the spouse's earnings rise from 0 to 1 x AW, principal "
                    "earner at 1 x AW", "source": os.path.join(run_dir, "results.jsonl"), "countries": {}}
    events = []
    for (c, kids, married), rs in sorted(by.items()):
        rs.sort(key=lambda r: r["spouse_wages"])
        key = f"{kids}/{'married' if married else 'unmarried'}"
        step_n = max(1, int(round(0.01 * AW[c] / units[c])))
        pts = rs[::step_n]
        out["countries"].setdefault(c, {})[key] = {
            "spouse_aw": [round(r["spouse_wages"] / AW[c], 4) for r in pts],
            "net": [r["net"] for r in pts],
            "taxes_all": [r["gross"] - r["net"] for r in pts],
            "participation_tax_rate": [r4(rate((r["gross"] - r["net"]) - (rs[0]["gross"] - rs[0]["net"]),
                                                r["spouse_wages"])) for r in pts]}
        for a, b in zip(rs, rs[1:]):
            if b["net"] < a["net"]:
                events.append({"country": c, "kids": kids, "married": married, "spouse_before": a["spouse_wages"],
                               "spouse_after": b["spouse_wages"], "spouse_aw": round(b["spouse_wages"] / AW[c], 4),
                               "net_change": b["net"] - a["net"],
                               "changes": {k: (b[k] - a[k]) for k in FIELDS if b[k] != a[k]}})
    out["net_falls"] = events
    dump("walls_second_earner.json", out)
    return out


# ---------------------------------------------------------------------------------------------------------------
# C. The family: what a child is worth, marriage, one earner or two
# ---------------------------------------------------------------------------------------------------------------

def family(countries, step=0.05, top=5.0):
    cs = avail(countries)
    n = int(round(top / step))
    variants = {
        # name: (adults, married, children, share)
        "single_0": (1, False, (), 1.0), "single_2": (1, False, CHILD_AGES, 1.0),
        "m1_0": (2, True, (), 1.0), "m1_2": (2, True, CHILD_AGES, 1.0),
        "m2_0": (2, True, (), 0.6), "m2_2": (2, True, CHILD_AGES, 0.6),
        "m5_0": (2, True, (), 0.5), "m5_2": (2, True, CHILD_AGES, 0.5),
        "u1_0": (2, False, (), 1.0), "u1_2": (2, False, CHILD_AGES, 1.0),
        "u2_0": (2, False, (), 0.6), "u2_2": (2, False, CHILD_AGES, 0.6),
        "u5_0": (2, False, (), 0.5), "u5_2": (2, False, CHILD_AGES, 0.5),
        "m7_0": (2, True, (), 0.7), "u7_0": (2, False, (), 0.7),
    }

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            for v, (na, married, kids, share) in variants.items():
                for i in range(n + 1):
                    x = round(i * step, 6)
                    g = x * AW[c]
                    hid = f"fam-{c}-{v}-{i}"
                    if na == 1:
                        ads = [adult(wages=g)]
                    else:
                        w1 = round(g * share)
                        ads = [adult(wages=w1), adult(wages=round(g) - w1)]
                    hs.append(household(hid, ads, married=married, children=kids))
                    meta[hid] = {"variant": v, "h_aw": x}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("family", cs, slim=True, gen=gen)
    T = {}
    for r in rows:
        T[(r["country"], r["variant"], r["h_aw"])] = r
    xs = [round(i * step, 6) for i in range(n + 1)]
    res = {"title": "The family: child value, marriage, one or two earners", "source": os.path.join(run_dir, "results.jsonl"),
           "x": "household gross earnings, multiples of AW", "definitions": {
               "child_value": "net(with two children) - net(same adults and earnings, no children), per child, as a "
                              "share of the average wage; split into the tax part (income tax + surtaxes + local), "
                              "the social-contribution part and the benefit part",
               "marriage": "net(married) - net(the same two people unmarried, cohabiting), as a share of AW; positive "
                           "= marriage bonus",
               "earner_split": "net(two earners, 50:50) - net(one earner), married, same household earnings, as a "
                               "share of AW"}, "countries": {}}
    for c in cs:
        aw = AW[c]
        out = {}

        def diff(v1, v0, parts=True):
            vals, taxp, socp, benp, dflt = [], [], [], [], []
            for x in xs:
                a, b = T.get((c, v1, x)), T.get((c, v0, x))
                if a is None or b is None:
                    vals.append(None); taxp.append(None); socp.append(None); benp.append(None); dflt.append(None)
                    continue
                vals.append(round((a["net"] - b["net"]) / aw, 5))
                taxp.append(round(-(tx(a, "tax") - tx(b, "tax")) / aw, 5))
                socp.append(round(-(a["employeeSocial"] - b["employeeSocial"]) / aw, 5))
                benp.append(round((a["benefits"] - b["benefits"]) / aw, 5))
                dflt.append(round((a.get("net_default", a["net"]) - b.get("net_default", b["net"])) / aw, 5))
            d = {"total": vals, "via_tax": taxp, "via_social": socp, "via_benefits": benp}
            if dflt != vals:  # an election changed something: keep the result under the model's defaults as well
                d["total_default"] = dflt
            return d
        per_child = {}
        for name, (v1, v0) in {"single_parent_vs_single": ("single_2", "single_0"),
                               "couple_one_earner": ("m1_2", "m1_0"),
                               "couple_two_earner_60_40": ("m2_2", "m2_0")}.items():
            d2 = diff(v1, v0)
            per_child[name] = {k: [None if v is None else round(v / 2, 5) for v in vs] for k, vs in d2.items()}
        out["child_value_per_child"] = per_child
        out["marriage"] = {name: diff(v1, v0) for name, (v1, v0) in {
            "one_earner_100_0_no_children": ("m1_0", "u1_0"), "one_earner_100_0_two_children": ("m1_2", "u1_2"),
            "split_70_30_no_children": ("m7_0", "u7_0"),
            "split_60_40_no_children": ("m2_0", "u2_0"), "split_60_40_two_children": ("m2_2", "u2_2"),
            "split_50_50_no_children": ("m5_0", "u5_0"), "split_50_50_two_children": ("m5_2", "u5_2")}.items()}
        out["earner_split"] = {"married_no_children": diff("m5_0", "m1_0"), "married_two_children": diff("m5_2", "m1_2"),
                               "unmarried_no_children": diff("u5_0", "u1_0")}
        res["countries"][c] = out
    res["x_values"] = xs
    dump("family.json", res)
    return res


def child_rank(countries, levels=(0.5, 1.0, 2.0, 3.0, 5.0)):
    """What the first, second and third child are each worth: a married one-earner couple, children aged 11, 6, 3
    added one at a time (the third is under 6 nowhere relevant: ages 11, 6 and 3 all count as children everywhere)."""
    cs = avail(countries)
    ages = [11, 6, 3]

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            for lv in levels:
                for k in range(4):
                    hid = f"rank-{c}-{lv}-{k}"
                    hs.append(household(hid, [adult(wages=lv * AW[c]), adult(wages=0)], married=True,
                                        children=ages[:k]))
                    meta[hid] = {"level": lv, "kids": k}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("child_rank", cs, slim=True, gen=gen)
    T = {(r["country"], r["level"], r["kids"]): r for r in rows}
    res = {"title": "What each additional child is worth (net income gained, % of AW): married one-earner couple, "
                    "children aged 11, 6 and 3 added in that order", "source": os.path.join(run_dir, "results.jsonl"),
           "levels": list(levels), "countries": {}}
    for c in cs:
        o = {}
        for lv in levels:
            o[str(lv)] = {f"child{k}": r4((T[(c, lv, k)]["net"] - T[(c, lv, k - 1)]["net"]) / AW[c])
                          for k in (1, 2, 3) if (c, lv, k) in T and (c, lv, k - 1) in T}
        res["countries"][c] = o
    dump("child_rank.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# D. The base: the marginal rate on one more unit of each kind of income, at several wage levels
# ---------------------------------------------------------------------------------------------------------------

def base(countries):
    cs = avail(countries)
    levels = [0.5, 1.0, 2.0, 5.0]
    kinds = ["wages", "interest", "dividends", "capitalGains", "rentalIncome"]

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            d = 0.10 * AW[c]  # the extra income: 10 % of the average wage
            for lv in levels:
                w = lv * AW[c]
                hid = f"base-{c}-{lv}-none"
                hs.append(household(hid, [adult(wages=w)]))
                meta[hid] = {"level": lv, "kind": "none", "extra": 0}
                for k in kinds:
                    hid = f"base-{c}-{lv}-{k}"
                    if k == "wages":
                        h = household(hid, [adult(wages=w + d)])
                    else:
                        h = household(hid, [adult(wages=w)], **{k: d})
                    hs.append(h)
                    meta[hid] = {"level": lv, "kind": k, "extra": round(d)}
            # living on capital: 1 x AW of each kind and nothing else
            for k in kinds:
                hid = f"base-{c}-only-{k}"
                if k == "wages":
                    h = household(hid, [adult(wages=AW[c])])
                else:
                    h = household(hid, [adult(wages=0)], **{k: AW[c]})
                hs.append(h)
                meta[hid] = {"level": "only", "kind": k, "extra": round(AW[c])}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("base", cs, slim=False, gen=gen)
    T = {(r["country"], r["level"], r["kind"]): r for r in rows}
    res = {"title": "What counts as income and how it is taxed: the marginal rate on an extra 10 % of the average wage "
                    "of each kind of income, for a single person earning 0.5, 1, 2 and 5 x AW; and the average rate "
                    "of someone living on 1 x AW of one kind of income only",
           "source": os.path.join(run_dir, "results.jsonl"), "kinds": kinds, "levels": levels, "countries": {}}
    for c in cs:
        o = {"marginal": {}, "only": {}}
        for lv in levels:
            b = T.get((c, lv, "none"))
            if not b:
                continue
            row = {}
            for k in kinds:
                r = T.get((c, lv, k))
                if not r:
                    continue
                dg = r["gross"] - b["gross"]
                row[k] = {"all": r4(rate(tx(r, "all") - tx(b, "all"), dg)), "tax": r4(rate(tx(r, "tax") - tx(b, "tax"), dg)),
                          "it": r4(rate(tx(r, "it") - tx(b, "it"), dg)),
                          "surtaxes": r4(rate(r["surtaxes"] - b["surtaxes"], dg)),
                          "social": r4(rate(r["employeeSocial"] - b["employeeSocial"], dg))}
                if "election" in r:  # the cheapest election (common.ELECTIONS) and the rate under the model's default
                    row[k]["election"] = r["election"]
                    row[k]["all_default"] = r4(rate((r["gross"] - r["net_default"]) - tx(b, "all"), dg))
            o["marginal"][str(lv)] = row
        for k in kinds:
            r = T.get((c, "only", k))
            if r:
                o["only"][k] = {"avg_all": r4(rate(tx(r, "all"), r["gross"])), "avg_tax": r4(rate(tx(r, "tax"), r["gross"])),
                                "surtaxes": r["surtaxes"], "incomeTax": r["incomeTax"], "gross": r["gross"]}
                if "election" in r:
                    o["only"][k]["election"] = r["election"]
                    o["only"][k]["avg_all_default"] = r4(rate(r["gross"] - r["net_default"], r["gross"]))
        res["countries"][c] = o
    dump("base.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# E. Progressivity on one synthetic population expressed in multiples of the average wage
# ---------------------------------------------------------------------------------------------------------------

def lognormal_quantiles(n, sigma, mean=1.0):
    """n equally weighted points: the mid-quantiles of a lognormal with the given mean and log-sd."""
    mu = math.log(mean) - sigma * sigma / 2
    from statistics import NormalDist
    nd = NormalDist()
    return [math.exp(mu + sigma * nd.inv_cdf((i + 0.5) / n)) for i in range(n)]


def gini(values, weights=None):
    xs = sorted(values)
    n = len(xs)
    s = sum(xs)
    if s == 0:
        return 0.0
    cum = 0.0
    for i, x in enumerate(xs, 1):
        cum += i * x
    return (2 * cum) / (n * s) - (n + 1) / n


def concentration(values, order):
    """Concentration index of `values` with units ranked by `order` (ascending)."""
    idx = sorted(range(len(values)), key=lambda i: order[i])
    n = len(values)
    s = sum(values)
    if s == 0:
        return 0.0
    cum = sum((k + 1) * values[i] for k, i in enumerate(idx))
    return (2 * cum) / (n * s) - (n + 1) / n


def progressivity(countries, n=1000, sigma=0.6):
    cs = avail(countries)
    q = lognormal_quantiles(n, sigma)
    fams = ["single", "couple_1earner_2"]

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            for fam in fams:
                for i, x in enumerate(q):
                    hid = f"prog-{c}-{fam}-{i}"
                    hs.append(fam_household(c, hid, fam, x))
                    meta[hid] = {"family": fam, "h_aw": x, "rank": i}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("progressivity", cs, slim=True, gen=gen)
    res = {"title": "Progressivity on one synthetic population of earnings in multiples of the average wage",
           "population": f"{n} equally weighted earners at the mid-quantiles of a lognormal with mean 1 x AW and "
                         f"log standard deviation {sigma} (median {round(q[n // 2], 3)} x AW); the same population in "
                         "every country, so differences come from the tax schedules alone, not from each country's "
                         "real earnings distribution",
           "measures": {"kakwani": "concentration index of taxes minus Gini of gross",
                        "reynolds_smolensky": "Gini of gross minus Gini of net (after taxes, contributions and benefits)",
                        "deciles": "taxes / gross within each tenth of the population (by gross)"},
           "source": os.path.join(run_dir, "results.jsonl"), "countries": {}}
    by = {}
    for r in rows:
        by.setdefault((r["country"], r["family"]), []).append(r)
    for (c, fam), rs in by.items():
        rs.sort(key=lambda r: r["rank"])
        g = [r["gross"] for r in rs]
        netv = [r["net"] for r in rs]
        o = {"gini_gross": round(gini(g), 4), "gini_net": round(gini(netv), 4),
             "share_no_income_tax": round(sum(1 for r in rs if r["incomeTax"] <= 0) / n, 4)}
        o["reynolds_smolensky"] = round(gini(g) - gini(netv), 5)  # from the unrounded Ginis
        for k in ("it", "tax", "all"):
            t = [tx(r, k) for r in rs]
            avg = sum(t) / sum(g)
            # the Kakwani index needs a positive total: with refundable credits a family's total income tax can be
            # near zero or negative, and the concentration index then explodes; left out below a 2 % average rate
            o[f"kakwani_{k}"] = round(concentration(t, g) - o["gini_gross"], 4) if avg >= 0.02 else None
            o[f"avg_rate_{k}"] = round(avg, 4)
            dec = []
            for d in range(10):
                part = rs[d * n // 10:(d + 1) * n // 10]
                dec.append(round(sum(tx(r, k) for r in part) / sum(r["gross"] for r in part), 4))
            o[f"decile_rates_{k}"] = dec
        res["countries"].setdefault(c, {})[fam] = o
    dump("progressivity.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# A2. The same curves on a purchasing-power axis: household earnings 0 to 400,000 US dollars at PPP
# ---------------------------------------------------------------------------------------------------------------

def curves_ppp(countries, step=2000, top_usd=400000):
    cs = avail(countries)
    n = int(top_usd // step)

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            for fam in FAMILIES:
                for i in range(n + 1):
                    usd = i * step
                    hid = f"ppp-{c}-{fam}-{i}"
                    hs.append(fam_household(c, hid, fam, usd * PPP[c] / AW[c]))
                    meta[hid] = {"family": fam, "usd_ppp": usd}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("curves_ppp", cs, slim=True, gen=gen)
    by = {}
    for r in rows:
        by.setdefault((r["country"], r["family"]), []).append(r)
    res = {"title": "Average and marginal rates against household earnings in US dollars at purchasing power parity",
           "x": "household gross earnings, 2025 US dollars at PPP (OECD's PPP implied by Taxing Wages 2026: national-"
                "currency AW / AW in USD PPP)", "ppp_used": {c: PPP[c] for c in cs},
           "series_definition": "as curves_<family>.json; net_usd_ppp = net income converted at the same PPP",
           "source": os.path.join(run_dir, "results.jsonl"), "families": {}}
    for fam in FAMILIES:
        fo = {}
        for c in cs:
            rs = sorted(by.get((c, fam), []), key=lambda r: r["usd_ppp"])
            if not rs:
                continue
            s = {"x_usd_ppp": [r["usd_ppp"] for r in rs], "x_aw": [round(r["gross"] / AW[c], 4) for r in rs],
                 "avg_it": [r4(rate(tx(r, "it"), r["gross"])) for r in rs],
                 "avg_all": [r4(rate(tx(r, "all"), r["gross"])) for r in rs],
                 "net_usd_ppp": [round(r["net"] / PPP[c]) for r in rs], "mtr_all": [], "x_mid": []}
            for a, b in zip(rs, rs[1:]):
                s["x_mid"].append((a["usd_ppp"] + b["usd_ppp"]) / 2)
                s["mtr_all"].append(r4(rate(tx(b, "all") - tx(a, "all"), b["gross"] - a["gross"])))
            fo[c] = s
        res["families"][fam] = fo
    dump("curves_ppp.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# B3. One-unit resolution: how far net income can dip for one more unit of pay from rounding alone
# ---------------------------------------------------------------------------------------------------------------

def unit_scan(countries, lo=0.9, hi=1.1):
    """A single person's pay from `lo` to `hi` x AW in steps of one currency unit (JPY: 1 yen over a 1/20 window):
    every fall of net income, its size, and what moved. Rounding to the unit makes small dips everywhere; the file
    shows how large they get in each system."""
    cs = avail(countries)

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            a, b = int(lo * AW[c]), int(hi * AW[c])
            if c == "JP":  # 1-yen steps over 2 % of AW (about 114,000 households)
                a, b = int(0.99 * AW[c]), int(1.01 * AW[c])
            hs = [household(f"u-{c}-{g}", [adult(wages=g)]) for g in range(a, b + 1)]
            for h in hs:
                meta[h["id"]] = {"wages": h["adults"][0]["wages"]}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("unit_scan", cs, slim=True, gen=gen)
    by = {}
    for r in rows:
        by.setdefault(r["country"], []).append(r)
    res = {"title": "One more unit of pay, a single person near the average wage: how often and how much net income "
                    "falls (rounding and table steps)", "source": os.path.join(run_dir, "results.jsonl"),
           "window": {"default": [lo, hi], "JP": [0.99, 1.01]}, "countries": {}}
    for c, rs in by.items():
        rs.sort(key=lambda r: r["wages"])
        falls = []
        for a, b in zip(rs, rs[1:]):
            if b["net"] < a["net"] - 1e-9:
                falls.append({"wages": b["wages"], "net_change": round(b["net"] - a["net"], 2),
                              "changes": {k: round(b[k] - a[k], 2) for k in FIELDS if b[k] != a[k]}})
        worst = min(falls, key=lambda f: f["net_change"]) if falls else None
        res["countries"][c] = {"points": len(rs), "falls": len(falls), "worst": worst,
                               "falls_over_one_unit": sum(1 for f in falls if f["net_change"] < -1)}
    dump("unit_scan.json", res)
    return res


# ---------------------------------------------------------------------------------------------------------------
# F. Top rates: the marginal rate far up the scale, on wages and on each kind of investment income
# ---------------------------------------------------------------------------------------------------------------

def top(countries):
    cs = avail(countries)
    levels = [10, 20, 50]
    kinds = ["wages", "interest", "dividends", "capitalGains", "rentalIncome"]

    def gen(cs2):
        out, meta = {}, {}
        for c in cs2:
            hs = []
            for lv in levels:
                for k in kinds:
                    for step in (0, 1):
                        amt = lv * AW[c] + step * 0.01 * AW[c]
                        hid = f"top-{c}-{lv}-{k}-{step}"
                        if k == "wages":
                            h = household(hid, [adult(wages=amt)])
                        else:
                            # the income in question on top of 1 x AW of wages
                            h = household(hid, [adult(wages=AW[c])], **{k: amt})
                        hs.append(h)
                        meta[hid] = {"level": lv, "kind": k, "step": step}
            out[c] = hs
        return out, meta
    run_dir, rows, info = runner.run("top", cs, slim=False, gen=gen)
    T = {(r["country"], r["level"], r["kind"], r["step"]): r for r in rows}
    res = {"title": "Top marginal rates: one more 1 % of AW at 10, 20 and 50 x AW (wages alone, or each kind of "
                    "investment income on top of 1 x AW of wages), single person",
           "source": os.path.join(run_dir, "results.jsonl"), "countries": {}}
    for c in cs:
        o = {}
        for lv in levels:
            for k in kinds:
                a, b = T.get((c, lv, k, 0)), T.get((c, lv, k, 1))
                if not a or not b:
                    continue
                dg = b["gross"] - a["gross"]
                o[f"{k}@{lv}"] = {"all": r4(rate(tx(b, "all") - tx(a, "all"), dg)),
                                  "tax": r4(rate(tx(b, "tax") - tx(a, "tax"), dg)),
                                  "it": r4(rate(tx(b, "it") - tx(a, "it"), dg)),
                                  "surtaxes": r4(rate(b["surtaxes"] - a["surtaxes"], dg)),
                                  "local": r4(rate(b["localIncomeTax"] - a["localIncomeTax"], dg)),
                                  "social": r4(rate(b["employeeSocial"] - a["employeeSocial"], dg))}
                if "election" in a and "election" in b:
                    o[f"{k}@{lv}"]["election"] = [a["election"], b["election"]]
                    o[f"{k}@{lv}"]["all_default"] = r4(rate((b["gross"] - b["net_default"])
                                                            - (a["gross"] - a["net_default"]), dg))
        res["countries"][c] = o
    dump("top_rates.json", res)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what")
    ap.add_argument("--countries", default=",".join(COUNTRIES))
    a = ap.parse_args()
    cs = a.countries.split(",")
    todo = (["curves", "curves_ppp", "cliffs", "walls", "unit_scan", "family", "child_rank", "base", "progressivity",
             "top"] if a.what == "all"
            else a.what.split(","))
    for w in todo:
        t0 = time.time()
        r = globals()[w](cs)
        print(w, "done in %.1f s" % (time.time() - t0), flush=True)
