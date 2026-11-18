import UsLoop.Core

/-!
# Headline scenarios (tax year 2025)

The households behind the theorems in `UsLoop.Theorems`. Every figure is computed by the model (`form1040F`); the
only thing added here is FICA on wages, which the model's return does not carry (it carries self-employment tax and
the 0.9% additional Medicare tax): §3101(a)/§3111(a) 6.2% up to the $176,100 contribution and benefit base (SSA,
2025) and §3101(b)(1)/§3111(b) 1.45%, each half rounded to the dollar.
-/

namespace UsLoop
open TaxCode.Individual

/-- One half (employee or employer) of FICA on wages `w`. -/
def ficaHalf (w : Int) : Int := roundDollar (62 * min (max 0 w) 176100) 1000 + roundDollar (145 * max 0 w) 10000

def p (a : Nat) : Person := { age := a }
def kids (n : Nat) : List Dependent := (List.range n).map fun i => { age := 5 + i }

/-! K03 carried interest: $1m of fund profit share as a fee (self-employment income of an investment manager, a
specified service business under §199A(d)(2)) or as long-term capital gain (§1061 holding period met). -/
def ciFee : Household := { filing := .mfj, head := p 45, spouse := some (p 45), wages := 500000, seIncome := 1000000 }
def ciCarry : Household := { filing := .mfj, head := p 45, spouse := some (p 45), wages := 500000, longTermGains := 1000000 }

/-! K20 an S-corporation owner (MFJ, non-SSTB, $1m profit, no other employees) chooses the salary `w`. The K-1 is the
profit less the salary and the employer's FICA; the salary is the business's §199A(b)(2)(B) W-2 wages. Burden =
the return plus both FICA halves. -/
def scorp (profit w : Int) : Household :=
  let k1 := profit - w - ficaHalf w
  { filing := .mfj, head := p 45, spouse := some (p 45), wages := w, otherIncome := k1, qbi := k1 }
def scorpBurden (profit w : Int) : Int := (form1040F { qbiW2Wages := w } (scorp profit w)).netTax + 2 * ficaHalf w

/-! K22 the same business at $200k as a sole proprietorship (Schedule C, SE tax) or an S corporation paying $80k. -/
def soleProp : Household := { filing := .single, head := p 45, seIncome := 200000 }
def scorpSingle (profit w : Int) : Household :=
  let k1 := profit - w - ficaHalf w
  { filing := .single, head := p 45, wages := w, otherIncome := k1, qbi := k1 }
def scorpSingleBurden (profit w : Int) : Int :=
  (form1040F { qbiW2Wages := w } (scorpSingle profit w)).netTax + 2 * ficaHalf w

/-! K32 pass-through entity tax: $550k of K-1 income, $27.5k of state income tax and $15k of property tax. -/
def ptetNo : Household :=
  { filing := .mfj, head := p 50, spouse := some (p 50), otherIncome := 550000, qbi := 550000,
    stateLocalTaxes := 42500 }
def ptetYes : Household := { ptetNo with otherIncome := 522500, qbi := 522500, stateLocalTaxes := 15000 }
def ptetFacts : B.Facts := { qbiW2Wages := 300000 }

/-! N1 separate returns for the child tax credit: $365k + $215k, four children on the lower earner's return. -/
def ctcJoint : Household :=
  { filing := .mfj, head := p 40, spouse := some (p 40), wages := 580000,
    wagesSpouse := 215000, dependents := kids 4 }
def ctcSepA : Household := { filing := .mfs, head := p 40, wages := 365000 }
def ctcSepB : Household := { filing := .mfs, head := p 40, wages := 215000, dependents := kids 4 }
def stdOnly : B.Facts := { electItemize := some false }

/-! K25b two $25k earners with two children: married (joint) or not (head of household with both children + single). -/
def mpJoint : Household :=
  { filing := .mfj, head := p 30, spouse := some (p 30), wages := 50000, wagesSpouse := 25000,
    dependents := [{ age := 4 }, { age := 7 }] }
def mpHoh : Household := { filing := .hoh, head := p 30, wages := 25000, dependents := [{ age := 4 }, { age := 7 }] }
def mpSingle : Household := { filing := .single, head := p 30, wages := 25000 }

/-! T2 a retired couple (67 and 67) with $40,000 of Social Security and long-term gains `g`. -/
def retired (g : Int) : Household :=
  { filing := .mfj, head := p 67, spouse := some (p 67), socialSecurity := 40000,
    longTermGains := g }

/-! K27 the EIC investment-income limit (§32(i), $11,950 for 2025). -/
def eicAt (i : Int) : Household :=
  { filing := .hoh, head := p 40, dependents := [{ age := 6 }], wages := 25000,
    taxableInterest := i }

/-! T1 the §86 'torpedo' with the senior deduction: single, 67, $40,000 of benefits, IRA withdrawals `x`. The senior
deduction is switched off through its SSN condition (§151(d)(5)(C)(iv)) to measure its part. -/
def torpedo (x : Int) : Household := { filing := .single, head := p 67, socialSecurity := 40000, iraDistributions := x }
def noSenior : B.Facts := { headSsn := false }

/-! K04 0% gain harvesting: MFJ with $80k wages. -/
def harvest (g : Int) : Household := { filing := .mfj, head := p 40, spouse := some (p 40), wages := 80000, longTermGains := g }

/-! K21 an SSTB S-corporation owner at $450k MFJ defers $23,500 into a 401(k). -/
def sstb (w : Int) : Household :=
  { filing := .mfj, head := p 50, spouse := some (p 50), wages := w,
    otherIncome := 300000, qbi := 300000 }
def sstbFacts : B.Facts := { qbiSstb := true, qbiW2Wages := 150000 }

end UsLoop
