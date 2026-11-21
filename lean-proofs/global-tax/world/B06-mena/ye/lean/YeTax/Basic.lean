import TaxKernel.World

/-!
# Yemen: Income Tax Law No. 17 of 2010 (payroll tax and resident natural persons), 2025

Authority modelled: the Tax Authority whose site is `tax.gov.ye` (seat Sana'a; it publishes Law No. 8 of 2020 issued
"بالعاصمة صنعاء" by the Supreme Political Council). The internationally recognised government (Aden) applies Law
17/2010 too; no amendment of arts. 62 or 67 by either authority was found (the Sana'a site lists Law 8/2020 as the
only amending law of the income tax law). Text read: the authority's English translation of Law 17/2010
(`tax.gov.ye/images/portfolio/tax/files/incometax/17-en.pdf`, sha256 f15a682277cc…); the Arabic original was not found
on the site (access B).
* Art. 62: resident natural persons, on the annual proceeds subject to the commercial and industrial profits tax, the
  non-commercial professions tax and the salary and wages tax: "120,000 Riyal  The annual exemption limit / The next
  120,000 Riyal 10% / The next 600,000 15% / Any amount in excess of YR 840,000 20%".
* Art. 67: payroll tax "determined monthly on the total net monthly income … at a rate of 1/12 of the rates described
  in Article (62)" (read as the bands divided by 12).
* Art. 49 (a): pension premiums excluded from taxable pay (rate not read: not modelled); art. 50 (d): "Pension and
  Severance allowances" exempt.
* Art. 66: other payments (bonuses, overtime, commissions) 15 % flat: not in the household (all pay is salary).
* Law 8/2020 (Sana'a) art. 1, new art. 160 (ج) ثانياً: pay of employees of small and micro enterprises exempt: not
  modelled (employer size is not in the household; flagged).
Unit: individual; each category of income taxed on its own (schedular).
-/

namespace YeTax
open TaxKernel

/-- Art. 62 (annual bands, bp). -/
def sched : Schedule := Schedule.ofList [(0, 0), (120000, 1000), (240000, 1500), (840000, 2000)]

/-- Art. 67: the monthly payroll bands (art. 62 / 12). -/
def monthly : Schedule := Schedule.ofList [(0, 0), (10000, 1000), (20000, 1500), (70000, 2000)]

def payrollTax (annual : Int) : Int := perPeriod 12 (fun m => monthly.tax Rule.unitDown (pos m)) (pos annual)

def profitsTax (p : Int) : Int := sched.tax Rule.unitDown (pos p)

def out (c : Canon) : Out :=
  let pay := sumInts (c.adults.map fun a => payrollTax a.wages)
  let prof := sumInts (c.adults.map fun a => profitsTax a.selfEmployment)
  Out.make c "YE" "YER" (pay + prof)
    (detail := [Out.d "payrollTax" pay, Out.d "profitsTax" prof, Out.d "taxableIncome" (sumInts (c.adults.map (·.earnings)))])
    (unsupported := ["employee pension contributions (art. 49 (a)) not modelled and not excluded",
      "Law 8/2020 (Sana'a) exemption of employees of small/micro enterprises not modelled",
      "real-estate revenue tax, interest and dividends not modelled; pensions exempt (art. 50 (d))"])

def country : Country :=
  { code := "YE", name := "Yemen (Income Tax Law 17/2010)", currency := "YER", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Art. 62's bands: 240,000 → 12,000; 840,000 → 102,000; 1,000,000 → 134,000. Art. 67: twelve months at 1/12 give
   the annual figure for even pay. -/
#guard profitsTax 240000 = 12000 ∧ profitsTax 840000 = 102000 ∧ profitsTax 1000000 = 134000
#guard payrollTax 840000 = 102000 ∧ payrollTax 1200000 = profitsTax 1200000

end YeTax
