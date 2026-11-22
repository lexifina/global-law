S = dict(cc="UK", fam="Consumption", family_name="5111 VAT, 5121 tobacco and alcohol duty",
doc=r'''# United Kingdom 2025: VAT (5111), tobacco products duty and alcohol duty (5121)

Sources: legislation.gov.uk point-in-time versions at 2025-07-01 (`uk/law/*_2025-07-01.html`, sha256 in
`law/SHA256SUMS`): VATA 1994 s. 2, Sch. 1, 7A, 8, 9; Tobacco Products Duty Act 1979 Sch. 1; Finance (No. 2) Act 2023
s. 48 and Sch. 7 (as substituted from 1.2.2025 by Finance Act 2025 s. 63); Hydrocarbon Oil Duties Act 1979 s. 6.
* **VATA s. 2 (1)**: "VAT shall be charged at the rate of 20 per cent"; **Sch. 7A** reduced rate (5 %), Group 1
  "Supplies of domestic fuel or power"; **Sch. 8** zero rate: Group 1 Food, Group 2 Sewerage services and water, Group
  3 Books, Group 8 Transport, Group 12 Drugs, medicines; **Sch. 9** exempt: Group 1 Land, Group 2 Insurance, Group 5
  Finance, Group 6 Education, Group 7 Health and welfare. **Sch. 1 para 1 (1) (a)**: registration when taxable supplies
  in the last year "exceeded £90,000".
* **TPDA 1979 Sch. 1** cigarettes: "An amount equal to the higher of— (a) 16.5% of the retail price plus £334.58 per
  thousand cigarettes, or (b) £446.67 per thousand cigarettes".
* **F(No.2)A 2023 Sch. 7** (from 1.2.2025), per litre of alcohol: less than 3.5 % £9.61; 3.5 %-8.5 %: beer £21.78,
  spirits, wine and other fermented products £25.67; 8.5 %-22 % £29.54; exceeding 22 % £32.79.
* **HODA 1979 s. 6 (1A)**: the text in the record reads £0.5795 a litre for unleaded petrol and heavy oil; the
  temporary 5p reduction applied since March 2022 was not found in the dated record, so fuel duty is not modelled.
''',
vat=dict(name="Value added tax", standard=2000, reduced=500, threshold=90000,
  statute="VATA 1994 s. 2 (1) 20 %; Sch. 7A Group 1 (5 %); Sch. 8 Groups 1, 2, 3, 8, 12 (zero); Sch. 9 Groups 1, 2, 5, 6, 7 (exempt); Sch. 1 para 1 (£90,000)",
  classes={"electricity": "reduced", "gas": "reduced", "food": "zero", "water": "zero", "books": "zero",
           "newspapers": "zero", "transport": "zero", "medicines": "zero",
           "rent": "exempt", "insurance": "exempt", "financial": "exempt", "education": "exempt", "health": "exempt"}),
excise=[dict(good="cigarettes", name="Tobacco products duty (cigarettes)", num=33458, den=100000, adv=1650, minNum=44667, minDen=100000,
             statute="TPDA 1979 Sch. 1: higher of 16.5 % of retail price + £334.58 / 1 000 and £446.67 / 1 000")],
lean=r'''
/-- F(No.2)A 2023 Sch. 7 (from 1.2.2025): pence per litre of alcohol by strength (and, at 3.5-8.5 %, by product). -/
def alcoholPence (g : Good) (abvBp : Int) : Int :=
  if abvBp < 350 then 961
  else if abvBp < 850 then (if g == .beer then 2178 else 2567)
  else if abvBp ≤ 2200 then 2954 else 3279

def alcoholDuty (s : Spend) : Int := divR .down (divR .down (s.quantity * s.abvBp) BP * alcoholPence s.good s.abvBp) (100 * 1000)

def alcoholCharges (xs : List Spend) : List Charge :=
  (xs.filter fun s => s.good == .beer || s.good == .wine || s.good == .spirits).map fun s =>
    charge .excise "Alcohol duty" s.quantity id (fun _ => alcoholDuty s) (event := s.good.name) (bearer := .consumer)
      (statute := "F(No.2)A 2023 s. 48, Sch. 7 (rates from 1.2.2025)")
''',
extra_run=["alcoholCharges g.consumption"],
notes=["UK 5111/5121: legislation.gov.uk point-in-time 2025-07-01"],
unsupported=[("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel)", "fuel duty not modelled: HODA s. 6 (1A) reads £0.5795/l but the temporary 5p reduction in force in 2025 was not located in the dated record"),
  ("g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits)", "alcohol duty at the rates from 1 February 2025 (Jan 2025: earlier Sch. 7); draught relief (s. 50) and small producer relief not modelled"),
  ("g.consumption.any (fun s => s.good == .food || s.good == .restaurants)", "food zero-rated as Sch. 8 Group 1 (catering, confectionery, soft drinks and other excepted items are standard-rated: give them as restaurants/other)")],
guards=["vat.embedded { good := .clothing, amount := 120 } == 20",
        "vat.embedded { good := .electricity, amount := 105 } == 5",
        "vat.embedded { good := .food, amount := 100 } == 0",
        "vat.net { turnover := 90000, sales := [{ good := .other, net := 90000 }] } == 0",
        "vat.net { turnover := 90001, sales := [{ good := .other, net := 90001 }] } == 18000",
        "-- 1 000 cigarettes at £600: 99 + 334 < 446 (the minimum binds); at £1 000: 165 + 334",
        "excise.duty { good := .cigarettes, amount := 600, quantity := 1000000 } == 446",
        "excise.duty { good := .cigarettes, amount := 1000, quantity := 1000000 } == 499",
        "alcoholDuty { good := .beer, amount := 400, quantity := 100000, abvBp := 500 } == 108",
        "alcoholDuty { good := .wine, amount := 900, quantity := 100000, abvBp := 1200 } == 354",
        "alcoholDuty { good := .spirits, amount := 2500, quantity := 100000, abvBp := 4000 } == 1311"],
taxes=[{"oecd": "5111", "tax": "Value added tax", "statute": "VATA 1994 s. 2, Sch. 1 para 1, Sch. 7A, 8, 9", "dated": "legislation.gov.uk point in time 2025-07-01", "grade": "A", "kernel_parts": ["Vat"], "unsupported": ["Sch. 8 Group 1 excepted items", "children's clothing (Group 16) not separable in the basket"]},
 {"oecd": "5121", "tax": "Tobacco products duty (cigarettes)", "statute": "TPDA 1979 Sch. 1", "dated": "point in time 2025-07-01", "grade": "A", "kernel_parts": ["ExciseRate (minimum)"], "unsupported": ["cigars, hand-rolling and other tobacco"]},
 {"oecd": "5121", "tax": "Alcohol duty", "statute": "F(No.2)A 2023 s. 48, Sch. 7 (FA 2025 s. 63)", "dated": "point in time 2025-07-01", "grade": "A", "kernel_parts": ["custom (rate by strength band)"], "unsupported": ["draught relief", "small producer relief", "January 2025 rates"]},
 {"oecd": "5121", "tax": "Hydrocarbon oil duty", "statute": "HODA 1979 s. 6 (1A)", "dated": "point in time 2025-07-01", "grade": "B", "status": "unsupported", "kernel_parts": [], "unsupported": ["the 2025 rate (temporary reduction to £0.5295) not located in the record: would unlock with the provision enacting the 2022-2026 reduction"]}])

