import IeTax.Model

/-!
# Ireland 2025: theorems (no `sorry`)

Kernel instances (one line each) and Ireland's own properties:
* the income tax and USC schedules are progressive, monotone, convex, and the marginal rate is the band rate;
* **band transfer** (s. 15(3)): the increase is at most €35,000 and at most the lower spouse's income, so the
  married band never exceeds €88,000; and for any incomes the joint gross tax is never more than the two single
  gross taxes (`joint_gross_le_single`);
* **USC exemption notch** (s. 531AM(2)): €0 at €13,000, €79.82 at €13,000.01; above €13,000 USC is at least that;
* **PRSI** (SWCA s. 13(2)): a €2.43 notch at €352.01 a week (4.1 %), a marginal rate of rate + 1/6 inside the credit
  band, and a jump of less than a cent at €424 (the credit formula's €352.01 leaves 1/6 cent of credit at €424);
* **home carer credit** (s. 466A): a kernel `Credit`: never above €1,950, never rising with the carer's income;
* **age exemption** (s. 188): never more than 40 % of the excess over the limit while within twice the limit;
* **USC medical-card amount aligned** with the end of the 2 % band (s. 531AN(3) = Table Part 1 rows 1-2).
-/

namespace IeTax
open TaxKernel

/-! ## Schedules (kernel instances) -/
theorem single_progressive : (bands bandSingle).progressive = true := by decide
theorem spcc_progressive : (bands bandSPCC).progressive = true := by decide
theorem married_progressive : (bands bandMarried).progressive = true := by decide
theorem married_max_progressive : (bands (bandMarried + bandIncreaseCap)).progressive = true := by decide
theorem usc_progressive : uscSchedule.progressive = true := by decide
theorem usc_reduced_progressive : uscReducedSchedule.progressive = true := by decide

theorem single_mono : Monotone' (bands bandSingle).ticks :=
  Schedule.ticks_mono_of_progressive _ single_progressive
theorem single_convex : Convex (bands bandSingle).ticks := Schedule.ticks_convex _ single_progressive
theorem usc_convex : Convex uscSchedule.ticks := Schedule.ticks_convex _ usc_progressive
/-- The marginal rate is the band's rate (kernel `ticks_succ`). -/
theorem single_marginal (x : Int) : (bands bandSingle).ticks (x + 1) - (bands bandSingle).ticks x =
    (bands bandSingle).rate x := Schedule.ticks_succ _ x
/-- No jump anywhere in the income tax schedule: at most 40 % per unit. -/
theorem single_lipschitz {x y : Int} (h : x ≤ y) :
    (bands bandSingle).ticks y - (bands bandSingle).ticks x ≤ (bands bandSingle).maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ single_progressive h).2

/-! ## Band transfer, s. 15(3) -/
theorem bandIncrease_le_cap (a b : Int) : bandIncrease a b ≤ bandIncreaseCap := by
  unfold bandIncrease; omega
theorem bandIncrease_le_lower (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) : bandIncrease a b ≤ min a b := by
  unfold bandIncrease pos; omega
theorem bandIncrease_nonneg (a b : Int) : 0 ≤ bandIncrease a b := by
  unfold bandIncrease pos bandIncreaseCap eur; omega
/-- The married band is at most €88,000. -/
theorem married_band_le (a b : Int) : bandMarried + bandIncrease a b ≤ eur 88000 := by
  have := bandIncrease_le_cap a b
  unfold bandMarried bandIncreaseCap eur at *; omega

/-- The two amounts that must move together did: the two-earner married band (€53,000 + €35,000) is exactly two
single bands (2 × €44,000), as in 2022-2024 (€45,800 + €27,800 = 2 × €36,800; €49,000 + €31,000 = 2 × €40,000;
€51,000 + €33,000 = 2 × €42,000; Revenue chart), and the Part 2 band is the single band + €4,000. -/
theorem married_cap_two_singles : bandMarried + bandIncreaseCap = 2 * bandSingle := by decide
theorem spcc_band_plus4000 : bandSPCC = bandSingle + eur 4000 := by decide

/-- The two-band schedule written out. -/
theorem bands_ticks (B x : Int) :
    (bands B).ticks x = 2000 * pos (min x B - 0) + 4000 * pos (x - B) := rfl

/-- Joint assessment never charges more gross tax than two single assessments: the joint band
€53,000 + min(€35,000, lower income) always covers what the two €44,000 bands cover. -/
theorem joint_gross_le_single (i1 i2 : Int) (h1 : 0 ≤ i1) (h2 : 0 ≤ i2) :
    (bands (bandMarried + bandIncrease i1 i2)).ticks (i1 + i2)
      ≤ (bands bandSingle).ticks i1 + (bands bandSingle).ticks i2 := by
  simp only [bands_ticks, bandIncrease, bandMarried, bandSingle, bandIncreaseCap, eur, pos]
  omega

