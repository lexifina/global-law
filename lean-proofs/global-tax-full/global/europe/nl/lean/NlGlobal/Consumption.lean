import NlGlobal.Pit

/-!
# NL 2025: Omzetbelasting (5111); excises not modelled in this pass

Source: Wet op de omzetbelasting 1968 (BWBR0002629), wetten.overheid.nl (official), version "Geldend van 01-01-2025 t/m 31-12-2025" (`nl/law/wetob_g2025.html`); sha256 in `law/SHA256SUMS`.
* art. 9: "1 De belasting bedraagt 21 percent. 2 In afwijking van het eerste lid bedraagt de belasting: a. 9 percent voor leveringen van goederen en diensten, genoemd in de bij deze wet behorende tabel I"


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), NL excise records for the situation on 1 July 2025 (tobacco 4137, alcohol 4135, energy 4136; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `nl/law/tedb_*.json`).
* TEDB NL manufactured tobacco (1.7.2025): 362.12 EUR per 1 000 cigarettes + 5.0 % of the retail selling price, at least 390.42 EUR per 1 000
* TEDB NL beer (1.7.2025): 8.12 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB NL still wine (1.7.2025): 95.69 EUR per hl of product
* TEDB NL ethyl alcohol (1.7.2025): 1827 EUR per hl of pure alcohol
* TEDB NL energy products (1.7.2025): unleaded petrol 789.1 EUR per 1 000 l
* TEDB NL energy products (1.7.2025): gas oil used as propellant 516.25 EUR per 1 000 l
* TEDB NL energy products (1.7.2025): gas oil used as heating fuel (non-business use) 516.25 EUR per 1 000 l
-/

namespace NlGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Omzetbelasting", standard := 2100, reduced := 900, threshold := 0,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .medicines | .books | .newspapers | .hotels | .transport | .restaurants => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Wet op de omzetbelasting 1968 art. 9 lid 1 (21 %), lid 2 onderdeel a (9 %, tabel I); art. 11 (vrijstellingen); art. 25a (KOR)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 9053, perUnitDen := 25000, adValoremBp := 500, minNum := 19521, minDen := 50000, statute := "TEDB NL manufactured tobacco (1.7.2025): 362.12 EUR per 1 000 cigarettes + 5.0 % of the retail selling price, at least 390.42 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 203, perUnitDen := 25, onPureAlcohol := true, statute := "TEDB NL beer (1.7.2025): 8.12 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 9569, perUnitDen := 10000, statute := "TEDB NL still wine (1.7.2025): 95.69 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 1827, perUnitDen := 100, onPureAlcohol := true, statute := "TEDB NL ethyl alcohol (1.7.2025): 1827 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 7891, perUnitDen := 10000, statute := "TEDB NL energy products (1.7.2025): unleaded petrol 789.1 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 413, perUnitDen := 800, statute := "TEDB NL energy products (1.7.2025): gas oil used as propellant 516.25 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 413, perUnitDen := 800, statute := "TEDB NL energy products (1.7.2025): gas oil used as heating fuel (non-business use) 516.25 EUR per 1 000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Omzetbelasting", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["NL 5111: wetten.overheid.nl, geldend 2025-01-01 t/m 2025-12-31", "NL 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["kleineondernemersregeling (art. 25a, optional exemption up to 20 000 euro) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exemptions (art. 11) by category, not quoted"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Wet op de accijns (BWBR0005135; fetched, rates not extracted in this pass)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 NL: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12100 } == 2100
#guard vat.embedded { good := .food, amount := 10900 } == 900
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 612
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 40
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 95
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 730
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 789
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 516
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 516

end NlGlobal.Consumption
