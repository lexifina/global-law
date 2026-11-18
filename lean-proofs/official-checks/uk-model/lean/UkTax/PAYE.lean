import UkTax.Basic

/-!
# PAYE: HMRC's tax table routines (withholding)

The annual liability (ITA 2007 s. 23) is settled after the year; employers withhold during it by the PAYE tax table
routines, which HMRC publishes as a specification (Payroll technical specifications: Income Tax, "Specification for
PAYE tax table routines", version 24.0, February 2026; the method is that of earlier versions) with test data
("Software developers: payroll test data 2025 to 2026", PAYE Tax v1.0). This is that routine, for suffix codes, prefix
K codes, BR, D0–D3 and NT, cumulative or Week 1/Month 1, rest of the UK, Wales (C codes, same rates in 2025-26) and
Scotland (S codes). Units: `u` = 1/10 000 of a pound ("4 decimal places of a pound"), pence for results.

* Stage 2 (para 4.3.1): Free Pay (or K codes' Additional Pay) for week/month 1 from the code number: £10 × code + £9,
  ÷ 52 or 12, rounded up to the penny, the code split into 500s (£96.16 a week, £416.67 a month for each 500).
* Stage 3 (para 4.4): thresholds `c_i` = cumulative bandwidth × n ÷ 52 (or 12) to 4 dp, tested against them rounded
  up to £1 (`Cvalue`); taxable pay rounded down to £1; tax = threshold tax `k_(i-1)` + (pay − `c_(i-1)`) × rate, to
  4 dp, then rounded down to the penny.
* Stage 4 (para 4.5): this period's tax = tax to date less last period's, at most 50 % of the period's pay (the
  "overriding Regulatory limit"), the shortfall carried in the cumulative figure.
-/

namespace UkTax

structure PayeRegime where
  /-- Annual bandwidths (pounds) of all but the top rate. -/
  bands : List Int
  /-- Rates (basis points), one more than the bands. -/
  rates : List Int
  /-- Index (from 0) of the basic rate ("pointer to Basic Rate", Definition 6). -/
  basicIdx : Nat
  deriving Repr

/-- Rest of the UK and Wales, 2025-26: 20 % on £37,700, 40 % on £87,440, 45 % above. -/
def payeRUK : PayeRegime := { bands := [37700, 87440], rates := [2000, 4000, 4500], basicIdx := 0 }

/-- Scotland, 2025-26 (the Scottish rate resolution; HMRC's table): 19 % on £2,827, 20 % on £12,094, 21 % on
£16,171, 42 % on £31,338, 45 % on £62,710, 48 % above. -/
def payeScot : PayeRegime :=
  { bands := [2827, 12094, 16171, 31338, 62710], rates := [1900, 2000, 2100, 4200, 4500, 4800], basicIdx := 1 }

inductive PayeCode where
  | suffix (n : Nat)
  | kcode (n : Nat)
  | br
  | d (k : Nat)
  | nt
  deriving Repr, DecidableEq

/-- Para 4.3.1: Free Pay (or Additional Pay) for week or month 1, in pence; `per` is 52 or 12. -/
def freePay1 (code per : Nat) : Int :=
  if code = 0 then 0 else
  let q : Int := ((code - 1) / 500 : Nat)
  let r : Int := ((code - 1) % 500 + 1 : Nat)
  ceilDiv ((10 * r + 9) * 100) per + q * (if per = 52 then 9616 else 41667)

/-- Cumulative sums of a list (`[a, b, c]` ↦ `[a, a+b, a+b+c]`). -/
def cumsum (xs : List Int) : List Int := (xs.foldl (fun (acc : List Int × Int) x => (acc.1 ++ [acc.2 + x], acc.2 + x)) ([], 0)).1

/-- Para 4.4: tax to date (pence) on taxable pay to date `U` (in u) in period `n` of `per`. -/
def payeTaxToDate (g : PayeRegime) (U : Int) (n per : Nat) : Int :=
  if U ≤ 0 then 0 else
  let C := cumsum g.bands
  let K := cumsum ((g.bands.zip g.rates).map fun (b, r) => b * r)
  let c := C.map fun (x : Int) => x * 10000 * (n : Int) / (per : Int)   -- Definition 9, to 4 dp (u)
  let k := K.map fun (x : Int) => x * (n : Int) / (per : Int)           -- Definition 11 (u)
  let v := c.map fun (x : Int) => ceilDiv x 10000                       -- Definition 10, £1 above
  let j := (v.findIdx? fun (x : Int) => decide (U ≤ x * 10000)).getD c.length
  let T := U / 10000                                             -- para 4.4.4, £1 below
  let c0 := if j = 0 then 0 else c.getD (j - 1) 0
  let k0 := if j = 0 then 0 else k.getD (j - 1) 0
  (k0 + (T * 10000 - c0) * g.rates.getD j 0 / 10000) / 100

/-- One payment: the pay this period (pence), the period number, the code, Scottish or not, Week 1/Month 1 or not. -/
structure PayePayment where
  period : Nat
  pay : Int
  code : PayeCode
  scot : Bool
  w1 : Bool
  deriving Repr

/-- Tax to date (pence) before the regulatory limit, on pay to date `P` (pence). -/
def payeLiability (g : PayeRegime) (per : Nat) (code : PayeCode) (P : Int) (n : Nat) : Int :=
  match code with
  | .nt => 0
  | .br => (P / 100) * g.rates.getD g.basicIdx 0 / 100
  | .d k => (P / 100) * g.rates.getD (g.basicIdx + 1 + k) 0 / 100
  | .kcode m => payeTaxToDate g ((P + (n : Int) * freePay1 m per) * 100) n per
  | .suffix m => payeTaxToDate g ((P - (n : Int) * freePay1 m per) * 100) n per

/-- A run of payments to one or more employees (a new employee starts when the period number does not rise):
returns, for each payment, (tax this period, tax to date), in pence. Para 4.5: the regulatory limit is 50 %. -/
def payeRun (per : Nat) (ps : List PayePayment) : List (Int × Int) :=
  let step := fun (st : Int × Int × Nat × List (Int × Int)) (x : PayePayment) =>
    let (cum0, L0, last, out) := st
    let (cum, Lprev) := if x.period ≤ last then (0, 0) else (cum0, L0)
    let cum := cum + x.pay
    let g := if x.scot then payeScot else payeRUK
    let P := if x.w1 then x.pay else cum
    let n := if x.w1 then 1 else x.period
    let L := payeLiability g per x.code P n
    let prev := if x.w1 then 0 else Lprev
    let limit := x.pay * 5000 / 10000
    let (due, L') := if L - prev > limit then (limit, prev + limit) else (L - prev, L)
    (cum, (if x.w1 then Lprev else L'), x.period, out ++ [(due, if x.w1 then due else L')])
  (ps.foldl step (0, 0, 0, [])).2.2.2

/-- Para 4.3.1's worked constants: "(500 x £10 / 52 (rounded to 1p above) = £ 96.16", "(500 x £10 / 12 (rounded to
1p above) = £416.67"; code 1257L a month: 2 × £416.67 + £214.92 = £1,048.26. -/
theorem freePay_examples :
    ceilDiv (500 * 10 * 100) 52 = 9616 ∧ ceilDiv (500 * 10 * 100) 12 = 41667 ∧ freePay1 1257 12 = 104826 := by
  decide

end UkTax
