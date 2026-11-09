/-!
# A semantics of amending acts

The corpora are built by replaying amending acts: "§ 5 is replaced by …", "§ 12 is repealed", "§ 50c is inserted".
Here that process is itself formal. A statute maps provision keys to texts; an amendment is an instruction; a day's
consolidation applies that day's instructions in order.

Two vulnerability kinds fall out as theorems rather than definitions:

* **Failed amendments**: an instruction aimed at a provision that does not exist changes nothing at all
  (`replace_missing_noop`, `repeal_missing_noop`). This is the GwG § 50c case: the Annual Tax Act 2024 amended a section
  that was never enacted, so the statute after the amendment is literally the statute before it.
* **Same-day conflicts**: a day's instructions can be applied in any order exactly when no two of them touch the same
  provision. `consolidate_perm` proves order-independence for instructions on distinct provisions (by induction over
  permutations); `same_key_conflict` proves that two different replacements of one provision give different statutes in
  the two orders. So a same-day conflict is a genuine ambiguity in the law unless the gazette fixes an order.
-/

namespace Legal

abbrev Key := String
/-- A statute: the text of each provision, `none` where there is no such provision. -/
abbrev Statute := Key → Option String

/-- An amending instruction. -/
inductive Amendment where
  | insert (k : Key) (t : String)   -- "§ k is inserted": only where there is no § k yet
  | replace (k : Key) (t : String)  -- "§ k is replaced by": only where § k exists
  | repeal (k : Key)                -- "§ k is repealed"
  deriving DecidableEq

def Amendment.key : Amendment → Key
  | insert k _ | replace k _ | repeal k => k

/-- The new text of the target provision, given its old text. An instruction that cannot be carried out leaves it as
it was. -/
def Amendment.newText : Amendment → Option String → Option String
  | insert _ t, none => some t
  | insert _ _, some u => some u
  | replace _ t, some _ => some t
  | replace _ _, none => none
  | repeal _, _ => none

/-- Apply one instruction to a statute: only its target provision can change. -/
def Amendment.apply (a : Amendment) (s : Statute) : Statute :=
  fun j => if j = a.key then a.newText (s j) else s j

/-- Consolidate a list of instructions, in order. -/
def consolidate (as : List Amendment) (s : Statute) : Statute := as.foldl (fun s a => a.apply s) s

/-! ## Failed amendments are no-ops -/

theorem replace_missing_noop (s : Statute) (k : Key) (t : String) (h : s k = none) :
    (Amendment.replace k t).apply s = s := by
  funext j
  by_cases hj : j = k
  · subst hj; simp [Amendment.apply, Amendment.key, Amendment.newText, h]
  · simp [Amendment.apply, Amendment.key, hj]

theorem repeal_missing_noop (s : Statute) (k : Key) (h : s k = none) : (Amendment.repeal k).apply s = s := by
  funext j
  by_cases hj : j = k
  · subst hj; simp [Amendment.apply, Amendment.key, Amendment.newText, h]
  · simp [Amendment.apply, Amendment.key, hj]

/-- The GwG case in miniature: a statute without § 50c, and the 2024 instruction to amend § 50c(2). -/
def gwg : Statute := fun k => if k = "§ 50" then some "Aufsichtsbehörden …" else if k = "§ 55" then some "…" else none

example : (Amendment.replace "§ 50c" "… Nummer 5 …").apply gwg = gwg :=
  replace_missing_noop gwg "§ 50c" _ (by decide)

/-! ## Instructions on different provisions commute -/

theorem apply_same (a : Amendment) (s : Statute) : a.apply s a.key = a.newText (s a.key) := by
  simp [Amendment.apply]

theorem apply_other (a : Amendment) (s : Statute) (j : Key) (h : j ≠ a.key) : a.apply s j = s j := by
  simp [Amendment.apply, h]

theorem commute (a b : Amendment) (s : Statute) (h : a.key ≠ b.key) :
    a.apply (b.apply s) = b.apply (a.apply s) := by
  funext j
  by_cases ha : j = a.key
  · have hb : j ≠ b.key := by rw [ha]; exact h
    subst ha
    rw [apply_same, apply_other b _ _ hb, apply_other b _ _ hb, apply_same]
  · by_cases hb : j = b.key
    · subst hb
      rw [apply_other a _ _ ha, apply_same, apply_same, apply_other a _ _ ha]
    · rw [apply_other a _ _ ha, apply_other b _ _ hb, apply_other b _ _ hb, apply_other a _ _ ha]

/-- **Order-independence.** If no two of a day's instructions touch the same provision, every order of applying them
gives the same statute. -/
theorem consolidate_perm {as bs : List Amendment} (p : as.Perm bs)
    (hd : as.Pairwise (fun a b => a.key ≠ b.key)) : ∀ s, consolidate as s = consolidate bs s := by
  induction p with
  | nil => intro s; rfl
  | cons x _ ih =>
    intro s
    simp only [consolidate, List.foldl_cons] at *
    exact ih (List.pairwise_cons.mp hd).2 _
  | swap x y l =>
    intro s
    have hxy : y.key ≠ x.key := (List.pairwise_cons.mp hd).1 x (List.mem_cons_self ..)
    simp only [consolidate, List.foldl_cons]
    rw [commute y x s hxy]
  | trans p₁ _ ih₁ ih₂ =>
    intro s
    have hd₂ := p₁.pairwise hd (fun h => Ne.symm h)
    rw [ih₁ hd s, ih₂ hd₂ s]

/-- **Same-day conflicts are real.** Two different replacements of one existing provision give different statutes in
the two orders, so the result depends on an order the law has to supply. -/
theorem same_key_conflict (s : Statute) (k : Key) (t₁ t₂ : String) (hk : s k ≠ none) (ht : t₁ ≠ t₂) :
    (Amendment.replace k t₁).apply ((Amendment.replace k t₂).apply s) ≠
      (Amendment.replace k t₂).apply ((Amendment.replace k t₁).apply s) := by
  intro h
  have := congrFun h k
  cases hs : s k with
  | none => exact hk hs
  | some u =>
    simp [Amendment.apply, Amendment.key, Amendment.newText, hs] at this
    exact ht this

end Legal
