import LuGlobal.Pit
import TaxKernel.Global2

/-!
# LU 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (LIR art. 99bis, 99ter (plus-values spéculatives)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 gains of individuals stacked on the 1.x income tax (pass 10, kernel 2.5.0 StackRule)
Source: Loi modifiée du 4 décembre 1967 concernant l'impôt sur le revenu, texte coordonné (`lu/law/LIR_2025-01-01.txt`); kernel 2.5.0 StackRule.
* art. 99bis (1) 1.: gains on property acquired for consideration are speculative when the interval between acquisition and realisation does not exceed five years for real estate and six months for other property; real estate realised between 1 January and 30 June 2025: two years (from 1 July to 30 September 2025: two years if the compromis was registered by 30 June 2025)
* art. 99bis: speculative gains are exempt where their total for the calendar year is below 500 euros (Freigrenze)
* speculative gains are revenus divers taxed at the progressive scale: the net gain enters the 1.x line's `rentalIncome`, which the 1.x model adds in full to the taxable income
* long-held non-substantial shares are exempt; art. 99ter (real estate after the speculative period) and art. 100 (substantial participations) are taxed at half the global rate: grade C


## 1100 art. 99ter and 100 at half the global rate (pass 14, kernel 2.6.0)
Source: Loi modifiée du 4 décembre 1967 concernant l'impôt sur le revenu, texte coordonné en vigueur au 1er janvier 2025 (`lu/law/LIR_2025-01-01.txt`).
* art. 99ter (1): gains on private real estate realised more than five years after acquisition; for sales from 1 January to 30 June 2025 more than two years (from 1 July to 30 September 2025 also, with a compromis registered by 30 June 2025); (2) the gain is the price less the acquisition price and costs
* art. 100 (1)-(2): gains on a participation realised more than six months after acquisition where the seller (with spouse or partner and minor children) held more than 10 % at any time in the five preceding years
* art. 102 (6): the acquisition price for art. 99ter to 101 is revalued by the year's coefficient (read from the disposal's index); art. 102bis: the main home is outside art. 99bis and 99ter
* art. 130 (4): the sum of the art. 99ter to 101 income is reduced by 50 000 euros (100 000 for spouses taxed jointly), less the abattements of the ten earlier years
* art. 131 (1) c, 132 (2): that income is taxed at half the global rate of the adjusted taxable income; the 1.x line keeps the ordinary income at the tariff (art. 131 (1) a). Kernel: the amount enters the 1.x line's `rentalIncome` after the speculative gains, and the charge is 1/2 x amount x PIT / taxable income of that line (`detail.taxableIncome`); the 1.x PIT includes the contribution au fonds pour l'emploi, so the charge carries the contribution on this tax
* Hand check (case lu-half): single, wages 80 000 (taxable income 70 100), a 25 % participation held 36 months sold at a gain of 400 000: less 50 000 = 350 000; the 1.x line with it: taxable income 420 100, income tax 158 921 + fonds pour l'emploi 13 369 = 172 290; 1/2 x 350 000 x 172 290 / 420 100 = 71 771

* FT review (seventh pass): art. 99ter gains realised 1 January - 30 September 2025 are taxed at a quarter of the global rate (Loi du 22 mai 2024 art. 14; L. 04.04.25 art. 7; L. 27.06.25 art. 7); the rule takes the quarter for every 2025 sale (no date window in kernel 2.6.0); art. 100 stays at half.


