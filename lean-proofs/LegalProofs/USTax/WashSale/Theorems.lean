import LegalProofs.USTax.WashSale.Rules

/-!
# What the wash-sale rule does, proved for every sequence of trades

1. **Deferral, not forgiveness** (`conservation`, `deferral_not_forgiveness`): across any sequence of trades, gain
   recognized minus the basis still held equals cash in minus cash out. So once every position is closed, every
   disallowed loss has come back: the rule changes *when* a loss counts, never *whether*.
2. **The rule's reach** (`outside_scope`): for assets that are not stock or securities, no loss is ever disallowed,
   whatever the trades and however close together.
3. **The window** (`outside_window`): a sale is never matched to an acquisition 31 or more days away. A position can be
   kept without interruption, and the loss still recognized, by buying the new unit 31 days before selling the old one.
-/

namespace Legal.USTax.WashSale

theorem sumB_append (ls : List Lot) (x : Lot) : sumB (ls ++ [x]) = sumB ls + x.basis := by
  induction ls with
  | nil => simp [sumB]
  | cons l ls ih => simp [sumB, ih]; omega

/-- The conserved quantity. -/
def Φ (b : Book) : Int := b.recognized - sumB b.lots - sumP b.pending - b.proceeds + b.costs

theorem step_conserves (M : Market) (plan : List (Nat × Trade)) (b b' : Book) (x : Nat × Trade)
    (h : step M plan b x = some b') : Φ b' = Φ b := by
  obtain ⟨i, t⟩ := x
  unfold step at h
  simp only at h
  split at h
  · -- a purchase: the cost and any waiting disallowed loss become the new unit's basis
    have hp := takePending_sum i b.pending
    simp at h; subst h; simp [Φ, sumB_append]; omega
  · split at h
    · simp at h
    · rename_i lot others hf
      have hs := takeFirst_sum t.asset b.lots lot others hf
      split at h
      · split at h
        · simp at h; subst h; simp [Φ]; omega
        · split at h
          · simp at h; subst h; simp [Φ, sumP]; omega
          · split at h
            · simp at h; subst h; simp [Φ]; omega
            · rename_i ls hb
              have := bump_sum _ _ others ls hb
              simp at h; subst h; simp [Φ]; omega
      · simp at h; subst h; simp [Φ]; omega

theorem conservation (M : Market) (plan : List (Nat × Trade)) :
    ∀ (xs : List (Nat × Trade)) (b b' : Book), runFrom M plan xs b = some b' → Φ b' = Φ b
  | [], b, b', h => by simp [runFrom] at h; subst h; rfl
  | x :: xs, b, b', h => by
    simp only [runFrom] at h
    cases hs : step M plan b x with
    | none => simp [hs] at h
    | some m => simp [hs] at h; rw [conservation M plan xs m b' h, step_conserves M plan b m x hs]

/-- **Deferral, not forgiveness.** Start with nothing held; trade in any way at all; close every position. Then the
gain recognized is exactly cash in minus cash out: every loss the rule disallowed along the way has come back. -/
theorem deferral_not_forgiveness (M : Market) (trades : List Trade) (b' : Book)
    (h : execute M trades ⟨[], [], [], 0, 0, 0, 0⟩ = some b') (closed : b'.lots = [] ∧ b'.pending = []) :
    b'.recognized = b'.proceeds - b'.costs := by
  have := conservation M _ _ _ _ h
  simp [Φ, closed.1, closed.2, sumB, sumP] at this; omega

/-- **Outside the rule's reach.** If no asset traded is stock or securities, no loss is ever disallowed. -/
theorem outside_scope (M : Market) (hs : ∀ a, (M.assets a).security = false) (plan : List (Nat × Trade)) :
    ∀ (xs : List (Nat × Trade)) (b b' : Book), runFrom M plan xs b = some b' → b'.disallowed = b.disallowed
  | [], b, b', h => by simp [runFrom] at h; subst h; rfl
  | (i, t) :: xs, b, b', h => by
    simp only [runFrom] at h
    cases hstep : step M plan b (i, t) with
    | none => simp [hstep] at h
    | some m =>
      simp [hstep] at h
      have ih := outside_scope M hs plan xs m b' h
      rw [ih]
      unfold step at hstep; simp only at hstep
      split at hstep
      · simp at hstep; subst hstep; rfl
      · split at hstep
        · simp at hstep
        · simp [hs] at hstep; subst hstep; rfl

/-- **The window.** If every acquisition of a substantially identical asset in the plan is 31 or more days from the
sale, the search for a replacement finds none. -/
theorem outside_window (M : Market) (plan : List (Nat × Trade)) (b : Book) (i cls d own : Nat)
    (hw : ∀ j t, (j, t) ∈ plan → t.buy = true → (M.assets t.asset).cls = cls → t.day + 31 ≤ d ∨ d + 31 ≤ t.day) :
    replacement M plan b i cls d own = none := by
  unfold replacement
  simp only [Option.map_eq_none_iff, List.find?_eq_none]
  intro x hx
  obtain ⟨j, t⟩ := x
  have := hw j t hx
  simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq, not_and, Bool.not_eq_true]
  intro hb
  exfalso
  rcases this hb.1.1.1.1.1 hb.1.1.1.1.2 with h1 | h1
  · have := hb.1.1.1.2; omega
  · have := hb.1.1.2; omega

end Legal.USTax.WashSale
