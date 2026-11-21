import TaxKernel.World

/-!
# Belize: income tax of a resident employed individual and Social Security contributions, basis year 2025

Sources (Global law corpus `belize/national/acts`: Laws of Belize Revised Edition 2020 + Acts 2021-2026 as enacted;
files in `bz/law/`):
* Income and Business Tax Act Cap. 55 (Rev. Ed. 2020) as amended by the Income and Business Tax (Amendment) Act 2024
  (No. 40 of 2024, assented 11 December 2024; s. 34: "This Act shall come into force on the 1st day of January, 2025").
  - new s. 6(2): "no tax shall be charged upon the chargeable income of any person other than an employed person";
    s. 6(3): "the tax on the chargeable income of every employed person ... shall be charged at the rate of
    twenty-five per centum of the chargeable income".
  - new s. 16(1): "there shall be allowed a basic deduction in the case of an employed individual whose total income in
    a basis year from all sources exceeds twenty-nine thousand dollars ---- $20,000.00, Provided that in the case of an
    employed individual whose total income ... exceeds twenty-nine thousand dollars but does not exceed thirty two
    thousand dollars, a tax credit equivalent to the sum of two thousand two hundred fifty dollars ($2,250.00) less
    seventy five percent of the difference between total income and twenty-nine thousand dollars ($29,000.00)";
    s. 16(2): "Any employed individual ... whose total income in a basis year from all sources is less than twenty nine
    thousand dollars shall not be chargeable to tax in that year" (FINDINGS: exactly 29,000 is in neither clause).
  - s. 16(5) (Rev. Ed.): "all income, whether exempt from tax or not, shall be included as gross income".
  - s. 19(1), (3)(a) (Rev. Ed.): a married woman's income "shall ... be deemed to be the income of the husband" unless
    "she and her husband so jointly elect" separate assessment (election; default separate, input `bzJoint`).
  - s. 20 (5 % final tax on time-deposit interest) repealed by Act 40 of 2024 s. 5; s. 8(1)(m) exempts "any interest
    paid on savings where the investment does not constitute the ordinary business".
* Social Security (Collection of Contributions) Regulations (Cap. 44, Rev. Ed. 2020, agm.gov.bz PDF) reg. 6(1): the
  employed person's contribution is "the amounts set out in columns 2, 3, and 4 of the respective tables in the
  Schedule"; reg. 6(4): "The Minister shall, by Notice published in the Gazette, declare the period for Table 3".
  Schedule Table 2, "PERIOD JANUARY 6, 2020 UNTIL THE DECLARATION OF THE PERIOD OF TABLE 3": employed person's weekly
  contribution by actual weekly earnings (below). No declaring notice was found in the record of statutory instruments
  2020-2026 (input `bzSsTable: 3` switches to Table 3, rows 1-7 read).
-/

namespace BzTax
open TaxKernel

/-- Table 2 (lower bound of actual weekly earnings in cents, employed person's weekly contribution in cents). -/
def ssTable2 : List (Int × Int) :=
  [(0, 93), (7000, 152), (11000, 219), (14000, 354), (18000, 534), (22000, 714), (26000, 894), (30000, 1074),
   (34000, 1259), (38000, 1454), (42000, 1660), (46000, 1878)]

def ssWeek (wc : Int) : Int := if wc ≤ 0 then 0 else ssTable2.foldl (fun acc r => if wc ≥ r.1 then r.2 else acc) 0

def weeks : Int := 52

/-- s. 16 as replaced by Act 40 of 2024: (basic deduction, tax credit in cents, chargeable?) for total income `ti`. -/
def chargeable (ti : Int) : Bool := ti ≥ 29000
def basicDeduction (ti : Int) : Int := if ti > 29000 then 20000 else 0
def creditCents (ti : Int) : Int := if ti > 29000 && ti ≤ 32000 then pos (225000 - 75 * (ti - 29000)) else 0

/-- Tax in cents on an employed individual's total income `ti` (whole dollars). -/
def taxCents (ti : Int) : Int :=
  if chargeable ti then pos (25 * pos (ti - basicDeduction ti) - creditCents ti) else 0

structure Person where
  ss : Int
  ti : Int
  tax : Int

def person (a : Adult) (extra : Int) : Person :=
  let w := pos a.wages
  let wc := divR .down (w * 100) weeks
  let ss := if a.age < 65 then weeks * ssWeek wc else 0
  let ti := w + extra
  { ss := ss, ti := ti, tax := taxCents ti }

def out (c : Canon) : Out :=
  let joint := c.bool? "bzJoint" == some true && c.married && c.isCouple
  let ps : List Person :=
    if joint then
      match c.adults with
      | [a, b] =>
        let pa := person a (pos b.wages)
        let pb := person b 0
        [pa, { pb with ti := 0, tax := 0 }]
      | _ => c.adults.map (fun a => person a 0)
    else c.adults.map (fun a => person a 0)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment: business tax on receipts (Part XI, s. 6(2)) not modelled"] else []) ++
    (if c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["dividends, rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions (largely exempt, s. 8(1)(q)) not modelled"] else []) ++
    (if c.bool? "bzSsTable3" == some true then ["Table 3 requested but not encoded (only rows 1-7 read)"] else [])
  Out.make c "BZ" "BZD" (divR .halfUp (sumInts (ps.map (·.tax))) 100)
    (employeeSocial := divR .halfUp (sumInts (ps.map (·.ss))) 100)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (fun p => pos (p.ti - basicDeduction p.ti)))),
      Out.dBool "jointAssessment" joint,
      Out.dStr "note" "Act 40 of 2024 (from 1 Jan 2025): 25 % on total income less 20,000 above 29,000, phase-in credit 29,000-32,000; savings interest exempt (s. 8(1)(m)); SS Collection Regs Table 2 weekly (52 weeks)"])
    (unsupported := unsup ++ ["wages assumed paid evenly over 52 weeks (Social Security is weekly)", "employed status assumed for wage earners (s. 6(3))"])

def country : Country := { code := "BZ", name := "Belize (Income and Business Tax Act Cap. 55 as amended 2024)", currency := "BZD", year := "2025", compute := out }

/- s. 16 phase-in: at 29,001 tax = 25 % x 9,001 - (2,250 - 0.75) = 1.00; at 32,000 = 3,000; 100 % marginal rate between. -/
#guard taxCents 28999 = 0
#guard taxCents 29000 = 725000       -- F1: exactly 29,000 is chargeable with no basic deduction
#guard taxCents 29001 = 100
#guard taxCents 32000 = 300000
#guard taxCents 32001 = 300025
#guard taxCents 30000 = 100000       -- 2,500 - (2,250 - 750) = 1,000: 100 % of the excess over 29,000
/- Table 2: row 1 $0.93, row 12 ($460 and over) $18.78 a week. -/
#guard ssWeek 6999 = 93
#guard ssWeek 46000 = 1878
#guard ssWeek 1000000 = 1878

end BzTax
