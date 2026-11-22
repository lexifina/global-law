import LtGlobal.Pit

/-!
# LT 2025: Pridėtinės vertės mokestis (5111); excises not modelled in this pass

Source: Pridėtinės vertės mokesčio įstatymas, e-seimas consolidated edition "nuo 2023-05-01 iki 2025-04-30" as captured by the Internet Archive on 2025-01-21 (`lt/law/pvm_ed20230501_wb20250121.html`); the 2025-05-01 and later 2025 editions are not archived; sha256 in `law/SHA256SUMS`.
* 2 str. 32 d.: "Standartinis PVM tarifas – 21 procento PVM tarifas."
* 19 str. 3 d.: "Lengvatinis 9 procentų PVM tarifas taikomas: 1) šilumos energijai, tiekiamai gyvenamosioms patalpoms šildyti ...; 2) spausdintoms ir elektroninėms knygoms ...; 3) ... apgyvendinimo paslaugoms; 4) keleivių vežimo ... reguliariais reisais" (items 6, 8, 9 ended in 2023)
* 19 str. 4 d.: "Lengvatinis 5 procentų PVM tarifas taikomas: 1) vaistams, medicinos pagalbos priemonėms ...; 3) spausdintiems ir (arba) elektroniniams laikraščiams, žurnalams ..."
* 71 str. 2 d.: registration when supplies over the last 12 months exceed the limit: "neviršijo 45 000 eurų"


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), LT excise records for the situation on 1 July 2025 (tobacco 4130, alcohol 4101, energy 4129; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `lt/law/tedb_*.json`).
* TEDB LT manufactured tobacco (1.7.2025): 92.6 EUR per 1 000 cigarettes + 25.0 % of the retail selling price, at least 149.7 EUR per 1 000
* TEDB LT beer (1.7.2025): 10.97 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB LT still wine (1.7.2025): 254 EUR per hl of product
* TEDB LT ethyl alcohol (1.7.2025): 2778 EUR per hl of pure alcohol
* TEDB LT energy products (1.7.2025): unleaded petrol 513 EUR per 1 000 l
* TEDB LT energy products (1.7.2025): gas oil used as propellant 519.6 EUR per 1 000 l
* TEDB LT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 113.6 EUR per 1 000 l
-/

namespace LtGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Pridėtinės vertės mokestis", standard := 2100, reduced := 900, superReduced := 500, threshold := 45000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .books | .hotels | .transport => .reduced
      | .medicines | .newspapers => .superReduced
      | _ => .standard }

def vatStatute : String := "PVM įstatymas (IX-751) 2 str. 32 d. (21 %), 19 str. 1, 3, 4 d. (9 %, 5 %), 71 str. 2 d. (45 000 eurų)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 463, perUnitDen := 5000, adValoremBp := 2500, minNum := 1497, minDen := 10000, statute := "TEDB LT manufactured tobacco (1.7.2025): 92.6 EUR per 1 000 cigarettes + 25.0 % of the retail selling price, at least 149.7 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 1097, perUnitDen := 100, onPureAlcohol := true, statute := "TEDB LT beer (1.7.2025): 10.97 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 127, perUnitDen := 50, statute := "TEDB LT still wine (1.7.2025): 254 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 1389, perUnitDen := 50, onPureAlcohol := true, statute := "TEDB LT ethyl alcohol (1.7.2025): 2778 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 513, perUnitDen := 1000, statute := "TEDB LT energy products (1.7.2025): unleaded petrol 513 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 1299, perUnitDen := 2500, statute := "TEDB LT energy products (1.7.2025): gas oil used as propellant 519.6 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 71, perUnitDen := 625, statute := "TEDB LT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 113.6 EUR per 1 000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Pridėtinės vertės mokestis", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["LT 5111: consolidated edition 2023-05-01 to 2025-04-30 (later 2025 editions not reached)", "LT 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if !g.consumption.isEmpty then ["the edition read ends on 2025-04-30: changes from 2025-05-01 not checked"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["5 % only for reimbursed and prescription medicines; others 21 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Akcizų įstatymas (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 LT: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12100 } == 2100
#guard vat.embedded { good := .books, amount := 10900 } == 900
#guard vat.embedded { good := .medicines, amount := 10500 } == 500
#guard vat.net { turnover := 45000, sales := [{ good := .other, net := 45000 }] } == 0
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1342
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 54
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 254
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 1111
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 513
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 519
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 113

end LtGlobal.Consumption
