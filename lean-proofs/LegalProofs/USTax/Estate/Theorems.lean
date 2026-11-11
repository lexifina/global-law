import LegalProofs.USTax.Estate.Transfer

/-!
# What holds for every estate and every gift, not just the examples

* The rate table never decreases (`tentative_mono`), and above $1,000,000 it is a flat 40% (`top_rate`).
* The exclusion never decreased from one year to the next, 1977 to 2026 (`bea_mono`).
* An estate whose deductions use it up (everything to the spouse, to charity, to expenses) pays no estate tax
  (`full_marital_zero`); nor does one at or below its exclusion (`below_exclusion_zero`).
* Above the exclusion, from 2013 on, the estate tax is exactly 40% of the excess (`flat_forty`).
* Portability can at most double the survivor's exclusion (`dsue_le_bea`, `portability_cap`).
* Gifts within the annual exclusion are never taxable gifts (`annual_exclusion_free`).
* A gift sheltered by the credit lowers the estate tax by nothing: the estate pays as if the gift had stayed in the
  estate (`gift_no_escape`), since §2001(b) adds it back as an adjusted taxable gift.
* A transfer covered by allocated GST exemption bears no GST tax (`gst_exempt`).
-/

namespace Legal.USTax.Estate.Theorems
open Legal.USTax.Estate

/-! ## The rate table -/

theorem tent40_nonneg (x : Int) : 0 ≤ tent40 x := by
  unfold tent40 pct; repeat' split
  all_goals omega

theorem tent35_nonneg (x : Int) : 0 ≤ tent35 x := by
  unfold tent35 pct; repeat' split
  all_goals omega

theorem tent40_at (x : Int) (h : 1000000 < x) : tent40 x = 345800 + pct (x - 1000000) 40 := by
  unfold tent40; repeat' split
  all_goals first | rfl | omega

theorem tent40_ge (x : Int) (h : 1000000 ≤ x) : tent40 x = 345800 + pct (x - 1000000) 40 := by
  by_cases hx : x = 1000000
  · subst hx; decide
  · exact tent40_at x (by omega)

theorem tent45_nonneg (x : Int) : 0 ≤ tent45 x := by
  have := tent40_nonneg x
  unfold tent45 pct; repeat' split
  all_goals omega

theorem tentative_nonneg (y : Nat) (x : Int) : 0 ≤ tentative y x := by
  unfold tentative; split
  · exact tent35_nonneg x
  · split
    · exact tent45_nonneg x
    · exact tent40_nonneg x

theorem tent40_zero (x : Int) (h : x ≤ 0) : tent40 x = 0 := by unfold tent40; simp only [h, ↓reduceIte]
theorem tent35_zero (x : Int) (h : x ≤ 0) : tent35 x = 0 := by unfold tent35; simp only [h, ↓reduceIte]

theorem tentative_zero (y : Nat) (x : Int) (h : x ≤ 0) : tentative y x = 0 := by
  unfold tentative; split
  · exact tent35_zero x h
  · split
    · unfold tent45; simp only [show x ≤ 1000000 by omega, ↓reduceIte]; exact tent40_zero x h
    · exact tent40_zero x h

set_option maxHeartbeats 4000000 in
theorem tent40_step (x : Int) : tent40 x ≤ tent40 (x + 1) := by
  unfold tent40 pct; repeat' split
  all_goals omega

set_option maxHeartbeats 4000000 in
theorem tent35_step (x : Int) : tent35 x ≤ tent35 (x + 1) := by
  unfold tent35 pct; repeat' split
  all_goals omega

theorem tent45_step (x : Int) : tent45 x ≤ tent45 (x + 1) := by
  unfold tent45
  by_cases h1 : x + 1 ≤ 1000000
  · simp only [show x ≤ 1000000 by omega, h1, ↓reduceIte]; exact tent40_step x
  · by_cases h0 : x ≤ 1000000
    · have : x = 1000000 := by omega
      subst this; decide
    · simp only [h0, h1, ↓reduceIte]; unfold pct; repeat' split
      all_goals omega

theorem mono_of_step (f : Int → Int) (hs : ∀ x, f x ≤ f (x + 1)) (a : Int) :
    ∀ n : Nat, f a ≤ f (a + n) := by
  intro n; induction n with
  | zero => simp
  | succ n ih => have := hs (a + n); rw [show a + ((n + 1 : Nat) : Int) = a + n + 1 by omega]; omega

