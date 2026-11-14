"""Tax-Calculator on the Tax Court returns (oracle_work/returns.json), one Records batch per tax year, current-law
policy for that year. Mapping adapted from global-law-lean tools/taxcode/diff/run_taxcalc.py.

    ~/Documents/tax-formalization-data/refs-venv/Scripts/python.exe oracle_tc.py
"""
import json, os
import pandas as pd
import taxcalc as tc

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oracle_work")
COLS = ["c00100", "c04800", "taxbc", "c09600", "eitc", "c07220", "c11070", "c07100", "setax", "c02500", "iitax",
        "niit", "standard", "c04470", "c05800", "ptax_amc", "recovery_rebate_credit"]

rets = json.load(open(os.path.join(WORK, "returns.json"), encoding="utf-8"))
res = [None] * len(rets)
for year in sorted({h["year"] for h in rets}):
    idx = [i for i, h in enumerate(rets) if h["year"] == year]
    rows = []
    for i in idx:
        h = rets[i]
        deps = h["dependents"]
        joint = h["filing"] == "mfj"
        eic = sum(1 for d in deps if d["age"] < 19 or (d["student"] and d["age"] < 24))
        rows.append(dict(
            RECID=i + 1, MARS={"single": 1, "mfj": 2, "mfs": 3, "hoh": 4, "qss": 5}[h["filing"]],
            XTOT=(2 if joint else 1) + len(deps), FLPDYR=year,
            age_head=h["age"], age_spouse=h["spouseAge"] if joint else 0,
            n24=sum(1 for d in deps if d["age"] < 17), nu18=sum(1 for d in deps if d["age"] < 18),
            nu06=sum(1 for d in deps if d["age"] < 6), nu13=sum(1 for d in deps if d["age"] < 13),
            EIC=min(3, eic), e00200=h["wages"], e00200p=h["wages"] - h["wagesSpouse"], e00200s=h["wagesSpouse"],
            e00900=h["se"] + h["seSpouse"], e00900p=h["se"] + (0 if joint else h["seSpouse"]),
            e00900s=h["seSpouse"] if joint else 0,
            e00300=h["interest"], e00400=h["exemptInterest"], e00600=h["ordDiv"], e00650=h["qualDiv"],
            p23250=h["ltcg"], p22250=h["stcg"], e01400=h["ira"], e01500=h["pensions"], e01700=h["pensions"],
            e02400=h["ss"], e02300=h["ui"],
            # otherIncome and gambling winnings: taxable state refunds is a plain ordinary-income line in AGI
            # (Form 4797 gain e01200 would count as EIC investment income)
            e00700=h["other"] + h["gamblingWin"],
            e03400=h["adjustments"],                       # an uncapped above-the-line deduction
            e19200=h["itemized"] + h["gamblingLoss"],      # the allowed itemized total, as interest (no floor/cap)
            blind_head=int(h["blind"]), blind_spouse=int(joint and h["spouseBlind"])))
    df = pd.DataFrame(rows)
    recs = tc.Records(data=df, start_year=year, gfactors=None, weights=None, adjust_ratios=None,
                      exact_calculations=True)
    pol = tc.Policy()
    # everyone claims EITC / ACTC (no random non-take-up)
    pol.implement_reform({"eitc_claim_prob_scale": {year: 9e99}, "actc_claim_prob_scale": {year: 9e99}})
    calc = tc.Calculator(policy=pol, records=recs)
    if calc.current_year != year:
        calc.advance_to_year(year)
    calc.calc_all()
    out = {}
    for c in COLS:
        try:
            out[c] = calc.array(c)
        except Exception:
            pass
    for j, i in enumerate(idx):
        r = {c: float(v[j]) for c, v in out.items()}
        r.update(key=rets[i]["key"], which=rets[i]["which"])
        res[i] = r
    print(year, len(idx), flush=True)
json.dump({"engine": "taxcalc " + tc.__version__, "results": res}, open(os.path.join(WORK, "tc_out.json"), "w"),
          indent=1)
