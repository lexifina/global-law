"""Markdown tables from the chart data files, for RESULTS.md and the blog post.

    python3 report.py  -> TABLES.md (every number below is read from charts/*.json)
"""
import json
import os

ROOT = os.path.join(os.path.expanduser("~"), "cmp", "compare")
CH = os.path.join(ROOT, "charts")
ORDER = ["US", "FR", "UK", "DE", "JP"]
FAMS = ["single", "single_parent_2", "couple_1earner_2", "couple_2earner_2"]
FAMNAME = {"single": "single", "single_parent_2": "single parent, 2 children",
           "couple_1earner_2": "one-earner couple, 2 children", "couple_2earner_2": "two-earner couple (60:40), 2 children"}


def load(n):
    p = os.path.join(CH, n)
    return json.load(open(p)) if os.path.exists(p) else None


def pct(x, d=1):
    return "" if x is None else f"{100 * x:.{d}f} %"


def num(x):
    if x is None:
        return ""
    return f"{x:+,.0f}" if isinstance(x, (int, float)) else str(x)


def at(xs, ys, x):
    i = min(range(len(xs)), key=lambda j: abs(xs[j] - x))
    return ys[i]


def oecd_table(o):
    out = ["### OECD Taxing Wages 2026 (year 2025): Lean minus OECD, national currency",
           "", "Lines: income tax = central government income tax finally paid (CGITFP, mapped per country), SSC = "
           "employee social security contributions, transfers = cash transfers, take-home = take-home pay "
           "(US: excluding the OECD's state and local tax, which the federal model leaves out).", "",
           "| Country | Type | Gross | Income tax | SSC | Transfers | Take-home |", "|---|---|---|---|---|---|---|"]
    for r in sorted(o["rows"], key=lambda r: (ORDER.index(r["country"]), r["type"])):
        L = r["lines"]
        out.append(f"| {r['country']} | {r['type']} | {r['gross']:,.0f} | {num(L['CGITFP']['diff'])} | "
                   f"{num(L['EECSSC']['diff'])} | {num(L['CTGG']['diff'])} | {num(L['THP']['diff'])} |")
    return "\n".join(out)


