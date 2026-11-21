import TaxKernel.Theorems.Schedule
import TaxKernel.Allowance
import TaxKernel.Credit
import TaxKernel.Surcharge
import TaxKernel.Social
import TaxKernel.Dual

/-!
# Generic theorems about allowances, tapers, credits, surcharges, the unit of assessment, social contributions

Proved once for every input; a country instantiates them with its parameters (conditions such as
`Taper.WellFormed` are discharged by `decide` or `by simp [WellFormed]; omega` on concrete numbers).
-/

set_option linter.deprecated false

namespace TaxKernel

/-! ## Tapers -/
namespace Taper

theorem reduction_nonneg (t : Taper) (hw : t.WellFormed) (inc : Int) : 0 ≤ t.reduction inc := by
  obtain ⟨hd, hn, _, hr⟩ := hw
  unfold reduction; rw [hr]; simp only [divR]
  exact Int.ediv_nonneg (Int.mul_nonneg hn (pos_nonneg _)) (by omega)

theorem amount_le_full (t : Taper) (hw : t.WellFormed) (inc : Int) : t.amount inc ≤ t.full := by
  have := t.reduction_nonneg hw inc
  have hf := hw.2.2.1
  unfold amount; omega

theorem floor_le_amount (t : Taper) (inc : Int) : t.floor ≤ t.amount inc := by unfold amount; omega

theorem reduction_mono (t : Taper) (hw : t.WellFormed) {x y : Int} (h : x ≤ y) :
    t.reduction x ≤ t.reduction y := by
  obtain ⟨hd, hn, _, hr⟩ := hw
  unfold reduction; rw [hr]; simp only [divR]
  exact Int.ediv_le_ediv hd (mul_le_mul_rate hn (pos_mono (by omega)))

/-- More income never raises a tapered allowance. -/
theorem amount_antitone (t : Taper) (hw : t.WellFormed) {x y : Int} (h : x ≤ y) : t.amount y ≤ t.amount x := by
  have := t.reduction_mono hw h
  unfold amount; omega

/-- Below the start of the taper the full allowance is given. -/
theorem amount_below_start (t : Taper) (hw : t.WellFormed) {inc : Int} (h : inc ≤ t.start) :
    t.amount inc = t.full := by
  obtain ⟨hd, hn, hf, hr⟩ := hw
  unfold amount reduction; rw [hr]; simp only [divR]
  rw [pos_of_nonpos (by omega), Int.mul_zero, Int.zero_ediv]; omega

/-- Inside the band, `den` more units of income add exactly `num` to the reduction. -/
theorem reduction_step (t : Taper) (hw : t.WellFormed) {inc : Int} (hs : t.start ≤ inc) :
    t.reduction (inc + t.den) = t.reduction inc + t.num := by
  obtain ⟨hd, hn, _, hr⟩ := hw
  unfold reduction; rw [hr]; simp only [divR]
  rw [pos_of_nonneg (by omega : 0 ≤ inc + t.den - t.start), pos_of_nonneg (by omega : 0 ≤ inc - t.start)]
  have : t.num * (inc + t.den - t.start) = t.num * (inc - t.start) + t.num * t.den := by
    rw [← Int.mul_add]; congr 1; omega
  rw [this, Int.add_mul_ediv_right _ _ (by omega : t.den ≠ 0)]

/-- **Taper step**: while the allowance stays above its floor, `den` more income removes exactly `num` of it. -/
theorem amount_step (t : Taper) (hw : t.WellFormed) {inc : Int} (hs : t.start ≤ inc)
    (hin : t.floor < t.amount (inc + t.den)) : t.amount (inc + t.den) = t.amount inc - t.num := by
  have h := t.reduction_step hw hs
  have hn := hw.2.1
  unfold amount at *; omega

/-- Taxable income rises by `den + num` when income rises by `den` inside the band (income above the allowance). -/
theorem taxable_step (t : Taper) (hw : t.WellFormed) {inc : Int} (hs : t.start ≤ inc)
    (hin : t.floor < t.amount (inc + t.den)) (hpos : t.amount inc ≤ inc) :
    taxableAfter (t.amount (inc + t.den)) (inc + t.den) = taxableAfter (t.amount inc) inc + t.den + t.num := by
  have h := t.amount_step hw hs hin
  have hd := hw.1
  have hn := hw.2.1
  rw [h]; unfold taxableAfter pos; omega

