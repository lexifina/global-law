import McGlobal.Pit

/-!
# MC 2025: Consumption family not reached (grade C)

* 5111 VAT (Code des taxes (TVA, art. A. 1 ff.)): tried legimonaco.mc not captured by the Internet Archive; would unlock: the Code des taxes text in force 2025 (legimonaco.mc)
* 5121 Excise duties (French excise regime applied by convention (CIBS, Légifrance blocked)): tried not reached in the P1 pass; would unlock: the excise act's 2025 rate articles


## 5111 VAT still grade C (pass 9)
* Monaco applies French VAT through its own Code des taxes (1963 customs union); the code was not fetched
* would unlock: Code des taxes sur le chiffre d'affaires, rate articles (Legimonaco)


## 5111 Taxe sur la valeur ajoutée (Monaco) (pass 13, grade A)
Source: Code des taxes sur le chiffre d'affaires (Monaco), legimonaco.mc, consolidated version dated 2025.01.01 as captured by the Internet Archive on 2025-05-13.
* art. 51: "Le taux normal de la taxe sur la valeur ajoutée est fixé à 20 %" (since 1 January 2014)
* art. 52-0 A 1°: 5,5 % on foodstuffs for human consumption (not confectionery, most chocolate products, margarines, caviar, alcoholic drinks); A 6°: books, including e-books; B: only the standing charge (abonnement) of electricity up to 36 kVA, gas and heat
* art. 56: 10 % on hotel accommodation (a), passenger transport (f), television subscriptions (h), sales for consumption on the premises and take-away prepared food, alcoholic drinks excepted (o, p)
* art. 59: 2,10 % on medicines reimbursable to the insured (art. 53: 10 % on the others); art. 95: 2,10 % on press publications
* art. 87 I (replaced from 1 January 2025 by the Ordonnance Souveraine n° 10.832): franchise for turnover of the previous year up to 85 000 euros (37 500 for services other than restaurants and accommodation)
-/

namespace McGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Taxe sur la valeur ajoutée (Monaco)", standard := 2000, reduced := 1000, reduced2 := 550, superReduced := 210, threshold := 85000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .books => .reduced2
      | .restaurants | .hotels | .transport => .reduced
      | .newspapers | .medicines => .superReduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "Code des taxes sur le chiffre d'affaires (version du 1er janvier 2025) art. 51 (20 %), 52-0 (5,5 %), 56 (10 %), 59 et 95 (2,10 %), 87 I (franchise: 85 000 euros)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Taxe sur la valeur ajoutée (Monaco) (pass 13)", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MC 5111 pass 13: Legimonaco, Code des taxes sur le chiffre d'affaires, version du 1er janvier 2025, via the Internet Archive 2025-05-13 (`mc/law/code_taxes_ca_v20250101_wb20250513.xml`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty || g.entity == .company then ["5121 Excise duties: not modelled (grade C: not reached in the P1 pass)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["health, education, residential rent, financial services and insurance taken as exempt from the code's structure (the exemption articles were not read item by item)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["medicines taken at 2,10 % (art. 59: reimbursable); non-reimbursable medicines are at 10 % (art. 53)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas) then ["electricity and gas at 20 %: the 5,5 % of art. 52-0 B applies to the standing charge only, which the basket does not separate"] else [])
  ++ (if g.entity == .company && !g.company.sales.isEmpty then ["the franchise threshold is the goods one (85 000 euros, previous year); the 37 500 euros services threshold and the current-year limits are not applied"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .food, amount := 10550 } == 550
#guard vat.embedded { good := .restaurants, amount := 11000 } == 1000
#guard vat.embedded { good := .newspapers, amount := 10210 } == 210
#guard vat.embedded { good := .health, amount := 10000 } == 0
#guard vat.net { turnover := 85000, sales := [{ good := .other, net := 85000 }] } == 0

end McGlobal.Consumption
