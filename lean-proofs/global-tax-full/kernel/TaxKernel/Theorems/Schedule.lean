import TaxKernel.Schedule
import TaxKernel.Unit

/-!
# Generic theorems about schedules (proved once, for every country)

* `bandsTicks_succ` / `Schedule.ticks_succ`: the tax on one more unit is exactly the marginal rate `rate s x` of the
  band containing `x`, for **any** list of bands (sorted or not).
* `Schedule.ticks_mono`: non-negative rates ⇒ monotone.
* `Schedule.ticks_of_nonpos`: thresholds ≥ 0 ⇒ the tax of 0 (or less) is 0.
* `Schedule.rate_bounds`: sorted bands with rates in `[0, R]` ⇒ marginal rate in `[0, R]`;
  `Schedule.ticks_lipschitz`: then the tax rises by at most `R` per unit (no jump: the schedule is continuous);
  `Schedule.ticks_le_mul`: and tax ≤ `R` × income.
* `Schedule.rate_mono` / `Schedule.ticks_convex`: progressive (sorted, non-decreasing non-negative rates) ⇒ the
  marginal rate never falls and the tax is convex.
* `Schedule.ticks_const_rate`: over an interval where the marginal rate is a constant `r`, `k` more units cost
  `r * k` (used by the taper theorem).
* Corollaries for `s.progressive = true` (a concrete schedule proves that by `decide`):
  `ticks_mono_of_progressive`, `rate_le_max`, `ticks_lipschitz_of_progressive`, `ticks_le_maxRate_mul`.
-/

namespace TaxKernel

/-! ## Increments of a function on the integers -/

/-- If every one-unit increment of `f` lies in `[lo, hi]`, then over `n` units the change lies in `[lo·n, hi·n]`. -/
theorem incr_bounds (f : Int → Int) (lo hi : Int) (h : ∀ x, lo ≤ f (x + 1) - f x ∧ f (x + 1) - f x ≤ hi)
    (x : Int) : ∀ n : Nat, lo * n ≤ f (x + n) - f x ∧ f (x + n) - f x ≤ hi * n := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    have e : x + ((n + 1 : Nat) : Int) = (x + n) + 1 := by omega
    rw [e]
    have := h (x + n)
    have c1 : lo * ((n + 1 : Nat) : Int) = lo * n + lo := by rw [Int.natCast_add, Int.mul_add]; simp
    have c2 : hi * ((n + 1 : Nat) : Int) = hi * n + hi := by rw [Int.natCast_add, Int.mul_add]; simp
    rw [c1, c2]; omega

theorem incr_bounds' (f : Int → Int) (lo hi : Int) (h : ∀ x, lo ≤ f (x + 1) - f x ∧ f (x + 1) - f x ≤ hi)
    {x y : Int} (hxy : x ≤ y) : lo * (y - x) ≤ f y - f x ∧ f y - f x ≤ hi * (y - x) := by
  have := incr_bounds f lo hi h x (y - x).toNat
  have e : ((y - x).toNat : Int) = y - x := Int.toNat_of_nonneg (by omega)
  rw [e] at this
  have e2 : x + (y - x) = y := by omega
  rw [e2] at this
  exact this

/-- Non-negative increments ⇒ monotone. -/
theorem mono_of_incr (f : Int → Int) (h : ∀ x, 0 ≤ f (x + 1) - f x) : Monotone' f := by
  intro x y hxy
  have key : ∀ n : Nat, f x ≤ f (x + n) := by
    intro n
    induction n with
    | zero => simp
    | succ n ih =>
      have e : x + ((n + 1 : Nat) : Int) = (x + n) + 1 := by omega
      rw [e]; have := h (x + n); omega
  have := key (y - x).toNat
  rwa [show x + ((y - x).toNat : Int) = y by omega] at this

/-! ## One band -/

