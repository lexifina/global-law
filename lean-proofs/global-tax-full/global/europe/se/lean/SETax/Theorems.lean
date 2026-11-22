import SETax.Tests

/-!
# Theorems for Sweden 2025: kernel instances and what the statute claims

Kernel instances (`TaxKernel.Theorems.*`): the state tax schedule (65 kap. 5 §) and the municipal flat rate are
progressive, monotone, convex, with marginal rate = band rate and no jump; the pensionsavgift (lag 1994:1744) is
monotone in income and has the kernel's floor notch at 42,3 % of pbb; the capital tax (65 kap. 7 §) is monotone.

Swedish properties, for every income (no sampling):
* `ga_bounds`: the grundavdrag of 63 kap. 3 § lies between 0,293 and 0,77 prisbasbelopp (17 300 and 45 300 kr
  after rounding up); `ga_le_ffi`: never more than the income (63 kap. 5 §).
* `jsa_le_municipal`: for a wage earner under 66 the jobbskatteavdrag never exceeds the municipal tax it is set
  against (the 67 kap. 7 § base never exceeds the arbetsinkomst), at Stockholm's rate and at the OECD's average.
* `jsa_max`: the 2025 jobbskatteavdrag is at most 44 657 kr in Stockholm.
* `ga_jump_272`, `jsa_jump_324`, `jsa_drop_808`: the 2025 formulas are not continuous at three joints (FINDINGS
  F4): the 63 kap. 3 § amount jumps up by 0,001 pbb at 2,72 pbb; the 67 kap. 7 § base jumps up by 0,000358 pbb at
  3,24 pbb and down by 0,00016 pbb at 8,08 pbb, where 100 kr more pay lowers the jobbskatteavdrag by 2 kr.
-/

namespace SETax
open TaxKernel

/-! ## Kernel instances -/

theorem state_progressive : (stateSchedule p2025).progressive = true := by decide
theorem municipal_progressive : (municipalSchedule p2025).progressive = true := by decide
theorem capital_progressive : (dual p2025).capital.progressive = true := by decide

theorem state_mono : Monotone' (stateSchedule p2025).ticks :=
  Schedule.ticks_mono_of_progressive _ state_progressive
theorem state_convex : Convex (stateSchedule p2025).ticks :=
  Schedule.ticks_convex _ state_progressive
/-- The marginal rate of the state tax on the krona `(x, x+1]` is the band's rate: 0 or 20 %. -/
theorem state_marginal (x : Int) :
    (stateSchedule p2025).ticks (x + 1) - (stateSchedule p2025).ticks x = (stateSchedule p2025).rate x :=
  Schedule.ticks_succ _ x
/-- No jump: one more krona of taxable income costs between 0 and 20 öre of state tax. -/
theorem state_lipschitz {x y : Int} (h : x ≤ y) :
    0 ≤ (stateSchedule p2025).ticks y - (stateSchedule p2025).ticks x ∧
      (stateSchedule p2025).ticks y - (stateSchedule p2025).ticks x ≤ (stateSchedule p2025).maxRate * (y - x) :=
  Schedule.ticks_lipschitz_of_progressive _ state_progressive h
theorem municipal_mono : Monotone' (municipalSchedule p2025).ticks :=
  Schedule.ticks_mono_of_progressive _ municipal_progressive

/-- The pensionsavgift is monotone in the (rounded) income. -/
theorem fee_ticks_mono {x y : Int} (h : x ≤ y) : (pensionFee p2025).ticks x ≤ (pensionFee p2025).ticks y :=
  Contribution.ticks_mono _ (by intro b hb; simp [pensionFee, Schedule.flat] at hb; subst hb; decide)
    (by intro b hb; simp [pensionFee, Schedule.flat] at hb; subst hb; decide) h

/-- The floor notch (kernel `Contribution.floor_notch`): at 24 873 kr the whole income becomes liable. -/
theorem fee_floor_notch :
    (pensionFee p2025).ticks (feeFloor p2025) - (pensionFee p2025).ticks (feeFloor p2025 - 1)
      = (pensionFee p2025).sched.ticks ((pensionFee p2025).base (feeFloor p2025)) :=
  Contribution.floor_notch _

theorem fee_floor_value : feeFloor p2025 = 24873 ∧ feeCeiling p2025 = 650442 := by decide

theorem capital_mono {x y : Int} (h : x ≤ y) : (dual p2025).capitalTicks x ≤ (dual p2025).capitalTicks y :=
  Dual.capitalTicks_mono _ (by intro b hb; simp [dual, Schedule.flat] at hb; subst hb; decide) h

/-! ## Grundavdrag -/

/-- The exact 63 kap. 3 § amount lies between 0,293 pbb (17 228,40 kr) and 0,77 pbb (45 276 kr), in 10⁻⁷ kr. -/
theorem baseN_bounds (f : Int) : 172284000000 ≤ baseN 58800 f ∧ baseN 58800 f ≤ 452760000000 := by
  unfold baseN kN
  dsimp only
  split
  · omega
  · split
    · omega
    · split
      · omega
      · split <;> omega

