import TaxKernel.World

/-!
# Philippines: income tax of resident citizens, taxable year 2025 (NIRC as amended by RA 10963, TRAIN)

Access tier A for the tax (statute). Republic Act No. 10963 is not in Global law (its Philippine corpus is as-enacted
and lacks it); officialgazette.gov.ph, elibrary.judiciary.gov.ph, congress.gov.ph and the Senate answer 403 to scripts
(not bypassed). Source: the Official Gazette's signed scan "20171219-RA-10963-RRD.pdf" as archived by the Internet
Archive on 2018-01-08 (`ph/law/ra10963.pdf`; the archived copy is truncated after 43 page images, which hold
Sections 1-10); page images extracted and OCR'd (tesseract eng), every number below checked against the page image
(OCR read "P30,000" as "P80,000" in the 2018 table):
* NIRC Sec. 24 (A) (2) (a) as amended by RA 10963 Sec. 5, "Tax Schedule Effective January 1, 2023 and onwards":
  "Not over P250,000 0%"; "Over P250,000 but not over P400,000 15% of the excess over P250,000"; "Over P400,000 but not
  over P800,000 P22,500 + 20% of the excess over P400,000"; "... P2,000,000 P102,500 + 25% ..."; "... P8,000,000
  P402,500 + 30% ..."; "Over P8,000,000 P2,202,500 + 35% of the excess over P8,000,000" (cumulative column checked).
  Spouses "shall compute separately their individual income tax"; minimum wage earners exempt.
* Sec. 24 (B) (1): final tax 20 % on bank deposit interest; (B) (2): 10 % final tax on dividends from domestic
  corporations.
* Sec. 32 (B) (7) (e): 13th-month pay and other benefits excluded up to P90,000.
W5 pattern A (2026-11-20; lawphil.net statute texts and the agencies' own issuances, `ph/law/w5/`):
* SSS: RA 11199 (Social Security Act of 2018) Sec. 4 (a) (9) schedule: "2025 | 15% | 10% | 5% | P5,000.00 |
  P35,000.00" (total, employer, member; minimum and maximum monthly salary credit); a member earning below the minimum
  or above the maximum pays on the minimum or maximum credit. Salary-credit brackets (agent 2, 2026-11-20): SSS
  Circular No. 2024-006 (19 Dec 2024, "Schedule of SSS contributions effective January 2025", per Commission
  Resolution 560-s.2024; the SSS's own table image, `ph/law/w5/`): "BELOW 5,250 | 5,000.00", "5,250 - 5,749.99 |
  5,500.00", ..., "34,750 - Over | 35,000.00", employee 250.00 ... 1,750.00 (regular SS + MPF): the credit is the
  compensation rounded to the nearest P500 (halves up), within 5,000-35,000, and the member pays 5 % of it.
* PhilHealth: RA 11223 (UHC Act) Sec. 10: "2025 | 5.00 % | P10,000.00 | P100,000.00" (rate, monthly income floor and
  ceiling); PhilHealth Advisory 2025-0002 keeps 5.0 % for 2025; Circular 2020-0005 (OCR): premium "computed straight
  based on the monthly basic salary of the employee to be equally shared between the employee and employer": employee
  2.5 % of monthly salary within 10,000-100,000.
* Pag-IBIG: RA 9679 Sec. 7: employees "earning more than ... P1,500.00 per month - two percent (2%)" (1 % at or below),
  maximum monthly compensation P5,000 "may be fixed from time to time by the Board"; raised to P10,000 from February
  2024 by HDMF Circular 460 (as stated in DBM Circular Letter 2024-2, official secondary): 2 % of at most 10,000 a month.
* Excluded from gross income: NIRC Sec. 32 (B) (7) (f) "GSIS, SSS, Medicare and Pag-ibig contributions, and union dues
  of individuals" (RA 8424 text; not amended by RA 10963).
Monthly wages = annual / 12. Input `"w5Contrib": false` drops all three and the exclusion.
Self-employment: taken as net income under the graduated rates (the 8 % gross-receipts option, Sec. 24 (A) (2) (b),
needs gross receipts).
Optional input field `"benefits13"` (whole pesos, per household, first adult): 13th-month pay and other benefits
included in wages, excluded up to P90,000.
-/

namespace PhTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 0), (250000, 1500), (400000, 2000), (800000, 2500),
  (2000000, 3000), (8000000, 3500)]

