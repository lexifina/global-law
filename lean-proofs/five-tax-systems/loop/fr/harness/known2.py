"""Step 3: recreate the catalogue items not covered by ~/fr/LOOPHOLES.md (income 2025 unless stated).
Each scenario: the household with the optimisation ("with") and without it ("base"); saving = base - with, on the
burden (income tax + CEHR + CDHR + levies on the return) or, where the levies are equal both ways and the emulation
does not carry them, on income tax + CEHR + CDHR (metric "tax3"). Output: ../runs/known2.json, table on stdout.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as L

S = {"0AC": 1, "0DA": 1980}
C = {"0AM": 1, "0DA": 1980, "0DB": 1982}
CD = dict(S, **{"1AJ": 30000, "2DC": 300000, "2BH": 300000})          # single CDHR payer (LOOPHOLES finding 2)
BAND = dict(S, **{"1AJ": 30000, "2DC": 290000, "2BH": 290000})         # inside the 82.5 % smoothing band
BIG = dict(S, **{"1AJ": 30000, "2DC": 600000, "2BH": 600000})          # CDHR above the band
CD2 = dict(S, **{"1AJ": 150000, "2DC": 800000, "2BH": 800000})       # CDHR payer with 45 k of scale tax


def B(*ds, **kw):
    o = {}
    for d in ds:
        o.update(d)
    o.update(kw)
    return o


SC = []


def sc(item, label, base, withb, xbase=None, xwith=None, metric="burden", note=""):
    SC.append(dict(item=item, label=label, base=base, withb=withb, xbase=xbase, xwith=xwith, metric=metric,
                   note=note))


# K17 overtime exemption (81 quater)
sc("K17", "overtime 7 500 exempt vs taxable, salary 40 000", B(S, **{"1AJ": 47500}), B(S, **{"1AJ": 40000, "1GH": 7500}))
sc("K17", "same, CDHR payer", B(CD, **{"1AJ": 37500}), B(CD, **{"1GH": 7500}))
# K18 PPV
sc("K18", "PPV 6 000 exempt (profit-sharing scheme) vs taxable", B(S, **{"1AJ": 46000}), B(S, **{"1AJ": 40000, "1AD": 6000, "1AV": 1}))
sc("K18", "PPV 6 000 without scheme (3 000 exempt)", B(S, **{"1AJ": 46000}), B(S, **{"1AJ": 40000, "1AD": 6000}))
# K19 PER
sc("K19", "PER 8 000, salary 80 000", B(S, **{"1AJ": 80000, "APS": 8000}), B(S, **{"1AJ": 80000, "APS": 8000, "6NS": 8000}))
sc("K19", "PER pooling 6QR: couple 150k/20k, 20 000 paid by decl. 1, ceilings 15k/5k",
   B(C, **{"1AJ": 150000, "1BJ": 20000, "6NS": 20000, "APS": 15000, "APT": 5000}),
   B(C, **{"1AJ": 150000, "1BJ": 20000, "6NS": 20000, "APS": 15000, "APT": 5000, "6QR": 1}))
sc("K19", "PER 10 000 in the CDHR band", B(BAND, APS=10000), B(BAND, APS=10000, **{"6NS": 10000}))
# K20 deficit foncier
sc("K20", "deficit foncier 10 700 on global income, salary 80 000", B(S, **{"1AJ": 80000}), B(S, **{"1AJ": 80000, "4BC": 10700}))
sc("K20", "deficit 21 400 (energy renovation 2023-2025)", B(S, **{"1AJ": 80000}), B(S, **{"1AJ": 80000, "4BC": 21400}))
sc("K20", "deficit 10 700, CDHR payer above the band", BIG, B(BIG, **{"4BC": 10700}))
sc("K20", "deficit 10 700, CDHR smoothing band", BAND, B(BAND, **{"4BC": 10700}))
# K21 monuments historiques (uncapped deficit)
sc("K21", "MH deficit 100 000, salary 400 000", B(S, **{"1AJ": 400000}), B(S, **{"1AJ": 400000, "4BC": 100000}))
# K22 micro-foncier vs real (30 %)
for e in (20, 30, 40, 60):
    sc("K22", f"rents 14 000, expenses {e} %: real vs micro", B(S, **{"1AJ": 50000, "4BE": 14000}),
       B(S, **{"1AJ": 50000, "4BA": 14000 * (100 - e) // 100}))
# K23 micro BNC (34 %) vs real
for e in (20, 34, 50):
    sc("K23", f"BNC receipts 60 000, expenses {e} %: real vs micro", B(S, **{"5HQ": 60000}), B(S, **{"5QC": 60000 * (100 - e) // 100}))
# K24 LMNP furnished letting, micro 50 % vs real with depreciation (profit 0)
sc("K24", "furnished rents 15 000: real with depreciation (0) vs micro 50 %", B(S, **{"1AJ": 50000, "5KP": 15000}), B(S, **{"1AJ": 50000}), metric="tax3",
   note="5KP stands for the 2025 non-professional furnished boxes (same 50 % rate); levies not compared")
# K25 life insurance allowance
sc("K25", "8-year life insurance: 4 600 of proceeds vs 4 600 of interest (PFU)", B(S, **{"1AJ": 50000, "2TR": 4600}), B(S, **{"1AJ": 50000, "2CH": 4600}), metric="tax3")
sc("K25", "post-2017 proceeds 20 000 (2VV, 7.5 %) vs interest", B(S, **{"1AJ": 50000, "2TR": 20000}), B(S, **{"1AJ": 50000, "2VV": 20000}), metric="tax3")
# K26 PEA
sc("K26", "PEA dividends 5 000 (exempt) vs securities account (PFU)", B(S, **{"1AJ": 50000, "2DC": 5000}), B(S, **{"1AJ": 50000}), metric="tax3")
# K27 year of death: two returns (6, 8; 196 ter)
SC.append(dict(item="K27", label="death on 30 June, salaries 60k/20k: two returns with 2 parts vs one",
               base=B(C, **{"1AJ": 60000, "1BJ": 20000}), withb=None, xbase=None, xwith=None,
               parts=[B(C, **{"1AJ": 30000, "1BJ": 10000}), B(C, **{"1AJ": 30000})], metric="burden", note="survivor return run as a couple (2 parts, couple decote)"))
SC.append(dict(item="K27", label="same, survivor return with 1 part (lower bound)",
               base=B(C, **{"1AJ": 60000, "1BJ": 20000}), withb=None, xbase=None, xwith=None,
               parts=[B(C, **{"1AJ": 30000, "1BJ": 10000}), B(S, **{"1AJ": 30000})], metric="burden", note=""))
# K28 married child attached (0DN, 196 B) vs alimony
sc("K28", "married child + spouse attached (2 x 6 855), no income of their own", B(C, **{"1AJ": 120000}), B(C, **{"1AJ": 120000, "0DN": 2}))
# K29 hosting a person over 75 (156, II, 2 ter): 4 075
sc("K29", "hosting a person over 75 of low means: 4 075 deduction", B(S, **{"1AJ": 60000}), B(S, **{"1AJ": 60000, "6DD": 4075}))
# K30 prestation compensatoire: capital within 12 months (25 %) vs over more than 12 months (deductible)
sc("K30", "PC 30 500 in capital (25 %) vs nothing, payer 120 000", B(S, **{"1AJ": 120000}), B(S, **{"1AJ": 120000}), xwith={"PC": 30500})
sc("K30", "PC 30 500 spread > 12 months (deductible as alimony) vs nothing", B(S, **{"1AJ": 120000}), B(S, **{"1AJ": 120000, "6GU": 30500}))
sc("K30", "recipient taxed on 30 500 when spread (pension 1AO), salary 25 000", B(S, **{"1AJ": 25000, "1AO": 30500}), B(S, **{"1AJ": 25000}))
# K31 quotient for exceptional income (ordinary taxation emulated by 5QC: a net amount with no allowance)
sc("K31", "exceptional 40 000 net, salary 40 000: quotient vs ordinary", B(S, **{"1AJ": 40000, "5QC": 40000}), B(S, **{"1AJ": 40000}), xwith={"EXC": 40000})
sc("K31", "exceptional 40 000 net, salary 20 000", B(S, **{"1AJ": 20000, "5QC": 40000}), B(S, **{"1AJ": 20000}), xwith={"EXC": 40000})
sc("K31", "exceptional 200 000, couple 2 children 60 000", B(C, **{"0CF": 2, "1AJ": 60000, "5QC": 200000}), B(C, **{"0CF": 2, "1AJ": 60000}), xwith={"EXC": 200000})
sc("K31", "exceptional 300 000, single, dividends 150 000 (CDHR quarter rule)", B(S, **{"5QC": 300000, "2DC": 150000, "2BH": 150000}), B(S, **{"2DC": 150000, "2BH": 150000}), xwith={"EXC": 300000})
# K32 Pinel + cap with home help
sc("K32", "Pinel 5 000 a year, salary 80 000", B(S, **{"1AJ": 80000}), B(S, **{"1AJ": 80000}), xwith={"PIN": 5000})
sc("K32", "Pinel 5 000 + home help 12 000 (credit 6 000): cap 10 000", B(S, **{"1AJ": 80000, "7DB": 12000}), B(S, **{"1AJ": 80000, "7DB": 12000}), xwith={"PIN": 5000})
sc("K32", "Pinel 5 000 for a CDHR payer (listed: keeps its value)", CD2, CD2, xwith={"PIN": 5000})
sc("K32", "home help 12 000 for the same CDHR payer (not listed: worth 0)", CD2, B(CD2, **{"7DB": 12000}))
# K33 Girardin
sc("K33", "Girardin reduction 50 000 asked, salary 300 000 (cap 18 000 / 44 %)", B(S, **{"1AJ": 300000}), B(S, **{"1AJ": 300000}), xwith={"GIR": 50000})
sc("K33", "Girardin 20 000 for a CDHR payer vs gifts giving 20 000", B(CD2, **{"7UF": 30304}), CD2, xwith={"GIR": 20000})
# K34 IR-PME
sc("K34", "IR-PME 50 000 subscribed (18 %), salary 100 000", B(S, **{"1AJ": 100000}), B(S, **{"1AJ": 100000}), xwith={"PME": 50000})
# K35 Malraux outside the cap
sc("K35", "Malraux 100 000 of works (30 %) + Pinel 10 000, salary 300 000", B(S, **{"1AJ": 300000}), B(S, **{"1AJ": 300000}), xwith={"MAL": 100000, "PIN": 10000})
# K37 pre-2018 securities, 65 % holding allowance, scale option (emulated: gain net of allowance + allowance in RFR via 2EE)
sc("K37", "gain 50 000 on pre-2018 shares held 8+ years: 2OP with 65 % allowance vs PFU, couple 60 000", B(C, **{"1AJ": 60000, "3VG": 50000}),
   B(C, **{"1AJ": 60000, "3VG": 17500, "2EE": 32500, "2OP": 1}), metric="tax3", note="levies on the full gain both ways")
sc("K37", "same, couple 200 000", B(C, **{"1AJ": 200000, "3VG": 50000}),
   B(C, **{"1AJ": 200000, "3VG": 17500, "2EE": 32500, "2OP": 1}), metric="tax3")
# K38 retiring director 500 000 allowance (150-0 D ter)
sc("K38", "director retiring: gain 700 000, 500 000 allowance (PFU)", B(S, **{"1AS": 30000, "3VG": 700000}),
   B(S, **{"1AS": 30000, "3VG": 200000, "2EE": 500000}), metric="tax3", note="allowance kept in the RFR (CEHR/CDHR on it)")
# K39 student summer job exemption (81, 36): 3 x monthly SMIC
sc("K39", "attached student earning 5 400: exempt vs declared", B(C, **{"0DJ": 1, "1AJ": 90000, "1CJ": 5400}), B(C, **{"0DJ": 1, "1AJ": 90000}))

cases = []
for i, s in enumerate(SC):
    if s.get("parts"):
        cases.append((f"{i}b", 2025, s["base"], None))
        for j, p in enumerate(s["parts"]):
            cases.append((f"{i}p{j}", 2025, p, None))
    else:
        cases.append((f"{i}b", 2025, s["base"], s["xbase"]))
        cases.append((f"{i}w", 2025, s["withb"], s["xwith"]))
R = L.run(cases)
# sanity: frloop without extras = frtax
plain = [c for c in cases if not c[3]]
ft = subprocess.run([os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")],
                    input="\n".join(L.line(*c[:3]) for c in plain) + "\n", capture_output=True, text=True).stdout
mism = 0
for ln in ft.splitlines():
    p = ln.split(";")
    d = dict(kv.split("=", 1) for kv in p[1:] if "=" in kv)
    if int(float(d["IMPNET"])) != R[p[0]]["IMPNET"] or int(float(d["CDHR"])) != R[p[0]]["CDHR"]:
        mism += 1
out = []
for i, s in enumerate(SC):
    m = L.burden if s["metric"] == "burden" else (lambda b, o: L.tax3(o))
    b0 = m(s["base"], R[f"{i}b"])
    if s.get("parts"):
        parts = [R[f"{i}p{j}"] for j in range(len(s["parts"]))]
        w = sum(m(p, o) for p, o in zip(s["parts"], parts))
        detail = {"base": R[f"{i}b"], "parts": parts}
    else:
        w = m(s["withb"], R[f"{i}w"])
        detail = {"base": R[f"{i}b"], "with": R[f"{i}w"]}
        if s["item"] == "K38":
            # art. 224, II, 1 deg: the CDHR base leaves out the 150-0 D ter allowance (an a bis allowance other than
            # 1 ter / 1 quater); the CEHR keeps it (RFR). Rerun without 2EE for the CDHR; CEHR from the 2EE run.
            o2 = L.one({k: v for k, v in s["withb"].items() if k != "2EE"})
            w = R[f"{i}w"]["IMPNET"] + R[f"{i}w"]["CHRAPRES"] + o2["CDHR"]
            detail["cdhr_without_allowance_in_base"] = o2["CDHR"]
    out.append(dict(item=s["item"], label=s["label"], base=b0, withv=w, saving=b0 - w, metric=s["metric"], note=s["note"],
                    detail=detail, boxes={"base": s["base"], "with": s.get("withb") or s.get("parts"), "xwith": s["xwith"]}))
    print(f'{s["item"]:4} {b0:>9} {w:>9} {b0 - w:>8}  {s["label"]}')
print("frloop vs frtax mismatches (no extras):", mism, "of", len(plain))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "known2.json"), "w"), indent=1)
