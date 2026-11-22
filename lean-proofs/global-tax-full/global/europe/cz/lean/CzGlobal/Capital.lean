import CzGlobal.Pit
import TaxKernel.Global2

/-!
# CZ 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (zákon 586/1992 Sb. § 4 (1) písm. b, w, § 10): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 gains of individuals stacked on the 1.x income tax (pass 10, kernel 2.5.0 StackRule)
Source: Zákon o daních z příjmů 586/1992 Sb., znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`); kernel 2.5.0 StackRule.
* § 4 odst. 1 písm. a): the sale of a family house or flat in which the seller lived for at least 2 years immediately before the sale is exempt
* § 4 odst. 1 písm. b): other real estate is exempt where more than 10 years pass between acquisition and sale; písm. u): securities where more than 3 years pass
* § 10 odst. 1 písm. b), odst. 4: other gains are 'ostatní příjmy', proceeds less the acquisition price, in the general base taxed at 15 % / 23 % (§ 16)
* the net gain enters the 1.x line as the seller's wage (`into := .wages`): the 1.x model taxes wages in full at the § 16 scale on the total base (employee contributions are not in its income tax); unlisted shares are left out (s.r.o. shares: 5-year test not separable)
-/

namespace CzGlobal.Capital
open TaxKernel TaxKernel.Global

/-- ZDP § 10 odst. 1 písm. b) bod 2, odst. 4; § 4 odst. 1 písm. u): securities, exempt when held more than 3 years -/
def p10czSec : StackRule :=
  { name := "Daň z příjmů fyzických osob: prodej cenných papírů (§ 10)",   statute := "zákon 586/1992 Sb. § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. u) (exempt after 3 years); rates § 16 (1.x model)",   gainKinds := [.listedShares, .bonds], gainRule := { exemptAfterMonths := 37 }, into := .wages }
/-- ZDP § 10 odst. 1 písm. b) bod 1; § 4 odst. 1 písm. a) (2 years' residence), písm. b) (10 years) -/
def p10czRe : StackRule :=
  { name := "Daň z příjmů fyzických osob: prodej nemovitých věcí (§ 10)",   statute := "zákon 586/1992 Sb. § 10 odst. 1 písm. b), odst. 4; § 4 odst. 1 písm. a) (main home, 2 years' residence), písm. b) (exempt after 10 years); rates § 16 (1.x model)",   gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 121, mainHomeExempt := true }, into := .wages }

def p10czStack : List StackRule := [p10czSec, p10czRe]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 gains stacked on the 1.x income tax (pass 10)", covers := [.pit],
     run := fun args g prev =>
       stackCharges base.pit base.route p10czStack args g }]

def absent : List Absent :=
  []

def notes : List String := ["CZ 1100 gains stacked on the 1.x PIT, pass 10 (kernel 2.5.0)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(stackUnknown base.pit base.route p10czStack args g).isEmpty then ["1100 gains: a stacked rule could not be priced on the 1.x line (grade C)"] else [])
  ++ (if g.disposals.any (fun d => d.kind == .unlistedShares) then ["1100 gains: unlisted shares (an s.r.o. share is not a security: 5-year test of § 4 odst. 1 písm. r)) are not modelled (grade C)"] else [])

#guard p10czStack.length == 2

end CzGlobal.Capital
