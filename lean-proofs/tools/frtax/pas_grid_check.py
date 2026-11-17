"""Default-rate grids: the statute dataset (data/pas_grids.jsonl) against the grids in the M code (chap-taux.m,
RASTXPACi, used for dependants' income, art. 204 H, III, 2) of each income year Y (rate year Y + 1), cell by cell.
Also checks the art. 204 H, II threshold per part: M's constant RFRPARQF, the indexed figure the BOFiP gives
(BOI-IR-PAS-20-20-10), Lean's `zeroRateThreshold` (read from Withholding.lean) and the figure printed in the
consolidated CGI on 1 September (pas_grids.jsonl, which lags one indexation). Writes runs/pas/grid_check.json."""
import json, os, re
H = os.path.expanduser("~/fr")
# BOI-IR-PAS-20-20-10 versions 20220516, 20230626, 20240618, 20250507, 20260407 (and its "Remarque" for income 2025)
BOFIP = {2020: 25705, 2021: 26065, 2022: 27473, 2023: 28792, 2024: 29310, 2025: 29574}
_w = open(f"{H}/lean/FrTax/Withholding.lean", encoding="utf-8").read()
_w = _w[_w.index("def zeroRateThreshold"):]
LEAN = {int(a): int(b) for a, b in re.findall(r"\| (\d{4}) => (\d+)", _w[:_w.index("| _ =>")])}
SRC = {2020: "sources2020m_6_5", 2021: "sources2021m_5_7", 2022: "sources2022m_6_1", 2023: "sources2023m_8_0",
       2024: "sources2024m_3_13", 2025: "sources2025m_3_11"}
stat = {(g["rate_year"], g["zone"]): g for g in map(json.loads, open(f"{H}/data/pas_grids.jsonl"))}
res = {"cells": 0, "equal": 0, "diffs": [], "rfr": []}
for y, s in SRC.items():
    d = f"{H}/mlang/ir-calcul/{s}"
    tgv = open(f"{d}/tgvI.m", encoding="latin-1").read()
    const = {m.group(1): float(m.group(2)) for m in re.finditer(r"^(TXPAC\w+|RFRPARQF) : const=([\d.]+)", tgv, re.M)}
    t = open(f"{d}/chap-taux.m", encoding="latin-1").read()
    blk = t[t.index("RASTXPACi = "):]
    blk = blk[:blk.index(";")]
    parts = re.split(r"\+ null\((\d) - V_REGCO\)", blk)
    zones = {"metropole": parts[0], **{ {"5": "gmr", "6": "gm"}[parts[i]]: parts[i + 1] for i in range(1, len(parts), 2)}}
    for z, txt in zones.items():
        lows = [int(x) for x in re.findall(r"positif_ou_nul\(REVMENSPACi - (\d+)\)", txt)]
        rates = [const[r] if r in const else float(r) for r in re.findall(r"REVMENSPACi\) \* (TXPAC\w+|[\d.]+)|REVMENSPACi - \d+\) \* (TXPAC\w+|[\d.]+)", txt) for r in [r[0] or r[1]]]
        first0 = int(re.search(r"positif\((\d+) - REVMENSPACi\) \* 0", txt).group(1))
        g = stat.get((y + 1, z))
        if not g:
            continue
        mrow = {"lower_bounds": [first0] + lows[1:] if lows[0] == first0 else lows, "rates": rates}
        # lows lists the lower bound of each non-zero bracket; first0 is the end of the 0 % bracket
        mlo = lows
        for k in range(19):
            for what, a, b in (("lower", g["lower_bounds"][k], mlo[k] if k < len(mlo) else None),
                               ("rate", g["rates"][k + 1], mrow["rates"][k + 1] if k + 1 < len(mrow["rates"]) else None)):
                res["cells"] += 1
                if b is not None and abs(a - b) < 1e-9:
                    res["equal"] += 1
                else:
                    res["diffs"].append({"income_year": y, "rate_year": y + 1, "zone": z, "bracket": k + 2, "what": what,
                                         "statute": a, "M": b})
        res["cells"] += 1
        if first0 == g["lower_bounds"][0]:
            res["equal"] += 1
        else:
            res["diffs"].append({"income_year": y, "rate_year": y + 1, "zone": z, "what": "zero-bracket end", "statute": g["lower_bounds"][0], "M": first0})
    g = stat.get((y + 1, "metropole"))
    res["rfr"].append({"income_year": y, "rate_year": y + 1, "M_RFRPARQF": const.get("RFRPARQF"),
                       "BOFiP_indexed": BOFIP.get(y), "Lean": LEAN.get(y),
                       "printed_on_1_Sept": g["rfr_threshold_per_part_204H_II"] if g else None})
res["rfr_equal_M_BOFiP_Lean"] = sum(r["M_RFRPARQF"] == r["BOFiP_indexed"] == r["Lean"] for r in res["rfr"])
json.dump(res, open(f"{H}/runs/pas/grid_check.json", "w"), indent=1)
print(f"grid cells {res['equal']}/{res['cells']} equal")
for d in res["diffs"][:30]:
    print("  ", d)
print(f"204 H II threshold per part, M = BOFiP = Lean: {res['rfr_equal_M_BOFiP_Lean']}/{len(res['rfr'])} years")
for r in res["rfr"]:
    print("  RFR/part", r)
