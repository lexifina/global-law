import BgGlobal.Pit
import TaxKernel.Global2

/-!
# BG 2025: Данък върху добавената стойност (5111); excises not modelled in this pass

Source: Закон за данък върху добавената стойност, lex.bg (private publisher of the consolidated text with the amendment notes of each provision), `bg/law/zdds.html`; sha256 in `law/SHA256SUMS`.
* чл. 66 (изм. ДВ бр. 52 от 2022 г., в сила от 01.07.2022 г.) "(1) Стандартната ставка на данъка е 20 на сто"
* чл. 66а (в сила от 01.01.2023 г.) "Ставката на данъка е 9 на сто за: 1. доставка на услуга по настаняване, предоставяно в хотели ...; 2. доставка на книги ...; 3. доставки на храни, подходящи за бебета"


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), BG excise records for the situation on 1 July 2025 (tobacco 4053, alcohol 4051, energy 4052; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `bg/law/tedb_*.json`).
* TEDB BG beer (1.7.2025): 1.5 BGN per hl and degree Plato
* TEDB BG still wine (1.7.2025): 0 BGN per hl of product
* TEDB BG ethyl alcohol (1.7.2025): 1100 BGN per hl of pure alcohol
* TEDB BG energy products (1.7.2025): unleaded petrol 710 BGN per 1 000 l
* TEDB BG energy products (1.7.2025): gas oil used as propellant 646 BGN per 1 000 l
* TEDB BG energy products (1.7.2025): gas oil used as heating fuel (non-business use) 646 BGN per 1 000 l
-/

namespace BgGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Данък върху добавената стойност", standard := 2000, reduced := 900, threshold := 0,
    classOf := fun gd => match gd with
      | .hotels | .books => .reduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "ЗДДС чл. 66 ал. 1 (20 %), чл. 66а (9 %); чл. 38-50 (освободени доставки); чл. 96 (регистрация)"

def excise : Excise :=
  { rates := [
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB BG still wine (1.7.2025): 0 BGN per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 11, onPureAlcohol := true, statute := "TEDB BG ethyl alcohol (1.7.2025): 1100 BGN per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 71, perUnitDen := 100, statute := "TEDB BG energy products (1.7.2025): unleaded petrol 710 BGN per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 323, perUnitDen := 500, statute := "TEDB BG energy products (1.7.2025): gas oil used as propellant 646 BGN per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 323, perUnitDen := 500, statute := "TEDB BG energy products (1.7.2025): gas oil used as heating fuel (non-business use) 646 BGN per 1 000 l" }] }

/-- TEDB BG beer (1.7.2025): 1.5 BGN per hl and degree Plato (kernel 2.1 `ExciseRule`, line field "platoBp"). -/
def gxBeerRule : ExciseRule :=
  { good := .beer, name := "Excise duty on beer", perPlatoNum := 3, perPlatoDen := 200,   statute := "TEDB BG beer (1.7.2025): 1.5 BGN per hl and degree Plato" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Данък върху добавената стойност", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges [gxBeerRule] g }]

def absent : List Absent :=
  []

def notes : List String := ["BG 5111: lex.bg current text; arts. 66, 66a unchanged since 2022/2023 per their notes", "BG 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["registration threshold (чл. 96) read only in its 2026 wording (EUR): not applied for 2025"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Закон за акцизите и данъчните складове) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["5121 Excise duty on beer: charged by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no beer duty"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes) then ["5121 BG: excise on cigarettes not charged: the 2025 rate changed during the year and the purchase is undated (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 BG: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .hotels, amount := 10900 } == 900
#guard gxBeerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 18
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 440
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 710
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 646
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 646

end BgGlobal.Consumption
