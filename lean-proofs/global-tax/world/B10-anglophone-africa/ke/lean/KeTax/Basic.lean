import TaxKernel.World

/-!
# Kenya: income tax on employment income, Income Tax Act (Cap. 470), year of income 2025 (calendar year)

Sources (Kenya Law, the official law reporter; archived copies of its pages because kenyalaw.org answers scripts with
an AWS WAF challenge, which was not bypassed; files in `ke/law/`):
* Income Tax Act, consolidated version 2025-07-01 (`ita_2025-07-01.html`, Internet Archive capture 2025-07-31 of
  new.kenyalaw.org/akn/ke/act/1973/16/eng@2025-07-01). Third Schedule Head B para. 1 (history note ends "Act No. 9 of
  2025, s. 30(a)"): "On the first Ksh. 288,000 | 10% | On the next Ksh. 100,000 | 25% | On the next Ksh. 5,612,000 |
  30% | On the next Ksh. 3,600,000 | 32.5% | On all income over 9,600,000 | 35%". Head A para. 1: "The amount of the
  personal relief shall be twenty-eight thousand eight hundred shillings". s. 30: "A resident individual in receipt
  of taxable income shall be entitled to a tax relief ... the personal relief". s. 45 (married women) "[Repealed by
  Act No. 4 of 2023, s. 22.]": spouses are taxed separately.
* s. 15(2)(ac) "in the case of an employee, the amount deducted in accordance with section 5(1)(a) of the Affordable
  Housing Act, 2024"; (ae) "contributions made to the Social Health Insurance Fund in accordance with section 27(a) and
  (b) of the Social Health Insurance Act, 2023" (both inserted by the Tax Laws (Amendment) Act 2024, No. 12 of 2024,
  s. 7, "Date of Commencement: 27th December, 2024": in force for the whole of 2025).
* s. 22A(1): deduction for an employee's contributions to registered funds "limited to the lesser of (a) the sum of
  the contributions ... (b) thirty per cent of the employee's pensionable income ... (c) three hundred and sixty
  thousand shillings" (Act No. 12 of 2024, s. 8); s. 22(8): "contributions made to the National Social Security Fund
  shall be deemed to be contributions made to a defined contribution registered fund".
* Finance Act 2025 (No. 9 of 2025, Kenya Gazette Supplement; `fa2025.pdf`), s. 1: "(b) all other sections, on 1st July,
  2025"; s. 30 changed Head B only by inserting "other than that of the total income comprising fringe benefits and
  the qualifying interest" in para. 1 and company rates: the individual bands are the same all year.
* National Social Security Fund Act 2013 (No. 45 of 2013, version 2022-12-31, `nssf2013.html`) s. 20(1)(b): "the
  employee's contribution at six per centum of the employee's pensionable earnings"; "pensionable earnings" means "the
  lower of the member's monthly wages and the Upper Earnings Limit"; Third Schedule table, year 3: Lower Earnings Limit
  8,000, Upper Earnings Limit "2 times National Average Earnings" (a KNBS figure, not reached: optional input).
* Affordable Housing Act 2024 (No. 2 of 2024, `aha2024.html`) s. 4(2): "The Levy shall be at the rate of one point
  five percent of— (a) the gross salary of an employee".
* Social Health Insurance Regulations 2024 (L.N. 49 of 2024, version 2025-02-28, `shi_regs_2025-02-28.html`) reg.
  17(1): "a rate of 2.75% of the gross salary or wage of the household"; (2): "shall not, in any case, be less than
  Kenya shillings three hundred per month".
