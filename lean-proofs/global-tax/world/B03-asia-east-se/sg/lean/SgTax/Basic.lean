import TaxKernel.World

/-!
# Singapore: income tax of resident individuals, Year of Assessment 2026 (income year 2025), and CPF

Access tier B. The Income Tax Act 1947 and the CPF Act are published on Singapore Statutes Online, which answers 403
to scripts (not bypassed; the Internet Archive copies were offline on 2026-11-20), and Global law's Singapore corpus is
empty. Every amount is therefore IRAS's or the CPF Board's own published table (official secondary; pages saved in
`sg/law/`, sha256 in `SHA256SUMS`, fetched 2026-11-20):
* IRAS "Individual Income Tax rates" (iras_rates.html), "From YA 2024 onwards": "First $20,000 0 ... Next $10,000 2 ...
  Next $10,000 3.50 ... Next $40,000 7 ... Next $40,000 11.5 ... 15 ... 18 ... 19 ... 19.5 ... 20 ... Next $180,000 22
  ... Next $500,000 23 ... In excess of $1,000,000 24"; cumulative column 200 / 550 / 3,350 / 7,950 / 13,950 / 21,150 /
  28,750 / 36,550 / 44,550 / 84,150 / 199,150 (checked by `#guard`). Rebates are listed for YA 2025 (60 %, max $200)
  and YA 2024 only: none for YA 2026.
* IRAS "Tax reliefs" (iras_tax_reliefs.html): "A personal income tax relief cap of $80,000 applies to the total amount
  of all tax reliefs claimed for each Year of Assessment".
* Earned Income Relief (iras_eir.html): age at 31 Dec of the previous year "Below 55 $1,000; 55 to 59 $6,000; 60 and
  above $8,000"; "capped at the amount of taxable earned income".
* CPF Relief (iras_cpfrelief.html): "capped by the amount of compulsory employee CPF contributions"; OW ceiling
  "1 Jan to 31 Dec 2025 $7,400" a month; example "Mr Lim is 40 years old. His compulsory employee CPF contribution rate
  is 20%" (2025).
* Spouse Relief (iras_spouse.html): $2,000 if the spouse "did not have an annual income of more than $8,000 in year
  2025"; annual income includes "tax-exempt income (e.g. bank interest, dividends and pensions)".
* Qualifying Child Relief (iras_qcr.html): "$4,000 per child" for a child below 16 (or a full-time student) with income
  not over $8,000; may be shared between the parents.
* CPF Board, "CPF Contribution Rate Table from 1 January 2026" (cpf_rates_2026.pdf): employee 55 & below: nil to $500,
  "0.6 (TW - $500)" from $500 to $750, "20% (OW)" above, "employee's share ... rounded down to the nearest dollar". The
  2025 table for ages above 55 was not reached at build time (the 2026 table differs for 55-65).
* CPF Board, "CPF Contribution Rate Table from 1 January 2025" (cpf_rates_2025.pdf, Table 1, fetched 2026-11-20 in
  round W2; the Board's schedule of the CPF Act First Schedule rates): employee's share for wages above $750 "[20%
  (OW)]" (55 & below), "[17% (OW)]" (above 55 - 60), "[11.5% (OW)]" (above 60 - 65), "[7.5% (OW)]" (above 65 - 70),
  "[5% (OW)]" (above 70); from $500 to $750 "0.6 / 0.51 / 0.345 / 0.225 / 0.15 (TW - $500)"; "OW: Ordinary Wages
  (capped at OW ceiling of $7,400)"; maxima $1,480 / $1,258 / $851 / $555 / $370; employee's share rounded down.
Unit: separate assessment of spouses. Wages are ordinary wages paid evenly over 12 months (no additional wages).
-/

namespace SgTax
open TaxKernel

/-- Resident rates from YA 2024 (IRAS table). -/
def sched : Schedule := Schedule.ofList [(0, 0), (20000, 200), (30000, 350), (40000, 700), (80000, 1150),
  (120000, 1500), (160000, 1800), (200000, 1900), (240000, 1950), (280000, 2000), (320000, 2200),
  (500000, 2300), (1000000, 2400)]

/- IRAS's printed "Gross Tax Payable" column equals the band sums (in cents of tax ticks: dollars x BP). -/
#guard [(30000, 200), (40000, 550), (80000, 3350), (120000, 7950), (160000, 13950), (200000, 21150),
  (240000, 28750), (280000, 36550), (320000, 44550), (500000, 84150), (1000000, 199150)].all
  fun (t, base) => sched.ticks t = base * BP

def reliefCap : Int := 80000
def eirMax (age : Nat) : Int := if age < 55 then 1000 else if age < 60 then 6000 else 8000
def qcrPerChild : Int := 4000
def spouseRelief : Int := 2000
def spouseIncomeLimit : Int := 8000
def owCeiling : Int := 7400

