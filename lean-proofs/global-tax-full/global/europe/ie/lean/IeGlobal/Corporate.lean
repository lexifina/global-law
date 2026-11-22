import IeGlobal.Pit

/-!
# IE 2025: Corporation tax (1200) and withholding on payments abroad

Source: Revenue, Notes for Guidance – Taxes Consolidation Act 1997 – Finance Act 2024 Edition – Part 2 (December 2024), Internet Archive capture of 2025-10-08 (`ie/law/tca_nfg_part02.pdf`); sha256 in `law/SHA256SUMS`.
* s. 21 notes: "The standard rate of corporation tax is — ... 16 per cent for the financial year 2002, and • 12½ per cent for the financial year 2003 and each subsequent year."
* s. 21A notes: "Corporation tax is charged at the rate of 25 per cent for the financial year 2000 and" later years on income "under Case III, IV or V of Schedule D or of income of an excepted trade"


## 1200 Withholding on payments abroad (DWT, interest, patent royalties): dividend, interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Ireland, Corporate - Withholding taxes, accessed 2025-06-13 (Wayback capture; `law/pwc_wht_wb2025.txt`); Revenue TCA Notes for Guidance Part 6 and Part 8 (`ie/law/tca_nfg_part06.txt`, `ie/law/tca_nfg_part08.txt`).
* DWT 25 % on distributions from 1 January 2020; interest: s. 246 obliges companies to deduct tax at the standard rate from annual interest paid abroad; patent royalties 20 %, other royalties none
* PSWT (20 %) is deducted only where the payer is a public body (a government department, a state agency or a local authority)
-/

namespace IeGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Corporation tax",   sched := Schedule.flat 1250 }

def citStatute : String := "Taxes Consolidation Act 1997 s. 21(1) (12½ per cent for the financial year 2003 and each subsequent year); s. 21A (25 per cent on Case III, IV, V and excepted-trade income)"

/-- TCA 1997 ss. 172B, 238, 246 -/
def p8wht : Wht :=
  { name := "Withholding on payments abroad (DWT, interest, patent royalties)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "TCA 1997 s. 172B: dividend withholding tax 25 %" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "TCA 1997 s. 246 (2): income tax at the standard rate (20 %) deducted from yearly interest paid to a person whose usual place of abode is abroad" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "TCA 1997 s. 238: income tax at the standard rate (20 %) deducted from patent royalties" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "professional services withholding (TCA Part 18, ch. 1) applies only to payments by public bodies: none on a company's service fees" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Corporation tax", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Withholding on payments abroad (DWT, interest, patent royalties) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["IE 1200: Revenue Notes for Guidance, Finance Act 2024 edition (the law as amended to FA 2024, in force for 2025); the statute's own revised text not reached", "IE 1200 withholding pass 8 (dividend, interest, royalty, services): 2025-06-13; Revenue Notes for Guidance (Wayback 2025-10) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: royalties are taken as patent royalties (s. 238); other royalties bear none"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) || g.entity == .company && g.company.paymentsAbroad.any (·.kind == .interest) then ["1200 withholding: the DWT exemptions for EU/treaty companies (s. 172D) and the s. 246 (3) interest exclusions not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 12500
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 125000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end IeGlobal.Corporate
