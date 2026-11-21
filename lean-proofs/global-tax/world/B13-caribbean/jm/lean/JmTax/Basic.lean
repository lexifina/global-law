import TaxKernel.World

/-!
# Jamaica: income tax (PAYE) and statutory deductions of an employee, year of assessment 2025 (access B)

Sources (files in `jm/law/`):
* The Income Tax Act, Ministry of Justice consolidation (laws.moj.gov.jm, answering 503 on 2026-11-20; Internet Archive
  copy of 2025-02-04 fetched from the laptop, `ITA_moj_wayback_20250204.pdf`, 295 pages, an older scanned consolidation
  whose OCR does not hold the current threshold and rate wording). The year's amounts therefore come from the tax
  authority's own published tables (official secondary):
* Tax Administration Jamaica, "Payroll Taxes and Statutory Contributions (Employee / Employer)" (PDF created
  2025-04-29), pp. 1-2 only (the worked "Illustrations" that follow were not read): "The threshold was increase from
  $1,500,096 to $1,700,088 on April 1, 2024, and from $1,700,088 to $1,799,376 on April 1, 2025"; Table # 2 (YA 2025):
  "($1,700,088 x 3/12) 425,022", "($1,799,376 x 9/12) 1,349,532", "Effective Threshold - 2025 1,774,554"; Table #5:
  "NIS Contribution 3% ... Gross Emoluments not exceeding $5,000,000"; "NHT Contribution 2% ... Gross Emoluments";
  "Education Tax 2.25% ... Statutory Income"; "PAYE /Income Tax Up to Threshold - 0% Threshold up to $6M -25% ... $6M -
  30% ... Statutory Income"; "Statutory Income ... is the gross emoluments less all allowable deductions"; "Allowable
  deductions may include contributions to NIS, an approved pension fund".
* TAJ, "Individual Income Tax Rates, Threshold and Exemptions 2013-2028" (last updated April 2025): YA 2025 threshold
  1,774,554, age relief 250,040 (65 and over), pension relief 250,040; note: "SI in excess of ... $6M yearly ... is
  taxed at 30%".
-/

namespace JmTax
open TaxKernel

def threshold : Int := 1774554
def ageRelief : Int := 250040
def pensionRelief : Int := 250040

/-- Statutory income above the threshold at 25 %, above 6,000,000 of statutory income at 30 %. -/
def taxOf (si : Int) (relief : Int) : Int :=
  let lower := pos (min si 6000000 - relief)
  let upper := pos (si - max 6000000 relief)
  divR .down (2500 * lower + 3000 * upper) 10000

structure Person where
  nis : Int
  nht : Int
  edTax : Int
  si : Int
  tax : Int

/-- Contributions to an approved superannuation fund or approved retirement scheme are deducted in computing statutory
income (Income Tax Act s. 44A (1): "any sum paid by any person by way of contribution to an approved retirement scheme
shall ... be allowed to be deducted"; TAJ "Payroll Taxes and Statutory Contributions" (updated April 2025, law/payroll.txt
l. 45): "Allowable deductions may include contributions to NIS, an approved pension fund, an approved retirement
scheme", and its Illustrations: "Statutory Income ($480,000 - ($19,200 + $12,500))", Education Tax "2.25% of Statutory
Income"). Round D2. The Fourth Schedule's limit on deductible contributions was not read: none applied (flagged). -/
def person (a : Adult) (penContrib : Int) : Person :=
  let w := pos a.wages
  let nis := divR .down (300 * min w 5000000) 10000
  let nht := divR .down (200 * w) 10000
  let pen := pos a.pension
  let pc := min (pos penContrib) w
  let si := w + pos a.selfEmployment + pen - nis - pc
  let edTax := divR .down (225 * pos (w - nis - pc)) 10000
  let relief := threshold + (if a.age ≥ 65 then ageRelief else 0) + min pen pensionRelief
  { nis := nis, nht := nht, edTax := edTax, si := si, tax := taxOf si relief }

def out (c : Canon) : Out :=
  -- the household's pension contributions are the first adult's (contract field; one contributor)
  let ps := (c.adults.zip (List.range c.adults.length)).map fun (a, i) => person a (if i = 0 then c.pensionContributions else 0)
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends, rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed contributions not modelled"] else []) ++
    (if c.pensionContributions ≠ 0 then ["approved pension contributions deducted from the first adult's wages (s. 44A; TAJ); the Fourth Schedule limit not read, none applied"] else [])
  Out.make c "JM" "JMD" (sumInts (ps.map (·.tax)))
    (surtaxes := [("educationTax", sumInts (ps.map (·.edTax)))])
    (employeeSocial := sumInts (ps.map (fun p => p.nis + p.nht)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.si))), Out.d "nis" (sumInts (ps.map (·.nis))),
      Out.d "nht" (sumInts (ps.map (·.nht))),
      Out.dStr "note" "YA 2025 effective threshold 1,774,554 (TAJ: 1,700,088 Jan-Mar, 1,799,376 Apr-Dec); 25 % to 6M of statutory income, 30 % above; NIS 3 % to 5M, NHT 2 %, Education Tax 2.25 % (official secondary)"])
    (unsupported := unsup ++ ["amounts from TAJ tables (official secondary): the Act's current wording was not reached",
      "age limits for NIS/NHT/Education Tax not read (applied at all ages)", "annual computation with the effective threshold (PAYE is monthly)"])

/- TAJ Illustration 2 (April 2025, 480,000 a month with a 4 % pension contribution: statutory income 448,300 a month),
on a year: 5,760,000 with 230,400: NIS 150,000 (the 5,000,000 ceiling), statutory income 12 x 448,300. -/
#guard (person { age := 40, wages := 5760000 } 230400).si = 12 * 448300 ∧ (person { age := 40, wages := 5760000 } 230400).edTax = 121041

def country : Country := { code := "JM", name := "Jamaica (Income Tax Act; TAJ tables)", currency := "JMD", year := "2025", compute := out }

/-- The scale part of the tax: 25 % above the threshold (lower band) and 30 % above 6,000,000. -/
def sched : Schedule := Schedule.ofList [(0, 0), (threshold, 2500), (6000000, 3000)]
theorem sched_progressive : sched.progressive = true := by decide

/- TAJ Table # 2: 1,700,088 x 3/12 + 1,799,376 x 9/12 = 1,774,554. -/
#guard 1700088 * 3 / 12 + 1799376 * 9 / 12 = 1774554
#guard taxOf 6000000 threshold = 1056361
#guard taxOf 1774554 threshold = 0
#guard (List.range 3).all (fun i => taxOf (2000000 + i) threshold = sched.tax Rule.unitDown (2000000 + i))

end JmTax
