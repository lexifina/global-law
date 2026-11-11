"""Select 2018-2024 encoded Tax Court entries that PolicyEngine-US and Tax-Calculator can represent, and write
oracle_work/lean_in.json (the cases, for Run.lean) and oracle_work/returns.json (corrected and as-filed returns as
engine households).

    python oracle_select.py
"""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # .../taxcourt
ENC = os.path.join(BASE, "encoded")
WORK = os.path.join(BASE, "validation", "oracle_work")

# Fields the engines can take (directly or by an exact mapping, see oracle_engines.py)
SUPPORTED = {"filing", "taxpayerAge", "spouseAge", "taxpayerBlind", "spouseBlind", "wages", "wagesSpouse", "seProfit",
             "seProfitSpouse", "taxableInterest", "taxExemptInterest", "ordinaryDividends", "qualifiedDividends",
             "capitalGain", "longTermGain", "iraDistributions", "pensions", "socialSecurity", "unemployment",
             "unemploymentSpouse", "otherIncome", "adjustments", "itemizedDeductions", "itemize", "withholding",
             "estimatedPayments", "earlyDistributions", "otherNonrefundableCredits", "otherRefundableCredits",
             "otherTaxes", "dependents", "claimEIC", "claimCTC", "rollovers", "gamblingWinnings", "gamblingLosses",
             "agiOverride"}
BLOCKERS = {"ptc": "§36B premium tax credit", "foreign": "§911 exclusion", "ssLumpSums": "§86(e) lump-sum election",
            "alimonyReceived": "alimony (instrument-date rules)", "alimonyPaid": "alimony (instrument-date rules)",
            "hsaDistributions": "§223(f) HSA distributions", "students": "§25A education credits",
            "policyLapses": "§72(e) policy lapse", "advanceCtc": "2021 advance CTC reconciliation",
            "priorYearEarnedIncome": "2020/2021 prior-year earned-income election", "ira": "§219 IRA deduction",
            "spouseItemizes": "MFS spouse-itemizes rule", "charityNonItemizer": "non-itemizer charity",
            "qbiDeduction": "§199A given as an amount", "earnedIncomeOverride": "earned income given as a total"}
MONEY = {"wages", "wagesSpouse", "seProfit", "seProfitSpouse", "taxableInterest", "ordinaryDividends", "capitalGain",
         "iraDistributions", "pensions", "socialSecurity", "unemployment", "otherIncome", "gamblingWinnings",
         "itemizedDeductions", "rollovers"}


def rollover_includible(r):
    """§408(d)(3): the part not rolled over within 60 days (no waiver) is includible. Lean computes this too; the
    engines have no rollover input, so the includible part is added to pensions."""
    late = r.get("days", 0) > 60 and not r.get("waiverGranted", False)
    return r.get("distribution", 0) if late else max(0, r.get("distribution", 0) - r.get("rolledOver", 0))


def household(f, year):
    notes = []
    pensions = f.get("pensions", 0)
    for r in f.get("rollovers", []):
        inc = rollover_includible(r)
        pensions += inc
        notes.append(f"rollover includible {inc} added to pensions")
    deps = f.get("dependents", [])
    return dict(
        year=year, filing=f.get("filing", "single"), age=f.get("taxpayerAge", 40), spouseAge=f.get("spouseAge", 40),
        blind=f.get("taxpayerBlind", False), spouseBlind=f.get("spouseBlind", False),
        wages=f.get("wages", 0), wagesSpouse=f.get("wagesSpouse", 0), se=f.get("seProfit", 0),
        seSpouse=f.get("seProfitSpouse", 0), interest=f.get("taxableInterest", 0),
        exemptInterest=f.get("taxExemptInterest", 0), ordDiv=f.get("ordinaryDividends", 0),
        qualDiv=f.get("qualifiedDividends", 0), ltcg=f.get("longTermGain", 0),
        stcg=f.get("capitalGain", 0) - f.get("longTermGain", 0), ira=f.get("iraDistributions", 0), pensions=pensions,
        ss=f.get("socialSecurity", 0), ui=f.get("unemployment", 0), uiSpouse=f.get("unemploymentSpouse", 0),
        other=f.get("otherIncome", 0), adjustments=f.get("adjustments", 0),
        itemized=f.get("itemizedDeductions", 0),
        itemize=f.get("itemize"), gamblingWin=f.get("gamblingWinnings", 0), gamblingLoss=min(f.get("gamblingLosses", 0), f.get("gamblingWinnings", 0)),  # §165(d) cap
        otherNonref=f.get("otherNonrefundableCredits", 0), otherRef=f.get("otherRefundableCredits", 0),
        otherTaxes=f.get("otherTaxes", 0),
        dependents=[dict(age=d.get("age", 0), student=d.get("student", False), ssn=d.get("hasSSN", True))
                    for d in deps]), notes


def main():
    os.makedirs(WORK, exist_ok=True)
    lean_in, rets, sel = [], [], []
    seen = set()
    for path in sorted(glob.glob(os.path.join(ENC, "*.case.json"))):
        cid = os.path.basename(path)[:-len(".case.json")]
        cs = json.load(open(path, encoding="utf-8"))
        multi = isinstance(cs, list)
        cs = cs if multi else [cs]
        for i, c in enumerate(cs):
            key = f"{cid}#{i}" if multi else cid
            y = c.get("taxYear", 0)
            entry = dict(key=key, id=cid, index=i, citation=c.get("citation"), taxYear=y)
            if not 2018 <= y <= 2024:
                continue
            f, a = c.get("facts", {}), c.get("asFiled")
            used = set(f) | set(a or {})
            block = sorted({BLOCKERS[k] for k in used if k in BLOCKERS and (f.get(k) or (a or {}).get(k))})
            money = [k for k in used if k in MONEY and (f.get(k) or (a or {}).get(k))]
            sig = json.dumps([f, a], sort_keys=True)
            if block:
                entry["skipped"] = "needs " + ", ".join(block)
            elif not money:
                entry["skipped"] = "no income facts (only dependency / filing-status / eligibility findings)"
            elif sig in seen:
                entry["skipped"] = "same returns as an earlier variant of this case (penalty-only variant)"
            elif set(used) - SUPPORTED:
                entry["skipped"] = "fields not mapped: " + ", ".join(sorted(set(used) - SUPPORTED))
            if "skipped" in entry:
                sel.append(entry); continue
            seen.add(sig)
            entry["leanIndex"] = len(lean_in)
            lean_in.append(c)
            h, notes = household(f, y)
            rets.append(dict(key=key, which="corrected", **h)); entry["notes"] = notes
            if a:
                ha, na = household(a, y)
                rets.append(dict(key=key, which="asFiled", **ha))
            entry["taxShown"] = c.get("taxShown")
            entry["expected"] = c.get("expected", [])
            sel.append(entry)
    json.dump(lean_in, open(os.path.join(WORK, "lean_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump(rets, open(os.path.join(WORK, "returns.json"), "w", encoding="utf-8"), indent=1)
    json.dump(sel, open(os.path.join(WORK, "selection.json"), "w", encoding="utf-8"), indent=1)
    inc = [e for e in sel if "skipped" not in e]
    print(f"{len(inc)} included, {len(sel) - len(inc)} skipped, {len(rets)} returns")
    for e in sel:
        print(e["key"], e.get("skipped", "included"))


main()
