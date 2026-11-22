import TaxKernel.World

/-!
# Marshall Islands: tax on wages and salaries, Income Tax Act 1989 (48 MIRC Ch. 1) Part II, calendar year 2025

Sources (official: Nitijela, rmiparliament.org; files in `mh/law/`):
* Income Tax Act 1989, consolidation `1989-0050_5.pdf` ("Amended By: ... P.L. 2022-44 P.L. 2024-14 P.L. 2025-34"),
  § 103(1) as it now stands: "a tax of eight percent (8%) upon the first $10,400, to be prorated at $200 per week, or
  $866.67 per month, and twelve percent (12%) upon the amount over $10,400 as prorated by pay period"; (2) 5 % for
  United States contractor personnel; (3) "Every employee whose gross annual wages and salaries are $8,320 or less
  shall be allowed an exemption ... The exemption shall be allowed by pro-rated the salary at $160 per week or $693.33
  per month. Any who earns more than $160 per week or $693.33 per month shall not be entitled to an exemption. Any
  employee who holds two (2) or more jobs shall be entitled to only one exemption."
* Income Tax (Amendment) Act 2024, P.L. 2024-14 (scan `2024-0014A.pdf`, OCR checked on the page images): § 103(1)
  "eight percent (8%) upon the first $15,600.00 to be pro-rated at $300.00 per week, or $1,300.00 per month, twelve
  percent (12%) upon the next $10,400.00 and sixteen percent (16%) upon the amount over $26,000 as prorated by pay
  period"; "§103. Transitional Provision. There shall be a seven (7) months period for the implementation process to
  commence after the effective date."; "§104. ... take effect on the date of certification"; certified "8th day of
  October 2024" (passed 26 September 2024).
* Income Tax (Amendment) Act 2025, P.L. 2025-34 (scan `2025-0034A.pdf`): restores § 103(1) to 8 % on the first
  $10,400 ($866.67 a month) and 12 % above; "§103. Effective Date. This Act shall take effect on October 1, 2025";
  passed 18 February 2025, certified 25 September 2025.
  So 2025 has two schedules. Reading switch `mhReading`: "certification" (default: the 2024 schedule governs pay
  periods from its certification, i.e. January-September 2025) or "implementation" (the seven-month implementation
  period delays it to May 2025: January-April and October-December under the 8/12 schedule, May-September under the
  2024 schedule).
* Social Security Act of 1990 (49 MIRC Ch. 1), consolidation `1990-0075_6.pdf`: § 129(1)(d) worker's contribution
  "from March 6, 2017, and thereafter 8%" of covered earnings; § 102(k) "'Covered Earnings' means the worker's ...
  gross earnings during any quarter prior to March 6, 2017 and thereafter for new retirees ten thousand dollars
  (US$10,000)" (garbled; read as a ceiling of $10,000 a quarter, switch `mhSSCap: "none"`); § 132(1) refunds
  contributions "on earnings in excess of the covered earnings, whether from one (1) or more employers".
-/

namespace MhTax
open TaxKernel

/-- Monthly bands in cents. The 8/12 schedule of § 103(1) (1989 text, restored by P.L. 2025-34 from 1 October 2025). -/
def schedOld : Schedule := Schedule.ofList [(0, 800), (86667, 1200)]
/-- P.L. 2024-14: 8 % to $1,300 a month, 12 % on the next $10,400 a year ($866.67 a month), 16 % above $26,000 a year
    ($2,166.67 a month). -/
def sched2024 : Schedule := Schedule.ofList [(0, 800), (130000, 1200), (216667, 1600)]
/-- § 103(3): exemption at or below $693.33 a month. -/
def exemptMonthCents : Int := 69333
def usContractorRate : Int := 500
def ssRate : Int := 800
def ssQuarterCap : Int := 10000

/-- Which schedule governs month `m` (1..12) of 2025. -/
def is2024Month (reading : String) (m : Nat) : Bool :=
  if reading == "implementation" then decide (5 ≤ m ∧ m ≤ 9) else decide (m ≤ 9)