theorem piece_succ (r lo hi x : Int) :
    r * pos (min (x + 1) hi - lo) - r * pos (min x hi - lo) = if lo ≤ x ∧ x < hi then r else 0 := by
  split
  · next h =>
    have e : pos (min (x + 1) hi - lo) = pos (min x hi - lo) + 1 := by unfold pos; omega
    rw [e, Int.mul_add, Int.mul_one]; omega
  · next h =>
    have e : pos (min (x + 1) hi - lo) = pos (min x hi - lo) := by unfold pos; omega
    rw [e]; omega

theorem last_succ (r lo x : Int) : r * pos (x + 1 - lo) - r * pos (x - lo) = if lo ≤ x then r else 0 := by
  split
  · next h =>
    have e : pos (x + 1 - lo) = pos (x - lo) + 1 := by unfold pos; omega
    rw [e, Int.mul_add, Int.mul_one]; omega
  · next h =>
    have e : pos (x + 1 - lo) = pos (x - lo) := by unfold pos; omega
    rw [e]; omega

/-- **The marginal rate is the band's rate**, for every list of bands. -/
theorem bandsTicks_succ : ∀ (l : List Band) (x : Int), bandsTicks l (x + 1) - bandsTicks l x = bandsRate l x
  | [], x => by simp [bandsTicks, bandsRate]
  | [b], x => by simp only [bandsTicks, bandsRate]; exact last_succ b.rate b.lo x
  | b :: c :: rest, x => by
    simp only [bandsTicks, bandsRate]
    have h1 := piece_succ b.rate b.lo c.lo x
    have h2 := bandsTicks_succ (c :: rest) x
    omega

theorem bandsRate_nonneg : ∀ (l : List Band) (x : Int), (∀ b ∈ l, 0 ≤ b.rate) → 0 ≤ bandsRate l x
  | [], _, _ => by simp [bandsRate]
  | [b], x, h => by
    simp only [bandsRate]; have := h b (by simp); split <;> omega
  | b :: c :: rest, x, h => by
    simp only [bandsRate]
    have hb := h b (by simp)
    have ih := bandsRate_nonneg (c :: rest) x (fun d hd => h d (List.mem_cons_of_mem _ hd))
    split <;> omega

/-- Below the first threshold of sorted bands the marginal rate is 0. -/
theorem bandsRate_below : ∀ (c : Band) (rest : List Band) (x : Int),
    bandsSorted (c :: rest) = true → x < c.lo → bandsRate (c :: rest) x = 0
  | c, [], x, _, hx => by simp only [bandsRate]; split <;> omega
  | c, d :: rest, x, hs, hx => by
    simp only [bandsSorted, Bool.and_eq_true, decide_eq_true_eq] at hs
    simp only [bandsRate]
    have := bandsRate_below d rest x hs.2 (by omega)
    rw [this]; split <;> omega

/-- For sorted bands the marginal rate is 0 or one band's rate. -/
theorem bandsRate_cases : ∀ (l : List Band) (x : Int), bandsSorted l = true →
    bandsRate l x = 0 ∨ ∃ b ∈ l, bandsRate l x = b.rate
  | [], _, _ => by simp [bandsRate]
  | [b], x, _ => by
    simp only [bandsRate]; split
    · exact Or.inr ⟨b, by simp, rfl⟩
    · exact Or.inl rfl
  | b :: c :: rest, x, hs => by
    have hs' := hs
    simp only [bandsSorted, Bool.and_eq_true, decide_eq_true_eq] at hs'
    simp only [bandsRate]
    split
    · next h =>
      have := bandsRate_below c rest x hs'.2 h.2
      rw [this]; exact Or.inr ⟨b, by simp, by omega⟩
    · rcases bandsRate_cases (c :: rest) x hs'.2 with h | ⟨d, hd, e⟩
      · exact Or.inl (by omega)
      · exact Or.inr ⟨d, List.mem_cons_of_mem _ hd, by omega⟩