/-- CPF 2025 Table 1 age bands (employee's age; "55 & below", "Above 55 - 60", ...): (employee rate on OW above
$750, phase-in factor on TW - $500 from $500 to $750), both in basis points. -/
def cpfBand (age : Nat) : Int × Int :=
  if age ≤ 55 then (2000, 6000) else if age ≤ 60 then (1700, 5100) else if age ≤ 65 then (1150, 3450)
  else if age ≤ 70 then (750, 2250) else (500, 1500)

/-- Employee CPF for one month of ordinary wages (2025 table). -/
def cpfMonthlyAt (age : Nat) (m : Int) : Int :=
  let (r, f) := cpfBand age
  if m ≤ 500 then 0
  else if m ≤ 750 then divR .down (f * (m - 500)) BP
  else divR .down (r * min m owCeiling) BP

def cpfMonthly (m : Int) : Int := cpfMonthlyAt 40 m

def cpfAnnual (age : Nat) (wages : Int) : Int := perPeriod 12 (cpfMonthlyAt age) wages

/-- One resident: tax on chargeable income after reliefs (capped at $80,000). -/
def personTax (assessable reliefs : Int) : Int := sched.tax Rule.unitDown (pos (assessable - min reliefs reliefCap))

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let idx := List.range c.adults.length
  let earned (a : Adult) : Int := pos a.wages + pos a.selfEmployment
  let assess (i : Nat) (a : Adult) : Int := earned a + share c.rentalIncome i
  -- spouse's annual income for the spouse-relief test (all income incl. exempt interest/dividends)
  let incomeOf (i : Nat) (a : Adult) : Int := earned a + a.pension + share c.rentalIncome i + share c.interest i + share c.dividends i
  let rows := (c.adults.zip idx).map fun (a, i) => (a, i, assess i a, incomeOf i a)
  -- the adult who claims QCR: the higher assessable income (first on a tie)
  let top : Nat := match rows with
    | [(_, _, x0, _), (_, _, x1, _)] => if x1 > x0 then 1 else 0
    | _ => 0
  let others (i : Nat) : List Int := rows.filterMap fun (_, j, _, inc) => if j ≠ i then some inc else none
  let reliefsOf (a : Adult) (i : Nat) (assessable : Int) : Int :=
    let eir := min (eirMax a.age) (earned a)
    let cpf := cpfAnnual a.age a.wages
    let sp := if c.isCouple ∧ earned a > 0 ∧ (others i).all (· ≤ spouseIncomeLimit) ∧ i = top then spouseRelief else 0
    let qcr := if i = top then qcrPerChild * (c.childrenUnder 16 : Nat) else 0
    let _ := assessable
    eir + cpf + sp + qcr
  let taxes := rows.map fun (a, i, x, _) => personTax x (reliefsOf a i x)
  let cpfs := c.adults.map fun a => cpfAnnual a.age a.wages
  Out.make c "SG" "SGD" (sumInts taxes) (employeeSocial := sumInts cpfs)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map fun (a, i, x, _) => pos (x - min (reliefsOf a i x) reliefCap))),
      Out.dStr "note" "bank interest and dividends treated as tax-exempt (IRAS spouse-relief page); QCR claimed by the higher earner; no YA 2026 rebate"])
    (unsupported := (if c.capitalGains ≠ 0 then ["gains on property/shares: taxable only if trading (IRAS); not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions: exempt or taxable by scheme and accrual date (IRAS pension page); not modelled"] else []) ++
      (if c.nChildren > 0 ∧ c.adults.any (fun a => a.wages > 0) then ["working mother's child relief (WMCR) not modelled (needs the mother and the child's birth year)"] else []) ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["self-employed MediSave contributions not modelled"] else []))

def country : Country := { code := "SG", name := "Singapore (YA 2026)", currency := "SGD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- CPF phase-in: no employee share up to $500, 0.6 of the excess to $750 (= 20 % of $750), 20 % above. -/
#guard cpfMonthly 500 = 0 ∧ cpfMonthly 750 = 150 ∧ cpfMonthly 751 = 150 ∧ cpfMonthly 10000 = 1480
/- The 2025 table's printed maxima on OW (employee's share): $1,480 / $1,258 / $851 / $555 / $370; and the phase-in
reaches the full rate at $750 in every band (0.51 x 250 = 127.5 = 17 % of 750, rounded down to 127). -/
#guard [(40, 1480), (58, 1258), (63, 851), (68, 555), (75, 370)].all fun (a, m) => cpfMonthlyAt a 10000 = m
#guard [(58, 127), (63, 86), (68, 56), (75, 37)].all fun (a, m) => cpfMonthlyAt a 750 = m ∧ cpfMonthlyAt a 751 = m

end SgTax
