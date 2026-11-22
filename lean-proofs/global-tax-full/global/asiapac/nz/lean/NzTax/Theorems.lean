import NzTax.Basic

/-!
# New Zealand: properties proved for all inputs (no `sorry`)

1. The schedules (2025-26, 2024-25 composite, pre-31-July-2024) are progressive: monotone, convex, marginal rate =
   band rate, no jump (kernel one-liners).
2. **Table = statute.** IRD's payroll formula "multiply annual income by 17.5% and subtract $1,092.00 ..." (spec
   2025-26 s. 5.2 step 3) equals the sch 1 pt A schedule for every whole-dollar income.
3. **Composite rates.** Each 2024-25 composite rate is the day-weighted average of the old and new rates (121 and
   244 days) rounded *down* to 0.01 %, so the composite tax never exceeds the day-weighted tax, for every income.
4. **IETC.** At most $520; nil below $24,000; a $520 notch at $24,000 (one more cent of net income gives $520);
   in the abatement band each extra dollar removes exactly 13 c; nil from $70,000 with no jump there.
5. **Working for Families.** The two-credit abatement (FTC first, the rest off the IWTC) is the same as abating
   the sum once; the MFTC tops after-tax income up to exactly the threshold (a 100 % withdrawal by construction).
-/

namespace NzTax
open TaxKernel

/-! ## 1. Schedules -/

theorem sched2025_progressive : sched2025.progressive = true := by decide
theorem sched2024_progressive : sched2024.progressive = true := by decide
theorem schedOld_progressive : schedOld.progressive = true := by decide

theorem sched2025_mono : Monotone' sched2025.ticks :=
  Schedule.ticks_mono_of_progressive sched2025 sched2025_progressive
theorem sched2024_mono : Monotone' sched2024.ticks :=
  Schedule.ticks_mono_of_progressive sched2024 sched2024_progressive
theorem sched2025_convex : Convex sched2025.ticks := Schedule.ticks_convex sched2025 sched2025_progressive
theorem sched2024_convex : Convex sched2024.ticks := Schedule.ticks_convex sched2024 sched2024_progressive
theorem sched2025_marginal (x : Int) : sched2025.ticks (x + 1) - sched2025.ticks x = sched2025.rate x :=
  Schedule.ticks_succ sched2025 x

/-- Individual assessment with a convex schedule: two partners with incomes `a`, `b` never pay less than they
would under income splitting (the generic splitting theorem), i.e. New Zealand's lack of splitting costs couples
with unequal incomes, never benefits them. -/
theorem nz_split_ok (a b : Int) : splitting sched2025.ticks a b ≤ separate sched2025.ticks a b :=
  splitting_le_separate _ sched2025_convex sched2025_mono a b

/-! ## 2. IRD's payroll formula = the schedule -/

/-- IRD Payroll Calculations & Business Rules Specification 2025-26, s. 5.2 step 3 (and s. 5.3 step 5), in ticks
(cents × bp) for annual income `a` whole dollars: "If annual income is between $1 and $15,600 inclusive, multiply
annual income by 10.5%. ... between $15,601 and $53,500 inclusive, multiply annual income by 17.5% and subtract
$1092.00. ... between $53,501 and $78,100 ... 30% and subtract $7,779.50. ... between $78,101 and $180,000 ... 33% and
subtract $10,122.50. ... greater than $180,000 multiply annual income by 39% and subtract $20,922.50." -/
def specTicks (a : Int) : Int :=
  if a ≤ 0 then 0
  else if a ≤ 15600 then 1050 * (100 * a)
  else if a ≤ 53500 then 1750 * (100 * a) - 109200 * 10000
  else if a ≤ 78100 then 3000 * (100 * a) - 777950 * 10000
  else if a ≤ 180000 then 3300 * (100 * a) - 1012250 * 10000
  else 3900 * (100 * a) - 2092250 * 10000

theorem sched2025_eq : sched2025 =
    ⟨[⟨0, 1050⟩, ⟨1560000, 1750⟩, ⟨5350000, 3000⟩, ⟨7810000, 3300⟩, ⟨18000000, 3900⟩]⟩ := by decide
theorem sched2024_eq : sched2024 =
    ⟨[⟨0, 1050⟩, ⟨1400000, 1282⟩, ⟨1560000, 1750⟩, ⟨4800000, 2164⟩, ⟨5350000, 3000⟩, ⟨7000000, 3099⟩,
      ⟨7810000, 3300⟩, ⟨18000000, 3900⟩]⟩ := by decide
theorem schedOld_eq : schedOld =
    ⟨[⟨0, 1050⟩, ⟨1400000, 1750⟩, ⟨4800000, 3000⟩, ⟨7000000, 3300⟩, ⟨18000000, 3900⟩]⟩ := by decide

