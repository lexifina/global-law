import LcGlobal.Pit

/-!
# Saint Lucia 2025: income tax on companies (1200)

Source: Income Tax Act Cap. 15.02, Revised Laws of Saint Lucia (2023), attorneygeneralchambers.com (`lc/law/ita_s80.txt`,
`lc/law/ita_sch3.txt`, fetched 2026-11-21; Schedule 5 page held by the 1.x builder, `world/B13-caribbean/lc/law/
schedule-5.txt`). Grade A.
* s. 80 (1): tax charged "at the rates specified in Schedule 5"; Sched. 5 para 2 (a) (vi): companies "for income year
  2005 and subsequent income years-30%" (para (aa): the reduced rates need no arrears; assumed met).
* s. 80 (2) (b), Sched. 3 para 3 (S.I. 59/2010): payments to non-residents of royalty, management charges, commission
  or fee, premiums and other income payments 25 %; interest or discount 15 %; "final liability". Dividends excluded
  (para 1 (1) (g) (i)).

**Pass 7 (2026-11-21), withholding on payments abroad:** dividends are excluded from Sched. 3 (para 1 (1) (g) (i)): a cited 0.
-/

namespace LcGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon LcGlobal

def regime : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 3000 }

def citStatute : String := "Income Tax Act Cap. 15.02 s. 80 (1), Sched. 5 para 2 (a) (vi): 'for income year 2005 and subsequent income years-30%'"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 1500, statute := "ITA Cap. 15.02 Sched. 3 para 3 (b) (15 %)" }, { kind := .royalty, rateBp := 2500, statute := "ITA Cap. 15.02 Sched. 3 para 3 (a) (25 %)" }, { kind := .services, rateBp := 2500, statute := "ITA Cap. 15.02 Sched. 3 para 3 (a) (management charges, fees: 25 %)" }, { kind := .dividend, rateBp := 0, statute := "ITA Cap. 15.02 Sched. 3 para 1 (1) (g) (i) (S.I. 59/2010): dividends excluded: none withheld" }] }

def citF : Family := corpFamily "1200 Income tax (companies)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 250000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 0

end LcGlobal.Corporate
