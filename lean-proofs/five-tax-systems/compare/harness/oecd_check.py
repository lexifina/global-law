"""Independent check of the five models against the OECD's published country tables (Taxing Wages 2026, year 2025).

    python3 oecd_check.py [--countries US,FR] [--rerun]

Runs the eight Taxing Wages family types at the OECD's own average wage through each available model, maps each
model's figures onto the OECD's lines, and writes charts/oecd_check.json (every line: ours, OECD, difference) and
runs/oecd/latest/check.md (a table for RESULTS.md).

The OECD lines compared (OECD.CTP.TPS:DSD_TAX_WAGES_COU@DF_TW_COU, national currency):
  CGTC     central government taxable income
  CGITLETC central government income tax before tax credits
  CGITFP   central government income tax finally paid (after credits; refundable credits make it negative)
  SLT      state and local income taxes
  EECSSC   employees' compulsory social security contributions
  CTGG     cash transfers from general government
  THP      take-home pay = gross - CGITFP - SLT - EECSSC + CTGG
How each country's own classification maps onto these lines is in MAP below (the OECD counts France's CSG/CRDS on pay
as income tax, Germany's Kindergeld as a tax credit and its Soli inside income tax, Japan's 復興特別所得税 inside
income tax and 住民税 as local tax).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import COUNTRIES, ROOT  # noqa: E402
import run as runner  # noqa: E402

OECD = json.load(open(os.path.join(ROOT, "data", "oecd", "tw_cou_xdc.json")))
ISO3 = {"US": "USA", "FR": "FRA", "UK": "GBR", "DE": "DEU", "JP": "JPN"}
TYPES = ["S67", "S100", "S167", "SP67", "M100_0", "M100_100", "M100_67", "M100_67nc"]


def d(row, k, default=None):
    return (row.get("detail") or {}).get(k, default)


def st(row, k):
    return row.get("surtax_" + k, 0)


def map_us(row):
    return {"CGTC": d(row, "taxableIncome"), "CGITLETC": d(row, "regularTax"),
            "CGITFP": row["incomeTax"] + st(row, "AdditionalMedicare") + st(row, "NIIT"),
            "SLT": None, "EECSSC": row["employeeSocial"], "CTGG": row["benefits"]}


def map_fr(row):
    csg = d(row, "csgCrdsWages", 0)
    return {"CGTC": d(row, "rni"), "CGITLETC": None,
            "CGITFP": row["incomeTax"] + st(row, "CEHR") + st(row, "CDHR") + csg,
            "SLT": row["localIncomeTax"], "EECSSC": row["employeeSocial"] - csg, "CTGG": row["benefits"]}


def generic(row):
    """UK, Germany, Japan until their mapping is checked: income tax plus every surtax against CGITFP, local tax
    against SLT, social contributions and benefits as reported."""
    return {"CGTC": None, "CGITLETC": None, "CGITFP": row["incomeTax"] + row["surtaxes"],
            "SLT": row["localIncomeTax"], "EECSSC": row["employeeSocial"], "CTGG": row["benefits"]}


MAP = {"US": map_us, "FR": map_fr, "UK": generic, "DE": generic, "JP": generic}
# Germany: the OECD books Kindergeld as a child tax credit inside CGITFP (and CTGG = 0), so CGITFP is compared with
# income tax + Soli - Kindergeld when the model reports Kindergeld as a benefit; set in map_de once its output is known.
_mapfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oecd_maps.py")
if os.path.exists(_mapfile):
    exec(open(_mapfile).read())


def compare(rows):
    out = []
    for r in rows:
        c, t = r["country"], r["type"]
        o = OECD[ISO3[c]]["2025"][t]
        ours = MAP[c](r)
        thp_o = o["GEBT"] - o["CGITFP"] - o["SLT"] - o["EECSSC"] + o["CTGG"]
        lines = {}
        for k in ["CGTC", "CGITLETC", "CGITFP", "SLT", "EECSSC", "CTGG"]:
            ov = o.get(k)
            mv = ours.get(k)
            lines[k] = {"ours": mv, "oecd": None if ov is None else round(ov, 2),
                        "diff": None if (mv is None or ov is None) else round(mv - ov, 2)}
        # take-home pay without the lines a model leaves out (US state and local tax)
        slt_o = o["SLT"] if ours.get("SLT") is not None else 0
        thp_cmp = thp_o + (0 if ours.get("SLT") is not None else o["SLT"])
        mine = r["net"] if ours.get("SLT") is not None else r["net"]
        lines["THP"] = {"ours": mine, "oecd": round(thp_cmp, 2), "diff": round(mine - thp_cmp, 2),
                        "note": "" if ours.get("SLT") is not None else "OECD THP plus its state and local tax"}
        out.append({"country": c, "type": t, "gross": r["gross"], "oecd_gross": round(o["GEBT"], 2),
                    "lines": lines, "unsupported": r.get("unsupported", [])})
    return out


def markdown(cmp):
    lines = ["| Country | Type | Line | Lean | OECD | Lean - OECD |", "|---|---|---|---|---|---|"]
    for x in cmp:
        for k, v in x["lines"].items():
            if v["ours"] is None and k not in ("SLT",):
                continue
            ours = "n/m" if v["ours"] is None else f"{v['ours']:,}"
            oecd = "" if v["oecd"] is None else f"{v['oecd']:,.0f}"
            diff = "" if v["diff"] is None else f"{v['diff']:+,.0f}"
            lines.append(f"| {x['country']} | {x['type']} | {k} | {ours} | {oecd} | {diff} |")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default=",".join(COUNTRIES))
    ap.add_argument("--rerun", action="store_true")
    ap.add_argument("--age", type=int, default=None, help="override every adult's age (variant run)")
    ap.add_argument("--out", default="oecd_check.json")
    a = ap.parse_args()
    cs = a.countries.split(",")
    gen = None
    if a.age is not None:
        def gen(cs2):
            hs, meta = runner.REGISTRY["oecd"](cs2)
            for c in hs:
                for h in hs[c]:
                    for ad in h["adults"]:
                        ad["age"] = a.age
            return hs, meta
    run_dir, rows, info = runner.run("oecd" if a.age is None else f"oecd_age{a.age}", cs, gen=gen, elections=False)
    cmp = compare(rows)
    json.dump({"source": "OECD Taxing Wages 2026, country tables 2025 (DSD_TAX_WAGES_COU@DF_TW_COU 2.1); Lean models "
               "via harness/oecd_check.py", "run": run_dir, "exes": info["countries"], "rows": cmp},
              open(os.path.join(ROOT, "charts", a.out), "w"), indent=1, ensure_ascii=False)
    md = markdown(cmp)
    open(os.path.join(run_dir, "check.md"), "w").write(md + "\n")
    print(md)
    print(json.dumps(info["countries"], indent=1))
