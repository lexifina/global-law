import SkTax.Country

/-!
# Theorems for all inputs (no `sorry`, no `native_decide`)

Kernel theorems instantiated for § 15, and the statute's own structure: the § 11 withdrawals (where they start, where
they end, what they add to the marginal rate), the § 33 ods. 11 reduction (10 % per child), the § 32a premium that can
no longer be positive, and the two § 4 ods. 1 bases with two 19 % bands.
-/

namespace SkTax
open TaxKernel

/-! ## § 15: the schedule (kernel) -/

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem sched_maxRate : sched.maxRate = 2500 := by decide
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
theorem sched_zero : sched.ticks 0 = 0 := by decide

theorem sched_ticks_eq (x : Int) :
    sched.ticks x = 1900 * pos (min x 4844143 - 0) + 2500 * pos (x - 4844143) := rfl

theorem marginal_19 (b : Int) (h0 : 0 ≤ b) (h : b + 1 ≤ 4844143) : sched.ticks (b + 1) - sched.ticks b = 1900 := by
  rw [sched_ticks_eq, sched_ticks_eq]; unfold pos; omega

theorem marginal_25 (b : Int) (h : 4844143 ≤ b) : sched.ticks (b + 1) - sched.ticks b = 2500 := by
  rw [sched_ticks_eq, sched_ticks_eq]; unfold pos; omega

