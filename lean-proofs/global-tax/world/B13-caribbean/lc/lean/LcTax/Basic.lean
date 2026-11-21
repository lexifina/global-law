import TaxKernel.World

/-!
# Saint Lucia: income tax of a resident individual and the employee's NIC contribution, income year 2025

Sources: Revised Laws of Saint Lucia (2023), "Showing the law as at 31 December 2023", Attorney General's Chambers
(attorneygeneralchambers.com/laws-of-saint-lucia; the publisher Global law names; files in `lc/law/`):
* Income Tax Act Cap. 15.02:
  - s. 13: "Any income accrued to a married woman ... shall be charged to tax in her own name".
  - s. 45 and Schedule 6: personal allowance "2023 | $ 25,000 effective 1 January, 2023" (Act 21 of 2022).
  - s. 46: spouse allowance "$1,500 in respect of his or her spouse", "reduced where the spouse has assessable income in
    excess of $1,500 by $1 for each dollar of the excess".
  - s. 53(1)(b), (2): deduction of "contributions under the National Insurance Corporation Act" (with life premiums)
    not exceeding "the lower of (a) one-tenth of his or her assessable income; or (b) eight thousand dollars".
  - s. 80(1) and Schedule 5 para. 1 (Act 21 of 2022): "2023 | On the first $15,000 and under | 15% | On the next $15,000
    viz. 15,001 - 30,000 | 20% | On the remainder | 30%" (the latest row: it applies to 2025).
* National Insurance Corporation Act Cap. 16.01: s. 28(2), Schedule 2: "the employer's and employee's contribution
  shall each be 5% of the total salary or wages"; s. 29, Schedule 3 para. 1: employees "whose remuneration is in excess
  of $60,000 per annum ... are exempted in respect of that portion in excess of $60,000 or such other limit" fixed under
  s. 30(d) (no regulation fixing another limit is in the revision); s. 27(1)(a),(b): persons under 16 or over 60 are
  insured only by regulations.
No Act after the 2023 revision was reached (FINDINGS: the 2024-2025 Acts were not checked).
-/

namespace LcTax
open TaxKernel

/-- Schedule 5 para. 1 (income year 2023 row). -/
def sched : Schedule := Schedule.ofList [(0, 1500), (15000, 2000), (30000, 3000)]

def nicAnnual (age : Nat) (w : Int) : Int := if age ≥ 16 && age < 60 then divR .down (500 * min (pos w) 60000) 10000 else 0

structure Person where
  nic : Int
  chargeable : Int
  tax : Int

/-- Schedule 6 (s. 45): personal allowance "2023 | $ 25,000 effective 1 January, 2023" (Act 21 of 2022). -/
def personalAllowance : Int := 25000

/-- IRD convention (`--ird-code`, rule 8: the authority's published method): IRD Saint Lucia's PAYE calculator
(irdstlucia.gov.lc/payecalculator, saved as law/d7/ird_paye_calculator_page.html, sha256 23b3acad...) computes
"const allowance = digits * 100" from the PAYE tax code, whose default is "254M", with the note "the allowance code itself
changed alongside the rate change (184M -> 254M)": the IRD's codes carry 400 above the Schedule 6 allowance in both
periods (18,000 -> 184; 25,000 -> 254). No provision for the extra 400 was found in the Act (Revised Edition 2023, ss.
44-59, Schedule 6). Round D7. -/
def irdCodeAllowance : Int := 25400

def person (allowance : Int) (a : Adult) (spouseInc : Option Int) : Person :=
  let w := pos a.wages
  let nic := nicAnnual a.age w
  let assessable := w + pos a.selfEmployment + pos a.pension
  let s53 := min nic (min 8000 (assessable / 10))
  let spouse := match spouseInc with
    | some si => pos (1500 - pos (si - 1500))
    | none => 0
  let chargeable := pos (assessable - allowance - spouse - s53)
  { nic := nic, chargeable := chargeable, tax := sched.tax Rule.unitDown chargeable }

def out (args : List String) (c : Canon) : Out :=
  let allow := if args.contains "--ird-code" then irdCodeAllowance else personalAllowance
  let person := person allow
  let inc (a : Adult) : Int := pos a.wages + pos a.selfEmployment + pos a.pension
  let ps : List Person :=
    match c.adults with
    | [a, b] =>
      if c.married then
        -- s. 46: one spouse claims; the model gives it to the higher earner (the allowance is the same either way)
        if inc a ≥ inc b then [person a (some (inc b)), person b none] else [person a none, person b (some (inc a))]
      else [person a none, person b none]
    | l => l.map (fun a => person a none)
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends, rents and gains not modelled"] else []) ++
    (if c.children.length > 0 then ["child maintenance/education deductions (ss. 48-50) need inputs: not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed NIC not modelled"] else [])
  Out.make c "LC" "XCD" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.nic)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "nic" (sumInts (ps.map (·.nic))),
      Out.dStr "note" "individual taxation (s. 13); allowance 25,000 (Sch. 6), spouse 1,500 tapered (s. 46); NIC 5 % to 60,000 deductible up to min(10 %, 8,000) (s. 53); 15/20/30 % (Sch. 5, 2023 row)"])
    (unsupported := unsup ++ ["law as at 31 December 2023 (Revised Edition); later Acts not reached", "mortgage interest and home deductions (s. 54) need inputs"])

def country : Country :=
  { code := "LC", name := "Saint Lucia (Income Tax Act Cap. 15.02, Revised Edition 2023)", currency := "XCD", year := "2025", compute := out [], computeWith := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 15000 = 2250
#guard sched.tax Rule.unitDown 30000 = 5250
#guard nicAnnual 40 100000 = 3000
/- The IRD code's extra 400 costs 60 / 80 / 120 of tax in the 15 / 20 / 30 % bands. -/
#guard (person personalAllowance { age := 40, wages := 60000 } none).tax - (person irdCodeAllowance { age := 40, wages := 60000 } none).tax = 120

end LcTax
