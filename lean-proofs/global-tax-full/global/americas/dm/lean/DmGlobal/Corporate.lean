import DmGlobal.Pit

/-!
# Dominica 2025: income tax on companies (1200)

Source: Inland Revenue Division page "Current income tax rates" (1.x builder's copy
`world/B13-caribbean/dm/law/customer-service_current-income-tax-rates.txt`): "Effective 1st January 2016, tax on the
Chargeable Income of a company, on every dollar thereof at 25%". The Act held (Chap. 67:01, a 2008 scan) predates the
change: grade B (official guide). Withholding on payments to non-residents not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** Income Tax Act Chap. 67:01 s. 57: every person paying a non-resident deducts tax as the Third Schedule says; para 1 lists (a) dividends, (b) interest, (e) royalties (licence and branding fees, Act 6 of 2018), (f) management charges, (g) commissions or fees, (j) professional services (Act 6 of 2018); para 3 as substituted by Act 15 of 2007 s. 5: 15 % of every dollar, final liability. Grade A (consolidation scan and the amending Acts read; Acts of 2020-2023 checked: no change).
-/

namespace DmGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon DmGlobal

def regime : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 2500 }

def citStatute : String := "Income Tax Act Chap. 67:01 (as amended); IRD 'Current income tax rates': 'Effective 1st January 2016 ... company ... at 25%'"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1500, statute := "ITA Chap. 67:01 s. 57 and Third Sched. para 1 (Act 6 of 2018 s. 17) and para 3 as substituted by Act 15 of 2007 s. 5: 15 % of every dollar, final" }, { kind := .interest, rateBp := 1500, statute := "ITA Chap. 67:01 s. 57 and Third Sched. para 1 (Act 6 of 2018 s. 17) and para 3 as substituted by Act 15 of 2007 s. 5: 15 % of every dollar, final" }, { kind := .royalty, rateBp := 1500, statute := "ITA Chap. 67:01 s. 57 and Third Sched. para 1 (Act 6 of 2018 s. 17) and para 3 as substituted by Act 15 of 2007 s. 5: 15 % of every dollar, final" }, { kind := .services, rateBp := 1500, statute := "ITA Chap. 67:01 s. 57 and Third Sched. para 1 (Act 6 of 2018 s. 17) and para 3 as substituted by Act 15 of 2007 s. 5: 15 % of every dollar, final" }] }

def citF : Family := corpFamily "1200 Income tax (companies)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "treaty rates (s. 57 (3)) and the 2015 villa exemption not modelled"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end DmGlobal.Corporate
