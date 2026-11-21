import CaTax.Household

/-!
# Properties of the 2025 Canadian (federal + Ontario) model, for all inputs

Kernel instances (`TaxKernel.Theorems`) and statute-specific statements. No `sorry`.
-/

namespace CaTax
open TaxKernel

/-! ## The two rate schedules (ITA s. 117(2); OTA s. 6(1)) -/

theorem fed_progressive : fedSchedule.progressive = true := by decide
theorem on_progressive : onSchedule.progressive = true := by decide

/-- Federal tax before credits never falls when taxable income rises. -/
theorem fed_mono : Monotone' fedSchedule.ticks := Schedule.ticks_mono_of_progressive _ fed_progressive
theorem on_mono : Monotone' onSchedule.ticks := Schedule.ticks_mono_of_progressive _ on_progressive

/-- Both schedules are convex, so splitting income equally between spouses never raises their combined tax before
credits (Canada has no splitting; this bounds what income splitting between spouses can save). -/
theorem fed_convex : Convex fedSchedule.ticks := Schedule.ticks_convex _ fed_progressive
theorem on_convex : Convex onSchedule.ticks := Schedule.ticks_convex _ on_progressive

theorem fed_split_le_separate (a b : Int) :
    splitting fedSchedule.ticks a b ≤ separate fedSchedule.ticks a b :=
  splitting_le_separate _ fed_convex fed_mono a b

theorem on_split_le_separate (a b : Int) :
    splitting onSchedule.ticks a b ≤ separate onSchedule.ticks a b :=
  splitting_le_separate _ on_convex on_mono a b

/-- The marginal rate of each schedule is the rate of its band (one cent more, `rate` ticks more). -/
theorem fed_marginal (x : Int) : fedSchedule.ticks (x + 1) - fedSchedule.ticks x = fedSchedule.rate x :=
  Schedule.ticks_succ _ x

/-- The combined statutory top rate in Ontario is 33 % + 13.16 % × 1.56 (surtax): checked at a point in the top
band, where one more dollar of taxable income costs exactly 33 cents federal and 13.16 cents Ontario basic tax. -/
theorem top_rates : fedSchedule.rate (dol 300000) = 3300 ∧ onSchedule.rate (dol 300000) = 1316 := by decide

/-! ## The basic personal amount (ITA s. 118(1.1)) -/

theorem bpa_wellFormed : bpaTaper.WellFormed := by
  refine ⟨?_, ?_, ?_, rfl⟩ <;> decide

/-- The enhancement is withdrawn exactly over the 29 % bracket: it starts at the first dollar amount of
s. 117(2)(d) and ends at that of s. 117(2)(e), where the 33 % rate begins (the statute ties the taper to the
brackets, so the two can never drift apart when indexed). -/
theorem bpa_band_is_29pct_bracket :
    bpaTaper.start = dol 177882 ∧ bpaTaper.bandEnd = dol 253414 ∧
    fedSchedule.rate (dol 177882) = 2900 ∧ fedSchedule.rate (dol 253414) = 3300 := by decide

theorem bpa_antitone {x y : Int} (h : x ≤ y) : bpa y ≤ bpa x :=
  Taper.amount_antitone bpaTaper bpa_wellFormed h

theorem bpa_bounds (x : Int) : bpaMin ≤ bpa x ∧ bpa x ≤ bpaMax :=
  ⟨Taper.floor_le_amount bpaTaper x, Taper.amount_le_full bpaTaper bpa_wellFormed x⟩

/-- Inside the band, 75,532 dollars more net income remove exactly 1,591 dollars of basic personal amount, so the
federal marginal rate there is 29 % + 14.5 % × 1,591 / 75,532 (about 29.31 %): the kernel's taper theorem. -/
theorem bpa_step {inc : Int} (hs : bpaTaper.start ≤ inc) (hin : bpaTaper.floor < bpaTaper.amount (inc + bpaTaper.den)) :
    bpaTaper.amount (inc + bpaTaper.den) = bpaTaper.amount inc - bpaTaper.num :=
  Taper.amount_step bpaTaper bpa_wellFormed hs hin

/-! ## The Ontario tax reduction (OTA s. 20) doubles the Ontario marginal rate in its band -/

/-- OTA s. 20(1): the credit is "twice the individual's personal amount" less the tax otherwise payable `t`. In
the band `pa ≤ t ≤ 2·pa` the tax left is `2t − 2pa`: every dollar of Ontario tax costs two. -/
theorem on_reduction_band (pa t : Int) (h1 : pa ≤ t) (h2 : t ≤ 2 * pa) :
    t - min t (pos (2 * pa - t)) = 2 * t - 2 * pa := by
  unfold pos; omega

/-- Below the band the reduction wipes out the tax; above it the reduction is nil. -/
theorem on_reduction_below (pa t : Int) (h0 : 0 ≤ t) (h1 : t ≤ pa) : t - min t (pos (2 * pa - t)) = 0 := by
  unfold pos; omega
theorem on_reduction_above (pa t : Int) (h0 : 0 ≤ t) (h : 2 * pa ≤ t) : t - min t (pos (2 * pa - t)) = t := by
  unfold pos; omega

/-! ## The Ontario Health Premium (OTA s. 24(2)) -/

/-- The premium never exceeds $900. -/
theorem ohp_le_900 (x : Int) : ohp x ≤ dol 900 := by
  unfold ohp dol; simp only [divR, BP]; split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> omega

/-- And is never negative. -/
theorem ohp_nonneg (x : Int) : 0 ≤ ohp x := by
  unfold ohp dol pos; simp only [divR, BP]; split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> omega

/-! ## Canada child benefit (ITA s. 122.61): the independently indexed amounts do not meet at $81,222 -/

/-- With two children aged 6 to 17, the CCB rises by 23 cents when adjusted family net income passes $81,222 by one
cent: the indexed fixed reduction ($5,904) is below 13.5 % of the indexed band ($43,735 × 13.5 % = $5,904.225). -/
theorem ccb_two_children_jump :
    ccb [8, 12] (ccbT2 + 1) - ccb [8, 12] ccbT2 = 23 := by decide

/-- With three children the opposite: one more cent of income costs 35 cents of CCB ($8,310 > $8,309.65). -/
theorem ccb_three_children_notch :
    ccb [8, 10, 12] ccbT2 - ccb [8, 10, 12] (ccbT2 + 1) = 35 := by decide

end CaTax
