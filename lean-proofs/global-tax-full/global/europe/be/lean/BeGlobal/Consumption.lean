import BeGlobal.Pit
import TaxKernel.Global2

/-!
# BE 2025: Taxe sur la valeur ajoutée (5111); excises not modelled in this pass

Source: SPF Finances (official guide) as captured by the Internet Archive: "Les taux de TVA" 2025-05-17 (`be/law/spf_taux_tva_wb20250517.html`) and "Régime de la franchise de taxe" 2025-07-08 (`be/law/spf_franchise_wb20250708.html`); Justel pages of the Code (numac 1969070305) and AR n° 20 (numac 1970072012) carry no article text; sha256 in `law/SHA256SUMS`.
* SPF Finances page (in our words): three rates, 21 % standard (code R03), 12 % intermediate (R02) and 6 % reduced (R01), plus a zero rate (R00) for a few goods and services; the AR n° 20 lists what falls under each rate
* "Vous pouvez prétendre au régime de la franchise de taxe si le chiffre d'affaires annuel de votre entreprise ne dépasse pas 25.000 euros (hors TVA)."


## 5111 the 6 % and 12 % goods (pass 18, grade B)
Source: PwC Worldwide Tax Summaries, Belgium, Corporate - Other taxes, Internet Archive 2025-05-26 (`be/law/pwc_corpother_wb2025.*`), facts only.
* 12 %: restaurant and catering services (without the drinks), margarine, social housing and some renovation works
* 6 %: basic necessities such as food and pharmaceuticals, water by pipeline, some printed and electronic publications, passenger transport, hotels and camping, cultural and sporting venues, electricity and natural gas for non-business use (from 1 July 2023, under conditions)
* Basket: food, medicines, water, books, newspapers, transport, hotels, electricity, gas at 6 %; restaurants 12 %; the rest 21 %


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), BE excise records for the situation on 1 July 2025 (tobacco 4050, alcohol 4205, energy 4049; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `be/law/tedb_*.json`).
* TEDB BE manufactured tobacco (1.7.2025): 189.7803 EUR per 1 000 cigarettes + 31.5 % of the retail selling price, at least 353.9129 EUR per 1 000
* TEDB BE beer (1.7.2025): 2.0043 EUR per hl and degree Plato
* TEDB BE still wine (1.7.2025): 74.9086 EUR per hl of product
* TEDB BE ethyl alcohol (1.7.2025): 2992.7928 EUR per hl of pure alcohol
* TEDB BE energy products (1.7.2025): unleaded petrol 600.1587 EUR per 1 000 l
* TEDB BE energy products (1.7.2025): gas oil used as propellant 600.1586 EUR per 1 000 l
* TEDB BE energy products (1.7.2025): gas oil used as heating fuel (non-business use) 17.2564 EUR per 1 000 l
-/

namespace BeGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 2100, reduced := 1200, superReduced := 600, threshold := 25000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .medicines | .water | .books | .newspapers | .transport | .hotels | .electricity | .gas => .superReduced
      | .restaurants => .reduced
      | _ => .standard }

def vatStatute : String := "Code de la TVA art. 37 et AR n° 20 tableaux A (6 %) et B (12 %) as listed by PwC 2025 (21 %, 12 %: restaurant and catering services without drinks; 6 %: food, pharmaceuticals, piped water, printed and electronic publications, passenger transport, hotels, electricity and natural gas for non-business use); art. 56bis (régime de la franchise, 25 000 euros)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 1897803, perUnitDen := 10000000, adValoremBp := 3150, minNum := 3539129, minDen := 10000000, statute := "TEDB BE manufactured tobacco (1.7.2025): 189.7803 EUR per 1 000 cigarettes + 31.5 % of the retail selling price, at least 353.9129 EUR per 1 000" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 374543, perUnitDen := 500000, statute := "TEDB BE still wine (1.7.2025): 74.9086 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 3740991, perUnitDen := 125000, onPureAlcohol := true, statute := "TEDB BE ethyl alcohol (1.7.2025): 2992.7928 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 6001587, perUnitDen := 10000000, statute := "TEDB BE energy products (1.7.2025): unleaded petrol 600.1587 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 3000793, perUnitDen := 5000000, statute := "TEDB BE energy products (1.7.2025): gas oil used as propellant 600.1586 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 43141, perUnitDen := 2500000, statute := "TEDB BE energy products (1.7.2025): gas oil used as heating fuel (non-business use) 17.2564 EUR per 1 000 l" }] }

/-- TEDB BE beer (1.7.2025): 2.0043 EUR per hl and degree Plato (kernel 2.1 `ExciseRule`, line field "platoBp"). -/
def gxBeerRule : ExciseRule :=
  { good := .beer, name := "Excise duty on beer", perPlatoNum := 20043, perPlatoDen := 1000000,   statute := "TEDB BE beer (1.7.2025): 2.0043 EUR per hl and degree Plato" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Taxe sur la valeur ajoutée", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges [gxBeerRule] g }]

def absent : List Absent :=
  []

def notes : List String := ["BE 5111: SPF Finances pages captured 2025-05-17 / 2025-07-08", "BE 5111 pass 18: 6 % and 12 % goods from PwC 2025 (food, medicines, water, publications, transport, hotels, household energy at 6 %; restaurants 12 %), grade B", "BE 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Loi du 22 décembre 2009 (accises) and the loi-programme rate tables (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .restaurants) then ["restaurants at 12 % (AR n° 20 tableau B per PwC 2025): drinks served with meals are 21 % and are not separated"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas) then ["electricity and natural gas at 6 %: the rate for non-business use (from 1.7.2023, conditions not checked)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic || s.good == .recreation) then ["non-alcoholic drinks and recreation at 21 %: the PwC 2025 lists name food and cultural or sporting venues only"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["5121 Excise duty on beer: charged by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no beer duty"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 BE: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12100 } == 2100
#guard vat.net { turnover := 25000, sales := [{ good := .other, net := 25000 }] } == 0
#guard vat.embedded { good := .food, amount := 10600 } == 600
#guard vat.embedded { good := .restaurants, amount := 11200 } == 1200
#guard vat.embedded { good := .hotels, amount := 10600 } == 600
#guard vat.embedded { good := .nonAlcoholic, amount := 12100 } == 2100
#guard gxBeerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 24
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1764
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 74
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 1197
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 600
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 600
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 17

end BeGlobal.Consumption