def curves_tables():
    out = []
    for fam in FAMS:
        c = load(f"curves_{fam}.json")
        if not c:
            continue
        out += [f"### Average rates, {FAMNAME[fam]} (income tax alone / everything: income tax + surtaxes + local + "
                f"employee social - benefits)", "",
                "| Country | 0.5 AW | 0.67 AW | 1 AW | 1.67 AW | 3 AW | 5 AW | marginal (all) at 1 AW: 1 % / 10 % window | at 5 AW (10 %) | highest marginal (all), 1 % window |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for ct in ORDER:
            s = c["countries"].get(ct)
            if not s:
                continue
            cells = []
            for x in (0.5, 0.67, 1.0, 1.67, 3.0, 5.0):
                cells.append(f"{pct(at(s['x'], s['avg_it'], x))} / {pct(at(s['x'], s['avg_all'], x))}")
            m1 = at(s["x_mid"], s["mtr_all"], 1.0)
            m1s = at(s["x"], s["mtr10_all"], 1.0) if s.get("mtr10_all") else None
            m5 = s["mtr10_all"][-1] if s.get("mtr10_all") else s["mtr_all"][-1]
            # Japan: leave out the model boundary below 0.35 AW (no national pension / health insurance for a lone
            # earner under 88,000 yen a month; see model_boundaries in the chart file)
            lo = 0.35 if ct == "JP" else -1
            cand = [(m, x) for m, x in zip(s["mtr_all"], s["x_mid"]) if m is not None and x >= lo]
            mx, xm = max(cand) if cand else (None, None)
            note = " (x >= 0.35 AW)" if ct == "JP" else ""
            out.append(f"| {ct} | " + " | ".join(cells) + f" | {pct(m1)} / {pct(m1s)} | {pct(m5)} | {pct(mx)} at {xm} AW{note} |")
        out.append("")
    return "\n".join(out)


def cliffs_table():
    s = load("cliffs_summary.json")
    if not s:
        return ""
    out = ["### Notches (one more unit of pay lowers net income) and bands above 100 %", "",
           "| Country | Cause | Law | Notches found | First at | Worst loss for one more unit |", "|---|---|---|---|---|---|"]
    for k, v in sorted(s["causes"].items(), key=lambda kv: ORDER.index(kv[1]["country"])):
        w = v["worst"]
        out.append(f"| {v['country']} | {v['cause']} | {v['law']} | {v['notches']} | {v['first_gross']:,} | "
                   f"{w['net_change']:+,.2f} at {w['gross']:,} ({w['family']}) |")
    out += ["", "Bands where the marginal rate over 1 % of AW exceeds 100 %:", ""]
    for b in s["bands_mtr_above_100"]:
        out.append(f"- {b['country']} {b['family']}: gross {b['g0']:,} to {b['g1']:,} ({b['g0_aw']}-{b['g1_aw']} AW)")
    return "\n".join(out)


def family_tables():
    f = load("family.json")
    if not f:
        return ""
    xs = f["x_values"]
    out = ["### What a child is worth (per child, % of AW): total (via tax / via benefits)", "",
           "| Country | Household | 0.5 AW | 1 AW | 2 AW | 3 AW | 5 AW |", "|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        o = f["countries"].get(ct)
        if not o:
            continue
        for name, d in o["child_value_per_child"].items():
            cells = [f"{pct(at(xs, d['total'], x), 2)} ({pct(at(xs, d['via_tax'], x), 2)} / {pct(at(xs, d['via_benefits'], x), 2)})"
                     for x in (0.5, 1.0, 2.0, 3.0, 5.0)]
            out.append(f"| {ct} | {name.replace('_', ' ')} | " + " | ".join(cells) + " |")
    out += ["", "### Marriage bonus (+) or penalty (-): married minus the same two people unmarried, % of AW", "",
            "| Country | Earnings split | 0.5 AW | 1 AW | 2 AW | 3 AW | 5 AW |", "|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        o = f["countries"].get(ct)
        if not o:
            continue
        for name, d in o["marriage"].items():
            out.append(f"| {ct} | {name.replace('_', ' ')} | " + " | ".join(pct(at(xs, d['total'], x), 2) for x in (0.5, 1.0, 2.0, 3.0, 5.0)) + " |")
    out += ["", "### Two earners (50:50) minus one earner, same household earnings, % of AW", "",
            "| Country | Couple | 0.5 AW | 1 AW | 2 AW | 3 AW | 5 AW |", "|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        o = f["countries"].get(ct)
        if not o:
            continue
        for name, d in o["earner_split"].items():
            out.append(f"| {ct} | {name.replace('_', ' ')} | " + " | ".join(pct(at(xs, d['total'], x), 2) for x in (0.5, 1.0, 2.0, 3.0, 5.0)) + " |")
    return "\n".join(out)


def child_rank_table():
    r = load("child_rank.json")
    if not r:
        return ""
    out = ["### What the first, second and third child are each worth (married one-earner couple; % of AW)", "",
           "| Country | " + " | ".join(f"{lv} AW: 1st / 2nd / 3rd" for lv in r["levels"]) + " |",
           "|---|" + "---|" * len(r["levels"])]
    for ct in ORDER:
        o = r["countries"].get(ct)
        if not o:
            continue
        cells = []
        for lv in r["levels"]:
            d = o.get(str(lv), {})
            cells.append(" / ".join(f"{100 * d[k]:.1f}" if d.get(k) is not None else "" for k in ("child1", "child2", "child3")))
        out.append(f"| {ct} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def unit_scan_table():
    u = load("unit_scan.json")
    if not u:
        return ""
    out = ["### One more unit of pay near the average wage (single): how often and how much net income falls", "",
           "| Country | Points scanned | Falls | Falls of more than one unit | Worst fall (at pay) |", "|---|---|---|---|---|"]
    for ct in ORDER:
        o = u["countries"].get(ct)
        if not o:
            continue
        w = o["worst"]
        ws = "" if not w else f"{w['net_change']:+,.2f} at {w['wages']:,} ({', '.join(f'{k} {v:+,.2f}' for k, v in w['changes'].items())})"
        out.append(f"| {ct} | {o['points']:,} | {o['falls']:,} | {o['falls_over_one_unit']:,} | {ws} |")
    out += ["", "Window: 0.9-1.1 x AW in steps of one unit (Japan: 0.99-1.01 x AW in steps of one yen)."]
    return "\n".join(out)


def walls_table():
    w = load("walls_second_earner.json")
    if not w:
        return ""
    out = ["### Second earner: participation tax rate (household taxes on the spouse's pay / that pay), principal at 1 x AW", "",
           "| Country | Household | spouse at 0.1 AW | 0.25 AW | 0.5 AW | 0.67 AW | 1 AW |", "|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        d = w["countries"].get(ct)
        if not d:
            continue
        for key, s in sorted(d.items()):
            out.append(f"| {ct} | {key} | " + " | ".join(pct(at(s['spouse_aw'], s['participation_tax_rate'], x)) for x in (0.1, 0.25, 0.5, 0.67, 1.0)) + " |")
    return "\n".join(out)


def with_default(e, key, dkey):
    """A rate under the cheapest election, followed by the model default's in brackets when they differ."""
    if not e:
        return ""
    s = pct(e.get(key))
    d = e.get(dkey)
    if d is not None and e.get(key) is not None and abs(d - e[key]) >= 0.0005:
        s += f" (default {pct(d)})"
    return s


def base_table():
    b = load("base.json")
    if not b:
        return ""
    kinds = b["kinds"]
    out = ["### Marginal rate on 10 % of AW more of each kind of income (single, all taxes and contributions)", "",
           "| Country | Wage level | " + " | ".join(kinds) + " |", "|---|---|" + "---|" * len(kinds)]
    for ct in ORDER:
        o = b["countries"].get(ct)
        if not o:
            continue
        for lv, row in o["marginal"].items():
            out.append(f"| {ct} | {lv} AW | " + " | ".join(with_default(row.get(k), 'all', 'all_default') for k in kinds) + " |")
    out += ["", "### Living on 1 x AW of one kind of income only (single): average rate, all taxes and contributions", "",
            "| Country | " + " | ".join(kinds) + " |", "|---|" + "---|" * len(kinds)]
    for ct in ORDER:
        o = b["countries"].get(ct)
        if o:
            out.append(f"| {ct} | " + " | ".join(with_default(o['only'].get(k), 'avg_all', 'avg_all_default') for k in kinds) + " |")
    out += ["", "Where the law lets the taxpayer choose how investment income is taxed, the household makes the cheapest "
            "choice (harness/common.py ELECTIONS; France and Germany choose inside the model). Japan: dividends left to "
            "final withholding, declared separately or aggregated with the dividend credit; gains withheld or declared. "
            "\"default\" is the Japanese model's default (final withholding, 20.315 %)."]
    return "\n".join(out)


def top_table():
    t = load("top_rates.json")
    if not t:
        return ""
    kinds = ["wages", "interest", "dividends", "capitalGains", "rentalIncome"]
    out = ["### Top marginal rates: 1 % of AW more at 10, 20 and 50 x AW (single; investment income on top of 1 x AW of wages)", "",
           "| Country | Level | " + " | ".join(kinds) + " |", "|---|---|" + "---|" * len(kinds)]
    for ct in ORDER:
        o = t["countries"].get(ct)
        if not o:
            continue
        for lv in (10, 20, 50):
            out.append(f"| {ct} | {lv} AW | " + " | ".join(with_default(o.get(f"{k}@{lv}"), 'all', 'all_default') for k in kinds) + " |")
    return "\n".join(out)


def prog_table():
    p = load("progressivity.json")
    if not p:
        return ""
    out = ["### Progressivity on one synthetic population (" + p["population"] + ")", "",
           "| Country | Household | avg rate: income tax | avg rate: all | Kakwani: income tax | Kakwani: all | Reynolds-Smolensky | Gini net |",
           "|---|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        o = p["countries"].get(ct)
        if not o:
            continue
        for fam, v in o.items():
            k_it = "" if v["kakwani_it"] is None else f"{v['kakwani_it']:.3f}"
            k_all = "" if v["kakwani_all"] is None or v["avg_rate_all"] < 0.02 else f"{v['kakwani_all']:.3f}"
            out.append(f"| {ct} | {fam} | {pct(v['avg_rate_it'])} | {pct(v['avg_rate_all'])} | {k_it} | {k_all} | "
                       f"{v['reynolds_smolensky']:.3f} | {v['gini_net']:.3f} |")
    out += ["", "Kakwani left blank where the average tax is under 2 % or negative (refundable credits): the index is "
            "not meaningful there (US one-earner couple: income tax -1.5 % on average)."]
    return "\n".join(out)


def complexity_table():
    c = load("complexity.json")
    if not c:
        return ""
    out = ["### Size of each Lean model (computation = modules the calculator imports; whole = with tests and proofs)", "",
           "| Country | Lean lines (computation / whole) | definitions | theorems (whole) | #guard/example checks | distinct numeric literals in the computation (outside reproduced tables) | reproduced data tables | provisions cited |",
           "|---|---|---|---|---|---|---|---|"]
    for ct in ORDER:
        e = c["models"].get(ct)
        if not e or "computation" not in e:
            continue
        a, w = e["computation"], e["whole_model"]
        tables = ", ".join(f"{os.path.basename(t['file'])} ({t['distinct_literals']:,})" for t in a.get("data_table_files", [])) or "none"
        out.append(f"| {ct} | {a['lines']:,} / {w['lines']:,} | {a['defs']} / {w['defs']} | {w['theorems']} | {w['checks']} | "
                   f"{a.get('distinct_literals_outside_tables', a['distinct_literals']):,} | {tables} | {w['distinct_provisions_cited']} |")
    out += ["", "Counts measure the models, not the law: they are comparable because the five were written to one style "
            "(one definition per provision, statute quoted). The adapters this comparison added to the US and French "
            "models are counted apart in `charts/complexity.json` (comparison_adapter)."]
    return "\n".join(out)


def main():
    parts = ["# Tables (generated by harness/report.py from charts/*.json; do not edit by hand)", ""]
    o = load("oecd_check.json")
    if o:
        parts.append(oecd_table(o))
    for f in (curves_tables, cliffs_table, unit_scan_table, family_tables, child_rank_table, walls_table, base_table,
              top_table, prog_table, complexity_table):
        t = f()
        if t:
            parts += ["", t]
    open(os.path.join(ROOT, "TABLES.md"), "w").write("\n".join(parts) + "\n")
    print("\n".join(parts)[:6000])


if __name__ == "__main__":
    main()
