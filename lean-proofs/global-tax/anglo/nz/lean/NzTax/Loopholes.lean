import NzTax.Theorems
import NzTax.Checks

/-!
# New Zealand: findings stated and proved on named households (2025-26 unless stated; cents)

* `wff_ietc_notch`: the IETC is barred while the family is entitled to Working for Families; when the last cent of
  WFF abates, each partner with net income in $24,000-$70,000 gets $520 at once. A couple with one child, $44,672
  each: one more dollar of pay raises net income by more than $1,040.
* `mftc_acc_over_100`, `mftc_sl_over_100`: in the minimum family tax credit band the MFTC tops up income *after
  income tax* to $35,316, but the ACC earners' levy (and a student loan repayment) is outside "after tax", so one
  more dollar of pay lowers net income: an effective marginal rate of 101.67 % (113.67 % with a student loan).
* `help_notch`: payments from others for household expenses count as family income only when they exceed $5,000
  for the year, and then in full (IRD "Working out your family income"): $1 more of help costs $1,350.27 of WFF for
  a family in the abatement band.
* `composite_timing`: a $5,000 bonus at $50,000 costs $144.90 more income tax in 2024-25 (composite 21.64 % band)
  than in 2025-26 ($141.40 net of the lower 2024-25 ACC levy).
* `spouse_split`: $60,000 of interest held by the non-earning spouse instead of the $200,000 earner saves
  $13,699.50 (no attribution of investment income between spouses), of which $520 is the spouse's IETC.
-/

namespace NzTax
open TaxKernel

/-- Net income (cents) of a two-earner couple with `n` children aged 6-11 and wages `a`, `b` (dollars):
pay − income tax + IETC (only when no WFF) − ACC + WFF. -/
def coupleNet (a b : Int) (n : Nat) : Int :=
  let ta := tax25 a
  let tb := tax25 b
  let w := wff p2025 n 0 0 (nzd (a + b)) true true (ta + tb)
  let ie := if w.total = 0 then ietc p2025 (nzd a) + ietc p2025 (nzd b) else 0
  nzd (a + b) - ta - tb + ie - accLevy p2025 (nzd a) - accLevy p2025 (nzd b) + w.total

theorem wff_ietc_notch : coupleNet 44673 44672 1 - coupleNet 44672 44672 1 > 104000 := by decide

/-- Net income (cents) of a sole parent of two children (6, 11) on wages `w`, with or without a student loan. -/
def soleNet (w : Int) (sl : Bool) : Int :=
  let t := tax25 w
  let W := wff p2025 2 0 0 (nzd w) true true t
  nzd w - t + W.total - accLevy p2025 (nzd w) - (if sl then studentLoan p2025 (nzd w) else 0)

/-- At $30,000 (above 20 hours a week at the 2025 minimum wage), $100 more pay leaves the family $1.67 poorer. -/
theorem mftc_acc_over_100 : soleNet 30100 false - soleNet 30000 false = -167 := by decide
/-- With a student loan, $100 more pay leaves the family $13.67 poorer. -/
theorem mftc_sl_over_100 : soleNet 30100 true - soleNet 30000 true = -1367 := by decide

/-- $5,001 of help with household expenses counts in full (IRD); $5,000 counts as nil. Family with 2 children and
$60,000 of family income: WFF falls by 27 % of $5,001. -/
theorem help_notch :
    (wff p2025 2 0 0 (nzd 60000) true true 0).total - (wff p2025 2 0 0 (nzd 65001) true true 0).total = 135027 := by
  decide

/-- 2024-25 vs 2025-26: the extra income tax on a $5,000 bonus at $50,000. -/
theorem composite_timing :
    (taxOn sched2024 (nzd 55000) - taxOn sched2024 (nzd 50000)) - (tax25 55000 - tax25 50000) = 14490 := by decide

/-- Income splitting with a spouse: $200,000 earner, $60,000 of interest. -/
theorem spouse_split :
    (tax25 260000 + 0) - (tax25 200000 + (tax25 60000 - ietc p2025 (nzd 60000))) = 1369950 := by decide

end NzTax
