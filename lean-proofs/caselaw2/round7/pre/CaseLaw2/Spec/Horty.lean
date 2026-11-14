/-!
# Horty's reason model of precedent (specification)

Horty, "Rules and reasons in the theory of precedent" (2011), and Horty & Bench-Capon, "A factor-based definition of
precedential constraint" (2012), in decidable list form.

* A *factor* is a binary, legally relevant feature of a fact situation; each favours one side, `pi` (plaintiff) or
  `delta` (defendant).
* A *case* (precedent) `⟨X, r, s⟩` has fact situation `X`, outcome `s` and reason `r ⊆ X^s` (the factors of `X` that
  favour `s`). It is read as the defeasible rule `r → s`, and induces the priority "every set of opposing factors
  present in `X` is weaker than `r`".
* A case base `Γ` is *inconsistent* when its derived priority ordering orders some pair of reasons both ways. In pair
  form: two cases with opposite outcomes, each of whose reason is contained in the other's facts. `consistent` checks
  that no such pair exists.
* A decision is *permitted* when adding it keeps the base consistent; an outcome is *forced* on `X` when some
  precedent for it controls `X` a fortiori (Prakken's test: the precedent's reason is present, and every opposing
  factor of `X` was already present in the precedent).
* The *result model* is the special case where the reason is the whole of `X^s`; it is more conservative.
* Yes/no answers to a split question embed as fact-free cases (`answerCase`), so a binding base of such answers is
  consistent exactly when all answers agree.

This module is a specification used for "consistency of a court's binding case base where reasons exist": reasons come
from the optional `factors.tsv` (columns `holding_id, factor, side, inReason`). Overruling a holding removes it from
the base, and `consistent_sublist` / `consistent_erase` show that this preserves consistency.
-/

namespace CaseLaw2.Spec.Horty

/-- The two sides of a dispute: `pi` (plaintiff) and `delta` (defendant). -/
inductive Side
  | pi
  | delta
  deriving DecidableEq, Repr

/-- The other side. -/
def Side.opp : Side → Side
  | .pi => .delta
  | .delta => .pi

@[simp] theorem Side.opp_ne (s : Side) : s.opp ≠ s := by cases s <;> decide
@[simp] theorem Side.ne_opp (s : Side) : s ≠ s.opp := by cases s <;> decide

/-- A factor of the issue's vocabulary, with the side it favours. -/
structure Factor where
  id : Nat
  side : Side
  deriving DecidableEq, Repr

/-- A precedent `⟨X, r, s⟩`: fact situation, reason (`⊆ X^s`), outcome. -/
structure FCase where
  facts : List Factor
  reason : List Factor
  outcome : Side
  deriving DecidableEq, Repr

/-- List inclusion as a Bool. -/
def sub (a b : List Factor) : Bool := a.all fun x => decide (x ∈ b)

@[simp] theorem sub_iff (a b : List Factor) : sub a b = true ↔ ∀ x ∈ a, x ∈ b := by
  simp [sub]

/-- Well-formedness: every reason factor is a fact and favours the outcome (`r ⊆ X^s`). -/
def FCase.wf (c : FCase) : Bool :=
  c.reason.all fun f => decide (f ∈ c.facts) && decide (f.side = c.outcome)

theorem FCase.wf_iff (c : FCase) :
    c.wf = true ↔ ∀ f ∈ c.reason, f ∈ c.facts ∧ f.side = c.outcome := by
  simp [FCase.wf]

