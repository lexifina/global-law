import UkGlobal.Pit

/-!
# UK 2025: Corporation tax (1200) and withholding on payments abroad

Source: legislation.gov.uk point in time 2025-07-01: FA 2021 ss. 6, 7; CTA 2010 ss. 18B, 18D; ITA 2007 ss. 874, 906 (`uk/law/*_2025-07-01.html`); sha256 in `law/SHA256SUMS`.
* FA 2021 s. 6: the main rate "(b) is 25% for the financial year 2023" (later years charged at the same main rate by the annual Finance Acts, not read)
* FA 2021 s. 7: "(a) the standard small profits rate is 19%, and (b) the standard marginal relief fraction is 3/200ths"
* CTA 2010 s. 18D: "(a) the lower limit is £50,000, and (b) the upper limit is £250,000"; s. 18B: relief F × (U − A) × N/A
* The marginal relief turns into a marginal schedule (no associated companies, N = A): 19 % to £50,000, 26.5 % from £50,000 to £250,000, 25 % above (at £250,000: 9 500 + 53 000 = 62 500 = 25 %)
* ITA 2007 s. 874 (2): deduct income tax "at the basic rate"; s. 906 the same for royalties

* **CTA 2010 Part 7ZA** (FT review 2026-11-21; legislation.gov.uk point in time 2025-07-01, `uk/law/cta2010_s269Z*_2025-07-01.html`):
  s. 269ZB (2), (5): carried-forward trade-loss deductions "may not exceed the relevant maximum", "the sum of— (a) 50% of
  the company's relevant trading profits ..., and (b) the company's trading profits deductions allowance"; s. 269ZF (1):
  relevant trading profits = qualifying trading profits "less" that allowance; s. 269ZW (2): a company not in a group has a
  "deductions allowance for the accounting period [of] £5,000,000". So losses brought forward are set off in full up to
  £5 m of profit and against 50 % of the excess (`lossFull`, `lossExcessBp`); s. 269ZD applies the same maximum to
  deductions from total profits.

## 1200 Income tax deducted at source (dividends, services): dividend, services (pass 8, grade A)
Source: Income Tax Act 2007, legislation.gov.uk table of contents (`uk/law/ita2007_contents.txt`); ss. 874, 906 already modelled (`uk/law/ita2007_s874_2025-07-01.txt`).
* Part 15 chapters: 3 yearly interest; 4 building society securities; 5 UK public revenue dividends; 6 annual payments and patent royalties; 7 other intellectual property; 9 manufactured payments; 10 non-commercial payments by companies; 18 other regimes: none on company dividends or service fees
-/

namespace UkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Corporation tax",   sched := Schedule.ofList [(0, 1900), (50000, 2650), (250000, 2500)],   lossFull := 5000000, lossExcessBp := 5000 }

def wht : Wht :=
  { name := "Income tax deducted at source (interest, royalties)", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "ITA 2007 s. 874: income tax at the basic rate (20 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "ITA 2007 s. 906: income tax at the basic rate (20 %)" }] }

def citStatute : String := "FA 2021 s. 6 (main rate 25 %), s. 7 (small profits rate 19 %, marginal relief fraction 3/200); CTA 2010 Part 3A s. 18B, 18D (£50,000 / £250,000); Part 7ZA ss. 269ZB, 269ZD, 269ZF, 269ZW (losses: £5 m + 50 %)"

/-- Income Tax Act 2007 Part 15 (Deduction of income tax at source), Chapters 3-18 -/
def p8wht2 : Wht :=
  { name := "Income tax deducted at source (dividends, services)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "ITA 2007 Part 15: no duty to deduct income tax from dividends of companies (Chapter 5 covers only UK public revenue dividends)" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "ITA 2007 Part 15: no duty to deduct income tax from service fees (chapters cover interest, building society securities, public revenue dividends, annual payments and royalties, manufactured payments)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Corporation tax", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Income tax deducted at source (dividends, services) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["UK 1200: legislation.gov.uk 2025-07-01", "UK 1200 withholding pass 8 (dividend, services): legislation.gov.uk contents fetched 2026-11-21 (`uk/law/ita2007_contents.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: the construction industry scheme (FA 2004 ss. 57-77) applies only to construction payments: not modelled"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 22750
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 250000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
-- CTA 2010 ss. 269ZB, 269ZW: £5 m allowance, then 50 % of the excess
#guard cit.taxableProfit { profit := 12000000, lossesForward := 20000000 } == 3500000
#guard cit.taxableProfit { profit := 4000000, lossesForward := 20000000 } == 0
#guard cit.taxableProfit { profit := 12000000, lossesForward := 1000000 } == 11000000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end UkGlobal.Corporate
