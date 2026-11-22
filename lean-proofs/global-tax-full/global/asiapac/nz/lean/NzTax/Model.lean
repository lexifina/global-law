import NzTax.Params

/-!
# New Zealand: one person's income tax, the independent earner tax credit, the ACC earners' levy, the student loan
repayment, and Working for Families for the family

Kernel parts: `Schedule` (sch 1 pt A), `Rule` (cents, round down), `Credit` (IETC with its 13 c withdrawal, the
donation credit), `Contribution` (ACC earners' levy with its ceiling), `Taper` (FTC/IWTC/Best Start abatement).
Not in the kernel (written here, recorded as kernel gaps): the floor-and-ceiling eligibility of the IETC (a credit
that is nil below $24,000 and above $70,000: an eligibility window, not a phase-in), the shared abatement of two
credits (the FTC abates first and the remainder abates the IWTC), the minimum family tax credit (a top-up of
after-tax income to a guaranteed amount: 100 % withdrawal by construction), and the day-weighted composite
calculations of 2024-25.
-/

namespace NzTax
open TaxKernel

/-- Tax on taxable income `ti` (cents) under schedule `s`, in cents, fractions of a cent dropped. The Act states no
rounding of the liability; IRD's payroll specification says "Do not round this figure" for the annual tax and
truncates only the weekly amount to whole cents (spec 2025-26 s. 5.2 steps 3 and 6.1). -/
def taxOn (s : Schedule) (ti : Int) : Int := s.tax Rule.unitDown ti

/-! ## Independent earner tax credit (ss LC 13-LC 15) -/

/-- The IETC for a full year on net income `ni` (cents), one setting: $520 if `floor ≤ ni ≤ maxIncome`, less 13 c
per dollar above `abateStart`, never below 0. In cents. -/
def ietcSetting (maxAmt floor abateStart maxIncome rate : Int) (ni : Int) : Int :=
  if ni < nzd floor ∨ nzd maxIncome < ni then 0
  else pos (nzd maxAmt - rate * pos (ni - nzd abateStart) / BP)

def ietc (p : Params) (ni : Int) : Int :=
  ietcSetting p.ietcMax p.ietcFloor p.ietcAbateStart p.ietcMaxIncome p.ietcAbateRate ni

/-- 2024-25 composite IETC (Special report pp. 12-14): ((P − X) × 121/365 + (P − Y) × 244/365) × EM/12, each period
with its own setting. Each period's amount is floored at 0 here (`ietcSetting` already does); the formula as printed
in the special report does not floor `P − X`, which is negative for net income between $48,000 and $70,000 (F-list
item "IETC composite formula"). Cents, rounded down. -/
def ietc2024 (ni : Int) : Int :=
  let a := ietcSetting 520 24000 ietcOldAbateStart ietcOldMaxIncome 1300 ni
  let b := ietcSetting 520 24000 66000 70000 1300 ni
  (a * daysOld + b * daysNew) / daysYear

/-- The special report's formula exactly as printed (no floor on P − X, P − Y): P = $520 inside the setting's
income window, else 0; X, Y = 13 c per dollar above the setting's abatement start. -/
def ietc2024Printed (ni : Int) : Int :=
  let pOld := if nzd 24000 ≤ ni ∧ ni ≤ nzd 48000 then nzd 520 else 0
  let pNew := if nzd 24000 ≤ ni ∧ ni ≤ nzd 70000 then nzd 520 else 0
  let x := 1300 * pos (ni - nzd 44000) / BP
  let y := 1300 * pos (ni - nzd 66000) / BP
  ((pOld - x) * daysOld + (pNew - y) * daysNew) / daysYear

/-! ## ACC earners' levy and student loan -/

/-- ACC earners' levy on liable earnings `e` (cents): rate × min(e, maximum), cents rounded down (spec s. 5.2 step 4:
"multiply annual income by 1.67% ... equal to or more than $152,790 ... $2,551.59"). -/
def accLevy (p : Params) (e : Int) : Int :=
  (Contribution.flatCapped "ACC earners' levy" p.accRate (nzd p.accMaxEarnings)).amount (pos e)

/-- Student loan repayment on repayment income `ri` (cents): 12 % of the excess over the threshold. -/
def studentLoan (p : Params) (ri : Int) : Int := p.slRate * pos (ri - nzd p.slThreshold) / BP

/-! ## Working for Families (ITA 2007 subpart MD; MFTC s ME 1) -/

structure Wff where
  ftc : Int
  iwtc : Int
  mftc : Int
  bestStart : Int
  abatement : Int
  deriving Repr

