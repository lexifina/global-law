import SkGlobal.Pit
import TaxKernel.Global2

/-!
# SK 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (zákon 595/2003 Z. z. § 8, § 9 (2)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 gains of individuals stacked on the 1.x income tax (pass 10, kernel 2.5.0 StackRule)
Source: Zákon o dani z príjmov 595/2003 Z. z., Slov-Lex znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`); kernel 2.5.0 StackRule.
* § 9 ods. 1 písm. a): the sale of real estate is exempt after five years from acquisition; písm. k): securities admitted to a regulated market after one year from acquisition (and admission)
* § 9 ods. 1 písm. c): movable things are exempt (securities are not movable things for this purpose); písm. i): § 8 ods. 1 písm. d)-f) income up to 500 EUR in total is exempt
* the net gain enters the 1.x line's `capitalGains` (§ 8 ods. 1 písm. e) income, which the 1.x model taxes at the § 15 rates after the 500 EUR exemption); there is no main-home exemption beyond the five years
-/

namespace SkGlobal.Capital
open TaxKernel TaxKernel.Global

/-- ZDP § 8 ods. 1 písm. e); § 9 ods. 1 písm. k): listed securities, exempt after one year -/
def p10skSec : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj cenných papierov prijatých na regulovaný trh (§ 8)",   statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. e), ods. 5; § 9 ods. 1 písm. k) (exempt after one year), písm. i) (500 EUR, 1.x model); rates § 15 (1.x model)",   gainKinds := [.listedShares, .bonds], gainRule := { exemptAfterMonths := 13 }, into := .capitalGains }
/-- § 8 ods. 1 písm. e): other securities and shares, no holding-period exemption -/
def p10skOther : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj iných cenných papierov a podielov (§ 8)",   statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. e), ods. 5; § 9 ods. 1 písm. i) (500 EUR, 1.x model)",   gainKinds := [.unlistedShares], into := .capitalGains }
/-- § 8 ods. 1 písm. b); § 9 ods. 1 písm. a): real estate, exempt five years after acquisition -/
def p10skRe : StackRule :=
  { name := "Daň z príjmov fyzickej osoby: predaj nehnuteľnosti (§ 8)",   statute := "zákon 595/2003 Z. z. § 8 ods. 1 písm. b), ods. 5; § 9 ods. 1 písm. a) (exempt after five years)",   gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 61 }, into := .capitalGains }

def p10skStack : List StackRule := [p10skSec, p10skOther, p10skRe]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 gains stacked on the 1.x income tax (pass 10)", covers := [.pit],
     run := fun args g prev =>
       stackCharges base.pit base.route p10skStack args g }]

def absent : List Absent :=
  []

def notes : List String := ["SK 1100 gains stacked on the 1.x PIT, pass 10 (kernel 2.5.0)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(stackUnknown base.pit base.route p10skStack args g).isEmpty then ["1100 gains: a stacked rule could not be priced on the 1.x line (grade C)"] else [])
  ++ (if g.disposals.any (fun d => d.kind == .other) then ["1100 gains: movable things are exempt (§ 9 ods. 1 písm. c)); not booked"] else [])

#guard p10skStack.length == 3

end SkGlobal.Capital