/-- **Two § 4 ods. 1 bases, two 19 % bands** (kernel `separate_le_joint`): taxing an amount as two bases (§ 4 ods. 1
písm. a) and b), each with its own 176,8 × ŽM threshold under § 15 písm. a) bod 1 and bod 3) never costs more than
taxing it as one. -/
theorem two_bases_le_one {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    sched.ticks a + sched.ticks b ≤ sched.ticks (a + b) :=
  separate_le_joint _ sched_convex sched_zero ha hb

/-- ... and with both bases at the threshold the saving is 6 % of 48 441,43 € = 2 906,49 € (cents). -/
theorem two_bases_saving : taxSched 9688286 - (taxSched 4844143 + taxSched 4844143) = 290649 := by decide

/-! ## § 11 ods. 2: NČZD na daňovníka -/

theorem ncz21_eq : ncz21 = 575379 := by decide
theorem ncz928_eq : ncz928 = 2542627 := by decide
theorem ncz442_eq : ncz442 = 1211036 := by decide
theorem th1768_eq : th1768 = 4844143 := by decide
theorem sp192_eq : sp192 = 526061 := by decide
theorem sp634_eq : sp634 = 1737097 := by decide

/-- Continuous where the withdrawal starts (92,8 × ŽM = 25 426,27 €). -/
theorem ncz_continuous : nczTaxpayer 2542627 = 575379 ∧ nczTaxpayer 2542628 = 575379 ∧ nczTaxpayer 2542631 = 575378 := by
  decide

/-- Inside the band, 4 cents more base withdraw exactly 1 cent of allowance. -/
theorem ncz_step (zd : Int) (h1 : 2542627 < zd) (h2 : zd + 4 ≤ 4844143) :
    nczTaxpayer (zd + 4) = nczTaxpayer zd - 1 := by
  simp only [nczTaxpayer, ncz928_eq, ncz442_eq, rh, divR, pos, Int.reduceMul]
  rw [if_neg (by omega), if_neg (by omega)]; omega

/-- The allowance is gone exactly where the 25 % rate starts (4 × 44,2 = 176,8 × ŽM). -/
theorem ncz_zero (zd : Int) (h : 4844143 ≤ zd) : nczTaxpayer zd = 0 := by
  simp only [nczTaxpayer, ncz928_eq, ncz442_eq, rh, divR, pos, Int.reduceMul]
  rw [if_neg (by omega)]; omega

/-- So in the band the base after the allowance grows by 5 cents for 4 cents of base: the 19 % rate acts as
23,75 % (and the 25 % band starts with no allowance left, no overlap). -/
theorem ncz_band_marginal (zd : Int) (h1 : 2542627 < zd) (h2 : zd + 4 ≤ 4844143) :
    (zd + 4 - nczTaxpayer (zd + 4)) - (zd - nczTaxpayer zd) = 5 := by
  rw [ncz_step zd h1 h2]; omega

/-! ## § 11 ods. 3: NČZD na manželku (manžela) -/

theorem spouse_continuous : nczSpouse 4844143 0 = 526061 ∧ nczSpouse 4844144 0 = 526061 := by decide

theorem spouse_step (zd : Int) (h1 : 4844143 < zd) (h2 : zd + 4 ≤ 6948388) :
    nczSpouse (zd + 4) 0 = nczSpouse zd 0 - 1 := by
  simp only [nczSpouse, th1768_eq, sp634_eq, rh, divR, pos, Int.reduceMul]
  rw [if_neg (by omega), if_neg (by omega)]; omega

/-- The spouse allowance is gone at 4 × 63,4 = 253,6 × ŽM = 69 483,88 € of the claimant's base. -/
theorem spouse_zero (zd : Int) (h : 6948388 ≤ zd) : nczSpouse zd 0 = 0 := by
  simp only [nczSpouse, th1768_eq, sp634_eq, rh, divR, pos, Int.reduceMul]
  rw [if_neg (by omega)]; omega

/-- A sole earner with a dependent spouse, from 48 441,43 € to 69 483,88 € of base: the 25 % rate acts as 31,25 %
(5 cents of taxable base per 4 cents of base). -/
theorem spouse_band_marginal (zd : Int) (h1 : 4844143 < zd) (h2 : zd + 4 ≤ 6948388) :
    (zd + 4 - nczTaxpayer (zd + 4) - nczSpouse (zd + 4) 0) - (zd - nczTaxpayer zd - nczSpouse zd 0) = 5 := by
  rw [spouse_step zd h1 h2, ncz_zero zd (by omega), ncz_zero (zd + 4) (by omega)]; omega

/-! ## § 33 ods. 11: 10 % per child -/

theorem foldl_add_init (l : List Int) (a : Int) : l.foldl (· + ·) a = a + l.foldl (· + ·) 0 := by
  induction l generalizing a with
  | nil => simp
  | cons x l ih => simp only [List.foldl]; rw [ih (a + x), ih (0 + x)]; omega

theorem sumInts_replicate (n : Nat) (f : Kid → Int) (k : Kid) :
    sumInts ((List.replicate n k).map f) = n * f k := by
  induction n with
  | zero => simp [sumInts]
  | succ n ih =>
    simp only [List.replicate_succ, List.map_cons, sumInts, List.foldl] at ih ⊢
    rw [foldl_add_init, ih]; push_cast; rw [Int.add_mul, Int.one_mul]; omega

/-- A child under 15 all year (the OECD children 6 and 11). -/
def kidU15 : Kid := { age := 6 }

theorem kidU15_entitlement : kidU15.entitlement = 120000 := by decide
theorem kidU15_months : kidU15.nMonths = 12 := by decide

theorem kid_reduction_eq (b : Int) : kidU15.reduction b = (2 * (pos (b - 2574000) * 12) + 120) / 240 := by
  simp only [Kid.reduction, kidU15_months, bonusTaper_values.1, rh, divR, Int.reduceMul]

/-- **The § 33 ods. 11 withdrawal is 10 % per child**: with `n` children under 15, between 25 740 € and 37 740 € of base,
10 cents more base cost `n` cents of bonus. With the § 11 band (23,75 %) the tax on the last euro of base is
23,75 % + n × 10 %. -/
theorem bonus_taper_step (n : Nat) (b : Int) (h1 : 2574000 ≤ b) (h2 : b + 10 ≤ 3774000) :
    taperedBonus (List.replicate n kidU15) (b + 10) = taperedBonus (List.replicate n kidU15) b - n := by
  unfold taperedBonus
  simp only [sumInts_replicate]
  rw [kidU15_entitlement, kid_reduction_eq, kid_reduction_eq]
  have e1 : pos (120000 - (2 * (pos (b + 10 - 2574000) * 12) + 120) / 240) =
      pos (120000 - (2 * (pos (b - 2574000) * 12) + 120) / 240) - 1 := by unfold pos; omega
  rw [e1, Int.mul_sub, Int.mul_one]

/-- ... and the bonus of a child under 15 is gone at 37 740 € of base (31 740 € for a child of 15–17). -/
theorem bonus_gone : taperedBonus [kidU15] 3774000 = 0 ∧ taperedBonus [{age := 16}] 3174000 = 0 ∧
    taperedBonus [kidU15] 3773990 = 1 := by decide

/-- The § 33 ods. 6 cap and the ods. 11 reduction never bind together for up to 13 children under 15: above 25 740 €
the cap (at least 29 % of 1/12 of the base) exceeds 100 € per child. -/
theorem cap_slack : capMonth [kidU15] 2574000 1 = 62205 ∧ capMonth (List.replicate 6 kidU15) 2574000 1 = 137280 ∧
    137280 ≥ 13 * 10000 := by decide

/-! ## § 32a: the zamestnanecká prémia cannot be positive -/

theorem pctD_le (x bp : Int) (hx : 0 ≤ x) (hb : 0 ≤ bp) : 10000 * pctD x bp ≤ x * bp := by
  unfold pctD; have := Int.mul_nonneg hx hb; omega

theorem eeSocialMonth_le (v : Int) (hv : 0 ≤ v) : 10000 * eeSocialMonth v ≤ 940 * v := by
  unfold eeSocialMonth pctD sickEE oldEE invEE unempEE socMaxMonthly avgWage2023 pos
  dsimp only
  omega

theorem eeHealth_le (w : Int) (hw : 0 ≤ w) : 10000 * eeHealthYear w ≤ 400 * w := by
  unfold eeHealthYear pctD healthEE pos; omega

theorem zd5_lower (w : Int) (hw : 0 ≤ w) : 8660 * w ≤ 10000 * zd5Of w := by
  have h1 := eeSocialMonth_le (w / 12) (by omega)
  have h2 := eeSocialMonth_le (w - 11 * (w / 12)) (by omega)
  have h3 := eeHealth_le w hw
  unfold zd5Of eeSocialYear; unfold pos; omega

/-- **§ 32a is dead law in 2025**: for every income and every monthly minimum wage of at least 554 €, the premium is 0
(the § 5 ods. 8 base of 12 minimum wages, ≥ 86,6 % of them, exceeds the NČZD of 21 × ŽM = 5 753,79 €). The 2025
minimum wage is 816 €. -/
theorem premia_dead (mw w : Int) (hmw : 55400 ≤ mw) : premia mw w = 0 := by
  unfold premia
  split
  · rfl
  · dsimp only
    have hb := zd5_lower (max w (12 * mw)) (by omega)
    rw [if_neg (by rw [ncz21_eq]; omega)]

theorem premia_2025 (w : Int) : premia minWage2025 w = 0 := premia_dead _ w (by decide)

end SkTax
