import LegalProofs.CaseLaw2.Basic

/-!
# Spec: the conflict resolver and splits (doctrine §9 item 24; prior_art §7.1 items 3–4)

For one bound court, one issue and one date, the **candidates** are the good-law holdings on the issue with their
force on that court, their source's precedence (SCOTUS 4, court of last resort 3, intermediate or adopted 2, other 1),
date and whether they come from the court's own unit.

`resolve` returns a **set** (a list) of permissible holdings, not one answer:
1. keep candidates with force ≥ `bindingAbsentConflict` (the binding sub-base);
2. keep the highest precedence; among those, the strictly binding ones if any;
3. if they agree, done; otherwise first-in-time where the court's rule says so (F7), else the own unit under
   `ownUnitThenAny`/`ownUnitOnly` (§4.1 V), else all of them (the trial court's choice: CA, NJ, NY, IL, FL).

A **split** on a yes/no question: two courts that do not bind each other whose permissible answers are `{yes}` and
`{no}`. Theorem: a binding SCOTUS holding in both courts' bases, with SCOTUS consistent on the issue, leaves no split.
-/

namespace CaseLaw2.Spec
open CaseLaw2

def scotusPrec : Nat := 4

structure Cand where
  holding : Nat
  answer : Answer
  force : Force
  prec : Nat
  date : Date
  ownUnit : Bool
  deriving Repr, DecidableEq, Inhabited

def Cand.counts (c : Cand) : Bool := decide (Force.bindingAbsentConflict.rank ≤ c.force.rank)

def maxPrec (cs : List Cand) : Nat := cs.foldl (fun m c => max m c.prec) 0

/-- Steps 1–2. -/
def preferBinding (tops : List Cand) : List Cand :=
  if tops.any (fun c => c.force == .binding) then tops.filter (fun c => c.force == .binding) else tops

def top (cs : List Cand) : List Cand :=
  preferBinding ((cs.filter Cand.counts).filter (fun c => c.prec == maxPrec (cs.filter Cand.counts)))

def agree (cs : List Cand) : Bool :=
  match cs with
  | [] => true
  | c :: rest => rest.all (fun d => d.answer == c.answer)

def minDate : List Cand → Date
  | [] => forever
  | c :: rest => rest.foldl (fun m d => min m d.date) c.date

theorem minDate_attained : ∀ (rest : List Cand) (c : Cand), ∃ d ∈ c :: rest, d.date = minDate (c :: rest)
  | [], c => ⟨c, by simp, by simp [minDate]⟩
  | e :: es, c => by
    let c' := if c.date ≤ e.date then c else e
    have hc' : c'.date = min c.date e.date := by
      by_cases h : c.date ≤ e.date
      · simp only [c', h, if_true]; exact (Nat.min_eq_left h).symm
      · simp only [c', h, if_false]; exact (Nat.min_eq_right (by omega)).symm
    obtain ⟨d, hd, hdd⟩ := minDate_attained es c'
    refine ⟨d, ?_, ?_⟩
    · rcases List.mem_cons.mp hd with h | h
      · subst h; simp only [c']; split <;> simp
      · simp [h]
    · simp only [minDate, List.foldl_cons] at hdd ⊢; rw [hdd, hc']

/-- **The conflict resolver.** -/
def choose (firstInTime : Bool) (scope : Option TrialScope) (t : List Cand) : List Cand :=
  if agree t then t
  else if firstInTime then t.filter (fun c => c.date == minDate t)
  else if (scope == some .ownUnitThenAny || scope == some .ownUnitOnly) && t.any (·.ownUnit) then t.filter (·.ownUnit)
  else t

def resolve (firstInTime : Bool) (scope : Option TrialScope) (cs : List Cand) : List Cand :=
  choose firstInTime scope (top cs)

def allAnswer (cs : List Cand) (a : Answer) : Bool := !cs.isEmpty && cs.all (·.answer == a)

/-- A split between two courts on one question (given that neither binds the other). -/
def split (r₁ r₂ : List Cand) (bindsEachOther : Bool) : Bool :=
  !bindsEachOther && ((allAnswer r₁ .yes && allAnswer r₂ .no) || (allAnswer r₁ .no && allAnswer r₂ .yes))

/-! ## Theorems -/

theorem top_sub (cs : List Cand) : ∀ c ∈ top cs, c ∈ cs ∧ c.counts = true := by
  intro c hc
  unfold top preferBinding at hc
  split at hc <;> simp_all

theorem resolve_sub_top (f : Bool) (s : Option TrialScope) (cs : List Cand) : ∀ c ∈ resolve f s cs, c ∈ top cs := by
  intro c hc
  unfold resolve choose at hc
  split at hc
  · exact hc
  split at hc
  · exact (List.mem_filter.mp hc).1
  split at hc
  · exact (List.mem_filter.mp hc).1
  · exact hc

/-- The resolver only returns candidates it was given, and only binding-sub-base ones. -/
theorem resolve_sound (f : Bool) (s : Option TrialScope) (cs : List Cand) :
    ∀ c ∈ resolve f s cs, c ∈ cs ∧ c.counts = true :=
  fun c hc => top_sub cs c (resolve_sub_top f s cs c hc)

theorem foldl_max_ge_init (cs : List Cand) (m : Nat) : m ≤ cs.foldl (fun m c => max m c.prec) m := by
  induction cs generalizing m with
  | nil => simp
  | cons d cs ih => simp only [List.foldl_cons]; have := ih (max m d.prec); omega

theorem foldl_max_ge (cs : List Cand) (m : Nat) : ∀ c ∈ cs, c.prec ≤ cs.foldl (fun m c => max m c.prec) m := by
  induction cs generalizing m with
  | nil => simp
  | cons d cs ih =>
    intro c hc
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp hc with h | h
    · subst h; have := foldl_max_ge_init cs (max m c.prec); omega
    · exact ih _ c h

theorem foldl_max_le (cs : List Cand) (n m : Nat) (hm : m ≤ n) (h : ∀ c ∈ cs, c.prec ≤ n) :
    cs.foldl (fun m c => max m c.prec) m ≤ n := by
  induction cs generalizing m with
  | nil => simpa
  | cons d cs ih =>
    simp only [List.foldl_cons]
    apply ih
    · have := h d (by simp); omega
    · intro c hc; exact h c (by simp [hc])

/-- **A binding SCOTUS holding resolves the issue for every court it binds**: if a court's candidates include a binding
SCOTUS holding with answer `a`, no candidate outranks SCOTUS, and every SCOTUS candidate in the binding base answers
`a`, then every permissible holding answers `a`. -/
theorem scotus_resolves (f : Bool) (s : Option TrialScope) (cs : List Cand) (a : Answer)
    (hs : ∃ c ∈ cs, c.prec = scotusPrec ∧ c.force = .binding ∧ c.answer = a)
    (hle : ∀ c ∈ cs, c.prec ≤ scotusPrec)
    (hcons : ∀ c ∈ cs, c.prec = scotusPrec → c.counts = true → c.answer = a) :
    ∀ c ∈ resolve f s cs, c.answer = a := by
  intro c hc
  have hct := resolve_sub_top f s cs c hc
  obtain ⟨hcs, hcc⟩ := top_sub cs c hct
  apply hcons c hcs _ hcc
  -- c has the top precedence, which is scotusPrec
  obtain ⟨d, hd, hdp, hdf, _⟩ := hs
  have hdc : d.counts = true := by simp [Cand.counts, hdf, Force.rank]
  have hdbs : d ∈ cs.filter Cand.counts := List.mem_filter.mpr ⟨hd, hdc⟩
  have hmax_ge := foldl_max_ge (cs.filter Cand.counts) 0 d hdbs
  have hmax_le := foldl_max_le (cs.filter Cand.counts) scotusPrec 0 (by simp [scotusPrec])
    (fun c hc => hle c (List.mem_filter.mp hc).1)
  have hcp : c.prec = maxPrec (cs.filter Cand.counts) := by
    unfold top preferBinding at hct
    split at hct <;> simp_all [maxPrec]
  simp only [maxPrec] at hcp
  omega

/-- **A later binding SCOTUS holding resolves any split** among the courts it binds. -/
theorem scotus_resolves_split (f₁ f₂ : Bool) (s₁ s₂ : Option TrialScope) (cs₁ cs₂ : List Cand) (a : Answer) (b : Bool)
    (h₁ : ∃ c ∈ cs₁, c.prec = scotusPrec ∧ c.force = .binding ∧ c.answer = a)
    (h₂ : ∃ c ∈ cs₂, c.prec = scotusPrec ∧ c.force = .binding ∧ c.answer = a)
    (hle₁ : ∀ c ∈ cs₁, c.prec ≤ scotusPrec) (hle₂ : ∀ c ∈ cs₂, c.prec ≤ scotusPrec)
    (hc₁ : ∀ c ∈ cs₁, c.prec = scotusPrec → c.counts = true → c.answer = a)
    (hc₂ : ∀ c ∈ cs₂, c.prec = scotusPrec → c.counts = true → c.answer = a) :
    split (resolve f₁ s₁ cs₁) (resolve f₂ s₂ cs₂) b = false := by
  have r₁ := scotus_resolves f₁ s₁ cs₁ a h₁ hle₁ hc₁
  have r₂ := scotus_resolves f₂ s₂ cs₂ a h₂ hle₂ hc₂
  unfold split allAnswer
  cases a <;>
  · cases hr1 : resolve f₁ s₁ cs₁ with
    | nil => simp
    | cons c₁ t₁ =>
      cases hr2 : resolve f₂ s₂ cs₂ with
      | nil => simp
      | cons c₂ t₂ =>
        have e1 := r₁ c₁ (by simp [hr1])
        have e2 := r₂ c₂ (by simp [hr2])
        simp_all

/-- If the binding sub-base agrees, the resolver returns it unchanged (no choice is needed). -/
theorem resolve_agree (f : Bool) (s : Option TrialScope) (cs : List Cand) (h : agree (top cs) = true) :
    resolve f s cs = top cs := by
  simp [resolve, choose, h]

/-- With some binding candidate, the resolver is never empty. -/
theorem resolve_nonempty (f : Bool) (s : Option TrialScope) (cs : List Cand)
    (h : ∃ c ∈ cs, c.counts = true) : resolve f s cs ≠ [] := by
  obtain ⟨d, hd, hdc⟩ := h
  have hbs : (cs.filter Cand.counts) ≠ [] := List.ne_nil_of_mem (List.mem_filter.mpr ⟨hd, hdc⟩)
  -- the maximum precedence is attained
  have attained : ∀ (l : List Cand), l ≠ [] → ∃ c ∈ l, c.prec = l.foldl (fun m c => max m c.prec) 0 := by
    intro l hl
    have gen : ∀ (l : List Cand) (m : Nat), (∃ c ∈ l, c.prec = l.foldl (fun m c => max m c.prec) m) ∨
        l.foldl (fun m c => max m c.prec) m = m := by
      intro l
      induction l with
      | nil => intro m; right; rfl
      | cons e es ih =>
        intro m
        simp only [List.foldl_cons]
        rcases ih (max m e.prec) with ⟨c, hc, hcp⟩ | h
        · left; exact ⟨c, by simp [hc], hcp⟩
        · by_cases hme : m ≤ e.prec
          · left; exact ⟨e, by simp, by rw [h]; omega⟩
          · right; rw [h]; omega
    rcases gen l 0 with h | h
    · exact h
    · match l, hl with
      | e :: es, _ =>
        have := foldl_max_ge (e :: es) 0 e (by simp)
        exact ⟨e, by simp, by omega⟩
  obtain ⟨c, hc, hcp⟩ := attained _ hbs
  have htop : top cs ≠ [] := by
    unfold top preferBinding
    split
    · rename_i h; simp only [List.any_eq_true] at h
      obtain ⟨x, hx, hxb⟩ := h
      exact List.ne_nil_of_mem (List.mem_filter.mpr ⟨hx, hxb⟩)
    · exact List.ne_nil_of_mem (List.mem_filter.mpr ⟨hc, by simp [maxPrec, hcp]⟩)
  unfold resolve choose
  split
  · exact htop
  split
  · -- the earliest candidate is kept
    intro hnil
    match htc : top cs, htop with
    | c₀ :: rest, _ =>
      obtain ⟨d, hd, hdd⟩ := minDate_attained rest c₀
      have : d ∈ (c₀ :: rest).filter (fun c => c.date == minDate (c₀ :: rest)) :=
        List.mem_filter.mpr ⟨hd, by simp [hdd]⟩
      rw [htc] at hnil; rw [hnil] at this; simp at this
  split
  · rename_i _ _ h
    simp only [Bool.and_eq_true, List.any_eq_true] at h
    obtain ⟨x, hx, hxo⟩ := h.2
    exact List.ne_nil_of_mem (List.mem_filter.mpr ⟨hx, hxo⟩)
  · exact htop

end CaseLaw2.Spec
