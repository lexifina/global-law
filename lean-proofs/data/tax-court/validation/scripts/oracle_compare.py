"""Compare PolicyEngine-US and Tax-Calculator with the Lean model and the court, per encoded Tax Court case.

    python oracle_select.py            # oracle_work/{lean_in,returns,selection}.json
    lake env lean --run LegalProofs/USTax/TaxCourt/Run.lean oracle_work/lean_in.json oracle_work/lean_out.json
    <pev python> oracle_pe.py; <refs-venv python> oracle_tc.py
    python oracle_compare.py           # validation/oracle_results.json

Engine net tax = regular tax + AMT - nonrefundable credits (engine; then the case's other nonrefundable credits,
capped) + SE tax + §72(t) + other taxes - EIC - refundable CTC - other refundable credits. Neither engine computes
§72(t) (PolicyEngine `qualified_retirement_penalty` and Tax-Calculator `e09900` are inputs), so the engines' net tax
uses Lean's §72(t) figure. NIIT, additional Medicare tax and the recovery rebate credit are left out of the net tax
(Lean takes the first two as `otherTaxes` amounts found by the court and does not model the third); they are reported
in the notes when an engine computes one.
"""
import json, os

V = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(V, "oracle_work")
TOL = 10

PE = {"agi": "adjusted_gross_income", "taxableIncome": "taxable_income", "eic": "eitc",
      "ctcNonrefundable": "non_refundable_ctc", "refundableCtc": "refundable_ctc",
      "taxableSocialSecurity": "taxable_social_security", "seTax": "self_employment_tax"}
TC = {"agi": "c00100", "taxableIncome": "c04800", "regularTax": "taxbc", "eic": "eitc", "ctcNonrefundable": "c07220",
      "refundableCtc": "c11070", "taxableSocialSecurity": "c02500", "seTax": "setax"}
ITEMS = ["agi", "taxableIncome", "regularTax", "eic", "ctcNonrefundable", "refundableCtc", "taxableSocialSecurity",
         "seTax", "earlyDistributionTax", "totalTax", "netTax"]


def engine_figures(r, kind, h, lean_edt):
    if r is None or "error" in r:
        return None, [f"{kind} error: {r and r.get('error')}"]
    notes = []
    if kind == "policyengine":
        g = {k: r[v] for k, v in PE.items()}
        amt = r["alternative_minimum_tax"]
        g["regularTax"] = r["income_tax_before_credits"] - amt
        nonref = r["income_tax_capped_non_refundable_credits"]
        extra = {"NIIT": r.get("net_investment_income_tax", 0), "additional Medicare tax":
                 r.get("additional_medicare_tax", 0), "recovery rebate credit": r.get("recovery_rebate_credit", 0)}
    else:
        g = {k: r[v] for k, v in TC.items()}
        amt = r["c09600"]
        nonref = r["c07100"]
        extra = {"NIIT": r.get("niit", 0), "additional Medicare tax": r.get("ptax_amc", 0),
                 "recovery rebate credit": r.get("recovery_rebate_credit", 0)}
    if amt:
        notes.append(f"{kind} AMT {amt:.0f} (in its net tax; Lean takes AMT as otherTaxes)")
    for k, v in extra.items():
        if round(v):
            notes.append(f"{kind} {k} {v:.0f} (not in net tax)")
    other_nonref = min(h["otherNonref"], max(0.0, g["regularTax"] + amt - nonref))
    g["earlyDistributionTax"] = None
    g["totalTax"] = g["regularTax"] + amt - nonref - other_nonref + g["seTax"] + lean_edt + h["otherTaxes"]
    g["netTax"] = g["totalTax"] - g["eic"] - g["refundableCtc"] - h["otherRef"]
    return {k: (None if v is None else round(v)) for k, v in g.items()}, notes