/-! ## USC, s. 531AM(2): the €13,000 notch -/
theorem usc_at_exempt : uscStd.ticks uscExempt = 0 := by decide
/-- One cent above €13,000 the whole income is charged: 0.5 % × €12,012 + 2 % × €988.01 = €79.8202. -/
theorem usc_notch : uscStd.ticks (uscExempt + 1) = 79820200 := by decide
/-- Above €13,000 the USC is never less than the notch. -/
theorem usc_above_exempt {a : Int} (h : uscExempt < a) : 79820200 ≤ uscStd.ticks a := by
  have hp := Schedule.progressive_parts usc_progressive
  have hm := Contribution.ticks_mono uscStd hp.2.2.1 hp.2.2.2 (show uscExempt + 1 ≤ a by omega)
  rw [usc_notch] at hm; exact hm
/-- The notch is the kernel's floor notch. -/
theorem usc_floor_notch : uscStd.ticks uscStd.floor - uscStd.ticks (uscStd.floor - 1) =
    uscStd.sched.ticks (uscStd.base uscStd.floor) := Contribution.floor_notch uscStd

/-- s. 531AN(3)'s amount for 2025 (€27,382, FA 2024 s. 2(1)(a)) equals the end of the 2 % band in Table Part 1
(€12,012 + €15,370, FA 2024 s. 2(1)(b)): the two amounts were updated together (as in FA 2020 and FA 2022). -/
theorem usc_medical_card_aligned : uscMedicalCardFrom = usc1 + usc2 := by decide

/-! ## PRSI Class A1, SWCA s. 13(2) (one week, units of 1/60000 cent) -/
/-- €352.00 a week: nothing. €352.01: 4.1 % less the full €12 credit = €2.4324 (a notch). -/
theorem prsi_notch_352 : prsiWeekX 410 35201 - prsiWeekX 410 35200 = 14594460 := by decide
theorem prsi_notch_352_oct : prsiWeekX 420 35201 - prsiWeekX 420 35200 = 16706520 := by decide

/-- Inside the credit band (€352.01 to €424) six more cents of pay cost 6 × the rate plus one cent: the marginal
rate is the PRSI rate + 1/6 (4.1 % + 16.67 % = 20.77 %). -/
theorem prsi_credit_band_marginal (w : Int) (h1 : prsiCreditBase ≤ w) (h2 : w + 6 ≤ prsiCreditTop) :
    prsiWeekX 410 (w + 6) - prsiWeekX 410 w = 6 * (6 * 410) + 60000 := by
  unfold prsiWeekX
  simp only [prsiWeeklyFloor, prsiCreditTop, prsiCreditMax, prsiCreditBase, eur] at *
  have a1 : ¬ (w + 6 ≤ 100 * 352) := by omega
  have a2 : (w + 6 ≤ 100 * 424) := by omega
  have a3 : ¬ (w ≤ 100 * 352) := by omega
  have a4 : (w ≤ 100 * 424) := by omega
  simp only [a1, a2, a3, a4, ↓reduceIte]
  unfold pos
  rw [Int.max_def, Int.max_def]
  split <;> split <;> omega

/-- At €424 the credit has not quite reached 0 (€12 − (€424 − €352.01)/6 = €0.0017): the step to €424.01 is the
rate on one cent plus 1/6 of a cent. The taper is continuous to within a cent. -/
theorem prsi_step_424 (r : Int) (h0 : 1 ≤ r) (h1 : r ≤ 10000) :
    prsiWeekX r 42401 - prsiWeekX r 42400 = 6 * r + 10000 := by
  unfold prsiWeekX prsiWeeklyFloor prsiCreditTop prsiCreditMax prsiCreditBase eur pos
  simp only [show ¬ ((42401 : Int) ≤ 100 * 352) by decide, show ¬ ((42400 : Int) ≤ 100 * 352) by decide,
    show ¬ ((42401 : Int) ≤ 100 * 424) by decide, show ((42400 : Int) ≤ 100 * 424) by decide, if_true, if_false]
  omega

/-! ## Home carer credit, s. 466A (kernel `Credit`) -/
theorem homeCarer_le_full (e i : Int) : homeCarerCr.value e i ≤ homeCarerCredit :=
  Credit.value_le_full homeCarerCr (by decide) (by decide) (by decide) rfl e i
theorem homeCarer_antitone (e : Int) {x y : Int} (h : x ≤ y) : homeCarerCr.value e y ≤ homeCarerCr.value e x :=
  Credit.value_antitone_inc homeCarerCr (by decide) (by decide) (by decide) rfl e h
/-- The credit is gone at €11,100 of carer income (7,200 + 2 × 1,950). -/
theorem homeCarer_zero : homeCarerCr.value 0 (eur 11100) = 0 := by decide

/-! ## Age exemption, s. 188 -/
theorem ageExemption_le (L t x : Int) (h1 : L < t) (h2 : t ≤ 2 * L) :
    ageExemption L t x ≤ ageMarginalRate * (t - L) / BP := by
  unfold ageExemption
  rw [if_neg (by omega), if_pos h2]
  exact Int.min_le_right _ _
theorem ageExemption_zero (L t x : Int) (h : t ≤ L) : ageExemption L t x = 0 := by
  unfold ageExemption; rw [if_pos h]

end IeTax