def Wff.total (w : Wff) : Int := w.ftc + w.iwtc + w.mftc + w.bestStart

/-- Working for Families for a family with `n` dependent children, `nb0` Best Start children in their first year,
`nb12` in their second or third year, family scheme income `fsi` (cents), `work` (income from paid work), `wages`
(salary or wage income, the MFTC condition) and income tax `tax` (cents, for the MFTC's "family income after tax").
Weights `wOld/wNew` (days) pro-rate the IWTC base and MFTC threshold in 2024-25; 2025-26 uses (0, 1). -/
def wffWith (p : Params) (iwtcOld mftcOld wOld wNew : Int) (n nb0 nb12 : Nat) (fsi : Int) (work wages : Bool)
    (tax : Int) : Wff :=
  if n = 0 then { ftc := 0, iwtc := 0, mftc := 0, bestStart := 0, abatement := 0 } else
  let ftcFull := nzd (p.ftcEldest + p.ftcOther * ((n : Int) - 1))
  let extra := nzd (p.iwtcExtra * pos ((n : Int) - 3))
  let iwtcFull := if work then (nzd iwtcOld * wOld + nzd p.iwtcBase * wNew) / (wOld + wNew) + extra else 0
  let abat := p.wffAbateRate * pos (fsi - nzd p.wffAbateStart) / BP
  let ftc := pos (ftcFull - abat)
  let iwtc := pos (iwtcFull - pos (abat - ftcFull))
  let thr := (nzd mftcOld * wOld + nzd p.mftcThreshold * wNew) / (wOld + wNew)
  let mftc := if wages then pos (thr - (fsi - tax)) else 0
  let bs12 := pos (nzd p.bestStart * nb12 - p.bestStartAbateRate * pos (fsi - nzd p.bestStartAbateStart) / BP)
  let bs := nzd p.bestStart * nb0 + bs12
  { ftc, iwtc, mftc, bestStart := bs, abatement := abat }

def wff (p : Params) (n nb0 nb12 : Nat) (fsi : Int) (work wages : Bool) (tax : Int) : Wff :=
  wffWith p p.iwtcBase p.mftcThreshold 0 1 n nb0 nb12 fsi work wages tax

def wff2024 (n nb0 nb12 : Nat) (fsi : Int) (work wages : Bool) (tax : Int) : Wff :=
  wffWith p2024 iwtcBaseOld mftcThresholdOld daysOld daysNew n nb0 nb12 fsi work wages tax

/-! ## One person -/

structure PersonIn where
  age : Nat
  wages : Int
  selfEmployment : Int
  pension : Int
  interest : Int
  /-- cash dividends from New Zealand companies, fully imputed -/
  dividends : Int
  rental : Int
  gifts : Int
  studentLoan : Bool
  deriving Repr

structure PersonOut where
  /-- imputation credit attached to the dividends (cents) -/
  imputationCredit : Int
  /-- net income = taxable income (no losses, no deductions modelled), cents -/
  netIncome : Int
  taxOnIncome : Int
  imputationUsed : Int
  imputationExcess : Int
  ietc : Int
  donationCredit : Int
  /-- income tax after credits (negative = refund) -/
  incomeTax : Int
  acc : Int
  studentLoan : Int
  deriving Repr

/-- `ietcAllowed`: false when the family receives Working for Families, or the person receives NZ Super (modelled:
pension income at age 65+), the IETC exclusions as IRD lists them (ss LC 13-LC 15; Special report p. 11: "main benefit, student allowance, New Zealand
superannuation or veteran's pension or are eligible to receive Working for Families tax credits"). -/
def person (p : Params) (y2024 : Bool) (x : PersonIn) (ietcAllowed : Bool) : PersonOut :=
  let ic := (nzd x.dividends * companyRate) / (BP - companyRate)
  let ni := nzd (x.wages + x.selfEmployment + x.pension + x.interest + x.rental + x.dividends) + ic
  let t := taxOn p.sched (pos ni)
  let icUsed := min (pos t) ic
  let ie := if ietcAllowed then (if y2024 then ietc2024 ni else ietc p ni) else 0
  let dc := min (nzd (pos x.gifts)) (pos ni) * donationNum / donationDen
  { imputationCredit := ic, netIncome := ni, taxOnIncome := t, imputationUsed := icUsed,
    imputationExcess := ic - icUsed, ietc := ie, donationCredit := dc,
    incomeTax := t - icUsed - ie - dc,
    acc := accLevy p (nzd (x.wages + x.selfEmployment)),
    studentLoan := if x.studentLoan then studentLoan p ni else 0 }

end NzTax