/-- **The taper band's marginal rate**: where the schedule's marginal rate is a constant `r` over the taxable
income the step covers, `den` more units of income cost `r * (den + num)` ticks: an effective marginal rate of
`r * (1 + num/den)`, above the schedule's own (UK: 40 % × 3/2 = 60 % between £100,000 and £125,140). -/
theorem taper_marginal (t : Taper) (hw : t.WellFormed) (s : Schedule) (r : Int) {inc : Int} (hs : t.start ≤ inc)
    (hin : t.floor < t.amount (inc + t.den)) (hpos : t.amount inc ≤ inc)
    (hr : ∀ i, taxableAfter (t.amount inc) inc ≤ i → i < taxableAfter (t.amount inc) inc + t.den + t.num →
      s.rate i = r) :
    s.ticks (taxableAfter (t.amount (inc + t.den)) (inc + t.den)) - s.ticks (taxableAfter (t.amount inc) inc)
      = r * (t.den + t.num) := by
  rw [t.taxable_step hw hs hin hpos]
  have hd := hw.1
  have hn := hw.2.1
  generalize taxableAfter (t.amount inc) inc = a at hr ⊢
  have e : (((t.den + t.num).toNat : Nat) : Int) = t.den + t.num := Int.toNat_of_nonneg (by omega)
  have := s.ticks_const_rate a r (t.den + t.num).toNat (fun i h1 h2 => hr i h1 (by omega))
  rw [e] at this
  rw [show a + t.den + t.num = a + (t.den + t.num) by omega]
  exact this

/-- …and that is strictly more than the schedule rate alone would charge on `den` units. -/
theorem taper_marginal_gt (r den num : Int) (hr : 0 < r) (hn : 0 < num) : r * den < r * (den + num) := by
  rw [Int.mul_add]
  have := Int.mul_pos hr hn
  omega

end Taper

/-! ## Credits -/

theorem Credit.value_le_full (c : Credit) (hd : 0 < c.den) (hn : 0 ≤ c.num) (hf : c.floor ≤ c.full)
    (hr : c.round = .down) (earn inc : Int) : c.value earn inc ≤ c.full := by
  have := Taper.amount_le_full c.taper ⟨hd, hn, hf, hr⟩ inc
  have e : c.taper.full = c.full := rfl
  unfold Credit.value; omega

theorem Credit.value_antitone_inc (c : Credit) (hd : 0 < c.den) (hn : 0 ≤ c.num) (hf : c.floor ≤ c.full)
    (hr : c.round = .down) (earn : Int) {x y : Int} (h : x ≤ y) : c.value earn y ≤ c.value earn x := by
  have := Taper.amount_antitone c.taper ⟨hd, hn, hf, hr⟩ h
  unfold Credit.value; omega

/-- Without refundable credits the tax after credits is never negative. -/
theorem applyCredits_nonneg (tax : Int) (nonref : List Int) : 0 ≤ applyCredits tax nonref [] := by
  simp [applyCredits, sumInts]; omega

/-- Tax after credits is monotone in the tax before credits. -/
theorem applyCredits_mono (nonref ref : List Int) {x y : Int} (h : x ≤ y) :
    applyCredits x nonref ref ≤ applyCredits y nonref ref := by
  unfold applyCredits; omega

/-- A non-refundable credit is worth its face value only to someone with that much tax: the unused part is lost. -/
theorem applyCredits_waste (tax : Int) (nonref : List Int) (h : tax < sumInts nonref) :
    applyCredits tax nonref [] = 0 := by
  unfold applyCredits
  have : sumInts ([] : List Int) = 0 := rfl
  rw [this]; omega

/-! ## Surcharges -/
namespace Surcharge

theorem ticks_nonneg (s : Surcharge) (hr : 0 ≤ s.rate) (hg : 0 ≤ s.glide) (x : Int) : 0 ≤ s.ticks x := by
  unfold ticks
  split
  · exact Int.le_refl 0
  · next hx =>
    split
    · have := mul_nonneg' hr (pos_nonneg (x - s.deduct))
      have := mul_nonneg' hg (show 0 ≤ x - s.exempt by omega)
      omega
    · exact mul_nonneg' hr (pos_nonneg _)

