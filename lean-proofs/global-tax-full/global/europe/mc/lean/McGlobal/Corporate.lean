import McGlobal.Pit

/-!
# MC 2025: Corporate family not reached (grade C)

* 1200 Corporate income tax (Impôt sur les bénéfices (Ordonnance souveraine n° 3.152 du 19 mars 1964), 25 %): tried legimonaco.mc not captured; would unlock: the ISB ordinance in force 2025
* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried legimonaco.mc not captured; would unlock: the ISB ordinance in force 2025


## 1200 Impôt sur les bénéfices (pass 9, grade A)
Source: Ordonnance Souveraine n° 3.152 du 19 mars 1964 instituant un impôt sur les bénéfices, Legimonaco via the Internet Archive (`mc/law/legimonaco_isb_wb.txt`).
* art. 1: the tax falls on a) enterprises with an industrial or commercial activity in Monaco "lorsque leur chiffre d'affaires provient à concurrence de 25 % au moins, d'opérations faites ... en dehors du territoire monégasque", b) companies whose Monaco activity is collecting royalties from patents, trademarks, processes or literary and artistic property
* art. 21: "À compter du 1er janvier 2022, le taux normal est fixé à 25 %"
* a company below the 25 % test owes no profits tax: the model books none for it


## 1200 withholding still grade C (pass 9)
* OS n° 3.152 (profits tax) read: it contains no withholding on payments abroad; no Monegasque text stating the absence of withholding was found
* would unlock: a Monegasque official text listing the taxes levied (Département des Finances) to cite the absence
-/

namespace McGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- OS n° 3.152 art. 1 a): the profits tax applies to an industrial or commercial enterprise whose turnover comes for at
least 25 % from operations made outside Monaco (taken here as the exported share of the company's sales). -/
def mcIsbScope (co : Company) : Bool :=
  let tot := co.sales.foldl (fun a s => a + s.net) 0
  let ex := (co.sales.filter (·.exported)).foldl (fun a s => a + s.net) 0
  tot > 0 && 4 * ex ≥ tot

/-- Ordonnance Souveraine n° 3.152 du 19 mars 1964 art. 1 a), art. 21 (25 % from 1.1.2022) -/
def p9cit : CorpRegime :=
  { name := "Impôt sur les bénéfices", sched := Schedule.flat 2500 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impôt sur les bénéfices (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company && mcIsbScope g.company then [p9cit.citCharge g.company "Ordonnance Souveraine n° 3.152 du 19 mars 1964 art. 1 a), art. 21 (25 % from 1.1.2022)"] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MC 1200 Impôt sur les bénéfices pass 9: Legimonaco, Internet Archive capture 2026-05-08 (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["1200 Withholding on payments abroad: not modelled (grade C: legimonaco.mc not captured)"] else [])
  ++ (if g.entity == .company then ["the 25 % test is read on the exported share of the company's sales; royalty-collecting companies (art. 1 b)) and the option of other companies are not tested"] else [])

#guard p9cit.citTax { profit := 100000, turnover := 10000000 } == 25000
#guard p9cit.citTax { profit := 0, turnover := 10000000 } == 0
#guard mcIsbScope { sales := [{ good := .other, net := 75, exported := false }, { good := .other, net := 25, exported := true }] } == true
#guard mcIsbScope { sales := [{ good := .other, net := 76, exported := false }, { good := .other, net := 24, exported := true }] } == false

end McGlobal.Corporate
