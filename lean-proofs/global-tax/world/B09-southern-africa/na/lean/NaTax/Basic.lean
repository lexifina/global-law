import TaxKernel.World

/-!
# Namibia: normal tax on individuals, year of assessment ending 28 February 2026 (1 March 2025 - 28 February 2026)

Access tier A for the income tax (statute and the year's amounts in the Act itself), contributions official secondary.
Source: Income Tax Act 24 of 1981 as in force on 2025-06-30 (Global law `namibia/national/acts/income-tax`, publisher
NamibLII, consolidation eng@2024-09-16 = Income Tax Amendment Act 4 of 2024, GG 8442 of 16 September 2024, commenced
13 September 2024; read from the archived official page web.archive.org/web/20260212092155id_/https://namiblii.org/akn/na/act/1981/24/eng@2024-09-16).
No Income Tax amendment act among Namibia's 2025 acts (NamibLII acts 2025/1-5: student fund, appropriation, judiciary,
roads, appropriation amendment; Wayback CDX of namiblii.org/akn/na/act/2025/, 2026-11-20).
* s. 5 (1) (a): normal tax "in respect of the taxable income received by or accrued to ... any person other than a
  company during the year of assessment ending on the last day of February".
* s. 6: "The rates of normal tax chargeable in respect of taxable income ... shall be as set out in Schedule 4."
* Sch. 4 para 1 (substituted by s. 6 of Act 4 of 2024): "(a) does not exceed N$100 000 no tax payable; (b) ... 18 per
  cent of the amount by which the taxable amount exceeds N$100 000; (c) ... N$9 000 plus 25 per cent ... exceeds
  N$150 000; (d) N$59 000 plus 28 per cent ... N$350 000; (e) N$115 000 plus 30 per cent ... N$550 000; (f) N$205 000
  plus 32 per cent ... N$850 000; (g) exceeds N$1 550 000 N$429 000 plus 37 per cent".
* s. 1 "gross income": "from a source within or deemed to be within Namibia, excluding receipts or accruals of a
  capital nature" (source basis; no capital gains tax on individuals).
* s. 16 (1) (n) (i): exempt "dividends received by or accrued to or in favour of any taxpayer" (subject to s. 42,
  non-resident shareholders' tax, which does not reach residents).
* s. 34A (1)-(2): "withholding tax on interest ... equal to 10 per cent of any amount of interest ... from a banking
  institution ... or a unit trust scheme"; "a final tax as the interest on which it is paid is not added to or set-off
  against any other income". The contract's `interest` is read as bank / unit-trust interest.
* s. 17 (1) (n) (i), (q) and s. 17 (2): pension / provident fund and retirement annuity contributions deductible, together
  with (qA) and (w) not to "exceed the sum of N$150 000" a year.
* s. 58 (1)-(2) deleted by Act 25 of 1992: spouses are taxed separately (no aggregation of a married woman's income).
* Social Security Act 34 of 1994 s. 21 (2): employer and employee liable for "the prescribed contributions" to the
  Maternity Leave, Sick Leave and Death Benefit (MSD) Fund. Social Security Commission (ssc.org.na/msd, data served
  2026-11-20): MSD from 2025-03-01 to 2026-08-31 "contributionRate 0.018, maxContributionWages 11000,
  minContributionWages 500" (monthly). W5 pattern A (2026-11-20): the split is in the Regulations made under s. 47
  (Government Notice 198 of 1995, Government Gazette 1181 of 1 November 1995, Legal Assistance Centre copy
  lac.org.na/laws/1995/1181.pdf, `na/law/w5/`), reg. 8: the MSD contributions "shall - (a) in the case of an employee,
  be equal to 0,9 per cent of his or her remuneration; (b) in the case of the employer of such employee, be equal to the
  contribution contemplated in paragraph (a)". Employee share = 0.9 % of monthly remuneration in the SSC's N$500-11 000
  band. Not deductible: s. 17 (1) allows pension, provident and retirement annuity fund contributions, not SSC
  contributions. Input `"w5Contrib": false` drops it.
-/

namespace NaTax
open TaxKernel

/-- Sch. 4 para 1 (Act 4 of 2024). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (100000, 1800), (150000, 2500), (350000, 2800), (550000, 3000), (850000, 3200), (1550000, 3700)]

/- The printed amounts "N$9 000 / 59 000 / 115 000 / 205 000 / 429 000" equal the band sums. -/
#guard [(150000, 9000), (350000, 59000), (550000, 115000), (850000, 205000), (1550000, 429000)].all
  fun (t, base) => sched.ticks t = base * BP

def interestWhtRate : Int := 1000          -- s. 34A (1)
def retirementCap : Int := 150000          -- s. 17 (2)
/-- MSD Fund, SSC table 2025-03-01..2026-08-31: 1.8 % of monthly remuneration between N$500 and N$11 000 (combined). -/
def msdCombinedMonthly (m : Int) : Int :=
  if m < 500 then 0 else divR .halfUp (180 * min m 11000) BP

/-- Employee MSD share, GN 198/1995 reg. 8 (a): 0.9 % of monthly remuneration in the SSC band. -/
def msdEmployeeMonthly (m : Int) : Int :=
  if m < 500 then 0 else divR .halfUp (90 * min m 11000) BP

#guard msdEmployeeMonthly 11000 = 99 ∧ msdEmployeeMonthly 20000 = 99 ∧ msdEmployeeMonthly 499 = 0 ∧ msdEmployeeMonthly 500 = 5

def personTI (a : Adult) (rental retire : Int) : Int :=
  pos (a.wages + a.selfEmployment + a.pension + rental - min retire retirementCap)

def personTax (ti : Int) : Int := sched.tax Rule.unitDown (pos ti)

#guard personTax 100000 = 0 ∧ personTax 100001 = 0 ∧ personTax 150000 = 9000 ∧ personTax 1550000 = 429000

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let tis := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    personTI a (share c.rentalIncome i) (share c.pensionContributions i)
  let it := sumInts (tis.map personTax)
  let wht := divR .down (interestWhtRate * c.interest) BP
  let msd := sumInts (c.adults.map fun a => 12 * msdCombinedMonthly (divR .down a.wages 12))
  let w5 := (c.bool? "w5Contrib").getD true
  let msdEe := if w5 then sumInts (c.adults.map fun a => 12 * msdEmployeeMonthly (divR .down a.wages 12)) else 0
  Out.make c "NA" "NAD" it (surtaxes := [("interestWithholdingTax", wht)]) (employeeSocial := msdEe)
    (detail := [Out.d "taxableIncome" (sumInts tis), Out.d "taxBeforeCredits" it,
      Out.d "msdCombinedEmployerEmployee" msd, Out.d "msdEmployee" msdEe,
      Out.dStr "note" "Income Tax Act 24 of 1981 Sch. 4 (Act 4 of 2024); interest = 10 % final WHT (s. 34A); dividends exempt (s. 16 (1) (n)); capital gains outside gross income; spouses separate"])
    (unsupported := (if c.foreignIncome ≠ 0 then ["foreign-source income: outside gross income (s. 1 source rule) unless deemed Namibian (s. 15): not modelled"] else []) ++
      ["interest other than bank / unit-trust interest (s. 34A) is taxed at the Schedule 4 rates: not distinguished"])

def country : Country := { code := "NA", name := "Namibia (year of assessment ending 28 Feb 2026)", currency := "NAD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end NaTax