/-- Wage tax for one month in cents. -/
def monthTaxCents (reading : String) (m : Nat) (c : Int) : Int :=
  if c ≤ exemptMonthCents then 0
  else divR .down ((if is2024Month reading m then sched2024 else schedOld).ticks c) BP

/-- Annual tax for wages paid evenly over the twelve months of 2025 (the tax is withheld per pay period: § 104). -/
def wageTax (reading : String) (w : Int) : Int :=
  if w ≤ 0 then 0 else
  let mc := divR .down (w * 100) 12
  divR .down (((List.range 12).map (fun i => monthTaxCents reading (i + 1) mc)).foldl (· + ·) 0) 100

def ssEmployee (cap : Bool) (w : Int) : Int :=
  divR .down (ssRate * (if cap then min (pos w) (4 * ssQuarterCap) else pos w)) BP

structure Person where
  wages : Int
  tax : Int
  ss : Int

def person (reading : String) (usc cap : Bool) (a : Adult) : Person :=
  let w := pos a.wages
  { wages := w, tax := if usc then divR .down (usContractorRate * w) BP else wageTax reading w, ss := ssEmployee cap w }

def out (c : Canon) : Out :=
  let reading := (c.str? "mhReading").getD "certification"
  let usc := (c.bool? "mhUSContractor").getD false
  let cap := (c.str? "mhSSCap").getD "quarter" != "none"
  let ps := c.adults.map (person reading usc cap)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment: gross revenue tax (§ 109) and Net Profit Act 2025 not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rent: tax on income from immovable property (§ 116) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.capitalGains ≠ 0 then ["interest, dividends, gains: not taxed by Part II (wages and salaries); other Parts not modelled"] else [])
  Out.make c "MH" "USD" (sumInts (ps.map (·.tax)))
    (employeeSocial := sumInts (ps.map (·.ss)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.wages))), Out.d "socialSecurityEmployee" (sumInts (ps.map (·.ss))),
      Out.dStr "reading" reading,
      Out.dStr "note" "monthly wage tax: P.L. 2024-14 schedule (8/12/16 %) then P.L. 2025-34 (8/12 %) from 1 October 2025; all-or-nothing exemption at or below $693.33 a month; social security 8 %"])
    (unsupported := unsup ++ ["wages paid monthly and evenly; one job per person (§ 103(3) allows one exemption for two or more jobs)",
      "§ 103 dates: the 2024 schedule from its certification (default) or after the seven-month implementation period (mhReading = implementation)"])

def country : Country := { code := "MH", name := "Marshall Islands (Income Tax Act 1989)", currency := "USD", year := "2025", compute := out }

theorem schedOld_progressive : schedOld.progressive = true := by decide
theorem sched2024_progressive : sched2024.progressive = true := by decide

/- § 103(3) cliff: $693.33 a month pays nothing; one cent more pays 8 % of the whole $693.34 = $55.47 a month. -/
#guard monthTaxCents "certification" 10 69333 = 0
#guard monthTaxCents "certification" 10 69334 = 5546
/- Under the 2024 schedule $2,000 a month pays 8 % of 1,300 + 12 % of 700 = 104 + 84 = 188 a month; under the 8/12
   schedule 8 % of 866.67 + 12 % of 1,133.33 = 69.33 + 136.00 = 205.33. -/
#guard monthTaxCents "certification" 1 200000 = 18800
#guard monthTaxCents "certification" 10 200000 = 20533
/- $24,000 a year: 9 x 188 + 3 x 205.33 = 2,307.99 (certification); 4 x 205.33 + 5 x 188 + 3 x 205.33 = 2,377.31. -/
#guard wageTax "certification" 24000 = 2307
#guard wageTax "implementation" 24000 = 2377
#guard ssEmployee true 50000 = 3200

end MhTax