/-- At or above the first threshold of sorted bands with non-decreasing rates, the marginal rate is at least the
first band's. -/
theorem bandsRate_ge_head : ∀ (c : Band) (rest : List Band) (x : Int),
    bandsSorted (c :: rest) = true → ratesMono (c :: rest) = true → c.lo ≤ x → c.rate ≤ bandsRate (c :: rest) x
  | c, [], x, _, _, hx => by simp only [bandsRate]; split <;> omega
  | c, d :: rest, x, hs, hm, hx => by
    simp only [bandsSorted, Bool.and_eq_true, decide_eq_true_eq] at hs
    simp only [ratesMono, Bool.and_eq_true, decide_eq_true_eq] at hm
    simp only [bandsRate]
    split
    · next h =>
      have := bandsRate_below d rest x hs.2 h.2
      omega
    · next h =>
      have hx' : d.lo ≤ x := by omega
      have := bandsRate_ge_head d rest x hs.2 hm.2 hx'
      omega

/-- Progressive bands: the marginal rate never falls. -/
theorem bandsRate_mono : ∀ (l : List Band) (x y : Int), bandsSorted l = true → ratesMono l = true →
    (∀ b ∈ l, 0 ≤ b.rate) → x ≤ y → bandsRate l x ≤ bandsRate l y
  | [], _, _, _, _, _, _ => by simp [bandsRate]
  | [b], x, y, _, _, hn, hxy => by
    simp only [bandsRate]; have := hn b (by simp); split <;> split <;> omega
  | b :: c :: rest, x, y, hs, hm, hn, hxy => by
    have hs' := hs
    have hm' := hm
    simp only [bandsSorted, Bool.and_eq_true, decide_eq_true_eq] at hs'
    simp only [ratesMono, Bool.and_eq_true, decide_eq_true_eq] at hm'
    have hb := hn b (by simp)
    have hn' : ∀ d ∈ c :: rest, 0 ≤ d.rate := fun d hd => hn d (List.mem_cons_of_mem _ hd)
    have ty := bandsRate_nonneg (c :: rest) y hn'
    simp only [bandsRate]
    by_cases hx1 : x < b.lo
    · have := bandsRate_below c rest x hs'.2 (by omega)
      rw [this]
      split
      · omega
      · split <;> omega
    · by_cases hx2 : x < c.lo
      · have tx := bandsRate_below c rest x hs'.2 hx2
        rw [tx]
        by_cases hy : y < c.lo
        · have := bandsRate_below c rest y hs'.2 hy
          rw [this]; split <;> split <;> omega
        · have := bandsRate_ge_head c rest y hs'.2 hm'.2 (by omega)
          split <;> split <;> omega
      · have := bandsRate_mono (c :: rest) x y hs'.2 hm'.2 hn' hxy
        split <;> split <;> omega

/-- Monotone tax for non-negative rates (direct, band by band). -/
theorem bandsTicks_mono : ∀ (l : List Band), (∀ b ∈ l, 0 ≤ b.rate) → ∀ x y : Int, x ≤ y →
    bandsTicks l x ≤ bandsTicks l y
  | [], _, _, _, _ => by simp [bandsTicks]
  | [b], h, x, y, hxy => by
    simp only [bandsTicks]
    exact mul_le_mul_rate (h b (by simp)) (pos_mono (by omega))
  | b :: c :: rest, h, x, y, hxy => by
    simp only [bandsTicks]
    have h1 : b.rate * pos (min x c.lo - b.lo) ≤ b.rate * pos (min y c.lo - b.lo) :=
      mul_le_mul_rate (h b (by simp)) (pos_mono (by omega))
    have h2 := bandsTicks_mono (c :: rest) (fun d hd => h d (List.mem_cons_of_mem _ hd)) x y hxy
    omega

/-- With thresholds ≥ 0, no tax on income ≤ 0. -/
theorem bandsTicks_of_nonpos : ∀ (l : List Band), (∀ b ∈ l, 0 ≤ b.lo) → ∀ x : Int, x ≤ 0 → bandsTicks l x = 0
  | [], _, _, _ => by simp [bandsTicks]
  | [b], h, x, hx => by
    simp only [bandsTicks]; have := h b (by simp)
    rw [pos_of_nonpos (by omega)]; simp
  | b :: c :: rest, h, x, hx => by
    simp only [bandsTicks]; have := h b (by simp)
    rw [pos_of_nonpos (by omega), bandsTicks_of_nonpos (c :: rest) (fun d hd => h d (List.mem_cons_of_mem _ hd)) x hx]
    simp

