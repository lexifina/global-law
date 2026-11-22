import TaxCode.Individual.B.Deductions

/-!
# Group B: properties proved for all inputs

Each theorem below holds for every input satisfying its hypotheses; the concrete `decide` theorems are the
counterexamples and notches that the general statements predict (findings, see `FINDINGS.md`).
-/

namespace TaxCode.Individual.B
open TaxCode.Individual

set_option linter.deprecated false

/-! ## Arithmetic lemmas -/

/-- Rounding half up is monotone in the numerator when the multiplier is non-negative (nonlinear, so by hand). -/
theorem rd_mul_mono {c x y r : Int} (hc : 0 ≤ c) (hr : 0 < r) (h : x ≤ y) :
    roundDollar (c * x) r ≤ roundDollar (c * y) r := by
  unfold roundDollar
  apply Int.ediv_le_ediv (by omega)
  have := Int.mul_le_mul_of_nonneg_left h hc
  omega

/-- Rounding an exact multiple returns it. -/
theorem rd_exact (k r : Int) (hr : 0 < r) : roundDollar (k * r) r = k := by
  unfold roundDollar
  have : 2 * (k * r) + r = (2 * r) * k + r := by rw [Int.mul_comm k r, ← Int.mul_assoc]
  rw [this, Int.add_comm, Int.add_mul_ediv_left _ _ (by omega)]
  have : r / (2 * r) = 0 := Int.ediv_eq_zero_of_lt (by omega) (by omega)
  omega

/-! ## §164(b)(6)–(7): the SALT cap and its phase-down -/