theorem spec_eq_statute (a : Int) : specTicks a = sched2025.ticks (nzd a) := by
  rw [sched2025_eq]
  simp only [specTicks, nzd, Schedule.ticks, bandsTicks, pos]
  split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> omega

/-! ## 3. Composite rates of 2024-25 -/

/-- The day weights (Special report p. 13: 121 days to 30 July 2024, 244 days after). -/
theorem days_total : daysOld + daysNew = daysYear := by decide

/-- Each composite rate is the day-weighted average rounded down to a whole basis point:
`365 × composite ≤ 121 × old + 244 × new < 365 × (composite + 1)`. -/
theorem composite_rates_round_down :
    (365 * 1282 ≤ 121 * 1750 + 244 * 1050 ∧ 121 * 1750 + 244 * 1050 < 365 * 1283) ∧
    (365 * 2164 ≤ 121 * 3000 + 244 * 1750 ∧ 121 * 3000 + 244 * 1750 < 365 * 2165) ∧
    (365 * 3099 ≤ 121 * 3300 + 244 * 3000 ∧ 121 * 3300 + 244 * 3000 < 365 * 3100) := by decide

/-- For every income, the composite tax is at most the day-weighted tax of the old and new schedules (the
rounding of the composite rates always favours the taxpayer), and less than 1 bp of income below it. -/
theorem composite_le_dayweighted (x : Int) :
    365 * sched2024.ticks x ≤ 121 * schedOld.ticks x + 244 * sched2025.ticks x ∧
    121 * schedOld.ticks x + 244 * sched2025.ticks x ≤ 365 * sched2024.ticks x + 365 * pos x := by
  rw [sched2024_eq, schedOld_eq, sched2025_eq]
  simp only [Schedule.ticks, bandsTicks, pos]
  omega

/-! ## 4. Independent earner tax credit (2025-26) -/

theorem ietc25_eq (ni : Int) : ietc p2025 ni = ietcSetting 520 24000 66000 70000 1300 ni := rfl

theorem ietc_le_max (ni : Int) : ietc p2025 ni ≤ 52000 := by
  rw [ietc25_eq]; unfold ietcSetting; split <;> (try simp only [nzd, pos, BP]) <;> omega

theorem ietc_nonneg (ni : Int) : 0 ≤ ietc p2025 ni := by
  rw [ietc25_eq]; unfold ietcSetting; split <;> (try simp only [nzd, pos, BP]) <;> omega

/-- The $520 notch at $24,000: one cent of net income more takes the credit from nil to $520. -/
theorem ietc_notch : ietc p2025 2400000 - ietc p2025 2399999 = 52000 := by decide

/-- In the abatement band ($66,000 to $70,000) every extra dollar removes exactly 13 cents. -/
theorem ietc_abatement_step (ni : Int) (h1 : 6600000 ≤ ni) (h2 : ni + 100 ≤ 7000000) :
    ietc p2025 ni - ietc p2025 (ni + 100) = 13 := by
  rw [ietc25_eq, ietc25_eq]; unfold ietcSetting
  rw [if_neg (by simp only [nzd]; omega), if_neg (by simp only [nzd]; omega)]
  simp only [nzd, pos, BP]; omega

/-- No jump at the top: the credit is already nil at $70,000 (520 − 13 % × 4,000 = 0) and stays nil above. -/
theorem ietc_top_continuous : ietc p2025 7000000 = 0 ∧ ietc p2025 7000001 = 0 := by decide

/-! ## 5. Working for Families -/

/-- The FTC-then-IWTC abatement equals one abatement of the combined credit (for non-negative amounts). -/
theorem shared_abatement (F I a : Int) (_hF : 0 ≤ F) (hI : 0 ≤ I) (ha : 0 ≤ a) :
    pos (F - a) + pos (I - pos (a - F)) = pos (F + I - a) := by
  unfold pos; omega

/-- The MFTC guarantees after-tax family income: below the threshold, income after tax + MFTC = threshold. -/
theorem mftc_tops_up (p : Params) (n nb0 nb12 : Nat) (fsi tax : Int) (hn : n ≠ 0)
    (h : fsi - tax ≤ nzd p.mftcThreshold) :
    (fsi - tax) + (wff p n nb0 nb12 fsi true true tax).mftc = nzd p.mftcThreshold := by
  simp only [wff, wffWith, hn, if_false, pos]
  have : (nzd p.mftcThreshold * 0 + nzd p.mftcThreshold * 1) / (0 + 1) = nzd p.mftcThreshold := by omega
  rw [this]; simp only [if_true]; omega

end NzTax