/-! ## The schedule-level statements -/

namespace Schedule

theorem ticks_succ (s : Schedule) (x : Int) : s.ticks (x + 1) - s.ticks x = s.rate x := bandsTicks_succ s.bands x

theorem ticks_mono (s : Schedule) (h : s.RatesNonneg) {x y : Int} (hxy : x ≤ y) : s.ticks x ≤ s.ticks y :=
  bandsTicks_mono s.bands h x y hxy

theorem ticks_of_nonpos (s : Schedule) (h : s.LosNonneg) {x : Int} (hx : x ≤ 0) : s.ticks x = 0 :=
  bandsTicks_of_nonpos s.bands h x hx

theorem ticks_zero (s : Schedule) (h : s.LosNonneg) : s.ticks 0 = 0 := s.ticks_of_nonpos h (Int.le_refl 0)

theorem ticks_nonneg (s : Schedule) (hr : s.RatesNonneg) (hl : s.LosNonneg) (x : Int) : 0 ≤ s.ticks x := by
  by_cases hx : x ≤ 0
  · rw [s.ticks_of_nonpos hl hx]; exact Int.le_refl 0
  · have := s.ticks_mono hr (show (0 : Int) ≤ x by omega); rw [s.ticks_zero hl] at this; exact this

/-- Sorted bands with rates in `[0, R]`: the marginal rate is in `[0, R]`. -/
theorem rate_bounds (s : Schedule) (hs : s.Sorted) (hn : s.RatesNonneg) {R : Int} (hR : s.RatesLe R) (h0 : 0 ≤ R)
    (x : Int) : 0 ≤ s.rate x ∧ s.rate x ≤ R := by
  unfold rate
  refine ⟨bandsRate_nonneg s.bands x hn, ?_⟩
  rcases bandsRate_cases s.bands x hs with h | ⟨b, hb, e⟩
  · omega
  · rw [e]; exact hR b hb

/-- **No jump**: tax rises by at most `R` per unit and never falls. -/
theorem ticks_lipschitz (s : Schedule) (hs : s.Sorted) (hn : s.RatesNonneg) {R : Int} (hR : s.RatesLe R)
    (h0 : 0 ≤ R) {x y : Int} (hxy : x ≤ y) : 0 ≤ s.ticks y - s.ticks x ∧ s.ticks y - s.ticks x ≤ R * (y - x) := by
  have := incr_bounds' s.ticks 0 R (fun z => by rw [s.ticks_succ]; exact s.rate_bounds hs hn hR h0 z) hxy
  simp at this; omega

/-- Tax ≤ `R` × income. -/
theorem ticks_le_mul (s : Schedule) (hs : s.Sorted) (hn : s.RatesNonneg) (hl : s.LosNonneg) {R : Int}
    (hR : s.RatesLe R) (h0 : 0 ≤ R) {x : Int} (hx : 0 ≤ x) : s.ticks x ≤ R * x := by
  have := s.ticks_lipschitz hs hn hR h0 hx
  rw [s.ticks_zero hl] at this; simp at this; omega

/-- Over an interval where the marginal rate is constant `r`, `k` more units cost `r * k`. -/
theorem ticks_const_rate (s : Schedule) (a r : Int) (k : Nat) (h : ∀ i : Int, a ≤ i → i < a + k → s.rate i = r) :
    s.ticks (a + k) - s.ticks a = r * k := by
  induction k with
  | zero => simp
  | succ n ih =>
    have ih' := ih (fun i h1 h2 => h i h1 (by omega))
    have e : a + ((n + 1 : Nat) : Int) = (a + n) + 1 := by omega
    rw [e]
    have := s.ticks_succ (a + n)
    rw [h (a + n) (by omega) (by omega)] at this
    have c : r * ((n + 1 : Nat) : Int) = r * n + r := by rw [Int.natCast_add, Int.mul_add]; simp
    rw [c]; omega

