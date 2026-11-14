/-!
# Red-team T6 (part 2): a statement over ALL move sequences, in a cut-down model

Cut down, and said plainly: one regulated investment company share class; the price moves only when a capital gain
dividend is paid (flat total return, as in the C2 scenario); no calendar (every move is inside the six-month window of
§852(b)(4), so the legitimate "hold past six months" route is outside this model); a wash sale is a sale at a loss
with a simultaneous repurchase (§1091(a), (d)). `closed = false` is the statute as written: the §852(b)(4)(A) amount
stays with "such share". `closed = true` is the T2 rule: it follows the §1091(d) basis into the replacement share.

No imports, no `native_decide`, no axioms of our own.
-/
namespace Legal.USTax.Hunt.Audit.InstrumentsRedKernel

structure L where
  basis : Int
  taint : Int      -- capital gain dividends received on the share (or, closed rule, inherited through §1091(d))
  deriving DecidableEq, Repr

structure S where
  p : Int                -- price
  lots : List L
  ltGain : Int := 0      -- §852(b)(3)(B): capital gain dividends
  ltLoss : Int := 0      -- §852(b)(4)(A): loss treated as long-term
  stLoss : Int := 0      -- loss left short-term
  gain : Int := 0        -- gain on sales (none arises on a flat path; kept for completeness)
  deriving DecidableEq, Repr

inductive Mv where
  | buy                  -- buy one share at the price
  | div (d : Nat)        -- the company pays a capital gain dividend of d a share; the price falls by d
  | sell (i : Nat)       -- sell share i
  | wash (i : Nat)       -- sell share i at a loss and buy a share back at once
  deriving DecidableEq, Repr

def step (closed : Bool) (s : S) : Mv → S
  | .buy => { s with lots := s.lots ++ [{ basis := s.p, taint := 0 }] }
  | .div d => { s with p := s.p - d, lots := s.lots.map (fun l => { l with taint := l.taint + d }),
                       ltGain := s.ltGain + d * s.lots.length }
  | .sell i =>
    match s.lots[i]? with
    | none => s
    | some l =>
      let loss := l.basis - s.p
      if loss ≤ 0 then { s with lots := s.lots.eraseIdx i, gain := s.gain - loss }
      else { s with lots := s.lots.eraseIdx i, ltLoss := s.ltLoss + min loss l.taint,
                    stLoss := s.stLoss + (loss - min loss l.taint) }
  | .wash i =>
    match s.lots[i]? with
    | none => s
    | some l =>
      let loss := l.basis - s.p
      if loss ≤ 0 then s
      else { s with lots := s.lots.eraseIdx i ++
               [{ basis := s.p + loss, taint := if closed then min loss l.taint else 0 }] }

def run (closed : Bool) (s : S) (ms : List Mv) : S := ms.foldl (step closed) s

def s0 : S := { p := 100000, lots := [] }

/-- The plan: buy, the dividend of 10,000 is paid, sell and rebuy (wash sale), sell the replacement. -/
def plan : List Mv := [.buy, .div 10000, .wash 0, .sell 0]

/-- Statute as written: 10,000 of long-term gain and 10,000 of short-term loss. -/
theorem open_plan : (run false s0 plan).ltGain = 10000 ∧ (run false s0 plan).stLoss = 10000 ∧
    (run false s0 plan).ltLoss = 0 ∧ (run false s0 plan).lots = [] := by decide

/-- Without the wash sale the statute already works: the loss is long-term. -/
theorem open_no_wash : (run false s0 [.buy, .div 10000, .sell 0]).stLoss = 0 ∧
    (run false s0 [.buy, .div 10000, .sell 0]).ltLoss = 10000 := by decide

/-- Closed rule, same plan: the loss is long-term. -/
theorem closed_plan : (run true s0 plan).ltGain = 10000 ∧ (run true s0 plan).stLoss = 0 ∧
    (run true s0 plan).ltLoss = 10000 := by decide

/-- Invariant: no short-term loss has been taken, and every share's unrealized loss is covered by its taint. -/
def Inv (s : S) : Prop := s.stLoss = 0 ∧ ∀ l ∈ s.lots, l.basis - s.p ≤ l.taint

theorem inv_s0 : Inv s0 := ⟨rfl, by intro l h; cases h⟩

theorem inv_step (s : S) (m : Mv) (h : Inv s) : Inv (step true s m) := by
  obtain ⟨h0, hl⟩ := h
  cases m with
  | buy =>
    refine ⟨h0, ?_⟩
    intro l hm
    simp only [step, List.mem_append, List.mem_singleton] at hm ⊢
    rcases hm with hm | hm
    · exact hl l hm
    · subst hm; simp
  | div d =>
    refine ⟨h0, ?_⟩
    intro l hm
    simp only [step, List.mem_map] at hm ⊢
    obtain ⟨l', hm', rfl⟩ := hm
    have := hl l' hm'
    simp only
    omega
  | sell i =>
    simp only [step]
    cases hi : s.lots[i]? with
    | none => exact ⟨h0, hl⟩
    | some l =>
      have hmem : l ∈ s.lots := List.mem_of_getElem? hi
      have hb := hl l hmem
      simp only
      by_cases hloss : l.basis - s.p ≤ 0
      · rw [if_pos hloss]
        exact ⟨h0, fun x hx => hl x (List.mem_of_mem_eraseIdx hx)⟩
      · rw [if_neg hloss]
        refine ⟨?_, fun x hx => hl x (List.mem_of_mem_eraseIdx hx)⟩
        simp only
        rw [h0]
        omega
  | wash i =>
    simp only [step]
    cases hi : s.lots[i]? with
    | none => exact ⟨h0, hl⟩
    | some l =>
      have hmem : l ∈ s.lots := List.mem_of_getElem? hi
      have hb := hl l hmem
      simp only
      by_cases hloss : l.basis - s.p ≤ 0
      · rw [if_pos hloss]; exact ⟨h0, hl⟩
      · rw [if_neg hloss]
        refine ⟨h0, ?_⟩
        intro x hx
        simp only [List.mem_append, List.mem_singleton] at hx
        rcases hx with hx | hx
        · exact hl x (List.mem_of_mem_eraseIdx hx)
        · subst hx
          simp only [if_true]
          omega

theorem inv_run (ms : List Mv) : ∀ s, Inv s → Inv (run true s ms) := by
  induction ms with
  | nil => intro s h; exact h
  | cons m ms ih => intro s h; exact ih _ (inv_step s m h)

/-- **Closed rule, every sequence of moves of every length:** no short-term loss is ever produced. In particular
no sequence reaches the plan's result (long-term gain with a short-term loss of 10,000). -/
theorem closed_no_short_term_loss (ms : List Mv) : (run true s0 ms).stLoss = 0 := (inv_run ms s0 inv_s0).1

theorem closed_never_reaches_plan (ms : List Mv) : (run true s0 ms).stLoss ≠ 10000 := by
  rw [closed_no_short_term_loss]; decide

/-- And under the statute as written the same universal statement is false (witness: the plan). -/
theorem open_not_universal : ¬ ∀ ms : List Mv, (run false s0 ms).stLoss = 0 := by
  intro h; have := h plan; revert this; decide

#print axioms open_plan
#print axioms open_no_wash
#print axioms closed_plan
#print axioms closed_no_short_term_loss
#print axioms closed_never_reaches_plan
#print axioms open_not_universal

end Legal.USTax.Hunt.Audit.InstrumentsRedKernel