#guard [(400000, 22500), (800000, 102500), (2000000, 402500), (8000000, 2202500)].all
  fun (t, base) => sched.ticks t = base * BP

def benefitsCap : Int := 90000
def interestRate : Int := 2000
def dividendRate : Int := 1000

/-- Employee contributions on one month's compensation `m` (SSS 5 %, PhilHealth 2.5 %, Pag-IBIG 2 % / 1 %). -/
def sssMonth (m : Int) : Int := if m ≤ 0 then 0 else divR .halfUp (500 * clamp 5000 35000 (500 * ((m + 250) / 500))) BP
def philhealthMonth (m : Int) : Int := if m ≤ 0 then 0 else divR .halfUp (250 * clamp 10000 100000 m) BP
def pagibigMonth (m : Int) : Int := if m ≤ 0 then 0 else divR .halfUp ((if m ≤ 1500 then 100 else 200) * min m 10000) BP
def contribMonth (m : Int) : Int := sssMonth m + philhealthMonth m + pagibigMonth m
def contributions (wages : Int) : Int := perPeriod 12 contribMonth (pos wages)

#guard sssMonth 35000 = 1750 ∧ sssMonth 3000 = 250 ∧ philhealthMonth 100000 = 2500 ∧ philhealthMonth 5000 = 250
/- SSS Circular 2024-006 rows: 5,249 -> MSC 5,000 (250.00); 5,250 -> 5,500 (275.00); 20,249 -> 20,000 (1,000.00);
   20,250 -> 20,500 (1,025.00); 34,749 -> 34,500 (1,725.00); 34,750 -> 35,000 (1,750.00). -/
#guard sssMonth 5249 = 250 ∧ sssMonth 5250 = 275 ∧ sssMonth 20249 = 1000 ∧ sssMonth 20250 = 1025 ∧ sssMonth 34749 = 1725 ∧ sssMonth 34750 = 1750
#guard pagibigMonth 10000 = 200 ∧ pagibigMonth 50000 = 200 ∧ pagibigMonth 1500 = 15
#guard contributions 600000 = 12 * (1750 + 1250 + 200)

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let idx := List.range c.adults.length
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let ben : Int := (c.int? "benefits13").getD 0
  let rs := (c.adults.zip idx).map fun (a, i) =>
    let excl := if i = 0 then min benefitsCap (pos ben) else 0
    let ctr := if w5 then contributions a.wages else 0
    let ti := pos (pos a.wages - excl - ctr + a.selfEmployment)
    (sched.tax Rule.unitDown ti, ti, ctr)
  let fin := sumInts (idx.map fun i => divR .down (interestRate * pos (share c.interest i)) BP +
    divR .down (dividendRate * pos (share c.dividends i)) BP)
  Out.make c "PH" "PHP" (sumInts (rs.map (·.1))) (surtaxes := [("finalTaxPassiveIncome", fin)])
    (employeeSocial := sumInts (rs.map (·.2.2)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2.1))), Out.d "sssPhilhealthPagibig" (sumInts (rs.map (·.2.2))),
      Out.dStr "note" "spouses separately (Sec. 24 (A) (2)); 13th-month exclusion only via the optional benefits13 field"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) then ["SSS: compensation taken as wages / 12 each month (the circular's daily / partial-month rules not applied)"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rent: business income with deductions not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: Sec. 24 (C)/(D) final taxes need the asset and price"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exclusion conditions (Sec. 32 (B) (6)) not read"] else []))

def country : Country := { code := "PH", name := "Philippines", currency := "PHP", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end PhTax
