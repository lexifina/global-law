# Country mappings onto the OECD Taxing Wages lines, read by oecd_check.py (exec'd there).
# UK: incomeTax is the ITA 2007 s23 liability (HICBC sits in benefits, CGT in surtaxes); no local tax.
def map_uk(row):
    ps = (row.get("detail") or {}).get("persons", [])
    return {"CGTC": sum(p.get("step3Income", 0) for p in ps) if ps else None,
            "CGITLETC": (row.get("detail") or {}).get("liabilityITA2007s23"),
            "CGITFP": row["incomeTax"] + row.get("surtax_capitalGainsTax", 0),
            "SLT": row["localIncomeTax"], "EECSSC": row["employeeSocial"], "CTGG": row["benefits"]}
# Germany: the OECD books Kindergeld as a child tax credit inside CGITFP (CTGG = 0) and the Soli inside income tax;
# the DE model reports the Kindergeld the family keeps as benefits (none when the Freibetraege win, and then no
# add-back in incomeTax), so CGITFP = incomeTax + Soli + church tax - benefits, CTGG = 0.
def map_de(row):
    us = (row.get("detail") or {}).get("units", [])
    return {"CGTC": sum(u.get("zvE", 0) for u in us) if us else None,
            # the OECD's tax before credits includes the Soli too (S167: its CGITLETC equals its CGITFP)
            "CGITLETC": (sum(u.get("tariffTax_32a", 0) for u in us) + row.get("surtax_Soli", 0)
                         + row.get("surtax_Kirchensteuer", 0)) if us else None,
            "CGITFP": row["incomeTax"] + row.get("surtax_Soli", 0) + row.get("surtax_Kirchensteuer", 0) - row["benefits"],
            "SLT": row["localIncomeTax"], "EECSSC": row["employeeSocial"], "CTGG": 0}
MAP["UK"] = map_uk
MAP["DE"] = map_de
# Japan: the OECD's CGITFP is 所得税 + 復興特別所得税 (cut to 100 yen); SLT is the 住民税; CTGG the 児童手当 (+ for the
# single parent the 児童扶養手当, a means-tested allowance outside the contract's scope).
def map_jp(row):
    ps = (row.get("detail") or {}).get("persons", [])
    return {"CGTC": sum(p.get("taxableIncome_kazeiSoShotoku", 0) for p in ps) if ps else None,
            "CGITLETC": sum(p.get("taxBeforeCredits_sanshutsuZei", 0) for p in ps) if ps else None,
            "CGITFP": sum(p.get("nationalPayableRounded100", 0) for p in ps) if ps else row["incomeTax"] + row["surtaxes"],
            "SLT": row["localIncomeTax"], "EECSSC": row["employeeSocial"], "CTGG": row["benefits"]}
MAP["JP"] = map_jp