## 1100 art. 99bis / 99ter split by the sale date (pass 17, kernel 2.7.0, grade A)
Sources: Loi du 22 mai 2024 (Mémorial A 219) art. 14; Loi du 4 avril 2025 (Mémorial A 121) art. 1, 2, 7 (effect 1 January 2025, art. 9); Loi du 27 juin 2025 (Mémorial A 271) art. 1, 2, 7 (in force the day after publication, 1 July 2025, art. 8); L.I.R. texte coordonné au 1er janvier 2025 art. 99bis, 99ter, 102bis, 130 (4), 131 (1) c, d. Texts in `lu/law/`.
* art. 99bis: real estate realised 1.1-30.6.2025 is speculative within two years; 1.7-30.9.2025 within two years if the compromis was registered by 30.6.2025 (not an input: taken as registered, flagged); from 1.10.2025 within five years
* art. 99ter: the matching derogations (more than two years, to 30.9.2025); from 1.10.2025 more than five years
* Loi du 22 mai 2024 art. 14 as amended: art. 99ter income realised 1.1-30.9.2025 is extraordinary income of art. 131 (1) d (a quarter of the global rate); from 1.10.2025 art. 131 (1) c (half)
* Kernel 2.7.0: four dated rules (`dateTo := "2025-09-30"` / `dateFrom := "2025-10-01"`); the art. 99ter rules and the art. 100 rule take their global rate from the 1.x line with every stacked amount (`rateFromStack`), the one rate of art. 131 (1); a real-estate disposal without a `"date"` is not priced (grade C), and neither are the rules after it
* This supersedes the FT reviewer 7 block above (a quarter for every 2025 sale, grade B, while kernel 2.6.0 had no date window); the reviewer's note is kept in the spec
-/

namespace LuGlobal.Capital
open TaxKernel TaxKernel.Global

/-- L.I.R. art. 99bis (1) 1. b), (3): speculative gains on movables held at most six months; Freigrenze 500 EUR -/
def p10luMov : StackRule :=
  { name := "Impôt sur le revenu: bénéfices de spéculation, biens meubles (art. 99bis)",   statute := "L.I.R. art. 99bis (1) 1. b) (six months), art. 99bis Freigrenze (inférieur à 500 euros); barème art. 118 (1.x model)",   gainKinds := [.listedShares, .unlistedShares, .bonds, .other], gainRule := { exemptAfterMonths := 7 },   exclusion := { amount := 500, threshold := true }, into := .rentalIncome }
/-- L.I.R. art. 99bis (1) 1. a) with the 2025 derogations: real estate realised 1.1-30.6.2025 (L. 04.04.25 art. 1) and
1.7-30.9.2025 with a compromis registered by 30.6.2025 (L. 27.06.25 art. 1) is speculative within two years; 102bis: not
the main home (pass 17: dated, kernel 2.7.0) -/
def p10luRe : StackRule :=
  { name := "Impôt sur le revenu: bénéfices de spéculation, immeubles (art. 99bis), réalisés du 1.1 au 30.9.2025 (deux ans)",   statute := "L.I.R. art. 99bis (1) 1. a), 102bis; dérogations pour les immeubles réalisés du 1er janvier au 30 juin 2025 (L. 04.04.25 art. 1) et du 1er juillet au 30 septembre 2025, compromis enregistré au plus tard le 30 juin 2025 (L. 27.06.25 art. 1): two years; barème art. 118 (1.x model)",   gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 25, mainHomeExempt := true }, into := .rentalIncome,   dateTo := "2025-09-30" }
/-- art. 99bis (1) 1. a) without a derogation: real estate realised from 1.10.2025 is speculative within five years -/
def p17luRe5 : StackRule :=
  { p10luRe with name := "Impôt sur le revenu: bénéfices de spéculation, immeubles (art. 99bis), réalisés à partir du 1.10.2025 (cinq ans)",   statute := "L.I.R. art. 99bis (1) 1. a) (five years), 102bis; barème art. 118 (1.x model)",   gainRule := { exemptAfterMonths := 61, mainHomeExempt := true }, dateTo := "", dateFrom := "2025-10-01" }
/-- L.I.R. art. 99ter (1)-(2) with the derogations of L. 04.04.25 art. 2 and L. 27.06.25 art. 2 (more than two years after
acquisition, realised 1.1-30.9.2025), 102 (6), 102bis, 130 (4); Loi du 22 mai 2024 art. 14 (end date 30.9.2025 by
L. 04.04.25 art. 7 and L. 27.06.25 art. 7): extraordinary income of art. 131 (1) d, a quarter of the global rate (pass 17:
dated, kernel 2.7.0; one global rate for the whole stack) -/
def p14luRe (married : Bool) : StackRule :=
  { name := "Impôt sur le revenu: plus-values immobilières (art. 99ter), quart du taux global (réalisées du 1.1 au 30.9.2025)",   statute := "L.I.R. art. 99ter (1)-(2), 102 (6), 102bis, 130 (4), 131 (1) d, 132 (2); Loi du 22 mai 2024 art. 14 (L. 04.04.25 art. 7, L. 27.06.25 art. 7: revenus réalisés jusqu'au 30 septembre 2025); L. 04.04.25 art. 2, L. 27.06.25 art. 2 (two years)",   gainKinds := [.home, .realEstate, .land],   gainRule := { longAfterMonths := 25, inclusionShortBp := 0, inclusionLongBp := 10000, indexCost := true, mainHomeExempt := true },   exclusion := { amount := if married then 100000 else 50000 }, pool := .household, into := .rentalIncome,   mode := .averageRate "taxableIncome", shareBp := 2500, dateTo := "2025-09-30", rateFromStack := true }
