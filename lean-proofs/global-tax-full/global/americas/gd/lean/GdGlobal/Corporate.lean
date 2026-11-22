import GdGlobal.Pit

/-!
# GD 2025: corporate income tax (1200)

Income Tax Act (Grenada), Schedule (Rates of Tax) [Section 56.]: "(b) a company 30 per cent" (`world/B13-caribbean/gd/law/ita.txt`): grade B, the consolidation's date and the later amending Acts not checked.

**Pass 7 (2026-11-21), withholding on payments abroad:** Income Tax Act Cap. 149 s. 50 (1) as substituted by Act 27 of 2015 s. 11: a resident payer deducts tax at the Third Schedule rate on a payment of a kind it lists; para 1 (1) (Act 27 of 2015 s. 18): (a) interest or discount, (c) royalty, (d) technical assistance fee, management charge, director's fee or similar commission or fee; para 3: 15 % of every dollar, final. Dividends are not listed: a cited 0. Grade A.
-/

namespace GdGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon GdGlobal

def regime : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 3000 }

def citStatute : String := "Income Tax Act s. 56, Schedule: '(b) a company 30 per cent'"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .interest, rateBp := 1500, statute := "ITA Cap. 149 s. 50 (1) (Act 27 of 2015 s. 11), Third Sched. para 1 (1) (Act 27 of 2015 s. 18), para 3: 15 %, final" }, { kind := .royalty, rateBp := 1500, statute := "ITA Cap. 149 s. 50 (1) (Act 27 of 2015 s. 11), Third Sched. para 1 (1) (Act 27 of 2015 s. 18), para 3: 15 %, final" }, { kind := .services, rateBp := 1500, statute := "ITA Cap. 149 s. 50 (1) (Act 27 of 2015 s. 11), Third Sched. para 1 (1) (Act 27 of 2015 s. 18), para 3: 15 %, final" }, { kind := .dividend, rateBp := 0, statute := "ITA Cap. 149 Third Sched. para 1 (1) as substituted by Act 27 of 2015 s. 18: dividends are not a listed payment: none withheld" }] }

def citF : Family := corpFamily "1200 Income tax (companies)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "s. 50 (4A)-(4C) waivers for qualifying tourism and health investments (Act 8 of 2016) not modelled"

#guard regime.citTax { profit := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 0

end GdGlobal.Corporate
