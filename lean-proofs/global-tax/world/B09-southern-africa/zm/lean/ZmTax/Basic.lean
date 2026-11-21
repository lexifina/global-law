import TaxKernel.World

/-!
# Zambia: income tax on individuals, charge year 2025 (1 January - 31 December 2025)

Access tier B: the rate bands are statute (amending Acts read in full), but the consolidated Income Tax Act (Cap. 323)
and the contribution regulations were not reached (ZambiaLII document pages answer a Cloudflare challenge to every
host; only its search API answers). Sources, National Assembly of Zambia (parliament.gov.zm/acts-of-parliament, PDFs
fetched from the laptop 2026-11-20, sha256 in `zm/law/SHA256SUMS`):
* Income Tax (Amendment) Act No. 22 of 2023, s. 1 (2): "This Act shall come into operation on 1st January, 2024";
  s. 11 (a): Charging Schedule para 2 (1) item (c) "sixty-one thousand two hundred Kwacha"; (d) "on the balance of so
  much of an individual's income as exceeds sixty-one thousand two hundred Kwacha but does not exceed eighty-five
  thousand two hundred Kwacha, at the rate of twenty percent per annum"; (e) "... exceeds eighty-five thousand two
  hundred Kwacha but does not exceed one hundred and ten thousand four hundred Kwacha, at the rate of thirty percent";
  (f) "... exceeds one hundred and ten thousand four hundred Kwacha, at the rate of thirty-seven percent per annum".
* Item (c) is the zero-rate band: Income Tax (Amendment) Act 1 of 2008 refers to "zero per centum per annum as set out
  in clause (c) of subparagraph (1) of paragraph 2 of the Charging Schedule" (ZambiaLII search snippet, page 7).
* Income Tax (Amendment) Act No. 22 of 2024 (in operation 1 January 2025): amends para 5-7 (turnover on letting, gaming,
  WHT) but not para 2 (1): the 2024 bands apply to 2025. Act No. 10 of 2025 (assent 8 August 2025: minimum
  alternative tax s. 14A, 1 % of turnover; WHT on non-resident interest 20 %) does not touch para 2. Act No. 17 of
  2025 comes into operation on 1 January 2026.
Contributions: National Pension Scheme Act 1996 (Cap. 256) with the Pensionable Earnings Regulations (SI 22 of 2000:
"calculated at ten per centum of pensionable [earnings]", search snippet only; the employee share and the 2025 ceiling
not reached) and National Health Insurance Act 2018 s. 15 (1): "an employee's contribution consisting of the
employer's contribution and the employee's contribution at a prescribed percentage" (SI 63 of 2019 not reached).
W5 pattern A (2026-11-20): NAPSA employee contribution modelled from the NAPSA public notice "Revision in Contribution
Ceiling for the Year 2025" (7 January 2025; Internet Archive copy of napsa.co.zm, `zm/law/w5/`): "the maximum monthly
deductible employee's contribution amount for the year 2025 has been revised to ZMW1,708.20 and correspondingly, the
maximum monthly payable employee and employer statutory contribution amount has moved to ZMW3,416.40 ... The NAE
figure for 2025 has increased to ZMW8,541.00 ... The contribution rate, however, remains unchanged at 10 percent of an
employee's monthly gross earnings" (half each: NAPSA contributions page "Employee: 5% of gross earnings"). Ceiling
ZMW 34,164 a month (1,708.20 / 5 % = 4 x NAE 8,541). Its income-tax deductibility (ITA s. 37 and the Charging Schedule
in the consolidated Act) was not reached: no deduction (unchanged). NHIMA (Act 2018 s. 15 (1), "prescribed percentage")
stays unsupported: SI 63 of 2019 was reached only as a truncated scan (Internet Archive copy cut at 1 MiB; NHIMA site
404; ZambiaLII Cloudflare). Input `"w5Contrib": false` drops NAPSA.
Unit: individual (para 2 (1) charges "an individual's income").
-/

namespace ZmTax
open TaxKernel

/-- Charging Schedule para 2 (1) (c)-(f) as amended by Act 22 of 2023 (charge years 2024 and 2025). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (61200, 2000), (85200, 3000), (110400, 3700)]

/-- NAPSA employee share: 5 % (500 bp) of gross earnings up to ZMW 34,164 a month (2025 notice), annual base. -/
def napsa : Contribution := Contribution.flatCapped "NAPSA" 500 (34164 * 12)

#guard napsa.amount (34164 * 12) = 20498   -- 12 x 1,708.20 (the notice's monthly maximum), whole kwacha down
#guard napsa.amount 600000 = 20498
#guard napsa.amount 100000 = 5000

def personTax (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

#guard personTax 61200 = 0 ∧ personTax 85200 = 4800 ∧ personTax 110400 = 4800 + 7560

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let tis := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    pos (a.wages + a.selfEmployment + a.pension + share c.rentalIncome i)
  let it := sumInts (tis.map personTax)
  let w5 := (c.bool? "w5Contrib").getD true
  let np := if w5 then sumInts (c.adults.map fun a => napsa.amount a.wages) else 0
  Out.make c "ZM" "ZMW" it (employeeSocial := np)
    (detail := [Out.d "napsa" np, Out.d "taxableIncome" (sumInts tis), Out.d "taxBeforeCredits" it,
      Out.dStr "note" "Charging Schedule para 2 (1) (c)-(f) as amended by Act 22 of 2023 (unchanged for 2025 by Acts 22/2024 and 10/2025)"])
    (unsupported := (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["interest and dividends: withholding rates and Second Schedule exemptions in the consolidated Act were not reached"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: property transfer tax regime not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["approved fund deduction (s. 37) amount not reached"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income is charged by turnover tax (para 5 (e): 0 % to K12 000, 4 % to K800 000, 16 % above, Act 22/2024); the model puts it in the income bands"] else []) ++
      ["NHIMA health contribution: rate in SI 63 of 2019 not reached; NAPSA's income-tax deductibility (ITA s. 37) not reached (no deduction)",
       "Charging Schedule para 2 (1) items (a)-(b) not read (consolidated Act not reached)"])

def country : Country := { code := "ZM", name := "Zambia (charge year 2025)", currency := "ZMW", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end ZmTax