/-- 63 kap. 3 §: the ordinary grundavdrag 2025 is between 17 300 and 45 300 kr (0,293 and 0,77 pbb rounded up). -/
theorem ga_bounds (f : Int) : 17300 ≤ gaRaw p2025 false f ∧ gaRaw p2025 false f ≤ 45300 := by
  have h := baseN_bounds f
  unfold gaRaw roundUp100 ceilDiv N
  simp only [p2025]
  simp only [Bool.false_eq_true, ite_false]
  omega

/-- 63 kap. 5 §: never more than the income. -/
theorem ga_le_ffi (p : Params) (old : Bool) (f : Int) : ga p old f ≤ pos f := by
  unfold ga; omega

/-! ## Jobbskatteavdrag -/

/-- The 67 kap. 7 § base never exceeds the arbetsinkomst (10⁻⁷ kr), for any non-negative income. -/
theorem jsaBase_le (ai : Int) (_h : 0 ≤ ai) : jsaBaseN 58800 ai ≤ ai * N := by
  unfold jsaBaseN kN N
  dsimp only
  split
  · omega
  · split
    · omega
    · split <;> omega

/-- The base is at most 2,77616 pbb (reached at 8,08 pbb, just before the plateau of 2,776 pbb). -/
theorem jsaBase_le_top (ai : Int) : jsaBaseN 58800 ai ≤ 1632382080000 := by
  unfold jsaBaseN kN
  dsimp only
  split
  · omega
  · split
    · omega
    · split <;> omega

/-- The jobbskatteavdrag 2025 (Stockholm, under 66) never exceeds 44 657 kr: (2,77616 pbb − 17 300) × 30,60 %. -/
theorem jsa_max (ai g : Int) (hg : 17300 ≤ g) : jsaUnder66 p2025 ai g ≤ 44657 := by
  have h := jsaBase_le_top ai
  unfold jsaUnder66 pos N BP
  simp only [p2025]
  omega

/-- For a wage earner under 66 (arbetsinkomst = fastställd förvärvsinkomst) the jobbskatteavdrag never exceeds
the municipal tax it is set against (Stockholm 2025), for every wage. -/
theorem jsa_le_municipal (w : Int) (h : 0 ≤ w) :
    jsaUnder66 p2025 (ffi w) (ga p2025 false (ffi w))
      ≤ (municipalSchedule p2025).ticks (pos (ffi w - ga p2025 false (ffi w))) / BP := by
  have hf : 0 ≤ ffi w := by simp only [ffi, toMultiple, divR, pos]; omega
  have hb := jsaBase_le (ffi w) hf
  generalize ffi w = f at *
  generalize ga p2025 false f = g
  unfold jsaUnder66 municipalSchedule Schedule.flat Schedule.ticks bandsTicks pos N BP at *
  simp only [p2025] at *
  omega

/-- The same at the OECD's average municipal rate (32,41 %). -/
theorem jsa_le_municipal_oecd (w : Int) (h : 0 ≤ w) :
    jsaUnder66 p2025oecd (ffi w) (ga p2025oecd false (ffi w))
      ≤ (municipalSchedule p2025oecd).ticks (pos (ffi w - ga p2025oecd false (ffi w))) / BP := by
  have hf : 0 ≤ ffi w := by simp only [ffi, toMultiple, divR, pos]; omega
  have hb := jsaBase_le (ffi w) hf
  generalize ffi w = f at *
  generalize ga p2025oecd false f = g
  unfold jsaUnder66 municipalSchedule Schedule.flat Schedule.ticks bandsTicks pos N BP at *
  simp only [p2025oecd, p2025] at *
  omega

/-! ## Discontinuities of the 2025 formulas (the statute's coefficients do not meet at the joints) -/

/-- 63 kap. 3 §: at 2,72 pbb (159 936 kr) the second line ends at 0,423 + 0,20 × 1,73 = 0,769 pbb and the third
line is 0,77 pbb: the exact grundavdrag jumps by 0,001 pbb = 58,80 kr (hidden by the rounding up to 100). -/
theorem ga_jump_272 : baseN 58800 159937 - baseN 58800 159936 = 588000000 := by decide

/-- 67 kap. 7 §: at 3,24 pbb the second line ends at 1,812642 pbb and the third starts at 1,813 pbb: the base
jumps up by 21,05 kr (0,000358 pbb), plus the 19,9 % slope on the one krona. -/
theorem jsa_jump_324 : jsaBaseN 58800 190513 - jsaBaseN 58800 190512 = 210504000 + 1990 * 1000 := by decide

/-- 67 kap. 7 §: at 8,08 pbb the third line ends at 2,77616 pbb and the fourth is 2,776 pbb: the base drops by
9,41 kr. In whole kronor (arbetsinkomst in hundreds): 100 kr more arbetsinkomst lowers the Stockholm
jobbskatteavdrag from 44 656 to 44 654 kr. -/
theorem jsa_drop_808 :
    jsaBaseN 58800 475104 - jsaBaseN 58800 475105 = 94080000 ∧
    jsaUnder66 p2025 475100 17300 = 44656 ∧ jsaUnder66 p2025 475200 17300 = 44654 := by decide

end SETax
