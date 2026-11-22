import NoGlobal.Pit

/-!
# NO 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (arveavgift abolished 2014 (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (Stortingets skattevedtak 2025 (formuesskatt 1,0 % / 1,1 %, kommune 0,525 %)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 not levied (cited)**: Lov om avgift på arv og visse gaver (arveavgiftsloven) LOV-1964-06-19-14; lov 13 des 2013 nr. 110: lovdata: "Loven er opphevet med virkning for gaver som ytes 1 jan 2014 eller senere og arv etter dødsfall som skjer 1 jan 2014 eller senere, se lov 13 des 2013 nr. 110."


## 4200 Formuesskatt (stat 0,475/0,575 %, kommune 0,525 %) (pass 6)
Source: Stortingsvedtak om skatt av inntekt og formue mv. for inntektsåret 2025, lovdata (`no/law/stv_skatt2025.txt`).
* § 2-1: "Personlig skattyter og dødsbo svarer formuesskatt til staten av den delen av skattyterens samlede antatte formue som overstiger 1 760 000 kroner. Satsen skal være 0,475 pst. for formue inntil 20 700 000 kroner og 0,575 pst. for den delen av formuen som overstiger 20 700 000 kroner."; spouses taxed jointly: "3 520 000 kroner" and "41 400 000 kroner"
* § 2-3: "Personlig skattyter og dødsbo skal ha et fradrag i formuen på 1 760 000 kroner ... Satsen for formuesskatt til kommunene må ikke være høyere enn 0,525 pst. Maksimumssatsen gjelder når ikke lavere sats er vedtatt av kommunen."
* state + municipal: 1,0 % of the net wealth above the allowance, 1,1 % above 20 700 000 kr (the state band limit is on the whole wealth: 20 700 000 - 1 760 000 above the allowance)
-/

namespace NoGlobal.Wealth
open TaxKernel TaxKernel.Global

/-- Stortingets skattevedtak 2025 §§ 2-1, 2-3 (allowance 1 760 000 kr, 3 520 000 kr for spouses taxed jointly; state 0,475 % to 20 700 000 kr, 0,575 % above; municipal at most 0,525 %, the maximum applying unless lower is resolved) -/
def p6formue : WealthTax := { name := "Formuesskatt (stat 0,475/0,575 %, kommune 0,525 %)", sched := Schedule.ofList [(0, 1000), (18940000, 1100)], allowance := 1760000 }
def p6formueFor (married : Bool) : WealthTax := if married then { p6formue with allowance := 3520000 } else p6formue
def p6formueCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.assets.isEmpty then [] else
  let w := p6formueFor g.household.married
  [charge .wealth w.name (w.netWealth g.assets) (fun _ => w.base g.assets) (fun _ => w.gross g.assets)
     (event := "2025") (level := .central) (statute := "Stortingets skattevedtak 2025 §§ 2-1, 2-3 (allowance 1 760 000 kr, 3 520 000 kr for spouses taxed jointly; state 0,475 % to 20 700 000 kr, 0,575 % above; municipal at most 0,525 %, the maximum applying unless lower is resolved)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4200 Formuesskatt (stat 0,475/0,575 %, kommune 0,525 %)", covers := [.wealth],
     run := fun args g prev =>
       p6formueCharges g }]

def absent : List Absent :=
  [{ oecd := .estate, why := "lovdata: \"Loven er opphevet med virkning for gaver som ytes 1 jan 2014 eller senere og arv etter dødsfall som skjer 1 jan 2014 eller senere, se lov 13 des 2013 nr. 110.\"" }]

def notes : List String := ["NO 4200 Formuesskatt (stat 0,475/0,575 %, kommune 0,525 %): Stortingsvedtak 13.12.2024 for inntektsåret 2025 (lovdata STV/forskrift/2024-12-13-3203) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.assets.isEmpty then ["4200 asset values: the input's assessed value is taken as the formuesverdi; the skatteloven ch. 4 valuation discounts (home 25 %/70 %, shares and operating assets 80 %) are not applied to market values"] else [])
  ++ (if g.household.married then ["4200 spouses: the joint allowance 3 520 000 kr is applied, but the state band limit stays at 20 700 000 kr (41 400 000 kr jointly in § 2-1)"] else [])

#guard p6formue.gross [{ kind := .deposits, value := 1760000 }] == 0
#guard p6formue.gross [{ kind := .deposits, value := 2760000 }] == 100000
#guard p6formue.gross [{ kind := .deposits, value := 22600000 }] == 2103000
#guard (p6formueFor true).gross [{ kind := .deposits, value := 4520000 }] == 100000

end NoGlobal.Wealth
