import IeGlobal.Pit
import TaxKernel.Global2

/-!
# Ireland 2025: value-added tax (5111); excise not read

Source: Value-Added Tax Consolidation Act 2010, Revised Act (Law Reform Commission, revisedacts.lawreform.ie,
"Updated to 1 August 2026"; `ie/law/vatca2010.html`, sha256 in `law/SHA256SUMS`). The revision is later than 2025;
the provisions used carry their own periods or were unchanged in 2025 (grade B: the dated 2025 revision not read).
* **s. 46 (1) (c)**: "13.5 per cent of the amount on which tax is chargeable in relation to goods or services of a kind
  specified in Schedule 3" (fuel, construction, hotel and restaurant services from 1 September 2023 ...); **(ca)** 9 %
  for Schedule 3 paragraphs 7(a), 7A, 12, 12A (newspapers, sporting facilities ...); **(caa)** "during the period from
  1 May 2022 to 31 December 2030, 9 per cent in relation to goods of a kind specified in paragraph 17(2) and (3) of
  Schedule 3" (electricity, gas); s. 46 (1) (a) standard 23 %; (b) zero rate, Schedule 2 (food, books, oral
  medicines, children's clothing). Exempt, Schedule 1 (financial, insurance, medical, education, passenger transport,
  letting of residential property).
* **s. 2 (1)**: "goods threshold" means "€85,000"; "services threshold" "€42,500".


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), IE excise records for the situation on 1 July 2025 (tobacco 4094, alcohol 4091, energy 4093; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `ie/law/tedb_*.json`).
* TEDB IE manufactured tobacco (1.7.2025): 463.62 EUR per 1 000 cigarettes + 8.97 % of the retail selling price, at least 515.2 EUR per 1 000
* TEDB IE beer (1.7.2025): 22.55 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB IE still wine (1.7.2025): 424.84 EUR per hl of product
* TEDB IE ethyl alcohol (1.7.2025): 4257 EUR per hl of pure alcohol
* TEDB IE energy products (1.7.2025): unleaded petrol 688.78 EUR per 1 000 l
* TEDB IE energy products (1.7.2025): gas oil used as propellant 595.68 EUR per 1 000 l


## 5121 Mineral oil tax with carbon charge, heating oil (rate from 1 May 2025) (gap pass 2) (gap pass, grade B)
Source: EC TEDB tax 4093 (Mineral oil tax), situations 1.1 and 1.7.2025 (`tools/in_gap/tedb/tax_IE_4093_*.json`).
* Finance Act 1999 Part 2 Ch. 1, Sch. 2A; TEDB IE 4093 at 1.1.2025: 199,17 EUR / 1 000 l
* Finance Act 1999 Sch. 2A; TEDB IE 4093 at 1.7.2025: 219,50 EUR / 1 000 l (the record: from 1 May 2025 the carbon charge of 63,50 EUR per tonne of CO2 applies to the other mineral oils)
-/

namespace IeGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value-added tax", standard := 2300, reduced := 1350, reduced2 := 900, threshold := 42500,
    classOf := fun gd => match gd with
      | .food | .books | .medicines => .zero
      | .newspapers | .electricity | .gas => .reduced2
      | .hotels | .restaurants | .heatingOil => .reduced
      | .health | .education | .financial | .insurance | .rent | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "VATCA 2010 s. 46 (1) (a) 23 %, (b) zero (Sch. 2), (c) 13.5 % (Sch. 3), (ca), (caa) 9 %; Sch. 1 (exempt); s. 2 (1) services threshold €42,500"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 23181, perUnitDen := 50000, adValoremBp := 897, minNum := 322, minDen := 625, statute := "TEDB IE manufactured tobacco (1.7.2025): 463.62 EUR per 1 000 cigarettes + 8.97 % of the retail selling price, at least 515.2 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 451, perUnitDen := 20, onPureAlcohol := true, statute := "TEDB IE beer (1.7.2025): 22.55 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 10621, perUnitDen := 2500, statute := "TEDB IE still wine (1.7.2025): 424.84 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 4257, perUnitDen := 100, onPureAlcohol := true, statute := "TEDB IE ethyl alcohol (1.7.2025): 4257 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 34439, perUnitDen := 50000, statute := "TEDB IE energy products (1.7.2025): unleaded petrol 688.78 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 3723, perUnitDen := 6250, statute := "TEDB IE energy products (1.7.2025): gas oil used as propellant 595.68 EUR per 1 000 l" }] }

/-- Mineral oil tax with carbon charge, heating oil (rate from 1 May 2025) (gap pass 2; kernel 2.1 `ExciseRule` date windows). -/
def gxDated0 : ExciseRule :=
  { good := .heatingOil,   name := "Mineral oil tax (gas oil for heating, incl. carbon charge)",   perUnitNum := 19917,   perUnitDen := 100000,   validTo := "2025-05-01",   statute := "Finance Act 1999 Part 2 Ch. 1, Sch. 2A; TEDB IE 4093 at 1.1.2025: 199,17 EUR / 1 000 l" }
def gxDated1 : ExciseRule :=
  { good := .heatingOil,   name := "Mineral oil tax (gas oil for heating, incl. carbon charge)",   perUnitNum := 21950,   perUnitDen := 100000,   validFrom := "2025-05-01",   statute := "Finance Act 1999 Sch. 2A; TEDB IE 4093 at 1.7.2025: 219,50 EUR / 1 000 l (the record: from 1 May 2025 the carbon charge of 63,50 EUR per tonne of CO2 applies to the other mineral oils)" }

def gxDatedRules : List ExciseRule := [gxDated0, gxDated1]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 VAT", covers := [.vat, .excise, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges gxDatedRules g }]

def absent : List Absent :=
  []

def notes : List String := ["IE 5111: VATCA 2010 revised (LRC, updated to 1 August 2026)", "IE 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)", "IE 5121 gap pass 2: Mineral oil tax with carbon charge, heating oil (rate from 1 May 2025) (B, change on 1.5.2025 (carbon charge on non-auto fuels))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["registration threshold taken as the services threshold €42,500 (goods: €85,000)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants) then ["restaurant and catering at 13.5 % all 2025: the 9 % of s. 46 (1) (cb) ended 31.8.2023 and returns only from 1.7.2026 (Finance Act 2025 s. 71)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Finance Act 1999 Part 2 mineral oil tax, tobacco products tax, alcohol products tax) not read"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 IE: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 123 } == 23
#guard vat.embedded { good := .hotels, amount := 1135 } == 135
#guard vat.embedded { good := .electricity, amount := 109 } == 9
#guard vat.embedded { good := .food, amount := 100 } == 0
#guard vat.net { turnover := 42500, sales := [{ good := .other, net := 42500 }] } == 0
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 911
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 112
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 424
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 1702
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 688
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 595
#guard gxDated0.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 199
#guard gxDated1.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 219
#guard gxDated0.windowDays 2025 + gxDated1.windowDays 2025 == 365

end IeGlobal.Consumption
