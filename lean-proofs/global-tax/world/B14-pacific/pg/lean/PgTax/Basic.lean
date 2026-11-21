import TaxKernel.World

/-!
# Papua New Guinea: salary or wages tax on residents, 2025

Access tier A for the rate table (rescue pass 2): certified prints on the National Parliament's legislation service
(parliament.gov.pg "Acts and Legislation" -> PDIS API `pdis.parliament.gov.pg/uploads/<uuid>`; files in
`pg/law/rescue2/`, sha256 in SHA256SUMS; scans read by OCR and checked on the page images):
* Income Tax (Salary or Wages Tax)(Rates)(2024 Budget)(Amendment) Act 2023 (No. 25 of 2023 (number handwritten on the print), certified 16 Jan 2024,
  "to come into operation on 1 January 2024"), inserting Part 7 in Schedule 1 of the Income Tax (Salary or Wages Tax)
  (Rates) Act 1979: "TABLE 1. - Resident Salary and Wages Tax Rates for the period 1 January 2024 and onwards":
  "Does not exceed K20,000.00 0; exceeds K20,001.00 but does not exceed K33,000.00 30; exceeds K33,001.00 but does not
  exceed K70,000.00 35; exceeds K70,001.00 but does not exceed K250,000.00 40; exceeds K250,001.00. 42".
* Income Tax (Salary or Wages Tax)(Rates)(2025 Budget)(Amendment) Act 2024 (No. 18 of 2024, certified 13 Dec 2024, in
  operation 1 January 2025): ends Table 2 (non-residents) on 31 December 2024 and inserts Table 2A (non-residents
  from 2025: 30/35/40/42 %); adds s. 1(2A) (payments under ITA s. 46B(2A)(a) exempt) and s. 1(5) (fortnightly tables
  "issued administratively by the Commissioner General"). Table 1 (residents) is not amended, so it governs 2025.
* Income Tax (2025 Budget)(Amendment) Act 2024 (No. 16) and Income Tax (Amendment) Act 2024 (No. 23): exemptions
  (club representatives, pensions incl. judges' pensions), s. 46B, CbC penalties; nothing on the resident rates.
* Income Tax Act 2025 (certified 20 Oct 2025): "to come into operation on 1st January, 2026" (p. 5): not for 2025.
* Income Tax (Salary or Wages Tax)(Rates) Act 1979 s. 1(1) (PacLII consolidation, archived 2024-10-27; structure only):
  "the rates of tax payable on salary or wages are as set out in Schedule 1".
Reading: Table 1 is a graduated annual scale on a resident's salary or wages (the lower bounds printed as 20,001 /
33,001 / 70,001 / 250,001 leave one-kina gaps; read as the excess over 20,000 / 33,000 / 70,000 / 250,000). The
Table has no dependant column (the dependant notes of Schedule 1 belong to the earlier Tables A-C). Salary or wages
tax on a salary-only resident is final (ITA 1959 s. 65J). Whole kina, down.
-/

namespace PgTax
open TaxKernel

/-- Part 7, Table 1 (2024 Budget amendment), annual kina. -/
def table1 : Schedule := Schedule.ofList [(0, 0), (20000, 3000), (33000, 3500), (70000, 4000), (250000, 4200)]

def swt (wages : Int) : Int := table1.tax Rule.unitDown (pos wages)

-- The table's own bands: tax at each printed upper bound.
#guard swt 20000 = 0
#guard swt 33000 = 13000 * 30 / 100
#guard swt 70000 = 13000 * 30 / 100 + 37000 * 35 / 100
#guard swt 250000 = 13000 * 30 / 100 + 37000 * 35 / 100 + 180000 * 40 / 100
#guard swt 250001 = 3900 + 12950 + 72000 + 0

def out (c : Canon) : Out :=
  let t := sumInts (c.adults.map fun a => swt a.wages)
  Out.make c "PG" "PGK" t (employeeSocial := 0)
    (detail := [Out.d "salaryOrWagesTax" t,
      Out.dStr "note" "Income Tax (Salary or Wages Tax)(Rates) Act 1979 Sch. 1 Part 7 Table 1 (2024 Budget amendment, unchanged for residents by the 2025 Budget amendment); individual; final for salary-only residents"])
    (unsupported := ["superannuation employee contribution (Superannuation (General Provisions) Act): not read; employeeSocial = 0"] ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) ∨ c.interest ≠ 0 ∨ c.dividends ≠ 0 ∨ c.rentalIncome ≠ 0 ∨ c.capitalGains ≠ 0 then
        ["non-salary income: the resident general rates (Income Tax, Dividend (Withholding) Tax and Interest (Withholding) Tax Rates Act, Schedule 1) not read"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exemptions of ITA s. 29 not modelled"] else []))

def country : Country := { code := "PG", name := "Papua New Guinea", currency := "PGK", year := "2025", compute := out }

theorem table1_progressive : table1.progressive = true := by decide

end PgTax