/-- **A surcharge is monotone in its base** (non-negative rate and glide rate). -/
theorem ticks_mono (s : Surcharge) (hr : 0 ≤ s.rate) (hg : 0 ≤ s.glide) {x y : Int} (h : x ≤ y) :
    s.ticks x ≤ s.ticks y := by
  by_cases hx : x ≤ s.exempt
  · have := s.ticks_nonneg hr hg y
    unfold ticks at *; rw [if_pos hx]; exact this
  · have hy : ¬ y ≤ s.exempt := by omega
    unfold ticks; rw [if_neg hx, if_neg hy]
    split
    · have h1 := mul_le_mul_rate hr (pos_mono (show x - s.deduct ≤ y - s.deduct by omega))
      have h2 := mul_le_mul_rate hg (show x - s.exempt ≤ y - s.exempt by omega)
      omega
    · exact mul_le_mul_rate hr (pos_mono (by omega))

theorem amount_mono (s : Surcharge) (hr : 0 ≤ s.rate) (hg : 0 ≤ s.glide) (hs : 0 < s.round.step)
    (hm : s.round.mode.isMonotoneMode) {x y : Int} (h : x ≤ y) : s.amount x ≤ s.amount y :=
  Rule.ofTicks_mono s.round hs hm (s.ticks_mono hr hg h)