/-- art. 99ter (1)-(2) (more than five years), 102 (6), 102bis, 130 (4), 131 (1) c, 132 (2): realised from 1.10.2025,
half the global rate -/
def p17luReH (married : Bool) : StackRule :=
  { p14luRe married with
    name := "Impôt sur le revenu: plus-values immobilières (art. 99ter), demi-taux global (réalisées à partir du 1.10.2025)",   statute := "L.I.R. art. 99ter (1)-(2) (more than five years), 102 (6), 102bis, 130 (4), 131 (1) c, 132 (2)",   gainRule := { longAfterMonths := 61, inclusionShortBp := 0, inclusionLongBp := 10000, indexCost := true, mainHomeExempt := true },   shareBp := 5000, dateTo := "", dateFrom := "2025-10-01" }
/-- art. 100 (1)-(2) (a participation of more than 10 % within the five years, realised more than six months after
acquisition), 102 (6), 130 (4), 131 (1) c, 132 (2): half the global rate of the whole stack -/
def p14luSub (married : Bool) : StackRule :=
  { name := "Impôt sur le revenu: participations importantes (art. 100), demi-taux global",   statute := "L.I.R. art. 100 (1)-(2), 102 (6), 130 (4), 131 (1) c, 132 (2)",   gainKinds := [.listedShares, .unlistedShares],   gainRule := { longAfterMonths := 7, inclusionShortBp := 0, inclusionLongBp := 10000, indexCost := true, minStakeBp := 1001 },   exclusion := { amount := if married then 100000 else 50000 }, pool := .household, into := .rentalIncome,   mode := .averageRate "taxableIncome", shareBp := 5000, rateFromStack := true }
/-- the speculative gains (art. 99bis, at the tariff) first, then the extraordinary income at a quarter or half of one
global rate (art. 131 (1) c, d: the rate of the adjusted taxable income with all of it) -/
def p10luStackFor (married : Bool) : List StackRule :=
  [p10luMov, p10luRe, p17luRe5, p14luRe married, p17luReH married, p14luSub married]
/-- pass 17: each disposal with its record's "date" ("" when none) -/
def p17luDated (g : CanonGlobal) : List (Disposal × String) :=
  let js := (arrField g.raw "disposals").toList
  g.disposals.zipIdx.map fun (d, i) => (d, strField (js.getD i Lean.Json.null) "date")
def p17luIsRe (d : Disposal) : Bool := d.kind == .home || d.kind == .realEstate || d.kind == .land
def p10luStack : List StackRule := [p10luMov, p10luRe]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 gains stacked on the 1.x income tax (pass 10; art. 99ter / 100, pass 14; dated by the sale, one global rate, pass 17, kernel 2.7.0)", covers := [.pit],
     run := fun args g prev =>
       stackCharges base.pit base.route (p10luStackFor g.household.married) args g }]

def absent : List Absent :=
  []

