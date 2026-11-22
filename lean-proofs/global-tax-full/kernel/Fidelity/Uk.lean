import TaxKernel

/-!
# Kernel fidelity: the UK income tax 2025-26 (England, employees) re-expressed with kernel parts

Built only from kernel parts and the statute's parameters (no code from `cmp/uk`), then compared with `uktax`
on a grid (`fidelity/check_fidelity.py`). Scope: residents of England whose income is employment income, no gifts
or pension contributions; individual taxation; marriage allowance; Class 1 primary contributions on the annual
earnings period; child benefit and the high income child benefit charge.

| Statute | Kernel part |
|---|---|
| ITA 2007 s. 35 (personal allowance £12,570, "reduced by one-half of the excess" over £100,000, rounded up to £1) | `Taper {full := 12570, start := 100000, num := 1, den := 2}` |
| ITA 2007 s. 10, s. 6 (basic 20 % to £37,700; higher 40 % to £125,140; additional 45 %) | `Schedule.ofList` (in pence) |
| ITA 2007 s. 55A-55E (marriage allowance: 10 % of the PA rounded up to £10 transferred; tax reduction at the basic rate; neither spouse liable above the basic rate) | `transferAllowance`-style choice + `applyCredits` (non-refundable) |
| SSCBA 1992 s. 8 (8 % between £12,570 and £50,270, 2 % above) | `Contribution` with a three-band `Schedule` (pence) |
| S.I. 2006/965 reg. 2 (child benefit £26.05 eldest, £17.25 others, weekly) | plain arithmetic (52 weeks) |
| ITEPA 2003 s. 681B-681C (HICBC: 1 % of child benefit per £200 of ANI over £60,000, each figure rounded down) | `Taper {full := 100, start := 60000, num := 1, den := 200}` on the percentage kept |

Money in pence inside (`gbp`); incomes arrive in whole pounds.
-/

namespace Fidelity.Uk
open TaxKernel

def gbp (x : Int) : Int := 100 * x

/-- ITA 2007 s. 35(1)-(2). -/
def pa : Taper := { full := 12570, start := 100000, num := 1, den := 2 }
/-- ITA 2007 s. 10 with the 2025-26 rates (s. 6) and limits (basic rate limit £37,700, s. 10(5); higher rate limit
£125,140, s. 10(5A)), on taxable income in pence. -/
def rates : Schedule := Schedule.ofList [(0, 2000), (3770000, 4000), (12514000, 4500)]
/-- SSCBA 1992 s. 8(2): primary threshold £12,570, upper earnings limit £50,270 (pence). -/
def class1 : Contribution := { name := "class1", sched := Schedule.ofList [(0, 0), (1257000, 800), (5027000, 200)] }
/-- ITEPA 2003 s. 681C(2): the percentage of child benefit kept = 100 − 1 % per £200 over £60,000. -/
def hicbcKept : Taper := { full := 100, start := 60000, num := 1, den := 200 }
/-- ITA 2007 s. 55B(5): 10 % of the personal allowance rounded up to a multiple of £10. -/
def maAmount : Int := Rule.apply (Rule.upTo 10) (12570 / 10)

theorem rates_progressive : rates.progressive = true := by decide
theorem maAmount_eq : maAmount = 1260 := by decide

structure PersonTax where
  pa : Int          -- pounds
  taxable : Int     -- pounds
  tax : Int         -- pence, before the marriage allowance reduction
  deriving Repr

/-- One person's tax with a given personal allowance adjustment (−1,260 for a transferor). -/
def personTax (income : Int) (paAdj : Int) : PersonTax :=
  let a := pos (pa.amount income + paAdj)
  let ti := taxableAfter a income
  { pa := a, taxable := ti, tax := rates.tax Rule.unitDown (gbp ti) }

/-- Liable only at the basic rate (s. 55B(2)(b)): taxable income within the basic rate limit. -/
def basicOnly (p : PersonTax) : Bool := decide (p.taxable ≤ 37700)

/-- Couple's income tax (pence) under individual taxation, with the marriage allowance elected when it lowers the
total (either direction), as the law leaves the election to the couple. -/
def coupleTax (i1 i2 : Int) (married : Bool) : Int × String :=
  let p1 := personTax i1 0
  let p2 := personTax i2 0
  let none_ := p1.tax + p2.tax
  if !married then (none_, "none") else
  let ma (tIn tOut : Int) : Option Int :=
    let tr := personTax tOut (-maAmount)
    let rc := personTax tIn 0
    if basicOnly tr && basicOnly rc then
      some (tr.tax + applyCredits rc.tax [2000 * maAmount / 100] [])
    else Option.none
  let opts := [(none_, "none")] ++ ((ma i1 i2).map (fun t => (t, "2to1"))).toList ++ ((ma i2 i1).map (fun t => (t, "1to2"))).toList
  opts.foldl (fun b o => if o.1 < b.1 then o else b) (none_, "none")

/-- S.I. 2006/965 reg. 2(1)-(2) for 52 weeks, pence. -/
def childBenefit (k : Nat) : Int := if k = 0 then 0 else 52 * (2605 + 1725 * ((k : Int) - 1))

/-- ITEPA 2003 s. 681C: the charge (pence) on the partner with the higher adjusted net income. -/
def hicbc (ani cb : Int) : Int :=
  if ani ≤ 60000 then 0 else
  let pct := 100 - hicbcKept.amount ani
  gbp (pct * (cb / 100) / 100)

/-- The household, all in pence: income tax, Class 1, child benefit net of the charge. -/
def household (c : Canon) : Int × Int × Int × String :=
  let incs := c.adults.map (·.wages)
  let (it, el) := match incs with
    | [a] => ((personTax a 0).tax, "single")
    | [a, b] => coupleTax a b c.married
    | _ => (0, "")
  let ni := sumInts (c.adults.map fun a => class1.amount (gbp a.wages))
  let cb := childBenefit (c.children.filter (·.age < 20)).length
  let ani := incs.foldl max 0
  let ben := cb - hicbc ani cb
  (it, ni, ben, el)

end Fidelity.Uk