/-- Unfold the SALT cap for a concrete filing status and finish with `omega`. -/
macro "salt_tac" : tactic => `(tactic| (simp only [saltCap, saltLimitAmount, saltThreshold, saltBase, roundDollar,
  reduceIte, reduceCtorEq, ite_true, ite_false, Int.reduceMul, Int.reduceAdd] at *; omega))

section Salt
variable (fl : Filing)

/-- At or below $500,000 MAGI (non-separate returns) the cap is the full $40,000. -/
theorem salt_cap_flat (hf : fl ≠ .mfs) (m : Int) (hm : m ≤ 500000) : saltCap fl m = 40000 := by
  cases fl <;> first | exact absurd rfl hf | salt_tac

/-- **The exact $300 per $1,000 rule.** Inside the band, each extra $1,000 of MAGI lowers the cap by exactly $300. -/
theorem salt_step_300 (hf : fl ≠ .mfs) (m : Int) (h1 : 500000 ≤ m) (h2 : m + 1000 ≤ 600000) :
    saltCap fl (m + 1000) = saltCap fl m - 300 := by
  cases fl <;> first | exact absurd rfl hf | salt_tac

/-- The phase-down ends exactly at $600,000: the cap is $10,000 from there on ... -/
theorem salt_floor (hf : fl ≠ .mfs) (m : Int) (hm : 600000 ≤ m) : saltCap fl m = 10000 := by
  cases fl <;> first | exact absurd rfl hf | salt_tac

/-- ... and strictly above $10,000 below that — except that half-up rounding of the 30% reduction reaches the floor
$1 early, at $599,999. -/
theorem salt_above_floor (hf : fl ≠ .mfs) (m : Int) (hm : m < 599999) : 10000 < saltCap fl m := by
  cases fl <;> first | exact absurd rfl hf | salt_tac

/-- In the band the cap is exactly $40,000 minus 30% of the excess (half-dollar rounding only). -/
theorem salt_closed_form (hf : fl ≠ .mfs) (m : Int) (h1 : 500000 ≤ m) (h2 : m ≤ 600000) :
    saltCap fl m = 40000 - (6 * (m - 500000) + 10) / 20 := by
  cases fl <;> first | exact absurd rfl hf | salt_tac

/-- The cap never rises with MAGI, for every filing status. -/
theorem salt_cap_antitone (m m' : Int) (h : m ≤ m') : saltCap fl m' ≤ saltCap fl m := by
  cases fl <;> salt_tac

/-- One more dollar of MAGI lowers the cap by at most $1 (in fact by $0 or $1: the 30% rate plus rounding). -/
theorem salt_cap_step (m : Int) : saltCap fl m ≤ saltCap fl (m + 1) + 1 := by
  cases fl <;> salt_tac

/-- The cap always lies between $10,000 ($5,000 separate) and $40,000 ($20,000 separate). -/
theorem salt_cap_bounds (m : Int) :
    (if fl = .mfs then 5000 else 10000) ≤ saltCap fl m ∧ saltCap fl m ≤ (if fl = .mfs then 20000 else 40000) := by
  cases fl <;> salt_tac

end Salt

/-- **Separate returns: 15%, ending at $350,000.** Because §164(b)(6)(B) halves the applicable limitation amount
after §164(b)(7)(B) has reduced it, a separate return loses $150 (not $300) per $1,000 ... -/
theorem salt_mfs_step_150 (m : Int) (h1 : 250000 ≤ m) (h2 : m + 1000 ≤ 350000) :
    saltCap .mfs (m + 1000) = saltCap .mfs m - 150 := by
  salt_tac

/-- ... reaches the $5,000 floor only at $350,000 MAGI ... -/
theorem salt_mfs_floor (m : Int) (h : 350000 ≤ m) : saltCap .mfs m = 5000 := by
  salt_tac

/-- ... and at $300,000 (where a 30% rate on a $20,000 cap would have hit $5,000) still allows $12,500. -/
theorem salt_mfs_at_300k : saltCap .mfs 300000 = 12500 := by decide

/-- A couple splitting income evenly gets at least as large a combined SALT cap filing separately as jointly
(for each spouse at MAGI m versus the couple at 2m), strictly more inside the band. -/
theorem salt_split_ge_joint (m : Int) : saltCap .mfj (2 * m) ≤ 2 * saltCap .mfs m := by
  salt_tac

theorem salt_split_beats_joint : saltCap .mfj 600000 = 10000 ∧ 2 * saltCap .mfs 300000 = 25000 := by decide

/-- Two unmarried individuals each get a $40,000 cap; married filing jointly they share one $40,000 cap. -/
theorem salt_marriage_penalty (m : Int) (hm : m ≤ 250000) :
    saltCap .single m + saltCap .single m = 2 * saltCap .mfj (m + m) := by
  rw [salt_cap_flat .single (by decide) m (by omega), salt_cap_flat .mfj (by decide) (m + m) (by omega)]
  decide

theorem salt_floor_rounding : saltCap .single 599998 = 10001 ∧ saltCap .single 599999 = 10000 := by decide

/-- The deduction never exceeds taxes paid and never falls below the smaller of taxes paid and $10,000 ($5,000). -/
theorem salt_deduction_bounds (h : Household) (m : Int) :
    saltDeduction h m ≤ max 0 h.stateLocalTaxes ∧
    min (max 0 h.stateLocalTaxes) (if h.filing = .mfs then 5000 else 10000) ≤ saltDeduction h m := by
  have := salt_cap_bounds h.filing m
  unfold saltDeduction
  constructor <;> omega

/-- **Effective marginal effect on itemized deductions.** With taxes paid of at least $40,000 and no AGI-dependent
items besides SALT, every $1,000 of MAGI in $500,000–$600,000 removes exactly $300 of itemized deductions. -/
theorem itemized_salt_step (h : Household) (hf : h.filing ≠ .mfs) (ht : 40000 ≤ h.stateLocalTaxes)
    (hc : h.charitableCash ≤ 0) (hmed : h.medicalExpenses ≤ 0) (agi : Int) (h1 : 500000 ≤ agi)
    (h2 : agi + 1000 ≤ 600000) : itemized h (agi + 1000) = itemized h agi - 300 := by
  have s1 := salt_step_300 h.filing hf agi h1 h2
  have b1 := salt_cap_bounds h.filing agi
  have b2 := salt_cap_bounds h.filing (agi + 1000)
  simp only [itemized, magi, saltDeduction, charityDeduction, medicalDeduction, roundDollar]
  simp only [Int.add_zero]
  have : h.filing = .mfs ↔ False := ⟨hf, False.elim⟩
  simp only [this, ite_false] at b1 b2
  omega

/-! ## §151(d)(5)(C): enhanced deduction for seniors -/

theorem senior_bounds (fl : Filing) (m : Int) : 0 ≤ seniorPerPerson fl m ∧ seniorPerPerson fl m ≤ 6000 := by
  cases fl <;> simp [seniorPerPerson, seniorThreshold, roundDollar] <;> omega

theorem senior_antitone (fl : Filing) (m m' : Int) (h : m ≤ m') : seniorPerPerson fl m' ≤ seniorPerPerson fl m := by
  cases fl <;> simp [seniorPerPerson, seniorThreshold, roundDollar] <;> omega

/-- Per person, one more dollar of MAGI costs at most $1 of deduction (6 cents plus rounding). -/
theorem senior_step (fl : Filing) (m : Int) : seniorPerPerson fl m ≤ seniorPerPerson fl (m + 1) + 1 := by
  cases fl <;> simp [seniorPerPerson, seniorThreshold, roundDollar] <;> omega

/-- The 6% rate exactly: $6 per $100 of MAGI inside the band. -/
theorem senior_rate (fl : Filing) (m : Int) (h1 : seniorThreshold fl ≤ m) (h2 : m + 100 ≤ seniorThreshold fl + 100000) :
    seniorPerPerson fl (m + 100) = seniorPerPerson fl m - 6 := by
  cases fl <;> simp_all [seniorPerPerson, seniorThreshold, roundDollar] <;> omega

/-- The phase-out ends $100,000 above the threshold (MAGI $175,000 single, $250,000 joint) — in fact $8 earlier,
because 6% of $99,992 already rounds to $6,000. -/
theorem senior_gone (fl : Filing) (m : Int) (h : seniorThreshold fl + 99992 ≤ m) : seniorPerPerson fl m = 0 := by
  cases fl <;> simp_all [seniorPerPerson, seniorThreshold, roundDollar] <;> omega

theorem senior_end_exact : seniorPerPerson .single 174991 = 1 ∧ seniorPerPerson .single 174992 = 0 := by decide

theorem seniorCount_bounds (h : Household) (f : Facts) : 0 ≤ seniorCount h f ∧ seniorCount h f ≤ 2 := by
  unfold seniorCount
  split
  · omega
  · cases h.spouse <;> simp only [] <;> split <;> (try split) <;> omega

/-- The whole deduction is between $0 and $12,000 and never rises with MAGI. -/
theorem seniorDeduction_bounds (h : Household) (m : Int) (f : Facts) :
    0 ≤ seniorDeduction h m f ∧ seniorDeduction h m f ≤ 12000 := by
  have hc := seniorCount_bounds h f
  have hs := senior_bounds h.filing m
  unfold seniorDeduction
  generalize seniorCount h f = c at *
  generalize seniorPerPerson h.filing m = s at *
  constructor
  · exact Int.mul_nonneg hc.1 hs.1
  · have : c * s ≤ 2 * s := Int.mul_le_mul_of_nonneg_right hc.2 hs.1
    omega

theorem seniorDeduction_antitone (h : Household) (f : Facts) (m m' : Int) (hm : m ≤ m') :
    seniorDeduction h m' f ≤ seniorDeduction h m f := by
  unfold seniorDeduction
  exact Int.mul_le_mul_of_nonneg_left (senior_antitone _ _ _ hm) (seniorCount_bounds h f).1

/-- Two seniors on a joint return lose at most $2 per extra dollar (12 cents plus rounding). -/
theorem seniorDeduction_step (h : Household) (f : Facts) (m : Int) :
    seniorDeduction h m f ≤ seniorDeduction h (m + 1) f + 2 := by
  have hc := seniorCount_bounds h f
  have hs := senior_step h.filing m
  unfold seniorDeduction
  generalize seniorCount h f = c at *
  generalize seniorPerPerson h.filing m = s at *
  generalize seniorPerPerson h.filing (m + 1) = s' at *
  have h1 : c * (s - s') ≤ c * 1 := Int.mul_le_mul_of_nonneg_left (by omega) hc.1
  have h2 : c * 1 ≤ 2 * 1 := Int.mul_le_mul_of_nonneg_right hc.2 (by omega)
  rw [Int.mul_sub] at h1
  omega

/-- Interaction with §63(f): outside separate returns, every qualified individual for the senior deduction also
earns a §63(f)(1) age amount in the standard deduction (both use "attained age 65 before the close of the taxable
year"), so the senior count never exceeds the age-and-blind box count. -/
theorem senior_within_63f (h : Household) (f : Facts) (hf : h.filing ≠ .mfs) : seniorCount h f ≤ additionalCount h f := by
  unfold seniorCount additionalCount personBoxes
  have hm : (h.filing = .mfs) = False := propext ⟨hf, False.elim⟩
  simp only [hm, ite_false]
  cases hs : h.spouse with
  | none => simp only []; split <;> split <;> split <;> omega
  | some s =>
    simp only []
    cases hfl : h.filing <;> simp only [] <;> (repeat' split) <;> simp_all <;> omega

/-- The converse fails: a 70-year-old filing separately gets the §63(f) amount but no senior deduction
(§151(d)(5)(C)(v)). -/
theorem senior_mfs_counterexample :
    let h : Household := { filing := .mfs, head := { age := 70 }, spouse := some ({ age := 70 } : Person) }
    additionalCount h = 1 ∧ seniorCount h = 0 := by decide

/-- A senior who can be claimed as someone else's dependent: the §63(c)(5) limit cuts the standard deduction to
$1,350 + $2,000, but §151(d)(5)(C) has no dependency condition (unlike the exemption amount, §151(d)(2)), so the
full $6,000 is allowed on top. -/
theorem senior_dependent :
    let h : Household := { filing := .single, head := { age := 70 }, canBeClaimedAsDependent := true }
    standardDeduction h = 3350 ∧ seniorDeduction h 20000 = 6000 := by decide

/-- An itemizing senior keeps the $6,000 but loses the $2,000 §63(f) amount (which only lives in the standard
deduction): for a single 70-year-old with $30,000 of itemized deductions and AGI $60,000, taxable income before §199A
is $60,000 − $30,000 − $6,000. -/
theorem senior_itemizer :
    let h : Household := { filing := .single, head := { age := 70 }, mortgageInterest := 30000 }
    deduction h 60000 = 30000 ∧ taxableBeforeQbi h 60000 = 24000 ∧ standardDeduction h = 17750 := by decide

/-! ## §224 tips, §225 overtime, §163(h)(4) car loan interest -/

section Steps
variable (h : Household) (f : Facts)

theorem tips_bounds (m : Int) :
    0 ≤ tipsDeduction h m f ∧ tipsDeduction h m f ≤ min (max 0 h.qualifiedTips) 25000 := by
  unfold tipsDeduction tipsReduction; split <;> omega

theorem tips_antitone (m m' : Int) (hm : m ≤ m') : tipsDeduction h m' f ≤ tipsDeduction h m f := by
  unfold tipsDeduction tipsReduction
  split
  · omega
  · have : max 0 (m - tipsThreshold h.filing) / 1000 ≤ max 0 (m' - tipsThreshold h.filing) / 1000 :=
      Int.ediv_le_ediv (by decide) (by omega)
    omega

/-- One more dollar of MAGI costs at most $100 of tips deduction (a whole $1,000 step). -/
theorem tips_step (m : Int) : tipsDeduction h m f ≤ tipsDeduction h (m + 1) f + 100 := by
  unfold tipsDeduction tipsReduction; split <;> omega

/-- Over any span the loss is at most 10% of the span plus one step of $100. -/
theorem tips_average (m d : Int) (hd : 0 ≤ d) : tipsDeduction h m f ≤ tipsDeduction h (m + d) f + d / 10 + 100 := by
  unfold tipsDeduction tipsReduction; split <;> omega

/-- The tips deduction is gone $250,000 above the threshold ($400,000 single, $550,000 joint). -/
theorem tips_gone (m : Int) (hm : tipsThreshold h.filing + 250000 ≤ m) : tipsDeduction h m f = 0 := by
  unfold tipsDeduction tipsReduction; split <;> omega

theorem overtimeCap_pos (fl : Filing) : 12500 ≤ overtimeCap fl ∧ overtimeCap fl ≤ 25000 := by
  cases fl <;> decide

theorem overtime_bounds (m : Int) :
    0 ≤ overtimeDeduction h m f ∧ overtimeDeduction h m f ≤ min (max 0 h.qualifiedOvertime) (overtimeCap h.filing) := by
  have := overtimeCap_pos h.filing
  unfold overtimeDeduction tipsReduction; split <;> omega

theorem overtime_antitone (m m' : Int) (hm : m ≤ m') : overtimeDeduction h m' f ≤ overtimeDeduction h m f := by
  unfold overtimeDeduction tipsReduction
  split
  · omega
  · have : max 0 (m - tipsThreshold h.filing) / 1000 ≤ max 0 (m' - tipsThreshold h.filing) / 1000 :=
      Int.ediv_le_ediv (by decide) (by omega)
    omega

theorem overtime_step (m : Int) : overtimeDeduction h m f ≤ overtimeDeduction h (m + 1) f + 100 := by
  unfold overtimeDeduction tipsReduction; split <;> omega

/-- Overtime ends $125,000 above the threshold for $12,500 caps ($275,000), $250,000 above for joint ($550,000). -/
theorem overtime_gone (m : Int) (hm : tipsThreshold h.filing + 10 * overtimeCap h.filing ≤ m) :
    overtimeDeduction h m f = 0 := by
  have : overtimeCap h.filing = 12500 ∨ overtimeCap h.filing = 25000 := by cases h.filing <;> decide
  unfold overtimeDeduction tipsReduction; split <;> omega

theorem car_bounds (m : Int) : 0 ≤ carLoanDeduction h m f ∧ carLoanDeduction h m f ≤ min (max 0 h.carLoanInterest) 10000 := by
  unfold carLoanDeduction carReduction; split <;> omega

theorem car_antitone (m m' : Int) (hm : m ≤ m') : carLoanDeduction h m' f ≤ carLoanDeduction h m f := by
  unfold carLoanDeduction carReduction
  split
  · omega
  · have : (max 0 (m - carThreshold h.filing) + 999) / 1000 ≤ (max 0 (m' - carThreshold h.filing) + 999) / 1000 :=
      Int.ediv_le_ediv (by decide) (by omega)
    omega

/-- One more dollar of MAGI costs at most $200 of car-loan deduction. -/
theorem car_step (m : Int) : carLoanDeduction h m f ≤ carLoanDeduction h (m + 1) f + 200 := by
  unfold carLoanDeduction carReduction; split <;> omega

/-- "(or portion thereof)": the car-loan deduction is gone once MAGI exceeds the threshold by $49,001 — $999 before
the $50,000 that a continuous 20% rate would need ($149,001 single, $249,001 joint). -/
theorem car_gone (m : Int) (hm : carThreshold h.filing + 49001 ≤ m) : carLoanDeduction h m f = 0 := by
  unfold carLoanDeduction carReduction; split <;> omega

end Steps

/-- The tips/overtime rule ("for each $1,000", rounded down) and the car rule ("or portion thereof", rounded up)
differ: $1 over the threshold costs nothing for tips and $200 for car interest. -/
theorem steps_differ : tipsReduction .single 150001 = 0 ∧ carReduction .single 100001 = 200 := by decide

/-- **Notch, tips:** $1 of MAGI from $150,999 to $151,000 costs $100 of deduction. -/
theorem tips_notch :
    let h : Household := { filing := .single, head := { age := 30 }, qualifiedTips := 30000 }
    tipsDeduction h 150999 = 25000 ∧ tipsDeduction h 151000 = 24900 := by decide

/-- **Notch, car:** $1 of MAGI from $100,000 to $100,001 costs $200 of deduction. -/
theorem car_notch :
    let h : Household := { filing := .single, head := { age := 30 }, carLoanInterest := 10000 }
    carLoanDeduction h 100000 = 10000 ∧ carLoanDeduction h 100001 = 9800 ∧ carLoanDeduction h 149000 = 200 ∧
    carLoanDeduction h 149001 = 0 := by decide

/-! ## Itemized deductions: §170 cash, §213 medical -/

section Itemized
variable (h : Household) (f : Facts)

/-- The cash deduction is the lesser of the gift and 60% of AGI, never negative. -/
theorem charity_bounds (agi : Int) :
    0 ≤ charityDeduction h agi ∧ charityDeduction h agi ≤ max 0 h.charitableCash ∧
    charityDeduction h agi ≤ max 0 (roundDollar (60 * agi) 100) := by
  unfold charityDeduction; omega

/-- More AGI never lowers the charitable deduction, and raises it by at most the extra AGI (60 cents per dollar,
plus rounding): the one deduction in this group that *grows* with income. -/
theorem charity_mono (a a' : Int) (ha : a ≤ a') :
    charityDeduction h a ≤ charityDeduction h a' ∧ charityDeduction h a' ≤ charityDeduction h a + (a' - a) := by
  unfold charityDeduction roundDollar; omega

theorem medical_antitone (a a' : Int) (ha : a ≤ a') : medicalDeduction h a' ≤ medicalDeduction h a := by
  unfold medicalDeduction roundDollar; omega

theorem medical_step (a : Int) : medicalDeduction h a ≤ medicalDeduction h (a + 1) + 1 := by
  unfold medicalDeduction roundDollar; omega

/-- With non-negative AGI the medical deduction never exceeds the expenses. -/
theorem medical_le (a : Int) (ha : 0 ≤ a) : medicalDeduction h a ≤ max 0 h.medicalExpenses := by
  unfold medicalDeduction roundDollar; omega

end Itemized

/-- **§213(a) read literally with negative AGI**: "exceed 7.5 percent of adjusted gross income" — 7.5% of −$100,000 is
−$7,500, so $1,000 of expenses yields an $8,500 deduction (Schedule A line 4 does the same subtraction). -/
theorem medical_exceeds_expenses :
    medicalDeduction { filing := .single, head := { age := 50 }, medicalExpenses := 1000 } (-100000) = 8500 := by decide

/-- Itemized deductions can rise with AGI (charity) but by less than the AGI itself. -/
theorem itemized_lip (h : Household) (f : Facts) (a a' : Int) (ha : a ≤ a') :
    itemized h a' f ≤ itemized h a f + (a' - a) := by
  have s := salt_cap_antitone h.filing (magi a f) (magi a' f) (by unfold magi; omega)
  have c := charity_mono h a a' ha
  have m := medical_antitone h a a' ha
  unfold itemized saltDeduction
  omega

/-- One more dollar of AGI lowers itemized deductions by at most $2 (SALT $1, medical $1, both with rounding). -/
theorem itemized_step (h : Household) (f : Facts) (a : Int) : itemized h a f ≤ itemized h (a + 1) f + 2 := by
  have s := salt_cap_step h.filing (magi a f)
  have c := charity_mono h a (a + 1) (by omega)
  have m := medical_step h a
  have e : magi (a + 1) f = magi a f + 1 := by unfold magi; omega
  unfold itemized saltDeduction
  rw [e]
  omega

theorem deduction_lip (h : Household) (f : Facts) (a a' : Int) (ha : a ≤ a') :
    deduction h a' f ≤ deduction h a f + (a' - a) := by
  have := itemized_lip h f a a' ha
  unfold deduction
  split <;> omega

theorem deduction_step (h : Household) (f : Facts) (a : Int) : deduction h a f ≤ deduction h (a + 1) f + 2 := by
  have := itemized_step h f a
  unfold deduction
  split <;> omega

/-! ## The §63(b) deductions together, and taxable income -/

theorem belowTheLine_antitone (h : Household) (f : Facts) (a a' : Int) (ha : a ≤ a') :
    belowTheLine h a' f ≤ belowTheLine h a f := by
  have hm : magi a f ≤ magi a' f := by unfold magi; omega
  have := seniorDeduction_antitone h f _ _ hm
  have := tips_antitone h f _ _ hm
  have := overtime_antitone h f _ _ hm
  have := car_antitone h f _ _ hm
  unfold belowTheLine
  simp only []
  omega

/-- One more dollar of MAGI costs at most $402 of the four new deductions together ($2 seniors, $100 tips, $100
overtime, $200 car interest). -/
theorem belowTheLine_step (h : Household) (f : Facts) (a : Int) : belowTheLine h a f ≤ belowTheLine h (a + 1) f + 402 := by
  have e : magi (a + 1) f = magi a f + 1 := by unfold magi; omega
  have := seniorDeduction_step h f (magi a f)
  have := tips_step h f (magi a f)
  have := overtime_step h f (magi a f)
  have := car_step h f (magi a f)
  unfold belowTheLine
  simp only []
  rw [e]
  omega

/-- **Taxable income before §199A never falls when AGI rises** (no deduction in the group grows faster than AGI). -/
theorem taxableBeforeQbi_mono (h : Household) (f : Facts) (a a' : Int) (ha : a ≤ a') :
    taxableBeforeQbi h a f ≤ taxableBeforeQbi h a' f := by
  have := deduction_lip h f a a' ha
  have := belowTheLine_antitone h f a a' ha
  unfold taxableBeforeQbi
  omega

/-- ... but it can rise by much more than the extra dollar: at most $405 per $1 of AGI (1 + 2 + 402). -/
theorem taxableBeforeQbi_step (h : Household) (f : Facts) (a : Int) :
    taxableBeforeQbi h (a + 1) f ≤ taxableBeforeQbi h a f + 405 := by
  have := deduction_step h f a
  have := belowTheLine_step h f a
  unfold taxableBeforeQbi
  omega

/-- **More than $1 of deductions lost per $1 of income — car interest.** Single, $10,000 of qualified interest:
AGI $100,000 → $100,001 raises taxable income by $201. -/
theorem notch_car :
    let h : Household := { filing := .single, head := { age := 30 }, carLoanInterest := 10000 }
    taxableIncome h 100000 = 74250 ∧ taxableIncome h 100001 = 74451 := by decide

/-- **Tips and overtime together.** A joint return with $25,000 of each: AGI $300,999 → $301,000 raises taxable income
by $201. -/
def tipsOvertimeCouple : Household :=
  { filing := .mfj, head := { age := 40 }, spouse := some { age := 40 }, qualifiedTips := 25000,
    qualifiedOvertime := 25000 }

theorem notch_tips_overtime :
    taxableIncome tipsOvertimeCouple 300999 = 219499 ∧ taxableIncome tipsOvertimeCouple 301000 = 219700 := by decide

/-! ## §199A -/

section Qbi

/-- The phase-in never raises the per-business amount as taxable income rises (any `a`, `b`). -/
theorem qbiPhase_antitone (fl : Filing) (a b t t' : Int) (ht : t ≤ t') : qbiPhase fl t' a b ≤ qbiPhase fl t a b := by
  have hR : 0 < qbiRange fl := by cases fl <;> decide
  have zero : ∀ x, 0 ≤ x → b < a → 0 ≤ roundDollar ((a - b) * x) (qbiRange fl) := by
    intro x hx hab
    have := rd_mul_mono (c := a - b) (r := qbiRange fl) (x := 0) (y := x) (by omega) hR hx
    unfold roundDollar at this ⊢
    simp only [Int.mul_zero, Int.zero_add, Int.mul_zero] at this
    have : qbiRange fl / (2 * qbiRange fl) = 0 := Int.ediv_eq_zero_of_lt (by omega) (by omega)
    omega
  have top : ∀ x, x ≤ qbiRange fl → b < a → roundDollar ((a - b) * x) (qbiRange fl) ≤ a - b := by
    intro x hx hab
    have := rd_mul_mono (c := a - b) (r := qbiRange fl) (by omega) hR hx
    rwa [rd_exact _ _ hR] at this
  unfold qbiPhase
  by_cases h1 : t ≤ qbiThreshold fl
  · rw [if_pos h1]
    by_cases h2 : t' ≤ qbiThreshold fl
    · rw [if_pos h2]; exact Int.le_refl a
    · rw [if_neg h2]
      split
      · rename_i h3; have := zero (t' - qbiThreshold fl) (by omega) h3.2; omega
      · omega
  · rw [if_neg h1, if_neg (by omega : ¬ t' ≤ qbiThreshold fl)]
    by_cases h3 : t ≤ qbiThreshold fl + qbiRange fl ∧ b < a
    · rw [if_pos h3]
      by_cases h4 : t' ≤ qbiThreshold fl + qbiRange fl ∧ b < a
      · rw [if_pos h4]
        have := rd_mul_mono (c := a - b) (r := qbiRange fl) (by omega) hR
          (show t - qbiThreshold fl ≤ t' - qbiThreshold fl by omega)
        omega
      · rw [if_neg h4]
        have := top (t - qbiThreshold fl) (by omega) h3.2
        omega
    · have h4 : ¬ (t' ≤ qbiThreshold fl + qbiRange fl ∧ b < a) := fun ⟨p, q⟩ => h3 ⟨by omega, q⟩
      rw [if_neg h3, if_neg h4]
      exact Int.le_refl _

/-- At the end of the range the phase-in meets the full limit exactly: no cliff at $247,300 / $494,600. -/
theorem qbiPhase_continuous_at_end (fl : Filing) (a b : Int) :
    qbiPhase fl (qbiThreshold fl + qbiRange fl) a b = min a b := by
  have hR : 0 < qbiRange fl := by cases fl <;> decide
  unfold qbiPhase
  rw [if_neg (by omega)]
  split
  · rename_i h; rw [show qbiThreshold fl + qbiRange fl - qbiThreshold fl = qbiRange fl by omega, rd_exact _ _ hR]
    omega
  · rfl

/-- (Reviewer.) Pins the 2025 phase-in formula of §199A(b)(3)(B) for all inputs, not just its shape: halfway through
the range ($25,000 / $50,000 above the threshold) exactly half the excess of the 20%-of-QBI amount over the wage/property
amount is lost (TI $222,300 / $444,600, written as literals so a wrong `qbiThreshold` or `qbiRange` breaks it). A wrong range (e.g. the 2026 $75,000 / $150,000), a wrong threshold, or a phase-in that ignored `b`
fails this; `qbiPhase_antitone` and `qbiPhase_continuous_at_end` are also satisfied by `fun _ _ a b => min a b`. -/
theorem qbiPhase_midpoint (fl : Filing) (b k : Int) (hk : 0 < k) :
    qbiPhase fl (if fl = .mfj then 444600 else 222300) (b + 2 * k) b = b + k := by
  cases fl <;> simp only [qbiPhase, qbiThreshold, qbiRange, roundDollar, reduceCtorEq, ite_true, ite_false] <;> (repeat' split) <;> omega

/-- (Reviewer.) Pins the §199A(d)(3)(B) applicable percentage: halfway through the 2025 range an SSTB counts exactly
half of its QBI (or wages, or property). -/
theorem sstbShare_midpoint (fl : Filing) (k : Int) :
    sstbShare fl (if fl = .mfj then 444600 else 222300) (2 * k) = k := by
  cases fl <;> simp only [sstbShare, qbiThreshold, qbiRange, reduceCtorEq, ite_true, ite_false] <;> (repeat' split) <;> omega

theorem qbiDeduction_nonneg (h : Household) (t n : Int) (f : Facts) : 0 ≤ qbiDeduction h t n f := by
  unfold qbiDeduction; simp only []; omega

/-- §199A(a)(2): never more than 20% of the excess of taxable income over net capital gain. -/
theorem qbiDeduction_le_income (h : Household) (t n : Int) (f : Facts) :
    qbiDeduction h t n f ≤ roundDollar (20 * max 0 (t - n)) 100 := by
  unfold qbiDeduction roundDollar; simp only []; omega

/-- At or below the threshold (and not an SSTB) the deduction is the plain lesser of 20% of QBI and 20% of
(taxable income − net capital gain): W-2 wages and property do not matter. -/
theorem qbiDeduction_below (h : Household) (t n : Int) (f : Facts) (hs : f.qbiSstb = false)
    (ht : t ≤ qbiThreshold h.filing) :
    qbiDeduction h t n f = max 0 (min (roundDollar (20 * h.qbi) 100) (roundDollar (20 * max 0 (t - n)) 100)) := by
  unfold qbiDeduction qbiComponent qbiPhase
  simp only [hs, Bool.false_eq_true, ite_false, if_pos ht]

/-- **Taxable income after §199A never falls when taxable income before it rises** (non-SSTB, any QBI, wages,
property): the phase-in only lowers the deduction, and the 20%-of-income limit grows slower than income. -/
theorem qbi_net_mono (h : Household) (n : Int) (f : Facts) (hs : f.qbiSstb = false) (t t' : Int) (ht : t ≤ t') :
    t - qbiDeduction h t n f ≤ t' - qbiDeduction h t' n f := by
  have c := qbiPhase_antitone h.filing (roundDollar (20 * h.qbi) 100)
    (max (roundDollar (50 * f.qbiW2Wages) 100) (roundDollar (25 * f.qbiW2Wages) 100 + roundDollar (25 * f.qbiUbia) 1000))
    t t' ht
  unfold qbiDeduction qbiComponent
  simp only [hs, Bool.false_eq_true, ite_false]
  generalize qbiPhase h.filing t _ _ = p at *
  generalize qbiPhase h.filing t' _ _ = p' at *
  unfold roundDollar
  omega

/-- **Headline: taxable income is monotone in AGI** for every household without an SSTB: earning more never lowers
taxable income anywhere in group B (the notches below make it rise *faster* than income, never slower than zero). -/
theorem taxableIncome_mono (h : Household) (f : Facts) (hs : f.qbiSstb = false) (a a' : Int) (ha : a ≤ a') :
    taxableIncome h a f ≤ taxableIncome h a' f := by
  have t := taxableBeforeQbi_mono h f a a' ha
  have q := qbi_net_mono h (netCapitalGain h) f hs _ _ t
  unfold taxableIncome
  simp only []
  omega

/-- **The §199A phase-in loses more than $1 per $1.** A sole proprietor with $537,300 of QBI, no employees or
property, and a $300,000 cash gift to charity (within 60% of AGI): taxable income before §199A $237,300, inside the
2025 band. One more dollar of AGI raises taxable income by $3 (the deduction falls $2). -/
theorem notch_qbi :
    let h : Household := { filing := .single, head := { age := 45 }, qbi := 537300, charitableCash := 300000 }
    taxableBeforeQbi h 537300 = 237300 ∧ taxableIncome h 537300 = 215808 ∧ taxableIncome h 537301 = 215811 := by
  decide

/-- The per-dollar loss grows without bound with QBI: with $5,000,000 of QBI it is $20 per $1 (taxable income rises
$21). -/
def largeQbiOwner : Household :=
  { filing := .single, head := { age := 45 }, qbi := 5000000, charitableCash := 3000000, mortgageInterest := 1770000 }

theorem notch_qbi_large :
    taxableIncome largeQbiOwner 5016000 = 220000 ∧ taxableIncome largeQbiOwner 5016001 = 220021 := by decide

end Qbi

end TaxCode.Individual.B
