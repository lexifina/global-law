import TmGlobal.Pit

/-!
# Turkmenistan 2025: VAT (5111) and excises (5121)

Source: Tax Code of Turkmenistan (Russian text), mejlis.gov.tm > Codes, consolidated with the amending laws up to
12 April 2025 (Ведомости 2025 № 1 ст. 4) (`cmp20/world/B05-former-ussr/tm/law/mejlis_code10_taxcode_20261120.txt`,
fetched 2026-11-20 by the 1.x TM builder; the articles used carry no amendment after 2024; sha256 in `law/SOURCES.tsv`).
* **art. 103**: "15 процентов - в отношении других налогооблагаемых операций"; 0 % for art. 105 (exports).
* **art. 95 (2)**: not VAT payers: "юридические лица частной формы собственности" and individual entrepreneurs under
  the simplified system. A company line with flag `private` therefore owes no VAT.
* **art. 106 (1)** no VAT on: urban public passenger transport (taxis excepted); medicines; health services;
  education; insurance; food products other than excisable goods; catering ("продукции общественного питания");
  housing and communal services to the population, rent included.
* **art. 119** excise on goods produced in Turkmenistan, ad valorem "от стоимости": beer 34,5 %; grape wines,
  spirits and other alcoholic drinks with alcohol up to 20 % 44,85 %, over 20 to 30 % 70,15 %, over 30 % 88,55 %;
  petrol 40 %; diesel 40 %. The base is the cost before excise and VAT (art. 117-118), so inside a retail price `p`
  (VAT charged on the price with excise) the excise is p·e / ((1+e)(1+0.15)) for a VAT-taxed good. Imports are taxed
  on the customs value (not in the basket): not modelled; tobacco is only listed for imports.
-/

namespace TmGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Налог на добавленную стоимость", standard := 1500,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .restaurants | .transport | .medicines | .health | .education | .insurance
      | .rent | .water | .electricity | .gas => .exempt
      | _ => .standard }

/-- art. 119 domestic ad valorem rate, bp of the value before excise. -/
def exciseBp (s : Spend) : Int :=
  match s.good with
  | .beer => 3450
  | .wine | .spirits => if s.abvBp ≤ 2000 then 4485 else if s.abvBp ≤ 3000 then 7015 else 8855
  | .petrol | .diesel => 4000
  | _ => 0

/-- Excise inside a retail price: value v, price = v (1 + e) (1 + VAT). -/
def exciseIn (s : Spend) : Int :=
  let e := exciseBp s
  let t := vat.rateOf s.good
  divR .down (pos s.amount * e * BP) ((BP + e) * (BP + t))

def exciseCharges (xs : List Spend) : List Charge :=
  (xs.filter fun s => exciseBp s > 0).map fun s =>
    charge .excise "Акциз" s.amount id (fun _ => exciseIn s) (event := s.good.name) (bearer := .consumer)
      (statute := s!"Налоговый кодекс ст. 119 (производимые товары, {exciseBp s / 100},{exciseBp s % 100} % от стоимости)")

def vatStatute : String := "Налоговый кодекс ст. 103 (15 %), ст. 95 п. 2, ст. 106 п. 1"

def families : List Family :=
  [{ name := "5111 НДС, 5121 акциз", covers := [.vat, .excise],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty && !g.company.flags.contains "private" then
            [vat.businessCharge g.company vatStatute] else [])
       ++ exciseCharges g.consumption }]

def absent : List Absent := []
def notes : List String := ["TM 5111/5121: Tax Code (mejlis.gov.tm consolidation to 12.04.2025)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise (art. 119) is on imports by customs value: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) then
    ["excise taken at the domestic-production rate (imports: customs value with minima, not modelled)"] else [])
  ++ (if !g.consumption.isEmpty then ["VAT in the basket assumes VAT-paying (state-form) sellers; private sellers are not VAT payers (art. 95 (2))"] else [])

#guard vat.embedded { good := .clothing, amount := 11500 } == 1500
#guard vat.embedded { good := .food, amount := 11500 } == 0
-- petrol: value 100, excise 40, VAT 15 % of 140 = 21; retail 161
#guard exciseIn { good := .petrol, amount := 161 } == 40
-- vodka 40 %: value 100, excise 88,55, VAT 28,28; retail 216,83
#guard exciseIn { good := .spirits, amount := 21683, abvBp := 4000 } == 8854

end TmGlobal.Consumption
