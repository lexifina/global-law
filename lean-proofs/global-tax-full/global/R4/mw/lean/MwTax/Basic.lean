import TaxKernel.World

/-!
# Malawi: income tax on individuals, rates in force from 30 December 2025 (Taxation (Amendment) (No. 2) Act 36 of 2025)

Access tier B, and **only the end of 2025 is covered**: the rates that applied before 30 December 2025 (Taxation
(Amendment) Act 2024 / Bill 2024, Gazette Notice B No. 3 of 22 March 2024) were not reached. MalawiLII (the Act 36 of
2025 text, the Taxation Act Cap. 41:01 consolidated to 2014) answers a Cloudflare challenge to every host; only its
search API answers (excerpts: "The principal Act is amended, in the Eleventh Schedule — (a) under paragraph (c)(ii)
..."; Act 36 of 2025 "(Published 30th December, 2025)"). Amounts are therefore the Malawi Revenue Authority's public
notice, official secondary (mra.mw download "NEW TAX MEASURES UNDER AMENDED TAXATION AND VALUE ADDED TAX LAWS March
2026", sha256 07af8860..., in `mw/law/`):
* "the Taxation (Amendment) and Value Added Tax (Amendment) (No.2) Acts 2025, introduced the following income tax and
  valued added tax measures, with effect from 30th December 2025".
* "V. Personal Income Tax Rates ... First K2,040,000 0% / Excess of K2,040,000 30%".
* "VI. Pay As You Earn (PAYE) Rates. Rates of income tax on employment income ... K2,040,000 First K170,000 0%; Next
  K16,800,000 Next K1,400,000 30%; Next K101,160,000 Next K8,430,000 35%; Excess over K120,000,000 Excess over
  10,000,000 40%".
* "III. ... all gains from sales of shares are now subject to income tax regardless of the holding period."
The model applies the PAYE (employment) schedule to wages and pensions and the "personal income tax" schedule to other
income of the individual, each on its own (how the two schedules combine for a person with both kinds of income is not
said in the notice: unsupported). Unit: individual.
W5 pattern A (2026-11-20): Pension Act No. 6 of 2023 (published 10 February 2023; gazette text as hosted by
businessmalawi.com, `mw/law/w5/`), s. 12 (1): "contributions relating to pensionable emoluments for an employee shall,
under the mandatory occupational pension scheme, be made in the following manner__ (a) a minimum of ten per cent by
the employer; and (b) a minimum of five per cent by the employee"; s. 2 "pensionable emoluments" means "any guaranteed
wages and other earnings, but does not include personal investment income or capital gains or provision from an
employer in the form of a house or a motor vehicle". No ceiling or floor in the Act. Modelled: 5 % of wages (the
statutory minimum; s. 12 (3) allows more by agreement; s. 11 exemption orders not reached). Its income-tax treatment
(Taxation Act Cap. 41:01, not reached: MalawiLII Cloudflare) is not applied: no deduction. Input `"w5Contrib": false`
drops it.
-/

namespace MwTax
open TaxKernel

/-- PAYE rates on employment income from 30 December 2025 (MRA notice, item VI), annual column. -/
def empSched : Schedule := Schedule.ofList [(0, 0), (2040000, 3000), (18840000, 3500), (120000000, 4000)]
/-- Personal income tax rates (item V). -/
def persSched : Schedule := Schedule.ofList [(0, 0), (2040000, 3000)]

/- The monthly column is the annual one divided by 12 (170 000, 1 400 000, 8 430 000; 10 000 000). -/
#guard 2040000 / 12 = 170000 ∧ 16800000 / 12 = 1400000 ∧ 101160000 / 12 = 8430000 ∧ 120000000 / 12 = 10000000
#guard 2040000 + 16800000 + 101160000 = 120000000

def empTax (x : Int) : Int := empSched.tax Rule.unitDown (pos x)
def persTax (x : Int) : Int := persSched.tax Rule.unitDown (pos x)

/-- Pension Act 2023 s. 12 (1) (b): employee minimum 5 % of pensionable emoluments (no ceiling). -/
def pensionEmployee : Contribution := Contribution.flatCapped "pension" 500 (-1)

#guard pensionEmployee.amount 2040000 = 102000 ∧ pensionEmployee.amount 120000000 = 6000000

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let parts := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    (empTax (a.wages + a.pension), persTax (a.selfEmployment + share c.rentalIncome i + share c.capitalGains i))
  let it := sumInts (parts.map fun p => p.1 + p.2)
  let w5 := (c.bool? "w5Contrib").getD true
  let pen := if w5 then sumInts (c.adults.map fun a => pensionEmployee.amount a.wages) else 0
  Out.make c "MW" "MWK" it (employeeSocial := pen)
    (detail := [Out.d "pensionActEmployee" pen, Out.d "taxBeforeCredits" it, Out.d "employmentTax" (sumInts (parts.map (·.1))),
      Out.dStr "note" "rates in force from 30 Dec 2025 (Act 36 of 2025), MRA public notice (official secondary); earlier 2025 rates not reached"])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["withholding taxes on interest and dividends: rates not reached"] else []) ++
      ["rates before 30 December 2025 (the larger part of 2025) not reached: the model gives the rates in force from 30 December 2025",
       "combination of the PAYE and personal schedules for a person with both employment and other income not stated in the source",
       "income-tax treatment of the Pension Act 2023 s. 12 employee contribution (Taxation Act not reached): not deducted"])

def country : Country := { code := "MW", name := "Malawi (rates from 30 Dec 2025)", currency := "MWK", year := "2025", compute := out }

theorem empSched_progressive : empSched.progressive = true := by decide
theorem sched_progressive : persSched.progressive = true := by decide
def sched : Schedule := empSched

end MwTax