theorem mono_of_step' (f : Int → Int) (hs : ∀ x, f x ≤ f (x + 1)) (a b : Int) (h : a ≤ b) : f a ≤ f b := by
  have := mono_of_step f hs a (b - a).toNat
  rwa [show a + ((b - a).toNat : Int) = b by omega] at this

/-- **Monotonicity.** More transferred never means less tentative tax, in any year's table. -/
theorem tentative_mono (y : Nat) (a b : Int) (h : a ≤ b) : tentative y a ≤ tentative y b := by
  unfold tentative; split
  · exact mono_of_step' tent35 tent35_step a b h
  · split
    · exact mono_of_step' tent45 tent45_step a b h
    · exact mono_of_step' tent40 tent40_step a b h

/-- **The top rate.** From 2013, above $1,000,000 every further dollar is taxed at exactly 40%: from a starting amount
that is a multiple of $5 (every exclusion amount is), the extra tax on `d` more dollars is 40% of `d`, to the dollar. -/
theorem top_rate (y : Nat) (hy : top35 y = false) (hy' : top45 y = false) (a d : Int) (ha : 1000000 ≤ a)
    (h5 : a % 5 = 0) (hd : 0 ≤ d) : tentative y (a + d) - tentative y a = pct d 40 := by
  simp only [tentative, hy, hy', Bool.false_eq_true, ↓reduceIte]
  rw [tent40_ge _ (by omega), tent40_ge _ ha]; unfold pct; omega

/-! ## The exclusion -/

/-- The basic exclusion amount never went down, 1977 to 2026. -/
theorem bea_mono (a b : Nat) (h : a ≤ b) : bea a ≤ bea b := by
  unfold bea; repeat' split
  all_goals omega

theorem bea_nonneg (y : Nat) : 0 ≤ bea y := by
  unfold bea; repeat' split
  all_goals omega

theorem bea_from_2013 (y : Nat) (hy : 2013 ≤ y) :
    1000000 ≤ bea y ∧ bea y % 5 = 0 ∧ top35 y = false ∧ top45 y = false := by
  have h1 : top35 y = false := by
    unfold top35; simp; omega
  have h2 : top45 y = false := by
    unfold top45; simp; omega
  refine ⟨?_, ?_, h1, h2⟩ <;> (unfold bea; repeat' split) <;> omega

/-! ## The estate tax -/

/-- **Full marital deduction.** When the deductions (marital, charitable, expenses) take the whole gross estate and
there were no lifetime taxable gifts, the estate tax is zero, in every year. -/
theorem full_marital_zero (d : Death) (hg : d.gifts = []) (h : d.gross ≤ d.deductions) : d.tax = 0 := by
  have hb : d.base = 0 := by
    simp [Death.base, Death.taxableEstate, Death.adjustedTaxableGifts, hg]; omega
  have hp : d.giftTaxPayable = 0 := by simp [Death.giftTaxPayable, hg, schedule]
  have hc := tentative_nonneg d.year d.exclusion
  simp only [Death.tax, hb, hp, credit, tentative_zero d.year 0 (by omega)]
  omega

/-- An estate (with no lifetime gifts) at or below its applicable exclusion owes nothing. -/
theorem below_exclusion_zero (d : Death) (hg : d.gifts = []) (h : d.base ≤ d.exclusion) : d.tax = 0 := by
  have hp : d.giftTaxPayable = 0 := by simp [Death.giftTaxPayable, hg, schedule]
  have := tentative_mono d.year _ _ h
  simp only [Death.tax, hp, credit]
  omega

/-- **Flat 40%.** For a death in 2013 or later, with no lifetime gifts and no DSUE, the estate tax on a taxable estate
above the exclusion is exactly 40% of the excess. -/
theorem flat_forty (d : Death) (hy : 2013 ≤ d.year) (hg : d.gifts = []) (hs : d.dsue = 0)
    (h : bea d.year ≤ d.taxableEstate) : d.tax = pct (d.taxableEstate - bea d.year) 40 := by
  obtain ⟨h1, h5, h35, h45⟩ := bea_from_2013 d.year hy
  have hp : d.giftTaxPayable = 0 := by simp [Death.giftTaxPayable, hg, schedule]
  have hb : d.base = d.taxableEstate := by simp [Death.base, Death.adjustedTaxableGifts, hg]
  have he : d.exclusion = bea d.year := by simp [Death.exclusion, hs]
  have ht := top_rate d.year h35 h45 (bea d.year) (d.taxableEstate - bea d.year) h1 h5 (by omega)
  have hn : 0 ≤ pct (d.taxableEstate - bea d.year) 40 := by unfold pct; omega
  simp only [Death.tax, hp, hb, he, credit]
  rw [show bea d.year + (d.taxableEstate - bea d.year) = d.taxableEstate by omega] at ht
  omega

/-! ## Portability -/

/-- The DSUE a decedent can pass on is never more than the basic exclusion of the year of death, nor negative. -/
theorem dsue_le_bea (d : Death) : 0 ≤ d.dsueOut ∧ d.dsueOut ≤ bea d.year := by
  unfold Death.dsueOut
  have := bea_nonneg d.year
  omega

/-- **Portability at most doubles the exclusion.** A survivor who dies (or gives) in a year no earlier than the first
spouse's death has an applicable exclusion of her own basic exclusion plus the DSUE, and that is at most twice her
own basic exclusion. -/
theorem portability_cap (d : Death) (y : Nat) (hy : d.year ≤ y) :
    survivorExclusion y d.dsueOut ≤ 2 * bea y := by
  have := dsue_le_bea d
  have := bea_mono d.year y hy
  unfold survivorExclusion; omega

/-! ## Gifts -/

/-- **The annual exclusion.** Present-interest gifts of no more than the year's exclusion to each donee are never
taxable gifts, however many donees. -/
theorem annual_exclusion_free (y : Nat) (gs : List Gift)
    (h : ∀ g ∈ gs, g.present = true ∧ g.value ≤ annualExclusion y) : taxableGifts y gs = 0 := by
  induction gs with
  | nil => rfl
  | cons g gs ih =>
    have hg := h g (by simp)
    have ht : Gift.taxable y g = 0 := by
      unfold Gift.taxable; simp only [hg.1]; split <;> simp; omega
    have := ih (fun g' hm => h g' (by simp [hm]))
    simp only [taxableGifts, List.map_cons, List.sum_cons] at this ⊢
    omega

/-- **No escape through the credit.** A taxable gift that the credit fully sheltered when made adds back at death:
the estate pays exactly the tax it would have paid had the property stayed in the estate. -/
theorem gift_no_escape (d : Death) (p : Period) (hp : 0 ≤ p.taxable)
    (hcov : tentative d.year p.taxable ≤ credit d.year (bea p.year + p.dsue)) (h0 : d.deductions ≤ d.gross) :
    ({ d with gifts := [p] } : Death).tax = ({ d with gifts := [], gross := d.gross + p.taxable } : Death).tax := by
  have hz := tentative_zero d.year 0 (by omega)
  have hpay : ({ d with gifts := [p] } : Death).giftTaxPayable = 0 := by
    have hm : min (tentative d.year p.taxable) (max 0 (credit d.year (bea p.year + p.dsue)))
        = tentative d.year p.taxable := by omega
    simp [Death.giftTaxPayable, schedule, hz, hm]
  have hpay' : ({ d with gifts := [], gross := d.gross + p.taxable } : Death).giftTaxPayable = 0 := by
    simp [Death.giftTaxPayable, schedule]
  have hbase : ({ d with gifts := [p] } : Death).base =
      ({ d with gifts := [], gross := d.gross + p.taxable } : Death).base := by
    simp only [Death.base, Death.taxableEstate, Death.adjustedTaxableGifts, Death.deductions] at h0 ⊢
    simp; omega
  simp only [Death.tax, hpay, hpay', hbase]
  rfl

/-! ## GST -/

/-- **GST exemption.** A transfer covered in full by allocated exemption bears no GST tax. -/
theorem gst_exempt (y : Nat) (amount allocated : Int) (ha : 0 < amount) (h : amount ≤ allocated) :
    gstTax y amount allocated = 0 := by
  have hf : applicableFraction allocated amount = 1000 := by
    unfold applicableFraction
    have : 1000 ≤ (allocated * 2000 + amount) / (2 * amount) := by
      apply (Int.le_ediv_iff_mul_le (by omega)).mpr
      have : amount * 2000 ≤ allocated * 2000 := by omega
      calc 1000 * (2 * amount) = amount * 2000 := by omega
        _ ≤ allocated * 2000 + amount := by omega
    simp only [show ¬ amount ≤ 0 by omega, ↓reduceIte]; omega
  unfold gstTax inclusionRatio; rw [hf]; simp

end Legal.USTax.Estate.Theorems
