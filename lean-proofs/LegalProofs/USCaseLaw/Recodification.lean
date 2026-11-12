/-!
# Recodification: does every old provision land somewhere?

When Congress restates a title of the US Code as positive law, it repeals the old sections and enacts new ones. The
Office of the Law Revision Counsel prints a disposition table: each former section, and the new section it became, or
why it has none ("Rep.", "Elim.", "Omitted", "Previously repealed", ...).

The model: a restatement has
* `old`: the provisions in force at the old locations the day before it took effect (read from the record);
* `dispo`: what the official tables say became of each (`mapped` to new sections, or `omitted` with a reason);
* `inForce`: the sections in force in the record once the restatement took effect.

`total` holds when every old provision has a disposition: images, or a stated reason. `sound` holds when every image
the table names is a section the record has in force. Proved: `total` gives each old provision an image or a recorded
omission (`total_spec`), and with `sound` every image is in force (`check_images_in_force`); the unaccounted list is
empty exactly when the check passes (`unaccounted_nil_iff`), and anything not on it is accounted for
(`accounted_of_not_unaccounted`); what is accounted for stays so when more of the table is added (`accounted_append`).
-/

namespace Legal.USCaseLaw.Recodification

/-- What became of an old provision: new provisions it maps to, or a reason it has none. -/
inductive Disposition where
  | mapped (images : List String)
  | omitted (reason : String)
  deriving Repr, DecidableEq, Inhabited

/-- One restatement: old provisions, the official dispositions, and the provisions in force afterwards. -/
structure Restatement where
  old : List String
  dispo : List (String × Disposition)
  inForce : List String
  deriving Repr, Inhabited

/-- The first disposition the tables give an old provision. -/
def lookup (r : Restatement) (o : String) : Option Disposition :=
  (r.dispo.find? (fun p => p.1 == o)).map (·.2)

/-- Accounted for: mapped to at least one provision, or omitted with a stated (non-empty) reason. -/
def accountedBy : Option Disposition → Bool
  | some (.mapped imgs) => !imgs.isEmpty
  | some (.omitted reason) => !reason.isEmpty
  | none => false

def accounted (r : Restatement) (o : String) : Bool := accountedBy (lookup r o)

/-- Every image of an old provision is in force (vacuous for omissions). -/
def imagesInForce (r : Restatement) (o : String) : Bool :=
  match lookup r o with
  | some (.mapped imgs) => imgs.all (fun i => r.inForce.contains i)
  | _ => true

def unaccounted (r : Restatement) : List String := r.old.filter (fun o => !accounted r o)

/-- Images the tables name that the record does not have in force. -/
def missingImages (r : Restatement) : List (String × String) :=
  r.old.flatMap fun o =>
    match lookup r o with
    | some (.mapped imgs) => (imgs.filter (fun i => !r.inForce.contains i)).map (o, ·)
    | _ => []

def total (r : Restatement) : Bool := r.old.all (accounted r)
def sound (r : Restatement) : Bool := r.old.all (imagesInForce r)
def check (r : Restatement) : Bool := total r && sound r

theorem accountedBy_spec (d : Option Disposition) (h : accountedBy d = true) :
    (∃ imgs, d = some (.mapped imgs) ∧ imgs ≠ []) ∨ (∃ reason, d = some (.omitted reason) ∧ reason ≠ "") := by
  match d, h with
  | some (.mapped imgs), h =>
    left; refine ⟨imgs, rfl, ?_⟩
    intro he; subst he; simp [accountedBy] at h
  | some (.omitted reason), h =>
    right; refine ⟨reason, rfl, ?_⟩
    intro he; subst he; simp [accountedBy] at h

/-- When the totality check passes, every old provision has an image or a recorded omission. -/
theorem total_spec (r : Restatement) (h : total r = true) (o : String) (ho : o ∈ r.old) :
    (∃ imgs, lookup r o = some (.mapped imgs) ∧ imgs ≠ []) ∨
    (∃ reason, lookup r o = some (.omitted reason) ∧ reason ≠ "") := by
  unfold total at h
  rw [List.all_eq_true] at h
  exact accountedBy_spec _ (h o ho)

/-- When the whole check passes, every old provision that maps somewhere maps only to provisions in force. -/
theorem check_images_in_force (r : Restatement) (h : check r = true) (o : String) (ho : o ∈ r.old)
    (imgs : List String) (hl : lookup r o = some (.mapped imgs)) (i : String) (hi : i ∈ imgs) : i ∈ r.inForce := by
  unfold check sound at h
  rw [Bool.and_eq_true, List.all_eq_true] at h
  have := h.2 o ho
  unfold imagesInForce at this
  rw [hl] at this
  simp only [List.all_eq_true] at this
  exact List.contains_iff_mem.mp (this i hi)

/-- And it has at least one: totality plus soundness give an image in force or a recorded omission. -/
theorem check_spec (r : Restatement) (h : check r = true) (o : String) (ho : o ∈ r.old) :
    (∃ imgs, lookup r o = some (.mapped imgs) ∧ imgs ≠ [] ∧ ∀ i ∈ imgs, i ∈ r.inForce) ∨
    (∃ reason, lookup r o = some (.omitted reason) ∧ reason ≠ "") := by
  have ht : total r = true := by unfold check at h; exact (Bool.and_eq_true _ _).mp h |>.1
  rcases total_spec r ht o ho with ⟨imgs, hl, hn⟩ | hr
  · exact Or.inl ⟨imgs, hl, hn, fun i hi => check_images_in_force r h o ho imgs hl i hi⟩
  · exact Or.inr hr

/-- The list of unaccounted provisions is empty exactly when the totality check passes. -/
theorem unaccounted_nil_iff (r : Restatement) : unaccounted r = [] ↔ total r = true := by
  unfold unaccounted total
  rw [List.filter_eq_nil_iff, List.all_eq_true]
  constructor
  · intro h o ho; have := h o ho; simpa using this
  · intro h o ho; simp [h o ho]

/-- An old provision not on the unaccounted list is accounted for. -/
theorem accounted_of_not_unaccounted (r : Restatement) (o : String) (ho : o ∈ r.old) (hn : o ∉ unaccounted r) :
    accounted r o = true := by
  unfold unaccounted at hn
  cases hc : accounted r o with
  | true => rfl
  | false => exact absurd (List.mem_filter.mpr ⟨ho, by simp [hc]⟩) hn

/-- Adding rows to the end of the tables never un-accounts a provision (the first row for it still decides). -/
theorem accounted_append (r : Restatement) (more : List (String × Disposition)) (o : String)
    (h : accounted r o = true) : accounted { r with dispo := r.dispo ++ more } o = true := by
  unfold accounted lookup at *
  cases hf : r.dispo.find? (fun p => p.1 == o) with
  | none => simp [hf, accountedBy] at h
  | some p => simp [List.find?_append, hf] at h ⊢; exact h

/-! A toy restatement: one section moves, one is omitted as executed, and one the table forgets. -/

def toy : Restatement where
  old := ["40:1", "40:2", "40:3"]
  dispo := [("40:1", .mapped ["40:101"]), ("40:2", .omitted "executed")]
  inForce := ["40:101"]

example : unaccounted toy = ["40:3"] := by decide
example : total toy = false := by decide
example : sound toy = true := by decide
example : total { toy with dispo := toy.dispo ++ [("40:3", .mapped ["2:1927"])] } = true := by decide
example : sound { toy with dispo := toy.dispo ++ [("40:3", .mapped ["2:1927"])] } = false := by decide

end Legal.USCaseLaw.Recodification