def notes : List String := ["LU 1100 gains stacked on the 1.x PIT, pass 10 (kernel 2.5.0)", "LU 1100 art. 99ter / 100 at half the global rate (art. 131 (1) c): kernel 2.6.0 StackRule mode averageRate \"taxableIncome\", shareBp 5000 (pass 14)", "LU 1100 pass 17 (kernel 2.7.0): art. 99bis / 99ter split by the disposal's \"date\" (StackRule dateFrom / dateTo): to 30.9.2025 two years and a quarter of the global rate, from 1.10.2025 five years and half; art. 99ter and 100 share one global rate (rateFromStack); an undated real-estate disposal is grade C"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(stackUnknown base.pit base.route (p10luStackFor g.household.married) args g).isEmpty then ["1100 gains: a stacked rule could not be priced on the 1.x line (grade C)"] else [])
  ++ (if g.disposals.any (fun d => (d.kind == .home || d.kind == .realEstate || d.kind == .land || d.kind == .unlistedShares || d.kind == .listedShares) && 7 ≤ d.heldMonths) then ["1100 gains (art. 99ter / 100): the abattements granted in the ten earlier years (art. 130 (4)) and the 75 000 euros for a building inherited in the direct line (art. 130 (5)) are not known and not applied; the art. 102 (6) coefficient is the disposal's index (none given: 1)"] else [])
  ++ (if g.disposals.any (fun d => d.kind == .unlistedShares || d.kind == .listedShares) then ["1100 gains (art. 100): the stake is the one at the sale; a participation above 10 % at another time in the five years (art. 100 (2)) is not seen"] else [])
  ++ (if [g.disposals.any (fun d => p17luIsRe d && !d.mainHome && 25 ≤ d.heldMonths), g.disposals.any (fun d => (d.kind == .unlistedShares || d.kind == .listedShares) && 7 ≤ d.heldMonths && 1000 < d.stakeBp)].all id || ((p17luDated g).any (fun (d, s) => p17luIsRe d && !d.mainHome && 25 ≤ d.heldMonths && decide (s < "2025-10-01")) && (p17luDated g).any (fun (d, s) => p17luIsRe d && !d.mainHome && 61 ≤ d.heldMonths && !(decide (s < "2025-10-01")))) then ["1100 gains: the art. 130 (4) abattement is applied by each rule (real estate to 30.9.2025, real estate from 1.10.2025, participations); with two of them in one year it is counted more than once (grade C)"] else [])
  ++ (if (p17luDated g).any (fun (d, s) => p17luIsRe d && (isoYmd? s).isNone) then ["1100 gains (art. 99bis / 99ter): a real-estate disposal has no \"date\"; in 2025 the sale date decides the speculative period (two years to 30.9.2025, five years from 1.10.2025) and the rate (a quarter of the global rate to 30.9.2025, half from 1.10.2025): the stacked gains are not priced (grade C)"] else [])
  ++ (if (p17luDated g).any (fun (d, s) => p17luIsRe d && !d.mainHome && 25 ≤ d.heldMonths && d.heldMonths ≤ 60 && !(decide (s < "2025-07-01")) && decide (s < "2025-10-01")) then ["1100 gains (art. 99bis / 99ter): real estate sold 1.7-30.9.2025 more than two and at most five years after acquisition is taken under the two-year derogation, which needs the compromis registered by 30 June 2025 (L. 27.06.25 art. 1-2; not an input); without it the gain is speculative at the tariff"] else [])

#guard (p10luStackFor true).length == 6
#guard p10luStack.length == 2
#guard (p14luRe false).exclusion.amount == 50000
#guard (p14luSub true).exclusion.amount == 100000
#guard (p14luRe false).gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 24 } == 0
#guard (p14luRe false).gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 25 } == 200000
#guard (p14luSub false).gainRule.taxable 10000 10000 { kind := .unlistedShares, proceeds := 500000, cost := 100000, heldMonths := 24, stakeBp := 1000 } == 0
#guard (p14luSub false).gainRule.taxable 10000 10000 { kind := .unlistedShares, proceeds := 500000, cost := 100000, heldMonths := 24, stakeBp := 2500 } == 400000
#guard (p14luRe false).shareBp == 2500
#guard (p14luSub false).shareBp == 5000
#guard (p14luRe false).dateTo == "2025-09-30" && (p14luRe false).rateFromStack
#guard (p17luReH true).dateFrom == "2025-10-01" && (p17luReH true).shareBp == 5000 && (p17luReH true).exclusion.amount == 100000
#guard (p14luSub false).rateFromStack && p10luRe.dateTo == "2025-09-30" && p17luRe5.dateFrom == "2025-10-01"
#guard p17luRe5.gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 60 } == 200000
#guard p17luRe5.gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 61 } == 0
#guard (p17luReH false).gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 60 } == 0
#guard (p17luReH false).gainRule.taxable 10000 10000 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 61 } == 200000
#guard p10luRe.gainRule.taxable 10000 10000 { kind := .home, proceeds := 500000, cost := 300000, heldMonths := 12, mainHome := true } == 0

end LuGlobal.Capital
