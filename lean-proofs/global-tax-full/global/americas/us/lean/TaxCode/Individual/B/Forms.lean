import TaxCode.Individual.B.Deductions

/-!
# Group B: the 2025 IRS forms, line by line, agree with the statute

Each definition below follows one official 2025 worksheet literally (its line numbers in comments); each theorem proves
for all inputs that the worksheet gives the same amount as the statutory definition in `Deductions.lean`. A mismatch
would be a place where the form departs from the Code; none was found for these four.

Sources: Schedule 1-A (Form 1040) 2025 (created 11/4/25), Parts II, IV, V; Instructions for Schedule A (Form 1040)
2025, State and Local Tax Deduction Worksheet (line 5e).
-/

namespace TaxCode.Individual.B
open TaxCode.Individual

set_option linter.deprecated false

/-- Schedule 1-A lines 7–13 (qualified tips), given line 6 (tips) and line 3 (MAGI). Line 11: "If the resulting
number isn't a whole number, decrease the result to the next lower whole number." -/
def sched1aTips (fl : Filing) (line6 line3 : Int) : Int :=
  let l7 := min line6 25000
  let l9 : Int := if fl = .mfj then 300000 else 150000
  let l10 := line3 - l9
  if l10 ≤ 0 then l7
  else
    let l11 := l10 / 1000
    let l12 := l11 * 100
    max 0 (l7 - l12)

theorem sched1aTips_eq (h : Household) (m : Int) (f : Facts) (hf : h.filing ≠ .mfs) (hs : f.earnerSsn = true)
    (hq : 0 ≤ h.qualifiedTips) : sched1aTips h.filing h.qualifiedTips m = tipsDeduction h m f := by
  unfold sched1aTips tipsDeduction tipsReduction tipsThreshold
  have hne : ¬ (h.filing = .mfs ∨ f.earnerSsn = false) := by simp [hf, hs]
  rw [if_neg hne]
  cases hfl : h.filing <;> simp only [reduceCtorEq, ite_true, ite_false] <;> split <;> omega

/-- Schedule 1-A lines 15–21 (qualified overtime), given line 14c and line 3. -/
def sched1aOvertime (fl : Filing) (line14c line3 : Int) : Int :=
  let l15 := min line14c (if fl = .mfj then 25000 else 12500)
  let l17 : Int := if fl = .mfj then 300000 else 150000
  let l18 := line3 - l17
  if l18 ≤ 0 then l15
  else max 0 (l15 - (l18 / 1000) * 100)

theorem sched1aOvertime_eq (h : Household) (m : Int) (f : Facts) (hf : h.filing ≠ .mfs) (hs : f.earnerSsn = true)
    (hq : 0 ≤ h.qualifiedOvertime) : sched1aOvertime h.filing h.qualifiedOvertime m = overtimeDeduction h m f := by
  unfold sched1aOvertime overtimeDeduction tipsReduction tipsThreshold overtimeCap
  have hne : ¬ (h.filing = .mfs ∨ f.earnerSsn = false) := by simp [hf, hs]
  rw [if_neg hne]
  cases hfl : h.filing <;> simp only [reduceCtorEq, ite_true, ite_false] <;> split <;> omega

/-- Schedule 1-A lines 24–30 (car loan interest), given line 23 and line 3. Line 28: "If the resulting number isn't
a whole number, increase the result to the next higher whole number." -/
def sched1aCar (fl : Filing) (line23 line3 : Int) : Int :=
  let l24 := min line23 10000
  let l26 : Int := if fl = .mfj then 200000 else 100000
  let l27 := line3 - l26
  if l27 ≤ 0 then l24
  else
    let l28 := (l27 + 999) / 1000
    max 0 (l24 - l28 * 200)

theorem sched1aCar_eq (h : Household) (m : Int) (f : Facts) (hv : f.vinReported = true)
    (hq : 0 ≤ h.carLoanInterest) : sched1aCar h.filing h.carLoanInterest m = carLoanDeduction h m f := by
  unfold sched1aCar carLoanDeduction carReduction carThreshold
  simp only [hv, Bool.true_eq_false, ite_false]
  cases hfl : h.filing <;> simp only [reduceCtorEq, ite_true, ite_false] <;> split <;> omega

/-- Schedule 1-A lines 31–35 (seniors, per person), given line 3. Line 34 "Multiply line 33 by 6% (0.06)", rounded to
whole dollars under the Form 1040 instructions' rounding rule. -/
def sched1aSenior (fl : Filing) (line3 : Int) : Int :=
  let l32 : Int := if fl = .mfj then 150000 else 75000
  let l33 := line3 - l32
  if l33 ≤ 0 then 6000
  else max 0 (6000 - roundDollar (6 * l33) 100)

theorem sched1aSenior_eq (fl : Filing) (m : Int) : sched1aSenior fl m = seniorPerPerson fl m := by
  unfold sched1aSenior seniorPerPerson seniorThreshold roundDollar
  cases fl <;> simp only [reduceCtorEq, ite_true, ite_false] <;> split <;> omega

/-- Schedule 1-A lines 36a–37: each spouse with an SSN born before 2 January 1961 adds line 35; the separate-return bar
is the Part V caution ("If married, you must file jointly"). -/
theorem sched1aSenior_total (h : Household) (m : Int) (f : Facts) :
    seniorDeduction h m f = seniorCount h f * sched1aSenior h.filing m := by
  rw [sched1aSenior_eq]; rfl

/-- Schedule A instructions 2025, State and Local Tax Deduction Worksheet, given Schedule A line 5d and the MAGI of
lines 2–4. Line 1 "No" branch: 5d ≤ $10,000 ($5,000 MFS) is entered unchanged. -/
def scheduleASaltWorksheet (fl : Filing) (line5d line4 : Int) : Int :=
  if line5d ≤ (if fl = .mfs then 5000 else 10000) then line5d
  else
    let l1 : Int := 40000
    let l5 : Int := if fl = .mfs then 250000 else 500000
    let l9 :=
      if line4 ≤ l5 then l1
      else
        let l6 := line4 - l5
        let l7 := roundDollar (3 * l6) 10
        max (l1 - l7) 10000
    min (if fl = .mfs then roundDollar l9 2 else l9) line5d

theorem scheduleASalt_eq (h : Household) (m : Int) (ht : 0 ≤ h.stateLocalTaxes) :
    scheduleASaltWorksheet h.filing h.stateLocalTaxes m = saltDeduction h m := by
  unfold scheduleASaltWorksheet saltDeduction saltCap saltLimitAmount saltThreshold saltBase roundDollar
  cases h.filing <;> simp only [reduceCtorEq, ite_true, ite_false, Int.reduceMul] <;> split <;> (try split) <;> omega

-- `scheduleASalt_eq` relies on the worksheet's "No" branch being harmless: a 5d at or below the floor is never cut.

end TaxCode.Individual.B