/-- **Surcharges preserve monotonicity**: if tax `f` is monotone in income, so is tax + surcharge on tax. -/
theorem withSurcharge_mono (s : Surcharge) (hr : 0 ≤ s.rate) (hg : 0 ≤ s.glide) (hs : 0 < s.round.step)
    (hm : s.round.mode.isMonotoneMode) (f : Int → Int) (hf : Monotone' f) : Monotone' (fun x => f x + s.amount (f x)) := by
  intro x y h
  have h1 := hf x y h
  have h2 := s.amount_mono hr hg hs hm h1
  simp only []; omega

/-- **The exemption-limit notch**: with no glide zone, one unit of base above the exemption limit costs
`rate × (exempt + 1 − deduct)` — the whole base above `deduct` becomes taxable at once. -/
theorem exempt_notch (s : Surcharge) (hg : s.glide = 0) (hd : s.deduct ≤ s.exempt) :
    s.ticks (s.exempt + 1) - s.ticks s.exempt = s.rate * (s.exempt + 1 - s.deduct) := by
  unfold ticks
  rw [if_neg (by omega), if_pos (Int.le_refl _), if_neg (by omega), pos_of_nonneg (by omega)]
  omega

/-- With a glide zone, the step at the exemption limit is at most `glide` per unit (no notch). -/
theorem glide_no_notch (s : Surcharge) (hg : 0 < s.glide) (hr : 0 ≤ s.rate) :
    s.ticks (s.exempt + 1) - s.ticks s.exempt ≤ s.glide := by
  unfold ticks
  rw [if_neg (by omega), if_pos (Int.le_refl _), if_pos hg]
  have : s.glide * (s.exempt + 1 - s.exempt) = s.glide := by rw [show s.exempt + 1 - s.exempt = 1 by omega]; omega
  omega

end Surcharge

/-! ## Unit of assessment -/

theorem incr_mono_of_convex (f : Int → Int) (hc : Convex f) (i : Int) :
    ∀ n : Nat, f (i + 1) - f i ≤ f (i + n + 1) - f (i + n) := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    have h := hc (i + n)
    have e1 : i + ((n + 1 : Nat) : Int) = i + n + 1 := by omega
    have e2 : i + n + 2 = i + n + 1 + 1 := by omega
    rw [e1]; rw [e2] at h; omega

/-- Convexity: the gain over `k` units starting higher is at least the gain starting lower. -/
theorem shift_le_of_convex (f : Int → Int) (hc : Convex f) {a m : Int} (h : a ≤ m) :
    ∀ k : Nat, f (a + k) - f a ≤ f (m + k) - f m := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
    have hi := incr_mono_of_convex f hc (a + k) (m - a).toNat
    have e : a + k + ((m - a).toNat : Int) = m + k := by omega
    rw [e] at hi
    have e1 : a + ((k + 1 : Nat) : Int) = a + k + 1 := by omega
    have e2 : m + ((k + 1 : Nat) : Int) = m + k + 1 := by omega
    rw [e1, e2]; omega

theorem splitting_le_separate_aux (f : Int → Int) (hc : Convex f) (hm : Monotone' f) {a b : Int} (h : a ≤ b) :
    splitting f a b ≤ separate f a b := by
  unfold splitting separate
  have ham : a ≤ (a + b) / 2 := by omega
  have := shift_le_of_convex f hc ham ((a + b) / 2 - a).toNat
  have e1 : a + (((a + b) / 2 - a).toNat : Int) = (a + b) / 2 := by omega
  rw [e1] at this
  have hb := hm ((a + b) / 2 + (((a + b) / 2 - a).toNat : Int)) b (by omega)
  omega

/-- **Splitting never costs more than separate assessment** for a convex, monotone tax function (any progressive
`Schedule`: `Schedule.ticks_convex`, `Schedule.ticks_mono_of_progressive`), whatever the split of the income. -/
theorem splitting_le_separate (f : Int → Int) (hc : Convex f) (hm : Monotone' f) (a b : Int) :
    splitting f a b ≤ separate f a b := by
  rcases Int.le_total a b with h | h
  · exact splitting_le_separate_aux f hc hm h
  · have := splitting_le_separate_aux f hc hm h
    unfold splitting separate at *
    rw [Int.add_comm a b]; omega

/-- …and gains nothing when the two incomes are equal. -/
theorem splitting_eq_of_equal (f : Int → Int) (a : Int) : splitting f a a = separate f a a := by
  unfold splitting separate
  rw [show (a + a) / 2 = a by omega]; omega

/-- **Aggregation without splitting never beats separate assessment**: for a convex tax function with no tax on
nothing, `f a + f b ≤ f (a + b)` for non-negative incomes (joint taxation of a couple on one schedule is a
marriage penalty unless the schedule's bands are widened). -/
theorem separate_le_joint (f : Int → Int) (hc : Convex f) (h0 : f 0 = 0) {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate f a b ≤ joint f a b := by
  unfold separate joint
  have := shift_le_of_convex f hc hb a.toNat
  have e : (a.toNat : Int) = a := Int.toNat_of_nonneg ha
  rw [e, show (0 : Int) + a = a by omega] at this
  have h2 := shift_le_of_convex f hc (show (0 : Int) ≤ b from hb) a.toNat
  rw [e, show (0 : Int) + a = a by omega, h0, Int.add_comm b a] at h2
  omega

/-! ## Social contributions -/
namespace Contribution

/-- **The floor notch**: earning one unit more than `floor - 1` makes the whole base contributable. -/
theorem floor_notch (c : Contribution) : c.ticks c.floor - c.ticks (c.floor - 1) = c.sched.ticks (c.base c.floor) := by
  unfold ticks
  rw [if_neg (by omega), if_pos (by omega)]
  omega

/-- Above the ceiling the contribution no longer grows (a regressive feature: the average rate falls). -/
theorem ticks_above_ceiling (c : Contribution) (hc : 0 ≤ c.ceiling) {x : Int} (hx : c.ceiling ≤ x)
    (hf : c.floor ≤ x) : c.ticks x = c.sched.ticks c.ceiling := by
  unfold ticks base
  rw [if_neg (by omega), if_neg (by omega), show min x c.ceiling = c.ceiling by omega]

theorem ticks_mono (c : Contribution) (hr : c.sched.RatesNonneg) (hl : c.sched.LosNonneg) {x y : Int} (h : x ≤ y) :
    c.ticks x ≤ c.ticks y := by
  unfold ticks
  by_cases hx : x < c.floor
  · rw [if_pos hx]; split
    · exact Int.le_refl 0
    · exact c.sched.ticks_nonneg hr hl _
  · rw [if_neg hx, if_neg (by omega)]
    apply c.sched.ticks_mono hr
    unfold base; split <;> omega

end Contribution

/-! ## Dual income tax -/

theorem Dual.capitalTicks_mono (d : Dual) (hr : d.capital.RatesNonneg) {x y : Int} (h : x ≤ y) :
    d.capitalTicks x ≤ d.capitalTicks y := by
  unfold Dual.capitalTicks
  exact d.capital.ticks_mono hr (pos_mono (by omega))

end TaxKernel
