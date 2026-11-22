import PtGlobal.Pit

/-!
# PT 2025: Imposto sobre o valor acrescentado (5111); excises not modelled in this pass

Source: Código do IVA, Portal das Finanças (Autoridade Tributária, official), article page `pt/law/civa18.html` (current text); sha256 in `law/SHA256SUMS`.
* art. 18.º 1: "a) Para as importações, transmissões de bens e prestações de serviços constantes da lista I anexa a este diploma, a taxa de 6%"
* "b) ... constantes da lista II ..., a taxa de 13%"


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), PT excise records for the situation on 1 July 2025 (tobacco 4143, alcohol 4141, energy 4142; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `pt/law/tedb_*.json`).
* TEDB PT manufactured tobacco (1.7.2025): 151.88 EUR per 1 000 cigarettes + 1.0 % of the retail selling price, at least 154.46 EUR per 1 000
* TEDB PT still wine (1.7.2025): 0 EUR per hl of product
* TEDB PT ethyl alcohol (1.7.2025): 1602.51 EUR per hl of pure alcohol
* TEDB PT energy products (1.7.2025): unleaded petrol 634.36 EUR per 1 000 l
* TEDB PT energy products (1.7.2025): gas oil used as propellant 504 EUR per 1 000 l
* TEDB PT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 504 EUR per 1 000 l
-/

namespace PtGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Imposto sobre o valor acrescentado", standard := 2300, reduced := 1300, superReduced := 600, threshold := 0,
    classOf := fun gd => match gd with
      | .food | .water | .books | .newspapers | .medicines | .hotels | .transport => .superReduced
      | .restaurants => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "CIVA art. 18.º n.º 1 a) 6 % (lista I), b) 13 % (lista II), c) 23 %; art. 9.º (isenções)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 3797, perUnitDen := 25000, adValoremBp := 100, minNum := 7723, minDen := 50000, statute := "TEDB PT manufactured tobacco (1.7.2025): 151.88 EUR per 1 000 cigarettes + 1.0 % of the retail selling price, at least 154.46 EUR per 1 000" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB PT still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 160251, perUnitDen := 10000, onPureAlcohol := true, statute := "TEDB PT ethyl alcohol (1.7.2025): 1602.51 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 15859, perUnitDen := 25000, statute := "TEDB PT energy products (1.7.2025): unleaded petrol 634.36 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 63, perUnitDen := 125, statute := "TEDB PT energy products (1.7.2025): gas oil used as propellant 504 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 63, perUnitDen := 125, statute := "TEDB PT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 504 EUR per 1 000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Imposto sobre o valor acrescentado", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["PT 5111: Portal das Finanças current text (continental rates)", "PT 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["small-business exemption (art. 53.º) not read: no threshold applied"] else [])
  ++ (if !g.consumption.isEmpty then ["continental rates (Açores and Madeira lower) ; lists I and II by category"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Código dos Impostos Especiais de Consumo (DL 73/2010)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["5121 PT beer duty (CIEC art. 78, banded by degree Plato) not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 PT: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12300 } == 2300
#guard vat.embedded { good := .restaurants, amount := 11300 } == 1300
#guard vat.embedded { good := .food, amount := 10600 } == 600
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 201
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 641
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 634
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 504
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 504

end PtGlobal.Consumption