W5 pattern A (2026-11-20): default Upper Earnings Limit for year 3 = KES 72,000 a month (input `nssfUEL` still wins;
`"w5Contrib": false` restores the old default, the LEL). The Third Schedule sets the year-3 UEL at 2 x National Average
Earnings; the NSSF's own notices give the NAE through the other years' limits: "Year 2 contribution rates, 2024 ... In
accordance with the Third Schedule ... Upper Limit (Tier 2) 36,000.00" (= 1 x NAE, from February 2024; poster of
12 Jan 2024) and "Year 4 (2026) ... Upper Earning Limit (Tier 2) 108,000.00" (= 3 x NAE; notice of 18 Feb 2026, which
also says "Year 3 contribution rates ended on 31st January, 2026"), so NAE = 36,000 at both ends of year 3 and the year-3
UEL = 72,000 (reading: the year-3 notice itself was not found; official secondary). `ke/law/w5/`. January 2025 still
fell in year 2: with the switch on, January uses the year-2 limits (LEL 7,000, UEL 36,000, the NSSF's year-2 notice)
and February-December year 3 (the year-4 notice of 18 Feb 2026: "the implementation of Year 3 contribution rates ended on
31st January, 2026", so year 3 began in February 2025; Reviewer 3 pass 3 row 127, gaa.go.ke copy in `ke/law/w5/`).
-/

namespace KeTax
open TaxKernel

/-- Third Schedule Head B para. 1 (annual; bands as last set by Act No. 4 of 2023, s. 26(b)(i) per the history note; unchanged in 2025). -/
def sched : Schedule :=
  Schedule.ofList [(0, 1000), (288000, 2500), (388000, 3000), (6000000, 3250), (9600000, 3500)]
/-- Head A para. 1. -/
def personalRelief : Int := 28800
/-- s. 22A(1)(b), (c). -/
def pensionPct : Int := 3000
def pensionCap : Int := 360000
/-- NSSF Act 2013 s. 20(1)(b) and Third Schedule (year 3 Lower Earnings Limit). -/
def nssfRate : Int := 600
def nssfLEL : Int := 8000
/-- Social Health Insurance Regulations 2024 reg. 17. -/
def shifRate : Int := 275
def shifMin : Int := 300
/-- Affordable Housing Act 2024 s. 4(2)(a). -/
def ahlRate : Int := 150

def pct (bp x : Int) : Int := divR .down (bp * x) BP

/-- Monthly NSSF employee contribution: 6 % of pensionable earnings = min(wage, UEL). Without the UEL (input
    `nssfUEL`, monthly KES), Tier II cannot be computed: the UEL then defaults to the LEL (Tier I only). -/
def nssfMonth (uel m : Int) : Int := pct nssfRate (min (pos m) (max nssfLEL uel))
def shifMonth (m : Int) : Int := if m ≤ 0 then 0 else max shifMin (pct shifRate m)
def ahlMonth (m : Int) : Int := pct ahlRate (pos m)

structure Person where
  tax : Int
  taxable : Int
  nssf : Int
  shif : Int
  ahl : Int

/-- W5 pattern A: NSSF year 2 (January 2025): LEL 7,000, UEL 1 x NAE = 36,000. -/
def nssfMonthYear2 (m : Int) : Int := pct nssfRate (min (pos m) 36000)
#guard nssfMonthYear2 5000 = 300 ∧ nssfMonthYear2 100000 = 2160

def person (uel : Int) (a : Adult) (w5 : Bool := false) : Person :=
  let w := pos a.wages
  let nssf := if w5 then perPeriodIdx 12 (fun i m => if i = 0 then nssfMonthYear2 m else nssfMonth uel m) w
    else perPeriod 12 (nssfMonth uel) w
  let shif := perPeriod 12 shifMonth w
  let ahl := perPeriod 12 ahlMonth w
  let penDed := min nssf (min (pct pensionPct w) pensionCap)
  let ti := pos (w - penDed - shif - ahl)
  let t := pos (sched.tax Rule.unitDown ti - (if ti > 0 then personalRelief else 0))
  { tax := t, taxable := ti, nssf := nssf, shif := shif, ahl := ahl }

/-- W5 pattern A: year-3 UEL = 2 x NAE 36,000 (NSSF notices for years 2 and 4: 36,000 = 1 x NAE, 108,000 = 3 x NAE). -/
def nssfUELYear3 : Int := 2 * 36000

#guard nssfMonth nssfUELYear3 100000 = 4320 ∧ nssfMonth nssfUELYear3 50000 = 3000

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let uel := (c.int? "nssfUEL").getD (if w5 then nssfUELYear3 else nssfLEL)
  let ps := c.adults.map (fun a => person uel a w5)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 then ["interest and dividends: final withholding (Third Schedule Head B para. 3) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income (s. 6A residential rental income tax) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains (Eighth Schedule) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "KE" "KES" (sumInts (ps.map (·.tax)))
    (surtaxes := [("AffordableHousingLevy", sumInts (ps.map (·.ahl)))])
    (employeeSocial := sumInts (ps.map (·.nssf)) + sumInts (ps.map (·.shif)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "nssf" (sumInts (ps.map (·.nssf))),
      Out.d "shif" (sumInts (ps.map (·.shif))), Out.d "nssfUELMonthly" (max nssfLEL uel),
      Out.dStr "note" "individual taxation (s. 45 repealed); annual Head B bands less personal relief 28,800; NSSF, SHIF and AHL deducted (ss. 15(2)(ac),(ae), 22A)"])
    (unsupported := unsup ++ [if w5 then "NSSF: January at year-2 limits (7,000 / 36,000), February-December at year 3 (8,000 / 72,000, the UEL inferred from the NSSF year-2 and year-4 notices)" else "NSSF Tier II: Upper Earnings Limit (2 x KNBS National Average Earnings) not reached; pass nssfUEL (monthly KES), default = LEL 8,000 (Tier I only)",
      "insurance relief (Head A para. 2), post-retirement medical fund and mortgage interest deductions need inputs not in the contract",
      "wages paid evenly over 12 months (NSSF, SHIF minimum and AHL are monthly)"])

def country : Country := { code := "KE", name := "Kenya (Income Tax Act Cap. 470)", currency := "KES", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed from Head B: tax on 388,000 = 28,800 + 25,000 = 53,800; on 6,000,000 = 53,800 + 30 % x 5,612,000. -/
#guard sched.tax Rule.unitDown 388000 = 53800
#guard sched.tax Rule.unitDown 6000000 = 53800 + 1683600
#guard sched.tax Rule.unitDown 9600000 = 53800 + 1683600 + 1170000
/- The personal relief exactly cancels the 10 % band: no tax at or below 288,000 of taxable income. -/
#guard sched.tax Rule.unitDown 288000 = personalRelief
/- SHIF minimum: 300 a month below 10,909 a month of salary (2.75 % x 10,909 = 299.99). -/
#guard shifMonth 10000 = 300 ∧ shifMonth 20000 = 550 ∧ shifMonth 0 = 0

end KeTax