def main():
    sel = json.load(open(os.path.join(WORK, "selection.json"), encoding="utf-8"))
    lean = json.load(open(os.path.join(WORK, "lean_out.json"), encoding="utf-8"))
    rets = {(h["key"], h["which"]): h for h in json.load(open(os.path.join(WORK, "returns.json"), encoding="utf-8"))}
    pe_doc = json.load(open(os.path.join(WORK, "pe_out.json")))
    tc_doc = json.load(open(os.path.join(WORK, "tc_out.json")))
    pe = {(r["key"], r["which"]): r for r in pe_doc["results"]}
    tc = {(r["key"], r["which"]): r for r in tc_doc["results"]}
    cases, tot = [], {"items": 0, "itemsAllThreeComputed": 0, "allThreeAgree": 0, "allThreeExact": 0, "itemsWithCourt": 0, "itemsWithCourtAllThreeComputed": 0, "allThreeAgreeWithCourt": 0,
                      "leanAgreesWithCourt": 0, "policyengineAgreesWithCourt": 0, "taxcalcAgreesWithCourt": 0,
                      "itemsPeComputed": 0, "itemsTcComputed": 0, "peAgreesWithLean": 0, "tcAgreesWithLean": 0}
    for e in sel:
        out = {"id": e["id"], "key": e["key"], "citation": e["citation"], "taxYear": e["taxYear"]}
        if "skipped" in e:
            out.update(status="skipped", reason=e["skipped"]); cases.append(out); continue
        out["status"] = "included"
        lo = lean[e["leanIndex"]]
        court = {x["item"]: x["value"] for x in e["expected"] if x.get("value") is not None}
        notes = list(e.get("notes", []))
        items = []
        nets = {}
        for which in ("corrected", "asFiled"):
            lr = lo.get(which)
            if not lr:
                continue
            h = rets[(e["key"], which)]
            edt = lr["earlyDistributionTax"]
            figs = {}
            for kind, src in (("policyengine", pe), ("taxcalc", tc)):
                figs[kind], n = engine_figures(src.get((e["key"], which)), kind, h, edt)
                notes += [f"{which}: {x}" for x in n]
            nets[which] = {"lean": lr["netTax"], **{k: (v or {}).get("netTax") for k, v in figs.items()}}
            for it in ITEMS:
                lv = lr[it]
                cname = it if which == "corrected" else {"agi": "asFiled.agi", "taxableIncome": "asFiled.taxableIncome",
                    "regularTax": "asFiled.regularTax", "totalTax": "asFiled.totalTax", "netTax": "asFiled.netTax",
                    "eic": "asFiled.eic"}.get(it)
                cv = court.get(cname) if cname else None
                if cv is None and which == "asFiled" and it == "regularTax":
                    cv = court.get("asFiled.tax")
                pv, tv = (figs["policyengine"] or {}).get(it), (figs["taxcalc"] or {}).get(it)
                if lv == 0 and not pv and not tv and cv is None and it not in ("netTax", "agi"):
                    continue  # all zero, nothing found by the court: not an informative item
                items.append(dict(item=it if which == "corrected" else "asFiled." + it, court=cv, lean=lv,
                                  policyengine=pv, taxcalc=tv))
        # deficiency
        shown = lo.get("taxShown")
        if lo.get("deficiency") is not None:
            def defi(k):
                c = nets["corrected"].get(k)
                if c is None:
                    return None
                if e.get("taxShown") is not None:
                    return c - e["taxShown"]
                a = nets.get("asFiled", {}).get(k)
                return None if a is None else c - a
            items.append(dict(item="deficiency", court=court.get("deficiency"), lean=lo["deficiency"],
                              policyengine=defi("policyengine"), taxcalc=defi("taxcalc")))
        for x in items:
            vals = [x["lean"], x["policyengine"], x["taxcalc"]]
            close = lambda a, b: a is not None and b is not None and abs(a - b) <= TOL
            x["peAgreesLean"] = close(x["policyengine"], x["lean"]) if x["policyengine"] is not None else None
            x["tcAgreesLean"] = close(x["taxcalc"], x["lean"]) if x["taxcalc"] is not None else None
            x["allThreeAgree"] = all(v is not None for v in vals) and close(vals[0], vals[1]) and close(vals[0], vals[2]) \
                and close(vals[1], vals[2])
            if x["court"] is not None:
                x["leanAgreesCourt"] = close(x["lean"], x["court"])
                x["peAgreesCourt"] = close(x["policyengine"], x["court"]) if x["policyengine"] is not None else None
                x["tcAgreesCourt"] = close(x["taxcalc"], x["court"]) if x["taxcalc"] is not None else None
            x["exactAll"] = x["allThreeAgree"] and len({v for v in vals}) == 1
            tot["items"] += 1
            comparable = all(v is not None for v in vals)
            tot["itemsAllThreeComputed"] += comparable
            tot["allThreeAgree"] += x["allThreeAgree"]
            tot["allThreeExact"] += x["exactAll"]
            tot["itemsPeComputed"] += x["policyengine"] is not None
            tot["itemsTcComputed"] += x["taxcalc"] is not None
            tot["peAgreesWithLean"] += bool(x["peAgreesLean"])
            tot["tcAgreesWithLean"] += bool(x["tcAgreesLean"])
            if x["court"] is not None:
                tot["itemsWithCourt"] += 1
                tot["leanAgreesWithCourt"] += x["leanAgreesCourt"]
                tot["policyengineAgreesWithCourt"] += bool(x["peAgreesCourt"])
                tot["taxcalcAgreesWithCourt"] += bool(x["tcAgreesCourt"])
                tot["allThreeAgreeWithCourt"] += x["allThreeAgree"] and x["leanAgreesCourt"]
                tot["itemsWithCourtAllThreeComputed"] += comparable
        for x in items:  # default classification; oracle_annotations.json overrides
            ev = [v for v in (x["policyengine"], x["taxcalc"]) if v is not None]
            if x["item"].endswith("earlyDistributionTax"):
                x["note"] = ("engine not supporting: §72(t) is an input in both engines (PolicyEngine "
                             "qualified_retirement_penalty, Tax-Calculator e09900); their net tax uses Lean's figure")
            elif ev and all(abs(v - x["lean"]) <= TOL for v in ev) and any(v != x["lean"] for v in ev):
                x["note"] = ("method: Lean reads the IRS Tax Table ($50 bands, tax at the midpoint) below $100,000 of "
                             "taxable income; both engines apply the rate schedule to the exact amount")
        out["items"] = items
        out["notes"] = notes
        cases.append(out)
    doc = {"engines": [pe_doc["engine"], tc_doc["engine"]], "tolerance": TOL,
           "method": __doc__.strip().split("\n\n", 1)[1], "totals": tot, "cases": cases}
    return doc


if __name__ == "__main__":
    doc = main()
    ann_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle_annotations.json")
    if os.path.exists(ann_path):  # hand-written classification of each difference, keyed "case key|item"
        ann = json.load(open(ann_path, encoding="utf-8"))
        for c in doc["cases"]:
            for x in c.get("items", []):
                k = f"{c['key']}|{x['item']}"
                if k in ann:
                    x["note"] = ann[k]
            if c["key"] in ann:
                c["caseNote"] = ann[c["key"]]
        doc["summary"] = ann.get("_summary")
    json.dump(doc, open(os.path.join(V, "oracle_results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(doc["totals"], indent=1))
    for c in doc["cases"]:
        if c["status"] != "included":
            continue
        for x in c["items"]:
            flag = "" if x["allThreeAgree"] and x.get("leanAgreesCourt", True) else "  <--"
            print(f"{c['key']:20} {x['item']:28} court={x['court']} lean={x['lean']} pe={x['policyengine']} "
                  f"tc={x['taxcalc']}{flag}")
        for n in c["notes"]:
            print("   ", n)