/-- Pair-form inconsistency: opposite outcomes, and each case's reason is present in the other's facts. Then `c1`
says `c1.reason` beats the opposing factors of `c1.facts` (which include `c2.reason`), and `c2` says the reverse: the
derived priority ordering orders this pair of reasons both ways (Horty's inconsistency, in pair form). -/
def conflict (c1 c2 : FCase) : Bool :=
  decide (c1.outcome ≠ c2.outcome) && sub c2.reason c1.facts && sub c1.reason c2.facts

/-- A case base is consistent iff no pair of its cases conflicts (Horty: the derived priority ordering orders no pair
of reasons both ways, checked pairwise). -/
def consistent (Γ : List FCase) : Bool :=
  Γ.all fun c1 => Γ.all fun c2 => !conflict c1 c2

theorem consistent_iff (Γ : List FCase) :
    consistent Γ = true ↔ ∀ c1 ∈ Γ, ∀ c2 ∈ Γ, conflict c1 c2 = false := by
  simp [consistent]

/-- A decision `c` is permitted by `Γ` iff adding it keeps the base consistent. -/
def permitted (Γ : List FCase) (c : FCase) : Bool := consistent (c :: Γ)

/-- A fortiori control (Prakken's test): the precedent's reason is present in `X`, and every factor of `X` against the
precedent's outcome was already present in the precedent. -/
def forcedBy (c : FCase) (X : List Factor) : Bool :=
  sub c.reason X && sub (X.filter fun f => decide (f.side = c.outcome.opp)) c.facts

theorem forcedBy_iff (c : FCase) (X : List Factor) :
    forcedBy c X = true ↔
      (∀ f ∈ c.reason, f ∈ X) ∧ (∀ f ∈ X, f.side = c.outcome.opp → f ∈ c.facts) := by
  simp [forcedBy]

/-- Outcome `s` is forced on `X` by `Γ`: some precedent for `s` controls `X` a fortiori. -/
def forced (Γ : List FCase) (X : List Factor) (s : Side) : Bool :=
  Γ.any fun c => decide (c.outcome = s) && forcedBy c X

/-- Result model: read the precedent's reason as all of `X^s`. -/
def resultCase (c : FCase) : FCase :=
  { c with reason := c.facts.filter fun f => decide (f.side = c.outcome) }

/-- A yes/no answer to a split question as a fact-free case. -/
def answerCase (yes : Bool) : FCase := ⟨[], [], if yes then .pi else .delta⟩

/-! ## Theorems -/

/-- Overruling = removing holdings preserves consistency. -/
theorem consistent_sublist {Γ Γ' : List FCase} (h : ∀ x ∈ Γ', x ∈ Γ) :
    consistent Γ = true → consistent Γ' = true := by
  rw [consistent_iff, consistent_iff]
  intro hc c1 h1 c2 h2
  exact hc c1 (h c1 h1) c2 (h c2 h2)

/-- Overruling one case preserves consistency. -/
theorem consistent_erase {Γ : List FCase} (c : FCase) (h : consistent Γ = true) :
    consistent (Γ.erase c) = true :=
  consistent_sublist (fun _ hx => List.mem_of_mem_erase hx) h

/-- Overruling every case matching a predicate preserves consistency. -/
theorem consistent_filter {Γ : List FCase} (p : FCase → Bool) (h : consistent Γ = true) :
    consistent (Γ.filter p) = true :=
  consistent_sublist (fun _ hx => (List.mem_filter.mp hx).1) h

/-- If a precedent forces its outcome on `X`, every decision for the other side on `X` (with any reason made of
present, other-side factors) is inconsistent with the case base. -/
theorem forced_blocks_opposite {Γ : List FCase} {c : FCase} {X : List Factor} (hc : c ∈ Γ)
    (hf : forcedBy c X = true) :
    ∀ r, sub r X = true → (∀ f ∈ r, f.side = c.outcome.opp) →
      consistent (⟨X, r, c.outcome.opp⟩ :: Γ) = false := by
  intro r hr hside
  rw [forcedBy_iff] at hf
  rw [sub_iff] at hr
  have hconf : conflict ⟨X, r, c.outcome.opp⟩ c = true := by
    simp only [conflict, sub_iff, Bool.and_eq_true, decide_eq_true_eq]
    refine ⟨⟨Side.opp_ne _, hf.1⟩, ?_⟩
    intro f hfr
    exact hf.2 f (hr f hfr) (hside f hfr)
  cases hcons : consistent (⟨X, r, c.outcome.opp⟩ :: Γ) with
  | false => rfl
  | true =>
    rw [consistent_iff] at hcons
    have := hcons _ List.mem_cons_self c (List.mem_cons_of_mem _ hc)
    rw [hconf] at this
    exact absurd this (by decide)

/-- The result model never forces where the reason model does not. -/
theorem result_not_stricter {c : FCase} {X : List Factor} (hwf : FCase.wf c = true)
    (h : forcedBy (resultCase c) X = true) : forcedBy c X = true := by
  rw [FCase.wf_iff] at hwf
  rw [forcedBy_iff] at h ⊢
  refine ⟨?_, h.2⟩
  intro f hf
  apply h.1
  simp [resultCase, (hwf f hf).1, (hwf f hf).2]

theorem answerCase_conflict (a b : Bool) :
    conflict (answerCase a) (answerCase b) = !(a == b) := by
  cases a <;> cases b <;> decide

/-- Yes/no holdings are the degenerate fact-free case: a split question's binding base is consistent iff all answers
agree. -/
theorem answers_consistent_iff (as : List Bool) :
    consistent (as.map answerCase) = true ↔ ∀ a ∈ as, ∀ b ∈ as, a = b := by
  rw [consistent_iff]
  constructor
  · intro h a ha b hb
    have := h _ (List.mem_map_of_mem ha) _ (List.mem_map_of_mem hb)
    rw [answerCase_conflict] at this
    cases a <;> cases b <;> simp_all
  · intro h c1 h1 c2 h2
    obtain ⟨a, ha, rfl⟩ := List.mem_map.mp h1
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp h2
    rw [answerCase_conflict, h a ha b hb]
    simp

/-- A base whose cases all share one outcome is consistent. -/
theorem consistent_of_same_outcome {Γ : List FCase} {s : Side} (h : ∀ c ∈ Γ, c.outcome = s) :
    consistent Γ = true := by
  rw [consistent_iff]
  intro c1 h1 c2 h2
  simp [conflict, h c1 h1, h c2 h2]

/-- If every case in a consistent base has outcome `s`, any well-formed case with outcome `s` is permitted. (The
consistency and well-formedness hypotheses are not needed for the conclusion.) -/
theorem permitted_of_consistent_same_outcome {Γ : List FCase} {s : Side} {c : FCase}
    (_hΓ : consistent Γ = true) (hs : ∀ d ∈ Γ, d.outcome = s) (_hwf : FCase.wf c = true)
    (hc : c.outcome = s) : permitted Γ c = true := by
  apply consistent_of_same_outcome (s := s)
  intro d hd
  rcases List.mem_cons.mp hd with rfl | hd
  · exact hc
  · exact hs d hd

/-! ## Examples: a trade-secret-like factor base

Factors (id, side): 1 security measures (pi), 2 agreed not to disclose (pi), 3 info known to competitors (delta),
4 info reverse-engineerable (delta), 5 disclosed in negotiations (delta). -/

private def f1 : Factor := ⟨1, .pi⟩
private def f2 : Factor := ⟨2, .pi⟩
private def f3 : Factor := ⟨3, .delta⟩
private def f4 : Factor := ⟨4, .delta⟩
private def f5 : Factor := ⟨5, .delta⟩

/-- Plaintiff wins on {1,2,3} because of security measures. -/
private def cA : FCase := ⟨[f1, f2, f3], [f1], .pi⟩
/-- Defendant wins on {2,4,5} because the info was reverse-engineerable. -/
private def cB : FCase := ⟨[f2, f4, f5], [f4], .delta⟩
/-- Defendant wins on {1,3} because the info was known to competitors: conflicts with `cA`. -/
private def cC : FCase := ⟨[f1, f3], [f3], .delta⟩

#guard cA.wf && cB.wf && cC.wf
#guard consistent [cA, cB]
#guard conflict cA cC
#guard !consistent [cA, cB, cC]
#guard consistent ([cA, cB, cC].erase cC)
-- cA controls {1,2,3}: reason f1 present, opposing {3} was in cA. Forced for pi; a delta decision is not permitted.
#guard forced [cA, cB] [f1, f2, f3] .pi
#guard !permitted [cA, cB] ⟨[f1, f2, f3], [f3], .delta⟩
-- With f4 added, cA no longer controls (f4 was absent from cA): distinguishable, and delta via f4 is permitted.
#guard !forced [cA, cB] [f1, f3, f4] .pi
#guard permitted [cA] ⟨[f1, f3, f4], [f4], .delta⟩
-- Result model is more conservative: resultCase cA needs both f1 and f2 present.
#guard forcedBy cA [f1, f3]
#guard !forcedBy (resultCase cA) [f1, f3]
-- Answer embedding.
#guard consistent ([true, true, true].map answerCase)
#guard !consistent ([true, false].map answerCase)
#guard consistent (([] : List Bool).map answerCase)

end CaseLaw2.Spec.Horty
