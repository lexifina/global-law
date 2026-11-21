import IeTax.Params

/-!
# Ireland 2025: income tax, USC, PRSI and benefits, built from TaxKernel parts

Kernel parts used: `Schedule` (income tax bands, USC bands), `Rule` (rounding), `Credit`/`applyCredits` (tax credits,
the home carer credit's withdrawal as a `Taper`), `Contribution` (USC: an all-or-nothing exemption at €13,000 is a
`floor`), `Surcharge` (the 3 % USC surcharge on non-PAYE income above €100,000), `Unit` (joint vs separate).
Written here because the kernel has no part for them (kernel gaps): the **partially transferable band** of
s. 15(3) (the married band rises by the lower earner's income, capped); the **age exemption with marginal relief**
of s. 188 (an exemption limit whose glide caps the *whole liability* at 40 % of the excess, not a rate of a base);
**weekly PRSI with a tapering credit** (SWCA s. 13(2)(b): a weekly floor with a credit withdrawn at 1/6), with a
rate that changes on 1 October; **a benefit withdrawn against net income** (working family payment, s. 229).

All money in cents. A household's adults are `Person`s; investment income, gains and pension contributions are
household totals in the contract and are split between two adults with `half1`/`half2` (contract rule).
-/

namespace IeTax
open TaxKernel

structure Person where
  age : Nat := 40
  wages : Int := 0          -- PAYE employment income (Schedule E), cents
  pension : Int := 0        -- occupational pension (PAYE emoluments; no PRSI), cents
  se : Int := 0             -- trading / professional profits (Schedule D Case I/II), cents
  dividends : Int := 0      -- Schedule F (Irish dividends; DWT credited, final tax at marginal rates), cents
  rent : Int := 0           -- Case V rental income, cents
  interest : Int := 0       -- deposit interest under DIRT (s. 261(c): final liability), cents
  gains : Int := 0          -- chargeable gains (CGT, a separate tax), cents
  contrib : Int := 0        -- pension contributions claimed (s. 774 / s. 787), cents
  /-- a proprietary director (s. 472(1): more than 15 % of the shares): wages are not "emoluments" for the employee
  credit but are earned income for the earned income credit (s. 472AB), and are reckonable emoluments for Class S
  PRSI (SWCA s. 21(1)(c)) instead of Class A (the 50 %+ shareholder case, the Department's scope rule) -/
  director : Bool := false
  deriving Repr, Inhabited

/-- PAYE emoluments (s. 472 "emoluments": income under the PAYE system): wages and occupational pension. -/
def Person.emol (p : Person) : Int := p.wages + p.pension

/-- Relief for pension contributions: the age-related percentage of earnings capped at €115,000 (s. 774(7)(c),
s. 787(8), s. 790A). Relevant earnings here are wages and trading income. -/
def Person.pensionRelief (p : Person) : Int :=
  min (pos p.contrib) (pensionPct p.age * min (pos (p.wages + p.se)) pensionEarningsCap / BP)

/-- Total income for income tax (s. 3, before DIRT interest, which is taxed at source as a final liability). -/
def Person.totalIncome (p : Person) : Int := pos (p.emol + p.se + p.dividends + p.rent - p.pensionRelief)

/-- s. 472(4): the lesser of €2,000 and the standard rate on the emoluments. -/
def Person.employeeCr (p : Person) (y : YP := yp2025) : Int :=
  min y.employeeCredit (standardRate * pos (if p.director then p.pension else p.emol) / BP)

/-- s. 472AB(2),(3): the lesser of €2,000 and 20 % of earned income other than PAYE emoluments, with the employee
credit no more than €2,000 for the individual's income. -/
def Person.earnedCr (p : Person) (y : YP := yp2025) : Int :=
  min (y.earnedIncomeCredit - p.employeeCr y)
    (min y.earnedIncomeCredit (standardRate * pos (p.se + (if p.director then p.wages else 0)) / BP))

def Person.ownCredits (p : Person) (y : YP := yp2025) : Int := p.employeeCr y + pos (p.earnedCr y)

/-- The income tax bands: 20 % up to the band, 40 % above (s. 15 Table). -/
def bands (band : Int) : Schedule := Schedule.ofList [(0, standardRate), (band, higherRate)]

/-- Gross income tax (cents, rounded down to the cent) on taxable income `ti` with standard rate band `band`. -/
def grossTax (band ti : Int) : Int := (bands band).tax Rule.unitDown ti

/-- s. 188: exempt up to the limit; between the limit and twice the limit, tax limited to 40 % of the excess. -/
def ageExemption (limit total tax : Int) : Int :=
  if total ≤ limit then 0
  else if total ≤ 2 * limit then min tax (ageMarginalRate * (total - limit) / BP)
  else tax

/-- s. 188(2A): the increase of the limit for qualifying children. -/
def ageChildIncrease (n : Nat) : Int :=
  ageExemptChild12 * (min n 2 : Nat) + ageExemptChild3 * (n - 2 : Nat)

/-! ## Single assessment (one person) -/

structure ITResult where
  tax : Int            -- income tax after credits and s. 188 (cents), without DIRT
  grossTax : Int
  credits : Int
  band : Int
  taxable : Int
  homeCarer : Int := 0
  option : String
  deriving Repr, Inhabited

/-- An individual assessed as a single person. `spcc`: entitled to the single person child carer credit (s. 462B)
and the Part 2 band; `kids`: qualifying children for s. 188(2A). -/
def singleIT (p : Person) (spcc : Bool) (kids : Nat) (y : YP := yp2025) : ITResult :=
  let band := if spcc then y.bandSPCC else y.bandSingle
  let ti := p.totalIncome
  let g := grossTax band ti
  let cr := y.basicCreditSingle + (if spcc then y.spccCredit else 0) + p.ownCredits y
    + (if p.age ≥ ageCreditAge then ageCreditSingle else 0)
  let t0 := applyCredits g [cr] []
  let t := if p.age ≥ ageCreditAge then
      ageExemption (ageExemptSingle + ageChildIncrease kids) (ti + p.interest) t0 else t0
  { tax := t, grossTax := g, credits := cr, band, taxable := ti,
    option := if spcc then "single person child carer (Part 2)" else "single (Part 1)" }

/-! ## Joint assessment (married couple / civil partners, s. 1017) -/

/-- s. 15(3): the Part 3 band increased by the lesser of €35,000 and the lower spouse's specified income. -/
def bandIncrease (inc1 inc2 : Int) : Int := min bandIncreaseCap (pos (min inc1 inc2))

/-- s. 466A(6): the home carer credit reduced by half the carer spouse's income above €7,200. -/
def homeCarerCr : Credit := { full := homeCarerCredit, start := homeCarerIncomeLimit, num := 1, den := 2 }

def jointIT (p1 p2 : Person) (kids : Nat) (y : YP := yp2025) : ITResult :=
  let i1 := p1.totalIncome
  let i2 := p2.totalIncome
  let ti := i1 + i2
  let old := p1.age ≥ ageCreditAge || p2.age ≥ ageCreditAge
  let base := y.basicCreditMarried + p1.ownCredits y + p2.ownCredits y + (if old then ageCreditMarried else 0)
  -- option A: the increased band (s. 15(3))
  let bandA := y.bandMarried + min y.bandIncreaseCap (pos (min i1 i2))
  let gA := grossTax bandA ti
  let tA := applyCredits gA [base] []
  -- option B: the home carer credit (s. 466A), carer = the spouse with the lower income; dependent = a child
  let carerInc := min (i1 + p1.interest) (i2 + p2.interest)
  let hc := if kids > 0 then ({ homeCarerCr with full := y.homeCarerCredit } : Credit).value 0 carerInc else 0
  let gB := grossTax y.bandMarried ti
  let tB := applyCredits gB [base + hc] []
  let useB := hc > 0 && tB < tA
  let (t0, g, band, cr, opt) :=
    if useB then (tB, gB, y.bandMarried, base + hc, "joint, home carer credit (s. 466A)")
    else (tA, gA, bandA, base, "joint, increased band (s. 15(3))")
  let t := if old then
      ageExemption (ageExemptMarried + ageChildIncrease kids) (ti + p1.interest + p2.interest) t0 else t0
  { tax := t, grossTax := g, credits := cr, band, taxable := ti, homeCarer := if useB then hc else 0,
    option := opt }

/-! ## DIRT and CGT -/
def dirt (p : Person) : Int := Rule.unitDown.ofTicks (dirtRate * pos p.interest)
def cgt (p : Person) : Int := Rule.unitDown.ofTicks (cgtRate * pos (p.gains - cgtExemption))

/-! ## Universal social charge -/

/-- Aggregate income for USC (s. 531AM(1)): PAYE emoluments and other income, before pension contributions;
DIRT interest excluded (s. 531AM(1)(b)(iii)). -/
def Person.uscIncome (p : Person) : Int := p.emol + p.se + p.dividends + p.rent
/-- Relevant (non-PAYE) income for the s. 531AN(2) surcharge. -/
def Person.relevantIncome (p : Person) : Int := p.se + p.dividends + p.rent

/-- USC as a kernel `Contribution`: nothing up to €13,000, the whole income above (`floor`). -/
def uscStd : Contribution := { name := "USC", sched := uscSchedule, floor := uscExempt + 1 }
def uscRed : Contribution := { name := "USC (70+)", sched := uscReducedSchedule, floor := uscExempt + 1 }
def uscSurcharge : Surcharge := Surcharge.above uscSurchargeRate uscSurchargeFrom

/-- USC with a given pair of schedules (standard, reduced): the 2025 law by default; the checks also use 2026. -/
def uscWith (std red : Schedule) (p : Person) : Int :=
  let a := p.uscIncome
  let c : Contribution := if p.age ≥ uscReducedAge && a ≤ uscReducedLimit
    then { uscRed with sched := red } else { uscStd with sched := std }
  if a ≤ uscExempt then 0
  else Rule.unitDown.ofTicks (c.ticks a + uscSurcharge.ticks p.relevantIncome)

def usc (p : Person) (y : YP := yp2025) : Int := uscWith y.uscSchedule uscReducedSchedule p

/-! ## PRSI -/

/-- One week's Class A1 employee contribution, in units of 1/60000 cent (exact: rate in bp, credit in sixths):
nothing up to €352; from €352.01 to €424 the rate less the credit €12 − (w − €352.01)/6; above €424 the rate. -/
def prsiWeekX (rate w : Int) : Int :=
  if w ≤ prsiWeeklyFloor then 0
  else if w ≤ prsiCreditTop then pos (6 * rate * w - (60000 * prsiCreditMax - 10000 * (w - prsiCreditBase)))
  else 6 * rate * w

/-- Readings that reproduce other calculators (for attributing differences; the default is the statute). -/
structure Reading where
  /-- PRSI Class A1 at 4.1 % for every week of 2025 (the OECD's convention for 2025, F2) -/
  prsiFlat41 : Bool := false
  /-- PRSI Class A1 at the year's first rate for every week (`--prsi-first-rate`): OECD TaxBEN's reading for 2024
  (4 % all year; the statute: 4.1 % from 1 October 2024). -/
  prsiFirstRate : Bool := false
  /-- working family payment without the s. 229(2) rounding of the weekly rate up to the euro (the OECD's, F4) -/
  wfpExact : Bool := false
  /-- no €20 minimum WFP payment (s. 229(2) prescribed amount), to show its effect -/
  wfpNoMinimum : Bool := false
  deriving Repr, Inhabited

/-- Class A1 for the year: weekly pay `wages/52` (to the cent), 39 weeks at 4.1 %, 13 at 4.2 %; rounded to the cent
at the end (half up; the Act states no rounding). -/
def prsiA (p : Person) (rd : Reading := {}) (y : YP := yp2025) : Int :=
  if p.age ≥ prsiAgeLimit || p.director then 0 else
  let w := pos p.wages / y.payWeeks
  -- the convention is the OECD's for 2025 only (4.1 % all year); for 2024 the OECD uses the statute's blend
  let x := if (rd.prsiFlat41 && y.year == 2025) || rd.prsiFirstRate then y.payWeeks * prsiWeekX y.prsiRate1 w else
    y.payWeeksAtRate1 * prsiWeekX y.prsiRate1 w + (y.payWeeks - y.payWeeksAtRate1) * prsiWeekX y.prsiRate2 w
  divR .halfUp x 60000

/-- Class S on reckonable income (trading, rental, dividends, interest) of €5,000 or more: the greater of 4.125 %
and €650 (SWCA s. 21(1)(a), F3). -/
def prsiS (p : Person) (y : YP := yp2025) : Int :=
  let r := pos (p.se + p.dividends + p.rent + p.interest + (if p.director then p.wages else 0))
  if p.age ≥ prsiAgeLimit || r < prsiClassSThreshold then 0
  else max prsiClassSMin (divR .halfUp (y.prsiClassSNum * r) prsiClassSDen)

/-! ## The household -/

structure HH where
  persons : List Person
  married : Bool
  kids : Nat            -- qualified children (under 18)
  deriving Repr, Inhabited

inductive Election where
  | best        -- the lower of joint and single assessment (both are open to a married couple, s. 1018)
  | jointOnly
  | singleOnly
  deriving Repr, DecidableEq, Inhabited

structure HHResult where
  it : Int
  itParts : List ITResult
  assessment : String
  jointTax : Int
  singleTax : Int
  dirt : Int
  usc : Int
  uscEach : List Int
  cgt : Int
  prsiA : Int
  prsiS : Int
  cb : Int
  wfpWeekly : Int
  wfp : Int
  familyIncomeWeekly : Int
  deriving Repr, Inhabited

def sumL (l : List Int) : Int := l.foldl (· + ·) 0

def hhCalc (h : HH) (el : Election := .best) (rd : Reading := {}) (y : YP := yp2025) : HHResult :=
  let ps := h.persons
  let (it, parts, how, jt, st) :=
    match ps with
    | [p] =>
      let r := singleIT p (h.kids > 0) h.kids y
      (r.tax, [r], r.option, r.tax, r.tax)
    | [p1, p2] =>
      if h.married then
        let j := jointIT p1 p2 h.kids y
        let s1 := singleIT p1 false 0 y
        let s2 := singleIT p2 false 0 y
        let st := s1.tax + s2.tax
        let useSingle := match el with
          | .singleOnly => true
          | .jointOnly => false
          | .best => st < j.tax
        if useSingle then (st, [s1, s2], "single assessment of each spouse (s. 1018 election)", j.tax, st)
        else (j.tax, [j], j.option, j.tax, st)
      else
        -- cohabitants: each single; no single person child carer credit (s. 462B excludes cohabitants)
        let s1 := singleIT p1 false h.kids y
        let s2 := singleIT p2 false 0 y
        (s1.tax + s2.tax, [s1, s2], "unmarried: each assessed alone", s1.tax + s2.tax, s1.tax + s2.tax)
    | _ => (0, [], "unsupported", 0, 0)
  let dirtT := sumL (ps.map dirt)
  let uscs := ps.map fun p => usc p y
  let uscT := sumL uscs
  let cgtT := sumL (ps.map cgt)
  let pa := sumL (ps.map fun p => prsiA p rd y)
  let pss := sumL (ps.map fun p => prsiS p y)
  let cb := 12 * childBenefitMonthly * h.kids
  let gross := sumL (ps.map fun p => p.wages + p.pension + p.se + p.dividends + p.rent + p.interest)
  let earns := sumL (ps.map fun p => p.wages + p.se) > 0
  let fiWeekly := (gross - it - dirtT - uscT - pa - pss) / y.payWeeks
  let thr := y.wfpThreshold h.kids
  let wfpW := if h.kids > 0 && earns && fiWeekly < thr then
      -- s. 229(1)-(2): 60 % of the shortfall, a fraction of €1 counted as €1
      let r := if rd.wfpExact then wfpRate * (thr - fiWeekly) / BP
               else 100 * ceilDiv (wfpRate * (thr - fiWeekly)) (BP * 100)
      if rd.wfpNoMinimum then r else max wfpMinimum r
      else 0
  { it := it + dirtT, itParts := parts, assessment := how, jointTax := jt, singleTax := st, dirt := dirtT,
    usc := uscT, uscEach := uscs, cgt := cgtT, prsiA := pa, prsiS := pss, cb, wfpWeekly := wfpW,
    wfp := y.payWeeks * wfpW, familyIncomeWeekly := fiWeekly }

end IeTax