/-! ### From `s.progressive = true` -/

theorem progressive_parts {s : Schedule} (h : s.progressive = true) :
    s.Sorted ∧ ratesMono s.bands = true ∧ s.RatesNonneg ∧ s.LosNonneg := by
  unfold progressive at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩

theorem ticks_mono_of_progressive (s : Schedule) (h : s.progressive = true) : Monotone' s.ticks :=
  fun _ _ hxy => s.ticks_mono (progressive_parts h).2.2.1 hxy

theorem rate_mono (s : Schedule) (h : s.progressive = true) {x y : Int} (hxy : x ≤ y) : s.rate x ≤ s.rate y := by
  have ⟨hs, hm, hn, _⟩ := progressive_parts h
  exact bandsRate_mono s.bands x y hs hm hn hxy

/-- **Progressive ⇒ convex** (the condition of the splitting theorem). -/
theorem ticks_convex (s : Schedule) (h : s.progressive = true) : Convex s.ticks := by
  intro x
  have e : x + 2 = (x + 1) + 1 := by omega
  rw [e, s.ticks_succ, s.ticks_succ]
  exact s.rate_mono h (by omega)

theorem maxRate_ge_aux : ∀ (l : List Band) (m : Int), m ≤ l.foldl (fun m b => max m b.rate) m
  | [], _ => by simp
  | b :: rest, m => by
    simp only [List.foldl_cons]
    have := maxRate_ge_aux rest (max m b.rate)
    omega

theorem maxRate_ge_mem : ∀ (l : List Band) (m : Int) (b : Band), b ∈ l →
    b.rate ≤ l.foldl (fun m b => max m b.rate) m
  | [], _, _, h => by simp at h
  | c :: rest, m, b, h => by
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp h with rfl | h
    · have := maxRate_ge_aux rest (max m b.rate); omega
    · exact maxRate_ge_mem rest _ b h

theorem maxRate_nonneg (s : Schedule) : 0 ≤ s.maxRate := maxRate_ge_aux s.bands 0
theorem ratesLe_maxRate (s : Schedule) : s.RatesLe s.maxRate := fun b hb => maxRate_ge_mem s.bands 0 b hb

theorem rate_le_max (s : Schedule) (h : s.progressive = true) (x : Int) : s.rate x ≤ s.maxRate := by
  have ⟨hs, _, hn, _⟩ := progressive_parts h
  exact (s.rate_bounds hs hn s.ratesLe_maxRate s.maxRate_nonneg x).2

theorem ticks_lipschitz_of_progressive (s : Schedule) (h : s.progressive = true) {x y : Int} (hxy : x ≤ y) :
    0 ≤ s.ticks y - s.ticks x ∧ s.ticks y - s.ticks x ≤ s.maxRate * (y - x) := by
  have ⟨hs, _, hn, _⟩ := progressive_parts h
  exact s.ticks_lipschitz hs hn s.ratesLe_maxRate s.maxRate_nonneg hxy

theorem ticks_le_maxRate_mul (s : Schedule) (h : s.progressive = true) {x : Int} (hx : 0 ≤ x) :
    s.ticks x ≤ s.maxRate * x := by
  have ⟨hs, _, hn, hl⟩ := progressive_parts h
  exact s.ticks_le_mul hs hn hl s.ratesLe_maxRate s.maxRate_nonneg hx

/-- The rounded tax is monotone too (any monotone rounding rule). -/
theorem tax_mono (s : Schedule) (r : Rule) (hs : 0 < r.step) (hm : r.mode.isMonotoneMode) (hn : s.RatesNonneg)
    {x y : Int} (hxy : x ≤ y) : s.tax r x ≤ s.tax r y :=
  Rule.ofTicks_mono r hs hm (s.ticks_mono hn hxy)

end Schedule
end TaxKernel