# ---- pass 2 (R1 Europe, 2026-11-21): the 5p fuel-duty cut searched on legislation.gov.uk ----
for _t in S["taxes"]:
    if _t["tax"] == "Hydrocarbon oil duty":
        _t.update({"grade": "C", "status": "unsupported",
          "tried": "legislation.gov.uk: HODA 1979 s. 6 (1A) point in time 2025-07-01 reads £0.5795 (unleaded petrol, heavy oil; FA 2013 s. 179); the changes register of HODA 1979 lists no amendment of s. 6 after 2021; the contents of FA 2022 (c. 3), FA 2023 (c. 1), F(No.2)A 2023 (c. 30), FA 2024 (c. 3), F(No.2)A 2024 (c. 12) and FA 2025 (c. 8) hold no fuel-duty rate provision (only rebated-diesel, heating-oil rebate and EPL sections)",
          "unsupported": ["would unlock: the instrument giving the 52.95p rate statutory effect in 2025 (a Provisional Collection of Taxes Act 1968 resolution is not on legislation.gov.uk); modelling £0.5795 would overstate the 2025 duty"]})
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("fuel duty")] + [
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel)", "fuel duty not modelled (grade C): HODA s. 6 (1A) reads £0.5795/l at 2025-07-01 and no enacted provision for the 52.95p rate was found on legislation.gov.uk")]
